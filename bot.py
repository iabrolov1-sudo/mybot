import asyncio
import logging
from io import BytesIO
import requests

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import BufferedInputFile
from google import genai
from google.genai import types as genai_types
from PIL import Image

# Вставьте ваши токены в кавычки!
TELEGRAM_BOT_TOKEN = "ВАШ_ТЕЛЕГРАМ_ТОКЕН"
GEMINI_API_KEY = "ВАШ_GEMINI_API_KEY"

gemini_client = genai.Client(api_key=GEMINI_API_KEY)
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я твой AI-ассистент.\n\n"
        "• Отправь текст, чтобы получить ответ.\n"
        "• Отправь /img описание, чтобы получить картинку.\n"
        "• Отправь фото с вопросом, чтобы проанализировать его."
    )

@dp.message(Command("img"))
async def generate_image(message: types.Message):
    prompt = message.text.replace("/img", "").strip()
    if not prompt:
        await message.answer("⚠️ Укажите описание картинки после /img.")
        return

    status_msg = await message.answer("🎨 *Генерирую...*")

    try:
        image_url = f"https://pollinations.ai/p/{requests.utils.quote(prompt)}?width=1024&height=1024&seed=42&model=flux"
        response = requests.get(image_url, timeout=30)

        if response.status_code == 200:
            photo = BufferedInputFile(response.content, filename="generated.png")
            await message.answer_photo(photo=photo, caption=f"🖼 _{prompt}_")
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ Ошибка генерации.")
    except Exception as e:
        await status_msg.edit_text("❌ Ошибка сервера.")

@dp.message(F.photo)
async def analyze_photo(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        photo_bytes = await bot.download_file(file_info.file_path)

        img = Image.open(photo_bytes)
        user_caption = message.caption if message.caption else "Что изображено на этом фото?"

        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[img, user_caption]
        )

        await message.reply(response.text)
    except Exception as e:
        await message.answer("⚠️ Не удалось разобрать изображение.")

@dp.message(F.text)
async def chat_text(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=message.text
        )
        await message.answer(response.text)
    except Exception as e:
        await message.answer("⚠️ Ошибка обработки запроса.")

async def main():
    await dp.start_polling(bot)

if name == "main":
    asyncio.run(main())

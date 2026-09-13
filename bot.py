import asyncio
import logging
from io import BytesIO
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from google import genai
from PIL import Image

# Ваши токены
TELEGRAM_BOT_TOKEN = "8764445915:AAF5W7g11AFoxnXBF69jVv-z5s7tdObsGL0"
GEMINI_API_KEY = "AQ.Ab8RN6IiK_YOPE7WiAExgr9ALJHQw52U8GlxRuvdGlCjaQDjcw"

# Инициализация клиентов
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

logging.basicConfig(level=logging.INFO)

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("Привет! Отправь мне текст или изображение, и я обработаю его через Gemini.")

@dp.message(F.text)
async def text_handler(message: types.Message):
    try:
        # Используем асинхронный клиент client.aio
        response = await gemini_client.aio.models.generate_content(
            model="gemini-2.0-flash",
            contents=message.text
        )
        await message.answer(response.text if response.text else "Пустой ответ от Gemini.")
    except Exception as e:
        logging.error(f"Ошибка Gemini: {e}")
        await message.answer(f"Ошибка API: {str(e)}")

@dp.message(F.photo)
async def photo_handler(message: types.Message):
    try:
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        photo_bytes = await bot.download_file(file_info.file_path)
        
        image = Image.open(photo_bytes)
        caption = message.caption if message.caption else "Что изображено на этом фото?"
        
        # Используем асинхронный клиент client.aio
        response = await gemini_client.aio.models.generate_content(
            model="gemini-2.0-flash",
            contents=[caption, image]
        )
        await message.answer(response.text if response.text else "Не удалось разобрать изображение.")
    except Exception as e:
        logging.error(f"Ошибка обработки фото: {e}")
        await message.answer(f"Ошибка обработки фото: {str(e)}")

async def main():
    await dp.start_polling(bot)

if name == "main":
    asyncio.run(main())

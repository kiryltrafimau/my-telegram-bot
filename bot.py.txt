from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import os

from dotenv import load_dotenv
load_dotenv()  # загружаем переменные из .env

TOKEN = os.getenv("TELEGRAM_TOKEN")
admins = os.getenv("ADMIN_IDS")  # например: "123456789,987654321"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.answer("Привет! Ответь на вопрос: Почему хочешь в этот чат?")

@dp.message_handler()
async def answer_handler(message: types.Message):
    admin_ids = [int(id.strip()) for id in admins.split(',')]  # преобразуем строку в список чисел
    for admin_id in admin_ids:
        await bot.send_message(admin_id, f"Ответ от {message.from_user.full_name}: {message.text}")
    await message.answer("Спасибо, ваш ответ отправлен администраторам!")

if __name__ == '__main__':
    executor.start_polling(dp)

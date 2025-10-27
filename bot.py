import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("TELEGRAM_TOKEN")
admins = os.getenv("ADMIN_IDS")
admin_ids = [int(id.strip()) for id in admins.split(',')]

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Привет! Отправь мне сообщение, и я перешлю его админам.")

@dp.message()
async def forward_to_admins(message: types.Message):
    for admin_id in admin_ids:
        await bot.send_message(
            admin_id,
            f"Сообщение от пользователя {message.from_user.id} (@{message.from_user.username}):\n\n{message.text}"
        )
    await message.answer("Ваше сообщение отправлено администраторам!")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

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
    await message.answer("Привет! Зачем вам этот чат? Напишите ваше сообщение, и я передам его администраторам.")

@dp.message()
async def forward_to_admins(message: types.Message):
    # Отправляем сообщение только в личку пользователю
    if message.chat.type == "private":
        for admin_id in admin_ids:
            await bot.send_message(
                admin_id,
                f"Новое сообщение от пользователя:\n\n"
                f"ID: {message.from_user.id}\n"
                f"Имя: {message.from_user.full_name}\n"
                f"Username: @{message.from_user.username if message.from_user.username else 'не указан'}\n\n"
                f"Текст сообщения:\n{message.text}"
            )
        await message.answer("Спасибо! Ваше сообщение передано администраторам. Мы свяжемся с вами в ближайшее время.")
    # Если сообщение из группы/чата - игнорируем
    else:
        pass

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

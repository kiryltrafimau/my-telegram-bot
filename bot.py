import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, ChatMemberUpdatedFilter, JOIN_TRANSITION

TOKEN = os.getenv("TELEGRAM_TOKEN")
admins = os.getenv("ADMIN_IDS")
admin_ids = [int(id.strip()) for id in admins.split(',')]

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer('Привет! Это контроль спама. Зачем вам нужен чат "ИП: Беременность и декрет в Польше"? Напишите ваше сообщение, и я передам его администраторам.')

@dp.chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def on_user_join(event: types.ChatMemberUpdated):
    """Когда пользователь пытается присоединиться к чату"""
    user = event.new_chat_member.user
    
    # Отправляем сообщение пользователю в личку
    try:
        await bot.send_message(
            user.id,
            'Привет! Это контроль спама. Зачем вам нужен чат "ИП: Беременность и декрет в Польше"? Напишите ваше сообщение, и я передам его администраторам.'
        )
    except Exception as e:
        print(f"Не удалось отправить сообщение пользователю {user.id}: {e}")
    
    # Уведомляем админов о новом пользователе
    for admin_id in admin_ids:
        await bot.send_message(
            admin_id,
            f"Новый пользователь хочет присоединиться к чату:\n\n"
            f"ID: {user.id}\n"
            f"Имя: {user.full_name}\n"
            f"Username: @{user.username if user.username else 'не указан'}"
        )

@dp.message()
async def forward_to_admins(message: types.Message):
    """Обработка личных сообщений боту"""
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

async def main():
    await dp.start_polling(bot, allowed_updates=["message", "chat_member"])

if __name__ == '__main__':
    asyncio.run(main())

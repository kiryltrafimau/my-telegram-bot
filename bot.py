import asyncio
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, ChatMemberUpdatedFilter, JOIN_TRANSITION

TOKEN = os.getenv("TELEGRAM_TOKEN")
admins = os.getenv("ADMIN_IDS")
admin_ids = [int(id.strip()) for id in admins.split(',')]

bot = Bot(token=TOKEN)
dp = Dispatcher()

# HTTP endpoint для Render
async def health(request):
    return web.Response(text="Bot is running!")

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer('Привет! Это контроль спама. Зачем вам нужен чат "ИП: Беременность и декрет в Польше"? Напишите ваше сообщение, и я передам его администраторам.')

@dp.chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def on_user_join(event: types.ChatMemberUpdated):
    user = event.new_chat_member.user
    try:
        await bot.send_message(
            user.id,
            'Привет! Это контроль спама. Зачем вам нужен чат "ИП: Беременность и декрет в Польше"? Напишите ваше сообщение, и я передам его администраторам.'
        )
    except Exception as e:
        print(f"Не удалось отправить сообщение пользователю {user.id}: {e}")
    
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

async def start_bot():
    await dp.start_polling(bot, allowed_updates=["message", "chat_member"])

async def start_web():
    app = web.Application()
    app.router.add_get('/', health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 10000)))
    await site.start()

async def main():
    await asyncio.gather(
        start_bot(),
        start_web()
    )

if __name__ == '__main__':
    asyncio.run(main())

import asyncio
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

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

@dp.chat_join_request()
async def on_join_request(chat_join_request: types.ChatJoinRequest):
    """Когда пользователь ЗАПРАШИВАЕТ вступление в чат (до одобрения)"""
    user = chat_join_request.from_user
    
    # Отправляем сообщение пользователю в личку
    try:
        await bot.send_message(
            user.id,
            'Привет! Это контроль спама. Зачем вам нужен чат "ИП: Беременность и декрет в Польше"? Напишите ваше сообщение, и я передам его администраторам.'
        )
    except Exception as e:
        print(f"Не удалось отправить сообщение пользователю {user.id}: {e}")
    
    # Уведомляем админов о новом запросе
    for admin_id in admin_ids:
        await bot.send_message(
            admin_id,
            f"Новый пользователь запросил вступление в чат:\n\n"
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
    await dp.start_polling(bot, allowed_updates=["message", "chat_join_request"])

async def start_web():
    app = web.Application()
    app.router.add_get('/', health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 10000)))
    await site.start()

async def main():
    await asyncio.gather(start_bot(), start_web())

if __name__ == '__main__':
    asyncio.run(main())

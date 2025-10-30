import asyncio
import os
import signal
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Получаем токен бота и список админов из переменных окружения
TOKEN = os.getenv("TELEGRAM_TOKEN")
admins = os.getenv("ADMIN_IDS")
admin_ids = [int(id.strip()) for id in admins.split(',')]

# Создаем объекты бота и диспетчера для aiogram
bot = Bot(token=TOKEN)
dp = Dispatcher()

# HTTP endpoint для проверки состояния сервиса на Render
async def health(request):
    return web.Response(text="Bot is running!")

# Обработчик команды /start для любого пользователя
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer('Привет! Это контроль спама. Зачем вам нужен чат "ИП: Беременность и декрет в Польше"? Напишите ваше сообщение, и я передам его администраторам.')

# Обработчик события запроса на вступление в чат (до одобрения)
@dp.chat_join_request()
async def on_join_request(chat_join_request: types.ChatJoinRequest):
    user = chat_join_request.from_user
    
    # Отправляем сообщение пользователю в личку с просьбой написать боту
    try:
        await bot.send_message(
            user.id,
            'Привет! Это контроль спама. Зачем вам нужен чат "ИП: Беременность и декрет в Польше"? Напишите ваше сообщение, и я передам его администраторам.'
        )
    except Exception as e:
        # Логируем ошибки если не удалось отправить сообщение
        print(f"Не удалось отправить сообщение пользователю {user.id}: {e}")
    
    # Уведомляем админов о новом запросе на вступление
    for admin_id in admin_ids:
        await bot.send_message(
            admin_id,
            f"Новый пользователь запросил вступление в чат:\n\n"
            f"ID: {user.id}\n"
            f"Имя: {user.full_name}\n"
            f"Username: @{user.username if user.username else 'не указан'}"
        )

# Пересылаем все личные сообщения пользователей (в ЛС бота) админам
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
        # Благодарим пользователя за сообщение
        await message.answer("Спасибо! Ваше сообщение передано администраторам. Мы свяжемся с вами в ближайшее время.")

# Запускаем бота с разрешенными обновлениями сообщений и запросов на вступление
async def start_bot():
    await dp.start_polling(bot, allowed_updates=["message", "chat_join_request"])

# Запускаем http сервер для Render, чтобы можно было проверять состояние
async def start_web():
    app = web.Application()
    # Регистрируем endpoint /
    app.router.add_get('/', health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 10000)))
    await site.start()

# Главная функция запуска, где добавлена обработка сигнала SIGTERM
async def main():
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    # Обработчик сигнала SIGTERM - выполняется при остановке сервиса Render
    def signal_handler():
        print("Получен SIGTERM, завершаем работу...")
        stop_event.set()  # Сигнализируем боту завершить работу

    # Регистрируем обработчик сигнала
    loop.add_signal_handler(signal.SIGTERM, signal_handler)

    # Запускаем одновременно бот, веб-сервер и ожидание завершения stop_event
    await asyncio.gather(
        start_bot(),
        start_web(),
        stop_event.wait()    # Останавливаемся здесь при получении сигнала
    )
    # Корректно закрываем сессию бота
    await bot.session.close()

# Запуск главной функции
if __name__ == '__main__':
    asyncio.run(main())

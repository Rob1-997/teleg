# main.py
import asyncio, logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from hendlers import all_routers
from database import connect_db, init_schema
from middlewares.last_seen import UpdateLastSeen , CheckBan
from aiogram.types import BotCommand, BotCommandScopeChat, MenuButtonCommands



bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def on_startup(bot: Bot):
    # Покажет всем пользователям кнопку «/» слева от ввода
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())

async def main():
    await connect_db()     # создаём pool
    await init_schema()    # гарантируем таблицы
    dp.startup.register(on_startup)
    dp.message.middleware(UpdateLastSeen())
    dp.callback_query.middleware(UpdateLastSeen())
    dp.message.middleware(CheckBan())
    dp.callback_query.middleware(CheckBan())
    dp.include_router(all_routers)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

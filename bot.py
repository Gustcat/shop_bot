from aiogram import Bot, Dispatcher
import asyncio

from aiogram.client.default import DefaultBotProperties

from config import TELEGRAM_TOKEN
from handlers import main_menu, catalog, cart, order


async def main():
    bot = Bot(token=TELEGRAM_TOKEN, defaults=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()

    dp.include_router(main_menu.router)
    dp.include_router(catalog.router)
    dp.include_router(cart.router)
    dp.include_router(order.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

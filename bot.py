from pathlib import Path

from aiogram import Bot, Dispatcher
import asyncio

from aiogram.client.default import DefaultBotProperties

from config import TELEGRAM_TOKEN
from handlers import main_menu, catalog, cart, order, admin
from middlewares import AdminCheckMiddleware


async def main():
    PRODUCT_MEDIA = Path("media/products")
    PRODUCT_MEDIA.mkdir(parents=True, exist_ok=True)

    bot = Bot(token=TELEGRAM_TOKEN, defaults=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()
    dp.update.middleware.register(AdminCheckMiddleware())

    dp.include_router(main_menu.router)
    dp.include_router(catalog.router)
    dp.include_router(cart.router)
    dp.include_router(order.router)
    dp.include_router(admin.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

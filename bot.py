import logging
from logging.config import dictConfig
from pathlib import Path

from aiogram import Bot, Dispatcher
import asyncio

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import TELEGRAM_TOKEN
from handlers import main_menu, catalog, cart, order, admin
from middlewares import UserMiddleware
from utils.log_config import LOGGING_CONFIG


async def main():
    Path("logs").mkdir(parents=True, exist_ok=True)
    dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)

    logger.info("Запуск бота...")

    PRODUCT_MEDIA = Path("media/products")
    PRODUCT_MEDIA.mkdir(parents=True, exist_ok=True)

    bot = Bot(
        token=TELEGRAM_TOKEN, defaults=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.update.middleware.register(UserMiddleware())

    dp.include_router(main_menu.router)
    dp.include_router(catalog.router)
    dp.include_router(cart.router)
    dp.include_router(order.router)
    dp.include_router(admin.router)

    await bot.delete_webhook(drop_pending_updates=True)

    try:
        logger.info("Начало polling...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception(
            f"Ошибка во время polling",
        )
        raise
    finally:
        await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.getLogger(__name__).critical(
            f"Критическая ошибка при запуске", exc_info=True
        )

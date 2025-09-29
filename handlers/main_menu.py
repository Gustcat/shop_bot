import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from db import User
from utils.constants.buttons import MAIN_MENU
from utils.constants.callbacks import MAIN_MENU_CD
from keyboards.main_menu_kb import main_menu_kb, main_reply_kb
from utils.messaging import update_or_replace_message

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "/start")
async def cmd_start(message: Message):
    logger.info(
        "Команда /start вызвана",
        extra={"user_id": message.from_user.id, "username": message.from_user.username},
    )
    await message.answer(
        f"Добро пожаловать! Используй кнопку {MAIN_MENU} внизу 👇",
        reply_markup=main_reply_kb,
    )


@router.message(F.text == MAIN_MENU)
async def back_to_main_message(message: Message, user: User | None):
    text = MAIN_MENU
    user_role = user.role if user else None
    await message.answer(text, reply_markup=main_menu_kb(user_role=user_role))


@router.callback_query(F.data == MAIN_MENU_CD)
async def back_to_main_callback(call: CallbackQuery, user: User | None):
    text = MAIN_MENU
    user_role = user.role if user else None
    print(user_role)
    await update_or_replace_message(
        call.message, text, main_menu_kb(user_role=user_role)
    )
    await call.answer()

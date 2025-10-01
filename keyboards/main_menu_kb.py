from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from db import UserRole
from utils.constants.buttons import MAIN_MENU, ORDERS, CATALOG, CREATE_PRODUCT
from keyboards.common_buttons import CART_BUTTON
from utils.constants.callbacks import CATALOG_CD, ORDERS_CD, CREATE_PRODUCT_CD

main_reply_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=MAIN_MENU)]],
    resize_keyboard=True,
)


def main_menu_kb(user_role: UserRole | None) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=CATALOG, callback_data=CATALOG_CD)],
        [InlineKeyboardButton(text=ORDERS, callback_data=ORDERS_CD)],
    ]

    if user_role == UserRole.ADMIN:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=CREATE_PRODUCT, callback_data=CREATE_PRODUCT_CD
                )
            ],
        )
    else:
        buttons.append([CART_BUTTON])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

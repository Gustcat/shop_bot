from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from db import UserRole
from utils.constants.buttons import MAIN_MENU
from keyboards.common import CART_BUTTON

main_reply_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=MAIN_MENU)]],
    resize_keyboard=True,
)


def main_menu_kb(user_role: UserRole | None) -> InlineKeyboardMarkup:
    if user_role == UserRole.ADMIN:
        buttons = [
            [
                InlineKeyboardButton(
                    text="➕ Создать товар", callback_data="admin_create_product"
                )
            ],
            [InlineKeyboardButton(text="📦 Все заказы", callback_data="admin_orders")],
        ]
    else:
        buttons = [
            [CART_BUTTON],
            [InlineKeyboardButton(text="📦 Мои заказы", callback_data="my_orders")],
        ]
    buttons.append(
        [InlineKeyboardButton(text="🛍 Каталог", callback_data="catalog")],
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

main_reply_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Главное меню")]],
    resize_keyboard=True,
)


def main_menu_kb(is_admin: bool = False) -> InlineKeyboardMarkup:
    if is_admin:
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
            [InlineKeyboardButton(text="🛒 Корзина", callback_data="cart")],
            [InlineKeyboardButton(text="📦 Мои заказы", callback_data="my_orders")],
        ]
    buttons.append(
        [InlineKeyboardButton(text="🛍 Каталог", callback_data="catalog")],
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)

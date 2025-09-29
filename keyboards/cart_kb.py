from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from db import CartItem
from keyboards.common import MAIN_MENU_BUTTON
from utils.constants.callbacks import CART_CD


class CartCD(CallbackData, prefix=CART_CD):
    action: str
    product_id: int | None = None
    category_id: int | None = None


def cart_kb(cart_items: list[CartItem]) -> InlineKeyboardMarkup:
    kb = []

    for item in cart_items:
        kb.append(
            [
                InlineKeyboardButton(
                    text=f"{item.product.name} \n {item.quantity} шт.",
                    callback_data="ignore",
                )
            ]
        )
        kb.append(
            [
                InlineKeyboardButton(
                    text="➖",
                    callback_data=CartCD(
                        action="decrease", product_id=item.product_id
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text="➕",
                    callback_data=CartCD(
                        action="increase", product_id=item.product_id
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text="❌ Удалить",
                    callback_data=CartCD(
                        action="remove", product_id=item.product_id
                    ).pack(),
                ),
            ]
        )

    kb.append(
        [InlineKeyboardButton(text="✅ Оформить заказ", callback_data="checkout")]
    )
    kb.append([MAIN_MENU_BUTTON])

    return InlineKeyboardMarkup(inline_keyboard=kb)

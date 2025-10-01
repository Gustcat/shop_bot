from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from db import CartItem
from keyboards.common_buttons import MAIN_MENU_BUTTON
from utils.constants.buttons import DELETE, DECREASE, INCREASE, PLACE_ORDER
from utils.constants.callbacks import (
    CART_CD,
    IGNORE_CD,
    PLACE_ORDER_CD,
    DELETE_ACTION,
    DECREASE_ACTION,
    INCREASE_ACTION,
)


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
                    callback_data=IGNORE_CD,
                )
            ]
        )
        kb.append(
            [
                InlineKeyboardButton(
                    text=DECREASE,
                    callback_data=CartCD(
                        action=DECREASE_ACTION, product_id=item.product_id
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text=INCREASE,
                    callback_data=CartCD(
                        action=INCREASE_ACTION, product_id=item.product_id
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text=DELETE,
                    callback_data=CartCD(
                        action=DELETE_ACTION, product_id=item.product_id
                    ).pack(),
                ),
            ]
        )

    kb.append([InlineKeyboardButton(text=PLACE_ORDER, callback_data=PLACE_ORDER_CD)])
    kb.append([MAIN_MENU_BUTTON])

    return InlineKeyboardMarkup(inline_keyboard=kb)

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db import OrderStatus
from keyboards.common_buttons import MAIN_MENU_BUTTON, BACK_TO_LIST_ORDERS_BUTTON
from utils.constants.buttons import CONFIRM, CANCEL
from utils.constants.callbacks import (
    PRODUCT_CONFIRM_CD,
    PRODUCT_CANCEL_CD,
    SET_STATUS_ACTION,
)


class AdminCD(CallbackData, prefix="admin"):
    order_id: int
    action: str
    order_status: OrderStatus | None = None


confirm_product_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=CONFIRM, callback_data=PRODUCT_CONFIRM_CD),
            InlineKeyboardButton(text=CANCEL, callback_data=PRODUCT_CANCEL_CD),
        ]
    ]
)


def admin_change_status_kb(order_id: int) -> InlineKeyboardMarkup:
    statuses = [
        ("❌ Отменен", OrderStatus.CANCELED),
        ("⏳ В пути", OrderStatus.PROCESSING),
        ("🚚 Доставлен", OrderStatus.COMPLETED),
    ]

    buttons = [
        [
            InlineKeyboardButton(
                text=text,
                callback_data=AdminCD(
                    order_id=order_id, action=SET_STATUS_ACTION, order_status=status
                ).pack(),
            )
        ]
        for text, status in statuses
    ]

    buttons.append(
        [
            BACK_TO_LIST_ORDERS_BUTTON,
            MAIN_MENU_BUTTON,
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db import OrderStatus, Order


class AdminCD(CallbackData, prefix="admin"):
    order_id: int
    action: str
    order_status: OrderStatus


confirm_product_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Подтвердить", callback_data="product_confirm"
            ),
            InlineKeyboardButton(text="❌ Отменить", callback_data="product_cancel"),
        ]
    ]
)


def orders_kb(orders: list[Order]) -> InlineKeyboardMarkup:
    """Клавиатура со списком всех заказов"""
    rows = [
        [
            InlineKeyboardButton(
                text=str(order.order_uuid),
                callback_data=AdminCD(
                    order_id=order.id, order_status=order.status, action="view"
                ).pack(),
            )
        ]
        for order in orders
    ]

    rows.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu")])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def admin_change_status_kb(order_id: int) -> InlineKeyboardMarkup:
    statuses = [
        ("❌ Отменен", OrderStatus.CANCELED),
        ("⏳ В пути", OrderStatus.PROCESSING),
        ("🚚 Доставлен", OrderStatus.COMPLETED),
    ]

    keyboard = [
        [
            InlineKeyboardButton(
                text=text,
                callback_data=AdminCD(
                    order_id=order_id, action="set_status", order_status=status
                ).pack(),
            )
        ]
        for text, status in statuses
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

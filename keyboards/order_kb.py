from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db import PickupPoint, Order
from keyboards.common import MAIN_MENU_BUTTON


class PickupCD(CallbackData, prefix="pickup"):
    id: int


class OrderCD(CallbackData, prefix="order"):
    id: int


delivery_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🚚 Курьер", callback_data="delivery_courier"),
            InlineKeyboardButton(text="🏬 Самовывоз", callback_data="delivery_pickup"),
        ]
    ]
)


confirm_order_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="order_confirm"),
            InlineKeyboardButton(text="❌ Отменить", callback_data="order_cancel"),
        ]
    ]
)

detail_order_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="my_orders"),
            MAIN_MENU_BUTTON,
        ]
    ]
)


def pickup_points_kb(points: list[PickupPoint]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{p.name} - {p.address}",
                    callback_data=PickupCD(id=p.id).pack(),
                )
            ]
            for p in points
        ]
    )


def user_orders_kb(orders: list[Order]) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"Заказ {order.order_uuid}\nСтатус: {order.status}",
                callback_data=OrderCD(id=order.id).pack(),
            )
        ]
        for order in orders
    ]

    keyboard.append([MAIN_MENU_BUTTON])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

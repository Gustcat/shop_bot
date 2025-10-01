from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db import PickupPoint, Order, UserRole
from keyboards.admin_kb import AdminCD
from keyboards.common_buttons import MAIN_MENU_BUTTON, BACK_TO_LIST_ORDERS_BUTTON
from utils.constants.buttons import CONFIRM, CANCEL, COURIER, PICKUP
from utils.constants.callbacks import (
    DELIVERY_COURIER_CD,
    DELIVERY_PICKUP_CD,
    ORDER_CONFIRM_CD,
    ORDER_CANCEL_CD,
    VIEW_ACTION,
)


class PickupCD(CallbackData, prefix="pickup"):
    id: int


class OrderCD(CallbackData, prefix="order"):
    id: int


delivery_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=COURIER, callback_data=DELIVERY_COURIER_CD),
            InlineKeyboardButton(text=PICKUP, callback_data=DELIVERY_PICKUP_CD),
        ]
    ]
)


confirm_order_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=CONFIRM, callback_data=ORDER_CONFIRM_CD),
            InlineKeyboardButton(text=CANCEL, callback_data=ORDER_CANCEL_CD),
        ]
    ]
)

detail_order_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            BACK_TO_LIST_ORDERS_BUTTON,
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


def orders_kb(orders: list[Order], user_role: UserRole) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"Заказ {order.order_uuid}\nСтатус: {order.status}",
                callback_data=(
                    AdminCD(order_id=order.id, action=VIEW_ACTION).pack()
                    if user_role == UserRole.ADMIN
                    else OrderCD(id=order.id).pack()
                ),
            )
        ]
        for order in orders
    ]

    keyboard.append([MAIN_MENU_BUTTON])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

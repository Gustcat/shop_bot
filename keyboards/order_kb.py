from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db import PickupPoint, Order


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
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"Заказ {order.order_uuid} \n Статус: {order.status}",
                    callback_data=OrderCD(id=order.id).pack(),
                )
            ]
            for order in orders
        ]
    )

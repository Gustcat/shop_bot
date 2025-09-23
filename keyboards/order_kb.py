from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db import PickupPoint


class PickupCD(CallbackData, prefix="pickup"):
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

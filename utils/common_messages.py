from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from db import Order, DeliveryType
from utils.formatting import format_price_text


async def create_order_details_message(
    call: CallbackQuery, order: Order | None, kb: InlineKeyboardMarkup | None = None
):
    if not order:
        await call.answer("Заказ не найден", show_alert=True)
        return

    if order.delivery_type == DeliveryType.PICKUP and order.pickup_point:
        delivery_info = (
            f"Пункт самовывоза: {order.pickup_point.name}, {order.pickup_point.address}"
        )
    else:
        delivery_info = f"Адрес: {order.address or '—'}"

    text_lines = [
        f"🧾 Заказ {order.order_uuid}",
        f"Статус: {order.status}",
        f"Имя: {order.name}",
        f"Телефон: {order.phone}",
        f"{delivery_info}",
        f"Тип доставки: {order.delivery_type}",
        f"Создан: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n",
    ]

    items = order.items
    total = 0
    for item in items:
        price = item.product_price
        line_total = price * item.quantity
        total += line_total
        text_lines.append(
            f"{item.product_name} — {item.quantity} × {format_price_text(price)} = {format_price_text(line_total)}"
        )

    text_lines.append(f"\nИтого: {format_price_text(total)}")

    await call.message.edit_text("\n".join(text_lines), reply_markup=kb)

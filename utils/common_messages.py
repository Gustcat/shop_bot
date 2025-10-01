from db import Order, DeliveryType, Product
from utils.formatting import format_price_in_text


async def get_order_details_text(order: Order) -> str:
    """Генерация текста с деталями заказа."""
    if order.delivery_type == DeliveryType.PICKUP and order.pickup_point:
        delivery_info = (
            f"Пункт самовывоза: {order.pickup_point.name}, {order.pickup_point.address}"
        )
    else:
        delivery_info = f"Адрес: {order.address or '—'}"

    text_lines = [
        f"<b>🧾 Заказ {order.order_uuid}</b>",
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
            f"{item.product_name} — {item.quantity} × {format_price_in_text(price)} = {format_price_in_text(line_total)}"
        )

    text_lines.append(f"\nИтого: {format_price_in_text(total)}")
    return "\n".join(text_lines)


def get_product_text(product: Product) -> str:
    """Генерация текста карточки товара."""
    return (
        f"<b>{product.name}</b>\n\n"
        f"{product.description or 'Без описания'}\n\n"
        f"Цена: {format_price_in_text(product.price)}"
    )

def format_price_in_text(price_cents: int) -> str:
    return f"{price_cents/100:.2f} ₽"


def format_text_in_price(text: str) -> int:
    """Форматирует текстовую цену в целое число копеек."""
    correct_text = text.replace(",", ".").replace("₽", "")
    price_cents = int(float(correct_text) * 100)
    return price_cents

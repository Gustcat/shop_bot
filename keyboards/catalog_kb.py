from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db import Category, Product, UserRole
from keyboards.cart_kb import CartCD
from keyboards.common import MAIN_MENU_BUTTON, CART_BUTTON


class CategoryCD(CallbackData, prefix="category"):
    id: int


class ProductCD(CallbackData, prefix="product"):
    id: int
    category_id: int
    action: str


def categories_kb(categories: list[Category]) -> InlineKeyboardMarkup:
    """Клавиатура со списком категорий"""
    rows = [
        [
            InlineKeyboardButton(
                text=cat.name, callback_data=CategoryCD(id=cat.id).pack()
            )
        ]
        for cat in categories
    ]

    rows.append([MAIN_MENU_BUTTON])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def products_kb(products: list[Product], category_id: int) -> InlineKeyboardMarkup:
    """Клавиатура со списком товаров в категории"""
    keyboard_rows = []

    for prod in products:
        keyboard_rows.append(
            [
                InlineKeyboardButton(
                    text=prod.name,
                    callback_data=ProductCD(
                        action="view", id=prod.id, category_id=category_id
                    ).pack(),
                )
            ]
        )

    keyboard_rows.append(
        [
            InlineKeyboardButton(text="⬅️ Категории", callback_data="catalog"),
            MAIN_MENU_BUTTON,
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)


def product_detail_kb(
    product_id, category_id: int, user_role: UserRole | None, quantity: int = 0
) -> InlineKeyboardMarkup:
    """Клавиатура для отдельного продукта"""
    buttons: list[list[InlineKeyboardButton]] = []

    if user_role == UserRole.ADMIN:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="✏️ Редактировать",
                    callback_data=ProductCD(
                        action="edit", id=product_id, category_id=category_id
                    ).pack(),
                )
            ]
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    text="🗑 Удалить",
                    callback_data=ProductCD(
                        action="delete", id=product_id, category_id=category_id
                    ).pack(),
                )
            ]
        )
    else:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"🛒 Добавить в корзину ({quantity})",
                    callback_data=CartCD(
                        action="add", product_id=product_id, category_id=category_id
                    ).pack(),
                ),
                CART_BUTTON,
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text="⬅️ Назад", callback_data=CategoryCD(id=category_id).pack()
            ),
            MAIN_MENU_BUTTON,
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)

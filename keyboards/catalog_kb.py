from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Sequence
from db import Category, Product


class CategoryCD(CallbackData, prefix="category"):
    id: int


class ProductCD(CallbackData, prefix="product"):
    id: int
    category_id: int


class CartCD(CallbackData, prefix="cart"):
    action: str
    product_id: int | None = None
    category_id: int | None = None


def categories_kb(categories: Sequence[Category]) -> InlineKeyboardMarkup:
    """Клавиатура со списком категорий"""
    rows = [
        [
            InlineKeyboardButton(
                text=cat.name, callback_data=CategoryCD(id=cat.id).pack()
            )
        ]
        for cat in categories
    ]

    rows.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu")])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def products_kb(products: Sequence[Product], category_id: int) -> InlineKeyboardMarkup:
    """Клавиатура со списком товаров в категории"""
    keyboard_rows = []

    for prod in products:
        keyboard_rows.append(
            [
                InlineKeyboardButton(
                    text=prod.name,
                    callback_data=ProductCD(id=prod.id, category_id=category_id).pack(),
                )
            ]
        )

    keyboard_rows.append(
        [
            InlineKeyboardButton(text="⬅️ Категории", callback_data="catalog"),
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu"),
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)


def product_detail_kb(product_id, category_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для отдельного продукта"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛒 В корзину",
                    callback_data=CartCD(action="add", product_id=product_id).pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад к категории",
                    callback_data=CategoryCD(id=category_id).pack(),
                ),
                InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu"),
            ],
        ]
    )

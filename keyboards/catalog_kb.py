from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Sequence
from db import Category, Product
from keyboards.cart_kb import CartCD


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

    rows.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu")])

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
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu"),
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)


def product_detail_kb(
    product_id, category_id: int, is_admin: bool = False
) -> InlineKeyboardMarkup:
    """Клавиатура для отдельного продукта"""
    buttons: list[list[InlineKeyboardButton]] = []

    if is_admin:
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
                    text="🛒 В корзину",
                    callback_data=CartCD(action="add", product_id=product_id).pack(),
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text="⬅️ Назад", callback_data=CategoryCD(id=category_id).pack()
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)

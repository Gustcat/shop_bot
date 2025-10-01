from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db import Category, Product, UserRole
from keyboards.cart_kb import CartCD
from keyboards.common_buttons import MAIN_MENU_BUTTON, CART_BUTTON
from utils.constants.buttons import BACK, EDIT, DELETE
from utils.constants.callbacks import VIEW_ACTION, EDIT_ACTION, DELETE_ACTION


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
                        action=VIEW_ACTION, id=prod.id, category_id=category_id
                    ).pack(),
                )
            ]
        )

    keyboard_rows.append([MAIN_MENU_BUTTON])

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
                    text=EDIT,
                    callback_data=ProductCD(
                        action=EDIT_ACTION, id=product_id, category_id=category_id
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text=DELETE,
                    callback_data=ProductCD(
                        action=DELETE_ACTION, id=product_id, category_id=category_id
                    ).pack(),
                ),
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
                text=BACK, callback_data=CategoryCD(id=category_id).pack()
            ),
            MAIN_MENU_BUTTON,
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)

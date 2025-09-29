from pathlib import Path

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
)
from sqlalchemy import select

from db import async_session, UserRole, CartItem, User
from db import Category, Product
from keyboards.catalog_kb import (
    categories_kb,
    products_kb,
    product_detail_kb,
    CategoryCD,
    ProductCD,
)
from config import MEDIA_ROOT
from utils.formatting import format_price_text
from utils.messaging import safe_delete_message, update_or_replace_message

router = Router()


@router.callback_query(F.data == "catalog")
async def show_categories(call: CallbackQuery):
    """
    Выводит список категорий.
    """
    async with async_session() as session:
        result = await session.execute(select(Category).order_by(Category.name))
        categories = result.scalars().all()

    if not categories:
        await call.answer("Категории пока не добавлены.")
        return

    if call.message.photo:
        await safe_delete_message(call.message)
        await call.message.answer(
            "Выберите категорию:", reply_markup=categories_kb(categories)
        )
    else:
        await call.message.edit_text(
            "Выберите категорию:", reply_markup=categories_kb(categories)
        )

    await call.answer()


@router.callback_query(CategoryCD.filter())
async def show_products(call: CallbackQuery, callback_data: CategoryCD):
    """
    Выводит список товаров для выбранной категории.
    """
    category_id = callback_data.id

    async with async_session() as session:
        category = (
            await session.execute(select(Category).where(Category.id == category_id))
        ).scalar_one_or_none()
        if category is None:
            await call.answer("Категория не найдена.", show_alert=True)
            return

        products = (
            (
                await session.execute(
                    select(Product)
                    .where(Product.category_id == category_id)
                    .order_by(Product.name)
                )
            )
            .scalars()
            .all()
        )

        text = (
            f"Товары из категории «{category.name}»:"
            if products
            else f"В категории «{category.name}» товаров пока нет."
        )

        await update_or_replace_message(
            call.message, text, reply_markup=products_kb(products, category_id)
        )
        await call.answer()


@router.callback_query(ProductCD.filter(F.action == "view"))
async def show_detail_product(
    call: CallbackQuery, callback_data: ProductCD, user: User | None
):
    """
    Выводит карточку конкретного товара.
    """
    product_id = callback_data.id
    category_id = callback_data.category_id

    async with async_session() as session:

        product = await session.get(Product, product_id)
        if not product:
            await call.answer("Такого товара нет.", show_alert=True)
            return

        text = (
            f"<b>{product.name}</b>\n\n"
            f"{product.description or 'Без описания'}\n\n"
            f"Цена: {format_price_text(product.price)}"
        )

        quantity = 0
        if user and user.role == UserRole.CUSTOMER:
            result = await session.execute(
                select(CartItem.quantity).where(
                    CartItem.product_id == product_id, CartItem.user_id == user.id
                )
            )

            quantity = result.scalar_one_or_none() or 0

        if product.photo_filename:
            photo_path = Path(MEDIA_ROOT) / product.photo_filename
            photo_file = FSInputFile(photo_path)

            await safe_delete_message(call.message)
            await call.message.answer_photo(
                photo=photo_file,
                caption=text,
                reply_markup=product_detail_kb(
                    product.id, category_id, user.role, quantity
                ),
                parse_mode=ParseMode.HTML,
            )
        else:
            await call.message.edit_text(
                text,
                reply_markup=product_detail_kb(
                    product.id, category_id, user.role, quantity
                ),
                parse_mode=ParseMode.HTML,
            )
        await call.answer()

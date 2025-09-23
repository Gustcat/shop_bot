from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy import delete, select
from sqlalchemy.orm import joinedload

from db import async_session, CartItem, Product
from keyboards.cart_kb import CartCD, cart_kb
from keyboards.main_menu_kb import main_menu_kb
from repository.user import get_or_create_user
from utils.formatting import format_price_text

router = Router()


@router.callback_query(CartCD.filter(F.action == "add"))
async def add_to_cart(call: CallbackQuery, callback_data: CartCD):
    product_id = callback_data.product_id

    async with async_session() as session:
        user = await get_or_create_user(session, call.from_user)
        user_id = user.id

        cart_item = (
            await session.execute(
                select(CartItem).where(
                    CartItem.user_id == user_id, CartItem.product_id == product_id
                )
            )
        ).scalar_one_or_none()

        if cart_item:
            cart_item.quantity += 1
            message_text = f"Количество товара увеличено на 1 ✅ \n (Всего в корзине {cart_item.quantity} шт.)"
        else:
            cart_item = CartItem(user_id=user_id, product_id=product_id, quantity=1)
            session.add(cart_item)
            message_text = "Товар добавлен в корзину 🛒"

        await session.commit()

    await call.answer(message_text, show_alert=True)


@router.callback_query(F.data == "cart")
async def show_cart(call: CallbackQuery):
    async with async_session() as session:
        user = await get_or_create_user(session, call.from_user)
        user_id = user.id
        result = await session.execute(
            select(CartItem)
            .where(CartItem.user_id == user_id)
            .options(joinedload(CartItem.product))
        )
        cart_items = result.scalars().all()

        if not cart_items:
            await call.message.edit_text(
                "🛒 Ваша корзина пуста.", reply_markup=main_menu_kb
            )
            await call.answer()
            return

        text_lines = ["🛒 Ваша корзина:"]
        total = 0

        for item in cart_items:
            product = await session.get(Product, item.product_id)
            if not product:
                continue
            cost = product.price * item.quantity
            total += cost
            text_lines.append(
                f"{product.name} — {item.quantity} шт. × {format_price_text(product.price)} = {format_price_text(cost)}"
            )

        text_lines.append(f"\n💰 Итого: {format_price_text(total)}")

    await call.message.edit_text(
        "\n".join(text_lines), reply_markup=cart_kb(cart_items)
    )
    await call.answer()


@router.callback_query(CartCD.filter(F.action == "increase"))
async def increase_quantity(call: CallbackQuery, callback_data: CartCD):
    async with async_session() as session:
        user = await get_or_create_user(session, call.from_user)
        user_id = user.id
        item = (
            await session.execute(
                select(CartItem).where(
                    CartItem.user_id == user_id,
                    CartItem.product_id == callback_data.product_id,
                )
            )
        ).scalar_one_or_none()

        if item:
            item.quantity += 1
            await session.commit()

    await show_cart(call)


@router.callback_query(CartCD.filter(F.action == "decrease"))
async def decrease_quantity(call: CallbackQuery, callback_data: CartCD):
    async with async_session() as session:
        user = await get_or_create_user(session, call.from_user)
        user_id = user.id
        item = (
            await session.execute(
                select(CartItem).where(
                    CartItem.user_id == user_id,
                    CartItem.product_id == callback_data.product_id,
                )
            )
        ).scalar_one_or_none()

        if item:
            if item.quantity > 1:
                item.quantity -= 1
            else:
                await session.delete(item)
            await session.commit()

    await show_cart(call)


@router.callback_query(CartCD.filter(F.action == "remove"))
async def remove_item(call: CallbackQuery, callback_data: CartCD):
    """
    Удаляет товар из корзины
    """
    async with async_session() as session:
        user = await get_or_create_user(session, call.from_user)
        user_id = user.id
        await session.execute(
            delete(CartItem).where(
                CartItem.user_id == user_id,
                CartItem.product_id == callback_data.product_id,
            )
        )
        await session.commit()

    await show_cart(call)


@router.callback_query(F.data == "ignore")
async def ignore_button(call: CallbackQuery):
    await call.answer()

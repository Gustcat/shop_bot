from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy import delete, select
from sqlalchemy.orm import joinedload

from handlers.main_menu import back_to_main_callback
from keyboards.catalog_kb import product_detail_kb
from utils.constants.buttons import CART
from db import async_session, CartItem, Product, User
from keyboards.cart_kb import CartCD, cart_kb
from repository.user import create_user
from utils.constants.callbacks import (
    CART_CD,
    IGNORE_CD,
    DELETE_ACTION,
    DECREASE_ACTION,
    INCREASE_ACTION,
)
from utils.constants.message_text import CART_EMPTY_TEXT
from utils.formatting import format_price_in_text
from utils.messaging import update_or_replace_message

router = Router()


@router.callback_query(CartCD.filter(F.action == "add"))
async def add_to_cart(call: CallbackQuery, callback_data: CartCD, user: User | None):
    product_id = callback_data.product_id
    category_id = callback_data.category_id

    async with async_session() as session:
        if not user:
            user = await create_user(session, call.from_user)
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
        else:
            cart_item = CartItem(user_id=user_id, product_id=product_id, quantity=1)
            session.add(cart_item)

        await session.commit()
    kb = product_detail_kb(product_id, category_id, user.role, cart_item.quantity)
    await call.message.edit_reply_markup(reply_markup=kb)
    await call.answer()


@router.callback_query(F.data == CART_CD)
async def show_cart(call: CallbackQuery, user: User | None):
    async with async_session() as session:
        if not user:
            user = await create_user(session, call.from_user)
        user_id = user.id
        result = await session.execute(
            select(CartItem)
            .where(CartItem.user_id == user_id)
            .options(joinedload(CartItem.product))
        )
        cart_items = result.scalars().all()

        if not cart_items:
            await call.answer(CART_EMPTY_TEXT, show_alert=False)
            await back_to_main_callback(call, user)
            return

        text_lines = [CART]
        total = 0

        for item in cart_items:
            product = await session.get(Product, item.product_id)
            if not product:
                continue
            cost = product.price * item.quantity
            total += cost
            text_lines.append(
                f"{product.name} — {item.quantity} шт. × {format_price_in_text(product.price)} = {format_price_in_text(cost)}"
            )

        text_lines.append(f"\n💰 Итого: {format_price_in_text(total)}")

    await update_or_replace_message(
        message=call.message,
        text="\n".join(text_lines),
        reply_markup=cart_kb(cart_items),
    )
    await call.answer()


@router.callback_query(CartCD.filter(F.action == INCREASE_ACTION))
async def increase_quantity(
    call: CallbackQuery, callback_data: CartCD, user: User | None
):
    async with async_session() as session:
        if not user:
            user = await create_user(session, call.from_user)
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

    await show_cart(call, user)


@router.callback_query(CartCD.filter(F.action == DECREASE_ACTION))
async def decrease_quantity(
    call: CallbackQuery, callback_data: CartCD, user: User | None
):
    async with async_session() as session:
        if not user:
            user = await create_user(session, call.from_user)
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

    await show_cart(call, user)


@router.callback_query(CartCD.filter(F.action == DELETE_ACTION))
async def remove_item(call: CallbackQuery, callback_data: CartCD, user: User | None):
    """
    Удаляет товар из корзины
    """
    async with async_session() as session:
        if not user:
            user = await create_user(session, call.from_user)
        user_id = user.id
        await session.execute(
            delete(CartItem).where(
                CartItem.user_id == user_id,
                CartItem.product_id == callback_data.product_id,
            )
        )
        await session.commit()

    await show_cart(call, user)


@router.callback_query(F.data == IGNORE_CD)
async def ignore_button(call: CallbackQuery):
    await call.answer()

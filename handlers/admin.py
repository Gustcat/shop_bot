from aiofiles import os
from aiogram import Router, F, Bot
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from utils.config import MEDIA_ROOT
from db import async_session, Order, Product, Category, OrderItem, UserRole, User
from keyboards.admin_kb import (
    AdminCD,
    admin_change_status_kb,
    confirm_product_kb,
)
from keyboards.catalog_kb import ProductCD
from keyboards.main_menu_kb import main_menu_kb
from repository.category import get_or_create_category
from utils.constants.buttons import MAIN_MENU
from utils.constants.callbacks import (
    CREATE_PRODUCT_CD,
    VIEW_ACTION,
    EDIT_ACTION,
    DELETE_ACTION,
    PRODUCT_CONFIRM_CD,
    PRODUCT_CANCEL_CD,
    SET_STATUS_ACTION,
)
from utils.constants.message_text import (
    INPUT_PRICE_TEXT,
    OPTIONAL_FIELD_TEXT,
    PRICE_ATTENTION_TEXT,
    INPUT_DESCRIPTION_TEXT,
    PRODUCT_NAME_ATTENTION_TEXT,
    INPUT_PRODUCT_NAME_TEXT,
    PRODUCT_NOT_FOUND_TEXT,
    INPUT_PHOTO_TEXT,
    PHOTO_ATTENTION_TEXT,
    INPUT_CATEGORY_TEXT,
    CATEGORY_ATTENTION_TEXT,
    NO_CATEGORIES_TEXT,
    INPUT_NEW_CATEGORY_TEXT,
    PRODUCT_DELETED_TEXT,
    CANCEL_UPDATE_PRODUCT_TEXT,
    CANCEL_CREATE_PRODUCT_TEXT,
)
from utils.formatting import format_text_in_price
from utils.messaging import (
    safe_delete_message,
    create_non_admin_forbidden_message,
    create_order_details_message,
)

router = Router()


class ProductFSM(StatesGroup):
    id = State()
    name = State()
    description = State()
    price = State()
    photo = State()
    category = State()
    category_creation = State()
    confirm = State()


async def file_remove(filename):
    if filename and not filename.contains("../"):
        file_path = f"{MEDIA_ROOT}/{filename}"
        try:
            await os.remove(file_path)
        except FileNotFoundError:
            pass


@router.callback_query(F.data == CREATE_PRODUCT_CD)
async def start_create_product(
    call: CallbackQuery, state: FSMContext, user: User | None
):
    if user and user.role != UserRole.ADMIN:
        await create_non_admin_forbidden_message(call)
        return
    await call.message.answer(INPUT_PRODUCT_NAME_TEXT + ":")
    await call.answer()
    await state.set_state(ProductFSM.name)


@router.callback_query(ProductCD.filter(F.action == EDIT_ACTION))
async def start_edit_product(
    call: CallbackQuery,
    callback_data: ProductCD,
    state: FSMContext,
    user: User | None,
):
    if user and user.role != UserRole.ADMIN:
        await create_non_admin_forbidden_message(call)
        return
    product_id = callback_data.id

    async with async_session() as session:
        product = await session.get(Product, product_id)
        if not product:
            return await call.answer(PRODUCT_NOT_FOUND_TEXT, show_alert=True)

    await state.update_data(id=product.id)
    await call.message.answer(
        f"✏️ Редактирование товара: {product.name}\n\n" + INPUT_PRODUCT_NAME_TEXT + ":"
    )
    await state.set_state(ProductFSM.name)


@router.message(ProductFSM.name)
async def process_name(message: Message, state: FSMContext):
    data = await state.get_data()
    if not message.text.isalpha() and not (message.text == "-" and "id" in data):
        return await message.answer(PRODUCT_NAME_ATTENTION_TEXT + ":")
    elif "id" not in data:
        await state.update_data(name=message.text)
    await message.answer(INPUT_DESCRIPTION_TEXT + OPTIONAL_FIELD_TEXT + ":")
    await state.set_state(ProductFSM.description)


@router.message(ProductFSM.description)
async def process_description(message: Message, state: FSMContext):
    if not message.text == "-":
        await state.update_data(description=message.text)

    data = await state.get_data()
    if "id" in data:
        await message.answer(INPUT_PRICE_TEXT + OPTIONAL_FIELD_TEXT + ":")
    else:
        await message.answer(INPUT_PRICE_TEXT + ":")
    await state.set_state(ProductFSM.price)


@router.message(ProductFSM.price)
async def process_price(message: Message, state: FSMContext):
    data = await state.get_data()
    if not message.text == "-" or "id" not in data:
        try:
            price = format_text_in_price(message.text)
            await state.update_data(price=price)
        except ValueError:
            return await message.answer(PRICE_ATTENTION_TEXT + ":")

    await message.answer(INPUT_PHOTO_TEXT + OPTIONAL_FIELD_TEXT + ":")
    await state.set_state(ProductFSM.photo)


@router.message(ProductFSM.photo, F.text)
async def process_photo_text(message: Message, state: FSMContext):
    if message.text == "-":
        pass
    else:
        return await message.answer(PHOTO_ATTENTION_TEXT + ":")

    await show_category(message, state)


@router.message(ProductFSM.photo, F.photo)
async def process_photo(message: Message, state: FSMContext, bot: Bot):
    if message.photo:
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)

        file_path = f"{MEDIA_ROOT}/{photo.file_id}"
        await bot.download_file(file_info.file_path, file_path)
        await state.update_data(photo=f"{photo.file_id}")
    else:
        return await message.answer(PHOTO_ATTENTION_TEXT + ":")

    await show_category(message, state)


async def show_category(message: Message, state):
    async with async_session() as session:
        result = await session.execute(select(Category).order_by(Category.id))
        categories = result.scalars().all()

    if not categories:
        await message.answer(NO_CATEGORIES_TEXT + ". " + INPUT_NEW_CATEGORY_TEXT + ":")
        await state.set_state(ProductFSM.category_creation)

    header = f"{'ID':<5} {'Имя'}"
    rows = [f"{c.id:<5} {c.name}" for c in categories]
    table = "\n".join([header, "-" * 30, *rows])

    text = f"<b>📂 Список категорий</b>\n\n<pre>{table}</pre>"
    await message.answer(text, parse_mode=ParseMode.HTML)

    message = INPUT_CATEGORY_TEXT
    data = await state.get_data()
    if "id" in data:
        message += OPTIONAL_FIELD_TEXT

    await message.answer(message + ":")
    await state.set_state(ProductFSM.category)


@router.message(ProductFSM.category)
async def process_category(message: Message, state: FSMContext):
    cat_name_or_id = message.text.strip()
    if cat_name_or_id.isdigit():
        try:
            category_id = int(cat_name_or_id)
            async with async_session() as session:
                result = await session.execute(
                    select(Category).where(Category.id == category_id)
                )
                category = result.scalar_one_or_none()

            if not category:
                raise ValueError(f"Not found Category by {category_id} ID")
            await state.update_data(category=category.id)
        except ValueError:
            return await message.answer(
                CATEGORY_ATTENTION_TEXT + INPUT_NEW_CATEGORY_TEXT + ":"
            )
    elif cat_name_or_id != "-":
        async with async_session() as session:
            category = await get_or_create_category(session, cat_name_or_id)
            await state.update_data(category=category.id)
    else:
        data = await state.get_data()
        if "id" not in data:
            return await message.answer(CATEGORY_ATTENTION_TEXT)

    await send_product_summary(message, state)
    await state.set_state(ProductFSM.confirm)


@router.message(ProductFSM.category_creation)
async def process_category_creation(message: Message, state: FSMContext):
    cat_name = message.text.strip()
    if cat_name == "-" or cat_name.isdigit():
        return await message.answer(INPUT_NEW_CATEGORY_TEXT)
    else:
        async with async_session() as session:
            category = await get_or_create_category(session, cat_name)
            await state.update_data(category=category.id)

    await send_product_summary(message, state)
    await state.set_state(ProductFSM.confirm)


async def send_product_summary(message: Message, state):
    data = await state.get_data()
    category_name = None

    async with async_session() as session:
        if "category" in data:
            category = await session.get(Category, data["category"])
            category_name = category.name if category else "—"
        elif "id" in data:
            result = await session.execute(
                select(Category).join(Product).where(Product.id == data["id"])
            )
            category = result.scalar_one_or_none()
            category_name = category.name if category else "—"

    summary = (
        "✅ Подтвердите сохранение товара (да/нет):\n\n"
        f"Название: {data.get('name', '- (Без изменений)')}\n"
        f"Описание: {data.get('description', '- (Без изменений)')}\n"
        f"Цена: {data.get('price', '- (Без изменений)')}\n"
        f"Категория: {category_name}\n"
    )

    photo = data.get("photo")
    if photo:
        await message.answer_photo(
            photo=photo, caption=summary, reply_markup=confirm_product_kb
        )
    else:
        await message.answer(summary, reply_markup=confirm_product_kb)


@router.callback_query(F.data == PRODUCT_CONFIRM_CD, ProductFSM.confirm)
async def confirm_product(call: CallbackQuery, state: FSMContext, user: User | None):
    """Сохраняет созданный или отредактированный товар в базе."""
    data = await state.get_data()
    user_role = user.role if user else None

    async with async_session() as session:
        if "id" in data:
            product = await session.get(Product, data["id"])
            product.name = data.get("name", product.name)
            product.description = data.get("description", product.description)
            product.price = data.get("price", product.price)
            product.photo_filename = data.get("photo", product.photo_filename)
            product.category_id = data.get("category", product.category_id)
        else:
            product = Product(
                name=data["name"],
                description=data.get("description", None),
                price=data["price"],
                photo_filename=data.get("photo", None),
                category_id=data["category"],
            )
            session.add(product)

        await session.commit()

    await call.answer("✅ Товар сохранён")
    await state.clear()
    await call.message.edit_reply_markup(reply_markup=main_menu_kb(user_role))


@router.callback_query(F.data == PRODUCT_CANCEL_CD, ProductFSM.confirm)
async def cancel_product(call: CallbackQuery, state: FSMContext, user: User | None):
    """Отмена создания/редактирования товара."""
    user_role = user.role if user else None
    data = await state.get_data()
    photo = data.get("photo")
    await file_remove(photo)
    if "id" in data:
        text = CANCEL_UPDATE_PRODUCT_TEXT
    else:
        text = CANCEL_CREATE_PRODUCT_TEXT
    await state.clear()
    await call.message.answer(text, show_alert=True)
    await call.message.answer(MAIN_MENU, reply_markup=main_menu_kb(user_role))


@router.callback_query(ProductCD.filter(F.action == DELETE_ACTION))
async def delete_product(
    call: CallbackQuery, callback_data: ProductCD, user: User | None
):
    """Удаляет товар из базы."""
    user_role = user.role if user else None
    if user and user.role != UserRole.ADMIN:
        await create_non_admin_forbidden_message(call)
        return

    product_id = callback_data.id
    async with async_session() as session:
        product = await session.get(Product, product_id)
        if not product:
            return await call.answer(PRODUCT_NOT_FOUND_TEXT, show_alert=True)
        file = product.photo_filename
        await session.delete(product)
        await session.commit()
        await file_remove(file)

    await call.answer(PRODUCT_DELETED_TEXT, show_alert=False)
    await safe_delete_message(call.message)
    await call.message.answer(MAIN_MENU, reply_markup=main_menu_kb(user_role))
    await call.answer()


@router.callback_query(AdminCD.filter())
async def admin_change_status(
    call: CallbackQuery, callback_data: AdminCD, user: User | None
):
    """Позволяет администратору просматривать и изменять заказы."""
    if user and user.role != UserRole.ADMIN:
        await create_non_admin_forbidden_message(call)
        return

    async with async_session() as session:
        result = await session.execute(
            select(Order)
            .options(
                selectinload(Order.items).selectinload(OrderItem.product),
                selectinload(Order.pickup_point),
            )
            .where(Order.id == callback_data.order_id)
        )
        order = result.scalar_one_or_none()

        action = callback_data.action

        if action == VIEW_ACTION:
            await create_order_details_message(
                call, order, admin_change_status_kb(order.id)
            )
            return

        if action == SET_STATUS_ACTION:
            new_status = callback_data.order_status
            if order.status != new_status:
                order.status = new_status
                await session.commit()
                await call.answer(
                    f"Статус изменён на {order.status} ✅", show_alert=False
                )
                await create_order_details_message(
                    call, order, admin_change_status_kb(order.id)
                )
            await call.answer()

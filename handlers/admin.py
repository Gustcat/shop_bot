from aiofiles import os
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from config import MEDIA_ROOT
from db import async_session, Order, Product, Category, OrderItem
from keyboards.admin_kb import (
    AdminCD,
    admin_change_status_kb,
    confirm_product_kb,
    orders_kb,
)
from keyboards.catalog_kb import ProductCD
from keyboards.main_menu_kb import main_menu_kb
from utils.common_messages import create_order_details_message

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


@router.callback_query(F.data == "admin_create_product")
async def start_create_product(call: CallbackQuery, state: FSMContext, is_admin):
    if not is_admin:
        return await call.answer("Нет доступа ❌", show_alert=True)
    await call.message.answer("✏️ Введите название товара:")
    await state.set_state(ProductFSM.name)


@router.callback_query(ProductCD.filter(F.action == "delete"))
async def delete_product(call: CallbackQuery, callback_data: ProductCD, is_admin):
    if not is_admin:
        return await call.answer("Нет доступа ❌", show_alert=True)
    product_id = callback_data.id
    async with async_session() as session:
        product = await session.get(Product, product_id)
        if not product:
            return await call.answer("❌ Товар не найден", show_alert=True)
        file = product.photo_filename
        await session.delete(product)
        await session.commit()
        await file_remove(file)

    await call.answer("✅ Товар успешно удалён", show_alert=True)
    await call.message.delete()
    await call.message.answer("📋 Меню:", reply_markup=main_menu_kb(True))


@router.callback_query(ProductCD.filter(F.action == "edit"))
async def start_edit_product(
    call: CallbackQuery, callback_data: ProductCD, state: FSMContext, is_admin
):
    if not is_admin:
        return await call.answer("Нет доступа ❌", show_alert=True)
    product_id = callback_data.id

    async with async_session() as session:
        product = await session.get(Product, product_id)
        if not product:
            return await call.answer("❌ Товар не найден", show_alert=True)

    await state.update_data(id=product.id)
    await call.message.answer(
        f"✏️ Редактирование товара: {product.name}\n\n"
        "Введите новое название или отправьте `-`, чтобы оставить без изменений:"
    )
    await state.set_state(ProductFSM.name)


@router.message(ProductFSM.name)
async def process_name(message: Message, state: FSMContext):
    data = await state.get_data()
    if not message.text == "-" and "id" in data:
        await state.update_data(name=message.text)
    elif not message.text.isalpha():
        "⚠️ Введите только буквы для названия товара"
    await message.answer(
        "📝 Введите описание товара (или `-`, чтобы оставить без изменений):"
    )
    await state.set_state(ProductFSM.description)


@router.message(ProductFSM.description)
async def process_description(message: Message, state: FSMContext):
    if not message.text == "-":
        await state.update_data(description=message.text)

    data = await state.get_data()
    if "id" in data:
        await message.answer(
            "💰 Введите цену товара (число, в копейках) или `-`, чтобы оставить без изменений:"
        )
    else:
        await message.answer("💰 Введите цену товара (число, в копейках):")
    await state.set_state(ProductFSM.price)


@router.message(ProductFSM.price)
async def process_price(message: Message, state: FSMContext):
    # TODO: convert from rouble to kopeyka
    data = await state.get_data()
    if not message.text == "-" or "id" not in data:
        try:
            price = int(message.text)
            await state.update_data(price=price)
        except ValueError:
            return await message.answer("⚠️ Введите число для цены")

    await message.answer(
        "📸 Отправьте фото товара или `-`, чтобы оставить без изменений:"
    )
    await state.set_state(ProductFSM.photo)


@router.message(ProductFSM.photo, F.text)
async def process_photo(message: Message, state: FSMContext):
    print(f"<process_photo> enter for {message.text}")
    if message.text == "-":
        pass
    else:
        return await message.answer("⚠️ Отправьте фото или `-`")

    await show_category(message, state)


@router.message(ProductFSM.photo, F.photo)
async def process_photo(message: Message, state: FSMContext, bot: Bot):
    print(f"<process_photo> enter for {message.text}")
    if message.photo:
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)

        file_path = f"{MEDIA_ROOT}/{photo.file_id}"
        await bot.download_file(file_info.file_path, file_path)
        await state.update_data(photo=f"{photo.file_id}")
    else:
        return await message.answer("⚠️ Отправьте фото или `-`")

    await show_category(message, state)


async def show_category(message: Message, state):
    async with async_session() as session:
        result = await session.execute(select(Category).order_by(Category.id))
        categories = result.scalars().all()

    if not categories:
        await message.answer(
            "📂 Категории отсутствуют, введите название новой категории:"
        )
        await state.set_state(ProductFSM.category_creation)

    header = f"{'ID':<5} {'Имя'}"
    rows = [f"{c.id:<5} {c.name}" for c in categories]
    table = "\n".join([header, "-" * 30, *rows])

    text = f"<b>📂 Список категорий</b>\n\n<pre>{table}</pre>"
    await message.answer(text, parse_mode="HTML")
    await message.answer("📂 Укажите ID категории (число):")

    await state.set_state(ProductFSM.category)


@router.message(ProductFSM.category)
async def process_category(message: Message, state: FSMContext):
    if message.text.isdigit():
        try:
            category_id = int(message.text)
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
                "⚠️ Введите ID (число) категории. Для создания новой категории введите её название."
            )
    elif message.text != "-":
        await get_or_create_category(message, state)
    else:
        data = await state.get_data()
        if "id" not in data:
            return await message.answer(
                "️⚠️ У товара нет категории! Введите название категории"
            )

    await send_product_summary(message, state)
    await state.set_state(ProductFSM.confirm)


@router.message(ProductFSM.category_creation)
async def process_category_creation(message: Message, state: FSMContext):
    if message.text == "-" or message.text.isdigit():
        return await message.answer("️⚠️ Введите название категории")
    else:
        await get_or_create_category(message, state)

    await send_product_summary(message, state)
    await state.set_state(ProductFSM.confirm)


async def get_or_create_category(message: Message, state):
    async with async_session() as session:
        result = await session.execute(
            select(Category).where(Category.name == message.text.strip())
        )
        category = result.scalar_one_or_none()

        if not category:
            category = Category(name=message.text)
            session.add(category)
            await session.commit()
            await session.refresh(category)
    await state.update_data(category=category.id)


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


@router.callback_query(F.data == "product_confirm", ProductFSM.confirm)
async def confirm_product(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

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
    await call.message.edit_reply_markup(reply_markup=main_menu_kb(True))


@router.callback_query(F.data == "product_cancel", ProductFSM.confirm)
async def cancel_product(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    photo = data.get("photo")
    await file_remove(photo)

    await state.clear()
    await call.message.answer("Изменения отменены.", show_alert=True)
    await call.message.answer("📋 Меню:", reply_markup=main_menu_kb(True))


@router.callback_query(F.data == "admin_orders")
async def show_orders(call: CallbackQuery, is_admin):
    if not is_admin:
        return await call.answer("Нет доступа ❌", show_alert=True)
    async with async_session() as session:
        res = await session.execute(select(Order).order_by(Order.created_at))
        orders = res.scalars().all()

    if not orders:
        await call.answer("Заказы пока не добавлены.")
        return

    await call.message.edit_text("Заказы:", reply_markup=orders_kb(orders))


@router.callback_query(AdminCD.filter())
async def admin_change_status(call: CallbackQuery, callback_data: AdminCD, is_admin):
    if not is_admin:
        return await call.answer("Нет доступа ❌", show_alert=True)

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

        if callback_data.action == "view":
            await create_order_details_message(
                call, order, admin_change_status_kb(callback_data.order_id)
            )
            return

        if callback_data.action == "set_status":
            order.status = callback_data.order_status
            await session.commit()
            await call.answer(f"Статус изменён на {order.status} ✅", show_alert=True)
            await call.message.delete()
            await create_order_details_message(call, order, main_menu_kb(is_admin))

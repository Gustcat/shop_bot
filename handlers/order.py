import uuid

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from keyboards.main_menu_kb import main_menu_kb
from db import (
    DeliveryType,
    async_session,
    CartItem,
    Product,
    Order,
    OrderItem,
    PickupPoint,
    User,
    UserRole,
)
from keyboards.order_kb import (
    confirm_order_kb,
    delivery_kb,
    PickupCD,
    pickup_points_kb,
    OrderCD,
    detail_order_kb,
    orders_kb,
)
from repository.user import create_user
from utils.constants.callbacks import (
    ORDERS_CD,
    PLACE_ORDER_CD,
    DELIVERY_COURIER_CD,
    DELIVERY_PICKUP_CD,
    ORDER_CANCEL_CD,
    ORDER_CONFIRM_CD,
)
from utils.constants.message_text import (
    CART_EMPTY_TEXT,
    INPUT_USER_NAME_TEXT,
    PHONE_ATTENTION_TEXT,
    INPUT_PHONE_TEXT,
    CHOOSE_DELIVERY_TYPE_TEXT,
    INPUT_ADDRESS_TEXT,
    NO_PICKUP_POINTS_TEXT,
    CHOOSE_PICKUP_POINT_TEXT,
)
from utils.formatting import format_price_in_text
from utils.messaging import create_order_details_message

router = Router()


class OrderFSM(StatesGroup):
    name = State()
    phone = State()
    address = State()
    delivery_type = State()
    pickup_point_id = State()
    confirm = State()


@router.callback_query(F.data == PLACE_ORDER_CD)
async def start_order(call: CallbackQuery, state: FSMContext, user: User | None):
    """
    Запуск оформления заказа из корзины.
    """
    async with async_session() as session:
        if not user:
            user = await create_user(session, call.from_user)
        user_id = user.id

        result = await session.execute(
            select(CartItem).where(CartItem.user_id == user_id)
        )
        cart_items = result.scalars().all()

    if not cart_items:
        await call.answer(CART_EMPTY_TEXT, show_alert=True)
        return

    await call.message.answer(INPUT_USER_NAME_TEXT)
    await state.set_state(OrderFSM.name)


@router.message(OrderFSM.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(INPUT_PHONE_TEXT)
    await state.set_state(OrderFSM.phone)


@router.message(OrderFSM.phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    if phone.startswith("+7"):
        phone = "8" + phone[2:]

    if not phone.isdigit():
        await message.answer(PHONE_ATTENTION_TEXT)
        return

    await state.update_data(phone=phone)
    await message.answer(CHOOSE_DELIVERY_TYPE_TEXT, reply_markup=delivery_kb)
    await state.set_state(OrderFSM.delivery_type)


@router.callback_query(F.data == DELIVERY_COURIER_CD, OrderFSM.delivery_type)
async def choose_courier(call: CallbackQuery, state: FSMContext):
    await state.update_data(delivery_type=DeliveryType.COURIER)
    await call.message.answer(INPUT_ADDRESS_TEXT)
    await state.set_state(OrderFSM.address)
    await call.answer()


@router.callback_query(F.data == DELIVERY_PICKUP_CD, OrderFSM.delivery_type)
async def choose_pickup(call: CallbackQuery, state: FSMContext):
    await state.update_data(delivery_type=DeliveryType.PICKUP)
    async with async_session() as session:
        result = await session.execute(select(PickupPoint))
        points = result.scalars().all()

    if not points:
        await call.answer(NO_PICKUP_POINTS_TEXT, show_alert=True)
        return

    await call.message.answer(
        CHOOSE_PICKUP_POINT_TEXT, reply_markup=pickup_points_kb(points)
    )
    await state.set_state(OrderFSM.pickup_point_id)
    await call.answer()


@router.message(OrderFSM.address)
async def process_address(message: Message, state: FSMContext, user: User | None):
    await state.update_data(address=message.text)

    async with async_session() as session:
        if not user:
            user = await create_user(session, message.from_user)
        user_id = user.id
        await send_order_summary(message, state, session, user_id)

    await state.set_state(OrderFSM.confirm)


@router.callback_query(PickupCD.filter(), OrderFSM.pickup_point_id)
async def pickup_selected(
    call: CallbackQuery, state: FSMContext, callback_data: PickupCD, user: User | None
):
    await state.update_data(pickup_point_id=callback_data.id)

    async with async_session() as session:
        if not user:
            user = await create_user(session, call.from_user)
        user_id = user.id
        await send_order_summary(call, state, session, user_id)

    await state.set_state(OrderFSM.confirm)
    await call.answer()


async def send_order_summary(
    target: Message | CallbackQuery, state, session: AsyncSession, user_id: int
):
    """
    Формирует и отправляет итоговое сообщение с заказом.
    Поддерживает курьера и самовывоз.
    """
    data = await state.get_data()

    result = await session.execute(select(CartItem).where(CartItem.user_id == user_id))
    cart_items = result.scalars().all()

    summary_lines = []
    total = 0

    for item in cart_items:
        product = await session.get(Product, item.product_id)
        if not product:
            continue
        cost = product.price * item.quantity
        total += cost
        summary_lines.append(
            f" - {product.name} ({item.quantity} шт.) — {format_price_in_text(cost)}"
        )

    delivery_text = ""
    if data.get("delivery_type") == DeliveryType.COURIER:
        delivery_text = f"🏠 Адрес: {data.get('address')}"
    elif data.get("delivery_type") == DeliveryType.PICKUP:
        pickup_point = await session.get(PickupPoint, data.get("pickup_point_id"))
        if pickup_point:
            delivery_text = f"🏬 Самовывоз: {pickup_point.name}, {pickup_point.address}"

    summary = (
        "Подтвердите заказ:\n\n"
        "🛒 Товары:\n"
        + "\n".join(summary_lines)
        + f"\n\nИтого: {format_price_in_text(total)}\n\n"
        f"👤 Имя: {data.get('name')}\n"
        f"📞 Телефон: {data.get('phone')}\n"
        f"{delivery_text}"
    )

    if isinstance(target, CallbackQuery):
        await target.message.answer(summary, reply_markup=confirm_order_kb)
    else:
        await target.answer(summary, reply_markup=confirm_order_kb)


@router.callback_query(F.data == ORDER_CONFIRM_CD, OrderFSM.confirm)
async def confirm_order(call: CallbackQuery, state: FSMContext, user: User | None):
    data = await state.get_data()

    async with async_session() as session:
        if not user:
            user = await create_user(session, call.from_user)
        user_id = user.id

        result = await session.execute(
            select(CartItem).where(CartItem.user_id == user_id)
        )
        cart_items = result.scalars().all()

        if not cart_items:
            await call.answer(CART_EMPTY_TEXT, show_alert=True)
            await state.clear()
            return

        order = Order(
            order_uuid=uuid.uuid4(),
            user_id=user_id,
            name=data.get("name"),
            phone=data.get("phone"),
            delivery_type=data.get("delivery_type"),
        )

        if data.get("delivery_type") == DeliveryType.COURIER:
            order.address = data.get("address")

        elif data.get("delivery_type") == DeliveryType.PICKUP:
            order.pickup_point_id = data.get("pickup_point_id")

        session.add(order)
        await session.flush()

        for item in cart_items:
            product = await session.get(Product, item.product_id)
            if not product:
                continue
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                product_price=product.price,
                quantity=item.quantity,
            )
            session.add(order_item)

        await session.execute(delete(CartItem).where(CartItem.user_id == user_id))

        await session.commit()

    await call.message.answer(
        f"Спасибо за заказ! Номер заказа: {order.order_uuid}",
        reply_markup=main_menu_kb(user_role=user.role),
    )
    await state.clear()
    await call.answer()


@router.callback_query(F.data == ORDER_CANCEL_CD, OrderFSM.confirm)
async def cancel_order(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer("Заказ отменён.")
    await call.answer()


@router.callback_query(F.data == ORDERS_CD)
async def show_orders(call: CallbackQuery, user: User | None):
    async with async_session() as session:
        if not user:
            user = await create_user(session, call.from_user)
        q = select(Order).order_by(Order.created_at.desc())
        if user.role != UserRole.ADMIN:
            q = q.where(Order.user_id == user.id)
        res = await session.execute(q)
        orders = res.scalars().all()

        if not orders:
            await call.answer("Заказов нет 📭", show_alert=False)
            return

        await call.message.edit_text(
            "Заказы:", reply_markup=orders_kb(orders, user.role)
        )
        await call.answer()


@router.callback_query(OrderCD.filter())
async def show_detail_order(
    call: CallbackQuery, callback_data: OrderCD, user: User | None
):
    order_id = callback_data.id

    async with async_session() as session:
        if not user:
            user = await create_user(session, call.from_user)
        user_id = user.id

        result = await session.execute(
            select(Order)
            .options(
                selectinload(Order.items).selectinload(OrderItem.product),
                selectinload(Order.pickup_point),
            )
            .where(Order.id == order_id, Order.user_id == user_id)
        )
        order = result.scalar_one_or_none()
    await create_order_details_message(call, order, detail_order_kb)
    await call.answer()

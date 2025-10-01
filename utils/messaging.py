from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery

from db import Order
from utils.common_messages import get_order_details_text


async def safe_delete_message(message: Message):
    """
    Попытка удалить сообщение, если нельзя — просто игнорируем.
    """
    try:
        await message.delete()
    except TelegramBadRequest:
        pass


async def update_or_replace_message(
    message: Message, text: str, reply_markup: InlineKeyboardMarkup | None = None
):
    """
    Обновляет текст сообщения, если оно текстовое.
    Если в сообщении фото — удаляет и отправляет новое.
    """
    if message.photo:
        await safe_delete_message(message)
        await message.answer(text, reply_markup=reply_markup)
    else:
        await message.edit_text(text, reply_markup=reply_markup)


async def create_non_admin_forbidden_message(call: CallbackQuery):
    """Отправление сообщения о том, что у пользователя нет прав администратора."""
    return await call.answer("Нет доступа ❌", show_alert=True)


async def create_order_details_message(
    call: CallbackQuery, order: Order | None, kb: InlineKeyboardMarkup | None = None
):
    """Отправление сообщения с деталями заказа."""
    if not order:
        await call.answer("Заказ не найден", show_alert=True)
        return
    text = await get_order_details_text(order)
    await call.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)

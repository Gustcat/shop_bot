from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, InlineKeyboardMarkup


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

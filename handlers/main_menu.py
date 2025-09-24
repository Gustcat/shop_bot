from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards.main_menu_kb import main_menu_kb, main_reply_kb

router = Router()


@router.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer(
        "Добро пожаловать! Используй кнопку «Главное меню» внизу 👇",
        reply_markup=main_reply_kb,
    )


@router.message(F.text == "Главное меню")
async def back_to_main_message(message: Message, is_admin):
    text = "Главное меню:"
    await message.answer(text, reply_markup=main_menu_kb(is_admin=is_admin))


@router.callback_query(F.data == "menu")
async def back_to_main_callback(call: CallbackQuery, is_admin):
    text = "Главное меню:"
    if call.message.photo:
        await call.message.delete()
        await call.message.answer(text, reply_markup=main_menu_kb(is_admin=is_admin))
    else:
        await call.message.edit_text(text, reply_markup=main_menu_kb(is_admin=is_admin))

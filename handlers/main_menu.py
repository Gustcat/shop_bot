from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards.main_menu_kb import main_menu_kb

router = Router()


@router.message(F.text == "/start")
async def start_cmd(message: Message):
    await message.answer("Добро пожаловать в магазин!", reply_markup=main_menu_kb)


@router.callback_query(F.data == "menu")
async def back_to_main(call: CallbackQuery):
    text = "Главное меню:"
    if call.message.photo:
        await call.message.delete()
        await call.message.answer(
            text,
            reply_markup=main_menu_kb,
        )
    else:
        await call.message.edit_text(
            text,
            reply_markup=main_menu_kb,
        )

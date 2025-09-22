from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="🛍 Каталог", callback_data="catalog")]]
)

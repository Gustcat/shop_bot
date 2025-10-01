from aiogram.types import InlineKeyboardButton

from utils.constants.buttons import MAIN_MENU, CART, BACK
from utils.constants.callbacks import MAIN_MENU_CD, CART_CD, ORDERS_CD

MAIN_MENU_BUTTON = InlineKeyboardButton(text=MAIN_MENU, callback_data=MAIN_MENU_CD)
CART_BUTTON = InlineKeyboardButton(text=CART, callback_data=CART_CD)
BACK_TO_LIST_ORDERS_BUTTON = InlineKeyboardButton(text=BACK, callback_data=ORDERS_CD)

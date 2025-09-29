from aiogram.types import InlineKeyboardButton

from utils.constants.buttons import MAIN_MENU, CART
from utils.constants.callbacks import MAIN_MENU_CD, CART_CD

MAIN_MENU_BUTTON = InlineKeyboardButton(text=MAIN_MENU, callback_data=MAIN_MENU_CD)
CART_BUTTON = InlineKeyboardButton(text=CART, callback_data=CART_CD)

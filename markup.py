from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


start_button = InlineKeyboardBuilder()
start_button.button(text='BITCOIN')
start_button.button(text='TONCOIN')
start_button.button(text='BLOCKCHAINS')

checker_button = InlineKeyboardBuilder()
checker_button.button(text='LAUNCH CHECKER')
checker_button.button(text='CHANGE PARAMETERS')
checker_button.button(text='STOP')

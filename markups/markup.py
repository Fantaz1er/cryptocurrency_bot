# -*- coding: utf-8 -*-
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton)

__all__ = ["start_kb", "choice_crypt", "button_request"]

button_start_setting = [
    [InlineKeyboardButton(text="🇬🇧", callback_data="code_en")],
    [InlineKeyboardButton(text="🇷🇺", callback_data="code_ru")],
]

start_kb = InlineKeyboardMarkup(
    inline_keyboard=button_start_setting,
)

choice_crypt = [
    [KeyboardButton(text="Toncoin (ton)")],
    [KeyboardButton(text="Bitcoin (btc)")],
]

run_checker = ReplyKeyboardMarkup(
    keyboard=choice_crypt,
    resize_keyboard=True,
    input_field_placeholder="Choice the cryptocurrency for run checker about needed category"
)

button_request_green_code = [
    [InlineKeyboardButton(text='✅', callback_data='code_green')],
    [InlineKeyboardButton(text='❌', callback_data='code_red')],
]

button_request = InlineKeyboardMarkup(
    inline_keyboard=button_request_green_code,
)

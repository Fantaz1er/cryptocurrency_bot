from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from cfg import config

bot = Bot(config.bot_token, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

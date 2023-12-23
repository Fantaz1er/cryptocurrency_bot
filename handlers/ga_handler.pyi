# -*- coding: utf-8 -*-
# Add ga_handler.py in 'handlers' folder,
# so you can use the chief admin panel from chatbot
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from cryptocurrency_bot.filters.ga_admin import IsGAAdmin  # type: ignore

ga_router = Router(name="ga_router")

@ga_router.message(Command(
    commands="isAdmin", prefix="_"
), IsGAAdmin())
async def isAdmin(message: Message) -> None: ...

@ga_router.message(Command(
    commands="upperAdmin", prefix="_"
), IsGAAdmin())
async def upperAdmin(message: Message) -> None: ...

@ga_router.message(Command(
    commands="leaveAdmin", prefix="_"
), IsGAAdmin())
async def leaveAdmin(message: Message) -> None: ...

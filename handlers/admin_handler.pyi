# -*- coding:utf-8 -*-
# Add admin_handler.py in 'handlers' folder,
# so you can use the admin panel from chatbot
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from cryptocurrency_bot.filters.admin import IsAdmin

admin_router = Router(name="admin_router")

@admin_router.message(Command(
    commands="stopMainTask", prefix="_", ignore_case=True
), IsAdmin())
async def stopMainTask(message: Message) -> None: ...

@admin_router.callback_query(lambda c: c.data == "code_green")
async def stopMainTaskYes(callback: CallbackQuery) -> None: ...

@admin_router.callback_query(lambda c: c.data == "code_red")
async def stopMainTaskNo(callback: CallbackQuery) -> None: ...

@admin_router.message(Command(
    commands="stopJobs", prefix="_", ignore_case=True
), IsAdmin())
async def stopJobs(message: Message) -> None: ...

@admin_router.message(Command(
    commands="stopLastActivityChecker", prefix="_", ignore_case=True
), IsAdmin())
async def stopLastActivityChecker(message: Message) -> None: ...

@admin_router.message(Command(
    commands="runTaskWithJob", prefix="_", ignore_case=True
), IsAdmin())
async def runTaskWithJob(message: Message) -> None: ...

@admin_router.message(Command(
    commands="deleteUser", prefix="_", ignore_case=True
), IsAdmin())
async def deleteUser(message: Message) -> None: ...

# -*- coding: utf-8 -*-
import aioschedule as schedule
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from filters.superuser import IsSuperUser
from language.exec import get_admin_answers

superuser_router = Router(name="superuser_router")


@superuser_router.message(Command(
    commands="getCurrentJobs", prefix="_", ignore_case=True
), IsSuperUser())
async def getCurrentJobs(message: Message):
    await message.answer(
        (await get_admin_answers(message.from_user.id))['get_count_checkers'] % len(schedule.jobs)
    )

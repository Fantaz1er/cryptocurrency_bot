# -*- coding: utf-8 -*-
from typing import Optional
from aiogram.filters import Filter
from aiogram.types import Message

from cryptocurrency_bot.db.adminbase import db_check_is_admin
from cryptocurrency_bot.language.exec import get_admin_answers


class IsAdmin(Filter):
    async def __call__(self, message: Message) -> Optional[bool]:
        if db_check_is_admin(message.from_user.id) >= 2:
            return True
        await message.answer((await get_admin_answers(message.from_user.id))["not_allowed"])
        return False

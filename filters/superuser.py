# -*- coding: utf-8 -*-
from typing import Optional
from aiogram.filters import Filter
from aiogram.types import Message

from db.adminbase import db_check_is_admin
from language.exec import get_user_functional_answers


class IsSuperUser(Filter):
    async def __call__(self, message: Message) -> Optional[bool]:
        if db_check_is_admin(message.from_user.id) >= 1:
            return True
        await message.answer(
            (await get_user_functional_answers(message.from_user.id, "superuser"))["not_allowed"]
        )
        return False

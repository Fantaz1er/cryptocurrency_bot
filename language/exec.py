# -*- coding: utf-8 -*-
from json import load
from typing import Optional, Union

from db.userbase import db_get_language_code

__all__ = ["get_admin_answers", "get_ga_admin_answers", "get_user_functional_answers"]

with open('./language/languages.json', "r", encoding="UTF-8") as language_init:
    languages = load(language_init)


async def get_admin_answers(admin_id: Optional[int]) -> Optional[dict]:
    return languages[db_get_language_code(admin_id)]["admin"]


async def get_ga_admin_answers(ga_admin_id: Optional[int]) -> Optional[dict]:
    return languages[db_get_language_code(ga_admin_id)]["ga_admin"]


async def get_user_functional_answers(
        user_id: Optional[int], functional: Optional[str]
) -> Union[Optional[dict], Optional[str]]:
    return languages[db_get_language_code(user_id)][functional]

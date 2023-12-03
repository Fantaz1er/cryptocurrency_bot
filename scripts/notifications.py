# -*- coding: utf-8 -*-
import aioschedule as schedule
import time
import asyncio

from typing import Optional, Union

from scripts.blockchains import Blockchains
from db.userbase import *
from language.exec import get_user_functional_answers

coins = Blockchains()


def getCurrentTime() -> Optional[str]:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))


async def runCheckers() -> None:
    try:
        while True:
            await schedule.run_pending()
            if not schedule.jobs:
                break
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        return


def checkLastActivity(bot) -> None:
    schedule.every().day.at("00:00").do(
        job_func=check_last_activity,
        bot=bot
    ).tag("activityChecker")


async def runCheckerIfDisable() -> None:
    if len(schedule.jobs) == 1:
        await asyncio.create_task(runCheckers(), name="MAIN")


async def cancel_checker(identifier: Union[str, int]) -> Optional[bool]:
    if db_get_user_state(identifier):
        for job in schedule.jobs:
            if str(identifier) in job.tags:
                schedule.cancel_job(job)
                return True
    return False


async def set_parameters(params: Union[list, tuple]) -> Optional[tuple]:
    try:
        limit, timer = params[1], int(params[2])
    except IndexError:
        limit, timer = '5', 5
    if ',' in limit:
        limit.replace(',', '.')
    limit = 1 - (float(limit) if '.' in limit else int(limit) / 100)
    return limit, timer


# ANSWERS
async def check_rise_toncoin(bot, _special_id: Union[int, str], _limit: Union[int, float]) -> None:
    """Get notification to telegram if toncoin rise around limit context parameter percent after start a program
    :param bot: bot from `main`
    :param _special_id Union[int, str]
    :param _limit Union[int, float]
    :return None
    """
    value = coins.toncoin_price_online()
    percent = db_get_last_value(_special_id) / value[0]
    if 0 < percent < _limit:
        await bot.send_message(
            chat_id=_special_id,
            text=f"{'RISE, TONCOIN RISE:'}\n\nValue: {value[0]:,} $ ({value[2]:,} ₽)\n"
                 f"Actual: {value[1]}"
        )
        db_edit_last_value(_special_id, value[0])


async def check_last_activity(bot) -> None:
    """Ban user if he was in inactivity one day (86400 seconds = 24 hours)"""
    users_activity = db_get_last_activity()
    for activ in users_activity:
        if round(time.time()) - activ[0] < 86400 and not db_get_user_state(activ[1]):
            db_delete_user(activ[1])
            await bot.send_message(activ[1], await get_user_functional_answers(activ[1], "ban"))

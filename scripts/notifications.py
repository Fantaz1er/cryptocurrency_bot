# -*- coding: utf-8 -*-
import asyncio
import time
from typing import Union, Optional

import aioschedule as schedule
from cryptocurrency_bot.db.userbase import *

from cryptocurrency_bot.bot import bot
from cryptocurrency_bot.exceptions.exceptions import *
from cryptocurrency_bot.language.exec import get_user_functional_answers
from cryptocurrency_bot.scripts.blockchains import Blockchains

coins = Blockchains()

__all__ = ['coins', 'get_current_time', 'runCheckers', 'runCheckerIfDisable', 'run_main_task',
           'cancel_checker', 'checkLastActivity', 'stop_jobs', 'stop_last_activity_checker',
           'set_parameters', 'check_rise_toncoin', 'change_user_state', 'stop_main_task',
           'delete_user']


def get_current_time() -> Optional[str]:
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
async def check_rise_toncoin(_special_id: Union[int, str], _limit: Union[int, float]) -> None:
    """Get notification to telegram if toncoin rise around limit context parameter percent after start a program
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


async def check_last_activity() -> None:
    """Ban user if he was in inactivity one day (86400 seconds = 24 hours)"""
    users_activity = db_get_last_activity()
    for activ in users_activity:
        if round(time.time()) - activ[0] < 86400 and not db_get_user_state(activ[1]):
            db_delete_user(activ[1])
            await bot.send_message(activ[1], await get_user_functional_answers(activ[1], "ban"))


async def checkLastActivity() -> None:
    schedule.every().day.at("00:00").do(
        job_func=check_last_activity,
    ).tag("activityChecker")


async def stop_last_activity_checker() -> None:
    for job in schedule.jobs:
        if job.tags[0] == "activityChecker":
            schedule.cancel_job(job)
            return
    else:
        raise StopJobError("not find 'lastActivity' job")


async def change_user_state(user_id: Optional[int]) -> None:
    db_edit_user_state(user_id, False)
    bot.send_message(user_id, await get_user_functional_answers(user_id, "stopJob"))


async def stop_jobs() -> None:
    for job in schedule.jobs:
        if job.tags == 'activityChecker':
            continue
        schedule.cancel_job(job)
        await change_user_state(job.tags[0])
    else:
        raise StopJobError("There are not active jobs. Nothing to stop")


async def stop_main_task() -> None:
    for task in asyncio.all_tasks():
        if task.get_name() == "MAIN":
            task.cancel()
            return
    else:
        raise StopMainTaskError("Couldn't find the process of the main task")


async def run_main_task() -> None:
    for task in asyncio.all_tasks():
        if task.get_name() == "MAIN":
            raise RunMainTaskError("couldn't run the task... this task run yet")
    if schedule.jobs == 0:
        await checkLastActivity()
    await runCheckerIfDisable()


async def delete_user(user_id: Optional[int]) -> None:
    if db_get_user_state(user_id):
        raise DeleteUserError("user have activ function")
    await bot.send_message(
        chat_id=user_id, text=(await get_user_functional_answers(user_id, 'ban'))
    )
    db_delete_user(user_id)

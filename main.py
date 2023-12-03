# -*- coding: utf-8 -*-
import asyncio
import logging

from sys import stdout, platform
from nest_asyncio import apply

from scripts.notifications import runCheckers, checkLastActivity
from handlers import admin_handler, main_handler, ga_handler, superuser_handler  # import routers
from bot import dp, bot


async def runBot():
    dp.include_routers(
        ga_handler.ga_router, admin_handler.admin_router, superuser_handler.superuser_router, main_handler.router
    )  # routers
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


def run():
    checkLastActivity(bot)
    try:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            loop.create_task(runCheckers(), name='MAIN')
            loop.run_until_complete(runBot())
        else:
            apply(loop)  # nest_asyncio
            loop.create_task(runCheckers(), name='MAIN')
            loop.run_until_complete(runBot())
    except KeyboardInterrupt:
        logging.warning("Finished")


if __name__ == '__main__':
    if platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # for Windows systems
    logging.basicConfig(level=logging.INFO, stream=stdout)
    run()

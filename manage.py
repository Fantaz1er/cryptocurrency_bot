# -*- coding: utf-8 -*-
import asyncio
import logging
import click
import typing
from sys import stdout, platform

from nest_asyncio import apply

from bot import dp, bot, config
from handlers import admin_handler, main_handler, ga_handler, superuser_handler  # import routers
from scripts.notifications import runCheckers, checkLastActivity
from cryptocurrency_bot.db.adminbase import db_add_new_administrator


async def runBot() -> None:
    dp.include_routers(
        ga_handler.ga_router, admin_handler.admin_router, superuser_handler.superuser_router, main_handler.router
    )  # routers
    await checkLastActivity()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


@click.group()
@click.version_option(version="0.01", prog_name="cryptocurrency-bot")
def main() -> None:
    """Add registration form for cryptocurrency chatbot"""
    pass


@main.command()
@click.option("--logg", "-lg", default=True, help="logging all in command line")
def run(logg: typing.Optional[bool]) -> None:
    if logg:
        logging.basicConfig(level=logging.INFO, stream=stdout)
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


@main.command()
@click.option("--rang", "-rg", default=1, prompt=True, help="start administrator level")
@click.option("--admin_id", "-id", prompt=True, help="ID in admin list")
def add_admin(rang: typing.Optional[int], admin_id: typing.Optional[typing.Union[str, int]]) -> None:
    click.echo(f'User {admin_id} was added in admin list on {rang} level!')
    db_add_new_administrator(admin_id, rang)


@main.command()
@click.argument("ga_id")
def add_ga_admin(ga_id: typing.Optional[typing.Union[str, int]]) -> None:
    if int(ga_id) in config.ga_ids:
        click.echo("User was added in GA admin list")
        db_add_new_administrator(ga_id, 6)


if __name__ == '__main__':
    # For Windows systems
    if platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    main()

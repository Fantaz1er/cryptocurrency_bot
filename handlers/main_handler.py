# -*- coding: utf-8 -*-
import asyncio
import logging
from time import time, gmtime, strftime

import aioschedule as schedule
from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hbold

from cryptocurrency_bot.db.userbase import *
from cryptocurrency_bot.handlers.commands import *
from cryptocurrency_bot.markups.markup import start_kb
from cryptocurrency_bot.scripts.notifications import *


router = Router(name="main")


@router.message(Command(
    commands=blockchains_cmd,
    prefix='/',
    ignore_case=True,
))
async def getBlockchainsValueHighAvg(message: Message) -> None:
    """
    This async function give to user information about blockchains who himself input in Telegram_Bot chat
    :param message: current message who user send to Telegram bot
    :return: Serialized data from open API blockchains "Yobit"
    """
    tickers = message.text.split()[1::]
    if not tickers:
        await message.reply('No enter tickers!')
        return
    serialized = coins.blockchains_price(tickers)
    print(serialized)
    for ticker in tickers:
        data = serialized.get(ticker, {"error": "Not Found", "code": 404})
        curr = ticker.split("_")[-1].upper()
        await message.answer(f"""The high: {data['high']:,} {curr}
The low {data['low']:,} {curr}
Updated: {hbold(strftime("%d.%m.%Y %H:%M:%S", gmtime(data['updated'])))}""")


@router.message(Command(
    commands=btc_avg_cmd,
    prefix='/',
    ignore_case=True
))
async def getBitcoinValueAvg(message: Message):
    await message.answer(f"{hbold('BITCOIN AVERAGE:')}\n"
                         f"The high: {coins.bitcoin_price_avg():,} $"
                         f"\nUpdated: {hbold(coins.updateTime)}")


@router.message(Command(
    commands=btc_online_cmd,
    prefix='/',
    ignore_case=True
))
async def getBitcoinValueOnline(message: Message):
    r = coins.bitcoin_price_online()
    await message.answer(f"{hbold('BITCOIN ONLINE:')}\n"
                         f"Value: {r[0]:,} $ ({r[2]:,} ₽)"
                         f"\nActual: {hbold(r[1])}")


@router.message(Command(
    commands=btc_high_cmd,
    prefix='/',
    ignore_case=True
))
async def getBitcoinValueHigh(message: Message):
    await message.answer(f"{hbold('BITCOIN HIGH:')}\n"
                         f"The high: {coins.bitcoin_price_high():,} $"
                         f"\nUpdated: {hbold(coins.updateTime)}")


@router.message(Command(
    commands=toncoin_cmd,
    prefix='/',
    ignore_case=True
))
async def getToncoinValueOnline(message: Message):
    r = coins.toncoin_price_online()
    await message.answer(f"{hbold('TONCOIN ONLINE:')}\n"
                         f"Value: {r[0]:,} $ ({r[2]:,} ₽)"
                         f"\nActual: {hbold(r[1])}")


@router.message(Command(
    commands=toncoin_avg_cmd,
    prefix='/',
    ignore_case=True
))
async def getToncoinValueAverage(message: Message):
    await message.answer(f"{hbold('TONCOIN AVERAGE:')}\n"
                         f"Value: {coins.toncoin_price_avg():,} $"
                         f"\nActual: {hbold(coins.updateTime)}")


@router.message(Command(
    commands=toncoin_high_cmd,
    prefix='/',
    ignore_case=True
))
async def getToncoinValueHigh(message: Message):
    await message.answer(f"{hbold('TONCOIN HIGH:')}\n"
                         f"Value: {coins.toncoin_price_high():,}$"
                         f"\nActual: {coins.updateTime}")


# Auto checker. Do every timer compare how much cost toncoin (while only toncoin cryptocurrency)
# If cost rise higher limit, bot send message user (notification user about that)
# Else pass steps and checking in the next minutes (timer)
@router.message(Command(
    commands=stop_checker,
    prefix='/',
    ignore_case=True
))
async def stopChecker(message: Message):
    if await cancel_checker(message.chat.id):
        logging.info(f'AUTOCHECKER: STOP JOB (TIME: {get_current_time()}, ID: {message.chat.id})')
        db_edit_user_state(message.chat.id, False)
        await message.answer(f"Checker {hbold('OFF')}")
        return
    await message.answer(f"Checker {hbold('isn`t run')}")


@router.message(Command(
    commands=change_parameters,
    prefix='/',
    ignore_case=True
))
async def changeParameters(message: Message):
    await cancel_checker(message.chat.id)
    limit, timer = await set_parameters(message.text.split())
    await message.answer(f'Checker with new parameters {hbold("launched")}\n'
                         f'Parameters: {hbold(limit)}% and {hbold(timer)} minutes')
    logging.info(f'AUTOCHECKER: RUN WITH NEW PARAMETERS(_limit={limit}, _timer={timer}) ({get_current_time()})')
    schedule.every(timer).minutes.do(
        check_rise_toncoin,
        _limit=limit,
        _special_id=message.chat.id
    ).tag(str(message.chat.id))
    if len(schedule.jobs) == 1:
        asyncio.create_task(runCheckers(), name="MAIN")
    db_edit_user_state(message.chat.id, True)
    db_edit_last_value(message.chat.id, coins.toncoin_price_online()[0])


@router.message(Command(
    commands=run_checker,
    prefix='/',
    ignore_case=True
))
async def runChecker(message: Message):
    if db_get_user_state(message.chat.id):
        await message.answer("Can't launch new job for checker...\n" +
                             hbold(f"Please shutdown the current job or use:\n"
                                   f"/parameters [limit] [timer]"))
        return
    limit, timer = await set_parameters(message.text.split())
    await message.answer(f'Checker is {hbold("launched")}'
                         f'\nParameters: {hbold(limit)}% and {hbold(timer)} minutes')
    logging.info(f'AUTOCHECKER: RUN(_limit={limit}, _timer={timer}) ({get_current_time()})')
    schedule.every(timer).minutes.do(
        check_rise_toncoin,
        _limit=limit,
        _special_id=message.chat.id
    ).tag(str(message.chat.id))
    if len(schedule.jobs) == 1:
        asyncio.create_task(runCheckers(), name="MAIN")
    db_edit_last_value(message.chat.id, coins.toncoin_price_online()[0])
    db_edit_user_state(message.chat.id, True)


# CALLBACKS from inline buttons.
# Inline buttons have a code, after you pressed on button
# this code uses here
@router.callback_query(lambda c: c.data == 'code_en')
async def setLanguageEnglish(callback_query: CallbackQuery):
    await callback_query.message.edit_text("You set English language")
    db_edit_language_code(callback_query.from_user.id, "en")


@router.callback_query(lambda c: c.data == "code_ru")
async def setLanguageRussian(callback_query: CallbackQuery):
    await callback_query.message.edit_text("Вы установили Русский язык")
    db_edit_language_code(callback_query.from_user.id, "ru")


# Start function, when user starting work with bot
# answers simply welcome message and request from user
# language who he wants to use while working with bot
@router.message(CommandStart())
async def onStart(message: Message):
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!\n"
                         "Now you can get notifications from me about rise the toncoin crypt...\n"
                         f"Your chat id: {hbold(message.chat.id)}\n"
                         f"/run for run checker toncoin crypt with next params: {hbold('5%')}"
                         f" rise and {hbold('5 minutes')} timer", reply_markup=start_kb)
    db_create_new_user(message.from_user.id, message.chat.id, int(time()))

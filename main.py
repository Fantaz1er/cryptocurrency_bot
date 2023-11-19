import asyncio
import logging
import sys
import nest_asyncio
import time
import aioschedule as schedule

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.fsm.storage.memory import MemoryStorage
from os import getenv
from dotenv import load_dotenv
from typing import Union
from currency_converter import CurrencyConverter

from commands import *
from database import *
from blockchains import *

load_dotenv(".env")
API_TOKEN = getenv("API_KEY")
bot = Bot(API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
ton = Toncoin()
btc = Bitcoin()
blockchains = Blockchains()
currency = CurrencyConverter()


def getCurrentTime():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))


async def check_rise_toncoin(_special_id: Union[int, str], _limit: Union[int, float]):
    """Get notification to telegram if toncoin rise around limit context parameter percent after start a program
    :param _special_id Union[int, str]
    :param _limit Union[int, float]
    :return None
    """
    value = ton.toncoin_price_online()
    percent = db_get_last_value(_special_id) / value[0]
    if 0 < percent < _limit:
        await bot.send_message(
            chat_id=_special_id,
            text=f"{hbold('RISE, TONCOIN RISE:')}\n\nValue: {hbold(value[0])} $ ({hbold(value[2])} ₽)\n"
                 f"Actual: {value[1]}"
        )
        db_edit_last_value(_special_id, value[0])


async def runToncoinChecker():
    try:
        while True:
            await schedule.run_pending()
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        pass


@dp.message(Command(
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
    serialized = blockchains.blockchains_price(tickers)
    print(serialized)
    for ticker in tickers:
        data = serialized.get(ticker, {"error": "Not Found", "code": 404})
        curr = ticker.split("_")[-1].upper()
        await message.answer(f"""The high: {hbold(data['high'])} {curr}
The low {hbold(data['low'])} {curr}
Updated: {hbold(time.strftime("%d.%m.%Y %H:%M:%S", time.gmtime(data['updated'])))}""")


@dp.message(Command(
    commands=btc_avg_cmd,
    prefix='/',
    ignore_case=True
))
async def getBitcoinValueAvg(message: Message):
    await message.answer(f"{hbold('BITCOIN AVERAGE:')}\n"
                         f"The high: {hbold(btc.bitcoin_price_avg())} $"
                         f"\nUpdated: {hbold(btc.updateTime)}")


@dp.message(Command(
    commands=btc_online_cmd,
    prefix='/',
    ignore_case=True
))
async def getBitcoinValueOnline(message: Message):
    r = btc.bitcoin_price_online()
    await message.answer(f"{hbold('BITCOIN ONLINE:')}\n"
                         f"Value: {hbold(r[0])} $ ({hbold(r[2])} ₽)"
                         f"\nActual: {hbold(r[1])}")


@dp.message(Command(
    commands=btc_high_cmd,
    prefix='/',
    ignore_case=True
))
async def getBitcoinValueHigh(message: Message):
    await message.answer(f"{hbold('BITCOIN HIGH:')}\n"
                         f"The high: {hbold(btc.bitcoin_price_high())} $"
                         f"\nUpdated: {hbold(btc.updateTime)}")


@dp.message(Command(
    commands=toncoin_cmd,
    prefix='/',
    ignore_case=True
))
async def getToncoinValueOnline(message: Message):
    r = ton.toncoin_price_online()
    await message.answer(f"{hbold('TONCOIN ONLINE:')}\n"
                         f"Value: {hbold(r[0])} $ ({hbold(r[2])} ₽)"
                         f"\nActual: {hbold(r[1])}")


@dp.message(Command(
    commands=toncoin_avg_cmd,
    prefix='/',
    ignore_case=True
))
async def getToncoinValueAverage(message: Message):
    await message.answer(f"{hbold('TONCOIN AVERAGE:')}\n"
                         f"Value: {hbold(ton.toncoin_price_avg())} $"
                         f"\nActual: {hbold(ton.updateTime)}")


@dp.message(Command(
    commands=toncoin_high_cmd,
    prefix='/',
    ignore_case=True
))
async def getToncoinValueHigh(message: Message):
    await message.answer(f"{hbold('TONCOIN HIGH:')}\n"
                         f"Value: {hbold(ton.toncoin_price_high())}$"
                         f"\nActual: {hbold(ton.updateTime)}")


@dp.message(Command(
    commands=exchange_valuta,
    prefix='/',
    ignore_case=True
))
async def exchangeValuta(message: Message):
    if message.text.split()[1] != "":
        await message.answer(str(currency.convert(int(message.text.split()[1]), "USD", "EUR")))


def cancel_checker(identifier: Union[str, int]) -> bool:
    if db_get_user_state(identifier):
        for job in schedule.jobs:
            if str(identifier) in job.tags:
                schedule.cancel_job(job)
                return True
    return False


def set_parameters(params: Union[list, tuple]) -> tuple:
    try:
        limit, timer = params[1], int(params[2])
    except IndexError:
        limit, timer = '5', 5
    if ',' in limit:
        limit.replace(',', '.')
    limit = 1 - (float(limit) if '.' in limit else int(limit) / 100)
    return limit, timer


@dp.message(Command(
    commands=stop_checker,
    prefix='/',
    ignore_case=True
))
async def stopChecker(message: Message):
    if cancel_checker(message.chat.id):
        logging.info(f'AUTOCHECKER: STOP JOB (TIME: {getCurrentTime()}, ID: {message.chat.id})')
        db_edit_user_state(message.chat.id, False)
        await message.answer(f"Checker {hbold('OFF')}")
        return
    await message.answer(f"Checker {hbold('isn`t run')}")


@dp.message(Command(
    commands=change_parameters,
    prefix='/',
    ignore_case=True
))
async def changeParameters(message: Message):
    cancel_checker(message.chat.id)
    limit, timer = set_parameters(message.text.split())
    await message.answer(f'Checker with new parameters {hbold("launched")}\n'
                         f'Parameters: {hbold(limit)}% and {hbold(timer)} minutes')
    logging.info(f'AUTOCHECKER: RUN WITH NEW PARAMETERS(_limit={limit}, _timer={timer}) ({getCurrentTime()})')
    schedule.every(timer).minutes.do(
        check_rise_toncoin,
        _limit=limit,
        _special_id=message.chat.id
    ).tag(str(message.chat.id))
    db_edit_user_state(message.chat.id, True)
    db_edit_last_value(message.chat.id, ton.toncoin_price_online()[0])


@dp.message(Command(
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
    limit, timer = set_parameters(message.text.split())
    await message.answer(f'Checker is {hbold("launched")}'
                         f'\nParameters: {hbold(limit)}% and {hbold(timer)} minutes')
    logging.info(f'AUTOCHECKER: RUN(_limit={limit}, _timer={timer}) ({getCurrentTime()})')
    schedule.every(timer).minutes.do(
        check_rise_toncoin,
        _limit=limit,
        _special_id=message.chat.id
    ).tag(str(message.chat.id))
    db_edit_last_value(message.chat.id, ton.toncoin_price_online()[0])
    db_edit_user_state(message.chat.id, True)


@dp.message(Command(
    commands='getCurrentJobs',
    prefix='_',
    ignore_case=True
))
async def getCurrentJobs(message: Message):
    if message.chat.id in [1491418466, 5720816788]:
        await message.answer(f"Count of launched the checker: {len(schedule.jobs)}")
        return
    await message.answer('You don`t have enough rights to use this command')


@dp.message(Command(
    commands='stopMainTask',
    prefix='_',
    ignore_case=True
))
async def stopTask(message: Message):
    if message.chat.id in [1491418466, 5720816788]:
        for task in asyncio.all_tasks(asyncio.get_event_loop()):
            if task.get_name() == "MAIN":
                task.cancel()
                await message.answer("Done! Delete thread")
        return
    await message.answer('You don`t have enough rights to use this command')


@dp.message(CommandStart())
async def onStart(message: Message):
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!\n"
                         "Now you can get notifications from me about rise the toncoin crypt...\n"
                         f"Your chat id: {hbold(message.chat.id)}\n"
                         f"/run for run checker toncoin crypt with next params: {hbold('5%')}"
                         f" rise and {hbold('5 minutes')} timer")
    db_create_new_user(message.chat.id)


def runBot():
    try:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            loop.create_task(runToncoinChecker(), name='MAIN')
            loop.run_until_complete(dp.start_polling(bot))
        else:
            nest_asyncio.apply(loop)
            loop.create_task(runToncoinChecker(), name='MAIN')
            asyncio.run(dp.start_polling(bot))
    except KeyboardInterrupt:
        logging.warning("Finished")


if __name__ == '__main__':
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # for Windows systems
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    runBot()

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
from os import getenv
from dotenv import load_dotenv
from typing import Union
from subprocess import call
from currency_converter import CurrencyConverter

from commands import *
from blockchains import Bitcoin, Toncoin, Blockchains
# from markup import start_button, checker_button

load_dotenv(".env")

API_TOKEN = getenv("API_KEY")
bot = Bot(API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
ton = Toncoin()
btc = Bitcoin()
blockchains = Blockchains()
cur = CurrencyConverter()
latestUpdate = ton.toncoin_price_online()[0]


async def check_rise_toncoin(_special_id: Union[int, str], _limit: Union[int, float]) -> None:
    """Get notification to telegram if toncoin rise around limit context parameter percent after start a program
    :param _special_id:
    :param _limit: required parameter Union[int, float]
    :return String
    """
    global latestUpdate
    if type(_limit) == int:
        _limit /= 100
    _limit: float = 1 - _limit
    value = ton.toncoin_price_online()
    percent = latestUpdate / value[0]
    if 0 < percent < _limit:
        await bot.send_message(
            chat_id=_special_id,
            text=f"{hbold('RISE, TONCOIN RISE:')}\n\nValue: {hbold(value[0])} $ ({hbold(value[2])} ₽)\nActual: {value[1]}"
        )
    latestUpdate = value[0]


run = True


async def runToncoinChecker(limit: Union[int, float], timer: int, special_id: Union[int, str]) -> None:
    schedule.every(timer).minutes.do(check_rise_toncoin, _limit=limit, _special_id=special_id)
    try:
        while run:
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
    :param message: Current message who user send to Telegram bot
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
        currency = ticker.split("_")[-1].upper()
        await message.answer(f"""The high: {hbold(data['high'])} {currency}
The low {hbold(data['low'])} {currency}
Updated: {hbold(time.strftime("%d.%m.%Y %H:%M:%S", time.gmtime(data['updated'])))}""")


@dp.message(Command(
    commands=btc_avg_cmd,
    prefix='/',
    ignore_case=True
))
async def getBitcoinValueAvg(message: Message):
    await message.answer(f"The average: {hbold(btc.bitcoin_price_avg())} $"
                         f"\nUpdated: {hbold(btc.updateTime)}")


@dp.message(Command(
    commands=btc_online_cmd,
    prefix='/',
    ignore_case=True
))
async def getBitcoinValueOnline(message: Message):
    await message.answer("developing")


@dp.message(Command(
    commands=btc_high_cmd,
    prefix='/',
    ignore_case=True
))
async def getBitcoinValueHigh(message: Message):
    await message.answer(f"""The high: {hbold(btc.bitcoin_price_high())} $
    Updated: {hbold(btc.updateTime)}""")


@dp.message(Command(
    commands=toncoin_cmd,
    prefix='/',
    ignore_case=True
))
async def getToncoinValueOnline(message: Message):
    r = ton.toncoin_price_online()
    await message.answer(f"{hbold('TONCOIN ONLINE:')}\n\nValue: {hbold(r[0])} $ ({hbold(r[2])} ₽)\nActual: {r[1]}")


@dp.message(Command(
    commands=toncoin_avg_cmd,
    prefix='/',
    ignore_case=True
))
async def getToncoinValueAverage(message: Message):
    await message.answer(f"{hbold('TONCOIN AVERAGE:')}"
                         f"\nValue: {hbold(ton.toncoin_price_avg())} $"
                         f"\nActual: {hbold(ton.updateTime)}")


@dp.message(Command(
    commands=toncoin_high_cmd,
    prefix='/',
    ignore_case=True
))
async def getToncoinValueHigh(message: Message):
    await message.answer(f"{hbold('TONCOIN HIGH:')}"
                         f"\nValue: {hbold(ton.toncoin_price_high())}$"
                         f"\nActual: {hbold(ton.updateTime)}")


@dp.message(Command(
    commands=exchange_valuta,
    prefix='/',
    ignore_case=True
))
async def exchangeValuta(message: Message):
    if message.text.split()[1] != "":
        await message.answer(str(cur.convert(int(message.text.split()[1]), "USD", "RUB")))


@dp.message(Command(
    commands=("change_params", 'params', 'change_parameters', 'parameters'),
    prefix='/',
    ignore_case=True
))
async def changeParameters(message: Message):
    global run
    run = False
    params = message.text.split()
    try:
        limit, timer = params[1], int(params[2])
    except IndexError:
        limit, timer = '11', 5
    if ',' in limit:
        limit.replace(',', '.')
    limit = float(limit) if '.' in limit else int(limit)
    asyncio.create_task(runToncoinChecker(limit=limit, special_id=message.chat.id, timer=timer))
    await message.answer(f"Checker with new parameters {hbold('launched')}")


@dp.message(Command(
    commands='stop',
    prefix='/',
    ignore_case=True
))
async def stopCheckerCoin(message: Message):
    global run
    run = False
    await message.answer(f"Checker the Toncoin {hbold('OFF')}")


@dp.message(Command(
    commands='shutdown',
    prefix='/',
    ignore_case=True
))
async def shutdownComputer(message: Message):
    call(f'shutdown -s -t {message.text.split()[1]}')


@dp.message(CommandStart())
async def onStart(message: Message):
    params = message.text.split()
    try:
        limit, timer = params[1], int(params[2])
    except IndexError:
        limit, timer = '11', 5
    if ',' in limit:
        limit.replace(',', '.')
    limit = float(limit) if '.' in limit else int(limit)
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!\n"
                         "Now you can get notifications from me about rise the toncoin crypt...\n"
                         f"Your chat id: {hbold(message.chat.id)}")
    asyncio.create_task(runToncoinChecker(limit=limit, special_id=message.chat.id, timer=timer))


async def runBot():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        try:
            first_loop = asyncio.get_event_loop()
        except RuntimeError:
            first_loop = asyncio.new_event_loop()
            first_loop.run_until_complete(runBot())
        else:
            nest_asyncio.apply(first_loop)
            asyncio.run(runBot())
    except KeyboardInterrupt:
        logging.warning("Finished")

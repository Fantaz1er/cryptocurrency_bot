import httpx
import asyncio
import time

from nest_asyncio import apply
from random import choice
from string import ascii_lowercase, digits
from typing import Any, Union

__all__ = ["Bitcoin", "Toncoin", "Blockchains"]

HEADERS: dict = {
    'authority': 'api.coinmarketcap.com',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'no-cache',
    'origin': 'https://coinmarketcap.com',
    'platform': 'web',
    'referer': 'https://coinmarketcap.com/',
    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 '
                  'Safari/537.36',
    'x-request-id': '69c74736249c4d3fbb59b279556793e5',  # not const value
}

RANDOM_LETTERS: str = ascii_lowercase + digits


def async_run(task, *args) -> Any:
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        return loop.run_until_complete(task(args))
    else:
        apply(loop)  # nest_asyncio
        return asyncio.run(task(args))


class AsyncToncoinHandler:
    def __init__(self):
        self.url_coinmarket = 'https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail/chart'
        self.url_yobit = "https://yobit.net/api/3/ticker/toncoin_usd"

    @property
    def updateHeaders(self):
        HEADERS['x-request-id'] = ''.join(choice(RANDOM_LETTERS) for _ in range(32))
        return HEADERS

    async def _get_toncoin_usd_online(self, *args) -> tuple:
        ctime = round(time.time()) - 1
        async with httpx.AsyncClient() as client:
            r = await client.get(
                self.url_coinmarket,
                headers=self.updateHeaders,
                params={'id': '11419', 'convertId': '2806', 'range': f'{ctime - 600}~{ctime}'}
            )
            res = r.json()['data']['points']
            idx_last = sorted(tuple(res))[-1]
        return (round(res[idx_last]['v'][0], 5),
                time.strftime("%Y-%m-%d %H:%M:%S %z", time.gmtime(int(idx_last))),
                round(res[idx_last]['c'][0], 2))

    async def _get_toncoin_usd_yobit(self, *args) -> Union[dict, None]:
        async with httpx.AsyncClient() as client:
            r = await client.get(self.url_yobit, )
        res = r.json()['toncoin_usd']
        try:
            return {'high': res['high'], 'avg': res['avg'],
                    'update': time.strftime("%Y-%m-%d %H:%M:%S %z", time.gmtime(res['updated']))}
        except KeyError:
            return None


class Toncoin(AsyncToncoinHandler):
    def __init__(self):
        super().__init__()
        self._update_time: Union[str, None] = None

    def toncoin_price_online(self) -> tuple:
        return async_run(self._get_toncoin_usd_online)

    @property
    def updateTime(self) -> str:
        """Getter last updated the course of coins"""
        return self._update_time

    def toncoin_price_high(self) -> int:
        res = async_run(self._get_toncoin_usd_yobit)
        self._update_time = res['update']
        return res['high']

    def toncoin_price_avg(self) -> int:
        res = async_run(self._get_toncoin_usd_yobit)
        self._update_time = res['update']
        return res['avg']


class AsyncBitcoinHandler:
    def __init__(self):
        self._bitcoin_url_yobit = "https://yobit.net/api/3/ticker/btc_usd"
        self._bitcoin_url_coinmarket = 'https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail/chart'

    @property
    def updateHeaders(self):
        HEADERS['x-request-id'] = ''.join(choice(RANDOM_LETTERS) for _ in range(32))
        return HEADERS

    async def _get_bitcoin_usd_online(self, *args) -> tuple:
        ctime = round(time.time()) - 1
        async with httpx.AsyncClient() as client:
            r = await client.get(
                url=self._bitcoin_url_coinmarket,
                headers=self.updateHeaders,
                params={'id': '1', 'convertId': '2806', "range": f'{ctime - 600}~{ctime}'}
            )
            res = r.json()['data']['points']
            idx_last = sorted(tuple(res))[-1]
        return (round(res[idx_last]['v'][0], 5),
                time.strftime("%Y-%m-%d %H:%M:%S %z", time.gmtime(int(idx_last))),
                round(res[idx_last]['c'][0], 2))

    async def _get_bitcoin_usd_yobit(self, *args) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.get(self._bitcoin_url_yobit)
            res = r.json()['btc_usd']
        return {"high": res['high'], "avg": res['avg'],
                "update": time.strftime("%d.%m.%Y %H:%M:%S", time.gmtime(int(res['updated'])))}


class Bitcoin(AsyncBitcoinHandler):
    def __init__(self):
        super().__init__()
        self._update_time: Union[str, None] = None

    @property
    def updateTime(self) -> str:
        """Getter attribute last update the coin"""
        return self._update_time

    def bitcoin_price_online(self) -> tuple:
        return async_run(self._get_bitcoin_usd_online)

    def bitcoin_price_high(self) -> int:
        res = async_run(self._get_bitcoin_usd_yobit)
        self._update_time = res['update']
        return res['high']

    def bitcoin_price_avg(self) -> int:
        res = async_run(self._get_bitcoin_usd_yobit)
        self._update_time = res['update']
        return res['avg']


class AsyncBlockchainsHandler:
    def __init__(self):
        self._blockchains_usd = "https://yobit.net/api/3/ticker/"
        self._blockchains_coinmarket = 'https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail/chart'

    @property
    def updateHeaders(self):
        HEADERS['x-request-id'] = ''.join(choice(RANDOM_LETTERS) for _ in range(32))
        return HEADERS

    async def _get_blockchains_usd_online(self, coinIds: Union[list[str], list[int]]) -> dict:
        ctime = round(time.time()) - 1
        result: dict = {}
        for coinId in coinIds:
            async with httpx.AsyncClient() as client:
                r = await client.get(
                    url=self._blockchains_coinmarket,
                    headers=self.updateHeaders,
                    params={'id': str(coinId), 'convertId': '2806', 'range': f'{ctime - 600}~{ctime}'}
                )
                res = r.json()['data']['points']
                idx_last = sorted(tuple(res))[-1]
            result |= {coinId: (
                res[idx_last]['v'][0],
                time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(idx_last)),
                res[idx_last]['c'][0]
            )}
        return result

    async def _get_blockchains_usd_yobit(self, tickers) -> Union[dict, None]:
        tickers = list(*tickers)
        async with httpx.AsyncClient() as client:
            response = await client.get(self._blockchains_usd + "_".join(e for e in list(tickers)))
            r = response.json()
        return {e: r.get(e, {"error": "not found", "code": 404}) for e in tickers}


class Blockchains(AsyncBlockchainsHandler):
    def __init__(self):
        super().__init__()

    def blockchains_price(self, tickers) -> Union[dict, None]:
        return async_run(self._get_blockchains_usd_yobit, tickers)

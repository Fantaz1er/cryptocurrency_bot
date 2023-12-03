# -*- coding: utf-8 -*-
from typing import Optional

from .request import AsyncBlockchainsRequest, async_run

__all__ = ["Blockchains"]


class Blockchains(AsyncBlockchainsRequest):
    def __init__(self):
        super().__init__()
        self._update_time: Optional[str] = None

    @property
    def updateTime(self) -> Optional[str]:
        return self._update_time

    def blockchains_price(self, tickers) -> Optional[dict]:
        return async_run(self._get_blockchains_usd_yobit, tickers)

    def toncoin_price_online(self) -> tuple:
        return async_run(self._get_toncoin_usd_online)

    def toncoin_price_high(self) -> Optional[int]:
        res = async_run(self._get_toncoin_usd_yobit)
        self._update_time = res['update']
        return res['high']

    def toncoin_price_avg(self) -> Optional[int]:
        res = async_run(self._get_toncoin_usd_yobit)
        self._update_time = res['update']
        return res['avg']

    def bitcoin_price_online(self) -> Optional[tuple]:
        return async_run(self._get_bitcoin_usd_online)

    def bitcoin_price_high(self) -> Optional[int]:
        res = async_run(self._get_bitcoin_usd_yobit)
        self._update_time = res['update']
        return res['high']

    def bitcoin_price_avg(self) -> Optional[int]:
        res = async_run(self._get_bitcoin_usd_yobit)
        self._update_time = res['update']
        return res['avg']

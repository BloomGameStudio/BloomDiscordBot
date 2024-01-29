# -*- coding: UTF-8 -*-
import os, json, aiohttp, asyncio
from .cg import *
from .settings import *
from .data_request import *
from .models import *

class CoinsList():
    __by_id = {} #cg_id
    __by_symbol = {} #ticker
    raw_list = None

    def __init__(self,raw_list):
        self.raw_list = raw_list
        for coin in raw_list:
            if 'id' in coin and 'symbol' in coin:
                token = Bitcoin(coin) if (coin['id'] == 'bitcoin' or coin['symbol'] == 'btc') else Token(coin)
                if coin['symbol'] in self.__by_symbol:
                    if 'wormhole' in token.name.lower(): #edge case with collissions of wormhole assets
                        continue
                self.__by_id[token.cg_id] = token
                self.__by_symbol[token.ticker] = token

    def __getitem__(self, key):
        if key in self.__by_id:
            return self.__by_id[key]
        elif key in self.__by_symbol:
            return self.__by_symbol[key]
        return None


class TokenManager():
    cg = CoinGeckoAPI()
    __coins_list = None #CoinGecko Formatted Tokens
    bitcoin = None
    header_alt = None
    rotating_tokens = {}
    display_limit = 15

    def __init__(self,settings=Settings()):
        raw_list = self.cg.get_coins_list()
        self.__coins_list = CoinsList(raw_list) 
        self.bitcoin = self.__unpriced_token_for_string('bitcoin')
        if not settings is None:
            if not settings.header_alt is None:
                self.header_alt = self.__unpriced_token_for_string(settings.header_alt)
        self.__update_token_price(self.bitcoin)

    def __len__(self):
        return len(self.rotating_tokens)

    def __getitem__(self, key):
        return self.__unpriced_token_for_string(key)

    def exists(self,token):
        return False if self.__unpriced_token_for_string(token) is None else True

    def clear(self):
        self.rotating_tokens.clear()

    def add_cached_rotating_tokens(self,tokens_json):
        tokens = [self.__unpriced_token_for_string(json.get('cg_id')) for json in tokens_json if 'cg_id' in json]
        for token in tokens:
            self.rotating_tokens[token.ticker] = token
        self.update_all_token_prices()

    def __unpriced_token_for_string(self,passed_ticker):
        passed_ticker = passed_ticker.lower()
        if passed_ticker in self.rotating_tokens:
            token = self.rotating_tokens[passed_ticker]
            return token
        elif passed_ticker == 'btc' or passed_ticker == 'bitcoin':
            if self.bitcoin is not None:
                return self.bitcoin
        return self.__coins_list[passed_ticker]

    def __update_token_price(self,token):
        response = self.cg.get_price(ids=token.cg_id, vs_currencies='usd,btc,eth')
        token.process_json(response[token.cg_id])
        delta_response = self.cg.get_coins_markets(ids=token.cg_id,vs_currency='usd')
        if delta_response[0]['id'] == token.cg_id:
            token.update_daily_delta(delta_response)
        return token

    def update_all_token_prices(self,tokens=None,settings=None,include_header_assets=True):
        if tokens is None:
            tokens = self.rotating_tokens.values()

        ids = [token.cg_id for token in tokens]
        if include_header_assets:
            ids.append('bitcoin')
            if not settings is None:
                ids.append(settings.header_alt)
        joined_ids = ",".join(ids)

        prices = self.cg.get_price(ids=joined_ids,vs_currencies='usd,btc,eth')
        delta_responses = self.cg.get_coins_markets(ids=joined_ids,vs_currency='usd')

        if include_header_assets:
            if self.bitcoin is not None:
                self.bitcoin.update_prices(prices[self.bitcoin.cg_id])
            if self.header_alt and self.header_alt.cg_id:
                self.header_alt.update_prices(prices[self.header_alt.cg_id])
        for token in tokens:
            token.update_prices(prices[token.cg_id])

        for delta_response in delta_responses:
            if not 'id' in delta_response:
                continue
            if delta_response['id'] == self.bitcoin.cg_id:
                self.bitcoin.update_daily_delta(delta_response)
            if not self.header_alt is None and delta_response['id'] == self.header_alt.cg_id:
                self.bitcoin.update_daily_delta(delta_response)

            [token.update_daily_delta(delta_response) for token in tokens if delta_response['id'] == token.cg_id]

        return tokens

    def get_priced_token_set(self,tickers,settings=None,include_header_assets=True):
        tokens = []
        for ticker in tickers:
            token = self.__unpriced_token_for_string(ticker)
            if not token is None:
                tokens.append(token)
        return self.update_all_token_prices(tokens,settings,include_header_assets)

class Bitcoin(Token):
    def status(self,denomination):
        return '🌽 ' + super().usd_percent

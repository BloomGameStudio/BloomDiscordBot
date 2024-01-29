# -*- coding: UTF-8 -*-
import discord, os, json, aiohttp, asyncio
from discord.ext import commands, tasks
from .cg import *
from .settings import *
from .ens_manager import *
from .data_request import *
from .models import *

#unoptimized (!)
def next_item(dic, key):
    nxt = False
    for k, v in dic.items():
        if k == key: #found the key
            nxt = True #so the next is what we want
        elif nxt == True: 
            return v #return it
    return None

def first(s):
    '''Return the first element from an ordered collection
       or an arbitrary element from an unordered collection.
       Raise StopIteration if the collection is empty.
    '''
    return next(iter(s))

class sci_clean(str):
    def __new__(cls, content):
        if 'e' in content:
            base,expo = content.split('e')
            updated = '%.*f'%(len(base)-2+abs(int(expo)),content)
            return super().__new__(cls, updated)
        return super().__new__(cls, content)

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
    rotating_tokens = {}
    display_limit = 10

    def __init__(self):
        raw_list = self.cg.get_coins_list()
        self.__coins_list = CoinsList(raw_list) 
        self.bitcoin = self.__unpriced_token_for_string('bitcoin')
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

    def add_rotating_token_set(self,tickers):
        if len(self.rotating_tokens) + len(tickers) >= self.display_limit:
            return None

        for ticker in tickers:
            token = self.__unpriced_token_for_string(ticker)
            if not token is None:
                self.rotating_tokens[token.ticker] = token

        updated_tokens = self.update_all_token_prices()

        return updated_tokens

    def remove_rotating_token(self,token_ticker):
        token_ticker = token_ticker.lower()
        if token_ticker in self.rotating_tokens:
            return self.rotating_tokens.pop(token_ticker)
        return None

    def update_all_token_prices(self,tokens=None):
        if tokens is None:
            tokens = self.rotating_tokens.values()

        ids = [token.cg_id for token in tokens]
        ids.append('bitcoin')
        joined_ids = ",".join(ids)

        prices = self.cg.get_price(ids=joined_ids,vs_currencies='usd,btc,eth')
        delta_responses = self.cg.get_coins_markets(ids=joined_ids,vs_currency='usd')

        if self.bitcoin is not None:
            self.bitcoin.update_prices(prices[self.bitcoin.cg_id])
        for token in tokens:
            token.update_prices(prices[token.cg_id])

        for delta_response in delta_responses:
            if not 'id' in delta_response:
                continue
            if delta_response['id'] == self.bitcoin.cg_id:
                self.bitcoin.update_daily_delta(delta_response)

            [token.update_daily_delta(delta_response) for token in tokens if delta_response['id'] == token.cg_id]

        return tokens

    def get_priced_token_set(self,tickers):
        tokens = []
        for ticker in tickers:
            token = self.__unpriced_token_for_string(ticker)
            if not token is None:
                tokens.append(token)
        return self.update_all_token_prices(tokens)

class Bitcoin(Token):
    def status(self,denomination):
        return '🌽 ' + super().usd_percent

class DataManager():
    # token_manager = TokenManager()
    # gas = Gas()
    # __ens_manager = ENSManager()
    __api_keys = {}

    # def __init__(self):
    #     load_dotenv()
    #     etherscan_api_key = os.getenv('ETHERSCAN_API_KEY')
    #     if etherscan_api_key:
    #         self.__api_keys['etherscan'] = etherscan_api_key
    #     else:
    #         print("Etherscan API Key could not be fetched. Please locate it at pks/etherscan_api_key.json")

    #     self.__get_cached_tokens()
    #     self.__get_cached_pokemon()

    # def __get_cached_tokens(self):
    #     tokens = self.__get_rotating_tokens_json()
    #     if tokens is None or not tokens:
    #         return
    #     self.token_manager.add_cached_rotating_tokens(tokens)

    # def __get_cached_pokemon(self):
    #     looks_orders = self.__get_pokemon_market_json()
    #     if looks_orders is None or not looks_orders:
    #         return
    #     self.__ens_manager.add_looks_orders(looks_orders)

    # async def update_gas(self):
    #     etherscan_api_key = self.__api_keys.get('etherscan')
    #     if etherscan_api_key:
    #         url = f'https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={etherscan_api_key}'
    #         await DataRequest(url).get(self.gas)

    # def update_all_token_prices(self):
    #     return self.token_manager.update_all_token_prices()

    # async def load_ens(self):
    #     await self.__ens_manager.get_looks_orders()
    #     self.__save_pokemon_market(self.__ens_manager.looks_rare_assets.values())

    # async def get_collections(self):
    #     await self.__ens_manager.get_collections()

    # def get_collection_floor(self,contract_address):
    #     return self.__ens_manager.get_collection_floor(contract_address)

    # def get_pokemon(self,generation=1):
    #     return self.__ens_manager.pokemon_assets()

    # def add_rotating_token_set(self,token_tickers):
    #     tokens = self.token_manager.add_rotating_token_set(token_tickers)
    #     self.__save_rotating_tokens(tokens)
    #     return tokens

    # def remove_rotating_token(self,ticker):
    #     token = self.token_manager.remove_rotating_token(ticker)
    #     self.__save_rotating_tokens(self.token_manager.rotating_tokens.values())
    #     return token

    # def __save_rotating_tokens(self, tokens, update_json=True):
    #     if update_json:
    #         json_object = json.dumps(list(tokens), default=lambda x: x.__json__, indent = 4) 
    #         with open(f'state/rotating_tokens.json', "w") as outfile:
    #             outfile.write(json_object)

    # def __save_pokemon_market(self, pokemon):
    #     json_object = json.dumps(list(pokemon), default=lambda x: x.__json__, indent = 4) 
    #     with open(f'state/looks_market.json', "w") as outfile:
    #         outfile.write(json_object)

    # def __get_pokemon_market_json(self):
    #     if not os.path.exists('state/looks_market.json'):
    #         return
    #     f = open('state/looks_market.json')
    #     data = json.load(f)
    #     return data

    # def __get_rotating_tokens_json(self):
    #     if not os.path.exists('state/rotating_tokens.json'):
    #         return
    #     f = open('state/rotating_tokens.json')
    #     data = json.load(f)
    #     return data

    # @property
    # def pokemon_floor(self):
    #     return self.__ens_manager.pokemon_floor

    # @property
    # def rotating_pokemon_floors(self):
    #     return self.__ens_manager.rotating_pokemon_floors

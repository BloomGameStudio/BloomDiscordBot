# -*- coding: UTF-8 -*-
from abc import ABC, abstractmethod
from .crypto_constants import *
from .helpers import *
from .models import *

class LooksRareOrderSet(Parsable):
    order_list = []

    def __init__(self, json=None):
        self.process_json(json)

    def process_json(self, json):
        if json:
            for element in json:
                order = LooksRareOrder(element)
                self.order_list.append(order)

"""
"hash": "0x70566e921c3f9c67e77a6a17cc29fb566b47b4d8091557eac16cc16bba6b77a9",
"collectionAddress": "0x57f1887a8BF19b14fC0dF6Fd9B2acc9Af147eA85",
"tokenId": "91618170700439972888900727650968364479264011142334729266575129829105022712533",
"isOrderAsk": true,
"signer": "0x895284A4059159E4D8e6c39df6b0Dc98e1a458EE",
"strategy": "0x56244Bb70CbD3EA9Dc8007399F61dFC065190031",
"currencyAddress": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
"amount": 1,
"price": "5000000000000000",
"nonce": "954",
"startTime": 1653583658,
"endTime": 1656175653,
"minPercentageToAsk": 8500,
"params": "",
"status": "VALID",
"signature": "0xa270954a102f6472cdccd58c8f23d403600d143cc7f78547f2de1b8877bd1e6410d62c6e7785b94902904aa5fef5323cc6f6fa355cf04d45c140f03b47d1279301",
"v": 28,
"r": "0xa270954a102f6472cdccd58c8f23d403600d143cc7f78547f2de1b8877bd1e64",
"s": "0x10d62c6e7785b94902904aa5fef5323cc6f6fa355cf04d45c140f03b47d12793"
"""

class LooksRareOrder(Parsable):
    __hash = None
    __is_ask_order = None # "true" / True => someone bidding / trying to buy
    __currency_address = None # "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2" / WETH [fetch from etherscan]
    __price = None #"5000000000000000" / 0.05Weth
    __signature = None
    __end_time = None

    def __init__(self, json=None):
        self.process_json(json)

    def process_json(self, json):
        if json:
            if 'data' in json:
                self.__parse(json.get('data'))
            else:
                self.__parse(json)

    def __parse(self, json):
        self.__is_ask_order = json.get('isOrderAsk',json.get('is_ask_order'))
        self.__currency_address = json.get('currencyAddress',json.get('currency_address'))
        self.__price = json.get('price')
        self.__hash = json.get('hash')
        self.__signature = json.get('signature')
        self.__end_time = json.get('endTime',json.get('end_time'))

    @property
    def has_price(self):
        return not self.__price is None

    @property
    def price_float(self):
        if self.__currency_address == "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2": #weth
            return float(self.__price) / float(1000000000000000000.0) #18 digit shift
        return float(self.__price) / float(1000000000000000000.0) #18 digit shift

    @property
    def price_string(self):
        if self.__currency_address == "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2": #weth
            return f"{ self.price_float } wETH"
        return f"{ self.price_float } ETH"

class LooksRareAsset(Parsable):
    name = None
    __collection_address = None
    __description = None
    __image_url = None
    token_id = None
    pokemon = None
    primary_order = None

    def __init__(self, json=None):
        self.process_json(json)

    def process_json(self, json):
        if json is None:
            return
        if isinstance(json,dict):
            self.__parse(json)

    def __parse(self, json):
        self.name = json.get('name')
        self.__collection_address = json.get('collectionAddress','collection_address')
        self.__description = json.get('description')
        self.__image_url = json.get('imageURI','image_url')
        self.token_id = json.get('tokenId','token_id')

        self.__add_pokemon(json)
        self.__add_primary_order(json)

    def __add_pokemon(self, json):
        pokemon_json = json.get('pokemon')
        if pokemon_json:
            self.pokemon = Pokemon(pokemon_json)

    def __add_primary_order(self, json):
        order_json = json.get('primary_order')
        if order_json:
            self.primary_order = LooksRareOrder(order_json)

    @property
    def has_price(self):
        if not self.__looks_order:
            return False
        return self.__looks_order.has_price

    @property
    def __looks_order(self):
        if self.primary_order:
            return self.primary_order
        return None

    @property
    def price_float(self):
        if not self.has_price:
            return None
        if self.__looks_order:
            return self.__looks_order.price_float
        return None

    @property
    def price_string(self):
        if not self.has_price:
            return None
        if self.__looks_order:
            return self.__looks_order.price_string
        return None

    @property
    def ens_name(self):
        return self.name

    @property
    def pokemon_name(self):
        if self.pokemon:
            return self.pokemon.name
        return self.ens_name.partition('.')[0]
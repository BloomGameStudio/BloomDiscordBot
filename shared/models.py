# -*- coding: UTF-8 -*-
from abc import ABC, abstractmethod
from enum import Enum
from .helpers import bold
from .constants import PRICE_CHANGE_NOMINAL_KEY, PRICE_CHANGE_PERCENT_KEY

class PriceMomentum(Enum):
    UP = 1
    DOWN = 2
    SIDEWAYS = 3

class PriceDenomination(Enum):
    USD = 1
    BTC = 2
    ETH = 3
    ROTATE = 4

class Parsable():
    @abstractmethod
    def process_json(self, json):
        pass


    @property
    def __private_prefix(self):
        return f'_{self.__class__.__name__}__'

    def __deprivate_key(self,key,prefix):
        return key.partition(prefix)[-1] if key.startswith(prefix) else key

    @property
    def __json__(self):
        prefix = self.__private_prefix
        return { self.__deprivate_key(key,prefix) : value for (key, value) in self.__dict__.items()}

    def __str__(self):
        return str(self.__json__)

class Gas(Parsable):
    slow = "NaN";
    medium = "NaN";
    fast = "NaN";

    def __init__(self, json=None):
        self.process_json(json)

    def process_json(self, json):
        if json:
            self.slow = json.get('SafeGasPrice',"NaN")
            self.medium = json.get('ProposeGasPrice',"NaN")
            self.fast = json.get('FastGasPrice',"NaN")

    @property
    def subtitle(self):
        return '⚡' + str(self.fast) + ' | 🐢' + self.slow

    @property
    def message(self):
        return "**⚡ {0} ⚡  |  🥱 {1} 🥱  |  🐢 {2} 🐢**".format(self.fast,self.medium,self.slow)

class Token(Parsable):
    __btc_price = 'NaN'
    __eth_price = 'NaN'
    __usd_price = 'NaN'
    __daily_percent_delta = None
    __daily_nominal_delta = None
    ticker = -1 #'symbol': 'btc'
    cg_id = -1 #'id': 'bitcoin'
    name = None

    def __init__(self,json):
        self.ticker = json.get('symbol').lower()
        self.cg_id = json.get('id')
        self.name = json.get('name')

    def update_prices(self,json):
        self.process_json(json)

    def process_json(self,json):
        if not 'usd' in json:
            return

        usd_price = json.get('usd')
        btc_price = json.get('btc')
        eth_price = json.get('eth')

        if 'e' in str(usd_price): #Turning scientific notation into readable
            base,expo = str(usd_price).split('e')
            updated = '%.*f'%(len(base)-2+abs(int(expo)),usd_price)
            usd_price = updated

        decimal_index = str(usd_price).find('.')
        if decimal_index > 0 and decimal_index < 4:
            shift = 5 - decimal_index
            usd_price = str(round(float(usd_price), shift))

        if 'e' in str(btc_price):
            base,expo = str(btc_price).split('e')
            updated = '%.*f'%(len(base)-2+abs(int(expo)),btc_price)
            btc_price = updated

        if 'e' in str(eth_price):
            base,expo = str(eth_price).split('e')
            updated = '%.*f'%(len(base)-2+abs(int(expo)),eth_price)
            eth_price = updated

        self.__usd_price = str(usd_price)
        self.__btc_price = str(btc_price)
        self.__eth_price = str(eth_price)

    def update_daily_delta(self,json):
        if PRICE_CHANGE_PERCENT_KEY in json:
            percent_delta = json[PRICE_CHANGE_PERCENT_KEY]
            if percent_delta:
                self.__daily_percent_delta = str(round(percent_delta,1)) + '%'
            return

        if PRICE_CHANGE_NOMINAL_KEY in json:
            nominal_delta = json[PRICE_CHANGE_NOMINAL_KEY]
            if nominal_delta:
                self.__daily_nominal_delta = str(round(nominal_delta,2)) + '%'
            return

    @property
    def __formatted_ticker(self):
        if self.ticker.lower() == "eth":
            return "Ξ"
        return self.ticker.capitalize() if len(self.ticker) > 3 else self.ticker.upper()

    @property
    def usd_percent(self):
        delta = self.__daily_percent_delta
        if delta is None or len(delta) == 0:
            return ''
        adjusted_percent = (' ⬊' if delta[0] == '-' else ' ⬈') + delta
        return '$' + self.__usd_price + adjusted_percent

    @property
    def update(self):
        formatted_ticker = self.__formatted_ticker
        unformatted = 'Added {0} to subtitle rotation.\n{1}'
        return unformatted.format(bold(formatted_ticker),self.message)

    @property
    def price_momentum(self): #up, down, sideways
        if self.__daily_percent_delta is None:
            return PriceMomentum.SIDEWAYS
        first_char = self.__daily_percent_delta[0]
        neg = first_char == '-'
        first_digit = self.__daily_percent_delta[1] if neg else first_char
        sideways_ish = first_digit == '0'
        if sideways_ish:
            return PriceMomentum.SIDEWAYS
        else:
            return PriceMomentum.DOWN if neg else PriceMomentum.UP

    @property
    def message(self):
        ticker = self.__formatted_ticker
        return bold(ticker + ' is currently ' + self.usd_percent + '  |  ₿' + self.__btc_price + '  |  Ξ' + self.__eth_price)

    def status(self,denomination):
        ticker = self.__formatted_ticker
        delim = '@' if len(ticker) > 3 else ' @ '
        if denomination == PriceDenomination.BTC:
            return ticker + delim + '₿' + self.__btc_price
        elif denomination == PriceDenomination.ETH:
            return ticker + delim + 'Ξ' + self.__eth_price
        else:
            return ticker + delim + self.usd_percent
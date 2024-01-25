#######################
# -*- coding: UTF-8 -*-
import os, json
from .models import *
from enum import Enum

class HeaderType(Enum):
    BTC = 1
    ENS = 2
    NFT = 3
    POKEMON = 4
    ALT = 5

class Settings(Parsable):
    header_type = HeaderType.BTC
    cycle_length = 20
    denomination = PriceDenomination.USD
    request_frequency = 15
    momentum = PriceMomentum.SIDEWAYS
    guild_id = None #will use this when we separate settings per guild

    def __init__(self):
        self.__load_from_json()

    def update_denomination(self, denomination, update_json):
        if denomination == 'btc' or denomination == 'eth' or denomination == 'usd' or denomination == 'rotate':
            self.denomination = denomination
            if update_json:
                self.__update_json()
            return True
        else:
            return False

    def update_speed(self, speed, update_json=True):
        speed = int(speed)
        if speed >= 8 and speed <= 30:
            self.cycle_length = speed
            if update_json:
                self.__update_json()
            return True
        return False

    def update_request_frequency(self, frequency, update_json=True):
        frequency = int(frequency)
        if frequency >= 8 and frequency <= 60:
            self.request_frequency = frequency
            if update_json:
                self.__update_json()
            return True
        return False

    def update_momentum(self, momentum, update_json=True):
        self.momentum = momentum
        if update_json:
            self.__update_json()

    def update_header_type(self, header_type, update_json=True):
        self.header_type = header_type
        if update_json:
            self.__update_json()

    def __update_json(self):
        dictionary = {
            "cycle_length": self.cycle_length,
            "denomination": str(self.denomination).split('.').pop(),
            "request_frequency": self.request_frequency,
            "momentum": str(self.momentum).split('.').pop(),
            "header_type": str(self.header_type).split('.').pop(),
        }
        json_object = json.dumps(dictionary, indent = 4)
  
        with open('state/settings.json', "w") as outfile:
            outfile.write(json_object)

    def __load_from_json(self):
        if not os.path.exists('state/settings.json'):
            return
        f = open('state/settings.json')
        data = json.load(f)

        self.update_speed(data.get('cycle_length'), False)
        self.update_denomination(PriceDenomination[data.get('denomination','USD')], False)
        self.update_request_frequency(data.get('request_frequency'), False)
        self.update_momentum(PriceMomentum[data.get('momentum','SIDEWAYS')], False)
        self.update_header_type(HeaderType[data.get('header_type','BTC')], False)
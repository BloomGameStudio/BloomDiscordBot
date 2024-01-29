# -*- coding: UTF-8 -*-
import json, aiohttp, asyncio
from .models import *

class DataRequest():
    url = None
    def __init__(self,url):
        self.url = url

    @property
    def __url_presumed_key(self):
        if self.url.startswith('https://api.looksrare.org/api/v1'):
            return 'data'
        elif self.url.startswith('https://api.etherscan.io/api'):
            return 'result'
        return None

    async def get(self,parsable=None,key=None,handler=None):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                try:
                    raw_json = await response.json()
                    if parsable and isinstance(parsable,Parsable):
                        if key:
                            element = raw_json.get(key)
                            if element:
                                parsable.process_json(element)
                        elif self.__url_presumed_key:
                            key = self.__url_presumed_key
                            element = raw_json.get(key)
                            if element:
                                parsable.process_json(element)
                        else:
                            parsable.process_json(raw_json)
                    if handler:
                        handler(raw_json,parsable)
                except ValueError:
                    print('Decoding Etherscan Gas JSON has failed')
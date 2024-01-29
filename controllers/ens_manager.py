# -*- coding: UTF-8 -*-
import requests
import aiohttp, asyncio, os, json
from .crypto_constants import *
from .models import *
from .ens_models import *
from .data_request import *

class LooksRareAPI():
    ens_assets = {}
    def __init__(self):
        print('Initializing LooksRare API')

    async def get_ens_info(self,ens_items):
        assets = {}
        items = list(ens_items.values())#[:180]
        for item in items:
            order_assets = LooksRareOrderSet()
            url = f"https://api.looksrare.org/api/v1/orders?tokenId={item.ens_id}&sort=PRICE_ASC&isOrderAsk=true&status[]=VALID"
            order_assets.order_list = [] #Unclear why this has to be reset; somehow old array carrying over even tho fresh init
            await DataRequest(url).get(order_assets)
            if not order_assets:
                continue

            primary_order = None
            low_price = float('inf')
            for order_asset in order_assets.order_list:
                if order_asset.price_float < low_price:
                    primary_order = order_asset
                    low_price = order_asset.price_float

            if primary_order is not None:
                asset = LooksRareAsset()
                url = f"https://api.looksrare.org/api/v1/tokens?collection={ENS_COLLECTION}&tokenId={item.ens_id}"
                await DataRequest(url).get(asset)
                asset.primary_order = primary_order
                asset.pokemon = item #generalize this
                assets[item.name] = asset

            await asyncio.sleep(0.6)

        self.ens_assets = assets

    async def get_collection_info(self,collection_address):
        assets = {}
        #pokemon = list(pokemon.values())#[:180]
        #asset = LooksRareAsset()
        url = f"https://api.looksrare.org/api/v1/orders?collection={collection_address}&sort=PRICE_ASC&status[]=VALID&isOrderAsk=true"
        x = requests.get(url)
        json = x.json()
        data = json['data']
        for listing in data:
            asset = LooksRareAsset(listing)

    def get_collection_floor(self,collection_address):
        assets = {}
        #pokemon = list(pokemon.values())#[:180]
        #asset = LooksRareAsset()
        url = f"https://api.looksrare.org/api/v1/orders?collection={collection_address}&sort=PRICE_ASC&status[]=VALID&isOrderAsk=true"
        x = requests.get(url)
        json = x.json()
        data = json['data']
        for listing in data:
            asset = LooksRareAsset(listing)
            return asset
            

class ENSManager():
    pokemon_gens = {}
    pokemon_all = {}
    looks_rare_assets = {}
    pokemon_floor = None #LooksRareAsset
    rotating_pokemon_floors = []

    def __init__(self):
        for i in range(POKEMON_GENERATIONS):
            self.pokemon_gens[i + 1] = {}

        if os.path.exists('./populate/pokemon_ens/pokedex_json/pokemon_all.json'):
            self.__load_from_json()


    async def get_looks_orders(self):
        api = LooksRareAPI()
        await api.get_ens_info(self.pokemon_all)
        self.looks_rare_assets = api.ens_assets

        all_asks_list = [asset for asset in self.looks_rare_assets.values() if asset.price_float is not None]
        asks = sorted(all_asks_list, key=lambda x: float(x.price_float))
        if asks:
            self.pokemon_floor = asks[0]

    async def get_collections(self):
        api = LooksRareAPI()
        await api.get_collection_info(NIGHTBIRDS_COLLECTION)

    def get_collection_floor(self,contract_address):
        api = LooksRareAPI()
        return api.get_collection_floor(contract_address)

    def pokemon_assets(self,generation=None):
        pokemon_gen_asks = {}
        for i in range(POKEMON_GENERATIONS):
            pokemon_gen_asks[i + 1] = []

        formatted_pokemon_assets = []
        all_pokemon = list(self.pokemon_all.values())
        all_asks = self.looks_rare_assets
        all_asks_list = list(all_asks.values())
        asks = sorted(all_asks_list, key=lambda x: float(x.price_float))
        for ask in asks:
            formatted_pokemon_assets.append(ask)
            pokemon_gen_asks[ask.pokemon.generation].append(ask)
        return {'all':formatted_pokemon_assets,'gens':pokemon_gen_asks}

    def __load_from_json(self):
        f = open('./populate/pokemon_ens/pokedex_json/pokemon_all.json')
        data = json.load(f)
        for value in data.values():
            pokemon = Pokemon(value)
            generation = value.get('generation')
            name = value.get('name')
            if generation is None or name is None:
                continue
            self.pokemon_gens[generation][name] = pokemon
            self.pokemon_all[name] = pokemon

    async def __load_from_api(self):
        offset = 0
        for i in range(8):
            gen = i + 1
            file = './populate/pokemon_ens/pokemon-ens-ids/Gen' + str(gen) + 'TokenIds.txt'
            f = open(file, 'r').read()
            elements = f.split(',')
            size = len(elements)
            await self.__get_pokemon_from_api(gen,elements,offset)
            offset = offset + size

    async def __get_pokemon_from_api(self,generation,ens_ids,offset):
        limit = len(ens_ids)
        async with aiohttp.ClientSession() as session:
            url = 'https://pokeapi.co/api/v2/pokemon?limit={0}&offset={1}'.format(limit,offset)
            async with session.get(url) as response:
                try:
                    raw_json = await response.json()
                    results = raw_json.get('results')
                    self.__parse_pokemon_results(generation,results,ens_ids)
                except ValueError as e:
                    print(f'Decoding Pokemon JSON has failed {e}')
                except TypeError as e:
                    print(f'Decoding Pokemon JSON has failed {e}')

    def __parse_pokemon_results(self,generation,results,ens_ids):
        reversed_ens_ids = ens_ids[::-1]
        for poke in results:
            ens_id = reversed_ens_ids.pop()
            poke[POKEMON_ENS_ID_KEY] = ens_id
            poke[POKEMON_GENERATION_KEY] = generation
            pokemon = Pokemon(poke)

            self.pokemon_all[pokemon.name] = pokemon
            self.pokemon_gens[generation][pokemon.name] = pokemon

        json_object = json.dumps(self.pokemon_gens[generation], default=lambda o: o.__json__, indent = 4)
        with open(f'./populate/pokemon_ens/pokedex_json/pokemon_gen_{generation}.json', "w") as outfile:
            outfile.write(json_object)

        for i in range(POKEMON_GENERATIONS):
            file = './populate/pokemon_ens/pokemon-ens-ids/Gen' + str(i + 1) + 'TokenIds.txt'
            f = open(file, 'r').read()
            ens_id_count = f.count(',') + 1 

        json_object = json.dumps(self.pokemon_all, default=lambda o: o.__json__, indent = 4)
        with open('./populate/pokemon_ens/pokedex_json/pokemon_all.json', "w") as outfile:
            outfile.write(json_object)


    def add_looks_orders(self,looks_orders):
        assets = {}
        for order in looks_orders:
            asset = LooksRareAsset(order)
            if asset and asset.pokemon:
                assets[asset.pokemon.name] = asset
        self.looks_rare_assets = assets
        
        sorted_assets = sorted(assets.values(), key=lambda x: float(x.price_float))
        if len(sorted_assets) > 0:
            self.pokemon_floor = sorted_assets[0]

# -*- coding: UTF-8 -*-
import discord
from .crypto_constants import *
from .settings import *
from .command_manager import *


class BotState():
    price_momentum = None #up, down, sideways
    name = None
    status = None

    def name_color(self):
        if self.price_momentum == PriceMomentum.DOWN:
            return 0xff275f #red
        elif self.price_momentum == PriceMomentum.UP:
            return 0x2ff572 #green
        elif self.price_momentum == PriceMomentum.SIDEWAYS:
            return 0x667C89 #neutral
        else:
            return None


class AppearanceManager():
    __current_state = BotState()
    __current_status_object = None

    def load_settings(self,settings):
        if not settings.momentum is None:
            self.__current_state.price_momentum = settings.momentum



    #Name Flow
    async def refresh_title_state(self,client,data_manager,user,settings):
        state = BotState()
        if settings.header_type == HeaderType.POKEMON:
            floor = data_manager.pokemon_floor
            if floor:
                state.name = "Floor " + floor.price_string
                state.price_momentum = PriceMomentum.SIDEWAYS
                await self.__sync_state(client,user,state)
        else: #if settings.header_type == HeaderType.BTC: #ENS & NFT defaults to this for now
            bitcoin = data_manager.token_manager.bitcoin
            if bitcoin is None or not isinstance(bitcoin,Bitcoin):
                return
            state.price_momentum = bitcoin.price_momentum
            state.name = bitcoin.status(settings.denomination)
            await self.__sync_state(client,user,state)

    #Status Flow
    async def refresh_status(self,client,data_manager,user,settings):
        if not data_manager.token_manager or self.__current_status_object is None:
            await self.__prepare_gas_state(client,user,data_manager)
            return

        if self.__current_status_object == data_manager.gas: #showing gas so show first token
            token_key = first(data_manager.token_manager.rotating_tokens) #first token [0] => first tuple, [1] => token value
            token = data_manager.token_manager.rotating_tokens[token_key]
            await self.__prepare_token_state(client,user,token,settings)
        else:
            if settings.header_type == HeaderType.POKEMON:
                if isinstance(self.__current_status_object, Pokemon): #showing a token, grab next
                    pokemon = next_item(data_manager.__ens_manager.rotating_pokemon_floors, self.__current_status_object.generation) #next token
                    if token is None:
                        await self.__prepare_gas_state(client,user,data_manager)
                    else:
                        await self.__prepare_pokemon_state(client,user,token,settings)
                print('pokemon shit')
            if isinstance(self.__current_status_object, Token): #showing a token, grab next
                token = next_item(data_manager.token_manager.rotating_tokens, self.__current_status_object.ticker) #next token
                if token is None:
                    await self.__prepare_gas_state(client,user,data_manager)
                else:
                    await self.__prepare_token_state(client,user,token,settings)

    #updating status
    async def __prepare_gas_state(self,client,user,data_manager):
        await data_manager.update_gas()
        self.__current_status_object = data_manager.gas

        state = BotState()
        state.status = data_manager.gas.subtitle

        await self.__sync_state(client,user,state)

    async def __prepare_token_state(self,client,user,token,settings):
        self.__current_status_object = token
        if settings.denomination == PriceDenomination.ROTATE:
            await self.__prepare_token_rotation(client,user,token,settings,PriceDenomination.USD)
        else:
            state = BotState()
            state.status = token.status(settings.denomination)
            await self.__sync_state(client,user,state)

    async def __prepare_token_rotation(self,client,user,token,settings,denomination):
        state = BotState()
        state.status = token.status(denomination)
        await self.__sync_state(client,user,state)

        if denomination == PriceDenomination.USD:
            await asyncio.sleep(float(settings.cycle_length) * 0.45) #45% time for usd
            if not token.ticker == 'btc':
                await self.__prepare_token_rotation(client,user,token,settings,'btc')
        if denomination == PriceDenomination.BTC:
            await asyncio.sleep(float(settings.cycle_length) * 0.32) #32% time for btc
            if not token.ticker == 'eth':
                await self.__prepare_token_rotation(client,user,token,settings,'eth')


    async def __prepare_pokemon_state(self,client,user,pokemon,settings):
        state = BotState()
        state.status = pokemon.generation_status
        await self.__sync_state(client,user,state)






    async def __sync_state(self,client,user,state):
        if state.name is not None and state.name != self.__current_state.name:
            self.__current_state.name = state.name
            await self.__render_name(user)

        if state.price_momentum is not None and state.price_momentum != self.__current_state.price_momentum:
            self.__current_state.price_momentum = state.price_momentum
            await self.__render_name_color(user)

        if state.status is not None and state.status != self.__current_state.status:
            self.__current_state.status = state.status
            await self.__render_status(client)





    async def __render_name(self,user):
        await user.edit(nick=str(self.__current_state.name))

    async def __render_name_color(self,user):
        for role in user.guild.roles:
            if str(role).startswith(COLOR_CHANGING_ROLE):
                colour = self.__current_state.name_color()
                if colour is None:
                    return
                await role.edit(colour=colour, enable_debug_events=True)
                break

    async def __render_status(self,client):
        await client.change_presence(activity=discord.Game(self.__current_state.status))

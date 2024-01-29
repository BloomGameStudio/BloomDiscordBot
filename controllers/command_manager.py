# -*- coding: UTF-8 -*-
from .data_manager import *
from .crypto_constants import *
from .menu_copy import *
from .settings import *
from discord.utils import get
from shared.helpers import get_channel_by_name
import logging

class CommandManager():

    def __is_command(self,message):
        delims = COMMAND_TRIGGERS
        for delim in delims:
            if message.content.startswith(delim):
                return True

    def __is_price_command(self,message):
        delims = PRICE_TRIGGERS
        for delim in delims:
            if message.content.startswith(delim):
                return True

    def __remove_tokens_from_cycle(self, remainder, data_manager, running_message=''):
        token_tickers = remainder
        if len(token_tickers) > 1:
            running_message = "Removing multiple tokens!\n------------------------\n"
        while len(token_tickers) > 0:
            next_token_ticker = token_tickers.pop(0)
            token = data_manager.remove_rotating_token(next_token_ticker)
            if token is None:
                failure_string = "Failed to removed {0}.\nTicker not in carousel.".format(next_token_ticker)
                running_message = running_message + bold(failure_string)
                continue
            elif isinstance(token,Token):
                success_string = "Removed {0}.\nIt's probably a shitcoin anyways.".format(token.ticker)
                running_message = running_message + success_string
            if len(token_tickers) > 0:
                running_message = running_message + '\n\n'
        return running_message

    def __add_tokens_to_cycle(self, token_tickers, data_manager, settings):
        running_message = ''
        if len(token_tickers) > 1:
            running_message = running_message + "**Adding multiple tokens!**\n------------------------"

        tokens = data_manager.add_rotating_token_set(token_tickers)

        if not tokens:
            return "**Failed to add tokens**.\nYou may have reached the limit of {0} or already added these ticker(s).".format(data_manager.token_manager.display_limit)

        found_tickers = []
        for token_ticker in token_tickers:
            for token in tokens:
                if token.cg_id == token_ticker or token.ticker == token_ticker:
                    running_message = running_message + '\n' + token.update
                    found_tickers.append(token_ticker)
                    break

        missed_tickers = [x for x in token_tickers if not x in found_tickers]

        failures = "\n" + "\n".join([bold("Failed to find {0}".format(ticker)) for ticker in missed_tickers])
        return running_message + failures

    def __print_specific_pokemon_element(self, pokemon_element):
        return f'**{pokemon_element.pokemon_name}** {pokemon_element.ens_name} @ { pokemon_element.price_string } '

    def __show_pokemon_all_floors(self, data_manager):
        pokemons = data_manager.get_pokemon()
        string_elements = []

        first_element = pokemons.get('all')[0]
        string_elements.append(f'Pokemon Floor is { bold(first_element.price_string) } ( { first_element.ens_name } )\n')

        gens = pokemons.get('gens')
        for key,val in gens.items():
            if val:
                first = True
                for pokemon_element in val:
                    if first:
                        string_elements.append(f'**Gen { key }** | { pokemon_element.price_string }')
                        first = False
            else:
                string_elements.append(f'**Gen { key }** has no pokemon for sale.')
        return '\n'.join(string_elements)

    def __show_pokemon_floor(self, data_manager, generation):
        pokemons = data_manager.get_pokemon()
        string_elements = []

        gens = pokemons.get('gens')
        mon = gens[int(generation)]
        if mon:
            first = True
            for pokemon_element in mon:
                if first:
                    string_elements.append(f'**Gen { generation }** Floor is { bold(pokemon_element.price_string) } ( { pokemon_element.ens_name } )\n')
                    first = False
                string_elements.append(self.__print_specific_pokemon_element(pokemon_element))
        else:
            string_elements.append(f'**Gen { generation }** has no pokemon for sale.')
        return '\n'.join(string_elements)

    def __show_carousel(self, data_manager):
        tokens = data_manager.update_all_token_prices()
        return '\n'.join([token.message for token in tokens])

    def __get_collection(self, data_manager, collection_string):
        collection = None
        if collection_string.startswith('night'):
            collection = NIGHTBIRDS_COLLECTION
        elif collection_string.startswith('moon'):
            collection = MOONBIRDS_COLLECTION
        elif collection_string.startswith('wass'):
            collection = WASSIES_COLLECTION
        else:
            return "Please include a collection\n**ens** pokemon, 999\n**nft** wassies, nightbirds, moonbirds"
        floor = data_manager.get_collection_floor(collection)
        return floor.price_string    #'\n'.join([token.message for token in tokens])

    def __show_prices(self, remainder, token_manager, running_message=''):
        token_tickers = remainder
        if len(token_tickers) > 10:
            token_tickers = token_tickers[:10]
            running_message = running_message + "**Error: Can only show 10 tokens!**\n\n"
        if len(token_tickers) > 1:
            running_message = running_message + "**Showing shitcoin prices!**\n------------------------"

        token_tickers = token_tickers[::-1]
        tokens = token_manager.get_priced_token_set(token_tickers)
        while len(tokens) > 0:
            token = tokens.pop()
            price_string = token.message
            running_message = running_message + '\n' + price_string

            token_tickers = [x for x in token_tickers if not (x == token.ticker or x == token.cg_id)]

        failures = "\n" + "\n".join([bold("Failed to find {0}.".format(ticker)) for ticker in token_tickers])
        return running_message + failures

    def __decipher_command(self, remainder, data_manager, settings): #Returns message string
        command = remainder.pop().lower()
        if command == 'floor' or command == 'floors':
            if not remainder or remainder[0].startswith('poke'):
                return self.__show_pokemon_all_floors(data_manager)
            elif not remainder:
                return "Please include a collection\n**ens** pokemon, 999\n**nft** wassies, nightbirds, moonbirds"
            return self.__get_collection(data_manager,remainder[0])
        elif command == 'gen' or command == 'generation':
            if not remainder:
                return bold("Missing argument for generation.")
            generation = remainder.pop()
            generation_int = int(generation)
            return self.__show_pokemon_floor(data_manager,generation)
        elif command == 'add':
            return self.__add_tokens_to_cycle(remainder,data_manager,settings)
        elif command == 'delete' or command == 'remove':
            return self.__remove_tokens_from_cycle(remainder,data_manager)
        elif command == 'carousel':
            return self.__show_carousel(data_manager)
        elif command == 'price' or command =='p':
            return self.__show_prices(remainder, data_manager.token_manager)
        elif command == 'gas':
            return data_manager.gas.message
        elif command == 'denom' or command == 'denomination':
            if not remainder:
                return bold("Missing argument for denomination.")
            denom = remainder.pop().lower()
            if settings.update_denomination(denom):
                return bold("Updated denomination to {0}!".format(denom))
            else:
                return bold("Failed to update denomination.")
        elif command == 'speed':
            if not remainder:
                return bold("Missing argument for cycle speed.")
            speed = remainder.pop()
            if settings.update_speed(speed):
                return bold("Successfully updated status cycle speed to {0} seconds!".format(settings.cycle_length))
            return bold("Failed to updated status cycle speed.")
        elif command == 'init':
            data_manager.token_manager.clear()
            base_message = "**Initializing Silph Bot!**\n------------------------\n"
            return base_message + self.__add_tokens_to_cycle(['eth'],data_manager,settings)
        elif command == 'help':
            return MENU_COPY
        else:
            return #"Command not found | Was processed as {0}".format(remainder)

    def __prepare_response(self, message, data_manager, settings):
        if self.__is_command(message):
            stripped = message.content[1:] #doing it this way allows no space between prompt | eg $eth is accepted
            remainder = str(stripped).split() #all words in list after delim
            return self.__decipher_command(remainder[::-1], data_manager, settings)
        elif self.__is_price_command(message):
            stripped = message.content[1:] #doing it this way allows no space between prompt | eg $eth is accepted
            remainder = str(stripped).split() #all words in list after delim
            if len(remainder) >= 1:
                if data_manager.token_manager.exists(remainder[0]):
                    return self.__show_prices(remainder, data_manager.token_manager)
        elif message.content == '🌽' or message.content.lower() == 'corn':
            return self.__show_prices(['bitcoin'], data_manager.token_manager)
        elif 'rook' in message.content.lower():
            return "Shush... We don't say that here."

    async def process_message_as_command(self, message, data_manager, settings):
        # await self.process_message_for_reaction(message)

        response = self.__prepare_response(message, data_manager, settings)
        if response:
            await message.channel.send(response)

        await self.run_background_fetch(message,data_manager)

    async def run_background_fetch(self,message,data_manager):
        if self.__is_command(message):
            stripped = message.content[1:] #doing it this way allows no space between prompt | eg $eth is accepted
            remainder = str(stripped).split()
            if len(remainder) > 0:
                command = remainder.pop().lower()
                if command == 'init':
                    await data_manager.load_ens()

    async def process_reaction_add(self, bot, payload):
        if payload.message_id == RULES_MESSAGE_ID:
            guild = bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            if payload.emoji.name == "🌺":
                role = get(guild.roles, name="bloomer")
                await member.add_roles(role)
                response = f"{member.display_name} has selected 🌺!\n\n**Their commitment is official and they are now a Bloomer!**"
                general_channel = get_channel_by_name(guild, "🌺│home")
                await general_channel.send(response)
            else:
                for role_info in DISCORD_ROLE_TRIGGERS:
                    if payload.emoji.id == role_info.get("emoji_id"):
                        general_channel = get_channel_by_name(guild, "🌺│home")
                        role = get(guild.roles, name=role_info.get("role"))
                        response = (
                            f"{member.display_name} has marked their interest in the **{role_info.get('name')}** pod!"
                        )
                        await general_channel.send(response)
                        if role is None:
                            logging.info(f"Role {role_info.get('role')} not found")
                            return
                        await member.add_roles(role)

    async def make_user_role(self,user,role=ROLE_WHEN_NEW_USER_CONFIRMED):
        for guild_role in user.guild.roles:
            if str(guild_role).startswith(role):
                await user.add_roles(guild_role)

    async def process_message_for_reaction(self, message):
        lower = message.content.lower()
        if lower.startswith('corn') or lower.startswith('btc') or lower.startswith('bitcoin'):
            await message.add_reaction('🌽')

    async def process_new_member(self, member: discord.Member) -> None:
    # Send to welcome channel
        welcome_channel = get(member.guild.channels, name="welcome")
        collab_land_join_channel = get(member.guild.channels, name="collabland-join")
        start_here_channel = get(member.guild.channels, name="start-here")
        await welcome_channel.send(
            f" 🌺 Welcome {member.mention}  to {member.guild.name}! We are pleased to have you here 🌺\n"
            "\n"
            "Take a moment to read and agree to the rules before you get started!"
            "\n"
            f"If you are an existing aXP, bXP, or cXP Hodler, please head over to <#{collab_land_join_channel.id}> to verify your wallet in order to receive your respective role! \n"
            "\n"
            f"Refer to <#{start_here_channel.id}> for more details about the studio!"
        )



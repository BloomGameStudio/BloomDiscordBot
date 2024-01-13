import discord
from discord.ext import commands
from discord import Embed
import logging
import textwrap
import re
from domain.contributor import Contributor
from domain.contributor_mention import ContributorMention
from shared.constants import GUILD_ID
from shared.constants import SYNC_COMMANDS

"""
Handles all event hooks for the discord bot application.

on_ready is used to initialize the application.
on_message is used to scan all incoming messages for contributor emojis.
on_reaction_add is used to scan all incoming reactions for contributor emojis.
on_event is currently unused. 
"""
class SharedEventHookCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Handle bot startup hook.
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user.name} ({self.bot.user.id})")
        await self.bot.change_presence()
        guild = self.bot.get_guild(GUILD_ID)
        print(f"Guild found {guild}")

        # TODO: re-enable later
        #if guild:
        #    # Start the background task to check events automatically every hour
        #    check_events.start(bot)
        #else:
        #    logging.error("Discord server ID not found")

        if SYNC_COMMANDS:
            print('Trying to sync up the commands added by the cogs...')

            try:
                sync = await self.bot.tree.sync()
                print(f"Sync Results:\r\n{sync}")
            except Exception as e:
                print(f"Error during sync: {e}")
        else:
            print("Skipped syncing commands, if you need to resync, alter SYNC_COMMANDS in constants.py.")


        print("Ready to go!")

    # Handle scanning messages for emojis of the user.
    @commands.Cog.listener()
    async def on_message(self, message):
        await SharedEventHookCog.scan_message_for_emojis_and_dm(self, message)
        return

    # Handle scanning messages for emojis of the user.
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        await SharedEventHookCog.scan_reaction_and_dm(self, reaction, user)
        return

    @commands.Cog.listener()
    async def on_scheduled_event_create(self, event):
        print(f"New scheduled event created: {event.name}")
        # TODO: Refactor into the database.
        #await add_event(event)

    # Scans a message for all emojis, and if there is a related contributor to them, alerts the contributor.
    # Lazily loads all of the contributors using an AND statement on the database query, should be relatively performant.
    async def scan_message_for_emojis_and_dm(self, message: discord.Message):
        """
        Scans a message for emojis and DMs relevant contributors.

        Accesses the ORM dataset to scan the contributor list for matching emojis.

        Parameters
        ----------
        message : discord.Message
            The message to scan.
        """
        # Get all emojis from message.
        custom_emojis = re.findall(r'<[a]?:\w*:\d*>', message.content)
        print(custom_emojis)
        if len(custom_emojis) > 0:
            print(f"Emojis found inside of message: {custom_emojis}")
            contributors = await Contributor.filter(emoji_string__in=custom_emojis)
            print(f"Searched contributors in DB: {contributors}")
            for c in contributors:
                try:
                    print(f'Found matching discord user for contributor: {c}')
                    user_to_alert = await self.bot.fetch_user(c.member_id)
                    #print (user_to_alert)
                    #alert_channel = await user_to_alert.create_dm()
                    e = Embed()
                    e.url = f"{message.jump_url}"
                    e.title = f"You have been mentioned in a message!"
                    e.description = f"{message.content}"
                    await user_to_alert.send(embed=e)

                    # Creates a link between this message and the user that was alerted.
                    # Will help us keep extensive records of how useful this is and will
                    # provide a great entry point for analytics.
                    mention_object = await ContributorMention.create(
                        member_id=message.author.id,
                        channel_id=message.channel.id,
                        message_id=message.id,
                        is_reaction=False,
                        contributor=c
                    )

                    print(f"Stored this instance of the mention in the database:{mention_object}")
                except Exception as e:
                    print(f"{'dm_user', e}")
        return custom_emojis

    # More or less the same thing as message scanning but handles reactions.
    # Could probably be combined with the message method but I wasn't thinking of how correctly.
    async def scan_reaction_and_dm(self, reaction: discord.Reaction, user: discord.User):
        """
        Scans a reactions for emojis and DMs relevant contributors.

        Accesses the ORM dataset to scan the contributor list for matching emojis.

        Parameters
        ----------
        reaction : discord.Reaction
            The Reaction to scan.
        user : discord.User
            The User to scan.
        """

        if user == self.bot.user:
            return
        
        print(reaction.emoji)

        contributors = await Contributor.filter(emoji_string=reaction.emoji)
        for c in contributors:
            try:
                print(f'Found matching discord user for contributor: {c}')
                user_to_alert = await self.bot.fetch_user(c.member_id)
                #print (user_to_alert)
                #alert_channel = await user_to_alert.create_dm()
                e = Embed()
                e.url = f"{reaction.message.jump_url}"
                e.title = f"Your emoji was used to react to a message!"
                e.description = f"{reaction.message.content}"
                await user_to_alert.send(embed=e)

                # Creates a link between this message and the user that was alerted.
                # Will help us keep extensive records of how useful this is and will
                # provide a great entry point for analytics.
                mention_object = await ContributorMention.create(
                    member_id=reaction.message.author.id,
                    channel_id=reaction.message.channel.id,
                    message_id=reaction.message.id,
                    is_reaction=True,
                    contributor=c
                )

                print(f"Stored this instance of the mention in the database:{mention_object}")
            except Exception as e:
                print(f"{'dm_user', e}")

        #if reaction.emoji == "📝":
        #    # Redo proposal edit/creation with modals here, easy enough... or... maybe...
        #    # maybe this was already handled by the /find_proposal command. could slim this whole
        #    # area down to almost nothing.
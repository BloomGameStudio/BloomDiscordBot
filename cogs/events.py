"""
The EventCommandsCog class is a cog that contains for listing events associated with a guild.
It contains the following commands:
- list_events: Lists the events associated with this guild when the "list_events" command is invoked.
- on_scheduled_event_create: Handles the "on_scheduled_event_create" event. This event is triggered when a new scheduled event is created.
- on_message: Event triggered when a message is sent in a server the bot is in. This happens in the "on_message" event.
- on_reaction_add: Event triggered when a reaction is added to a message in a sever the bot is in. This happens in the "on_reaction_add" event.
- on_raw_reaction_add: Event triggered when a raw reaction is added to a message in a server the bot is in. This happens in the "on_raw_reaction_add" event.
- on_member_join: Event triggered when a new member joins a server the bot is in. This happens in the "on_member_join" event.
"""

import discord
import time
from discord.ext import commands
from discord import app_commands
from utils.utils import Utils
from logger.logger import logger
from events.event_operations import EventOperations
from consts.constants import RULES_MESSAGE_ID
from database.service import DatabaseService


class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.event_operations = EventOperations(self.bot)

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Handles the on_ready event. This event is triggered when the bot has successfully connected.
        """
        logger.info(f"Logged in as {self.bot.user.name} ({self.bot.user.id})")

    @commands.Cog.listener()
    async def on_scheduled_event_create(self, event: discord.ScheduledEvent):
        """
        Handles the on_scheduled_event_create event. This event is triggered when a new scheduled event is created.
        notify_new_event is then invoked to notify the guild about the new event after a delay.
        """
        logger.info(f"New scheduled event created: {event.name}")
        try:
            db_service = DatabaseService()
            db_service.save_event(event.id, event.guild_id, None, time.time())
            await self.event_operations.notify_new_event(event, event.guild_id)
            logger.info(f"Successfully processed new event: {event.name}")
        except Exception as e:
            logger.error(f"Error in on_scheduled_event_create: {e}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Event triggered when a message is sent in a server the bot is in.

        Parameters:
        self (EventCommandsCog): An instance of the EventCommandsCog class.
        message (Message): The message that was sent.

        Returns:
        None
        """
        await self.event_operations.handle_message(message)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        """
        Event triggered when a reaction is added to a message in a sever the bot is in.

        Parameters:
        self (EventCommandsCog): An instance of the EventCommandsCog class.
        reaction (Reaction): The reaction that was added.
        user (User): The user who added the reaction.

        Returns:
        """
        await self.event_operations.handle_reaction(reaction, user)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """
        Event triggered when a raw reaction is added to a message in a server the bot is in.

        Parameters:
        payload: The payload for the raw reaction add event.

        Returns:
        None
        """
        if payload.message_id == RULES_MESSAGE_ID:
            await self.event_operations.process_reaction_add(payload)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """
        Event triggered when a new member joins a server the bot is in.

        Parameters:
        member (Member): The member who joined.

        Returns:
        None
        """
        logger.info(f"New member: {member.name} has joined: {member.guild.name}")
        await self.event_operations.process_new_member(member)

    @app_commands.command(name="list_events")
    async def list_events(self, interaction: discord.Interaction):
        """
        Lists the events associated with this guild.

        Parameters:
        interaction (Interaction): The interaction of the command invocation.
        """

        guild = interaction.guild

        event_list = guild.scheduled_events

        event_urls = [
            f"https://discord.com/events/{guild.id}/{event.id}" for event in event_list
        ]

        formatted_events = [
            f":link: **Event Link <{url}>** :link:" for url in event_urls
        ]
        formatted_string = "\n\n".join(formatted_events)
        await interaction.response.send_message(
            f"🗓️ **All Events**🗓️ \n\n{formatted_string}"
        )

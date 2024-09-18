"""
The EventCommandsCog class is a cog that contains for listing and deleting events.
It contains the following commands:
- list_events: Lists the events associated with this guild.
- delete_event: Deletes an event from the guild.
"""

import discord
import time
from discord.ext import commands
from discord import app_commands
from helpers.helpers import save_notified_events
from logger.logger import logger
from discord import ScheduledEvent
from events.event_operations import (
    notify_new_event,
    process_new_member,
    handle_message,
    handle_reaction,
    process_reaction_add,
)
from consts.constants import RULES_MESSAGE_ID


class EventsCog(commands.Cog):
    def __init__(self, bot, contributors, emoji_dicts):
        self.bot = bot
        self.contributors = contributors
        self.emoji_dicts = emoji_dicts

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Handles the on_ready event. This event is triggered when the bot has successfully connected.
        """
        print(f"Logged in as {self.bot.user.name} ({self.bot.user.id})")

    @commands.Cog.listener()
    async def on_scheduled_event_create(self, event: ScheduledEvent):
        """
        Handles the on_scheduled_event_create event. This event is triggered when a new scheduled event is created.
        notify_new_event is then invoked to notify the guild about the new event after a delay.

        Parameters:
        event (ScheduledEvent): The event that was created.
        """
        logger.info(f"New scheduled event created: {event.name}")
        self.bot.notified_events[event.id] = time.time()
        save_notified_events(self.bot.notified_events)
        await notify_new_event(self.bot, event, event.guild_id)

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
        await handle_message(self.bot, message, self.emoji_dicts)

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
        await handle_reaction(self.bot, reaction, user, self.emoji_dicts)

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
            await process_reaction_add(self.bot, payload)

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
        await process_new_member(member)

    @app_commands.command(name="list_events")
    async def list_events(self, interaction: discord.Interaction):
        """
        Lists the events associated with this guild.

        Parameters:
        interaction (Interaction): The interaction of the command invocation.
        """

        guild = interaction.guild

        # Get the list of events
        event_list = guild.scheduled_events

        # Extract event information
        event_urls = [
            f"https://discord.com/events/{guild.id}/{event.id}"
            for event in event_list  # Get the event URL
        ]

        # Format the information
        formatted_events = [
            f":link: **Event Link <{url}>** :link:"  # Wrap the URL in <> to prevent Discord from generating an embed
            for url in event_urls
        ]
        formatted_string = "\n\n".join(formatted_events)
        await interaction.response.send_message(
            f"🗓️ **All Events**🗓️ \n\n{formatted_string}"
        )

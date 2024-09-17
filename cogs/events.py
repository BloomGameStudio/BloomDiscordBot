"""
The EventCommandsCog class is a cog that contains for listing and deleting events.
It contains the following commands:
- list_events: Lists the events associated with this guild.
- delete_event: Deletes an event from the guild.
- on_ready: Handles the on_ready event. This event is triggered when the bot has successfully connected.
- on_scheduled_event_create: Handles the on_scheduled_event_create event. This event is triggered when a new scheduled event is created.
- on_message: Event triggered when a message is sent in a server the bot is in.
- on_reaction_add: Event triggered when a reaction is added to a message in a sever the bot is in.
- on_raw_reaction_add: Event triggered when a raw reaction is added to a message in a server the bot is in.
- on_member_join: Event triggered when a new member joins a server the bot is in.
"""

import discord
import time
from discord.ext import commands
from discord import app_commands
from utils.utils import Utils
from logger.logger import logger
from discord import ScheduledEvent
from events.event_operations import EventOperations
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
        Utils.save_notified_events(self.bot.notified_events)
        await EventOperations.notify_new_event(self.bot, event, event.guild_id)

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
        await EventOperations.handle_message(self.bot, message, self.emoji_dicts)

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
        await EventOperations.handle_reaction(
            self.bot, reaction, user, self.emoji_dicts
        )

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
            await EventOperations.process_reaction_add(self.bot, payload)

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
        await EventOperations.process_new_member(member)

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

    @app_commands.command(name="delete_event")
    async def delete_event(
        self, interaction: discord.Interaction, event_name: str = None
    ):
        """
        Deletes an event from the guild.

        Parameters:
        interaction (Interaction): The interaction of the command invocation.
        event_name (str): The name of the event to be deleted.
        """
        if event_name is None:
            await interaction.response.send_message(
                "Please enter an event name with this command. Example: `/delete_event My Event`"
            )
            return

        guild = interaction.guild

        await interaction.response.defer()

        permitted = await Utils.get_guild_member_check_role(interaction)

        if not permitted:
            await interaction.response.send_message(
                "You do not have permission to use this command."
            )
            return

        events = await guild.fetch_scheduled_events()
        event = next((e for e in events if e.name == event_name), None)

        if event:
            await event.delete()
            await interaction.followup.send(f"Event '{event_name}' has been deleted 🗑️")
        else:
            await interaction.followup.send(f"No event found with name '{event_name}'.")

"""
Events module for the bot. This module contains the event handlers for the bot.
The logic for these events is implemented in the event_operations module.
"""


from logger.logger import logger
from discord import ScheduledEvent, Message, Reaction, User
from discord.ext import commands
from events.event_operations import notify_new_event
from tasks.tasks import check_events, check_concluded_proposals_task
from .event_operations import (
    handle_message,
    handle_reaction,
    process_reaction_add,
    process_new_member,
)
from consts.constants import RULES_MESSAGE_ID


def setup_event_events(bot: commands.Bot) -> None:
    @bot.event
    async def on_ready():
        """
        Handles the on_ready event. This event is triggered when the bot has successfully connected.
        check_events is then started to check for upcoming events every hour.
        Concluded_proposals_task is then started to check for any proposals that have ended.
        """
        logger.info(f"Logged in as {bot.user.name} ({bot.user.id})")
        await bot.change_presence()
        logger.info(f"Starting background task for all guilds")
        check_events.start(bot)
        check_concluded_proposals_task.start(bot)
        # Perform tree synchronization
        try:
            await bot.tree.sync()
        except Exception as e:
            logger.error(e)

    @bot.event
    async def on_scheduled_event_create(event: ScheduledEvent) -> None:
        """
        Handles the on_scheduled_event_create event. This event is triggered when a new scheduled event is created.
        notify_new_event is then invoked to notify the guild about the new event after a delay.

        Parameters:
        event (ScheduledEvent): The event that was created.
        """
        logger.info(f"New scheduled event created: {event.name}")
        await notify_new_event(bot, event, event.guild_id)

    @bot.event
    async def on_message(message: Message) -> None:
        """
        Event triggered when a message is sent in a server the bot is in.

        Parameters:
        message (Message): The message that was sent.

        Returns:
        None
        """
        await handle_message(bot, message)

    @bot.event
    async def on_reaction_add(reaction: Reaction, user: User) -> None:
        """
        Event triggered when a reaction is added to a message in a server the bot is in.

        Parameters:
        reaction (Reaction): The reaction that was added.
        user (User): The user who added the reaction.

        Returns:
        None
        """
        await handle_reaction(bot, reaction, user)

    @bot.event
    async def on_raw_reaction_add(payload):
        """
        Event triggered when a raw reaction is added to a message in a server the bot is in.

        Parameters:
        payload: The payload for the raw reaction add event.

        Returns:
        None
        """
        if payload.message_id == RULES_MESSAGE_ID:
            await process_reaction_add(bot, payload)

    @bot.event
    async def on_member_join(member):
        """
        Event triggered when a new member joins a server the bot is in.

        Parameters:
        member: The member who joined.

        Returns:
        None
        """
        logger.info(f"New member: {member.name} has joined: {member.guild.name}")
        await process_new_member(member)

    @bot.event
    async def on_command_error(ctx, error):
        """
        Event triggered when a command error occurs.

        Parameters:
        ctx: The context in which the command was invoked.
        error: The error that occurred.

        Returns:
        None
        """
        if isinstance(error, commands.CommandNotFound):
            await ctx.message.channel.send("Command not found")

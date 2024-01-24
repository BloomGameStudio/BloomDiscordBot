import logging
from discord import ScheduledEvent
from discord.ext import commands
from events.event_operations import notify_new_event
from events.tasks import check_events
from typing import Dict

"""
The bot listens for the on_ready event and then calls check_events in tasks.py
This task runs every hour to check for upcoming events within the next 24 hours.

The bot will listen for the on_scheduled_event_create event and then call notify_new_event in event_operations.py
setup_event_events is used so that all event events can be loaded at once. instead of individually.
"""


def setup_event_events(
    bot: commands.Bot
) -> None:
    @bot.event
    async def on_ready():
        logging.info(f"Logged in as {bot.user.name} ({bot.user.id})")
        await bot.change_presence()
        logging.info(f"Starting background task for all guilds")
        check_events.start(bot)

    @bot.event
    async def on_scheduled_event_create(event: ScheduledEvent) -> None:
        logging.info(f"New scheduled event created: {event.name}")
        await notify_new_event(bot, event, event.guild_id)

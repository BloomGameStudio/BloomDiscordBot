"""
Setup event events for the bot.

The bot listens for the on_ready event and then starts check_events, located in tasks.py
This task runs every hour to check for upcoming events within the next 24 hours.

The bot will listen for the on_scheduled_event_create event and then invoke notify_new_event in event_operations.py
setup_event_events is used so that all event events can be loaded at once. instead of individually.
"""


from logger.logger import logger
from discord import ScheduledEvent
from discord.ext import commands
from events.event_operations import notify_new_event
from events.tasks import check_events


def setup_event_events(bot: commands.Bot) -> None:
    """
    Set up the event handlers for the bot.

    Parameters:
    bot (commands.Bot): The bot instance.
    """

    @bot.event
    async def on_ready():
        """
        Handles the on_ready event. This event is triggered when the bot has successfully connected.
        check_events is then started to check for upcoming events every hour.
        """
        logger.info(f"Logged in as {bot.user.name} ({bot.user.id})")
        await bot.change_presence()
        logger.info(f"Starting background task for all guilds")
        try:
            await bot.tree.sync()
        except Exception as e:
            logger.error(e)
        check_events.start(bot)

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

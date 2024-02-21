from logger.logger import logger
from discord import ScheduledEvent
from discord.ext import commands
from events.event_operations import notify_new_event
from events.tasks import check_events
from gov.tasks import concluded_proposals_task

def setup_event_events(bot: commands.Bot) -> None:
    @bot.event
    async def on_ready():
        """
        Handles the on_ready event. This event is triggered when the bot has successfully connected.
        check_events is then started to check for upcoming events every hour.
        """
        logger.info(f"Logged in as {bot.user.name} ({bot.user.id})")
        await bot.change_presence()
        logger.info("Starting background tasks for all guilds")
        try:
            await bot.tree.sync()
        except Exception as e:
            logger.error(e)
        check_events.start(bot)
        concluded_proposals_task.start(bot)  # Moved inside on_ready event

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
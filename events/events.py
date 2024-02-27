from logger.logger import logger
from discord import ScheduledEvent
from discord.ext import commands
from events.event_operations import notify_new_event
from events.tasks import check_events
from cogs.help import HelpCommandCog
from cogs.contributors import ContributorCommandsCog

def setup_event_events(bot: commands.Bot, contributors, emoji_dicts: dict) -> None:
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
        check_events.start(bot)
        
        # Load the HelpCommandCog
        await bot.add_cog(HelpCommandCog(bot))
        logger.info("HelpCommandCog loaded")
        await bot.add_cog(ContributorCommandsCog(bot, contributors, emoji_dicts))
        logger.info("ContributorCommandsCog loaded")
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
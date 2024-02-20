from logger.logger import logger
from discord.ext import tasks, commands
from events.event_operations import (
    get_guild_scheduled_event_users,
    save_posted_events,
    fetch_upcoming_events,
)
from events.task_operations import format_and_send_message
from shared.helpers import get_channel_by_name
from consts.constants import GENERAL_CHANNEL

# Events/tasks.py is responsible for handling the background tasks associated with Discord events.


@tasks.loop(minutes=60)
async def check_events(discord_bot: commands.Bot, custom_bot) -> None:
    """
    Check for upcoming events every 60 minutes. If there are any new events, they are posted to Discord.
    Interested users are identified and event details are formatted in a message and sent to the general channel.
    This is done through format_and_send_message invocation.

    The posted events are then saved to a JSON file to prevent duplicate posts.

    Parameters:
    discord_bot (commands.Bot): The discord bot instance.
    custom_bot: The custom bot instance.
    """
    if not discord_bot.guilds:
        logger.warning("Guild not found")

    for guild in discord_bot.guilds:
        try:
            channel = get_channel_by_name(guild, GENERAL_CHANNEL)
        except ValueError as e:
            logger.error(f" Cannot check events for guild {guild}, Error: {e}")
            continue  # Skip this guild and move on to the next one

        upcoming_events = await fetch_upcoming_events(guild)

        if not upcoming_events:
            logger.info(f"No upcoming events in the next 24 hours for guild {guild}.")
            continue

        # Check if it's the initial run or not
        if not discord_bot.posted_events:
            # Initial run, post events to Discord
            for event in upcoming_events:
                # Fetch subscribed users for each event
                users = get_guild_scheduled_event_users(guild.id, event.id)
                await format_and_send_message(event, users, channel)

            save_posted_events([event.id for event in upcoming_events])
        else:
            # Subsequent runs, filter out already posted events
            new_events = [
                event for event in upcoming_events if event.id not in discord_bot.posted_events
            ]

            if new_events:
                for event in new_events:
                    # Fetch subscribed users for each event
                    users = get_guild_scheduled_event_users(guild.id, event.id)
                    await format_and_send_message(event, users, channel)

                # Update the bot.posted_events list only for newly posted events
                discord_bot.posted_events.extend([event.id for event in new_events])
                save_posted_events(discord_bot.posted_events)
            else:
                logger.info(
                    f"No new upcoming events in the next 24 hours for guild {guild}."
                )

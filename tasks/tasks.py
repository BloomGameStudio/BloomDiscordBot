"""
tasks module contains the check_events task that is responsible for checking for upcoming events every 60 minutes.
If there are any new events, they are posted to Discord. Interested users are identified and event details are formatted in a message and sent to the general channel.
"""

from logger.logger import logger
from discord.ext import tasks, commands
from events.event_operations import (
    get_guild_scheduled_event_users,
    save_posted_events,
    fetch_upcoming_events,
)
from helpers import get_channel_by_name
from consts.constants import GENERAL_CHANNEL


@tasks.loop(minutes=60)
async def check_events(bot: commands.Bot) -> None:
    if not bot.guilds:
        logger.warning("Guild not found")

    for guild in bot.guilds:
        try:
            channel = get_channel_by_name(guild, GENERAL_CHANNEL)
        except ValueError as e:
            logger.error(f" Cannot check events for guild {guild}, Error: {e}")
            continue

        upcoming_events = await fetch_upcoming_events(guild)

        if not upcoming_events:
            logger.info(f"No upcoming events in the next 24 hours for guild {guild}.")
            continue

        if not bot.posted_events:
            for event in upcoming_events:
                users = get_guild_scheduled_event_users(guild.id, event.id)
                
                guild_id = event.guild.id
                user_mentions = [f"<@{user['user_id']}>" for user in users]
                user_list_string = ", ".join(user_mentions)

                formatted_string = (
                    f"📆 **Upcoming Events in the Next 24 Hours** 📆 \n"
                    f"\n"
                    f":link: **Event Link https://discord.com/events/{guild_id}/{event.id} :link:**\n"
                    f"\n"
                    f"{user_list_string}\n"
                )

                await channel.send(formatted_string)

            save_posted_events([event.id for event in upcoming_events])
        else:
            new_events = [
                event for event in upcoming_events if event.id not in bot.posted_events
            ]

            if new_events:
                for event in new_events:
                    users = get_guild_scheduled_event_users(guild.id, event.id)
                    
                    guild_id = event.guild.id
                    user_mentions = [f"<@{user['user_id']}>" for user in users]
                    user_list_string = ", ".join(user_mentions)

                    formatted_string = (
                        f"📆 **Upcoming Events in the Next 24 Hours** 📆 \n"
                        f"\n"
                        f":link: **Event Link https://discord.com/events/{guild_id}/{event.id} :link:**\n"
                        f"\n"
                        f"{user_list_string}\n"
                    )

                    await channel.send(formatted_string)

                bot.posted_events.extend([event.id for event in new_events])
                save_posted_events(bot.posted_events)
            else:
                logger.info(
                    f"No new upcoming events in the next 24 hours for guild {guild}."
                )
import logging
from discord.ext import tasks, commands
from events.event_operations import get_guild_scheduled_event_users, save_posted_events, fetch_upcoming_events
from shared.constants import GUILD_ID, GENERAL_CHANNEL_ID
from events.task_operations import format_and_send_message


@tasks.loop(minutes=60)
async def check_events(bot: commands.Bot):
    guild = bot.get_guild(GUILD_ID)

    if guild:
        upcoming_events = await fetch_upcoming_events(guild)

        if not upcoming_events:
            logging.info("No upcoming events in the next 24 hours.")
            return

        channel = guild.get_channel(GENERAL_CHANNEL_ID)

        if not channel:
            logging.warning("Event channel not found")
            return
        
        # Check if it's the initial run or not
        if not bot.posted_events:
            # Initial run, post events to Discord
            for event in upcoming_events:
                # Fetch subscribed users for each event
                users = get_guild_scheduled_event_users(event.id)
                await format_and_send_message(event, users, channel)

            save_posted_events([event.id for event in upcoming_events])
        else:
            # Subsequent runs, filter out already posted events
            new_events = [event for event in upcoming_events if event.id not in bot.posted_events]

            if new_events:
                for event in new_events:
                    # Fetch subscribed users for each event
                    users = get_guild_scheduled_event_users(event.id)
                    await format_and_send_message(event, users, channel)

                # Update the bot.posted_events list only for newly posted events
                bot.posted_events.extend([event.id for event in new_events])
                save_posted_events(bot.posted_events)
            else:
                logging.info("No new upcoming events in the next 24 hours.")
    else:
        logging.warning("Guild not found")


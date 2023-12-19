import os
import logging
from datetime import datetime, timezone
from discord.ext import tasks, commands
from updates.updates import load_posted_events, get_guild_scheduled_event_users, save_posted_events, GUILD_ID, GENERAL_CHANNEL_ID

@tasks.loop(minutes=1)
async def check_events(bot: commands.Bot):
    guild = bot.get_guild(GUILD_ID)

    if guild:
        current_time = datetime.now().astimezone(timezone.utc)
        events = await guild.fetch_scheduled_events()
        upcoming_events = []

        for event in events:
            time_difference = event.start_time - current_time
            if 0 <= time_difference.total_seconds() <= 24 * 3600:
                upcoming_events.append(event)

        if not upcoming_events:
            logging.info("No upcoming events in the next 24 hours.")
            return

        channel = guild.get_channel(GENERAL_CHANNEL_ID)

        if not channel:
            logging.warning("Event channel not found")
            return

        # Common message part
        common_message = f"<:inevitable_bloom:1178256658741346344> **Upcoming Events in the Next 24 Hours** <:inevitable_bloom:1178256658741346344> \n"

        # Load posted events
        posted_events = load_posted_events()

        # Check if it's the initial run or not
        if not posted_events:
            # Initial run, post events to Discord
            for event in upcoming_events:
                # Fetch subscribed users for each event
                users = get_guild_scheduled_event_users(event.id)
                await format_and_send_message(event, users, common_message, channel)

            save_posted_events([event.id for event in upcoming_events])
        else:
            # Subsequent runs, filter out already posted events
            new_events = [event for event in upcoming_events if event.id not in posted_events]

            if new_events:
                for event in new_events:
                    # Fetch subscribed users for each event
                    users = get_guild_scheduled_event_users(event.id)
                    await format_and_send_message(event, users, common_message, channel)

                # Update the posted_events list only for newly posted events
                posted_events.extend([event.id for event in new_events])
                save_posted_events(posted_events)
            else:
                logging.info("No new upcoming events in the next 24 hours.")
    else:
        logging.warning("Guild not found")

async def format_and_send_message(event, users, common_message, channel):
    user_mentions = [f"<@{user['user_id']}>" for user in users]
    user_list_string = ', '.join(user_mentions)

    formatted_string = (
        f"{common_message}\n"
        f":link: **Event Link https://discord.com/events/{GUILD_ID}/{event.id} :link:**\n"
        f"\n"
        f"{user_list_string}\n"
    )

    # Send message
    await channel.send(formatted_string)

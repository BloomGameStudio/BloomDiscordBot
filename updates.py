from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

def format_event(event):
    # Format the event start time for Discord time
    formatted_start_time = event.start_time.strftime('<t:%s>' % str(int(event.start_time.timestamp())))

    formatted_event = (
        f"**Event Name:** {event.name}\n"
        f"**Event ID:** {event.id}\n"
        f"**Event Start Time:** {formatted_start_time}\n"
        f"**Event Description:** {event.description}\n"
        f"**Event Interested:** {event.user_count}"
    )
    return formatted_event

async def notify_new_event(bot, event):
    guild_id = int(os.getenv("GUILD_ID"))
    guild = bot.get_guild(guild_id)

    if guild:
        # Wait for 60 mins before sending the notification
        await asyncio.sleep(3600)

        # Fetch the event again to get the updated details
        event = await guild.fetch_scheduled_event(event.id)
        formatted_event = format_event(event)

        channel_id = int(os.getenv("CHANNEL_ID"))
        channel = guild.get_channel(channel_id)

        if channel:
            # Send the notification
            await channel.send(f"**Newly Created Event**:\n{formatted_event}")
        else:
            print(f"Event channel not found")
    else:
        print(f"Guild not found")

def get_all_events(guild):
    return guild.scheduled_events

async def check_upcoming_events(guild, time_range=None):
    current_time = datetime.now().astimezone(timezone.utc)
    events = get_all_events(guild)
    upcoming_events = []

    # Check if the events start time is <= the current time
    # And >= the specified time range
    for event in events:
        if time_range:
            # Fetch the event again to get the updated user_count
            event = await guild.fetch_scheduled_event(event.id)

            time_difference = event.start_time - current_time
            if 0 <= time_difference.total_seconds() <= time_range:
                upcoming_events.append(event)
        else:
            upcoming_events.append(event)

    return upcoming_events

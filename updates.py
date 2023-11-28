from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os
import asyncio

#TODO:
#Delete events? Edit events?
#Emotes/emojis
#Interested users: 

load_dotenv()

def format_event(event):
    formatted_event = f"**Event Name:** {event.name}\n**Event ID:** {event.id}\n**Event Start Time:** {event.start_time}\n**Event Description:** {event.description}"
    return formatted_event

async def notify_new_event(bot, event):
    guild_id = int(os.getenv("GUILD_ID"))
    guild = bot.get_guild(guild_id)

    if guild:
        channel_id = int(os.getenv("CHANNEL_ID"))
        channel = guild.get_channel(channel_id)

        if channel:
            # Wait for 5 mins before sending the notification
            await asyncio.sleep(300)
            
            formatted_event = format_event(event)
            
            # Send the notification
            await channel.send(f"**Newly Created Event**:\n{formatted_event}")
        else:
            print(f"Event channel not found")
    else:
        print(f"Guild not found")

def get_all_events(guild):
    return guild.scheduled_events

def check_upcoming_events(guild, time_range=None):
    current_time = datetime.now().astimezone(timezone.utc)
    events = get_all_events(guild)
    upcoming_events = []
    
    #Check if the events start time is <= the current time
    #And >= the specified time range
    for event in events:
        if time_range:
            time_difference = event.start_time - current_time
            if 0 <= time_difference.total_seconds() <= time_range:
                upcoming_events.append(event)
        else:
            upcoming_events.append(event)

    return upcoming_events
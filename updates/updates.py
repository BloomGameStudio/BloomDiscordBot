import os
import asyncio
import json
import requests
import logging

GUILD_ID = int(os.getenv("GUILD_ID"))
GENERAL_CHANNEL_ID = int(os.getenv("GENERAL_CHANNEL_ID"))
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "updates", "posted_events.json")

def load_posted_events():
    try:
        logging.info(f"Loading events from: {FILE_PATH}")
        with open(FILE_PATH, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_posted_events(posted_events):
    try:
        logging.info(f"Saving events to: {FILE_PATH}")

        with open(FILE_PATH, "w") as file:
            json.dump(posted_events, file)
            
    except Exception as e:
        logging.error(f"Error saving posted events: {e}")
    
def format_event(event):
    # Format the event start time for Discord time
    event_url = f"https://discord.com/events/{GUILD_ID}/{event.id}"

    formatted_event = (
        f"\n"
        f" **{event.name}**\n"
        f"\n"
        f"To request someones attendance, react to this message with their emoji! \n"
        f"\n"
        f":link:** Event Link** {event_url} :link:\n"
    )
    return formatted_event

async def notify_new_event(bot, event):
    guild = bot.get_guild(GUILD_ID)

    if guild:
        # Wait for 30 mins before sending the notification
        await asyncio.sleep(60 * 1)

        # Fetch the event again to get the updated details
        event = await guild.fetch_scheduled_event(event.id)
        formatted_event = format_event(event)

        channel = guild.get_channel(GENERAL_CHANNEL_ID)

        if channel:
            # Send the notification and capture the Message object
            await channel.send(f"🌺 **__Newly Created Event__** 🌺 \n{formatted_event}")

        else:
            logging.info(f"Event channel not found")
    else:
        logging.info(f"Guild not found")

# NOTE: For some reason it doesn't appear that you can access the userIDs interested
# in a scheduled event. It's either a count, or a boolean.
# performing a GET request, however, does allow this.
def get_guild_scheduled_event_users(scheduled_event_id, limit=100, with_member=False, before=None, after=None):
    url = f"https://discord.com/api/v10/guilds/{GUILD_ID}/scheduled-events/{scheduled_event_id}/users"

    params = {
        'limit': limit,
        'with_member': with_member,
        'before': before,
        'after': after
    }

    headers = {
        'Authorization': f'Bot {DISCORD_BOT_TOKEN}'
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None
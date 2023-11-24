#When an event is deleted, it should be detected, and removed from updates.json
#Format time etc in Discord formatting
#Is Discord formatting applicable to the emotes/emojis

import discord
from discord.ext import commands
import json
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os

load_dotenv()

intents = discord.Intents.all()

# Create a bot instance with intents
bot = commands.Bot(command_prefix='!', intents=intents)

#NOTE: Put this as a helper function
# Custom JSON encoder to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Load scheduled events from updates.json
def load_scheduled_events():
    try:
        with open('updates.json', 'r') as file:
            data = json.load(file)
            # Convert start_time to datetime objects
            for event_id, event_info in data.items():
                event_info['start_time'] = datetime.fromisoformat(event_info['start_time'])
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


# Save scheduled events to updates.json
def save_scheduled_events():
    with open('updates.json', 'w') as file:
        json.dump(scheduled_events, file, indent=4, cls=DateTimeEncoder)

# Dictionary to store scheduled events
scheduled_events = load_scheduled_events()

# Event handler for on_scheduled_event_create
@bot.event
async def on_scheduled_event_create(event):
    # Store the scheduled event in the dictionary
    scheduled_events[event.id] = {
        'name': event.name,
        'start_time': event.start_time,
        'status': event.status
    }

    # Save the updated scheduled events to updates.json
    save_scheduled_events()

    print(f"New scheduled event created: {event.name}")


# Function to post event details 24 hours before it begins
async def post_event_details():
    print("Checking for scheduled events")
    print(f'Number of scheduled events: {len(scheduled_events)}')

    for event_id, event_info in scheduled_events.items():
        start_time = event_info['start_time'].replace(tzinfo=timezone.utc)  # Make start_time timezone-aware
        current_time = datetime.utcnow().replace(tzinfo=timezone.utc)  # Make current_time timezone-aware

        # Check if the event is scheduled within the next 24 hours
        # Check if the event is scheduled within the next 24 hours
    if start_time - current_time <= timedelta(hours=24) and start_time > current_time:
        print(f"Event '{event_info['name']}' is scheduled within the next 24 hours")

        # Get the #general channel (replace CHANNEL_ID with your actual channel ID)
        general_channel = bot.get_channel(os.getenv('CHANNEL_ID'))

        # Post event details
        await general_channel.send(f"Events in 24 hours or less!\n**Event Name:** {event_info['name']}\n**Start Time:** {start_time}")


# Function to load scheduled events and post details
async def load_and_post_events():
    await bot.wait_until_ready()  # Wait until the bot is fully connected and ready

    # Load scheduled events before starting the bot
    scheduled_events = load_scheduled_events()

    # Call the function to post event details
    await post_event_details()

# Command to list stored scheduled events
@bot.command(name='listevents')
async def list_events(ctx):
    if not scheduled_events:
        await ctx.send("No scheduled events found.")
    else:
        event_list = "\n".join(f"{name} - {info['start_time']} - {info['status']}" for name, info in scheduled_events.items())
        await ctx.send(f"Stored Scheduled Events:\n{event_list}")

# Event to run when the bot is fully connected and ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await load_and_post_events()

# Start the bot
bot.run(os.getenv('TOKEN'))

import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
from updates import *

intents = discord.Intents.all()

# Create a bot instance with intents
bot = commands.Bot(command_prefix='!', intents=intents)

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

    # Delay for 5 minutes (300 seconds) before checking for changes
    await asyncio.sleep(300)

    # Check if there are any changes to the event
    if has_changes(event):
        # Get the channel ID from the environment variable
        channel_id = int(os.getenv('CHANNEL_ID'))
        general_channel = bot.get_channel(channel_id)

        if general_channel:
            start_time = event.start_time.replace(tzinfo=timezone.utc)
            await general_channel.send(f"Updated Event!\n**Event Name:** {event.name}\n**Start Time:** {start_time}")
        else:
            print("General channel not found or bot doesn't have permission to send messages.")
    else:
        print("No changes to the event.")
        
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
    await load_and_post_events(bot)

# Function to check for changes in the event
def has_changes(event):
    stored_event = scheduled_events.get(event.id)
    if stored_event:
        return (
            stored_event['name'] != event.name or
            stored_event['start_time'] != event.start_time or
            stored_event['status'] != event.status
        )
    else :
        return True
# Start the bot
bot.run(os.getenv('TOKEN'))

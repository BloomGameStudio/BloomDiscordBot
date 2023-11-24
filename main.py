import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
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

async def load_and_post_events(bot):
    await bot.wait_until_ready()  # Wait until the bot is fully connected and ready

    # Load scheduled events before starting the bot
    scheduled_events = load_scheduled_events()
    await post_event_details(bot)  # Pass the bot instance to the function



# Start the bot
bot.run(os.getenv('TOKEN'))

import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from datetime import datetime
from updates import check_upcoming_events

intents = discord.Intents.all()

# Create a bot instance with intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Event handler for on_scheduled_event_create
@bot.event
async def on_scheduled_event_create(event):
    print(f"New scheduled event created: {event.name}")

# Event to run when the bot is fully connected and ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    guild_id = int(os.getenv("GUILD_ID"))
    guild = bot.get_guild(guild_id)
    
    if guild:
        check_upcoming_events(guild)
    else:
        print(f"Guild not found")

# Load the environment variables
load_dotenv()

# Start the bot
bot.run(os.getenv('TOKEN'))
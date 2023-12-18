import discord
import os
from discord.ext import commands

#Discord Config
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix="$", intents=intents)

# Load commands and events
bot.load_extension('commands')
bot.load_extension('events')

bot.run(os.getenv('DISCORD_BOT_TOKEN'))
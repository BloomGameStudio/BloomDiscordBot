import discord
import textwrap
import random
import os

# Discord Client Setup
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

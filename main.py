import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from updates import check_upcoming_events, format_event

intents = discord.Intents.all()

load_dotenv()

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    guild_id = int(os.getenv("GUILD_ID"))
    guild = bot.get_guild(guild_id)

    if guild:
        check_upcoming_events(guild)
        # Start the background task to check events automatically every 24 hours
        daily_check_events.start()
    else:
        print(f"Guild not found")

#This may have its own issues such as if the bot is restarted.
@tasks.loop(hours=24)
async def daily_check_events():
    guild_id = int(os.getenv("GUILD_ID"))
    guild = bot.get_guild(guild_id)

    if guild:
        event_list = check_upcoming_events(guild, time_range=24 * 3600)
        formatted_events = [format_event(event) for event in event_list]
        formatted_string = "\n\n".join(formatted_events)

        channel_id = int(os.getenv("CHANNEL_ID"))
        channel = guild.get_channel(channel_id)

        if channel:
            await channel.send(f"**Upcoming Events in the Next 24 Hours**:\n{formatted_string}")
        else:
            print(f"Event channel not found")
    else:
        print(f"Guild not found")

@bot.command(name='listevents')
async def listevents(ctx):
    guild = ctx.guild
    event_list = check_upcoming_events(guild)
    formatted_events = [format_event(event) for event in event_list]
    formatted_string = "\n\n".join(formatted_events)

    await ctx.send(f"**All Events**:\n{formatted_string}")

bot.run(os.getenv('TOKEN'))
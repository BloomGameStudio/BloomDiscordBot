from discord.ext import commands
import discord
import os
import logging

def setup_events(bot: events.Bot):
    @bot.event
    async def on_ready():
        logging.info(f"Logged in as {bot.user.name} ({bot.user.id})")
        await bot.change_presence(activity=discord.Game(name="Watching you sleep"))

        os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'emojis'))
        guild_id = int(os.getenv("GUILD_ID"))
        guild = bot.get_guild(guild_id)

        if guild:
            await check_upcoming_events(guild)
            # Start the background task to check events automatically every 24 hours
            daily_check_events.start()
        else:
            logging.error("Discord server ID not found")

    @bot.event
    async def on_scheduled_event_create(event):
        logging.info(f"New scheduled event created: {event.name}")
        await notify_new_event(bot, event)

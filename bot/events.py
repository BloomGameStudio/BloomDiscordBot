import os
import logging
from discord.ext import commands, tasks
from updates.updates import notify_new_event
from bot.tasks import check_events

def setup_events(bot: commands.Bot):
    @bot.event
    async def on_ready():
        logging.info(f"Logged in as {bot.user.name} ({bot.user.id})")
        await bot.change_presence()
        guild_id = int(os.getenv("GUILD_ID"))
        guild = bot.get_guild(guild_id)

        if guild:
            # Start the background task to check events automatically every 24 hours
            check_events.start(bot)
        else:
            logging.error("Discord server ID not found")

    @bot.event
    async def on_scheduled_event_create(event):
        logging.info(f"New scheduled event created: {event.name}")
        await notify_new_event(bot, event)
import logging
from discord import ScheduledEvent
from discord.ext import commands
from events.event_operations import notify_new_event
from events.tasks import check_events
from typing import Dict

"""
The bot listens for the on_ready event and then calls check_events in tasks.py
This task runs every hour to check for upcoming events within the next 24 hours.

The bot will listen for the on_scheduled_event_create event and then call notify_new_event in event_operations.py
setup_event_events is used so that all event events can be loaded at once. instead of individually.
"""

def setup_event_events(bot: commands.Bot, data: Dict[str, Dict[str, str]]) -> None:
    @bot.event
    async def on_ready():
        logging.info(f"Logged in as {bot.user.name} ({bot.user.id})")
        await bot.change_presence()
        logging.info(f"Starting background task for all guilds")
        for guild in bot.guilds:
            # Load Emoji ID Dictionary based on the guilds the bot is in
            if guild.name == "pub-server":
                emoji_id_mapping = data.get("public_server_emoji_dictionary")
                break
            elif guild.name == "priv-server":
                emoji_id_mapping = data.get("private_server_emoji_dictionary")
                break
        else:
            logging.info("Bot is not part of the expected servers with emoji dictionaries")
            emoji_id_mapping = {}
        
        check_events.start(bot)
        
    @bot.event
    async def on_scheduled_event_create(event: ScheduledEvent) -> None:
        logging.info(f"New scheduled event created: {event.name}")
        await notify_new_event(bot, event, event.guild_id)
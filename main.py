"""
This module contains the main class for the bot, which sets up the bot with intents, loads the contributors, emoji dicts, 
and posted events, loads the cogs, sets up commands and events for the bot, and then starts the bot.
"""

import discord
import os
import asyncio
from discord.ext import commands
from tasks.tasks import TaskManager
from utils.utils import Utils
from cogs.contributors import ContributorCommandsCog
from cogs.events import EventsCog
from cogs.help import HelpCommandCog
from cogs.gov import GovCommandsCog
from database.service import DatabaseService
from logger.logger import logger


class Bot:
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True  # Needed if your bot reads message content
        intents.guilds = True  # Needed for basic guild/server operations
        self.bot = commands.Bot(command_prefix="/", intents=intents)
        # Learn more about Discord gateways intents here: https://discord.com/developers/docs/events/gateway#gateway-intents

        db_service = DatabaseService()
        self.bot.ongoing_votes = db_service.get_ongoing_votes()

        @self.bot.event
        async def on_ready():
            logger.info(f"Logged in as {self.bot.user.name} ({self.bot.user.id})")
            await self.setup_cogs()
            await self.bot.tree.sync()
            await TaskManager.start_tasks(self.bot)

    async def setup_cogs(self):
        """Setup cogs after bot is ready"""
        try:
            await self.bot.add_cog(ContributorCommandsCog(self.bot))
            await self.bot.add_cog(EventsCog(self.bot))
            await self.bot.add_cog(GovCommandsCog(self.bot))
            logger.info("Cogs loaded successfully")
        except Exception as e:
            logger.error(f"Error loading cogs: {e}")
            raise

    async def main(self):
        try:
            discord_token = os.getenv("DISCORD_BOT_TOKEN")
            if not discord_token:
                raise ValueError("DISCORD_BOT_TOKEN environment variable is not set")
            await self.bot.start(discord_token)
        except Exception as e:
            logger.error(f"An error occurred in main: {e}")
            raise


if __name__ == "__main__":
    bot = Bot()
    asyncio.run(bot.main())

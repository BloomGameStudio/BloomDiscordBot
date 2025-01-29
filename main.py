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
        self.bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())
        # Initialize ongoing votes from database
        self.bot.ongoing_votes = Utils.get_ongoing_votes()
        
        # Register the on_ready event
        @self.bot.event
        async def on_ready():
            logger.info(f"Logged in as {self.bot.user.name} ({self.bot.user.id})")
            # Sync commands after bot is ready
            logger.info("Syncing commands with Discord...")
            await self.bot.tree.sync()
            logger.info("Commands synced successfully!")

    async def setup_hook(self):
        """Setup hook that runs when the bot starts"""
        logger.info("Setting up bot...")
        try:
            # Add cogs
            await self.bot.add_cog(ContributorCommandsCog(self.bot))
            await self.bot.add_cog(EventsCog(self.bot))
            await self.bot.add_cog(GovCommandsCog(self.bot))

        except Exception as e:
            logger.error(f"Error in setup_hook: {e}")
            raise

    async def main(self):
        try:
            # Run setup hook
            await self.setup_hook()

            # Start background tasks
            TaskManager.start_tasks(self.bot)

            # Run the bot
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

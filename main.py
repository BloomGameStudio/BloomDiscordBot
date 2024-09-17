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


class Bot:
    async def setup_background_tasks(self):
        TaskManager.check_events.start(self.bot)
        TaskManager.check_concluded_proposals_task.start(self.bot)

    async def main(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        intents.members = True
        self.bot = commands.Bot(command_prefix="", intents=intents)

        self.bot.ongoing_votes = Utils.load_ongoing_votes()
        self.bot.posted_events = Utils.load_posted_events()
        self.bot.notified_events = Utils.load_notified_events()
        self.contributors, self.emoji_dicts = Utils.load_contributors_and_emoji_dicts()

        await self.bot.add_cog(HelpCommandCog(self.bot))
        await self.bot.add_cog(
            ContributorCommandsCog(self.bot, self.contributors, self.emoji_dicts)
        )
        await self.bot.add_cog(GovCommandsCog(self.bot))
        await self.bot.add_cog(EventsCog(self.bot, self.contributors, self.emoji_dicts))

        await self.setup_background_tasks()

        await self.bot.start(os.getenv("DISCORD_BOT_TOKEN"))


if __name__ == "__main__":
    bot = Bot()
    asyncio.run(bot.main())

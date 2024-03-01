"""
This module contains the main class for the bot, which sets up the bot with intents, loads the contributors, emoji dicts, 
and posted events, loads the cogs, sets up commands and events for the bot, and then starts the bot.
"""

import discord
import os
import asyncio
import json
from discord.ext import commands
from events.events import setup_event_events
from helpers import load_posted_events, load_contributors_and_emoji_dicts
from cogs.help import HelpCommandCog
from cogs.contributors import ContributorCommandsCog
from cogs.events import EventCommandsCog
from cogs.help import HelpCommandCog
from cogs.gov import GovCommandsCog
from config.config import ONGOING_VOTES_FILE_PATH


class Bot:
    async def main(self):

        try:
            with open(ONGOING_VOTES_FILE_PATH, "r") as json_file:
                try:
                  self.ongoing_votes = json.load(json_file)
                except json.JSONDecodeError:
                    self.ongoing_votes = {}
        except FileNotFoundError:
            self.ongoing_votes = {}
        # Setup the bot with intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        intents.members = True
        self.bot = commands.Bot(command_prefix="", intents=intents)

        # Load the contributors, emoji dicts, and posted events
        self.bot.posted_events = load_posted_events()
        self.contributors, self.emoji_dicts = load_contributors_and_emoji_dicts()
        self.bot.ongoing_votes = self.ongoing_votes

        # Load the cogs
        await self.bot.add_cog(HelpCommandCog(self.bot))
        await self.bot.add_cog(
            ContributorCommandsCog(self.bot, self.contributors, self.emoji_dicts)
        )
        await self.bot.add_cog(GovCommandsCog(self.bot))
        await self.bot.add_cog(EventCommandsCog(self.bot))

        # Setup commands and events for the bot
        setup_event_events(self.bot)

        # Run the bot
        await self.bot.start(os.getenv("DISCORD_BOT_TOKEN"))


if __name__ == "__main__":
    bot = Bot()
    asyncio.run(bot.main())

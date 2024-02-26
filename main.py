import discord
import os
import json
import asyncio
from discord.ext import commands
from gov.commands import setup_gov_commands
from gov.proposals import proposals
from emotes.commands import setup_contributor_commands
from events.commands import setup_event_commands
from events.events import setup_event_events
from events.event_operations import load_posted_events
from config.config import CONTRIBUTORS_FILE_PATH
from shared.events import setup_shared_events
from logger.logger import logger


class Bot:
    async def main(self):
        # Load the contributor and dictionary data from the JSON file emotes/contributors.json
        with open(CONTRIBUTORS_FILE_PATH, "r") as json_file:
            self.data = json.load(json_file)
            self.contributors = {
                "Bloom Studio": self.data["servers"]["Bloom Studio"]["contributors"],
                "Bloom Collective": self.data["servers"]["Bloom Collective"][
                    "contributors"
                ],
            }
            self.emoji_dicts = {
                "Bloom Studio": self.data["servers"]["Bloom Studio"]["emoji_dictionary"],
                "Bloom Collective": self.data["servers"]["Bloom Collective"][
                    "emoji_dictionary"
                ],
            }

        # Setup the bot with intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        intents.members = True
        self.bot = commands.Bot(command_prefix="", intents=intents)

        # Setup commands and events for the bot
        setup_gov_commands(self.bot)
        setup_contributor_commands(self.bot, self.contributors, self.emoji_dicts)
        setup_shared_events(self.bot, self.data, proposals)
        self.bot.posted_events = load_posted_events()
        setup_event_commands(self.bot)
        setup_event_events(self.bot)

        # Perform tree synchronization
        try:
            await self.bot.tree.sync()
        except Exception as e:
            logger.error(e)

        # Run the bot
        await self.bot.start(os.getenv("DISCORD_BOT_TOKEN"))
       

if __name__ == "__main__":
    bot = Bot()
    asyncio.run(bot.main())
import discord
import os
import json
import asyncio
from discord.ext import commands
from proposals.proposals import proposals
from events.events import setup_event_events
from events.event_operations import load_posted_events
from config.config import CONTRIBUTORS_FILE_PATH

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
        self.bot.posted_events = load_posted_events()
        setup_event_events(self.bot, self.contributors, self.emoji_dicts, self.data, proposals)

        # Run the bot
        await self.bot.start(os.getenv("DISCORD_BOT_TOKEN"))
       

if __name__ == "__main__":
    bot = Bot()
    asyncio.run(bot.main())
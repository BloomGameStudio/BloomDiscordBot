import discord
import os
import json
from threading import Thread
from discord.ext import commands
#from gov.commands import setup_gov_commands
#from gov.proposals import proposals
#from emotes.commands import setup_contrbitutor_commands
#from events.commands import setup_event_commands
#from events.events import setup_event_events
#from events.event_operations import load_posted_events
#from shared.constants import CONTRIBUTORS_FILE_PATH, new_proposal_emoji
#from shared.events import setup_shared_events

from refactor.commands import CommandsCog
from refactor.shared_event_hooks import SharedEventHookCog

from refactor.api import init_db_api
from shared.constants import USE_API
from tortoise import Tortoise
import asyncio

async def main():
    # Discord Config
    intents = discord.Intents.default()

    intents.message_content = True

    # this one is fine.
    intents.reactions = True

    # Todo remove prefix entirely, this is deprecated, we need to only use slash commands.
    bot = commands.Bot(command_prefix=['..'], intents=intents)

    print("Setting up the commands, to register the commands and listen for them...")
    await bot.add_cog(CommandsCog(bot))

    print("Setting up the shared events to listen to messages, reactions and events...")
    await bot.add_cog(SharedEventHookCog(bot))

    print("Connecting to the database...")
    if USE_API:
        await init_db_api()
    else:
        await init_db()
    
    # TODO: Figure out what to use from this and what to axe from this.
    # Setup the governance discord commands, and events
    #setup_gov_commands(bot)
    # Setup the emotes discord commands, and events
    #setup_contrbitutor_commands(bot, contributors, emoji_id_mapping)
    # Setup the shared events
    #setup_shared_events(bot, contributors, emoji_id_mapping, proposals, new_proposal_emoji)
    #bot.posted_events = load_posted_events()
    # Setup the event discord commands, and events
    #setup_event_commands(bot)
    #setup_event_events(bot)

    print("Booting up the bot on a separate thread...")
    # Run the bot

    await bot.start("BOT_TOKEN")
    
    print("Bot should be good to go.")


async def init_db():
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={
            'models': [
                'domain.contributor',
                'domain.contributor_mention',
                'domain.proposal_vote',
                'domain.proposal',
                'domain.scheduled_event'
            ]
        }
    )

if __name__ == "__main__":
    asyncio.run(main())
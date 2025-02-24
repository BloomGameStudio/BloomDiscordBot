"""
Script to reconstruct and save a missing ongoing vote entry in the database using a thread ID.
"""

import asyncio
import discord
from discord.ext import commands
import time
from typing import Optional

import consts.constants as constants
import config.config as cfg
from database.service import DatabaseService
from logger.logger import logger
from proposals.thread_parser import ThreadParser


class VoteReconstructor:
    def __init__(self, bot_token: str):
        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = commands.Bot(command_prefix="!", intents=intents)
        self.token = bot_token

        @self.bot.event
        async def on_ready():
            logger.info(f"Bot is ready as {self.bot.user}")
            if not hasattr(self.bot, "reconstruct_task"):
                return
            try:
                await self.bot.reconstruct_task
            finally:
                await self.bot.close()

    async def find_vote_message(
        self, thread: discord.Thread
    ) -> Optional[discord.Message]:
        """Find the vote message in the thread by looking for the characteristic vote format"""
        async for message in thread.history():
            if all(
                emoji in message.content
                for emoji in [
                    constants.YES_VOTE,
                    constants.NO_VOTE,
                    constants.ABSTAIN_VOTE,
                ]
            ):
                return message
        return None

    async def reconstruct_vote(
        self, thread_id: str, end_time: Optional[int] = None
    ) -> bool:
        """Reconstruct and save the ongoing vote data for a given thread ID"""
        try:
            reconstruction_task = self._reconstruct_vote(thread_id, end_time)
            self.bot.reconstruct_task = reconstruction_task

            # Start the bot and wait for the reconstruction to complete
            async with self.bot:
                result = await asyncio.gather(
                    self.bot.start(self.token), reconstruction_task
                )
                return result[1]  # Return the result of _reconstruct_vote
        except Exception as e:
            logger.error(f"Error in reconstruct_vote: {e}")
            return False

    async def _reconstruct_vote(
        self, thread_id: str, end_time: Optional[int] = None
    ) -> bool:
        """Internal method to perform the reconstruction after bot is ready"""
        try:
            logger.info("Parsing thread...")

            # Parse the thread content
            thread_data, error = await ThreadParser.parse_thread(self.bot, thread_id)
            if error:
                logger.error(f"Error parsing thread: {error}")
                return False

            # Get the thread object
            thread = await self.bot.fetch_channel(int(thread_id))
            if not isinstance(thread, discord.Thread):
                logger.error("Provided ID is not a thread")
                return False

            # Find the vote message
            vote_message = await self.find_vote_message(thread)
            if not vote_message:
                logger.error("Could not find vote message in thread")
                return False

            # Use provided end_time or default to new 48h window
            if end_time is None:
                end_time = int(time.time() + cfg.DISCORD_VOTE_ENDTIME)

            # Reconstruct the proposal data
            proposal_data = {
                "draft": {
                    "member_id": str(thread.owner_id),
                    "title": thread_data["title"],
                    "type": thread_data["type"],
                    "sections": thread_data["sections"],
                },
                "end_time": end_time,
                "title": thread.name,
                "channel_id": str(thread.parent_id),
                "thread_id": str(thread.id),
                "message_id": str(vote_message.id),
                "proposal_id": str(thread.id),
            }

            # Print reconstructed proposal data
            logger.info("Reconstructed proposal data:")
            logger.info(f"Proposal ID: {proposal_data['proposal_id']}")
            logger.info(f"Title: {proposal_data['title']}")
            logger.info(f"Type: {proposal_data['draft']['type']}")
            logger.info(f"Member ID: {proposal_data['draft']['member_id']}")
            logger.info(f"End Time: {proposal_data['end_time']}")
            logger.info(f"Channel ID: {proposal_data['channel_id']}")
            logger.info(f"Thread ID: {proposal_data['thread_id']}")
            logger.info(f"Message ID: {proposal_data['message_id']}")

            # Save to database
            db_service = DatabaseService()
            db_service.save_ongoing_vote(proposal_data)

            logger.info(f"Successfully reconstructed vote for thread {thread_id}")
            return True

        except Exception as e:
            logger.error(f"Error reconstructing vote: {e}")
            return False
        finally:
            await self.bot.close()


def main():
    """Main function to run the script"""
    thread_id = input("Enter the thread ID to reconstruct: ")
    bot_token = input("Enter your bot token: ")  # Or load from config
    end_time_input = input(
        "Enter end time (Unix timestamp) or press Enter for default 48h window: "
    )

    end_time = int(end_time_input) if end_time_input else None

    bot = VoteReconstructor(bot_token)
    success = asyncio.run(bot.reconstruct_vote(thread_id, end_time))

    if success:
        print("Vote reconstruction completed successfully!")
    else:
        print("Failed to reconstruct vote.")


if __name__ == "__main__":
    main()

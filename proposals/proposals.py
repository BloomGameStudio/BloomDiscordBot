"""
The ProposalManager class handles the logic associated with proposals. These functions are invoked when the commands
in cogs/gov.py are invoked and the relevant buttons or selects are clicked.

The module contains the following functions:
- "handle_votedraft": Handles the vote draft command.
- "handle_publish_draft": Handles the publish draft command.
- "prepare_draft": Prepare the draft by setting the type, channel ID, and title based on the draft type.
- "publish_draft": Publish the draft by creating a thread with the prepared content and starting a vote timer.
- "react_to_vote": React to the published draft with the vote emojis.

The module also contains the following variables:
- proposals: A list of proposals.
- ongoing_votes: A dictionary of ongoing votes.
"""

import time
import discord
import consts.constants as constants
import config.config as cfg
from logger.logger import logger
from discord.ext import commands
from consts.types import GOVERNANCE_ID_TYPE, BUDGET_ID_TYPE
from typing import Any, Dict, List, Tuple
from utils.utils import Utils
import re
from database.service import DatabaseService


class ProposalManager:
    proposals: List[Dict[str, Any]] = []

    @staticmethod
    async def prepare_draft(
        guild: discord.Guild, draft: Dict[str, Any]
    ) -> Tuple[str, str, str]:
        """
        Prepare the draft by setting the type, channel ID, and title based on the draft type.
        This version uses a temporarily incremented ID for the title generation but does not update the config file.

        Parameters:
        guild (discord.Guild): The guild instance.
        draft (Dict[str, Any]): The draft to prepare.

        Returns:
        Tuple[str, str, str]: A tuple containing the ID type, channel name, and title.
        """
        draft_type = draft["type"].lower()
        if draft_type not in [BUDGET_ID_TYPE, GOVERNANCE_ID_TYPE]:
            raise ValueError(f"Invalid draft type: {draft_type}")

        if draft_type == BUDGET_ID_TYPE:
            id_type = BUDGET_ID_TYPE
            channel_name = constants.GOVERNANCE_BUDGET_CHANNEL
            title = f"Bloom Budget Proposal: {draft['title']}"
        else:
            id_type = GOVERNANCE_ID_TYPE
            channel_name = constants.GOVERNANCE_CHANNEL
            title = f"Bloom General Proposal: {draft['title']}"

        return id_type, channel_name, title

    @staticmethod
    async def get_forum_channel(
        draft_type: str, bot: commands.Bot, guild_id: int
    ) -> discord.ForumChannel:
        """Get the appropriate forum channel based on draft type"""
        guild = bot.get_guild(guild_id)
        if not guild:
            logger.error(f"Guild not found: {guild_id}")
            return None

        channel_name = (
            constants.GOVERNANCE_BUDGET_CHANNEL
            if draft_type.lower() == "budget"
            else constants.GOVERNANCE_CHANNEL
        )

        channel = discord.utils.get(guild.channels, name=channel_name)
        if not isinstance(channel, discord.ForumChannel):
            logger.error(f"Channel not found or not a forum channel: {channel_name}")
            return None

        return channel

    @staticmethod
    async def publish_draft(
        draft: Dict[str, Any], bot: commands.Bot, guild_id: int, guild: discord.Guild
    ) -> bool:
        """Publish the draft by creating a thread with the prepared content and starting a vote timer."""
        created_thread = None
        try:
            forum_channel = await ProposalManager.get_forum_channel(
                draft["type"], bot, guild_id
            )
            if not forum_channel:
                return False

            proposal_type = "General" if draft["type"] == "governance" else "Budget"
            thread_title = draft["title"]
            formatted_title = f"Bloom {proposal_type} Proposal: {thread_title}"

            content = draft.get("sections", {}).get("content", "No content")

            # Split content into sentences
            sentences = re.split(r"([.!?]\s+)", content)
            # Recombine sentences with their punctuation
            sentences = [
                "".join(i) for i in zip(sentences[0::2], sentences[1::2] + [""])
            ]

            current_message = ""
            messages = []

            for sentence in sentences:
                # If adding this sentence would exceed Discord's limit
                if len(current_message) + len(sentence) > 1900:
                    messages.append(current_message.strip())
                    current_message = sentence
                else:
                    current_message += sentence

            if current_message:
                messages.append(current_message.strip())

            # Create thread with first message
            created_thread = await forum_channel.create_thread(
                name=formatted_title, content=messages[0]
            )

            # Post remaining messages as replies
            for message in messages[1:]:
                await created_thread.message.reply(message)

            # Add voting options
            vote_message = await created_thread.message.reply(
                f"**{constants.YES_VOTE} Adopt**\n\n**{constants.NO_VOTE} Reassess**\n\n**{constants.ABSTAIN_VOTE} Abstain**\n\nVote will conclude in 48h from now."
            )

            # Rest of the function (proposal data storage, etc)
            proposal_id = str(created_thread.message.id)
            proposal_data = {
                "draft": draft,
                "end_time": time.time() + cfg.DISCORD_VOTE_ENDTIME,
                "title": formatted_title,
                "channel_id": str(forum_channel.id),
                "thread_id": str(created_thread.thread.id),
                "message_id": str(vote_message.id),
            }

            if not hasattr(bot, "ongoing_votes"):
                bot.ongoing_votes = {}
            bot.ongoing_votes[proposal_id] = proposal_data

            # Save to database
            db_service = DatabaseService()
            proposal_data["proposal_id"] = proposal_id
            db_service.save_ongoing_vote(proposal_data)

            await ProposalManager.react_to_vote(
                vote_message.id,
                bot,
                guild_id,
                forum_channel.name,
                created_thread.thread.id,
            )
            return True

        except Exception as e:
            logger.error(f"Error publishing draft: {e}")
            if created_thread:
                try:
                    await created_thread.thread.delete()
                except Exception as delete_error:
                    logger.error(f"Error cleaning up failed thread: {delete_error}")
            return False

    @staticmethod
    async def react_to_vote(
        message_id: int,
        bot: commands.Bot,
        guild_id: int,
        channel_name: str,
        thread_id: int,
    ) -> None:
        """
        Add reaction emojis for voting on a message.
        """
        guild = bot.get_guild(guild_id)
        if not guild:
            logger.error(f"Error: Guild with id {guild_id} not found.")
            return

        channel = discord.utils.get(guild.channels, name=channel_name)
        if not channel:
            logger.error(f"Error: Channel with name {channel_name} not found.")
            return

        thread = discord.utils.get(channel.threads, id=thread_id)
        if not thread:
            logger.error(f"Error: Thread with id {thread_id} not found.")
            return

        message = await thread.fetch_message(message_id)

        await message.add_reaction(constants.YES_VOTE)
        await message.add_reaction(constants.NO_VOTE)
        await message.add_reaction(constants.ABSTAIN_VOTE)

    def create_ongoing_vote_data(
        self, message_id: str, channel_id: str, thread_id: str
    ) -> dict:
        """Create ongoing vote data for storage"""
        return {
            "draft": self.draft,
            "end_time": self.end_time,
            "title": self.title,
            "channel_id": channel_id,
            "thread_id": thread_id,
            "message_id": message_id,
        }

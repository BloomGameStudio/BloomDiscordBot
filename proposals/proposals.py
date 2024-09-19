"""
The ProposalManager class handles the logic associated with proposals. These functions are invoked when the gov commands
in cogs/gov.py are invoked and the relevant buttons or selects are clicked.

The module contains the following functions:
- handle_votedraft: Handles the vote draft command.
- handle_publish_draft: Handles the publish draft command.
- prepare_draft: Prepare the draft by setting the type, channel ID, and title based on the draft type.
- publish_draft: Publish the draft by creating a thread with the prepared content and starting a vote timer.
- react_to_vote: React to the published draft with the vote emojis.
- vote_timer: Start a timer for the vote. After 48 hours, the vote is concluded and the result is posted.

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


class ProposalManager:
    proposals: List[Dict[str, Any]] = []

    @staticmethod
    async def handle_publish_draft(
        interaction: discord.Interaction,
        draft_name: str,
        proposals: List[Dict[str, str]],
        bot: commands.Bot,
    ) -> None:
        """
        Handle the publish draft command by publishing the draft if it exists in the proposals list.

        Parameters:
        interaction (discord.Interaction): The interaction of the command invocation.
        draft_name (str): The name of the draft to publish.
        proposals (List[Dict[str, str]]): The list of proposals.
        bot (commands.Bot): The bot instance.
        """
        if not interaction.response.is_done():
            await interaction.response.defer()

        draft_to_publish = next(
            (
                item
                for item in proposals
                if item.get("title", "").strip() == draft_name.strip()
            ),
            None,
        )

        if draft_to_publish:
            published_successfully = await ProposalManager.publish_draft(
                draft_to_publish, bot, interaction.guild.id, interaction.guild
            )
            if published_successfully:
                proposals.remove(draft_to_publish)
                embed = discord.Embed(
                    title=f"Published Draft: {draft_to_publish['title']}",
                    description=f"The draft '{draft_to_publish['title']}' has been published.",
                    color=discord.Color.green(),
                )
                embed.set_author(
                    name="Draft Publishing",
                    icon_url=interaction.user.display_avatar.url,
                )
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(
                    f"Failed to publish draft: {draft_name}"
                )
        else:
            await interaction.followup.send(f"Draft not found: {draft_name}")

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
    async def publish_draft(
        draft: Dict[str, Any], bot: commands.Bot, guild_id: int, guild: discord.Guild
    ) -> bool:
        """
        Publish the draft by creating a thread with the prepared content and starting a vote timer.
        Returns a boolean indicating whether the publication was successful.

        Parameters:
        draft (Dict[str, Any]): The draft to publish.
        bot (commands.Bot): The bot instance.
        guild_id (int): The ID of the guild.
        guild (discord.Guild): The guild instance.

        Returns:
        bool: A boolean indicating whether the publication was successful.
        """
        try:
            id_type, channel_name, title = await ProposalManager.prepare_draft(
                guild, draft
            )
            forum_channel = discord.utils.get(
                bot.get_guild(guild_id).channels, name=channel_name
            )
            if not forum_channel:
                logger.error(f"Error: Forum Channel {channel_name} not found.")
                return False

            thread = await forum_channel.create_thread(
                name=title, content=f"{draft['abstract']}"
            )
            await thread.message.reply(f"\n{draft['background']}")
            if "additional" in draft and draft["additional"].strip():
                await thread.message.reply(f"\n{draft['additional']}")

            vote_message = await thread.message.reply(
                f"**{constants.YES_VOTE} Adopt**\n\n**{constants.NO_VOTE} Reassess**\n\n**{constants.ABSTAIN_VOTE} Abstain**\n\nVote will conclude in 48h from now."
            )

            proposal_id = str(thread.message.id)
            proposal_data = {
                "draft": draft,
                "end_time": time.time() + cfg.DISCORD_VOTE_ENDTIME,
                "yes_count": 0,
                "title": title,
                "channel_id": str(forum_channel.id),
                "thread_id": str(thread.thread.id),
                "message_id": str(vote_message.id),
            }

            if not hasattr(bot, "ongoing_votes"):
                bot.ongoing_votes = {}
            bot.ongoing_votes[proposal_id] = proposal_data

            Utils.update_ongoing_votes_file(
                bot.ongoing_votes, cfg.ONGOING_VOTES_FILE_PATH
            )

            await ProposalManager.react_to_vote(
                vote_message.id, bot, guild_id, channel_name, thread.thread.id
            )
            return True

        except Exception as e:
            logger.error(f"Error publishing draft: {str(e)}")
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

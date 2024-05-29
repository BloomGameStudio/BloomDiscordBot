"""
Proposals module handles the logic associated with proposals. These functions are invoked when the gov commands
in cogs/gov.py are invoked and the relevant buttons or selects are clicked.

The module contains the following functions:
- handle_votedraft: Handles the vote draft command.
- handle_publishdraft: Handles the publish draft command.
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
from discord.ext.commands import Bot
from discord.ext import commands
from consts.types import GOVERNANCE_ID_TYPE, BUDGET_ID_TYPE
from logger.logger import logger
from typing import Any, Dict, List, Tuple
from helpers.helpers import get_channel_by_name, update_ongoing_votes_file


proposals: List[Dict[str, Any]] = []


async def handle_publishdraft(
    interaction: discord.Interaction,
    draft_name: str,
    proposals: List[Dict[str, str]],
    bot: commands.Bot,
) -> None:
    """
    Handle the publish draft command by publishing the draft if it exists in the proposals list.

    Parameters:
    interaction (discord.Interaction): The interaction object.
    draft_name (str): The name of the draft to be published.
    proposals (List[Dict[str, str]]): The list of proposals.
    bot (commands.Bot): The bot instance.

    Returns:
    None
    """
    # Defer the response if it might take some time to process
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
        published_successfully = await publish_draft(
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
                name="Draft Publishing", icon_url=interaction.user.display_avatar.url
            )
            await interaction.followup.send(embed=embed)  # Use followup if deferred
        else:
            await interaction.followup.send(f"Failed to publish draft: {draft_name}")
    else:
        await interaction.followup.send(f"Draft not found: {draft_name}")


# prepare the draft by setting the type, channel ID, and title based on the draft type
async def prepare_draft(
    guild: discord.Guild, draft: Dict[str, Any]
) -> Tuple[str, str, str]:
    """
    Prepare the draft by setting the type, channel ID, and title based on the draft type.
    This version uses a temporarily incremented ID for the title generation but does not update the config file.

    Parameters:
    guild (discord.Guild): The guild to search for the channel in.
    draft (Dict[str, Any]): The draft to be prepared.

    Returns:
    Tuple[str, str, str]: The ID type, channel name, and title of the draft.
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


# publish the draft by creating a thread with the prepared content and starting a vote timer
async def publish_draft(
    draft: Dict[str, Any], bot: Bot, guild_id: int, guild: discord.Guild
) -> bool:
    """
    Publish the draft by creating a thread with the prepared content and starting a vote timer.
    Returns a boolean indicating whether the publication was successful.

    Parameters:
    draft (Dict[str, Any]): The draft to be published.
    bot (Bot): The bot instance.
    guild_id (int): The ID of the guild.
    guild (discord.Guild): The guild to publish the draft in.

    Returns:
    bool: True if successfully published, False otherwise.
    """
    try:
        id_type, channel_name, title = await prepare_draft(guild, draft)
        forum_channel = discord.utils.get(
            bot.get_guild(guild_id).channels, name=channel_name
        )
        if not forum_channel:
            logger.error(
                f"Error: Unable to publish draft, Forum Channel not found. Please verify a channel exists with the name {channel_name} and it aligns with shared/constants.py"
            )
            return False

        thread = await forum_channel.create_thread(
            name=title, content=f"{draft['abstract']}"
        )

        # Post additional information and start the vote
        await thread.message.reply(f"\n{draft['background']}")
        if "additional" in draft and draft["additional"].strip():
            await thread.message.reply(f"\n{draft['additional']}")

        vote_message = await thread.message.reply(
            f"**{constants.YES_VOTE} Adopt**\n\n**{constants.NO_VOTE} Reassess**\n\n**{constants.ABSTAIN_VOTE} Abstain**\n\nVote will conclude in 48h from now."
        )

        proposal_id = str(thread.message.id)
        proposal_data = {
            "draft": draft,
            "end_time": time.time() + 48 * 60 * 60,  # 48 hours from now
            "yes_count": 0,
            "title": title,
            "channel_id": str(forum_channel.id),
            "thread_id": str(thread.thread.id),  # Add the thread ID
            "message_id": str(vote_message.id),  # Add the message ID
        }

        # Update ongoing_votes with new proposal data
        if not hasattr(bot, "ongoing_votes"):
            bot.ongoing_votes = {}  # In case ongoing_votes is not initialized
        bot.ongoing_votes[proposal_id] = proposal_data

        # Save to ongoing_votes.json
        update_ongoing_votes_file(bot.ongoing_votes, cfg.ONGOING_VOTES_FILE_PATH)

        await react_to_vote(
            vote_message.id, bot, guild_id, channel_name, thread.thread.id
        )
        return True

    except Exception as e:
        logger.error(f"Error publishing draft: {str(e)}")
        return False


async def react_to_vote(
    message_id: int, bot: Bot, guild_id: int, channel_name: str, thread_id: int
) -> None:
    guild = bot.get_guild(guild_id)
    if not guild:
        logger.error(f"Error: Guild with id {guild_id} not found.")
        return

    # Fetch the channel by name
    channel = discord.utils.get(guild.channels, name=channel_name)
    if not channel:
        logger.error(f"Error: Channel with name {channel_name} not found.")
        return

    # Fetch the thread from the channel
    thread = discord.utils.get(channel.threads, id=thread_id)
    if not thread:
        logger.error(f"Error: Thread with id {thread_id} not found.")
        return

    # Fetch the message using the message ID
    message = await thread.fetch_message(message_id)

    await message.add_reaction(constants.YES_VOTE)
    await message.add_reaction(constants.NO_VOTE)
    await message.add_reaction(constants.ABSTAIN_VOTE)

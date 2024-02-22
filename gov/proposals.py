"""
gov/proposals.py is responsible for handling the publishing of proposals.

Proposals are tracked through a timer, and if the posted proposal passes the sniff test (quorum of yes reacts)
they are published to snapshot through a node.js script.

Refer to snapshot for more information on how the snapshot is created.
"""

import json
import subprocess
import textwrap
import config.config as cfg
import discord
import time
from typing import Dict, Any, List, Tuple
from discord.ext.commands import Bot
from consts.constants import (
    GOVERNANCE_BUDGET_CHANNEL,
    GOVERNANCE_CHANNEL,
    YES_VOTE,
    NO_VOTE,
    ABSTAIN_VOTE,
)
from consts.types import GOVERNANCE_ID_TYPE, BUDGET_ID_TYPE
from logger.logger import logger
from config.config import ONGOING_VOTES_FILE_PATH

proposals: List[Dict[str, Any]] = []

def update_ongoing_votes_file(data, file_path):
    """
    Update ongoing_votes.json with the new data.

    Parameters:
    data (Dict): The data to update the ongoing_votes with.
    file_path (str): The file path to ongoing_votes.json.
    """
    # Write the updated data to the file
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)

async def check_ongoing_proposals(bot):
    """
    This function checks ongoing proposals and processes them if they have ended.
    It iterates over all ongoing votes, checks if the current time is past the end time of the vote,
    and if so, processes the vote. The processing includes running a snapshot creation function,
    posting a result message, and removing the concluded vote from ongoing_proposals.

    Parameters:
    bot (commands.Bot): The bot instance, which contains the ongoing_votes attribute.

    Returns:
    None
    """
    logger.info("Checking to see if proposals have ended")
    try:
        keys_to_remove = []  # Initialize list to store keys for removal
        for proposal_id, proposal_data in bot.ongoing_votes.items():
            current_time = time.time()
            end_time = proposal_data["end_time"]
            if current_time >= end_time:
                # Retrieve the channel by the channel_id stored in the ongoing votes
                channel_id = int(proposal_data["channel_id"])
                channel = bot.get_channel(channel_id)

                if channel:
                    # Use proposal_id as int to retrieve the thread
                    thread_id = int(proposal_id)
                    thread = channel.get_thread(thread_id)
                    if thread:
                        message = await thread.fetch_message(thread_id)

                        # Update the Yes/No/Abstain counts from message reactions
                        for reaction in message.reactions:
                            if str(reaction.emoji) == f"{YES_VOTE}":
                                proposal_data["yes_count"] = reaction.count - 1  # Subtract the bot's reaction
                            elif str(reaction.emoji) == f"{NO_VOTE}":
                                proposal_data["no_count"] = reaction.count - 1
                            elif str(reaction.emoji) == f"{ABSTAIN_VOTE}":
                                proposal_data["abstain_count"] = reaction.count - 1

                        # Process the concluded vote
                        if proposal_data["yes_count"] >= 1:  # Set to quorum needed
                            # Call the snapshot creation function
                            subprocess.run([
                                "node",
                                "./snapshot/wrapper.js",
                                proposal_data["title"],
                                proposal_data["draft"]["abstract"],
                                proposal_data["draft"]["background"],
                                "Yes",
                                "No",
                                "Abstain",
                            ], check=True)

                        logger.info("Yes vote count: " + str(proposal_data["yes_count"]) + " No vote count: " + str(proposal_data["no_count"]) + " Abstain vote count: " + str(proposal_data["abstain_count"]))

                        # Post the result message to the corresponding thread
                        result_message = f"The vote for '{proposal_data['title']}' has passed!" if proposal_data["yes_count"] >= 1 else f"The vote for '{proposal_data['title']}' has failed."
                        await thread.send(result_message)  # Send the result message to the corresponding thread

                        keys_to_remove.append(proposal_id)  # Add the key for removal
                    else:
                        logger.error(f"Unable to find the thread with id: {thread_id} in the channel: {channel.name}")
                else:
                    logger.error(f"Unable to find the channel with id: {channel_id}")

        # Remove the concluded vote from ongoing_proposals after the iteration
        for key in keys_to_remove:
            del bot.ongoing_votes[key]

        # Save to ongoing_votes.json
        update_ongoing_votes_file(bot.ongoing_votes, ONGOING_VOTES_FILE_PATH)

    except Exception as e:
        logger.error(f"An error occurred while checking ongoing proposals: {e}")

async def prepare_draft(
    guild: discord.Guild, draft: Dict[str, Any]
) -> Tuple[str, str, str]:
    """
    Prepare the draft by setting the type, channel ID, and title based on the draft type.
    Increment the current ID and update the config file.

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
        channel_name = GOVERNANCE_BUDGET_CHANNEL
        cfg.current_budget_id += 1
        cfg.update_id_values(
            cfg.current_budget_id, id_type
        )  # Update the governance ID in the config file
        title = (
            f"Bloom Budget Proposal (BBP) #{cfg.current_budget_id}: {draft['title']}"
        )
    else:
        id_type = GOVERNANCE_ID_TYPE
        channel_name = GOVERNANCE_CHANNEL
        cfg.current_governance_id += 1
        cfg.update_id_values(
            cfg.current_governance_id, id_type
        )  # Update the governance ID in the config file
        title = f"Bloom Governance Proposal (BGP) #{cfg.current_governance_id}: {draft['title']}"

    return id_type, channel_name, title


# publish the draft by creating a thread with the prepared content and starting a vote timer
async def publish_draft(
    draft: Dict[str, Any], bot: Bot, guild_id: int, guild: discord.Guild
):
    """
    Publish the draft by creating a thread with the prepared content and starting a vote timer.

    Parameters:
    draft (Dict[str, Any]): The draft to be published.
    bot (commands.Bot): The bot instance.
    guild_id (int): The ID of the guild where the draft will be published.
    guild (discord.Guild): The guild object.
    """
    id_type, channel_name, title = await prepare_draft(guild, draft)
    forum_channel = discord.utils.get(bot.get_guild(guild_id).channels, name=channel_name)
    if not forum_channel:
        logger.error(
            f"Error: Unable to publish draft, Forum Channel not found. Please verify a channel exists with the name {channel_name} and it aligns with shared/constants.py"
        )
        return

    # Store the content in a variable
    content = textwrap.dedent(
        f"""
    **{title}**

    __**Abstract**__
    {draft["abstract"]}

    **__Background__**
    {draft["background"]}

    **{YES_VOTE} Yes**

    **{NO_VOTE} Reassess**

    **{ABSTAIN_VOTE} Abstain**

    Vote will conclude in 48h from now.
    """
    )
    thread_with_message = await forum_channel.create_thread(name=title, content=content)

    proposal_id = str(thread_with_message.thread.id)
    proposal_data = {
        "draft": draft,
        "end_time": time.time() + 1 * 60,  # Calculate end time for 1 minute (for testing)
        "yes_count": 0,
        "title": title,
        "channel_id": str(forum_channel.id)
    }

    # Update ongoing_votes with new proposal data
    if not hasattr(bot, 'ongoing_votes'):
        bot.ongoing_votes = {}  # In case ongoing_votes is not initialized
    bot.ongoing_votes[proposal_id] = proposal_data

    # Save to ongoing_votes.json
    update_ongoing_votes_file(bot.ongoing_votes, ONGOING_VOTES_FILE_PATH)

    await react_to_vote(thread_with_message.thread.id, bot, guild_id, channel_name)

async def react_to_vote(
    thread_id: int, bot: Bot, guild_id: int, channel_name: str
) -> None:
    """
    React to the published draft with the vote emojis.
    This function is called when a draft is published.
    This will ensure that when a draft is published, the vote emojis are added to the thread.

    Parameters:
    thread_id (int): The ID of the thread where the vote is taking place.
    bot (Bot): The bot instance.
    guild_id (int): The ID of the guild where the vote is taking place.
    channel_name (str): The name of the channel where the vote is taking place.
    """
    guild = bot.get_guild(guild_id)
    if not guild:
        logger.error(f"Error: Guild with id {guild_id} not found.")
        return

    # Fetch the channel by name
    channel = discord.utils.get(guild.channels, name=channel_name)
    thread = channel.get_thread(thread_id)

    # Fetch the initial message in the thread using the thread ID
    message = await thread.fetch_message(thread_id)

    await message.add_reaction(YES_VOTE)
    await message.add_reaction(NO_VOTE)
    await message.add_reaction(ABSTAIN_VOTE)
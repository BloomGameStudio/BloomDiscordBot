import asyncio
import subprocess
import textwrap
import config.config as cfg
import discord
from typing import Dict, Any, List, Tuple
from discord.ext.commands import Bot
from shared.constants import GOVERNANCE_BUDGET_CHANNEL, GOVERNANCE_CHANNEL
from consts.types import GOVERNANCE_ID_TYPE, BUDGET_ID_TYPE
from logger.logger import logger

proposals: List[Dict[str, Any]] = []

ongoing_votes: Dict[int, Dict[str, Any]] = {}

"""
gov/proposals.py is responsible for handling the publishing of proposals.

Proposals are tracked through a timer, and if the posted proposal passes the sniff test (quorum of yes reacts)
they are published to snapshot through a node.js script.

Refer to snapshot for more information on how the snapshot is created.
"""


# prepare the draft by setting the type, channel ID, and title based on the draft type
async def prepare_draft(draft: Dict[str, Any]) -> Tuple[str, str, str]:
    """
    Prepare the draft by setting the type, channel ID, and title based on the draft type.
    Increment the current ID and update the config file.

    Parameters:
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
        title = f"Bloom Budget Proposal (BBP) #{cfg.current_budget_id}: {draft['name']}"
    else:
        id_type = GOVERNANCE_ID_TYPE
        channel_name = GOVERNANCE_CHANNEL
        cfg.current_governance_id += 1
        cfg.update_id_values(
            cfg.current_governance_id, id_type
        )  # Update the governance ID in the config file
        title = f"Bloom Governance Proposal (BGP) #{cfg.current_governance_id}: {draft['name']}"

    return id_type, channel_name, title


# publish the draft by creating a thread with the prepared content and starting a vote timer
async def publish_draft(draft: Dict[str, Any], bot: Bot, guild_id: int) -> None:
    """
    Publish the draft by creating a thread with the prepared content and starting a vote timer.

    Parameters:
    draft (Dict[str, Any]): The draft to be published.
    bot (Bot): The bot instance.
    guild_id (int): The ID of the guild where the draft will be published.
    """
    id_type, channel_name, title = await prepare_draft(draft)

    forum_channel = discord.utils.get(
        bot.get_guild(guild_id).channels, name=channel_name
    )
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

    **👍 Yes**

    **👎 Reassess**

    **❌ Abstain**

    Vote will conclude in 48h from now.
    """
    )

    thread_with_message = await forum_channel.create_thread(name=title, content=content)

    ongoing_votes[thread_with_message.thread.id] = {
        "draft": draft,  # Store the draft info
        "yes_count": 0,  # Initialize counts
        "reassess_count": 0,
        "abstain_count": 0,
    }

    await vote_timer(
        thread_with_message.thread.id, bot, guild_id, channel_name, title, draft
    )


async def vote_timer(
    thread_id: int,
    bot: Bot,
    guild_id: int,
    channel_name: str,
    title: str,
    draft: Dict[str, Any],
) -> None:
    """
    NOTE: This should be changed as a long sleep time is unideal, IE if the bot is restarted while sleeping.

    Start a timer for the vote. After 48 hours, the vote is concluded and the result is posted.

    Parameters:
    thread_id (int): The ID of the thread where the vote is taking place.
    bot (Bot): The bot instance.
    guild_id (int): The ID of the guild where the vote is taking place.
    channel_name (str): The name of the channel where the vote is taking place.
    title (str): The title of the vote.
    draft (Dict[str, Any]): The draft that is being voted on.
    """
    # Sleep until the vote ends
    await asyncio.sleep(48 * 3600)

    # Fetch the guild using the guild_id
    guild = bot.get_guild(guild_id)
    if not guild:
        print(f"Error: Guild with id {guild_id} not found.")
        return

    # Fetch the channel by name
    channel = discord.utils.get(guild.channels, name=channel_name)
    thread = channel.get_thread(thread_id)

    # Fetch the initial message in the thread using the thread ID
    message = await thread.fetch_message(thread_id)

    for reaction in message.reactions:
        if str(reaction.emoji) == "👍":
            ongoing_votes[message.id]["yes_count"] = reaction.count
        elif str(reaction.emoji) == "👎":
            ongoing_votes[message.id]["reassess_count"] = reaction.count
        elif str(reaction.emoji) == "❌":
            ongoing_votes[message.id]["abstain_count"] = reaction.count

    # Check the result and post it
    result_message = f"Vote for '{title}' has concluded:\n\n"

    if ongoing_votes[message.id]["yes_count"] >= 5:  # Set to quorum needed
        result_message += (
            "The vote passes! :tada:, snapshot proposal will now be created"
        )
        # Call the snapshot creation function
        subprocess.run(
            [
                "node",
                "./snapshot/wrapper.js",
                title,
                draft["abstract"],
                draft["background"],
                "Yes",
                "No",
                "Abstain",
            ],
            check=True,
        )
    else:
        result_message += "The vote fails. :disappointed:"

    result_message += f"\n\nYes: {ongoing_votes[message.id]['yes_count']}\nReassess: {ongoing_votes[message.id]['reassess_count']}\nAbstain: {ongoing_votes[message.id]['abstain_count']}"

    await bot.get_channel(thread_id).send(result_message)

    # Remove the vote from ongoing_votes
    del ongoing_votes[message.id]

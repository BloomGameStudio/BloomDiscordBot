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

import asyncio
import subprocess
import textwrap
import discord
import consts.constants as constants
import config.config as cfg
from logger.logger import logger
from discord.ext.commands import Bot
from discord.ext import commands
from consts.types import GOVERNANCE_ID_TYPE, BUDGET_ID_TYPE
from logger.logger import logger
from typing import Any, Dict, List, Tuple
from helpers import get_channel_by_name


proposals: List[Dict[str, Any]] = []

ongoing_votes: Dict[int, Dict[str, Any]] = {}


async def handle_votedraft(
    ctx: commands.Context, proposals: List[Dict[str, str]], new_proposal_emoji: str
) -> None:
    """
    Handles the vote draft command. This command allows users to draft a proposal.

    Parameters:
    ctx (commands.Context): The context in which the command was called.
    proposals (List[Dict[str, str]]): The list of proposals.
    new_proposal_emoji (str): The emoji for new proposals.
    """
    try:
        # Get the channel with the name 'governance' in the server
        governance_talk_channel = get_channel_by_name(
            ctx.guild, constants.GOVERNANCE_TALK_CHANNEL
        )
    except ValueError as e:
        await ctx.send(f"Cannot find governance channel in this server.")
        logger.error(f"Error drafting a vote: {str(e)}")
        return

    if ctx.channel.id != governance_talk_channel.id:
        await ctx.send(
            f"This command can only be used in <#{governance_talk_channel.id}>"
        )
        return


async def handle_publishdraft(
    interaction: discord.Interaction,
    draft_name: str,
    proposals: List[Dict[str, str]],
    bot: commands.Bot,
) -> None:
    """
    Handle the publishing of a draft.

    This function searches for a draft with the given name in the list of proposals.
    If the draft is found, it is published and removed from the list of proposals.
    If the draft is not found, a message is sent to the interaction.

    Parameters:
    interaction (discord.Interaction): The interaction that triggered the command.
    draft_name (str): The name of the draft to publish.
    proposals (List[Dict[str, str]]): The list of proposals.
    bot (commands.Bot): The bot instance.

    Returns:
    None
    """
    draft_to_publish = next(
        (
            item
            for item in proposals
            if item.get("title", "").strip() == draft_name.strip()
        ),
        None,
    )

    if draft_to_publish:
        embed = discord.Embed(
            title=f"Published Draft: {draft_to_publish['title']}",
            description=f"The draft '{draft_to_publish['title']}' has been published.",
            color=discord.Color.green(),
        )
        embed.set_author(
            name="Draft Publishing", icon_url=interaction.user.display_avatar.url
        )
        await interaction.response.send_message(embed=embed)

        proposals.remove(draft_to_publish)
        await publish_draft(
            draft_to_publish, bot, interaction.guild.id, interaction.guild
        )
    else:
        await interaction.response.send_message(f"Draft not found: {draft_name}")


# prepare the draft by setting the type, channel ID, and title based on the draft type
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
        channel_name = constants.GOVERNANCE_BUDGET_CHANNEL
        cfg.current_budget_id += 1
        cfg.update_id_values(
            cfg.current_budget_id, id_type
        )  # Update the governance ID in the config file
        title = (
            f"Bloom Budget Proposal (BBP) #{cfg.current_budget_id}: {draft['title']}"
        )
    else:
        id_type = GOVERNANCE_ID_TYPE
        channel_name = constants.GOVERNANCE_CHANNEL
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
    bot (Bot): The bot instance.
    guild_id (int): The ID of the guild where the draft will be published.
    """
    id_type, channel_name, title = await prepare_draft(guild, draft)
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

    **{constants.YES_VOTE} Yes**

    **{constants.NO_VOTE} Reassess**

    **{constants.ABSTAIN_VOTE} Abstain**

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
    await react_to_vote(thread_with_message.thread.id, bot, guild_id, channel_name)

    await vote_timer(
        thread_with_message.thread.id, bot, guild_id, channel_name, title, draft
    )


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

    await message.add_reaction(constants.YES_VOTE)
    await message.add_reaction(constants.NO_VOTE)
    await message.add_reaction(constants.ABSTAIN_VOTE)


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
        logger.error(f"Error: Guild with id {guild_id} not found.")
        return

    # Fetch the channel by name
    channel = discord.utils.get(guild.channels, name=channel_name)
    thread = channel.get_thread(thread_id)

    # Fetch the initial message in the thread using the thread ID
    message = await thread.fetch_message(thread_id)
    for reaction in message.reactions:
        if str(reaction.emoji) == f"{constants.YES_VOTE}":
            ongoing_votes[message.id]["yes_count"] = reaction.count - 1
        elif str(reaction.emoji) == f"{constants.NO_VOTE}":
            ongoing_votes[message.id]["reassess_count"] = reaction.count - 1
        elif str(reaction.emoji) == f"{constants.ABSTAIN_VOTE}":
            ongoing_votes[message.id]["abstain_count"] = reaction.count - 1

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

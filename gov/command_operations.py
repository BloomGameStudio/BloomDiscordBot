"""
command_operations.py is responsible for handling the business logic
associated with different commands such as !publish_draft, and !v / !vote_draft.
"""

from discord.ext import commands
from typing import List, Dict
from .proposals import publish_draft
from consts.constants import GOVERNANCE_TALK_CHANNEL
from shared.helpers import get_channel_by_name
from logger.logger import logger
import discord

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
            ctx.guild, GOVERNANCE_TALK_CHANNEL
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

    # Send a message
    msg = "Would you like to work on an existing draft proposal, or do you wish to create a new one? \nExisting drafts are:"
    await ctx.send(msg)

    # List existing draft proposals
    for proposal in proposals:
        await ctx.send(f"📝 {proposal['name']}")

    await ctx.send(f"{new_proposal_emoji} New")


async def handle_publishdraft(
    interaction: discord.Interaction,
    draft_name: str,
    proposals: List[Dict[str, str]],
    bot: commands.Bot,
) -> None:
    draft_to_publish = next(
        (item for item in proposals if item.get("title", "").strip() == draft_name.strip()),
        None,
    )

    if draft_to_publish:
        await interaction.response.send_message(f"Publishing draft: {draft_to_publish['title']}")
        proposals.remove(draft_to_publish)
        await publish_draft(draft_to_publish, bot, interaction.guild.id, interaction.guild)
    else:
        await interaction.response.send_message(f"Draft not found: {draft_name}")

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

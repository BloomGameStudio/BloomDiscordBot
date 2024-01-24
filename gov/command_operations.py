import discord
from discord.ext import commands
from typing import List, Dict
from .proposals import publish_draft
from shared.constants import GOVERNANCE_TALK_CHANNEL


async def handle_votedraft(
    ctx: commands.Context, proposals: List[Dict[str, str]], new_proposal_emoji: str
) -> None:
    # Get the channel with the name 'governance-talk' in the server
    governance_talk_channel = discord.utils.get(
        ctx.guild.channels, name=GOVERNANCE_TALK_CHANNEL
    )

    if governance_talk_channel is None:
        await ctx.send("The 'governance' channel could not be found in this server")
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
    ctx: commands.Context,
    draft_name: str,
    proposals: List[Dict[str, str]],
    bot: commands.Bot,
) -> None:
    draft_to_publish = next(
        (item for item in proposals if item["name"].strip() == draft_name.strip()),
        None,
    )

    if draft_to_publish:
        await ctx.send(f"Publishing draft: {draft_to_publish['name']}")
        proposals.remove(draft_to_publish)
        await publish_draft(draft_to_publish, bot, ctx.guild.id)
    else:
        await ctx.send(f"Draft not found: {draft_name}")

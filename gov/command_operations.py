from discord.ext import commands
from typing import List, Dict, Union
from .proposals import publish_draft
from shared.constants import GOVERNANCE_TALK_CHANNEL_ID

async def handle_votedraft(ctx: commands.Context, proposals: List[Dict[str, Union[str, int]]], new_proposal_emoji: str) -> None:
     #Use imported value
    if ctx.channel.id != int(GOVERNANCE_TALK_CHANNEL_ID):
        await ctx.send(f"This command can only be used in <#{GOVERNANCE_TALK_CHANNEL_ID}>")
        return
    msg = "Would you like to work on an existing draft proposal, or do you wish to create a new one? \nExisting drafts are:"

    await ctx.send(msg)

    for proposal in proposals:
        await ctx.send(f"📝 {proposal['name']}")

    await ctx.send(f"{new_proposal_emoji} New")

async def handle_publishdraft(ctx: commands.Context, draft_name: str, proposals: List[Dict[str, Union[str, int]]], bot: commands.Bot) -> None:
    draft_to_publish = next(
        (item for item in proposals if item["name"].strip() == draft_name.strip()),
        None,
    )

    if draft_to_publish:
        await ctx.send(f"Publishing draft: {draft_to_publish['name']}")
        await publish_draft(draft_to_publish, bot)
        proposals.remove(draft_to_publish)
    else:
        await ctx.send(f"Draft not found: {draft_name}")
from discord.ext import commands
from .command_operations import handle_votedraft, handle_publishdraft
from .proposal_modal import proposals
from consts.constants import new_proposal_emoji
from .proposal_modal import ProposalModal, ProposalButtonsView
from logger.logger import logger
from typing import Optional
import discord
from discord import ui

def setup_gov_commands(bot: commands.Bot) -> None:
    @bot.command(name="vote_draft", aliases=["v"], pass_context=True)
    async def votedraft(ctx):
        try: 
            view = ProposalButtonsView(proposals)
            await ctx.send("Select an option to create, edit, or delete a proposal.", view=view)
        except Exception as e:
            await ctx.send("Couldn't access proposal data.")
            logger.info(f"{'votedraft', e}")

    @bot.command(name="publish_draft")
    async def publishdraft(ctx: commands.Context, *, draft_name: str) -> None:
        if not draft_name:
            await ctx.send("Please provide a draft name.")
            return
        await handle_publishdraft(ctx, draft_name, proposals, bot)
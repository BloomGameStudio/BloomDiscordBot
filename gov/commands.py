from discord.ext import commands
from .command_operations import handle_votedraft, handle_publishdraft
from .proposals import proposals
from consts.constants import new_proposal_emoji
from .proposal_modal import ProposalButtonsView, PublishDraftSelect
from logger.logger import logger
from typing import Optional
import discord
from discord import ui

def setup_gov_commands(bot: commands.Bot) -> None:
    @bot.command(name="vote_draft", aliases=["v"], pass_context=True)
    async def votedraft(ctx):
        try: 
            view = ProposalButtonsView(proposals)
            await ctx.send("Click create, edit, or delete to modify or create a new proposal.", view=view)
        except Exception as e:
            await ctx.send("Couldn't access proposal data.")

    @bot.command(name="publish_draft")
    async def publishdraft(ctx: commands.Context, *, draft_name: str = None) -> None:
        try:
            view = discord.ui.View()
            view.add_item(PublishDraftSelect(proposals, bot))
            await ctx.send("Select a proposal.", view=view)
        except Exception as e:
            await ctx.send("Couldn't access proposal data.")
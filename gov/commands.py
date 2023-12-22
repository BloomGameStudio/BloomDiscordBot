from .command_operations import handle_votedraft, handle_publishdraft
from .proposals import proposals
from constants import new_proposal_emoji

def setup_gov_commands(bot):
    @bot.command(name='vote_draft', aliases=['v'], pass_context=True)
    async def votedraft(ctx):
        await handle_votedraft(ctx, proposals, new_proposal_emoji)

    @bot.command(name='publish_draft')
    async def publishdraft(ctx, *, draft_name=None):
        if not draft_name:
            await ctx.send("Please provide a draft name.")
            return
        await handle_publishdraft(ctx, draft_name, proposals, bot)
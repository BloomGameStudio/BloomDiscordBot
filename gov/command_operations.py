from .proposals import publish_draft
import os

async def handle_votedraft(ctx, proposals, new_proposal_emoji):
    if ctx.channel.id != int(os.getenv('GOVERNANCE_TALK_CHANNEL_ID')):
        await ctx.send("This command can only be used in the Governance talk channel")
        return
    msg = "Would you like to work on an existing draft proposal, or do you wish to create a new one? \nExisting drafts are:"

    await ctx.send(msg)

    for proposal in proposals:
        await ctx.send(f"📝 {proposal['name']}")

    await ctx.send(f"{new_proposal_emoji} New")

async def handle_publishdraft(ctx, draft_name, proposals, bot):
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
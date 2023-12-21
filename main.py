import discord
from discord.ext import commands
from gov.commands import setup_gov_commands
from gov.events import setup_gov_events
from constants import DISCORD_BOT_TOKEN, FILE_PATH
import json

def main():

    # Discord Config
    intents = discord.Intents.default()
    intents.message_content = True
    intents.reactions = True
    bot = commands.Bot(command_prefix="$", intents=intents)
    
    # Setup the governance discord commands, and events
    setup_gov_commands(bot, contributors, emoji_id_mapping)
    setup_gov_events(bot, contributors, emoji_id_mapping)

    # Run the bot
    bot.run(DISCORD_BOT_TOKEN)

if __name__ == "__main__":
    main()

@bot.event
async def on_message(message):
    for emoji_id, contributor_uid in emoji_id_mapping.items():
        contributor = next((c for c in contributors if c["uid"] == contributor_uid), None)

        if emoji_id in message.content:
            logging.info('Emoji Found in message!', emoji_id)

            if contributor:
                try:
                    logging.info(f'Messaging the user, {contributor["uid"]}')
                    message_link = message.jump_url
                    await send_dm_once(bot, contributor, message_link)
                except discord.errors.NotFound:
                    logging.warning(f'User not found: {contributor["uid"]}')

    fmt_proposals = ""

    # Loop over proposals and convert them to str with every proposal name being on a newline
    for proposal in proposals:
        fmt_proposals += f"📝 {proposal['name']}\n"

    if message.author == bot.user:
        return

    await bot.process_commands(message)

@bot.event
async def on_reaction_add(reaction, user):
    #Skip reactions from the bot
    if user == bot.user:
        return
    channel = reaction.message.channel

    def check(m):
        # message author == user who added the reaction
        return m.author == user

    contributor_emoji = next(
        (emoji_id for emoji_id, contributor_uid in emoji_id_mapping.items() if str(reaction.emoji) == emoji_id),
        
        None
    )

    if contributor_emoji:
        contributor = next(
            (c for c in contributors if c["uid"] == emoji_id_mapping[contributor_emoji]),
            None
        )

        if contributor:
            message_link = reaction.message.jump_url
            logging.info("Emoji react found, DMing contributor")
            await send_dm_once(bot, contributor, message_link)

    elif reaction.emoji == "📝":
        # Find/Get proposal that the user wants to edit or None
        edit_proposal = next(
            (
                item
                for item in proposals
                if (
                    reaction.message.content.strip().endswith(item["name"].strip())
                )  # In case of conflicts use == comparison after removing emoji and whitespace
            ),
            None,
        )

        if edit_proposal:
            await reaction.message.channel.send(f"You are editing: {edit_proposal['name']}")
            await reaction.message.channel.send("**Draft Details:**\n"
                                       f"**Title:** {edit_proposal['name']}\n"
                                       f"**Abstract:** {edit_proposal['abstract']}\n"
                                       f"**Background:** {edit_proposal['background']}\n")

            change_selection = await bot.wait_for("message", check=check)
            change_selection = change_selection.content.lower()

            while True:
                if change_selection == "title":
                    await channel.send("What will be the new title?")
                    change_answer = await bot.wait_for("message", check=check)
                    edit_proposal["name"] = change_answer.content

                if change_selection == "type":
                    await channel.send("What will be the new type?")
                    change_answer = await bot.wait_for("message", check=check)
                    edit_proposal["type"] = change_answer.content

                if change_selection == "abstract":
                    await channel.send("What will be the new abstract?")
                    change_answer = await bot.wait_for("message", check=check)
                    edit_proposal["abstract"] = change_answer.content

                if change_selection == "background":
                    await channel.send("What will be the new background?")
                    change_answer = await bot.wait_for("message", check=check)
                    edit_proposal["background"] = change_answer.content

                await channel.send(
                    "You can edit further by repeating the previous step. If you are finished type 'save' without the single quotes \n"
                    "If you wish to publish your draft, please use command ``$publish_draft``"
                )

                change_selection = await bot.wait_for("message", check=check)
                change_selection = change_selection.content.lower()

                if change_selection.lower() == "save":
                    await channel.send("Changes have been saved")

                    if edit_proposal["type"].lower() == "budget":
                        title = f"**Bloom Budget Proposal Draft: {edit_proposal['name']}**"
                    else:
                        title = f"**Bloom General Proposal Draft: {edit_proposal['name']}**"

                    msg = f"""
                    {title}

                    __**Abstract**__
                    {edit_proposal["abstract"]}

                    **__Background__**
                    {edit_proposal["background"]}

                    ** <:inevitable_bloom:1178256658741346344> Yes**
                    ** <:bulby_sore:1127463114481356882> Reassess**
                    ** <:pepe_angel:1161835636857241733> Abstain**

                    \n
                    If you wish to publish your draft proposal, please use command ``$publish_draft``.
                    """

                    await channel.send(textwrap.dedent(msg))

                    break

                elif change_selection.lower() == "cancel":
                    await channel.send("Editing has been cancelled")
                    break
        else:
            await channel.send("Draft not found")

    elif reaction.emoji == new_proposal_emoji:
        await reaction.message.channel.send("What is the title of this draft?")

        proposal = {}

        name = await bot.wait_for("message", check=check)
        proposal["name"] = name.content
        proposals.append(proposal)

        await channel.send("Is this budget or general?")

        type = await bot.wait_for("message", check=check)
        proposal["type"] = type.content

        await channel.send(f"Great! What is the abstract?")

        abstract = await bot.wait_for("message", check=check)
        proposal["abstract"] = abstract.content

        await channel.send("Can you provide some background?")

        background = await bot.wait_for("message", check=check)
        proposal["background"] = background.content

        if proposal["type"].lower() == "budget":
            title = f"**Bloom Budget Proposal Draft: {name.content}**"
       
        else:
            title = f"**Topic/Vote: {name.content}**"

        msg = f"""
        {title}

        __**Abstract**__
        {abstract.content}

        **__Background__**
        {background.content}

        ** <:inevitable_bloom:1178256658741346344> Yes**
        ** <:bulby_sore:1127463114481356882> Reassess**
        ** <:pepe_angel:1161835636857241733> Abstain**

    
        If you wish to publish your draft proposal, please use command ``$publish_draft``
        """

        await channel.send(textwrap.dedent(msg))

#Bot commands
@bot.command(name='vote_draft', aliases=['v'], pass_context=True)
async def votedraft(ctx):

    if ctx.channel.id != int(os.getenv('GOVERNANCE_TALK_CHANNEL_ID')):
        await ctx.send("This command can only be used in the Governance talk channel")
        return
    msg = "Would you like to work on an existing draft proposal, or do you wish to create a new one? \nExisting drafts are:"

    await ctx.send(msg)

    for proposal in proposals:
        await ctx.send(f"📝 {proposal['name']}")

    await ctx.send(f"{new_proposal_emoji} New")

@bot.command(name='publish_draft')
async def publishdraft(ctx, *, draft_name):
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
      
bot.run(os.getenv('DISCORD_BOT_TOKEN'))

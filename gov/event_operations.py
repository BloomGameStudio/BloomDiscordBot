import logging
import discord
import textwrap
from constants import new_proposal_emoji
from .proposals import proposals

async def handle_on_message(bot, message, proposals):
    fmt_proposals = ""

    # Loop over proposals and convert them to str with every proposal name being on a newline
    for proposal in proposals:
        fmt_proposals += f"📝 {proposal['name']}\n"

    if message.author == bot.user:
        return

    await bot.process_commands(message)

async def handle_on_reaction_add(bot, user, reaction, proposals, new_proposal_emoji):

    def check(m):
        return m.author == user and m.channel == reaction.message.channel
    
    channel = reaction.message.channel

    if reaction.emoji == "📝":
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
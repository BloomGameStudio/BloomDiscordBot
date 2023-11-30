import discord
import textwrap
import random
import os


# Discord Client Setup
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


# TODO:Add this to the draft proposal output ->

# This is a draft preview
# To publish the draft do xyz

# ----------


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


new_proposal_emoji = "💡"

proposals = []


# QUESTION: Should these be incremental, instead of random?
def get_governance_id():
    return random.randint(10, 100)


def get_budget_id():
    return random.randint(10, 100)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    fmt_proposals = ""

    # Loop over proposals and convert them to str with every proposal name being on a newline
    for proposal in proposals:
        fmt_proposals += f"📝 {proposal['name']}\n"

    if message.content.startswith("!vote_draft") or message.content.startswith("!v"):
        msg = f"Would you like to work on an existing draft or a new one? existing drafts are:"

        await message.channel.send(msg)

        for proposal in proposals:
            await message.channel.send(f"📝 {proposal['name']}")

        await message.channel.send(f"{new_proposal_emoji} New")

    if message.content.startswith("!publish_draft"):
        await message.channel.send("Sure! Here are the existing drafts:")
        for proposal in proposals:
            await message.channel.send(f"📝 {proposal['name']}")

        # Extract the draft name from the message
        draft_name = message.content.split("!publish_draft ", 1)[1].strip()

        # Find the draft with the specified name
        draft_to_publish = next(
            (item for item in proposals if item["name"].strip() == draft_name),
            None,
        )

        if draft_to_publish:
            await message.channel.send(f"Publishing draft: {draft_to_publish['name']}")

            # Implement your logic to publish the draft
            await publish_draft(draft_to_publish)

            # Remove the published draft from the list
            proposals.remove(draft_to_publish)
        else:
            await message.channel.send(f"Draft not found: {draft_name}")

@client.event
async def on_reaction_add(reaction, user):
    # The channel in which to operate in
    channel = reaction.message.channel

    def check(m):
        # message author == user who added the reaction
        return m.author == user

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

        await reaction.message.channel.send(f"You are editing: {edit_proposal['name']}")
        await reaction.message.channel.send("What would you like to change?")
        await reaction.message.channel.send("Title Type Abstract Background")

        change_selection = await client.wait_for("message", check=check)
        change_selection = change_selection.content.lower()

        while True:
            if change_selection == "title":
                await channel.send("What is be the new title?")
                change_answer = await client.wait_for("message", check=check)
                edit_proposal["name"] = change_answer.content

            if change_selection == "type":
                await channel.send("What is be the new type?")
                change_answer = await client.wait_for("message", check=check)
                edit_proposal["type"] = change_answer.content

            if change_selection == "abstract":
                await channel.send("What is be the new abstract?")
                change_answer = await client.wait_for("message", check=check)

                edit_proposal["abstract"] = change_answer.content

            if change_selection == "background":
                await channel.send("What is be the new background?")
                change_answer = await client.wait_for("message", check=check)
                edit_proposal["background"] = change_answer.content

            await channel.send(
                "You can edit further by repeating the previous step. If you are finished type 'save' without the single quotes"
            )

            change_selection = await client.wait_for("message", check=check)
            change_selection = change_selection.content.lower()

            if change_selection.lower() == "save":
                await channel.send("Changes have been saved")

                if edit_proposal["type"].lower() == "budget":
                    title = f"**Bloom Budget Proposal (BBP) #{get_budget_id()} {edit_proposal['name']}**"

                else:
                    title = (
                        f"**Topic/Vote {get_governance_id()}: {edit_proposal['name']}**"
                    )

                msg = f"""
                {title}

                __**Abstract**__
                {edit_proposal["abstract"]}

                **__Background__**
                {edit_proposal["background"]}

                ** :thumbsup: Yes**
                ** <:bulby_sore:1127463114481356882> Reassess**
                ** <:pepe_angel:1161835636857241733> Abstain**

                Vote will conclude in 48h from now.
                """

                await channel.send(textwrap.dedent(msg))

                break

    if reaction.emoji == new_proposal_emoji:
        await reaction.message.channel.send("What is the title of this draft?")

        proposal = {}

        name = await client.wait_for("message", check=check)
        proposal["name"] = name.content
        proposals.append(proposal)

        await channel.send("Is this budget or general?")

        type = await client.wait_for("message", check=check)
        proposal["type"] = type.content

        await channel.send(f"Great! what is the abstract?")

        abstract = await client.wait_for("message", check=check)
        proposal["abstract"] = abstract.content

        await channel.send("Can you provide some background?")

        background = await client.wait_for("message", check=check)
        proposal["background"] = background.content

        if proposal["type"].lower() == "budget":
            title = f"**Bloom Budget Proposal (BBP) #{get_budget_id()} {name.content}**"

        else:
            title = f"**Topic/Vote {get_governance_id()}: {name.content}**"

        msg = f"""
                {title}

                __**Abstract**__
                {abstract.content}

                **__Background__**
                {background.content}

                ** :thumbsup: Yes**
                ** <:bulby_sore:1127463114481356882> Reassess**
                ** <:pepe_angel:1161835636857241733> Abstain**

                Vote will conclude in 48h from now.
                """

        await channel.send(textwrap.dedent(msg))


def create_budget_vote(name, abstract, background):
    pass


async def publish_draft(draft):
    #tbd
    pass

client.run(os.environ["DISCORD_BOT_TOKEN"])

import discord
import textwrap
import random
import os
import configparser

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')  

# Global vars
current_governance_id = config.getint('ID_START_VALUES', 'governance_id')
current_budget_id = config.getint('ID_START_VALUES', 'budget_id')

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

def get_next_governance_id():
    global current_governance_id
    current_governance_id += 1
    return current_governance_id

def get_next_budget_id():
    global current_budget_id
    current_budget_id += 1
    return current_budget_id

def get_governance_id():
    return current_governance_id

def get_budget_id():
    return current_budget_id

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
        # Split the message content
        split_content = message.content.split("!publish_draft ", 1)

        # Check if there are elements after splitting
        if len(split_content) > 1:
            draft_name = split_content[1].strip()

            # Find the draft with the specified name
            draft_to_publish = next(
                (item for item in proposals if item["name"].strip() == draft_name),
                None,
            )

            if draft_to_publish:
                await message.channel.send(f"Publishing draft: {draft_to_publish['name']}")
                await publish_draft(draft_to_publish)
                proposals.remove(draft_to_publish)
            else:
                await message.channel.send(f"Draft not found: {draft_name}")
        else:
            await message.channel.send("Please provide the name of the draft to publish.")

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
                await channel.send("What will be the new title?")
                change_answer = await client.wait_for("message", check=check)
                edit_proposal["name"] = change_answer.content

            if change_selection == "type":
                await channel.send("What will be the new type?")
                change_answer = await client.wait_for("message", check=check)
                edit_proposal["type"] = change_answer.content

            if change_selection == "abstract":
                await channel.send("What will be the new abstract?")
                change_answer = await client.wait_for("message", check=check)
                
                edit_proposal["abstract"] = change_answer.content

            if change_selection == "background":
                await channel.send("What will be the new background?")
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
                    title = f"**Topic/Vote {get_governance_id()}: {edit_proposal['name']}**"

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
    channel_id = int(os.environ["POST_CHANNEL_ID"])
    print(f"{channel_id}")
    channel = client.get_channel(channel_id)

    if not channel:
        print("Error: Channel not found.")
        return

    # Increment the IDs only when publishing
    if draft["type"].lower() == "budget":
        current_budget_id = get_next_budget_id()
        title = f"**Bloom Budget Proposal (BBP) #{get_budget_id()} {draft['name']}**"
    else:
        current_governance_id = get_next_governance_id()
        title = f"**Topic/Vote {get_governance_id()}: {draft['name']}**"

    # Create the message content using the draft information
    msg = f"""
    {title}

    __**Abstract**__
    {draft["abstract"]}

    **__Background__**
    {draft["background"]}

    ** :thumbsup: Yes**
    ** <:bulby_sore:1127463114481356882> Reassess**
    ** <:pepe_angel:1161835636857241733> Abstain**

    Vote will conclude in 48h from now.
    """

    # Send the draft message to the specified channel
    await channel.send(textwrap.dedent(msg))

    print(f"Draft '{draft['name']}' published successfully.")

client.run(os.environ["DISCORD_BOT_TOKEN"])

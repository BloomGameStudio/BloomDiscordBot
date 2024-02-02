"""
shared/event_operations.py is responsible for handling the business logic associated with different
Events such as on_message, on_reaction_add, etc. Events that are shared across multiple domains of interest
are added here.
"""

import discord
import textwrap
from typing import List, Dict, Union
from discord.ext import commands
from discord import Message, Reaction, User
from discord.utils import get
from emotes.command_operations import send_dm_once
from consts.constants import MENU_COPY, DISCORD_ROLE_TRIGGERS, RULES_MESSAGE_ID, GENERAL_CHANNEL
from consts.types import BUDGET_ID_TYPE, GOVERNANCE_ID_TYPE
from .helpers import get_channel_by_name
from logger.logger import logger


async def process_new_member(member: discord.Member) -> None:
    """
    Sends a welcome message to a new member in the welcome channel.

    Args:
        member (discord.Member): The new member who joined the server.
    """
    try:
        # Get the welcome channel
        welcome_channel = get_channel_by_name(member.guild, GENERAL_CHANNEL)
        collab_land_join_channel = get_channel_by_name(member.guild, "collabland-join")
        start_here_channel = get_channel_by_name(member.guild, "start-here")

        # Send the welcome message
        await welcome_channel.send(
            f" 🌺 Welcome {member.mention}  to {member.guild.name}! We are pleased to have you here 🌺\n"
            "\n"
            "Take a moment to read and agree to the rules before you get started!"
            "\n"
            f"If you are an existing aXP, bXP, or uXP Hodler, please head over to <#{collab_land_join_channel.id}> to verify your wallet in order to receive your respective role! \n"
            "\n"
            f"Refer to <#{start_here_channel.id}> for more details about the studio!"
        )
    except ValueError as e:
        logger.error(f"Error sending welcome message: {str(e)}")


async def handle_message(
    bot: commands.Bot,
    message: Message,
    data: Dict[str, Dict[str, Union[List[Dict[str, str]], Dict[str, str]]]],
    proposals: List[Dict[str, Union[str, int]]],
) -> None:
    """
    Handles a new message in the server.
    If a contributors emoji is found, a DM is sent to the contributor.

    Args:
        bot (commands.Bot): The bot instance.
        message (Message): The new message.
        data (Dict): The server data.
        proposals (List): The list of proposals.
    """
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    server_name = message.guild.name
    server_data = data["servers"].get(server_name)

    # Log a warning if no data is found for the server
    if server_data is None:
        logger.warning(f"No data found for server: {server_name}")
        return

    # If the message starts with "!help", send the menu copy
    if message.content.startswith("!help"):
        await message.channel.send(MENU_COPY)
        return

    contributors = server_data["contributors"]
    emoji_dicts = server_data["emoji_dictionary"]

    fmt_proposals = ""
    for proposal in proposals:
        fmt_proposals += f"📝 {proposal['name']}\n"

    # Check if any emoji in the message matches an emoji in the emoji dictionary
    for emoji_id, contributor_uid in emoji_dicts.items():
        contributor = next(
            (c for c in contributors if c["uid"] == contributor_uid), None
        )
        if emoji_id in message.content:
            logger.info("Emoji Found in message! %s", emoji_id)
            if contributor:
                try:
                    logger.info(f'Messaging the user, {contributor["uid"]}')
                    message_link = message.jump_url
                    await send_dm_once(bot, contributor, message_link)
                except discord.errors.NotFound:
                    logger.warning(f'User not found: {contributor["uid"]}')
    # Process commands
    await bot.process_commands(message)


async def handle_reaction(
    bot: commands.Bot,
    reaction: Reaction,
    user: User,
    data: Dict[str, Dict[str, Union[List[Dict[str, str]], Dict[str, str]]]],
    proposals: List[Dict[str, Union[str, int]]],
    new_proposal_emoji: str,
) -> None:
    """
    Handles a new reaction in the server.
    If a contributors emoji is found, a DM is sent to the contributor.
    Proposals are edited if 📝 is used

    Args:
        bot (commands.Bot): The bot instance.
        reaction (Reaction): The new reaction.
        user (User): The user who added the reaction.
        data (Dict): The server data.
        proposals (List): The list of proposals.
        new_proposal_emoji (str): The emoji for new proposals.
    """
    # Get the server name and data
    server_name = reaction.message.guild.name
    server_data = data["servers"].get(server_name)

    # Log a warning if no data is found for the server
    if server_data is None:
        logger.warning(f"No data found for server: {server_name}")
        return

    # Ignore reactions from the bot itself
    if user == bot.user:
        return

    contributors = server_data["contributors"]
    emoji_dicts = server_data["emoji_dictionary"]

    # Check if the reaction emoji matches any in the emoji dictionary
    contributor_emoji = next(
        (
            emoji_id
            for emoji_id, contributor_uid in emoji_dicts.items()
            if str(reaction.emoji) == emoji_id
        ),
        None,
    )

    # If a matching emoji is found, send a DM to the contributor
    if contributor_emoji:
        contributor = next(
            (c for c in contributors if c["uid"] == emoji_dicts[contributor_emoji]),
            None,
        )
        if contributor:
            message_link = reaction.message.jump_url
            logger.info("Emoji react found, DMing contributor")
            await send_dm_once(bot, contributor, message_link)

    # check function for bot.wait_for
    def check(m):
        return m.author == user and m.channel == reaction.message.channel

    channel = reaction.message.channel

    # If the reaction emoji is "📝", edit the proposal
    if reaction.emoji == "📝":
        edit_proposal = next(
            (
                item
                for item in proposals
                if reaction.message.content.strip().endswith(item["name"].strip())
            ),
            None,
        )

        if edit_proposal:
            await reaction.message.channel.send(
                f"You are editing: {edit_proposal['name']}"
            )
            await reaction.message.channel.send(
                "**Draft Details:**\n"
                f"**Title:** {edit_proposal['name']}\n"
                f"**Abstract:** {edit_proposal['abstract']}\n"
                f"**Background:** {edit_proposal['background']}\n"
            )

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
                    "If you wish to publish your draft, please use command ``!publish_draft``"
                )

                change_selection = await bot.wait_for("message", check=check)
                change_selection = change_selection.content.lower()

                if change_selection.lower() == "save":
                    await channel.send("Changes have been saved")

                    if edit_proposal["type"].lower() == "budget":
                        title = (
                            f"**Bloom Budget Proposal Draft: {edit_proposal['name']}**"
                        )
                    else:
                        title = (
                            f"**Bloom General Proposal Draft: {edit_proposal['name']}**"
                        )

                    msg = textwrap.dedent(
                        f"""
                    {title}

                    __**Abstract**__
                    {edit_proposal["abstract"]}

                    **__Background__**
                    {edit_proposal["background"]}

                    ** 👍 Yes**

                    ** 👎 Reassess**

                    ** ❌ Abstain**

                    If you wish to publish your draft proposal, please use command ``!publish_draft``.
                    """
                    ).strip()

                    await channel.send(msg)
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

        def is_valid_type(message):
            return message.content.lower() in [BUDGET_ID_TYPE, GOVERNANCE_ID_TYPE]

        await channel.send("Is this budget or governance?")

        type_message = await bot.wait_for("message", check=is_valid_type)
        proposal["type"] = type_message.content

        await channel.send(f"Great! What is the abstract?")

        abstract = await bot.wait_for("message", check=check)
        proposal["abstract"] = abstract.content

        await channel.send("Can you provide some background?")

        background = await bot.wait_for("message", check=check)
        proposal["background"] = background.content

        if proposal["type"].lower() == "budget":
            title = f"**Bloom Budget Proposal (BBP) Draft: {name.content}**"

        else:
            title = f"**Bloom Governance Proposal (BGP) Draft: {name.content}**"

        msg = f"""
        {title}

        __**Abstract**__
        {abstract.content}

        **__Background__**
        {background.content}

        ** 👍 Yes**

        ** 👎 Reassess**

        ** ❌ Abstain**

    
        If you wish to publish your draft proposal, please use command ``!publish_draft``
        """

        await channel.send(textwrap.dedent(msg))


async def process_reaction_add(bot, payload):
    """
    Processes a reaction add event. Allocates roles to members based on their reaction.

    Args:
        bot (commands.Bot): The bot instance.
        payload (discord.RawReactionActionEvent): The reaction payload.
    """
    # If the reaction is on the rules message, process the reaction
    if payload.message_id == RULES_MESSAGE_ID:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)

        # If the reaction emoji is "🌺", add the "bloomer" role to the member
        if payload.emoji.name == "🌺":
            role = get(guild.roles, name="bloomer")
            await member.add_roles(role)
            response = f"{member.display_name} has selected 🌺!\n\n**Their commitment is official and they are now a Bloomer!**"
            general_channel = get_channel_by_name(guild, "🌺│home")
            await general_channel.send(response)
        else:
            # If the reaction emoji matches any in DISCORD_ROLE_TRIGGERS, add the corresponding role to the member
            for role_info in DISCORD_ROLE_TRIGGERS:
                if payload.emoji.id == role_info.get("emoji_id"):
                    general_channel = get_channel_by_name(guild, "🌺│home")
                    role = get(guild.roles, name=role_info.get("role"))
                    response = f"{member.display_name} has joined the **{role_info.get('name')}** pod!"
                    await general_channel.send(response)

                    if role is None:
                        logger.info(f"Role {role_info.get('role')} not found")
                        return
                    await member.add_roles(role)

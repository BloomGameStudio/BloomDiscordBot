import discord
import logging
import textwrap
from typing import List, Dict, Union
from discord.ext import commands
from discord import Message, Reaction, User
from discord.utils import get
from emotes.command_operations import send_dm_once
from shared.constants import DISCORD_ROLE_TRIGGERS, RULES_MESSAGE_ID
from shared.helpers import get_channel_by_name

async def process_reaction_add(bot, payload):
    if payload.message_id == RULES_MESSAGE_ID:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if payload.emoji.name == '🌺':
            role = get(guild.roles, name='bloomer')
            await member.add_roles(role)
            response = f"{member.display_name} has selected 🌺!\n\n**Their commitment is official and they are now a Bloomer!"
            general_channel = get_channel_by_name(guild, "🌺│home")
            await general_channel.send(response)
        else:
            for role_info in DISCORD_ROLE_TRIGGERS:
                if payload.emoji.id == role_info.get('emoji_id'):
                    general_channel = get_channel_by_name(guild, "🌺│home")
                    role = get(guild.roles, name=role_info.get('role'))
                    response = f"{member.display_name} has joined **{role_info.get('name')}**!"
                    await general_channel.send(response)
                    if role is None:
                        logging.info(f"Role {role_info.get('role')} not found")
                        return
                    await member.add_roles(role)
          
async def handle_member_join(member: discord.Member) -> None:
    #Send to welcome channel
    welcome_channel = get(member.guild.channels, name="welcome")
    collab_land_join_channel = get(member.guild.channels, name="collabland-join")
    start_here_channel = get(member.guild.channels, name="start-here")
    await welcome_channel.send(f" 🌺 Welcome {member.mention}  to {member.guild.name}! We are pleased to have you here 🌺\n"
                               "\n"
                               f"If you are an existing aXP, bXP, or cXP Hodler, please head over to <#{collab_land_join_channel.id}> to verify your wallet and to receive your respective role! \n"
                               "\n"
                               f"Refer to <#{start_here_channel.id}> for more details about the studio!")

async def handle_message(
    bot: commands.Bot,
    message: Message,
    data: Dict[str, Dict[str, Union[List[Dict[str, str]], Dict[str, str]]]],
    proposals: List[Dict[str, Union[str, int]]],
) -> None:
    if message.author == bot.user:
        return
    server_name = message.guild.name
    server_data = data["servers"].get(server_name)
    if server_data is None:
        logging.warning(f"No data found for server: {server_name}")
        return

    contributors = server_data["contributors"]
    emoji_dicts = server_data["emoji_dictionary"]

    fmt_proposals = ""
    for proposal in proposals:
        fmt_proposals += f"📝 {proposal['name']}\n"

    for emoji_id, contributor_uid in emoji_dicts.items():
        contributor = next(
            (c for c in contributors if c["uid"] == contributor_uid), None
        )
        if emoji_id in message.content:
            logging.info("Emoji Found in message! %s", emoji_id)
            if contributor:
                try:
                    logging.info(f'Messaging the user, {contributor["uid"]}')
                    message_link = message.jump_url
                    await send_dm_once(bot, contributor, message_link)
                except discord.errors.NotFound:
                    logging.warning(f'User not found: {contributor["uid"]}')
    await bot.process_commands(message)


async def handle_reaction(
    bot: commands.Bot,
    reaction: Reaction,
    user: User,
    data: Dict[str, Dict[str, Union[List[Dict[str, str]], Dict[str, str]]]],
    proposals: List[Dict[str, Union[str, int]]],
    new_proposal_emoji: str,
) -> None:
    server_name = reaction.message.guild.name
    server_data = data["servers"].get(server_name)
    if server_data is None:
        logging.warning(f"No data found for server: {server_name}")
        return
    if user == bot.user:
        return

    contributors = server_data["contributors"]
    emoji_dicts = server_data["emoji_dictionary"]

    contributor_emoji = next(
        (
            emoji_id
            for emoji_id, contributor_uid in emoji_dicts.items()
            if str(reaction.emoji) == emoji_id
        ),
        None,
    )
    if contributor_emoji:
        contributor = next(
            (c for c in contributors if c["uid"] == emoji_dicts[contributor_emoji]),
            None,
        )
        if contributor:
            message_link = reaction.message.jump_url
            logging.info("Emoji react found, DMing contributor")
            await send_dm_once(bot, contributor, message_link)

    def check(m):
        return m.author == user and m.channel == reaction.message.channel

    channel = reaction.message.channel

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
                    "If you wish to publish your draft, please use command ``$publish_draft``"
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

                    If you wish to publish your draft proposal, please use command ``$publish_draft``.
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

        await channel.send("Is this budget or governance?")

        type = await bot.wait_for("message", check=check)
        proposal["type"] = type.content

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

    
        If you wish to publish your draft proposal, please use command ``$publish_draft``
        """

        await channel.send(textwrap.dedent(msg))
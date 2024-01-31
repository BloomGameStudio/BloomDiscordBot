# -*- coding: UTF-8 -*-
from .crypto_constants import *
from .menu_copy import *
from discord.utils import get
from shared.helpers import get_channel_by_name
import logging
import discord

class CommandManager():

    async def process_reaction_add(self, bot, payload):
        if payload.message_id == RULES_MESSAGE_ID:
            guild = bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            if payload.emoji.name == "🌺":
                role = get(guild.roles, name="bloomer")
                await member.add_roles(role)
                response = f"{member.display_name} has selected 🌺!\n\n**Their commitment is official and they are now a Bloomer!**"
                general_channel = get_channel_by_name(guild, "🌺│home")
                await general_channel.send(response)
            else:
                for role_info in DISCORD_ROLE_TRIGGERS:
                    if payload.emoji.id == role_info.get("emoji_id"):
                        general_channel = get_channel_by_name(guild, "🌺│home")
                        role = get(guild.roles, name=role_info.get("role"))
                        response = (
                            f"{member.display_name} has joined the **{role_info.get('name')}** pod!"
                        )
                        await general_channel.send(response)
                        
                        if role is None:
                            logging.info(f"Role {role_info.get('role')} not found")
                            return
                        await member.add_roles(role)

    async def process_new_member(self, member: discord.Member) -> None:
    # Send to welcome channel
        welcome_channel = get(member.guild.channels, name="welcome")
        collab_land_join_channel = get(member.guild.channels, name="collabland-join")
        start_here_channel = get(member.guild.channels, name="start-here")
        await welcome_channel.send(
            f" 🌺 Welcome {member.mention}  to {member.guild.name}! We are pleased to have you here 🌺\n"
            "\n"
            "Take a moment to read and agree to the rules before you get started!"
            "\n"
            f"If you are an existing aXP, bXP, or cXP Hodler, please head over to <#{collab_land_join_channel.id}> to verify your wallet in order to receive your respective role! \n"
            "\n"
            f"Refer to <#{start_here_channel.id}> for more details about the studio!"
        )



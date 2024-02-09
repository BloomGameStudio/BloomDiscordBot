"""
shared/helpers.py is responsible for setting up helper functions for the bot.
helper functions may be functions that contain functionality that is used by multiple
modules.
"""

import discord


async def get_guild_member_check_role(ctx: discord.ext.commands.Context) -> bool:
    """
    Check if the guild member who invoked the command has the 'core' role.

    Parameters:
    ctx (discord.ext.commands.Context): The context in which the command was invoked.

    Returns:
    bool: True if the member has the 'core' role, False otherwise.
    """
    # Retrieve the guild member who invoked the command
    member = ctx.guild.get_member(ctx.author.id)
    permitted = False  # default value

    # Check if they have the 'core' role.
    if any(role.name == "core" for role in member.roles):
        permitted = True

    if not permitted:
        await ctx.send("You do not have permission to use this command.")

    return permitted

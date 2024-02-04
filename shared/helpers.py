"""
shared/helpers.py is responsible for setting up helper functions for the bot.
helper functions may be functions that contain functionality that is used by multiple
modules.
"""

import discord


def get_channel_by_name(guild: discord.Guild, channel_name: str) -> discord.TextChannel:
    """
    Soft match a channel name from consts/constants.py to a channel in the guild.

    Parameters:
    guild (discord.Guild): The guild to search for the channel in.
    channel_name (str): The name of the channel to search for.

    Returns:
    discord.TextChannel: The channel that matches the channel_name.

    Raises:
    ValueError: If no channel containing the channel_name exists in the guild.
    """
    # Get the channel name after the pipe character if it exists.
    channel_name = channel_name.split("│")[-1] if "│" in channel_name else channel_name

    for channel in guild.channels:
        if isinstance(channel, discord.TextChannel) and channel.name.endswith(
            channel_name
        ):
            return channel
    raise ValueError(
        f"No channel containing the name {channel_name} exists in the guild {guild}."
        "\nPlease check the channel names in consts/constants.py and make sure they match the channel names in your Discord server."
    )


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

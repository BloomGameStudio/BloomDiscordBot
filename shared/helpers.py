import discord


def get_channel_by_name(guild: discord.Guild, channel_name: str) -> discord.TextChannel:
    for channel in guild.channels:
        if isinstance(channel, discord.TextChannel) and channel.name == channel_name:
            return channel
    return None  # If no channel with this name exists


async def get_guild_member_check_role(ctx: discord.ext.commands.Context) -> bool:
    # Retrieve the guild member who invoked the command
    member = ctx.guild.get_member(ctx.author.id)
    permitted = False  # default value

    # Check if they have the 'core' role.
    if any(role.name == "core" for role in member.roles):
        permitted = True

    if not permitted:
        await ctx.send("You do not have permission to use this command.")

    return permitted

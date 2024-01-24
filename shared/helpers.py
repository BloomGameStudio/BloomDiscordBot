import discord

def get_channel_by_name(guild: discord.Guild, channel_name: str) -> discord.TextChannel:
    for channel in guild.channels:
        if isinstance(channel, discord.TextChannel) and channel.name == channel_name:
            return channel
    return None  # If no channel with this name exists
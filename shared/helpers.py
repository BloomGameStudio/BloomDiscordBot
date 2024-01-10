def get_channel_by_name(guild, channel_name):
    for channel in guild.channels:
        if channel.name == channel_name:
            return channel
    return None  # if no channel with this name exists
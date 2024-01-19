def get_channel_by_name(guild: int, channel_name: str) -> None:
    for channel in guild.channels:
        if channel.name == channel_name:
            return channel
    return None  # If no channel with this name exists

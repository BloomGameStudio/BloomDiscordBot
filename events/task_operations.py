from discord import ScheduledEvent, TextChannel
from typing import List, Dict, Union

"""
When the bot is initiated the on_ready event will be loaded which starts the check_events task.
This task runs every hour to check for upcoming events within the next 24 hours.
The formatted_string is used to format the message that will be sent to the channel.
"""

async def format_and_send_message(event: ScheduledEvent, users: List[Dict[str, Union[str, int]]], channel: TextChannel) -> None:
    guild_id = event.guild.id
    user_mentions = [f"<@{user['user_id']}>" for user in users]
    user_list_string = ', '.join(user_mentions)

    formatted_string = (
        f"📆 **Upcoming Events in the Next 24 Hours** 📆 \n"
        f"\n"
        f":link: **Event Link https://discord.com/events/{guild_id}/{event.id} :link:**\n"
        f"\n"
        f"{user_list_string}\n"
    )

    # Send message
    await channel.send(formatted_string)
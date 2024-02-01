from discord import ScheduledEvent, TextChannel
from typing import List, Dict, Union

"""
When the bot is initiated the on_ready event will be loaded which starts the check_events task.
This task runs every hour to check for upcoming events within the next 24 hours.
format_and_send_message is used to format the message and send it to the general channel.
"""


async def format_and_send_message(
    event: ScheduledEvent, users: List[Dict[str, Union[str, int]]], channel: TextChannel
) -> None:
    """
    Format and send a message to a specified channel. The message includes a link to the event and mentions all users.

    Parameters:
    event (ScheduledEvent): The event for which the message is being sent.
    users (List[Dict[str, Union[str, int]]]): The list of users to be mentioned in the message.
    channel (TextChannel): The channel to which the message is to be sent.
    """
    guild_id = event.guild.id
    user_mentions = [f"<@{user['user_id']}>" for user in users]
    user_list_string = ", ".join(user_mentions)

    formatted_string = (
        f"📆 **Upcoming Events in the Next 24 Hours** 📆 \n"
        f"\n"
        f":link: **Event Link https://discord.com/events/{guild_id}/{event.id} :link:**\n"
        f"\n"
        f"{user_list_string}\n"
    )

    # Send message
    await channel.send(formatted_string)

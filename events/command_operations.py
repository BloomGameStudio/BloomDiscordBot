"""
events/command_operations.py is responsible for handling the business logic associated with event commands
This includes fetching events, and deleting events.
"""

from discord import Guild
import discord
from shared.helpers import get_guild_member_check_role


async def list_events_operation(guild: Guild) -> str:
    """
    List all the events in the guild and format the information.

    Parameters:
    guild (Guild): The guild in which the events were created.

    Returns:
    str: The formatted event information.
    """
    event_list = guild.scheduled_events

    # Extracting event information
    event_info_list = [
        (event.name, event.id, event.description) for event in event_list
    ]

    # Formatting the information
    formatted_events = [
        f"🌺 **{name}**🌺 \n**event_id: **{event_id}\n**Description:** {description}"
        for name, event_id, description in event_info_list
    ]
    formatted_string = "\n\n".join(formatted_events)

    return formatted_string


async def delete_event_operation(interaction: discord.Interaction, guild: Guild, event_name: str):
    """
    Delete an event in the guild if the user has authorization to do so.

    Parameters:
    interaction (Interaction): The interaction of the command invocation.
    guild (Guild): The guild in which the event was created.
    event_name (str): The name of the event to be deleted.

    Returns:
    str: The result of the delete operation.
    """
    permitted = await get_guild_member_check_role(interaction)
    if not permitted:
        return

    events = await guild.fetch_scheduled_events()
    event = next((e for e in events if e.name == event_name), None)

    if event:
        # Delete the event
        await event.delete()
        return f"Event '{event_name}' has been deleted 🗑️"
    else:
        return f"No event found with name '{event_name}'."

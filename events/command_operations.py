from discord import Guild
from discord.ext.commands import Context
from shared.helpers import get_guild_member_check_role

"""
events/command_operations.py is responsible for handling the business logic associated with event commands
This includes fetching events, and deleting events.
"""

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


async def delete_event_operation(ctx: Context, guild: Guild, event_id: int):
    """
    Delete an event in the guild if the user has authorization to do so.

    Parameters:
    ctx (Context): The context of the command invocation.
    guild (Guild): The guild in which the event was created.
    event_id (int): The ID of the event to be deleted.

    Returns:
    str: The result of the delete operation.
    """
    permitted = await get_guild_member_check_role(ctx)
    if not permitted:
        return

    event = guild.get_scheduled_event(event_id)

    if event:
        # Delete the event
        await event.delete()
        return f"Event with ID {event_id} has been deleted 🗑️"
    else:
        return f"No event found with ID {event_id}."

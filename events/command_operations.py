async def list_events_operation(guild):
    event_list = guild.scheduled_events

    # Extracting event information
    event_info_list = [(event.name, event.id, event.description) for event in event_list]

    # Formatting the information
    formatted_events = [
        f"🌺 **{name}**🌺 \n**event_id: **{event_id}\n**Description:** {description}"
        for name, event_id, description in event_info_list
    ]
    formatted_string = "\n\n".join(formatted_events)

    return formatted_string

async def delete_event_operation(guild, event_id):
    event = guild.get_scheduled_event(event_id)

    if event:
        # Delete the event
        await event.delete()
        return f"Event with ID {event_id} has been deleted 🗑️"
    else:
        return f"No event found with ID {event_id}."
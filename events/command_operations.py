from discord import Guild


async def list_events_operation(guild: Guild) -> str:
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


async def delete_event_operation(ctx, guild, event_id):
    # Retrieve the guild member who invoked the command
    member = ctx.guild.get_member(ctx.author.id)

    # Check if they have the 'core' role.
    if not any(role.name == 'core' for role in member.roles):
        await ctx.send("You do not have permission to use this command.")
        return
    event = guild.get_scheduled_event(event_id)

    if event:
        # Delete the event
        await event.delete()
        return f"Event with ID {event_id} has been deleted 🗑️"
    else:
        return f"No event found with ID {event_id}."

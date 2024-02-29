import discord
from discord.ext import commands
from discord import app_commands
from helpers import get_guild_member_check_role


class EventCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="list_events")
    async def list_events(self, interaction: discord.Interaction):
        """
        Lists the events associated with this guild.

        Parameters:
        interaction (Interaction): The interaction of the command invocation.
        """

        guild = interaction.guild

        # Get the list of events
        event_list = guild.scheduled_events

        # Extract event information
        event_urls = [
            f"https://discord.com/events/{guild.id}/{event.id}"
            for event in event_list  # Get the event URL
        ]

        # Format the information
        formatted_events = [
            f":link: **Event Link <{url}>** :link:"  # Wrap the URL in <> to prevent Discord from generating an embed
            for url in event_urls
        ]
        formatted_string = "\n\n".join(formatted_events)
        await interaction.response.send_message(
            f"🗓️ **All Events**🗓️ \n\n{formatted_string}"
        )

    @app_commands.command(name="delete_event")
    async def delete_event(
        self, interaction: discord.Interaction, event_name: str = None
    ):
        """
        Deletes an event from the guild.

        Parameters:
        interaction (Interaction): The interaction of the command invocation.
        event_name (str): The name of the event to be deleted.
        """
        if event_name is None:
            await interaction.response.send_message(
                "Please enter an event name with this command. Example: `/delete_event My Event`"
            )
            return

        guild = interaction.guild

        # Defer the interaction response
        await interaction.response.defer()

        # Check if the member has the required role
        permitted = await get_guild_member_check_role(interaction)

        if not permitted:
            await interaction.response.send_message(
                "You do not have permission to use this command."
            )
            return

        # Fetch the list of events
        events = await guild.fetch_scheduled_events()
        event = next((e for e in events if e.name == event_name), None)

        if event:
            # Delete the event
            await event.delete()
            await interaction.followup.send(f"Event '{event_name}' has been deleted 🗑️")
        else:
            await interaction.followup.send(f"No event found with name '{event_name}'.")

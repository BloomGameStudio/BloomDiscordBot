""" 
The ContributorCommandsCog class is a cog for handling the contributor commands.
It contains the following commands:
- list_contributors: Lists the contributors associated with this guild. 
- remove_contributor: Removes a contributor from the list of contributors.
- add_contributor: Add a contributor to the list of contributors if the user invoking the command has the authorization to do so.
"""

import discord
from discord.ext import commands
from discord import app_commands
from utils.utils import Utils
from logger.logger import logger
from database.service import DatabaseService
from utils.utils import DiscordUtils


class ContributorCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DatabaseService()

    @app_commands.command(
        name="add_contributor", description="Add a contributor with their emoji"
    )
    async def add_contributor(
        self, interaction: discord.Interaction, member: discord.Member, emoji: str
    ):
        """Add a contributor with their emoji"""
        try:
            await interaction.response.defer()

            if not await DiscordUtils.get_guild_member_check_role(interaction):
                return

            guild_id = interaction.guild_id

            logger.info(
                f"Adding contributor {member.name} (ID: {member.id}) to guild {interaction.guild.name} (ID: {guild_id})"
            )

            self.db.update_contributor_in_db(
                guild_id=guild_id, uid=str(member.id), note=member.name, emoji_id=emoji
            )

            await interaction.followup.send(
                f"Contributor {member.mention} added successfully!"
            )

        except Exception as e:
            logger.error(f"Error adding contributor: {e}")
            await interaction.followup.send("Error adding contributor")

    @app_commands.command(name="remove_contributor", description="Remove a contributor")
    async def remove_contributor(
        self, interaction: discord.Interaction, member: discord.Member
    ):
        """Remove a contributor"""
        try:
            await interaction.response.defer()
            if not await DiscordUtils.get_guild_member_check_role(interaction):
                return

            guild_id = interaction.guild_id
            logger.info(
                f"Removing contributor {member.name} (ID: {member.id}) from guild {interaction.guild.name} (ID: {guild_id})"
            )

            contributors = self.db.get_contributors_from_db(guild_id)
            if not any(c.uid == str(member.id) for c in contributors):
                await interaction.followup.send(
                    f"{member.mention} is not a contributor.", ephemeral=True
                )
                return

            self.db.remove_contributor_from_db(guild_id=guild_id, uid=str(member.id))
            await interaction.followup.send(
                f"Contributor {member.mention} removed successfully!"
            )
        except Exception as e:
            logger.error(f"Error removing contributor: {e}")

    @app_commands.command(name="contributors", description="List all contributors")
    async def list_contributors(self, interaction: discord.Interaction):
        """List all contributors"""
        try:
            await interaction.response.defer()

            guild_id = interaction.guild_id

            logger.info(
                f"Listing contributors for guild {interaction.guild.name} (ID: {guild_id})"
            )

            contributors = self.db.get_contributors_from_db(guild_id)

            if not contributors:
                await interaction.followup.send("No contributors found.")
                return

            embed = discord.Embed(title=":artifacts: List of Contributors :artifacts:")

            for contributor in contributors:
                embed.add_field(
                    name=contributor.note, value=contributor.emoji_id, inline=True
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error listing contributors: {e}")
            await interaction.followup.send(
                "An error occurred while listing contributors."
            )

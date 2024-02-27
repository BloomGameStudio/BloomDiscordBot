import discord
from discord.ext import commands
from discord import app_commands
from shared.helpers import get_guild_member_check_role, update_json_file, add_contributor_to_list
from typing import Dict, Optional

class ContributorCommandsCog(commands.Cog):
    def __init__(self, bot, contributors, emoji_dicts):
        self.bot = bot
        self.contributors = contributors
        self.emoji_dicts = emoji_dicts

    @app_commands.command(name="contributors")
    async def list_contributors(self, interaction: discord.Interaction):
        """
        Lists the contributors associated with this guild.
        """
        # Defer the response
        await interaction.response.defer()

        server_name = interaction.guild.name
        emoji_dict = self.emoji_id_mapping.get(server_name)
        if emoji_dict is None:
            await interaction.followup.send(
                f"No emoji dictionary found for server: {server_name}"
            )
            return

        emoji_list = [emoji for emoji in emoji_dict.keys()]
        emoji_text = "\n".join(emoji_list)
        message = f" :fire: **List of Contributors** :fire: \n" f"{emoji_text}"
        await interaction.followup.send(message)
        
    @app_commands.command(name="remove_contributor")
    async def remove_contributor(
        self, interaction: discord.Interaction, user_mention: str
    ):
        """
        Removes a contributor from the list of contributors.

        Parameters:
        interaction (Interaction): The interaction of the command invocation.
        user_mention (str): The mention of the user to remove.
        """
        # Defer the response
        await interaction.response.defer()
        permitted = await get_guild_member_check_role(interaction)
        if not permitted:
            return
        if user_mention:
            uid = user_mention.strip("<@!>").split(">")[0]
            server_contributors = self.contributors.get(interaction.guild.name)
            if server_contributors is None:
                await interaction.followup.send(
                    "No contributors found for server: " + interaction.guild.name
                )
                return
            for contributor in server_contributors:
                if contributor["uid"] == uid:
                    emoji_dict = self.emoji_dicts.get(interaction.guild.name)
                    if emoji_dict is None:
                        await interaction.followup.send(
                            "Emoji dictionary not found for server: "
                            + interaction.guild.name
                        )
                        return
                    emoji_id_to_remove = next(
                        (
                            emoji_id
                            for emoji_id, c in emoji_dict.items()
                            if c == contributor["uid"]
                        ),
                        None,
                    )
                    if emoji_id_to_remove:
                        del emoji_dict[emoji_id_to_remove]
                    server_contributors.remove(contributor)
                    self.contributors[
                        interaction.guild.name
                    ] = server_contributors  # Update the contributors with the updated server_contributors
                    self.emoji_dicts[
                        interaction.guild.name
                    ] = emoji_dict  # Update the emoji_dicts with the updated emoji_dict
                    update_json_file(
                        interaction.guild.name,
                        {
                            "contributors": server_contributors,
                            "emoji_dictionary": emoji_dict,
                        },
                    )
                    await interaction.followup.send(
                        f"Contributor removed successfully!"
                    )
                    return
            await interaction.followup.send("Contributor not found.")
        else:
            await interaction.followup.send(
                "Please provide the mention of the contributor to remove."
            )
    
    @app_commands.command(name="add_contributor")
    async def add_contributor(self, interaction: discord.Interaction, user_mention: str, emoji: str):
        """
        Add a contributor to the list of contributors if the user invoking the command has the authorization to do so.
        The contributor is added by either tagging them with their emoji, or reacting to the message with their emoji.

        Parameters:
        interaction (Interaction): The interaction of the command invocation.
        user_mention (str): The mention of the user to add.
        emoji (str): The emoji to associate with the user.
        """
        
        await interaction.response.defer()

        permitted = await get_guild_member_check_role(interaction)
        if not permitted:
            return
        uid = user_mention.strip("<@!>")
        emoji_id = emoji
        server_contributors = self.contributors.get(interaction.guild.name)
        if server_contributors is None:
            await interaction.followup.send(
                "No contributors found for server: " + interaction.guild.name
            )
            return
        existing_contributor: Optional[Dict[str, str]] = next(
            (c for c in server_contributors if c["uid"] == uid), None
        )

        if existing_contributor:
            await interaction.followup.send(
                f"Contributor {existing_contributor['uid']} already exists"
            )
        else:
            emoji_dict = self.emoji_dicts.get(interaction.guild.name)
            if emoji_dict is None:
                await interaction.followup.send(
                    "Emoji dictionary not found for server: " + interaction.guild.name
                )
                return
            await add_contributor_to_list(
                interaction, uid, emoji_id, server_contributors, emoji_dict
            )
            await interaction.followup.send(f"Contributor added successfully!")
"""
emotes/command_operations.py is responsible for handling the business logic associated with emote commands
This includes adding, removing, listing, and direct messaging contributors.
"""

import asyncio
import json
import discord
from config.config import CONTRIBUTORS_FILE_PATH
from shared.helpers import get_guild_member_check_role
from typing import List, Dict, Any


async def add_contributor_to_list(
    ctx: discord.ext.commands.Context,
    uid: str,
    emoji_id: str,
    contributors: List[Dict[str, str]],
    emoji_id_mapping: Dict[str, str],
) -> Dict[str, str]:
    """
    Add a contributor to the list of contributors.
    Creates a new contributor object and adds it to the list of contributors.
    Adds the emoji ID to the emoji ID mapping.
    update_json_file is called to update the JSON file with the new contributor and emoji ID mapping.

    Parameters:
    ctx (Context): The context of the command invocation.
    uid (str): The UID of the contributor to add.
    emoji_id (str): The emoji ID of the contributor to add.
    contributors (List[Dict[str, str]]): The list of contributors to add to.
    emoji_id_mapping (Dict[str, str]): The emoji ID mapping to add to.

    """
    # Get the user's username
    user = await ctx.guild.fetch_member(int(uid))
    note = user.name if user else "User not found"

    new_contributor = {"uid": uid, "note": note}
    contributors.append(new_contributor)
    emoji_id_mapping[
        emoji_id
    ] = uid  # Use the UID directly as the value in emoji_id_mapping

    update_json_file(
        ctx.guild.name,
        {"contributors": contributors, "emoji_dictionary": emoji_id_mapping},
    )
    return new_contributor


async def send_dm_once(
    bot: discord.Client, contributor: Dict[str, str], message_link: str
) -> None:
    """
    Sends a direct message to a contributor if they are mentioned in a message.
    A contributor can be mentioned via a react, or in a message itself.
    To mention a contributor you must use their emoji.
    The contributor needs to exist in emotes/contributors.json for the contributor to be mentioned.

    Parameters:
    bot (discord.Client): The bot instance.
    contributor (Dict[str, str]): The contributor to send a DM to.
    message_link (str): The link to the message that mentioned the contributor.
    """

    user = await bot.fetch_user(int(contributor["uid"]))
    if user:
        dm_message = f"Hello {user.name}! You have been mentioned in this message! {message_link}"
        await user.send(dm_message)


def update_json_file(server_name: str, server_data: Dict[str, Any]) -> None:
    """
    Update emotes/contributors.json with the new contributor and emoji ID mapping.

    Parameters:
    server_name (str): The name of the server to update.
    server_data (Dict[str, Any]): The data to update the server with.
    """
    # Read the existing data
    with open(CONTRIBUTORS_FILE_PATH, "r") as json_file:
        data = json.load(json_file)

    # Update the specific server's data
    data["servers"][server_name] = server_data

    # Write the updated data back to the file
    with open(CONTRIBUTORS_FILE_PATH, "w") as json_file:
        json.dump(data, json_file, indent=4)


async def list_contributors(
    ctx: discord.ext.commands.Context,
    contributors: List[Dict[str, str]],
    emoji_id_mapping: Dict[str, Dict[str, str]],
) -> None:
    """
    List all contributors in a specific guild/s.

    Parameters:
    ctx (Context): The context in which the command was invoked.
    contributors (List[Dict[str, str]]): The contributors to list.
    emoji_id_mapping (Dict[str, Dict[str, str]]): The emoji ID mapping to use.
    """
    server_name = ctx.guild.name
    emoji_dict = emoji_id_mapping.get(server_name)
    if emoji_dict is None:
        await ctx.send(f"No emoji dictionary found for server: {server_name}")
        return

    emoji_list = [emoji for emoji in emoji_dict.keys()]
    emoji_text = "\n".join(emoji_list)
    message = f" :fire: **List of Contributors** :fire: \n" f"{emoji_text}"
    await ctx.send(message)


async def remove_contributor(
    ctx: discord.ext.commands.Context,
    contributors: Dict[str, List[Dict[str, str]]],
    emoji_dicts: Dict[str, Dict[str, str]],
    user_mention: str,
) -> None:
    """
    Remove a contributors details from the list of contributors.
    The user invoking this command needs the authorization to do so.

    Parameters:
    ctx (Context): The context in which the command was invoked.
    contributors (Dict[str, List[Dict[str, str]]]): The contributors to remove from.
    emoji_dicts (Dict[str, Dict[str, str]]): The emoji ID mapping to use.
    user_mention (str): The mention of the user to remove.

    """
    permitted = await get_guild_member_check_role(ctx)
    if not permitted:
        return
    if user_mention:
        uid = user_mention.strip("<@!>").split(">")[0]
        server_contributors = contributors.get(ctx.guild.name)
        if server_contributors is None:
            await ctx.send("No contributors found for server: " + ctx.guild.name)
            return
        for contributor in server_contributors:
            if contributor["uid"] == uid:
                emoji_dict = emoji_dicts.get(ctx.guild.name)
                if emoji_dict is None:
                    await ctx.send(
                        "Emoji dictionary not found for server: " + ctx.guild.name
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
                contributors[
                    ctx.guild.name
                ] = server_contributors  # Update the contributors with the updated server_contributors
                emoji_dicts[
                    ctx.guild.name
                ] = emoji_dict  # Update the emoji_dicts with the updated emoji_dict
                update_json_file(
                    ctx.guild.name,
                    {
                        "contributors": server_contributors,
                        "emoji_dictionary": emoji_dict,
                    },
                )
                await ctx.send(f"Contributor removed successfully!")
                return
        await ctx.send("Contributor not found.")
    else:
        await ctx.send("Please provide the mention of the contributor to remove.")


async def add_contributor(
    ctx: discord.ext.commands.Context,
    contributors: Dict[str, List[Dict[str, str]]],
    emoji_dicts: Dict[str, Dict[str, str]],
    bot: discord.client,
) -> None:
    """
    Add a contributor to the list of contributors if the user invoking the command has the authorization to do so.
    The contributor is added by either tagging them with their emoji, or reacting to the message with their emoji.

    Parameters:
    ctx (Context): The context in which the command was invoked.
    contributors (Dict[str, List[Dict[str, str]]]): The contributors dict to add to.
    emoji_dicts (Dict[str, Dict[str, str]]): The emoji ID mapping to use.
    bot (discord.client): The bot instance.

    """
    permitted = await get_guild_member_check_role(ctx)
    if not permitted:
        return
    message = await ctx.send(
        "**To add a contributor, reply to this message by tagging them with their emoji**\n"
        "\n"
        "**Example:** `@user <:emoji:123456789>`\n"
        "\n"
        "If you are adding yourself, simply react to this post with your emoji"
    )

    def check_message(msg: discord.Message) -> bool:
        return msg.author == ctx.author and msg.channel == ctx.channel

    def check_reaction(reaction: discord.Reaction, user: discord.User) -> bool:
        return user == ctx.author and reaction.message.id == message.id

    # Wait 60 seconds for either a message or a reaction, whichever is done first.
    done, pending = await asyncio.wait(
        [
            asyncio.create_task(
                bot.wait_for("message", check=check_message, timeout=60)
            ),
            asyncio.create_task(
                bot.wait_for("reaction_add", check=check_reaction, timeout=60)
            ),
        ],
        return_when=asyncio.FIRST_COMPLETED,
    )

    # Cancel the task(s) that didn't finish.
    for future in pending:
        future.cancel()

    result: tuple = done.pop().result()
    if isinstance(result, discord.Message):
        inputs: List[str] = result.content.split()
        if len(inputs) == 2:
            uid, emoji_id = inputs
            uid = uid.strip("<@!>")
            server_contributors = contributors.get(ctx.guild.name)
            if server_contributors is None:
                await ctx.send("No contributors found for server: " + ctx.guild.name)
                return
            existing_contributor: [Dict[str, str], None] = next(
                (c for c in server_contributors if c["uid"] == uid), None
            )

            if existing_contributor:
                await ctx.send(
                    f"Contributor {existing_contributor['uid']} already exists"
                )
            else:
                emoji_dict = emoji_dicts.get(ctx.guild.name)
                if emoji_dict is None:
                    await ctx.send(
                        "Emoji dictionary not found for server: " + ctx.guild.name
                    )
                    return
                await add_contributor_to_list(
                    ctx, uid, emoji_id, server_contributors, emoji_dict
                )
                await ctx.send(f"Contributor added successfully!")
        else:
            await ctx.send("Invalid input. Please provide all required information.")
    elif isinstance(result, tuple) and len(result) == 2:
        reaction, user = result
        emoji_id: str = str(reaction.emoji)
        uid: str = str(user.id)
        server_contributors = contributors.get(ctx.guild.name)
        if server_contributors is None:
            await ctx.send("No contributors found for server: " + ctx.guild.name)
            return
        existing_contributor: [Dict[str, str], None] = next(
            (c for c in server_contributors if c["uid"] == uid), None
        )

        if existing_contributor:
            await ctx.send(f"Contributor {existing_contributor['uid']} already exists")
        else:
            emoji_dict = emoji_dicts.get(ctx.guild.name)
            if emoji_dict is None:
                await ctx.send(
                    "Emoji dictionary not found for server: " + ctx.guild.name
                )
                return
            await add_contributor_to_list(
                ctx, uid, emoji_id, server_contributors, emoji_dict
            )
            await ctx.send(f"Contributor added successfully!")
    else:
        await ctx.send("Timeout. Please run the command again.")

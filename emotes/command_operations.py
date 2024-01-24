import asyncio
import json
import discord
from shared.constants import CONTRIBUTORS_FILE_PATH
from typing import List, Dict, Any


def add_contributor_to_list(
    ctx: discord.ext.commands.Context,
    uid: str,
    emoji_id: str,
    contributors: List[Dict[str, str]],
    emoji_id_mapping: Dict[str, str],
) -> Dict[str, str]:
    # Get the user's display name
    user = ctx.guild.get_member(int(uid))
    note = user.display_name if user else "User not found"

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
    user = await bot.fetch_user(int(contributor["uid"]))
    if user:
        dm_message = f"Hello {user.name}! You have been mentioned in this message! {message_link}"
        await user.send(dm_message)


def update_json_file(server_name: str, server_data: Dict[str, Any]) -> None:
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
    server_name = ctx.guild.name
    emoji_dict = emoji_id_mapping.get(server_name)
    if emoji_dict is None:
        await ctx.send(f"No emoji dictionary found for server: {server_name}")
        return

    emoji_mapping_list = [f"{emoji}" for emoji in emoji_dict.keys()]
    emoji_mapping_text = "\n".join(emoji_mapping_list)
    message = f" :fire: **List of Contributors** :fire: \n" f"{emoji_mapping_text}"
    await ctx.send(message)


async def remove_contributor(
    ctx: discord.ext.commands.Context,
    contributors: Dict[str, List[Dict[str, str]]],
    emoji_dicts: Dict[str, Dict[str, str]],
    user_mention: str,
) -> None:
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
                add_contributor_to_list(
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
            add_contributor_to_list(uid, emoji_id, server_contributors, emoji_dict)
            await ctx.send(f"Contributor added successfully!")
    else:
        await ctx.send("Timeout. Please run the command again.")

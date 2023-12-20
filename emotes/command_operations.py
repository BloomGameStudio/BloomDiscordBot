import asyncio
import json
from constants import FILE_PATH

def add_contributor_to_list(uid, emoji_id, contributors, emoji_id_mapping):    
    new_contributor = {"uid": uid}
    contributors.append(new_contributor)
    emoji_id_mapping[emoji_id] = uid  # Use the UID directly as the value in emoji_id_mapping
    update_json_file(contributors, emoji_id_mapping)  # Pass the required arguments
    return new_contributor
    
async def send_dm_once(bot, contributor, message_link):
    user = await bot.fetch_user(int(contributor["uid"]))
    if user:
        dm_message = f"Hello {user.name}! You have been mentioned in this message! {message_link}"
        await user.send(dm_message)

def update_json_file(contributors, emoji_id_mapping):
    # Extract emoji names from emojiIdMapping
    emoji_names = {uid: emoji.split(':')[1] for emoji, uid in emoji_id_mapping.items()}

    # Add 'note' to each contributor
    for contributor in contributors:
        uid = contributor['uid']
        if uid in emoji_names:
            contributor['note'] = emoji_names[uid]

    with open(FILE_PATH, 'w') as json_file:
        json.dump({"contributors": contributors or [], "emojiIdMapping": emoji_id_mapping or {}}, json_file, indent=4)

async def list_contributors(ctx, emoji_id_mapping):
    emoji_mapping_list = [emoji for emoji in emoji_id_mapping.keys()]
    emoji_mapping_text = "\n".join(emoji_mapping_list)
    message = (
        f"<:artifacts:1113725319011110943> **List of Contributors** <:artifacts:1113725319011110943>\n"
        f"{emoji_mapping_text}"
    )
    await ctx.send(message)

async def remove_contributor(ctx, contributors, emoji_id_mapping, user_mention=None):
    if user_mention:
        uid = user_mention.strip('<@!>').split('>')[0]
        for contributor in contributors:
            if contributor["uid"] == uid:
                emoji_id_to_remove = next((emoji_id for emoji_id, c in emoji_id_mapping.items() if c == contributor["uid"]), None)
                if emoji_id_to_remove:
                    del emoji_id_mapping[emoji_id_to_remove]
                contributors.remove(contributor)
                update_json_file(contributors, emoji_id_mapping)  # Pass the required arguments
                await ctx.send(f"Contributor removed successfully!")
                return
        await ctx.send("Contributor not found.")
    else:
        await ctx.send("Please provide the mention of the contributor to remove.")

async def add_contributor(ctx, contributors, emoji_id_mapping, bot):
    await ctx.send("**To add a contributor, reply to this message by tagging them with their emoji**\n"
                "\n"
                "**Example:** `@user <:emoji:123456789>`\n"
                "\n"
                "If you are adding yourself, simply react to this post with your emoji")

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    try:
        response = await bot.wait_for('message', check=check, timeout=60)
        inputs = response.content.split()
        if len(inputs) == 2:
            uid, emoji_id = inputs
            uid = uid.strip('<@!>')
            existing_contributor = next((c for c in contributors if c["uid"] == uid), None)

            if existing_contributor:
                await ctx.send(f"Contributor {existing_contributor['uid']} already exists")
            else:
                add_contributor_to_list(uid, emoji_id, contributors, emoji_id_mapping)  # Pass emoji_id here
                await ctx.send(f"Contributor added successfully!")
        else:
            await ctx.send("Invalid input. Please provide all required information.")
    except asyncio.TimeoutError:
        await ctx.send("Timeout. Please run the command again.")
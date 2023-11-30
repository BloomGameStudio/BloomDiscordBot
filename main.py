import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from emojis import *

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)

@bot.event
async def on_message(message):
    for emoji_id, contributor_uid in emoji_id_mapping.items():
        contributor = next((c for c in contributors if c["uid"].lower() == contributor_uid.lower()), None)

        if emoji_id in message.content:
            print(f'Emoji Found!', emoji_id)
            await message.add_reaction(emoji_id)

            if contributor:
                print(f'Messaging the user, {contributor["uid"]}')
                message_link = message.jump_url
                await send_dm_once(bot, contributor, message_link)

    # Process other commands
    await bot.process_commands(message)

@bot.command(name='contributors')
async def listcontributors(ctx):
    contributors_list = "\n".join([f"{contributor['name']} - UID: {contributor['uid']}" for contributor in contributors])
    await ctx.send("<:artifacts:1113725319011110943> **List of Contributors** <:artifacts:1113725319011110943>\n" + contributors_list)

@bot.command(name='removecontributor')
async def removecontributor(ctx, uid_to_remove=None):
    if uid_to_remove:
        for contributor in contributors:
            if contributor["uid"] == uid_to_remove:
                emoji_id_to_remove = next((emoji_id for emoji_id, c in emoji_id_mapping.items() if c == contributor), None)
                if emoji_id_to_remove:
                    del emoji_id_mapping[emoji_id_to_remove]
                contributors.remove(contributor)
                update_json_file()
                print(f"Contributor {contributor['name']} removed successfully!")
                await ctx.send(f"Contributor {contributor['name']} removed successfully!")
                return
        await ctx.send("Contributor not found.")
    else:
        await ctx.send("Please provide the UID of the contributor to remove.")


@bot.command(name='addcontributor')
async def addcontributor(ctx):
    await ctx.send("**To add a contributor provide the following information:**\n"
                   "\n"
                   "**1. Name**\n"
                   "**2. User ID (UID)**\n"
                   "**3. Emoji ID**\n"
                   "**Example:** `Sarahtonein 123456789012345678 <:sarah:123456789>`")

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    try:
        response = await bot.wait_for('message', check=check, timeout=60)
        inputs = response.content.split()
        if len(inputs) == 3:
            name, uid, emoji_id, = inputs

            # Check if the UID already exists in contributors
            existing_contributor = next((c for c in contributors if c["uid"].lower() == uid.lower()), None)

            if existing_contributor:
                print(f'Contributor {existing_contributor["name"]} already exists')
                await ctx.send(f"Contributor {existing_contributor['name']} already exists")
            else:
                # UID doesn't exist, call add_contributor
                new_contributor = add_contributor(name, uid, emoji_id)
                print(f'New contributor added', {name}, {uid})
                await ctx.send(f"Contributor {new_contributor['name']} added successfully!")
        else:
            await ctx.send("Invalid input. Please provide all required information.")
    except asyncio.TimeoutError:
        await ctx.send("Timeout. Please run the command again.")


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    await bot.change_presence(activity=discord.Game(name="Monitoring messages"))

bot_token = os.getenv('TOKEN')
bot.run(bot_token)

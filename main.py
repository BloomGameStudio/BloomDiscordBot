import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from emojis import *

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

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

    # Process add_contributor command
    if message.content.startswith("!addcontributor"):
        await message.channel.send("To add a contributor, please provide the following information:\n"
                                   "1. Name\n"
                                   "2. User ID (UID)\n"
                                   "3. Emoji ID\n"
                                   "Example: `Sarahtonein 123456789012345678 <:sarah:123456789>`")

        def check(msg):
            return msg.author == message.author and msg.channel == message.channel

        try:
            response = await bot.wait_for('message', check=check, timeout=60)
            inputs = response.content.split()
            if len(inputs) == 3:
                name, uid, emoji_id, = inputs

                # Check if the UID already exists in contributors
                existing_contributor = next((c for c in contributors if c["uid"].lower() == uid.lower()), None)

                if existing_contributor:
                    print(f'Contributor {existing_contributor["name"]} already exists')
                    await message.channel.send(f"Contributor {existing_contributor['name']} already exists")
                else:
                    # UID doesn't exist, call add_contributor
                    new_contributor = add_contributor(name, uid, emoji_id)
                    print(f'New contributor added', {name}, {uid})
                    await message.channel.send(f"Contributor {new_contributor['name']} added successfully!")
            else:
                await message.channel.send("Invalid input. Please provide all required information.")
        except asyncio.TimeoutError:
            await message.channel.send("Timeout. Please run the command again.")

    # Process contributors command
    if message.content.startswith("!contributors"):
        contributors_list = "\n".join([f"{contributor['name']} - UID: {contributor['uid']}" for contributor in contributors])
        await message.channel.send("List of Contributors:\n" + contributors_list)

    # Process removecontributor command
    if message.content.startswith("!removecontributor"):
        result_message = remove_contributor(message.content)
        await message.channel.send(result_message)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    await bot.change_presence(activity=discord.Game(name="Monitoring messages"))

bot_token = os.getenv('TOKEN')
bot.run(bot_token)

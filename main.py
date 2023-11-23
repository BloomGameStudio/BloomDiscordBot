import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from emotes import *

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_message(message):
    if not message.author.bot and message.content.startswith("!actioned"):
        contributor = get_contributor_by_uid(str(message.author.id))
        if contributor:
            contributor.actioned = True
            await message.channel.send("Thanks for the response! You won't receive any more reminders.")
            return  # Stop processing other checks if actioned command is received

    for emoji_id, contributor in emoji_id_mapping.items():
        if emoji_id in message.content:
            print(f'Emoji Found!', {emoji_id})
            await message.add_reaction(emoji_id)

            if not contributor.actioned:
                print(f'Messaging the user, {contributor.uid}')
                message_link = message.jump_url  # Get the jump URL of the message
                await send_dm_periodically(bot, contributor, message_link)

    # Process add_contributor command
    if message.content.startswith("!addcontributor"):
        await message.channel.send("To add a contributor, please provide the following information:\n"
                                   "1. Name\n"
                                   "2. User ID (UID)\n"
                                   "3. Emoji ID\n"
                                   "4. UTC Start Time\n"
                                   "5. UTC End Time\n"
                                   "Example: `Sarahtonein 123456789012345678 <:sarah:1176399164154851368> 1 5`")

        def check(msg):
            return msg.author == message.author and msg.channel == message.channel

        try:
            response = await bot.wait_for('message', check=check, timeout=60)
            inputs = response.content.split()
            if len(inputs) == 5:
                name, uid, emoji_id, start_time, end_time = inputs
                add_contributor(name, uid, emoji_id, int(start_time), int(end_time))
                print(f'New contributor added', {name}, {uid})
                await message.channel.send(f"Contributor {name} added successfully!")                
            else:
                await message.channel.send("Invalid input. Please provide all required information.")
        except asyncio.TimeoutError:
            await message.channel.send("Timeout. Please run the command again.")

    # Process contributors command
    if message.content.startswith("!contributors"):
        contributors_list = "\n".join([f"{contributor.name} - UID: {contributor.uid}" for contributor in contributors])
        await message.channel.send("List of Contributors:\n" + contributors_list)

    # Process removecontributor command
    if message.content.startswith("!removecontributor"):
        result_message = process_remove_contributor_command(message.content)
        await message.channel.send(result_message)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    await bot.change_presence(activity=discord.Game(name="Monitoring messages"))

bot_token = os.getenv('TOKEN')
bot.run(bot_token)

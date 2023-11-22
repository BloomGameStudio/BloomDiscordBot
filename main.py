import discord
import asyncio
from discord.ext import commands
import os
from dotenv import load_dotenv
from emotes import emoji_id_mapping, Contributor
from datetime import datetime
from pytz import timezone

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
                print(f'Annoying the user, {contributor.uid}')
                message_link = message.jump_url  # Get the jump URL of the message
                await send_dm_periodically(contributor, message_link)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    await bot.change_presence(activity=discord.Game(name="Monitoring messages"))

async def send_dm_periodically(contributor, message_link):
    user = await bot.fetch_user(int(contributor.uid))
    if user:
        if is_valid_time(contributor):  # Pass the contributor object
            dm_message = f"Hello {user.name}! You have been pinged! Reacted to a message: {message_link}\nReminder: Please respond with !actioned to stop the message"
            await user.send(dm_message)
            while not contributor.actioned:
                await asyncio.sleep(60 * 60 * 4)  # Wait for 4 hours before sending the next reminder


def is_valid_time(contributor):
    #DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    now = datetime.utcnow()
    current_hour = now.hour

    return contributor.utc_start_time <= current_hour <= contributor.utc_end_time

def get_contributor_by_uid(uid):
    for contributor in emoji_id_mapping.values():
        if contributor.uid == uid:
            return contributor
    return None

bot_token = os.getenv('TOKEN')
bot.run(bot_token)
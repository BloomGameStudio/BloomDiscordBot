import discord
import textwrap
import random
import os

# Discord Client Setup
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    fmt_proposals = ""

    # Loop over proposals and convert them to str with every proposal name beeing on a newline
    for proposal in proposals:
        fmt_proposals += f"📝 {proposal['name']}\n"

    if message.content.startswith("!vote_draft") or message.content.startswith("!v"):
        msg = f"Would you like to work on an existing draft or a new one? existing drafts are:"

        await message.channel.send(msg)

        for proposal in proposals:
            await message.channel.send(f"📝 {proposal['name']}")

        await message.channel.send(f"{new_proposal_emoji} New")

from discord.ext import commands
from emojis.emojis import emoji_id_mapping, contributors, update_json_file, add_contributor
import asyncio

def setup_commands(bot: commands.Bot):
    @bot.command(name='contributors')
    async def listcontributors(ctx):
        # Include only the emoji in the list
        emoji_mapping_list = [emoji for emoji in emoji_id_mapping.keys()]
        
        emoji_mapping_text = "\n".join(emoji_mapping_list)

        message = (
            f"<:artifacts:1113725319011110943> **List of Contributors** <:artifacts:1113725319011110943>\n"
            f"{emoji_mapping_text}"
        )
        
        await ctx.send(message)

    @bot.command(name='remove_contributor')
    async def removecontributor(ctx, user_mention=None):
        if user_mention:
            uid = user_mention.strip('<@!>').split('>')[0]
            for contributor in contributors:
                if contributor["uid"] == uid:
                    emoji_id_to_remove = next((emoji_id for emoji_id, c in emoji_id_mapping.items() if c == contributor["uid"]), None)
                    if emoji_id_to_remove:
                        del emoji_id_mapping[emoji_id_to_remove]
                    contributors.remove(contributor)
                    update_json_file()
                    await ctx.send(f"Contributor removed successfully!")
                    return
            await ctx.send("Contributor not found.")
        else:
            await ctx.send("Please provide the mention of the contributor to remove.")

    @bot.command(name='add_contributor')
    async def addcontributor(ctx):
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

                # Strip the <@> characters from the uid
                uid = uid.strip('<@!>')

                # Check if the UID already exists in contributors
                existing_contributor = next((c for c in contributors if c["uid"] == uid), None)

                if existing_contributor:
                    await ctx.send(f"Contributor {existing_contributor['uid']} already exists")
                else:
                    # UID doesn't exist, call add_contributor
                    add_contributor(uid, emoji_id)
                    await ctx.send(f"Contributor added successfully!")
            else:
                await ctx.send("Invalid input. Please provide all required information.")
        except asyncio.TimeoutError:
            await ctx.send("Timeout. Please run the command again.")
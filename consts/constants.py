"""
consts/constants.py contains constants used throughout the bot.

GENERAL_CHANNEL, GOVERNANCE_CHANNEL, GOVERNANCE_BUDGET_CHANNEL, GOVERNANCE_TALK_CHANNEL
are various channels used throughout the bot.
Example usage is when posting information to Discord such as new events, new governance proposals, when members join, etc.

new_proposal_emoji: The emoji used to inform the bot you wish to draft a new governance proposal.
This is required when !v or !vote_draft command is invoked.

CONTRIBUTORS_FILE_PATH: File path to the JSON file containing a dictionary of contributors and emoji dictionaries for both Bloom Studio and Bloom Collective.

POSTED_EVENTS_FILE_PATH: File path to the JSON file containing a list of posted events (events that have been posted to Discord). 
This is used to prevent duplicate events from being posted.

RULES_MESSAGE_ID: The ID of the message that contains the rules/welcome message.

DISCORD_ROLE_TRIGGERS: A list of dictionaries. Each dictionary represents a role that can be assigned to a bloomer.
Each dictionary contains the following keys:
- 'name': The name of the role.
- 'emoji_id': The ID of the emoji associated with the role.
- 'role': The actual role that will be assigned to the user.

MENU_COPY: A string containing the help menu for the bot. This menu lists all the available commands and their descriptions.

CONFIG_ID_MAP: A dictionary containing the valid ids and keys that can be selected to be incremented or in rare cases decremented in the config.ini file.

CONFIG_ABSOLUTE_PATH: The absolute path to the config.ini file.

"""

import discord

# Preferred consts
GENERAL_CHANNEL = "🌺│home"
GOVERNANCE_CHANNEL = "improvement-props"
GOVERNANCE_BUDGET_CHANNEL = "budgetary-props"
GOVERNANCE_TALK_CHANNEL = "🐬│governance"
COLLAB_LAND_CHANNEL = "🤖│collabland-join"
START_HERE_CHANNEL = "start-here"

# fallback consts
FALLBACK_GENERAL_CHANNEL = "🐘│announcements"
FALLBACK_GOVERNANCE_TALK_CHANNEL = "🌺│home"
FALLBACK_COLLAB_LAND_CHANNEL = "🌺│home"
FALLBACK_START_HERE_CHANNEL = "🌺│home"

# NOTE: There are no fallbacks for GOVERNANCE_CHANNEL and GOVERNANCE_BUDGET_CHANNEL
# Should there be the desire to do so, fallback channels should be created along with a function that handles forum channel types

# Attempt to get the preferred channel, if it fails, attempt to get the fallback channel, if it fails, attempt to get the default channel
# The default channel is "general" this is a text channel that is created when a server is made.
def get_channel(bot, guild_id, preferred_channel, fallback_channel):
    try:
        channel = discord.utils.get(
            bot.get_guild(guild_id).channels, name=preferred_channel
        )
        if channel is None:
            raise ValueError(f"Channel {preferred_channel} not found")
        return channel
    except ValueError:
        channel = discord.utils.get(
            bot.get_guild(guild_id).channels, name=fallback_channel
        )
        if channel is None:
            channel = discord.utils.get(
                bot.get_guild(guild_id).channels, name="general"
            )
            if channel is None:
                raise ValueError(
                    "Both preferred, fallback, and default channels not found"
                )
        return channel

new_proposal_emoji = "💡"

RULES_MESSAGE_ID = 1202059311681904661  # Set to ID of whatever message you want to be used as rules / to welcome a user

DISCORD_ROLE_TRIGGERS = [
    {"name": "Client", "emoji_id": 1199583728129802322, "role": "Client Pod"},
    {"name": "Graphics & Design", "emoji_id": 980752213347549234, "role": "Graphics Pod"},
    {"name": "Backend", "emoji_id": 846911453839228938, "role": "Backend Pod"},
    {"name": "Gameplay & Story Pod", "emoji_id": 961338498525306980, "role": "Gameplay & Story Pod"},
    {"name": "Operations", "emoji_id": 945177584768004127, "role": "Policy & Ops Pod"},
    {"name": "Financial", "emoji_id": 887872297082449970, "role": "Donator"},
]

MENU_COPY = """
__ 🌺 **Bloom Bot Commands** 🌺 __
Commands can be prompted with **!**

**!help**
```
Procure this message. You knew that already, silly goose.
```
**!add_contributor**
```
Add a contributor to the list of contributors
```
**!remove_contributor**
```
Remove a contributor from the list of contributors
```
**!contributors**
```
Display the list of contributors
```
**!list_events**
```
Display the list of events and their associated event ID
```
**!remove_event**
```
Remove an event from the list of events
Example: !remove_event 2583458345

```
**!v or !vote_draft**
```
Draft a vote proposal
```
**!publish_draft**
```
Publish a draft that has been worked on.
Example: !publish_draft Budget Proposal
```
"""

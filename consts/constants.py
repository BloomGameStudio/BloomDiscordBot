"""
consts/constants.py contains constants used throughout the bot.

CONFIG_ABSOLUTE_PATH: The absolute path to the config.ini file.

GENERAL_CHANNEL, GOVERNANCE_CHANNEL, GOVERNANCE_BUDGET_CHANNEL, GOVERNANCE_TALK_CHANNEL
are various channels used throughout the bot.
Example usage is when posting information to Discord such as new events, new governance proposals, when members join, etc.

YES_VOTE: The emoji used to vote yes on a proposal. Can be replaced with another emoji.

NO_VOTE: The emoji used to vote no on a proposal.Can be replaced with another emoji.

ABSTAIN_VOTE: The emoji used to abstain from voting on a proposal. Can be replaced with another emoji.

new_proposal_emoji: The emoji used to inform the bot you wish to draft a new governance proposal.
This is required when !v or !vote_draft command is invoked.

RULES_MESSAGE_ID: The ID of the message that contains the rules/welcome message.

DISCORD_ROLE_TRIGGERS: A list of dictionaries. Each dictionary represents a role that can be assigned to a bloomer.
Each dictionary contains the following keys:
- 'name': The name of the role.
- 'emoji_id': The ID of the emoji associated with the role.
- 'role': The actual role that will be assigned to the user.

MENU_COPY: A string containing the help menu for the bot. This menu lists all the available commands and their descriptions.

"""

GENERAL_CHANNEL = "🌺│home"
GOVERNANCE_CHANNEL = "improvement-props"
GOVERNANCE_BUDGET_CHANNEL = "budgetary-props"
GOVERNANCE_TALK_CHANNEL = "🐬│governance"
COLLAB_LAND_CHANNEL = "🤖│collabland-join"
START_HERE_CHANNEL = "start-here"
PROPOSAL_CONCLUSION_EMOJIS = [
    "<a:blob_time:1230791614851584060>",
    "<a:saber_pepe:1230791417220300800>",
    "<:inevitable_bloom:1192384857691656212>",
    ":tada:",
    ":hibiscus:",
]

YES_VOTE = "👍"
NO_VOTE = "👎"
ABSTAIN_VOTE = "❌"

FALLBACK_GENERAL_CHANNEL = "🐘│announcements"
FALLBACK_GOVERNANCE_TALK_CHANNEL = "🌺│home"

FALLBACK_GOVERNANCE_BUDGET_CHANNEL = "improvement-props"
FALLBACK_GOVERNANCE_CHANNEL = "budgetary-props"

CONSTANT_FALLBACK_MAPPING = {
    GENERAL_CHANNEL: FALLBACK_GENERAL_CHANNEL,
    GOVERNANCE_CHANNEL: FALLBACK_GOVERNANCE_CHANNEL,
    GOVERNANCE_BUDGET_CHANNEL: FALLBACK_GOVERNANCE_BUDGET_CHANNEL,
    GOVERNANCE_TALK_CHANNEL: FALLBACK_GOVERNANCE_TALK_CHANNEL,
}

RULES_MESSAGE_ID = 1202059311681904661  # Set to ID of whatever message you want to be used as rules / to welcome a user
DISCORD_ROLE_TRIGGERS = [
    {"name": "Client", "emoji_id": 1199583728129802322, "role": "Client Pod"},
    {
        "name": "Graphics & Design",
        "emoji_id": 980752213347549234,
        "role": "Graphics Pod",
    },
    {"name": "Backend", "emoji_id": 846911453839228938, "role": "Backend Pod"},
    {
        "name": "Gameplay & Story Pod",
        "emoji_id": 961338498525306980,
        "role": "Gameplay & Story Pod",
    },
    {"name": "Operations", "emoji_id": 945177584768004127, "role": "Policy & Ops Pod"},
    {"name": "Financial", "emoji_id": 887872297082449970, "role": "Donator"},
]

MENU_COPY = """
__ 🌺 **Bloom Bot Commands** 🌺 __
Commands can be prompted with **/**

**/help**
```
Display this help message with all available commands.
```

**/add_contributor {member} {emoji}**
```
Add a new member (and associated emoji) to the list of core contributors.
```

**/remove_contributor {member}**
```
Remove an existing member from the list of core contributors.
```

**/contributors**
```
Return a list of core contributors.
```

**/list_events**
```
Return a list of upcoming events.
```

**/create_proposal {thread_id}**
```
Create a new proposal from a draft thread and submit it for voting.
Use the thread ID from your draft proposal URL.
```
"""

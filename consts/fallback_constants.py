"""
consts/fallback_constants.py contains fallback constants used throughout the bot.

GENERAL_CHANNEL, GOVERNANCE_CHANNEL, GOVERNANCE_BUDGET_CHANNEL, GOVERNANCE_TALK_CHANNEL
are various channels used throughout the bot.
Example usage is when posting information to Discord such as new events, new governance proposals, when members join, etc.

YES_VOTE: The emoji used to vote yes on a proposal. Can be replaced with another emoji.

NO_VOTE: The emoji used to vote no on a proposal.Can be replaced with another emoji.

ABSTAIN_VOTE: The emoji used to abstain from voting on a proposal. Can be replaced with another emoji.

RULES_MESSAGE_ID: The ID of the message that contains the rules/welcome message.

DISCORD_ROLE_TRIGGERS: A list of dictionaries. Each dictionary represents a role that can be assigned to a bloomer.
Each dictionary contains the following keys:
- 'name': The name of the role.
- 'emoji_id': The ID of the emoji associated with the role.
- 'role': The actual role that will be assigned to the user.

MENU_COPY: A string containing the help menu for the bot. This menu lists all the available commands and their descriptions.

"""

# Preferred consts
GENERAL_CHANNEL = "🌺│home"
GOVERNANCE_CHANNEL = "improvement-props"
GOVERNANCE_BUDGET_CHANNEL = "budgetary-props"
GOVERNANCE_TALK_CHANNEL = "🐬│governance"
COLLAB_LAND_CHANNEL = "🤖│collabland-join"
START_HERE_CHANNEL = "🦤│faq"

YES_VOTE = "👍"
NO_VOTE = "👎"
ABSTAIN_VOTE = "❌"

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
Commands can be prompted with **/**

**/help**
```
Procure this message. You knew that already, silly goose.
```
**/add_contributor**
```
Add a contributor to the list of contributors
```
**/remove_contributor**
```
Remove a contributor from the list of contributors
```
**/contributors**
```
Display the list of contributors
```
**/list_events**
```
Display the list of events and their associated event ID
```
**/remove_event**
```
Remove an event from the list of events
Example: /remove_event my_event

```
**/vote_draft**
```
Draft a vote proposal
```
**/publish_draft**
```
Publish a draft that has been worked on.
```
"""

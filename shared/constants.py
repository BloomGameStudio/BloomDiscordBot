# Constants used throughout the bot
# Ensure the servers you run the bot in contain the required channel names
GENERAL_CHANNEL = "🌺│home"
GOVERNANCE_CHANNEL = "improvement-props"
GOVERNANCE_BUDGET_CHANNEL = "budgetary-props"
GOVERNANCE_TALK_CHANNEL = "🐬│governance"
INTRODUCE_YOURSELF_CHANNEL = "🌊│introduce-yourself"
new_proposal_emoji = "💡"
CONTRIBUTORS_FILE_PATH = "./emotes/contributors.json"
POSTED_EVENTS_FILE_PATH = "./events/posted_events.json"

RULES_MESSAGE_ID = 1202059311681904661 # Set to ID of whatever message you want to be used as rules / to welcome a user
DISCORD_ROLE_TRIGGERS = [
	{'name':'Client','emoji_id':1199583728129802322,'role':'Client Pod'},
	{'name':'Graphics & Design','emoji_id':980752213347549234,'role':'Graphics Pod'},
	{'name':'Backend','emoji_id':846911453839228938,'role':'Backend Pod'},
	{'name':'Gameplay & Story Pod','emoji_id':961338498525306980,'role':'Gameplay & Story Pod'},
	{'name':'Operations','emoji_id':945177584768004127,'role':'Policy & Ops Pod'},
	{'name':'Financial','emoji_id':887872297082449970,'role':'Donator'},
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
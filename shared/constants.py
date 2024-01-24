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

# This is an example message ID for a message of your choosing.
# Is used in shared/events.py and shared/event_operations.py
# Please reference those files for details on thse functions.
RULES_MESSAGE_ID = 1199577260643057685

# OK Bloomer ROLE_TRIGGERS:
DISCORD_ROLE_TRIGGERS = [
	{'name':'Client','emoji_id': 1199583728129802322 ,'role':'Client Pod'},
	{'name':'Graphics & Design','emoji_id':980752213347549234,'role':'Graphics Pod'},
	{'name':'Backend','emoji_id':846911453839228938,'role':'Backend Pod'},
	{'name':'Gameplay & Story Pod','emoji_id':961338498525306980,'role':'Gameplay & Story Pod'},
	{'name':'Operations','emoji_id':945177584768004127,'role':'Policy & Ops Pod'},
	{'name':'Financial','emoji_id':887872297082449970,'role':'Donator'},
]

# OK Bloomer default role
ROLE_WHEN_NEW_USER_CONFIRMED='contributors'

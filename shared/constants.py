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

#OK BLOOMER CONSTANTS

DISCORD_ROLE_TRIGGERS = [
	{'name':'Client','emoji_id':737603507795787816,'role':'Client Pod'},
	{'name':'Graphics & Design','emoji_id':980752213347549234,'role':'Graphics Pod'},
	{'name':'Backend','emoji_id':846911453839228938,'role':'Backend Pod'},
	{'name':'Gameplay & Story Pod','emoji_id':961338498525306980,'role':'Gameplay & Story Pod'},
	{'name':'Operations','emoji_id':945177584768004127,'role':'Policy & Ops Pod'},
	{'name':'Financial','emoji_id':887872297082449970,'role':'Donator'},
]

ROLE_WHEN_NEW_USER_CONFIRMED='contributors'

#-----------------------------#
#THESE ARE BOT/GUILD SPECIFIC #
#-----------------------------#
# GUILD_TRIGGER = 'Bloom Studio'
# COLOR_CHANGING_ROLE = 'bloom-visual'
# COMMAND_TRIGGERS = ['!']

#-----------------------------# 
#
#    @property
#    def __general_channel(self):
#        for guild in self.guilds:
#            if guild.name.startswith(GUILD_TRIGGER):
#                for channel in guild.channels:
#                    if "home" in channel.name:
#                        return channel
#        return None

import json
import os
from datetime import datetime
from pytz import timezone

# Get the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Construct the path to the contributors.json file
json_file_path = os.path.join(script_dir, 'contributors.json')

# Load contributors and emoji ID mapping from contributors.json
with open(json_file_path, 'r') as json_file:
    data = json.load(json_file)
    contributors = data["contributors"]

emoji_id_mapping = {emoji: contributor for emoji, contributor in data["emojiIdMapping"].items()}

def add_contributor(uid, emoji_id):    
    new_contributor = {"uid": uid}
    contributors.append(new_contributor)
    emoji_id_mapping[emoji_id] = uid  # Use the UID directly as the value in emoji_id_mapping
    update_json_file()
    return new_contributor
    
async def send_dm_once(bot, contributor, message_link):
    user = await bot.fetch_user(int(contributor["uid"]))
    if user:
        dm_message = f"Hello {user.name}! You have been mentioned in this message! {message_link}"
        await user.send(dm_message)

def update_json_file():
    with open(json_file_path, 'w') as json_file:
        json.dump({"contributors": contributors or [], "emojiIdMapping": emoji_id_mapping or {}}, json_file)
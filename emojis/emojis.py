import asyncio
import json
from datetime import datetime
from pytz import timezone

# Load contributors and emoji ID mapping from contributors.json
with open('contributors.json', 'r') as json_file:
    data = json.load(json_file)
    contributors = data["contributors"]

emoji_id_mapping = {emoji: contributor for emoji, contributor in data["emojiIdMapping"].items()}

def add_contributor(name, uid, emoji_id):    
    new_contributor = {"name": name, "uid": uid}
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
    with open('contributors.json', 'w') as json_file:
        json.dump({"contributors": contributors or [], "emojiIdMapping": emoji_id_mapping or {}}, json_file)

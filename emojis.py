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

def remove_contributor(uid):
    for contributor in contributors:
        if contributor["uid"] == uid:
            emoji_id_to_remove = next((emoji_id for emoji_id, c in emoji_id_mapping.items() if c == contributor), None)
            if emoji_id_to_remove:
                del emoji_id_mapping[emoji_id_to_remove]
            contributors.remove(contributor)
            update_json_file()
            return contributor

def process_remove_contributor_command(message_content):
    uid_to_remove = message_content.split()[1] if len(message_content.split()) > 1 else None
    if uid_to_remove:
        removed_contributor = remove_contributor(uid_to_remove)
        if removed_contributor:
            print(f"Contributor {removed_contributor['name']} removed successfully!")
            return f"Contributor {removed_contributor['name']} removed successfully!"
        else:
            return "Contributor not found."
    else:
        return "Please provide the UID of the contributor to remove."

async def send_dm_once(bot, contributor, message_link):
    user = await bot.fetch_user(int(contributor["uid"]))
    if user:
        dm_message = f"Hello {user.name}! You have been mentioned in this message! {message_link}"
        await user.send(dm_message)

def update_json_file():
    with open('contributors.json', 'w') as json_file:
        json.dump({"contributors": contributors or [], "emojiIdMapping": emoji_id_mapping or {}}, json_file)

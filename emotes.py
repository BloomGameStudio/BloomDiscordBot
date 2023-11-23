##If a contributors emoji is detected in chat, react and ping that user every 4 hrs
##Static assignment for initial run
##Functions exist to add, or remove contributors.
import asyncio
from datetime import datetime
from pytz import timezone

class Contributor:
    def __init__(self, name, uid, utc_start_time, utc_end_time):
        self.name = name
        self.uid = uid
        self.actioned = False
        self.utc_start_time = utc_start_time
        self.utc_end_time = utc_end_time

#Using UTC times found in:
#https://www.notion.so/bloomgame/38b4e7b631d94dcc969c421742ca76b1?v=5ea223e5b2ec4bf6a1ef58c22a9d3b1c

contributors = [
    Contributor("Sarahtonein", "316765092689608706", 21, 5),
    Contributor("Lapras", "395761182939807744", 15, 5),
    Contributor("Balu", "353572599957291010", 11, 23),
    Contributor("Pizzacat", "303732860265693185", 14, 2),
    Contributor("Spaghetto", "406302927884386318", 14, 2),
  # Contributor("Lilgumbo", "368617749041381388", 0, 0),
    Contributor("Baguette", "548974112131776522", 12, 22),
  # Contributor("Bagelface", "856041684588167188", 1, 5),
    Contributor("Breeze", "154033306894073856", 15, 5),
  # Contributor("Ploxx95", "406073034160472066", 1, 5)
]

emoji_id_mapping = {
    "<:sarah:1176399164154851368>": contributors[0],
    "<:lap:1110862059647795240>": contributors[1],
    "<:balu:1110862230343397387>": contributors[2],
    "<:pizzacat:1110862947145760939>": contributors[3],
    "<:spag:1110866508017586187>": contributors[4],
   # "<:gumbo:1145946572589383731>": contributors[5],
    "<:baguette:1113326206947954849>": contributors[5],
   # "<:bagelface:1148723908556632205>": contributors[7],
    "<:breeze:1113744843575922708>": contributors[6]
   # "<:ploxx:1154103719496003709>": contributors[9]
}

async def send_dm_periodically(bot, contributor, message_link):
    user = await bot.fetch_user(int(contributor.uid))
    if user:
        if is_valid_time(contributor):  # Pass the contributor object
            dm_message = f"Hello {user.name}! You have been mentioned in this message! {message_link}\nReminder: Please respond with !actioned to stop the message"
            await user.send(dm_message)
            while not contributor.actioned and is_valid_time(contributor):  # Check waking hours before sending the next reminder
                await asyncio.sleep(60 * 60 * 4)  # Wait for 4 hours before sending the next reminder

def add_contributor(name, uid, emoji_id, start_time, end_time):
    new_contributor = Contributor(name, uid, int(start_time), int(end_time))
    contributors.append(new_contributor)
    emoji_id_mapping[emoji_id] = new_contributor
    return new_contributor

def remove_contributor(uid):
    for contributor in contributors:
        if contributor.uid == uid:
            emoji_id_to_remove = next((emoji_id for emoji_id, c in emoji_id_mapping.items() if c == contributor), None)
            if emoji_id_to_remove:
                del emoji_id_mapping[emoji_id_to_remove]
            contributors.remove(contributor)
            return contributor
    return None

def is_valid_time(contributor):
    now = datetime.utcnow()
    current_hour = now.hour

    if contributor.utc_start_time <= contributor.utc_end_time:
        # Working hours are within a single day
        return contributor.utc_start_time <= current_hour <= contributor.utc_end_time
    else:
        # Working hours span across two days
        return current_hour >= contributor.utc_start_time or current_hour <= contributor.utc_end_time

def get_contributor_by_uid(uid):
    for contributor in emoji_id_mapping.values():
        if contributor.uid == uid:
            return contributor
    return None

def process_remove_contributor_command(message_content):
    uid_to_remove = message_content.split()[1] if len(message_content.split()) > 1 else None
    if uid_to_remove:
        removed_contributor = remove_contributor(uid_to_remove)
        if removed_contributor:
            print(f'Removed contributor', {removed_contributor.name}, {removed_contributor.uid})
            return f"Contributor {removed_contributor.name} removed successfully!"
        else:
            return "Contributor not found."
    else:
        return "Please provide the UID of the contributor to remove."

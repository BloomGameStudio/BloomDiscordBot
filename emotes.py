##If a contributors emoji is detected in chat, react and ping that user every 4 hrs

#ToDO:
##Add and Remove contributors
##Only ping during waking hours

##Note:
##Statically defining contributors is not ideal and there should be functionality
##to add and remove contributors as required based off uid for example

class Contributor:
    def __init__(self, name, uid, utc_start_time, utc_end_time):
        self.name = name
        self.uid = uid
        self.actioned = False
        self.utc_start_time = utc_start_time
        self.utc_end_time = utc_end_time

# Example usage:
contributor1 = Contributor("Sarah", "316765092689608706", 1, 5)

# Map Emoji_ID to Contributor:
emoji_id_mapping = {
    "<:sarah:1176399164154851368>": contributor1,
    # Add more entries as needed
}

from tortoise import Tortoise, run_async
import asyncio

from contributor import Contributor

"""
Setup.py is the main schema generation tool for the initial database setup.
This can be run one time to generate the initial schema.
"""
async def init(make_contributors):
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={
            'models': [
                'contributor_mention',             
                'contributor',
                'proposal',
                'proposal_vote',
                'scheduled_event'
            ]
        }
    )

    print("Generating schema...")
    await Tortoise.generate_schemas()

    if make_contributors:
        print("Making test contributors...")
        await init_contributors()

    print("Setup is done.")
    quit()
    

"""
Initializes the base contributor data that existed.
"""
async def init_contributors():
    await Contributor.create(member_id=353572599957291010,user_note="balu",guild_id=0,emoji_id=1110862230343397387,emoji_string="<:balu:1110862230343397387>")
    await Contributor.create(member_id=368617749041381388,user_note="gumbo",guild_id=0,emoji_id=1145946572589383731,emoji_string="<:gumbo:1145946572589383731>")
    await Contributor.create(member_id=303732860265693185,user_note="pizzacat",guild_id=0,emoji_id=1110862947145760939,emoji_string="<:pizzacat:1110862947145760939>")
    await Contributor.create(member_id=406302927884386318,user_note="spag",guild_id=0,emoji_id=1110866508017586187,emoji_string="<:spag:1110866508017586187>")
    await Contributor.create(member_id=548974112131776522,user_note="baguette",guild_id=0,emoji_id=1113326206947954849,emoji_string="<:baguette:1113326206947954849>")
    await Contributor.create(member_id=154033306894073856,user_note="breeze",guild_id=0,emoji_id=1113744843575922708,emoji_string="<:breeze:1113744843575922708>")
    await Contributor.create(member_id=316765092689608706,user_note="sarah",guild_id=0,emoji_id=1176399164154851368,emoji_string="<:sarah:1176399164154851368>")
    await Contributor.create(member_id=395761182939807744,user_note="lap",guild_id=0,emoji_id=1110862059647795240,emoji_string="<:lap:1110862059647795240>")
    await Contributor.create(member_id=287763415051665408,user_note="rod",guild_id=0,emoji_id=1191872082708013177,emoji_string="<a:rod:1191872082708013177>")
    await Contributor.create(member_id=856041684588167188,user_note="bagelface",guild_id=0,emoji_id=1148723908556632205,emoji_string="<:bagelface:1148723908556632205>")
    await Contributor.create(member_id=455131439906947072,user_note="monkeydluffy",guild_id=0,emoji_id=1115774904474816584,emoji_string="<:monkeydluffy:1115774904474816584>")
    await Contributor.create(member_id=675025391244673031,user_note="friedplant",guild_id=0,emoji_id=1192178028479004702,emoji_string="<:friedplant:1192178028479004702>")
    await Contributor.create(member_id=543409917306863626,user_note="balagio",guild_id=0,emoji_id=1128026645798846575,emoji_string="<:balagio:1128026645798846575>")
    await Contributor.create(member_id=395631657962569738,user_note="pete",guild_id=0,emoji_id=1145946537231392858,emoji_string="<:pete:1145946537231392858>")
    await Contributor.create(member_id=406073034160472066,user_note="ploxx",guild_id=0,emoji_id=1154103719496003709,emoji_string="<:ploxx:1154103719496003709>")

asyncio.run(init(True))
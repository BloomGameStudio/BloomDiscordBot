from tortoise.models import Model
from tortoise import fields 
from tortoise.contrib.pydantic import pydantic_model_creator

from enum import Enum, IntEnum

"""
Contributor is the part of the domain model that allows for the tracking
of all relevant contributor users and their meta-data. It also allows the
us to tie in all mention events through a many-to-one relationship with
contributor.
"""
class Contributor(Model):
    id = fields.IntField(pk=True)

    # Discord member_id to be used as a foreign key.
    member_id = fields.BigIntField()

    # Discord guild_id of the user (currently unused possibly unneeded)
    guild_id = fields.BigIntField()

    # id of the emoji.
    emoji_id = fields.BigIntField()

    # full emoji string of the emoji which translates to the full emoji in discord.
    emoji_string = fields.TextField()

    # notes about the user.
    user_note = fields.TextField(null=True)
    #mentions = fields.ForeignKeyField('models.ContributorMention', related_name='contributor')
    created_on = fields.DatetimeField(auto_now_add=True)
    active = fields.BooleanField(default=True)
    
    def __str__(self):
        return f"Contributor{tuple([self.id, self.member_id, self.guild_id])}"
    
    class PydanticMeta:
        computed = []
        exclude = []

Contributor_Pydantic = pydantic_model_creator(Contributor, name="Contributor")
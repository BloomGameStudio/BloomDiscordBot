from tortoise.models import Model
from tortoise import fields 
from tortoise.contrib.pydantic import pydantic_model_creator

from enum import Enum, IntEnum

class Contributor(Model):
    id = fields.IntField(pk=True)
    member_id = fields.BigIntField()
    guild_id = fields.BigIntField()
    emoji_id = fields.BigIntField()
    emoji_string = fields.TextField()
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
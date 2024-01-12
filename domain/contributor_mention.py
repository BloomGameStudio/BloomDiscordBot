from tortoise.models import Model
from tortoise import fields 
from tortoise.contrib.pydantic import pydantic_model_creator

from enum import Enum, IntEnum

class ContributorMention(Model):
    id = fields.IntField(pk=True)
    channel_id = fields.BigIntField()
    message_id = fields.BigIntField()
    member_id = fields.BigIntField()
    is_reaction = fields.BooleanField(default=False)
    contributor = fields.ForeignKeyField('models.Contributor', related_name='mentions')
    created_on = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"ContributorMention{tuple([self.id, self.message_id, self.member_id, self.is_reaction])}"

    class PydanticMeta:
        computed = []
        exclude = []

ContributorMention_Pydantic = pydantic_model_creator(ContributorMention, name="ContributorMention")
from tortoise.models import Model
from tortoise import fields 
from tortoise.contrib.pydantic import pydantic_model_creator

from enum import Enum, IntEnum

"""
ProposalVote is currently unused and is a place-holder for publish votes.
"""
class ProposalVote(Model):
    id = fields.IntField(pk=True)
    member_id = fields.BigIntField()
    emoji_string = fields.TextField()
    proposal = fields.ForeignKeyField('models.Proposal', related_name='votes')

    def __str__(self):
        return f"ProposalVote{tuple([self.id, self.member_id, self.emoji_string])}"
    
    class PydanticMeta:
        computed = []
        exclude = []

ProposalVote_Pydantic = pydantic_model_creator(ProposalVote, name="ProposalVote")
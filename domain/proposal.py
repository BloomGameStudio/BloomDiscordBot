from tortoise.models import Model
from tortoise import fields 
from tortoise.contrib.pydantic import pydantic_model_creator

from enum import Enum, IntEnum

class Proposal(Model):
    id = fields.IntField(pk=True)
    message_id = fields.BigIntField(null=True) # only not None if published.
    member_id = fields.BigIntField()
    title = fields.TextField()
    proposal_type = fields.TextField(null=True)
    abstract = fields.TextField(null=True)
    background = fields.TextField(null=True)
    created_on = fields.DatetimeField(auto_now_add=True)
    draft = fields.BooleanField(default=True)
    #votes = fields.ForeignKeyField('models.ProposalVote', related_name='proposal')
    
    def __str__(self):
        return f"""
            __**#{self.id} - {self.title}**__
            *by <@{self.member_id}>*

            > ***{self.proposal_type}***

            __**Abstract**__
            {self.abstract}

            **__Background__**
            {self.background}
        """
    
    class PydanticMeta:
        computed = []
        exclude = []

Proposal_Pydantic = pydantic_model_creator(Proposal, name="Proposal")
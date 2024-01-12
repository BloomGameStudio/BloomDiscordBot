from tortoise.models import Model
from tortoise import fields 
from tortoise.contrib.pydantic import pydantic_model_creator

from enum import Enum, IntEnum

class ScheduledEvent(Model):
    id = fields.IntField(pk=True)
    guild_id = fields.BigIntField()
    channel_id = fields.BigIntField()
    name = fields.TextField()
    description = fields.TextField()
    creator = fields.IntField()
    url = fields.TextField()
    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField()
    status = fields.TextField()
    user_count = fields.IntField()
    created_on = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"""
            __**#{id} - {self.name}**__
            *by <@{self.creator}>*

            > ***{self.description}***

            __**URL**__
            {self.url}

            **__Start/End__**
            {self.start_time}
            {self.end_time}
        """
    
    class PydanticMeta:
        computed = []
        exclude = []

ScheduledEvent_Pydantic = pydantic_model_creator(ScheduledEvent, name="ScheduledEvent")
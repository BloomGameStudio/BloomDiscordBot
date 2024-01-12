
from fastapi import FastAPI
from typing import List
from domain.contributor import Contributor, Contributor_Pydantic
from domain.contributor_mention import ContributorMention, ContributorMention_Pydantic
from domain.proposal import Proposal, Proposal_Pydantic
from domain.proposal_vote import ProposalVote, ProposalVote_Pydantic
from domain.scheduled_event import ScheduledEvent, ScheduledEvent_Pydantic

from pydantic import BaseModel

from tortoise.contrib.fastapi import register_tortoise

import uvicorn

import threading


# Proposal Votes (not implemented yet)

# Events (not implemented yet)

async def init_db_api():
    app = FastAPI(title="Bloom Bot Middleware Layer")

    class Status(BaseModel):
        message: str

    @app.get("/contributors", response_model=List[Contributor_Pydantic])
    async def get_contributors():
        return await Contributor_Pydantic.from_queryset(Contributor.all())

    @app.get("/contributors/{contributor_id}", response_model=List[Contributor_Pydantic])
    async def get_contributor(contributor_id: int):
        return await Contributor_Pydantic.from_queryset(Contributor.filter(id=contributor_id))

    @app.get("/contributors/{contributor_id}/mentions", response_model=List[ContributorMention_Pydantic])
    async def get_contributor_mentions_by_contributor(contributor_id: int):
        return await ContributorMention_Pydantic.from_queryset(
            ContributorMention.filter(contributor_id=contributor_id)
        )

    @app.get("/contributor_mentions", response_model=List[ContributorMention_Pydantic])
    async def get_contributor_mentions():
        return await ContributorMention_Pydantic.from_queryset(
            ContributorMention.all()
        )

    @app.get("/proposals", response_model=List[Proposal_Pydantic])
    async def get_proposals():
        return await Proposal_Pydantic.from_queryset(
            Proposal.all()
        )
    
    register_tortoise(
        app,
        db_url='sqlite://db.sqlite3',
        modules={
            'models': [
                'domain.contributor',
                'domain.contributor_mention',
                'domain.proposal_vote',
                'domain.proposal',
                'domain.scheduled_event'
            ]
        },
        add_exception_handlers=True
    )

    threading.Thread(target=uvicorn.run, args=(app,)).start()

    
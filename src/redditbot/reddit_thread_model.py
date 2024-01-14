# no dont do this!! from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING, Dict

from asyncpraw.models import Submission
from pydantic import field_validator
from sqlalchemy import Column
from sqlmodel import Field, JSON, SQLModel

if TYPE_CHECKING:
    ...


def submission_to_dict(submission: Submission):
    serializable_types = (int, float, str, bool, type(None))
    if isinstance(submission, Submission):
        submission = vars(submission)
    return {k: v for k, v in submission.items() if isinstance(v, serializable_types)}


class RedditThreadBase(SQLModel):
    # class Config:
    #     arbitrary_types_allowed = True

    reddit_id: str = Field(index=True, unique=True)
    title: str
    shortlink: str
    created_datetime: datetime
    submission: Dict = Field(default=None, sa_column=Column(JSON))
    # submission: Submission | dict = Field(sa_column=Column(JSON))

    @field_validator("submission", mode="before")
    def validate_submission(cls, v):
        return submission_to_dict(v)

    @classmethod
    def from_submission(cls, submission: Submission):
        tdict = dict(
            reddit_id=submission.id,
            title=submission.title,
            shortlink=submission.shortlink,
            created_datetime=submission.created_utc,
            submission=submission,
        )
        return cls.model_validate(tdict)

    @property
    def slug(self):
        return f"/red/{self.id}"

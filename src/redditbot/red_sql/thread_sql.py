from datetime import datetime
from typing import Optional, List, Dict
from pawsupport.misc_ps import obj_to_dict

from asyncpraw.models import Submission

try:
    from pydantic import field_validator
    from sqlalchemy import Column, JSON
    from sqlmodel import Field, Relationship, SQLModel
except ImportError as e:
    if "partially initialized module" not in str(e):
        e = f"sqlmodel optional dependency is not installed - {e}"
    raise ImportError(e)
from redditbot.red_sql.tag import Tag
from redditbot.red_sql.link import TagLink


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
        return obj_to_dict(v)

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


class RedditThread(RedditThreadBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tags: List["Tag"] = Relationship(back_populates="reddit_threads", link_model=TagLink)

from typing import Optional

from sqlmodel import SQLModel, Field


class TagLink(SQLModel, table=True):
    reddit_thread_id: Optional[int] = Field(default=None, foreign_key="redditthread.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)

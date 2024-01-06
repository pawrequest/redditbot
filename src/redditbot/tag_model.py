from typing import Optional, List, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from redditbot import RedditThread


class TagLink(SQLModel, table=True):
    reddit_thread_id: Optional[int] = Field(default=None, foreign_key="redditthread.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)


class TagBase(SQLModel):
    name: str = Field(default=None)


class Tag(TagBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # parents: List["Parent"] = Relationship(back_populates="tags", link_model=TagLink)
    reddit_threads: List["RedditThread"] = Relationship(back_populates="tags", link_model=TagLink)

from typing import Optional, List

from sqlmodel import Field, Relationship

from redditbot.reddit_thread_model import RedditThreadBase
from redditbot.tag_model import Tag, TagLink


class RedditThread(RedditThreadBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tags: List["Tag"] = Relationship(back_populates="reddit_threads", link_model=TagLink)

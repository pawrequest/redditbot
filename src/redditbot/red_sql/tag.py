from typing import List, Optional, TYPE_CHECKING

from .link import TagLink

try:
    from sqlmodel import SQLModel, Field, Relationship
except ImportError as e:
    if "partially initialized module" not in str(e):
        e = f"sqlmodel optional dependency is not installed - {e}"
    raise ImportError(e)

if TYPE_CHECKING:
    from .thread_sql import RedditThread


class TagBase(SQLModel):
    name: str = Field(default=None)


class Tag(TagBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    reddit_threads: List["RedditThread"] = Relationship(back_populates="tags", link_model=TagLink)

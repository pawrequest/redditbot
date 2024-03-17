from __future__ import annotations

from asyncpraw.models import Subreddit, WikiPage
from asyncpraw.reddit import Submission
from loguru import logger
import typing as _t


class Writer(_t.Protocol):
    def write_many(self, content: _t.Sequence = None) -> str:
        ...

    def write_one(self, content=None) -> str:
        ...

class Poster:
    def __init__(
        self,
        subreddit: Subreddit,
        post_writer: Writer,
        wiki_writer: Writer,
        wiki: WikiPage,
    ):
        self.subreddit_ = subreddit
        self.wiki = wiki
        self.post_writer = post_writer
        self.wiki_writer = wiki_writer

    async def update_wiki(self, markup):
        """Update wiki page with episodes."""
        await self.wiki.edit(content=markup)

    async def submit_subreddit_post(self, title: str, text: str) -> Submission:
        try:
            submission: Submission = await self.subreddit_.submit(title, selftext=text)
            logger.info(f"Submitted {title} to {self.subreddit_.display_name}: {submission.shortlink}")

            return submission
        except Exception as e:
            logger.error(f"Error submitting episode: {e}")

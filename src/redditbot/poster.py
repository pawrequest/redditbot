from __future__ import annotations

import os
from typing import Protocol, Sequence

from aiohttp import ClientSession
from asyncpraw.models import Subreddit, WikiPage
from asyncpraw.reddit import Submission
from sqlmodel import Session
from loguru import logger


class Writer(Protocol):
    def write_many(self, content: Sequence = None) -> str:
        ...

    def write_one(self, content=None) -> str:
        ...


class Poster:
    def __init__(
        self,
        session: Session,
        aio_session: ClientSession,
        subreddit: Subreddit,
        post_writer: Writer,
        wiki_writer: Writer,
        wiki: WikiPage,
    ):
        # self.session = session
        # self.aio_session = aio_session
        self.subreddit_ = subreddit
        self.wiki = wiki
        self.post_writer = post_writer
        self.wiki_writer = wiki_writer

    # @classmethod
    # async def from_config(cls, session: Session, aio_session: ClientSession, subreddit: Subreddit) -> Poster:
    #     wiki = await subreddit.wiki.get_page(WIKI_TO_WRITE)
    #     return cls(session, aio_session, subreddit, subreddit, wiki)

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

""" Monitors a subreddit.stream.submissions for new threads with guru_names in titles, adds to the db with Guru relationships
"""
from __future__ import annotations

from asyncio import Queue
from typing import AsyncGenerator

from asyncpraw.models import Submission, Subreddit
from loguru import logger


class SubredditMonitor:
    """Monitors a subreddit for new threads with guru tags and adds them to the database"""

    def __init__(self, subreddit: Subreddit):
        self.subreddit = subreddit

    async def generate_subs(self) -> AsyncGenerator[Submission, None]:
        """Infinite async coordinating submission stream"""
        logger.info(
            f"Initialised Generator for http://reddit.com/r/{self.subreddit.display_name}",
        )
        async for sub in self.subreddit.stream.submissions(skip_existing=False):
            sub: Submission = sub
            yield sub

    async def queue_subs(self, queue: Queue) -> None:
        """Infinite async coordinating submission stream"""
        logger.info(
            f"Initialised Submission Queuer for  http://reddit.com/r/{self.subreddit.display_name}",
        )

        async for sub in self.subreddit.stream.submissions(skip_existing=False):
            await queue.put(sub)

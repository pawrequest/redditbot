""" Monitors a subreddit.stream.submissions for new threads with guru_names in titles, adds to the db with Guru relationships
"""
from __future__ import annotations

import sys
from asyncio import Queue
from typing import AsyncGenerator, Type, TypeVar

from asyncpraw.models import Submission, Subreddit
from loguru import logger
from pawdantic.pawsql import sqlpr

from sqlmodel import SQLModel, Session, select


# global to allow defining models in client app, else fallback to RedditThread in this package for standalone
# must be a better way but many import errors and table collisions were had and this seems to work
THREAD_TYPE: Type[SQLModel]


TAG_TYPE = TypeVar("TAG_TYPE", bound=Type[SQLModel])
LINK_TYPE = TypeVar("LINK_TYPE", bound=Type[SQLModel])


def set_thread_type(thread_db_type: type[SQLModel] = None):
    global THREAD_TYPE
    if thread_db_type is None:
        logger.warning("No thread_db_type passed, using redditbot.red_sql.red_thread_sql.RedditThread")
        from redditbot.red_sql.thread_sql import RedditThread

        thread_db_type = RedditThread
    THREAD_TYPE = thread_db_type


class SubredditMonitorSQL:
    """Monitors a subreddit for new threads with guru tags and adds them to the database"""

    def __init__(self, session: Session, subreddit: Subreddit, thread_db_type: type[SQLModel] = None):
        self.subreddit = subreddit
        self.session = session
        set_thread_type(thread_db_type)

    async def run_q2(self, queue: Queue) -> None:
        """Infinite async coordinating submission stream"""
        logger.info(
            f"Initialised - watching  http://reddit.com/r/{self.subreddit.display_name}",
        )

        sub_stream = self.subreddit.stream.submissions(skip_existing=False)
        async for sub in self.filter_existing_submissions(sub_stream):
            sub = THREAD_TYPE.from_submission(sub)
            await queue.put(sub)

    async def filter_existing_submissions(
        self, sub_stream: AsyncGenerator[Submission, None]
    ) -> AsyncGenerator[THREAD_TYPE, None]:
        """Yields Submissions not already in db"""
        async for submission in sub_stream:
            thread = THREAD_TYPE.from_submission(submission)
            if not obj_in_session(self.session, thread, THREAD_TYPE):
                yield thread

    def submission_exists(self, submission: Submission) -> bool:
        """Checks if a Submission ID is already in the database of RedditThreads"""
        existing_thread = self.session.exec(select(THREAD_TYPE).where((THREAD_TYPE.reddit_id == submission.id))).first()
        return existing_thread is not None

""" Monitors a subreddit.stream.submissions for new threads with guru_names in titles, adds to the db with Guru relationships
"""
from __future__ import annotations

from asyncio import Queue
from typing import AsyncGenerator, Type, TypeVar

from asyncpraw.models import Submission, Subreddit
from sqlmodel import SQLModel, Session, select
from loguru import logger

# global to allow extending threadbase in client app, else fallback to RedditThread in this package for standalone
# must be a better way but many import errors and table collisions were had and this seems to work
THREAD_TYPE: Type[SQLModel]


async def is_match(model_inst_with_name, submission):
    return model_inst_with_name.name.lower() in submission.title.lower()


TAG_TYPE = TypeVar("TAG_TYPE", bound=Type[SQLModel])
LINK_TYPE = TypeVar("LINK_TYPE", bound=Type[SQLModel])


def set_thread_type(thread_db_type: type[SQLModel] = None):
    global THREAD_TYPE
    if thread_db_type is None:
        from .reddit_thread_db_model import RedditThread

        thread_db_type = RedditThread
    THREAD_TYPE = thread_db_type


class SubredditMonitor:
    """Monitors a subreddit for new threads with guru tags and adds them to the database"""

    def __init__[TAG_TYPE](self, session: Session, subreddit: Subreddit, thread_db_type: type[SQLModel] = None):
        self.subreddit = subreddit
        self.session = session
        # self.match_model = match_model
        set_thread_type(thread_db_type)

        # try:
        #     match_model.reddit_threads
        # except AttributeError:
        #     raise AttributeError(f"{match_model} does not have reddit threads attr")

    # async def run_q(self, queue: Queue) -> None:
    #     """Infinite async coordinating submission stream"""
    #     logger.info(
    #         f"Initialised - watching  http://reddit.com/r/{self.subreddit.display_name}",
    #     )
    #
    #     sub_stream = self.subreddit.stream.submissions(skip_existing=False)
    #     async for sub in self.filter_existing_submissions(sub_stream):
    #         if matches := await self.get_matches(sub):
    #             thread = await submission_to_thread(sub)
    #             for match in matches:
    #                 match.reddit_threads.append(thread)
    #             self.session.add(thread)
    #             self.session.commit()
    #             self.session.refresh(thread)
    #             await queue.put(thread)

    async def run_q2(self, queue: Queue) -> None:
        """Infinite async coordinating submission stream"""
        logger.info(
            f"Initialised - watching  http://reddit.com/r/{self.subreddit.display_name}",
        )

        sub_stream = self.subreddit.stream.submissions(skip_existing=False)
        async for sub in self.filter_existing_submissions(sub_stream):
            await queue.put(sub)
            # if matches := await self.get_matches(sub):
            #     thread = await submission_to_thread(sub)
            #     for match in matches:
            #         match.reddit_threads.append(thread)
            #     self.session.add(thread)
            #     self.session.commit()
            #     self.session.refresh(thread)

    async def filter_existing_submissions(
        self, sub_stream: AsyncGenerator[Submission, None]
    ) -> AsyncGenerator[Submission, None]:
        """Yields Submissions not already in db"""
        async for submission in sub_stream:
            if not self.submission_exists(submission):
                yield submission

    # async def get_matches(self, submission: Submission) -> list[SQLModel]:
    #     # todo cache
    #     tag_models = self.session.exec(select(self.match_model)).all()
    #     matched_tag_models = [_ for _ in tag_models if await is_match(_, submission)]
    #     return matched_tag_models

    def submission_exists(self, submission: Submission) -> bool:
        """Checks if a Submission ID is already in the database of RedditThreads"""
        existing_thread = self.session.exec(select(THREAD_TYPE).where((THREAD_TYPE.reddit_id == submission.id))).first()
        return existing_thread is not None

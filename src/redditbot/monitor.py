""" Monitors a subreddit.stream.submissions for new threads with guru_names in titles, adds to the db with Guru relationships
"""
from __future__ import annotations

import os
from typing import AsyncGenerator, Type, TypeVar

from asyncpraw.models import Submission, Subreddit
from sqlmodel import SQLModel, Session, select
from loguru import logger

from redditbot import RedditThread


def param_or_env(env_key: str, value: str | None, none_is_false=False) -> str | bool:
    value = value or os.environ.get(env_key)
    if value is None:
        if none_is_false:
            return False
        raise ValueError(f"{env_key} was not provided and is not an environment variable")

    return value


async def is_match(model_inst_with_name, submission):
    return model_inst_with_name.name.lower() in submission.title.lower()


TAG_TYPE = TypeVar("TAG_TYPE", bound=Type[SQLModel])
LINK_TYPE = TypeVar("LINK_TYPE", bound=Type[SQLModel])


class SubredditMonitor:
    """Monitors a subreddit for new threads with guru tags and adds them to the database"""

    def __init__[TAG_TYPE, LINK_TYPE](self, session: Session, match_model: Type[TAG_TYPE], subreddit: Subreddit):
        self.subreddit = subreddit
        self.session = session
        self.match_model = match_model

        # try:
        #     match_model.reddit_threads
        # except AttributeError:
        #     raise AttributeError(f"{match_model} does not have reddit threads attr")

    async def run(self, do_flair: bool = None) -> None:
        """Infinite async coordinating submission stream"""
        logger.info(
            f"Initialised - watching  http://reddit.com/r/{self.subreddit.display_name}",
        )

        sub_stream = self.subreddit.stream.submissions(skip_existing=False)
        async for sub in self.filter_existing_submissions(sub_stream):
            if matches := await self.get_matches(sub):
                thread = await submission_to_thread(sub)
                for match in matches:
                    match.reddit_threads.append(thread)
                self.session.add(thread)
                self.session.commit()
                self.session.refresh(thread)
                return

    # async def run1(self, do_flair: bool = None) -> None:
    #     """Infinite async coordinating submission stream"""
    #     logger.info(
    #         f"Initialised - watching  http://reddit.com/r/{self.subreddit.display_name}",
    #     )
    #
    #     sub_stream = self.subreddit.stream.submissions(skip_existing=False)
    #     async for sub in self.filter_existing_submissions(sub_stream):
    #         if matches_ := self.get_matches(sub):
    #             thread_ = await submission_to_thread(sub)
    #             for match in await matches_:
    #                 # yeah no
    #                 f"insert into {self.link_model.table_name} "
    #                 link = self.link_model(match.id, reddit_thread_id=thread_.id)
    #                 link = self.link_model(match, thread_)
    #                 self.session.add(link)
    #             self.session.commit()

    async def filter_existing_submissions(
        self, sub_stream: AsyncGenerator[Submission, None]
    ) -> AsyncGenerator[Submission, None]:
        """Yields Submissions not already in db"""
        async for submission in sub_stream:
            if not self.submission_exists(submission):
                yield submission

    async def get_matches(self, submission: Submission) -> list[SQLModel]:
        # todo cache
        tag_models = self.session.exec(select(self.match_model)).all()
        matched_tag_models = [_ for _ in tag_models if await is_match(_, submission)]
        return matched_tag_models

    def submission_exists(self, submission: Submission) -> bool:
        """Checks if a Submission ID is already in the database of RedditThreads"""
        existing_thread = self.session.exec(
            select(RedditThread).where((RedditThread.reddit_id == submission.id))
        ).first()
        return existing_thread is not None


async def submission_to_thread(submission: Submission) -> RedditThread:
    """Turns a Submission into a RedditThread for db insertion"""
    try:
        thread_ = RedditThread.from_submission(submission)
        return RedditThread.model_validate(thread_)
    except Exception as e:
        logger.error(f"Error Turning Submission into RedditThread {e}", bot_name="Monitor")

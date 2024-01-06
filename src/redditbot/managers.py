from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from asyncpraw.reddit import Reddit, Subreddit

from redditbot.monitor import param_or_env

if TYPE_CHECKING:
    pass


@asynccontextmanager
async def reddit_cm(client_id=None, client_sec=None, user_agent=None, redirect=None, reddit_token=None) -> Reddit:
    try:
        async with Reddit(
            client_id=param_or_env("REDDIT_CLIENT_ID", client_id),
            client_secret=param_or_env("REDDIT_CLIENT_SECRET", client_sec),
            user_agent=param_or_env("REDDIT_USER_AGENT", user_agent),
            redirect_uri=param_or_env("REDDIT_REDIRECT", redirect),
            refresh_token=param_or_env("REDDIT_TOKEN", reddit_token),
        ) as reddit:
            yield reddit
    finally:
        await reddit.close()


@asynccontextmanager
async def subreddit_cm(sub_name: str = None) -> Subreddit:
    sub_name = param_or_env("SUBREDDIT_NAME", sub_name)
    async with reddit_cm() as reddit:
        subreddit: Subreddit = await reddit.subreddit(sub_name)
        try:
            yield subreddit
        finally:
            await reddit.close()


# @asynccontextmanager
# async def wiki_page_cm(subreddit: Subreddit, page_name: str):
#     try:
#         wiki_page = await subreddit.wiki.get_page(page_name)
#         yield wiki_page
#     except Exception as e:
#         logger.error(f"error in wiki_page_cm: {e}")
#         raise e
#     finally:
#         ...

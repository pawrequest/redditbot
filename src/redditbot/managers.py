from __future__ import annotations

from contextlib import asynccontextmanager

from asyncpraw.reddit import Reddit, Subreddit

from suppawt import get_values


@asynccontextmanager
async def reddit_cm(client_id=None, client_sec=None, user_agent=None, redirect=None, reddit_token=None) -> Reddit:
    try:
        async with Reddit(
                client_id=get_values.param_or_env('REDDIT_CLIENT_ID', client_id),
                client_secret=get_values.param_or_env('REDDIT_CLIENT_SECRET', client_sec),
                user_agent=get_values.param_or_env('REDDIT_USER_AGENT', user_agent),
                redirect_uri=get_values.param_or_env('REDDIT_REDIRECT', redirect),
                refresh_token=get_values.param_or_env('REDDIT_TOKEN', reddit_token),
        ) as reddit:
            yield reddit
    finally:
        await reddit.close()


@asynccontextmanager
async def subreddit_cm(sub_name: str = None) -> Subreddit:
    sub_name = get_values.param_or_env('SUBREDDIT_NAME', sub_name)
    async with reddit_cm() as reddit:
        subreddit: Subreddit = await reddit.subreddit(sub_name)
        try:
            yield subreddit
        finally:
            await reddit.close()

import asyncio
from asyncio import Queue, create_task

import dotenv
import pytest_asyncio
import pytest
from asyncpraw.reddit import Subreddit, Submission

from redditbot import subreddit_cm
from redditbot.monitor import SubredditMonitor
from redditbot.thread import RedditThreadDC

dotenv.load_dotenv()


@pytest.mark.asyncio
async def test_sr_fxt():
    async with subreddit_cm("test") as subreddit:
        assert isinstance(subreddit, Subreddit)


@pytest_asyncio.fixture
async def monitor_fxt_dc(subreddit_fxt):
    yield SubredditMonitor(subreddit=subreddit_fxt)


@pytest.mark.asyncio
async def test_monitor_dc_fxt(monitor_fxt_dc):
    assert isinstance(monitor_fxt_dc, SubredditMonitor)


@pytest.mark.asyncio
async def test_monitor_generate_subs(monitor_fxt_dc):
    async for thread in monitor_fxt_dc.generate_subs():
        assert isinstance(thread, Submission)
        break


@pytest.mark.asyncio
async def test_monitor_queue_threads(monitor_fxt_dc):
    try:
        queue = Queue()
        task = create_task(monitor_fxt_dc.queue_subs(queue))
        while True:
            sub = await queue.get()
            assert isinstance(sub, Submission)
            break
        task.cancel()
        await task
    except asyncio.CancelledError:
        pass

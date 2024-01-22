import pytest
import pytest_asyncio

from redditbot import SubredditMonitorSQL
from redditbot.red_sql.thread_sql import RedditThread


@pytest.mark.asyncio
async def test_monitor_fxt_sql(monitor_fxt_sql):
    assert isinstance(monitor_fxt_sql, SubredditMonitorSQL)


@pytest.mark.asyncio
async def test_monitor_generate_threads_sql(monitor_fxt_sql):
    async for thread in monitor_fxt_sql.generate_threads():
        assert isinstance(thread, RedditThread)
        break

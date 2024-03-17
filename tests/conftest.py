import dotenv
import pytest_asyncio
from suppawt import session_fxt

from redditbot import SubredditMonitorSQL, subreddit_cm
from redditbot.monitor import SubredditMonitor

dotenv.load_dotenv()


@pytest_asyncio.fixture
async def subreddit_fxt():
    async with subreddit_cm("test") as subreddit:
        yield subreddit


@pytest_asyncio.fixture
async def monitor_fxt_dc(subreddit_fxt):
    yield SubredditMonitor(subreddit=subreddit_fxt)


@pytest_asyncio.fixture
async def monitor_fxt_sql(subreddit_fxt, session_fxt): # noqa F811 no pycharm it is not redefined
    yield SubredditMonitorSQL(session=session_fxt, subreddit=subreddit_fxt)

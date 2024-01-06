import dotenv
from redditbot.monitor import submission_to_thread
from sqlmodel import SQLModel, Session, create_engine
import pytest
from asyncpraw.reddit import Reddit, Subreddit

from redditbot import SubredditMonitor, RedditThread
from redditbot.managers import reddit_cm, subreddit_cm
from redditbot.tag_model import TagBase, Tag, TagLink

dotenv.load_dotenv()


@pytest.fixture(scope="function")
def test_engine(tmp_path):
    # Create a test engine, possibly using an in-memory database
    return create_engine(f"sqlite:///{tmp_path}/test.db")


@pytest.fixture(scope="function")
def test_session(test_engine):
    # Create a session for the test database
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session


@pytest.mark.asyncio
async def test_r():
    async with subreddit_cm() as subreddit:
        assert isinstance(subreddit, Subreddit)


@pytest.mark.asyncio
async def test_subreddit_monitor(test_session):
    async with subreddit_cm() as subreddit:
        mon = SubredditMonitor(session=test_session, match_model=Tag, link_model=TagLink, subreddit=subreddit)
        assert isinstance(mon, SubredditMonitor)


@pytest.mark.asyncio
async def test_filter_existing_submissions(test_session):
    test_session.add(Tag(name="Joe Rogan"))
    test_session.commit()

    async with subreddit_cm("test") as subreddit:
        mon = SubredditMonitor(session=test_session, match_model=Tag, subreddit=subreddit)
        sub_stream = mon.subreddit.stream.submissions(skip_existing=False)
        async for sub in mon.filter_existing_submissions(sub_stream):
            if matches := await mon.get_matches(sub):
                thread = await submission_to_thread(sub)
                assert isinstance(thread, RedditThread)
                for match in matches:
                    assert isinstance(match, Tag)
                    tds = match.reddit_threads
                    match.reddit_threads.append(thread)
                test_session.add(thread)
                test_session.commit()
                test_session.refresh(thread)
                assert isinstance(thread, RedditThread)
                return


def test_get_matches(subreddit_monitor):
    # Test the get_matches method
    # Provide a submission and check if it correctly identifies matching tags
    pass


def test_database_operations(subreddit_monitor):
    # Test database operations
    # Check if the correct entries are made in the database for new submissions and matches
    pass

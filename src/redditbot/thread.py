from dataclasses import dataclass
from datetime import datetime
from typing import Dict

from asyncpraw.models import Submission
from pawsupport.misc_ps import obj_to_dict

@dataclass
class RedditThreadDC:
    reddit_id: str
    title: str
    shortlink: str
    created_datetime: datetime
    submission: Submission

    def __post_init__(self):
        if isinstance(self.submission, Submission):
            self.submission = obj_to_dict(self.submission)
#
# @dataclass
# class RedditThreadDC:
#     reddit_id: str
#     title: str
#     shortlink: str
#     created_datetime: datetime
#     submission: Dict | Submission
#
#     def __post_init__(self):
#         if isinstance(self.submission, Submission):
#             self.submission = obj_to_dict(self.submission)

#
# @dataclass
# class RedditThreadDC:
#     reddit_id: str
#     title: str
#     shortlink: str
#     created_datetime: datetime
#     submission: Submission = None
#
#     @property
#     def submission(self):
#         return self._submission
#
#     @submission.setter
#     def submission(self, submission: Submission | Dict):
#         if isinstance(submission, Submission):
#             self._submission = obj_to_dict(submission)
#         else:
#             self._submission = submission


def thread_from_submission(thread_type, submission: Submission):
    return thread_type(
        reddit_id=submission.id,
        title=submission.title,
        shortlink=submission.shortlink,
        created_datetime=submission.created_utc,
        submission=submission,
    )

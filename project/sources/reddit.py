"""
Reddit source implementations.

"""
from __future__ import annotations
import abc
import logging
import os
from typing import Generator, TYPE_CHECKING

from project.models import Session
from project.result import Result
from project.sources.source import Source

import praw

if TYPE_CHECKING:
    from logging import Logger

    from praw.models.listing.generator import ListingGenerator
    from praw.models.subreddits import Subreddit
    from praw.models.reddit.submission import Submission


logger: Logger = logging.getLogger(__name__)
# initializes logging for reddit HTTP requests
logger.getChild("praw")
logger.getChild("prawcore")


class RedditSource(Source, abc.ABC):

    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_ID"),
        client_secret=os.getenv("REDDIT_SECRET"),
        user_agent="Mac OSX:membrain.data.project:v0.0.1 (by /u/dominictarro)",
    )

    def __init__(self, limit: int) -> None:
        super().__init__()
        self.limit: int = limit

    @abc.abstractmethod
    def subquery(self, subreddit: Subreddit) -> ListingGenerator:
        ...

    def extract(self) -> Generator[Result]:
        subreddit: Subreddit = self.reddit.subreddit("memes")
        for submission in self.subquery(subreddit):
            submission: Submission
            r: Result = Result(submission.url)
            r.set_meme_context_from_args('reddit', submission.shortlink)
            r.add_meme_text_from_args(submission.title, 'title', 1.0)
            yield r


class HotSource(RedditSource):

    def subquery(self, subreddit: Subreddit) -> ListingGenerator:
        return subreddit.hot(limit=self.limit)


class RisingSource(RedditSource):

    def subquery(self, subreddit: Subreddit) -> ListingGenerator:
        return subreddit.rising(limit=self.limit)


class TopSource(RedditSource):

    def subquery(self, subreddit: Subreddit) -> ListingGenerator:
        return subreddit.top(limit=self.limit)

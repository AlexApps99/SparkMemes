import enum
import random

# import praw
from models.meme import Meme


class RedditSort(enum.Enum):
    CONTROVERSIAL = "controversial"
    GILDED = "gilded"
    HOT = "hot"
    NEW = "new"
    RANDOM_RISING = "random_rising"
    RISING = "rising"
    TOP = "top"


class RedditTimeFilter(enum.Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    ALL = "all"


class Reddit:
    def __init__(self, praw_reddit):
        self.praw = praw_reddit

    def _download_submissions(self, subreddit, limit, sort, time_filter):
        if isinstance(subreddit, list):
            subreddit = "+".join(subreddit)
        if isinstance(time_filter, RedditTimeFilter):
            time_filter = time_filter.value

        sub = self.praw.subreddit(subreddit)
        if sort == RedditSort.CONTROVERSIAL:
            submissions = sub.controversial(time_filter, limit=limit)
        elif sort == RedditSort.GILDED:
            submissions = sub.gilded(limit=limit)
        elif sort == RedditSort.HOT:
            submissions = sub.hot(limit=limit)
        elif sort == RedditSort.NEW:
            submissions = sub.new(limit=limit)
        elif sort == RedditSort.RANDOM_RISING:
            submissions = sub.random_rising(limit=limit)
        elif sort == RedditSort.RISING:
            submissions = sub.rising(limit=limit)
        elif sort == RedditSort.TOP:
            submissions = sub.top(time_filter, limit=limit)
        else:
            return None

        return submissions

    @staticmethod
    def _filter_submissions_to_memes(submissions):
        # Make this much more customizable, as I will support text and video soon
        def filter_submission(s):
            if s.is_self:
                return False
            elif not hasattr(s, "preview"):
                return False
            elif not s.preview["enabled"]:
                return False
            elif "reddit_video_preview" in s.preview:
                return False
            elif "mp4" in s.preview["images"][0]["variants"]:
                return False
            elif "gif" in s.preview["images"][0]["variants"]:
                return False
            elif s.stickied:
                return False
            elif s.over_18:
                return False
            else:
                return True

        memes = [Meme.from_submission(s) for s in submissions if filter_submission(s)]

        random.shuffle(memes)

        return memes

    def download(
        self,
        subreddit,
        limit=100,
        sort=RedditSort.TOP,
        time_filter=RedditTimeFilter.DAY,
    ):
        s = self._download_submissions(subreddit, limit, sort, time_filter)
        m = self._filter_submissions_to_memes(s)
        return m

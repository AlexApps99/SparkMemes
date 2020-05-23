import argparse
from sparkmemes import *
import praw
from datetime import datetime, timedelta, timezone
from os import getenv


def main(subreddits, name, description, tags):
    intro = Transition(
        "res/intro/intro.png",
        "res/intro/intro.mp3",
        10,
        "Whatever could this be for???",
    )
    outro = Transition(
        "res/outro/outro.png",
        "res/outro/outro.mp3",
        20,
        "The end of this video\n(More to come very soon)",
    )
    memes = [m for m in Reddit(praw.Reddit()).download(subreddits, 75) if m.process()]

    vid = Video(intro, memes, outro, None)
    vid.prerender()
    vid.render()
    refr, client, secret = (
        getenv("YT_REFRESH_TOKEN"),
        getenv("YT_CLIENT_ID"),
        getenv("YT_CLIENT_SECRET"),
    )
    if refr is not None and client is not None and secret is not None:
        video = YouTube(refr, client, secret).upload(
            "video.mp4", name, args.description, args.tags
        )
        video.like()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "name",
        help="the name of the video, with every {} being replaced with the video number",
        type=str,
    )
    parser.add_argument(
        "offset",
        help="the number of days since 2020 that should set the version number",
        type=int,
    )
    parser.add_argument(
        "--subreddits",
        type=str,
        nargs="+",
        help="a list of subreddits to be compiled",
        default=["all"],
    )
    parser.add_argument(
        "--description",
        type=str,
        help="description (duh)",
        default="Like, subscribe and comment for 12 years of good luck\n\nMemes daily, SUBSCRIBE for more funny best memes compilation, clean memes, dank memes & tik tok memes of 2019.\ntik tok ironic memes compilation, family friendly pewdiepie memes, dog & cat reddit memes.",
    )
    parser.add_argument("--tags", type=str, nargs="+", help="tags (duh)")
    args = parser.parse_args()

    name = args.name.replace(
        "{}",
        str(
            (
                datetime.now(timezone.utc)
                - (
                    datetime(2020, 1, 1, tzinfo=timezone.utc)
                    + timedelta(days=args.offset)
                )
            ).days
        ),
    )
    main(args.subreddits, name, args.description, args.tags)

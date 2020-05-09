from sparkmemes import *
import praw


def main():
    intro = Transition(
        "res/intro/intro.png",
        "res/intro/intro.mp3",
        10,
        "Testing the\nrefactored version",
    )
    outro = Transition(
        "res/outro/outro.png",
        "res/outro/outro.mp3",
        20,
        "The end of this video\n(Please watch more)",
    )
    memes = [m for m in Reddit(praw.Reddit()).download("me_irl", 6) if m.process()]
    vid = Video(intro, memes, outro)
    vid.prerender()
    vid.render()


if __name__ == "__main__":
    main()

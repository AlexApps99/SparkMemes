from sparkmemes import *
import praw
from io import BytesIO


def main():
    print("WIP")
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
    memes = [
        m
        for m in Reddit(praw.Reddit()).download(
            "maliciouscompliance+choosingbeggars", 20
        )
        if m.process()
    ]
    concat_waves("tts.wav", [BytesIO(tts(m.tts_phrase())) for m in memes])

    vid = Video(intro, memes, outro)
    vid.prerender()
    vid.render()


if __name__ == "__main__":
    main()

# Intro/outro
# TODO make sure longer audio gets cut off
# support video transition as alternative (preferable really)

import ffmpeg

INTRO = {
    "background_path": "res/intro/intro.png",
    "audio_path": "res/intro/intro.mp3",
    "length": 10,
    "text": "A video by SparkMemes\n\nLike, subscribe, and comment...\nDon't forget to hit that bell!",
}

OUTRO = {
    "background_path": "res/outro/outro.png",
    "audio_path": "res/outro/outro.mp3",
    "length": 20,
    "text": "",
}


class Transition:
    def __init__(self, background_path, audio_path, length=10, text=""):
        if len(background_path) == 0:
            raise ValueError("A background path must be specified")
        else:
            self.background_path = background_path

        if len(audio_path) == 0:
            self.audio_path = None
        else:
            self.audio_path = audio_path

        if length > 0:
            self.length = length
        else:
            raise ValueError("Length must be greater than 0.")

        if text is None:
            self.text = ""
        else:
            self.text = text

    def to_ffmpeg_input(self, resolution):
        return (
            ffmpeg.input(self.background_path, loop="1", t=str(self.length))
            .filter("scale", **resolution)
            .drawtext(
                text=self.text,
                x="(w-tw)/2",
                y="(h-th)/2",
                fontcolor="white",
                fontfile="res/fonts/ObelixPro.ttf",
                fontsize="48",
            ),
            ffmpeg.input(self.audio_path).filter("atrim", duration=str(self.length)),
        )

from . import Meme, Subtitles
import ffmpeg
from os import remove

DEFAULT_CONFIG = {
    # Container: MP4
    "movflags": "+faststart",  # moov atom at the front of the file (Fast Start)
    # Audio codec: AAC-LC
    "c:a": "aac",  # AAC-LC
    "profile:a": "aac_low",  # AAC-LC
    "b:a": "384k",  # Recommended audio bitrate
    # Video codec: H.264
    "f": "mp4",
    "profile:v": "high",  # High Profile
    "bf": "2",  # 2 consecutive B frames
    "g": "15",  # Closed GOP, half of the frame rate
    "coder": "ac",  # CABAC
    "pix_fmt": "yuv420p",  # Chroma subsampling: 4:2:0
    # Framerate, Bitrate
    "r": "30",  # Framerate, naturally
    "map_metadata": "-1",
    "c:v": "libx264",  # H.264
    "crf": "20",  # Variable bitrate
    "tune": "stillimage",  # Optimize the filesize (rhyming)
    "preset": "veryfast",  # Speed up rendering a bit
}

DEFAULT_RESOLUTION = (1920, 1080)

QUIET = {"nostats": None, "hide_banner": None, "loglevel": "warning"}


class Video:
    def __init__(
        self,
        intro,
        memes,
        outro,
        image_delay=10,
        resolution=DEFAULT_RESOLUTION,
        config=DEFAULT_CONFIG,
    ):
        self.intro = intro
        self.memes = memes
        self.outro = outro
        self.image_delay = image_delay
        width, height = resolution
        self.resolution = {"w": str(width), "h": str(height)}
        self.config = config

        self.titles = None
        self.authors = None

    def gen_captions(self):
        self.titles = "titles.srt"
        Subtitles(
            [m.title for m in self.memes], self.image_delay, len(self.intro)
        ).save(self.titles)
        self.authors = "authors.srt"
        Subtitles(
            ["u/" + m.author for m in self.memes], self.image_delay, len(self.intro)
        ).save(self.authors)

    def prerender(self):
        try:
            mainstream = (
                ffmpeg.input(
                    "pipe:0",
                    format="png_pipe",
                    framerate=f"1/{self.image_delay}",
                    thread_queue_size="256",
                )
                .filter(
                    "scale", **self.resolution, force_original_aspect_ratio="decrease"
                )
                .filter("pad", **self.resolution, x="-1", y="-1", color="white")
            )

            Subtitles([m.title for m in self.memes], self.image_delay).save(
                "tmp_titles.srt"
            )
            mainstream = mainstream.filter(
                "subtitles",
                filename="tmp_titles.srt",
                fontsdir="res/fonts/",
                force_style="Alignment=1,"
                "Fontname=Obelix Pro,"
                "Fontsize=9,"
                "PrimaryColour=&HAAFFFFFF,"
                "OutlineColour=&HAA000000",
            )

            task = ffmpeg.output(
                mainstream,
                ffmpeg.input("res/loops/CoconutMall.mp3", stream_loop="-1"),
                "main.nut",
                shortest=None,
                max_muxing_queue_size="1024",
                **QUIET,
                # TODO this could be optimised for disk space/write time etc
                **{
                    "c:v": "rawvideo",
                    "c:a": "pcm_s16le",
                    "f": "nut",
                    "pix_fmt": "yuv420p",
                },
            ).overwrite_output()

            job = task.run_async(pipe_stdin=True, pipe_stderr=True)
            for meme in self.memes:
                job.stdin.write(meme.data.getvalue())
                job.stdin.flush()
            job.stdin.close()
            job.wait()
            try:
                remove("tmp_titles.srt")
            except OSError:
                pass

            print(*task.compile())
            print(job.stderr.read().decode())

            return "main.nut"
        except Exception as e:
            print("stderr:\n" + job.stderr.read().decode())
            raise e

    def render(self):
        try:
            oldvid = ffmpeg.input("main.nut", f="nut")

            mainstream = ffmpeg.concat(
                *self.intro.to_ffmpeg_input(self.resolution),
                oldvid.video,
                oldvid.audio,
                *self.outro.to_ffmpeg_input(self.resolution),
                n=3,
                a=1,
                v=1,
            ).drawtext(
                text="SparkMemes",
                x="0",
                y="0",
                fontcolor="black",
                fontfile="res/fonts/ObelixPro.ttf",
                alpha="0.25",
                fontsize="18",
            )

            task = mainstream.output(
                "video.mp4", **QUIET, **self.config  # shortest=None
            ).overwrite_output()

            job = task.run_async(pipe_stderr=True)
            job.wait()

            print(*task.compile())
            print(job.stderr.read().decode())

            try:
                remove("main.nut")
            except OSError:
                print("Could not delete main.nut")

        # be less vague
        except Exception as e:
            print("stderr:\n" + job.stderr.read().decode())
            raise e

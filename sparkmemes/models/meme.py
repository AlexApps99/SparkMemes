# TODO can ffmpeg handle image and video same way?

from abc import ABC, abstractmethod
import requests
from io import BytesIO
from PIL import Image, UnidentifiedImageError


class Meme(ABC):
    def __init__(self, submission):
        self.author = "/u/" + (
            submission.author.name if submission.author else "[deleted]"
        )
        self.title = submission.title
        self.subreddit = submission.subreddit.display_name
        self.post_url = submission.permalink

    @staticmethod
    def from_submission(submission):
        return ImageMeme(submission)
        # if is_text(submission):
        # 	return TextMeme(submission)
        # else if is_video(submission):
        # 	return VideoMeme(submission)
        # else if is_image(submission):
        # 	return ImageMeme(submission)
        # else:
        #     return None

    # Process whatever is stored
    @abstractmethod
    def process(self):
        pass


class MediaMeme(Meme):
    def __init__(self, submission):
        super().__init__(submission)
        self.url = submission.url
        self.data = None

    # Download URL directly to self.data
    def download(self):
        try:
            r = requests.get(self.url)
            r.raise_for_status()
        except requests.exceptions.RequestException:
            return False

        self.data = BytesIO(r.content)
        return True

    # Download to path, then set self.data to file object of path
    def download_disk(self, path):
        try:
            r = requests.get(self.url, stream=True)
            r.raise_for_status()  # TODO does this line delay saving?
        except requests.exceptions.RequestException:
            return False

        # TODO error handling
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=128):
                f.write(chunk)

        self.data = open(path, "rb")
        return True

    # Convert file to correct format, usually used within process
    @abstractmethod
    def convert(self):
        pass

    def process(self):
        if self.download():
            if self.convert():
                return True

        return False


class TextMeme(Meme):
    def __init__(self, submission):
        super().__init__(submission)
        self.text = submission.selftext


class ImageMeme(MediaMeme):
    def __init__(self, submission):
        super().__init__(submission)
        self.url = submission.preview["images"][0]["source"]["url"]

    def convert(self):
        try:
            img = Image.open(self.data).convert("RGBA")

            # Writing to BytesIO appends, so it needs to be empty
            if isinstance(self.data, BytesIO):
                self.data = BytesIO()

            Image.alpha_composite(
                # Replace transparency with Reddit's dark theme background
                Image.new("RGBA", img.size, (26, 26, 27)),
                img,
            ).convert("RGB").save(self.data, format="PNG")
        except UnidentifiedImageError as e:
            return False

        return True

    def tts_phrase(self):
        # TODO return OCR if confidence is high
        return self.title


class VideoMeme(MediaMeme):
    def __init__(self, submission):
        super().__init__(submission)
        self.url = ""  # TODO

    def convert(self):
        return False

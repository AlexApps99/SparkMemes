import requests
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw, UnidentifiedImageError
import textwrap


def _text_to_img(text, resolution=(1920, 1080), pad=(12, 2)):
    font = ImageFont.truetype("res/fonts/NotoSans.ttf", 18)

    img = Image.new("RGBA", resolution, (26, 26, 27, 0))
    draw = ImageDraw.Draw(img)

    for x in range(250, 150, -5):
        wtext = textwrap.fill(
            text, width=x, replace_whitespace=False, break_long_words=True
        )
        res = draw.multiline_textsize(wtext, font)
        # Only pad left/top
        if res[0] + pad[0] < resolution[0]:
            break
    else:
        return
    draw.multiline_text(pad, wtext, (215, 218, 220), font)

    return img


class Meme:
    def __init__(self, submission):
        self.author = submission.author.name if submission.author else "[deleted]"
        self.title = submission.title
        self.subreddit = submission.subreddit.display_name
        self.post_url = submission.permalink

        if submission.is_self:
            self.url = None
            self.text = submission.selftext
            self.data = BytesIO()
            _text_to_img(self.text).save(self.data, "PNG")
        else:
            self.url = submission.preview["images"][0]["source"]["url"]
            self.text = None
            self.data = None

    # Download URL directly to self.data
    def download(self):
        if self.url is not None:
            try:
                r = requests.get(self.url)
                r.raise_for_status()
            except requests.exceptions.RequestException:
                return False

            self.data = BytesIO(r.content)
            return True
        elif self.data is not None:
            return True
        else:
            return False

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

    # Process whatever is stored
    def process(self):
        if self.download():
            if self.convert():
                return True

        return False

    def tts_phrase(self):
        # TODO return OCR if confidence is high
        if self.text is not None:
            # return self.text
            return self.title
        else:
            return self.title

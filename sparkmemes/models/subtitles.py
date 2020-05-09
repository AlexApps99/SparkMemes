from datetime import datetime
from io import BytesIO


class Subtitles:
    def __init__(self, phrases, interval, offset=0):
        self.phrases = phrases
        self.interval = interval
        self.offset = offset

    # Saves to a file object
    def _save(self, fobject):
        for x, s in enumerate(self.phrases):
            fobject.write(
                "{}\n"
                "{:%H:%M:%S,000} --> {:%H:%M:%S,000}\n"
                "{}\n\n".format(
                    x + 1,
                    datetime.fromtimestamp((x * self.interval) + self.offset),
                    datetime.fromtimestamp(((x + 1) * self.interval) + self.offset),
                    s,
                )
            )

        return fobject

    # Saves subtitles to area on disk
    def save(self, path):
        with open(path, "w") as f:
            self._save(f)

    # BytesIO type object
    def to_file_object(self):
        fobject = BytesIO()
        return self._save(fobject)

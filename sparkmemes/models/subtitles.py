class Subtitles:
    def __init__(self, phrases, interval, offset=0):
        self.phrases = phrases
        self.interval = interval
        self.offset = offset

    @staticmethod
    def _h_m_s_ms(seconds):
        h, rem = divmod(seconds, 3600)
        m, rem = divmod(rem, 60)
        s, ms = divmod(rem, 1)
        return int(h), int(m), int(s), int(1000 * ms)

    @staticmethod
    def _timestamp(seconds):
        return "{:02}:{:02}:{:02},{:03}".format(*Subtitles._h_m_s_ms(seconds))

    # Saves to a file object
    def _save(self, fobject):
        for x, s in enumerate(self.phrases):
            fobject.write(
                "{}\n"
                "{} --> {}\n"
                "{}\n\n".format(
                    x + 1,
                    self._timestamp((x * self.interval) + self.offset),
                    self._timestamp(((x + 1) * self.interval) + self.offset),
                    s,
                )
            )

        return fobject

    # Saves subtitles to area on disk
    def save(self, path):
        with open(path, "w") as f:
            self._save(f)

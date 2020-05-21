import subprocess
import wave
import os

# TODO audio desyncs over time

class TTS:
    @staticmethod
    def supports_tts():
        import platform
        return platform.system() == "Windows"

    def __init__(self, balcon="res/tts/balcon.exe"):
        self.balcon = balcon
        print(self._list_voices().decode())

    def _balcon(self, *args, **kwargs):
        return subprocess.run(
            [self.balcon, *args], check=True, stdout=subprocess.PIPE, **kwargs
        ).stdout#.decode()

    def _list_voices(self):
        return self._balcon("-l")

    def say(self, phrase, voice=None):
        try:
            b = self._balcon(
                #"-f", "tmp_titles.srt",
                "-t", phrase,
                *("-n", voice) if voice is not None else (),
                "-enc", "utf8",
                #"-sub",
                #"--sub-fit",
                #"--sub-max", "5",
                "-o"
            )
        except subprocess.CalledProcessError as e:
            return None
        else:
            return b

    @staticmethod
    def concat_waves(file, waves, interval=10):
        waves = [wave.open(w, "rb") for w in waves]

        with wave.open(file, "wb") as final_wav:
            final_wav.setparams(waves[0].getparams())
            for w in waves:
                space = w.getframerate() * interval
                amount = w.getnframes()
                if amount < space:  # Pad
                    delay = space - amount
                    final_wav.writeframes(w.readframes(amount))
                    final_wav.writeframes(
                        delay * final_wav.getnchannels() * final_wav.getsampwidth() * b"\0"
                    )
                else:  # Clip
                    print(
                        "Warning: TTS was clipped! Extend the interval! ({} > {})".format(
                            amount, space
                        )
                    )
                    final_wav.writeframes(w.readframes(space))

        for w in waves:
            w.close()

import subprocess
import wave
import os
import pyttsx3

# TODO audio desyncs over time

class TTS:
    @staticmethod
    def supports_tts():
        import platform
        return platform.system() == "Windows"

    def __init__(self):
        self.engine = pyttsx3.init("sapi5")
        print(self._list_voices())
        print(self._get_voice())

    def _list_voices(self):
        return self.engine.getProperty("voices")

    def _get_voice(self):
        return self.engine.getProperty("voice")

    def _set_voice(self, name):
        self.engine.setProperty("voice", name)

    # TODO error handling
    def say(self, phrase, voice=None, tmp="tmp.wav"):
        if voice is not None:
            self._set_voice(voice)

        self.engine.save_to_file(phrase, tmp)
        try:
            with open(tmp, "rb") as f:
                tts = f.read()
            os.remove(tmp)
        except OSError:
            return None
        else:
            return tts

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

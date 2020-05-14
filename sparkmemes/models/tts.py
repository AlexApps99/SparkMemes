import subprocess
import wave
import os


# TODO audio desyncs over time
def supports_tts():
    import platform

    return platform.system() == "Darwin"


def say(*args):
    return subprocess.run(
        ["say", *args], check=True, stdout=subprocess.PIPE
    ).stdout.decode()


def check_supports_tts():
    required = {"voice": "Daniel", "file-format": "WAVE"}

    r = True

    for k, v in required.items():
        try:
            out = say("--" + k + "=?")
        except subprocess.CalledProcessError:
            out = ""

        if r and ("\n" + v + " ") in out:
            pass
        else:
            r = False

    return r


def tts(phrase, voice="Daniel", tmp="tmp"):
    tmp += ".wav"
    try:
        # https://developer.apple.com/library/archive/documentation/MusicAudio/Conceptual/CoreAudioOverview/SupportedAudioFormatsMacOSX/SupportedAudioFormatsMacOSX.html
        say(
            "--file-format=WAVE", "--data-format=LEI32", "-v", voice, "-o", tmp, phrase,
        )
    except subprocess.CalledProcessError as e:
        return None

    try:
        with open(tmp, "rb") as f:
            tts = f.read()

        os.remove(tmp)

        return tts
    except OSError as e:
        return None


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

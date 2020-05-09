def supports_tts():
    import platform

    return platform.system() == "Darwin"


if supports_tts():
    import subprocess

    def say(*args):
        return subprocess.run(
            ["say", *args], check=True, stdout=subprocess.PIPE
        ).stdout.decode()

    def check_support():
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
                "--file-format=WAVE",
                "--data-format=LEI32",
                "-v",
                voice,
                "-o",
                tmp,
                phrase,
            )
        except subprocess.CalledProcessError as e:
            return None

        try:
            with open(tmp, "rb") as f:
                tts = f.read()

            import os

            os.remove(tmp)

            return tts
        except OSError as e:
            return None

    if __name__ == "__main__":
        from io import BytesIO

        if check_support():
            o = tts("test")

            if o != None:
                import wave

                print(wave.open(BytesIO(o)).getparams())

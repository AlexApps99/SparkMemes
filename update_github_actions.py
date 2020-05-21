def ls(l, first=13, indent=8, limit=80):
    l = ['"' + x + '"' for x in l]
    lines = [[]]
    for x in l:
        if len(" ".join(lines[-1])) < limit - indent - (
            first if len(lines) == 1 else 0
        ):
            lines[-1].append(x)
        else:
            lines.append([lines[-1].pop()])

    return "\n".join(
        [(indent * " " if n > 0 else "") + " ".join(x) for n, x in enumerate(lines)]
    )


TEMPLATE = """name: "{1}"

on:
  schedule:
    - cron: "{3}"

jobs:
  memes:
    name: "{1}"
    runs-on: "windows-latest"
    timeout-minutes: 30
    steps:

    - name: "Checkout repository"
      uses: "actions/checkout@v2"

    - name: "Install Daniel UK TTS"
      run: "res/tts/DanielUK.msi /i /quiet /qn"
      continue-on-error: true

    - name: "Install dependencies"
      run: "choco install --no-progress ffmpeg"
    - name: "Setup Python"
      uses: "actions/setup-python@v2"
      with:
        python-version: "3.x"

    - name: "Install Python dependencies"
      run: "python -m pip install -r requirements.txt"

    - name: "Create video"
      env:
        praw_client_id: ${{{{ secrets.REDDIT_CLIENT_ID }}}}
        praw_client_secret: ${{{{ secrets.REDDIT_CLIENT_SECRET }}}}
        praw_user_agent: ${{{{ secrets.REDDIT_USER_AGENT }}}}
        YT_REFRESH_TOKEN: ${{{{ secrets.YT_REFRESH_TOKEN }}}}
        YT_CLIENT_ID: ${{{{ secrets.YT_CLIENT_ID }}}}
        YT_CLIENT_SECRET: ${{{{ secrets.YT_CLIENT_SECRET }}}}
      run: >
        python -m sparkmemes "{2}" "{4}"
        --subreddits {5}
        --tags {6}
"""

VIDEOS = [
    (
        "cringe",
        "therewasanattempt",
        "r/therewasanattempt v{}",
        "0 2 * * *",
        65,
        ls(["therewasanattempt"], 13),
        ls(
            [
                "There Was An Attempt - EPIC FAILS",
                "reddit",
                "funny",
                "epic fails",
                "epic",
                "fails",
                "funny fails",
                "r/",
                "giofilms",
                "sorrow tv",
                "rslash",
                "comedy",
                "memes",
                "dank doodle memes",
                "ddm",
                "best posts",
                "top reddit posts",
                "reddit stories",
                "cringe",
                "reddit cringe",
                "funniest",
                "fail",
            ],
            7,
        ),
    ),
    (
        "dankmemes",
        "Epicly dank memes",
        "Epicly dank memes v{}",
        "0 8 * * *",
        16,
        ls(
            [
                "dankmemes",
                "me_irl",
                "meirl",
                "memes",
                "wholesomememes",
                "MemeEconomy",
                "BikiniBottomTwitter",
            ],
            13,
        ),
        ls(
            [
                "memes",
                "dank doodle memes",
                "best memes",
                "memes compilation",
                "dank memes",
                "memes 2019",
                "funny memes",
                "dank memes compilation",
                "best memes compilation",
                "meme",
                "funny",
                "fortnite memes",
                "tik tok ironic memes compilation",
                "freememeskids",
                "pewdiepie",
                "try not to laugh challenge",
                "you laugh you lose challenge",
                "funniest memes",
                "ddm",
                "memes i like to watch",
                "ultimate memes compilation",
                "dank",
                "compilation",
                "tik tok memes",
                "2019",
                "meme review",
                "dog memes",
                "cat memes",
                "spongebob memes",
                "tiktok",
                "memes to watch",
            ],
            7,
        ),
    ),
    (
        "mildlyinfuriating",
        "The best of r/mildlyinfuriating",
        "The best of r/mildlyinfuriating v{}",
        "0 14 * * *",
        27,
        ls(["mildlyinfuriating"], 13),
        ls(
            [
                "r/mildlyinfuriating",
                "mildlyinfuriating",
                "unsatisfying",
                "onejob",
                "you had one job",
                "meme",
                "This video will make you mildly infuriated",
                "mildly infuriated",
                "mildlyinfuriating",
                "funny",
                "mildly",
                "infuriating",
                "infuriated",
                "funniest",
                "reddit",
                "memes",
                "dank doodle memes",
                "ddm",
                "satisfying",
                "interesting",
                "top posts",
                "best posts",
                "sorrow tv",
                "giofilms",
                "rslash",
            ],
            7,
        ),
    ),
    (
        "woooosh",
        "Funny r/woooosh moments",
        "Funny r/woooosh moments v{}",
        "0 20 * * *",
        21,
        ls(["woooosh"], 13),
        ls(
            [
                "r/woosh",
                "r/wooosh",
                "over their heads",
                "not getting the joke",
                "reddit",
                "r/woooosh",
                "woooosh",
                "top reddit posts",
                "best reddit posts",
                "r/woooosh top posts",
                "top posts of all time",
                "funny",
                "interesting",
                "memes",
                "jokes",
                "best posts",
                "top posts",
                "dank doodle memes",
                "giofilms",
                "emkay",
                "sorrowtv",
            ],
            7,
        ),
    ),
]

if __name__ == "__main__":
    for video in VIDEOS:
        with open(".github/workflows/" + video[0] + ".yml", "w") as f:
            f.write(TEMPLATE.format(*video))

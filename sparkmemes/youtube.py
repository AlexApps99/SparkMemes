from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from os import getenv, path

from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload


class YouTube:
    def __init__(self, refresh_token, client_id, client_secret):
        self.creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=[
                "https://www.googleapis.com/auth/youtube",
                "https://www.googleapis.com/auth/youtube.upload",
            ],
        )

        self.yt = build("youtube", "v3", credentials=self.creds)

    def upload(
        self,
        video="video.mp4",
        title="Untitled Video",
        description="",
        tags=[],
        privacy="public",
        category=23,
    ):
        if not path.exists(video):
            print("There's no video to upload!")
        else:
            body = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "categoryId": category,
                    "defaultLanguage": "en",
                },
                "status": {"privacyStatus": privacy.lower()},
            }

            try:
                insert_response = (
                    self.yt.videos()
                    .insert(
                        part=",".join(body.keys()),
                        body=body,
                        media_body=MediaFileUpload(video, chunksize=-1, resumable=True),
                        autoLevels=False,
                        stabilize=False,
                    )
                    .execute(num_retries=5)
                )
            except HttpError as e:
                print("An HTTP error " + e.resp.status + " occurred:\n" + e.content)
            else:
                print(
                    "The video ["
                    + insert_response["id"]
                    + "] was successfully uploaded."
                )
                return YouTubeVideo(self.yt, insert_response["id"])


class YouTubeVideo:
    def __init__(self, youtube, video_id):
        self.yt = youtube
        self.video_id = video_id

    def like(self):
        try:
            self.yt.videos().rate(id=self.video_id, rating="like").execute(
                num_retries=5
            )
        except HttpError as e:
            print("An HTTP error " + e.resp.status + " occurred:\n" + e.content)
        else:
            print("Video liked successfully")

    # Thumbnail should be a file object
    def upload_thumbnail(self, thumbnail, mimetype):
        try:
            self.yt.thumbnails().set(
                videoId=self.video_id,
                media_body=MediaIoBaseUpload(
                    thumbnail, mimetype=mimetype, chunksize=-1, resumable=True
                ),
            ).execute(num_retries=5)
        except HttpError as e:
            print("An HTTP error " + e.resp.status + " occurred:\n" + e.content)
        else:
            print("The custom thumbnail was successfully set.")

    def upload_captions(self, name):
        try:
            self.yt.captions().insert(
                part="snippet",
                body={
                    "snippet": {
                        "videoId": self.video_id,
                        "language": "en",
                        "name": name,
                    }
                },
                media_body=MediaFileUpload(name + ".srt", chunksize=-1, resumable=True),
            ).execute(num_retries=5)
        except HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
        else:
            print("Captions added successfully")

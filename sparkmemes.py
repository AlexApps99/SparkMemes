#!/usr/bin/env python3
from datetime import datetime, timedelta, timezone

import requests
from os import getenv, path, remove

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from random import shuffle
import praw
from tqdm import tqdm
from PIL import Image
from io import BytesIO

import ffmpeg

from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from googleapiclient.errors import HttpError

#import gtts

# TODO REFACTOR INTO CLASSES

################################################################################
# Video generation
################################################################################

def download_submissions(Subreddit, Sort = "Top", Limit = 75, TimeFilter = "Day"):
  Subreddit = "+".join(Subreddit)
  TimeFilter = TimeFilter.lower()

  reddit = praw.Reddit()

  sub = reddit.subreddit(Subreddit)
  if Sort == "Controversial": submissions = sub.controversial(TimeFilter, limit=Limit)
  elif Sort == "Gilded": submissions = sub.gilded(limit=Limit)
  elif Sort == "Hot": submissions = sub.hot(limit=Limit)
  elif Sort == "New": submissions = sub.new(limit=Limit)
  elif Sort == "Random Rising": submissions = sub.random_rising(limit=Limit)
  elif Sort == "Rising": submissions = sub.rising(limit=Limit)
  elif Sort == "Top": submissions = sub.top(TimeFilter, limit=Limit)

  def checkSubmission(s):
    if s.is_self: return False
    elif not hasattr(s, "preview"): return False
    elif not s.preview["enabled"]: return False
    elif "reddit_video_preview" in s.preview: return False
    elif "mp4" in s.preview["images"][0]["variants"]: return False
    elif "gif" in s.preview["images"][0]["variants"]: return False
    elif s.stickied: return False
    elif s.over_18: return False
    #elif s.spoiler: return False
    #elif s.locked: return False
    #elif hasattr(s, "crosspost_parent"): return False
    else: return True

  submissions = [s for s in tqdm(submissions, "Submissions filtered", Limit, unit="s") if checkSubmission(s)]

  shuffle(submissions)

  successes = 0

  images = [None for s in submissions]
  for x, s in tqdm(enumerate(submissions), "Images downloaded", len(submissions), unit="img"):
    try:
      img = Image.open(
        BytesIO(requests.get(s.preview["images"][0]["source"]["url"]).content)
      ).convert("RGBA")
      images[x] = Image.alpha_composite(
        Image.new("RGBA", img.size, (26,26,27)),
        img
      ).convert("RGB")
      successes += 1
    except Exception as err:
      print("Error on", s.preview["images"][0]["source"]["url"])
      print(err)

  print(f"\n{successes}/{len(submissions)} images downloaded successfully")
  
  #print(
  #  f"<details><summary>{len(submissions)}/{Limit} submissions:</summary><table><thead>"
  #  "<tr><th>Number</th><th>Title</th><th>Upvotes</th><th>Comments</th></tr></thead><tbody><tr>" +
  #  "</tr><tr>".join([f"<td>{i+1}</td><td>{s.title}</td><td>{s.score:,}</td><td>{s.num_comments:,}</td>" for i, s in enumerate(submissions)]) +
  #  "</tbody></tr></table></details>"
  #)
  
  return (submissions, images)


def render(submissions, images, ShowCaptions = True, ImageDelay = 10, Background = "White", FPS = 30, HardwareEncode = "None"):
  #["None", "VAAPI", "NVenc"]

  output_config = {
    "movflags": "+faststart", # moov atom at the front of the file (Fast Start)
    
    "c:a": "aac", # AAC-LC
    "profile:a": "aac_low", # AAC-LC
    "b:a": "384k", # Recommended audio bitrate

    "f": "mp4",
    "profile:v": "high", # High Profile
    "bf": "2", # 2 consecutive B frames
    "g": str(round(FPS/2)), # Closed GOP, half of the frame rate
    "coder": "ac", # CABAC
    "pix_fmt": "yuv420p", # Chroma subsampling: 4:2:0

    "r": str(FPS), # Framerate, naturally
    "map_metadata": "-1"
  }

  if not HardwareEncode == "NVenc":
    output_config.update({
      "c:v": "libx264", # H.264
      "crf": "20", # Variable bitrate
      "tune": "stillimage", # Optimize the filesize (rhyming)
      "preset": "veryfast" # Speed up rendering a bit
    })
    if HardwareEncode == "VAAPI":
      output_config["c:v"] = "h264_vaapi"
  else:
    output_config.update({
      "c:v": "h264_nvenc", # H.264
      "cq": "20", # This may not have been set up right
      "rc:v": "vbr_hq", # Look into it
      "preset": "medium" # Speed up rendering a bit
    })

  resolution = {"w": "1920", "h": "1080"}

  quiet = {"nostats": None, "hide_banner": None, "loglevel": "warning"}

  def genCaptions(capfile, infolist, offset=0):
    with capfile as captions:
      for x, s in tqdm(enumerate(infolist), 'Captions generated', len(infolist), unit='cap'):
        captions.write(
          "{}\n"
          "{:%H:%M:%S,000} --> {:%H:%M:%S,000}\n"
          "{}\n\n".format(
            x+1,
            datetime.fromtimestamp((x*ImageDelay)+offset),
            datetime.fromtimestamp(((x+1)*ImageDelay)+offset),
            s
          )
        )

  genCaptions(open("titles.srt", "w"), [s.title for s in submissions])

  try:
    mainstream = (
      ffmpeg.input("pipe:0", format="ppm_pipe", framerate=f"1/{ImageDelay}", thread_queue_size="256")
      .filter("scale", **resolution, force_original_aspect_ratio="decrease")
      .filter("pad", **resolution, x="-1", y="-1", color=Background.lower())
    )
      
    if ShowCaptions:
      mainstream = mainstream.filter(
        "subtitles",
        filename="titles.srt",
        fontsdir="res/fonts/",
        force_style="Alignment=1,Fontname=Obelix Pro,Fontsize=9,PrimaryColour=&HAAFFFFFF,OutlineColour=&HAA000000"
      )
    
    task = (
      ffmpeg.output(
        mainstream,
        ffmpeg.input("res/loops/CoconutMall.mp3", stream_loop="-1"),
        "main.nut",
        shortest=None,
        max_muxing_queue_size="1024",
        **quiet,
        **{"c:v": "rawvideo", "c:a": "pcm_s16le", "f": "nut", "pix_fmt": "yuv420p"}
      )
      .overwrite_output()
    )

    job = task.run_async(pipe_stdin=True, pipe_stderr=True)
    for img in tqdm(images, "Images passed to FFmpeg", unit='img'):
      img.save(job.stdin, "PPM")
      job.stdin.flush()
    job.stdin.close()
    job.wait()

    print(*task.compile())
    print(job.stderr.read().decode())

    oldvid = ffmpeg.input("main.nut", f="nut")

    mainstream = (
      ffmpeg.concat(
        (
          ffmpeg.input("res/intro/intro.png", loop="1", t="10")
          .filter("scale", **resolution)
          .drawtext(
            textfile="res/intro/intro.txt",
            x="(w-tw)/2",
            y="(h-th)/2",
            fontcolor="white",
            fontfile="res/fonts/ObelixPro.ttf",
            fontsize="48"
          )
        ),
        ffmpeg.input("res/intro/intro.mp3").filter("apad", whole_dur="10"),
        oldvid.video,
        oldvid.audio,
        (
          ffmpeg.input("res/outro/outro.png", loop="1", t="20")
          .filter("scale", **resolution)
        ),
        ffmpeg.input("res/outro/outro.mp3"),
        n=3,
        a=1,
        v=1
      ).drawtext(
        text="SparkMemes",
        x="0",
        y="0",
        fontcolor="black",
        fontfile="res/fonts/ObelixPro.ttf",
        alpha="0.25",
        fontsize="18"
      )
    )

    if HardwareEncode == "VAAPI":
      mainstream = mainstream.filter("format", "nv12").filter("hwupload")
    
    task = (
      mainstream
      .output("video.mp4", **quiet, **output_config)
      .overwrite_output()
    )

    if HardwareEncode == "VAAPI":
      task = task.global_args('-vaapi_device', '/dev/dri/renderD128')

    job = task.run_async(pipe_stderr=True)
    job.wait()

    print(*task.compile())
    print(job.stderr.read().decode())

    genCaptions(open("titles.srt", "w"), [s.title for s in submissions], 10)
    genCaptions(open("authors.srt", "w"), [f"/u/{s.author.name if s.author else '[deleted]'}" for s in submissions], 10)

    try:
      remove("main.nut")
    except:
      print("Could not delete main.nut")

  except Exception as e:
    print("stderr:\n" + job.stderr.read().decode())
    raise e

#def record_tts():
#  successes = 0
#
#  tts_audio = [BytesIO() for s in submissions]
#  for x, s in tqdm(enumerate(submissions), "TTS recordings downloaded", len(submissions), unit="tts"):
#    try:
#      gtts.gTTS(s.title, lang="en").write_to_fp(tts_audio[x])
#      successes += 1
#    except gtts.gTTSError as err:
#      print("Error on", s.title)
#      print(err.infer_msg())
#      print(err)
#
#  print(f"{successes}/{len(submissions)} successful TTS recordings")

################################################################################
# YouTube
################################################################################

def authenticate():
  creds = Credentials(
    token=None,
    refresh_token=getenv('YT_REFRESH_TOKEN'),
    token_uri="https://oauth2.googleapis.com/token",
    client_id=getenv('YT_CLIENT_ID'),
    client_secret=getenv('YT_CLIENT_SECRET'),
    scopes=["https://www.googleapis.com/auth/youtube", "https://www.googleapis.com/auth/youtube.upload"]
  )

  return build("youtube", "v3", credentials=creds)


def upload(youtube, Title, Description, Tags, Privacy = "Public"):
  video = "video.mp4"

  if not path.exists(video):
    print("There's no video to upload!")
  else:
    body = {
      "snippet": {
        "title": Title,
        "description": Description,
        "tags": Tags,
        "categoryId": 23, # Comedy
        "defaultLanguage": "en"
      },
      "status": {
        "privacyStatus": Privacy.lower()
      }
    }

    try:
      insert_response = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(video, chunksize=-1, resumable=True),
        autoLevels=False,
        stabilize=False
      ).execute(num_retries=5)
    except HttpError as e:
      print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
    else:
      print(f"The video [{insert_response['id']}] was successfully uploaded.")
      return insert_response['id']


def gen_thumbnail(image):
  resolution = {"w": "1280", "h": "720"}

  task = (
    ffmpeg.input("pipe:0", format="ppm_pipe")
    .filter("scale", **resolution, force_original_aspect_ratio="decrease")
    .filter("pad", **resolution, x="-1", y="-1", color="white")
    .output("pipe:1", f="singlejpeg", nostats=None, hide_banner=None, loglevel="warning")
  )

  job = task.run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)

  image.save(job.stdin, "PPM")
  
  return job


def gen_clickbait(url, caption):
  resolution = {"w": "1280", "h": "720"}
  
  if len(caption) > 0:
    task = (
      ffmpeg.input("pipe:0", format="ppm_pipe")
      .filter("scale", w="1280", h="640", force_original_aspect_ratio="decrease")
      .filter("pad", **resolution, x="-1", y="oh-ih", color="white")
      .drawtext(caption, fontfile="fonts/font.ttf", fontsize="40", x="(w-tw)/2", y="40-(th/2)")
      .output("pipe:1", f="singlejpeg", nostats=None, hide_banner=None, loglevel="warning")
    )
  else:
    task = (
      ffmpeg.input("pipe:0", format="ppm_pipe")
      .filter("scale", **resolution, force_original_aspect_ratio="decrease")
      .filter("pad", **resolution, x="-1", y="-1", color="white")
      .output("pipe:1", f="singlejpeg", nostats=None, hide_banner=None, loglevel="warning")
    )
    
  job = task.run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)

  Image.open(BytesIO(requests.get(url).content)).save(job.stdin, "PPM")
  
  return job

def upload_thumbnail(youtube, job, video_id):
  try:
    job.stdin.close()
    job.wait()

    print(job.stderr.read().decode())
  except ffmpeg.Error as err:
    print(e)
    print(e.stderr.decode())

  try:
    youtube.thumbnails().set(
      videoId=video_id,
      media_body=MediaIoBaseUpload(
        BytesIO(job.stdout.read()),
        mimetype="image/jpeg",
        chunksize=-1,
        resumable=True
      )
    ).execute(num_retries=5)
  except HttpError as e:
    print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
  else:
    print("The custom thumbnail was successfully set.")


def like_video(youtube, video_id):
  try:
    youtube.videos().rate(id=video_id, rating="like").execute(num_retries=5)
  except HttpError as e:
    print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
  else:
    print("Video liked successfully")


def upload_captions(youtube, video_id, name):
  try:
    youtube.captions().insert(
      part="snippet",
      body={
        "snippet": {
          "videoId": video_id,
          "language": "en",
          "name": "Credits"
        }
      },
      media_body = MediaFileUpload(f"{name}.srt", chunksize=-1, resumable=True)
    ).execute(num_retries=5)
  except HttpError as e:
    print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
  else:
    print("Captions added successfully")

################################################################################
# Main/commandline usage
################################################################################

if __name__ == "__main__":
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument('name', help='the name of the video, with every {} being replaced with the video number', type=str)
  parser.add_argument('offset', help='the number of days since 2020 that should set the version number', type=int)
  parser.add_argument('--subreddits', type=str, nargs='+', help='a list of subreddits to be compiled', default=["all"])
  parser.add_argument('--description', type=str, help='description (duh)', default="Like, subscribe and comment for 12 years of good luck\n\nMemes daily, SUBSCRIBE for more funny best memes compilation, clean memes, dank memes & tik tok memes of 2019.\ntik tok ironic memes compilation, family friendly pewdiepie memes, dog & cat reddit memes.")
  parser.add_argument('--tags', type=str, nargs='+', help='tags (duh)')
  args = parser.parse_args()
  
  posts, imgs = download_submissions(args.subreddits)
  render(posts, imgs, True)
  yt = authenticate()
  video_id = upload(yt, args.name.replace('{}',str((datetime.now(timezone.utc)-(datetime(2020,1,1,tzinfo=timezone.utc)+timedelta(days=args.offset))).days)), args.description, args.tags)
  #upload_thumbnail(yt, gen_thumbnail(imgs[0]), video_id)
  #upload_captions(yt, video_id, "authors")
  #upload_captions(yt, video_id, "titles")
  like_video(yt, video_id)
  
  print(
    "Video: https://youtube.com/watch?v={0}\n"
    "Studio: https://studio.youtube.com/video/{0}/edit\n"
    "Endscreen: https://www.youtube.com/endscreen?v={0}&nv=1\n"
    "Translations: https://studio.youtube.com/video/{0}/translations"
    .format(video_id)
  )

#!/usr/bin/env python3

import requests
import argparse
from time import sleep

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('client_id', type=str, help='client id for api')
  parser.add_argument('client_secret', type=str, help='client secret for api')
  #parser.add_argument('scope', type=str, nargs='+', help='scopes for api')
  args = parser.parse_args()
  client_id = args.client_id
  client_secret = args.client_secret
  #scope = args.scope
  scope = ["https://www.googleapis.com/auth/youtube", "https://www.googleapis.com/auth/youtube.upload"]

  zero = requests.get("https://accounts.google.com/.well-known/openid-configuration").json()

  one = requests.post(zero['device_authorization_endpoint'], params={
    "client_id": client_id,
    "scope": " ".join(scope)
  }).json()

  print(f"Visit {one['verification_url']} and type in \"{one['user_code']}\".")

  done = False

  while not done:
    sleep(one['interval'])
    two = requests.post(zero['token_endpoint'], params={
      "client_id": client_id,
      "client_secret": client_secret,
      "device_code": one['device_code'],
      "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
    })
    done = True if two.status_code == 200 else False

  two = two.json()

  print(
    f"\n\nDevice code: {one['device_code']}\n"
    f"Access token: {two['access_token']}\n"
    f"Expires in: {two['expires_in']}\n"
    f"Refresh token: {two['refresh_token']}"
  )

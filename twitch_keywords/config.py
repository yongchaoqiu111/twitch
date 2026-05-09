import os
from dotenv import load_dotenv

load_dotenv()

TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
TWITCH_REDIRECT_URI = os.getenv("TWITCH_REDIRECT_URI", "http://localhost")
TWITCH_NICKNAME = os.getenv("TWITCH_NICKNAME")
TWITCH_OAUTH_TOKEN = os.getenv("TWITCH_OAUTH_TOKEN")

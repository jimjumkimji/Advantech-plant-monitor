# app/dropbox/env.py
import os
from dotenv import load_dotenv

load_dotenv()

DROPBOX_TOKEN = os.getenv("DROPBOX_TOKEN")
WISE4051_ROOT = os.getenv("WISE4051_FOLDER")
WISE4012_ROOT = os.getenv("WISE4012_FOLDER")

if not DROPBOX_TOKEN:
    raise RuntimeError("DROPBOX_TOKEN is not set in .env")

if not WISE4051_ROOT:
    raise RuntimeError("WISE4051_FOLDER is not set in .env")

if not WISE4012_ROOT:
    raise RuntimeError("WISE4012_FOLDER is not set in .env")

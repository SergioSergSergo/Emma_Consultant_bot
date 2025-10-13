import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set.")

GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")
if not GROUP_CHAT_ID:
    raise ValueError("GROUP_CHAT_ID environment variable not set.")

CALENDLY_URL = os.getenv("CALENDLY_URL")
if not CALENDLY_URL:
    raise ValueError("CALENDLY_URL environment variable not set.")

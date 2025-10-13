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

USE_WEBHOOK = os.getenv("USE_WEBHOOK", "false").lower() == "true"
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
if USE_WEBHOOK and not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL environment variable must be set if USE_WEBHOOK is true.")

WEBAPP_HOST = os.getenv("WEBAPP_HOST", "localhost")
WEBAPP_PORT = os.getenv("WEBAPP_PORT", 3000)
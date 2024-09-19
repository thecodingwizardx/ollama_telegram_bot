import os

from dotenv import load_dotenv

load_dotenv(dotenv_path="config/.env")

TOKEN = os.getenv("BOT_TOKEN", None)
MONGO_URI = os.getenv("MONGO_URI", None)

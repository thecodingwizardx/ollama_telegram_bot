import os

from dotenv import load_dotenv

load_dotenv(dotenv_path="config/.env")

TOKEN = os.getenv("BOT_TOKEN", None)
MONGO_URI = os.getenv("MONGO_URI", None)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", None)
OLLAMA_DEFAULT_MODEL = os.getenv("OLLAMA_DEFAULT_MODEL", None)
TIMEOUT = os.getenv("TIMEOUT", "3000")

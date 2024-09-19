import os

from dotenv import load_dotenv
from ollama import AsyncClient

load_dotenv(dotenv_path="config/.env")

TOKEN = os.getenv("BOT_TOKEN", None)
MONGO_URI = os.getenv("MONGO_URI", None)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", None)
OLLAMA_DEFAULT_MODEL = os.getenv("OLLAMA_DEFAULT_MODEL", None)
OLLAMA_CUSTOM_PORT = os.getenv("OLLAMA_CUSTOM_PORT", 11434)
TIMEOUT = os.getenv("TIMEOUT", "3000")

client = AsyncClient(host=f"http://{OLLAMA_BASE_URL}:{OLLAMA_CUSTOM_PORT}")

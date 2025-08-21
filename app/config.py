import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_API_URL = os.getenv("TELEGRAM_API_URL", "https://api.telegram.org")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
LLM_URL = os.getenv("LLM_URL", "http://localhost:8081/api/v1/chat/ask")
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_API_URL = "https://api.telegram.org"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

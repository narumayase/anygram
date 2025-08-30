import os
from dotenv import load_dotenv

load_dotenv()

# telegram configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = os.getenv("TELEGRAM_API_URL", "https://api.telegram.org")

# llm configuration
LLM_URL = os.getenv("LLM_URL", "http://localhost:8081/api/v1/chat/ask")

# anyway configuration
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8003/api/v1/send")
GATEWAY_ENABLED = os.getenv("GATEWAY_ENABLED", "false").lower() == "true"

# server configuration
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
RELOAD = os.getenv("RELOAD", "true").lower() == "true"
LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO").upper()

# validate configurations
def validate_config():
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN environment variable is required")
    
    if not LLM_URL:
        raise ValueError("LLM_URL environment variable is required")

    print(f"✅ Configuration loaded successfully:")
    print(f"   - Host: {HOST}")
    print(f"   - Port: {PORT}")
    print(f"   - Telegram API: {TELEGRAM_API_URL}")
    print(f"   - LLM URL: {LLM_URL}")
    print(f"   - Reload: {RELOAD}")
    print(f"   - Log level: {LOG_LEVEL}")
    if GATEWAY_ENABLED:
        print(f"   - Gateway URL: {GATEWAY_URL}")

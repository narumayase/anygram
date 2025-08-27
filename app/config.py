import os
from dotenv import load_dotenv

load_dotenv()

# telegram configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = os.getenv("TELEGRAM_API_URL", "https://api.telegram.org")

# llm configuration
LLM_URL = os.getenv("LLM_URL", "http://localhost:8081/api/v1/chat/ask")

# kafka configuration
KAFKA_ENABLED = os.getenv("KAFKA_ENABLED", "false").lower() == "true"
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "anygram.prompts")

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
    if KAFKA_ENABLED:
        print(f"   - Kafka Broker: {KAFKA_BROKER}")
        print(f"   - Kafka Topic: {KAFKA_TOPIC}")

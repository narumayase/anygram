import httpx
from .config import TELEGRAM_API_URL, TELEGRAM_TOKEN, LLM_URL

async def send_telegram_message(msg):
    url = f"{TELEGRAM_API_URL}/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": msg.chat_id, "text": msg.text}
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload)
        return r.json()
    
async def ask_llm(prompt: str) -> str:
    payload = {"prompt": prompt}
    async with httpx.AsyncClient() as client:
        resp = await client.post(LLM_URL, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["response"]
import httpx
from .config import TELEGRAM_API_URL, TELEGRAM_TOKEN, LLM_URL, GATEWAY_URL
import logging
from uuid import uuid4
import json
import base64

# Configure logging
logger = logging.getLogger(__name__)

async def send_telegram_message(msg):
    url = f"{TELEGRAM_API_URL}/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": msg.chat_id, "text": msg.text}

    logger.debug(f"payload to send to telegram: payload: {payload}")

    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload)

        logger.debug(f"status code from telegram: response status: {r.status_code}")
        logger.debug(f"response receive from telegram: {r.json()}")
        
        return r.json()

async def ask_llm(prompt: str) -> str:
    payload = {"prompt": prompt}
    logger.debug(f"payload to send to llm: payload: {payload}")

    async with httpx.AsyncClient() as client:
        resp = await client.post(LLM_URL, json=payload)
        logger.debug(f"status code from llm: response status: {resp.status_code}")

        resp.raise_for_status()
        data = resp.json()        
        logger.debug(f"response receive from llm: {data}")

        return data["response"]

async def send_message_to_gateway(prompt: str, chat_id: str) -> None:
    correlation_id = str(uuid4())
    key = f"telegram:{chat_id}"
    content_json = json.dumps({"prompt": prompt})
    content_base64 = base64.b64encode(content_json.encode("utf-8")).decode("utf-8")

    payload = {"key": key,
               "headers": {
                   "correlation-id": correlation_id
               },
               "content": content_base64
               }

    logger.debug(f"payload to send to anyway: {payload}")
    logger.info(f"key to send to anyway: {key}")
    logger.info(f"header to send to anyway: correlation-id: {correlation_id}")

    async with httpx.AsyncClient() as client:
        resp = await client.post(GATEWAY_URL, json=payload)
        logger.debug(f"status code from anyway: response status: {resp.status_code}")

        resp.raise_for_status()
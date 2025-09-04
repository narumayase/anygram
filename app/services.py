import httpx
from .config import TELEGRAM_API_URL, TELEGRAM_TOKEN, LLM_URL, GATEWAY_API_URL
from fastapi import Request
from app.logger import logger, RequestLoggerAdapter
from uuid import uuid4
import json
import base64

async def send_telegram_message(msg, request: Request):
    log: RequestLoggerAdapter = request.state.logger
    url = f"{TELEGRAM_API_URL}/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": msg.chat_id, "text": msg.text}

    log.debug(f"payload to send to telegram: payload: {payload}")

    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload)

        log.debug(f"status code from telegram: response status: {r.status_code}")
        log.debug(f"response receive from telegram: {r.json()}")
        
        return r.json()

async def ask_llm(prompt: str, request: Request) -> str:
    log: RequestLoggerAdapter = request.state.logger
    request_id = log.extra['request_id']

    payload = {"prompt": prompt}
    headers = {
        "X-Request-Id": request_id,
        "Content-Type": "application/json",
    }
    log.debug(f"payload to send to llm: payload: {payload}")

    async with httpx.AsyncClient() as client:
        resp = await client.post(LLM_URL, json=payload, headers=headers)
        log.debug(f"status code from llm: response status: {resp.status_code}")

        resp.raise_for_status()
        data = resp.json()        
        log.debug(f"response receive from llm: {data}")

        return data["response"]

async def send_message_to_gateway(prompt: str, chat_id: str, request: Request) -> None:
    log: RequestLoggerAdapter = request.state.logger
    request_id = log.extra['request_id']
    
    correlation_id = str(uuid4())
    key = f"telegram:{chat_id}"
    content_json = json.dumps({"prompt": prompt})
    content_base64 = base64.b64encode(content_json.encode("utf-8")).decode("utf-8")

    payload = {"content": content_base64}

    headers = {
        "X-Correlation-Id": correlation_id,
        "X-Routing-Id": key,
        "X-Request-Id": request_id,
        "Content-Type": "application/json",
    }
    log.debug(f"payload to send to anyway: {payload}")
    log.info(f"key to send to anyway: {key}")
    log.info(f"header to send to anyway: correlation-id: {correlation_id}")

    async with httpx.AsyncClient() as client:
        resp = await client.post(GATEWAY_API_URL, json=payload, headers=headers)
        log.debug(f"status code from anyway: response status: {resp.status_code}")

        resp.raise_for_status()
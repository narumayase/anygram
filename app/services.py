import httpx
import json
from .config import TELEGRAM_API_URL, TELEGRAM_TOKEN, LLM_URL, KAFKA_BROKER, KAFKA_TOPIC
from kafka import KafkaProducer
import logging
from uuid import uuid4

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

def send_kafka_message(prompt: str, chat_id: str):
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: k.encode('utf-8')
    )

    correlation_id = str(uuid4())
    key = f"telegram:{chat_id}"
    headers = [
        ('correlation_id', correlation_id.encode('utf-8')),
        ('origin', b'anygram')
    ] 

    logger.debug(f"key to send to kafka: {key}")
    logger.debug(f"headers to send to kafka: {headers}")
    logger.debug(f"payload to send to kafka: {{'prompt': prompt}}")

    producer.send(
        KAFKA_TOPIC,
        key=key,
        value={"prompt": prompt},
        headers=headers
    )
    producer.flush()
    producer.close()
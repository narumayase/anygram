import httpx
import json
from .config import TELEGRAM_API_URL, TELEGRAM_TOKEN, LLM_URL, KAFKA_BROKER, KAFKA_TOPIC
from kafka import KafkaProducer

async def send_telegram_message(msg):
    url = f"{TELEGRAM_API_URL}/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": msg.chat_id, "text": msg.message_response}
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload)
        return r.json()

async def ask_llm(prompt: str) -> str:
    payload = {"prompt": prompt}
    async with httpx.AsyncClient() as client:
        resp = await client.post(LLM_URL, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["message_response"]

def send_kafka_message(prompt: str, chat_id: str):
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    headers = [('routing_id', f'telegram:{chat_id}'.encode('utf-8'))]
    producer.send(KAFKA_TOPIC, value={"prompt": prompt}, headers=headers)
    producer.flush()

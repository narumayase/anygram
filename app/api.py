from app.models import Message
from fastapi import APIRouter, Request, HTTPException
from app.services import send_telegram_message, ask_llm, send_kafka_message
from app.config import KAFKA_ENABLED
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/send")
async def send_message(request: Request, msg: Message):
    if msg.chat_id is None:
        routing_id = request.headers.get("X-Routing-ID")
        if routing_id:
            try:
                origin, chat_id = routing_id.split(":")
                if origin == "telegram":
                    msg.chat_id = chat_id
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid X-Routing-ID header format")

    if msg.chat_id is None:
        raise HTTPException(status_code=400, detail="chat_id is required")

    try:
        return await send_telegram_message(msg)
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        logger.debug("message received:", data)

        if "message" not in data or "text" not in data["message"] or "chat" not in data["message"] or "id" not in data["message"]["chat"]:
            raise HTTPException(status_code=400, detail="Invalid Telegram webhook payload")

        prompt = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]

        if KAFKA_ENABLED:
            try:
                send_kafka_message(prompt, str(chat_id))
                return {"ok": True, "source": "kafka"}
            except Exception as e:
                logger.error(f"Error sending Kafka message: {e}")
                raise HTTPException(status_code=500, detail="Error sending message to Kafka")
        else:
            try:
                llm_response = await ask_llm(prompt)
            except Exception as e:
                logger.error(f"Error querying LLM: {e}")
                raise HTTPException(status_code=500, detail="Error processing query")
            
            msg = Message(chat_id=chat_id, text=llm_response)
            
            try:
                await send_telegram_message(msg)
            except Exception as e:
                logger.error(f"Error sending Telegram response: {e}")
                raise HTTPException(status_code=500, detail="Error sending response")
            
            return {"ok": True, "source": "llm"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
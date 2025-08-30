from app.models import Message
from fastapi import APIRouter, Request, HTTPException
from app.services import send_telegram_message, ask_llm, send_message_to_gateway
from app.config import GATEWAY_ENABLED
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/send")
async def send_message(request: Request, msg: Message):
    logger.debug(f"Received message: {msg}")

    if not msg.chat_id:
        routing_id = request.headers.get("X-Routing-ID") or request.headers.get("X-Routing-Id")
        logger.debug(f"Received X-Routing-ID: {routing_id}")

        if routing_id:
            try:
                origin, chat_id = routing_id.split(":")
                if origin == "telegram":
                    msg.chat_id = chat_id
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid X-Routing-ID header format")

    if not msg.chat_id:
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

        if GATEWAY_ENABLED:
            try:
                await send_message_to_gateway(prompt, str(chat_id))
                return {"ok": True, "source": "gateway"}
            except Exception as e:
                logger.error(f"Error sending message to gateway: {e}")
                raise HTTPException(status_code=500, detail="Error sending message to gateway")
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
    
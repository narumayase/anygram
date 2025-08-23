from fastapi import APIRouter, Request, HTTPException
from app.models import TelegramMessage
from app.services import send_telegram_message, ask_llm
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/send")
async def send_message(msg: TelegramMessage):
    try:
        return await send_telegram_message(msg)
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        print("Message received:", data)
        
        # Validate required fields exist
        if "message" not in data:
            raise HTTPException(status_code=400, detail="Missing 'message' field in webhook")
        
        if "text" not in data["message"]:
            raise HTTPException(status_code=400, detail="Missing 'text' field in message")
        
        if "chat" not in data["message"] or "id" not in data["message"]["chat"]:
            raise HTTPException(status_code=400, detail="Missing chat information")
        
        prompt = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]
        
        try:
            llm_response = await ask_llm(prompt)
        except Exception as e:
            logger.error(f"Error querying LLM: {e}")
            raise HTTPException(status_code=500, detail="Error processing query")
        
        msg = TelegramMessage(chat_id=chat_id, text=llm_response)
        
        try:
            await send_telegram_message(msg)
        except Exception as e:
            logger.error(f"Error sending Telegram response: {e}")
            raise HTTPException(status_code=500, detail="Error sending response")
        
        return {"ok": True}
        
    except HTTPException:
        # Re-raise HTTPException so FastAPI can handle it correctly
        raise
    except Exception as e:
        logger.error(f"Unexpected error in webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
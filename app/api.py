from app.models import Message
from fastapi import APIRouter, Request, HTTPException
from app.services import send_telegram_message, ask_llm
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/send")
async def send_message(msg: Message):
    '''si chat_id es nulo, es porque llegó de un consumidor de kafka este request, 
    en el request buscar el header X-Routing-ID que está formado por origin:chat_id 
    donde origin = telegram y el chat_id = el chat_id
    con esos datos y el payload, enviar el mensaje a telegram.
    '''
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

        '''si está habilitado por variables de entorno, usar kafka para enviar el mensaje en vez de preguntarle a ask_llm (este servicio se "transforma" en un producer)'''
        '''tiene que mandar un header a kafka: "routing_id" que tendrá que llenarlo con origin:chat_id 
        donde origin = telegram y el chat_id = el chat_id que tenemos actualmente
        en el content de bytes del mensaje de kafka, irá el prompt con este formato {"prompt": prompt}, es el mismo json que espera la API que responde al ask_llm.
        '''

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
        
        msg = Message(chat_id=chat_id, message_response=llm_response)
        
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
    
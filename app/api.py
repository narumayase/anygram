from fastapi import APIRouter, Request
from app.models import TelegramMessage
from app.services import send_telegram_message, ask_llm

router = APIRouter()

@router.post("/send")
async def send_message(msg: TelegramMessage):
    return await send_telegram_message(msg)

@router.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    print("Mensaje recibido:", data)

    prompt = data["message"]["text"]
    chat_id = data["message"]["chat"]["id"]
    llm_response = await ask_llm(prompt)

    msg = TelegramMessage(chat_id=chat_id, text=llm_response)
    await send_telegram_message(msg)

    return {"ok": True}
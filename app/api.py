from fastapi import APIRouter, Request
from app.models import Message
from app.services import send_telegram_message, ask_llm

router = APIRouter()

@router.post("/send")
async def send_message(msg: Message):
    '''si chat_id es nulo, es porque llegó de un consumidor de kafka este request, 
    en el request buscar el header X-Routing-ID que está formado por origin:chat_id 
    donde origin = telegram y el chat_id = el chat_id
    con esos datos y el payload, enviar el mensaje a telegram.
    '''
    return await send_telegram_message(msg)

@router.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    print("Mensaje recibido:", data)

    prompt = data["message"]["text"]
    chat_id = data["message"]["chat"]["id"]

    '''si está habilitado por variables de entorno, usar kafka para enviar el mensaje en vez de preguntarle a ask_llm (este servicio se "transforma" en un producer)'''
    '''tiene que mandar un header a kafka: "routing_id" que tendrá que llenarlo con origin:chat_id 
    donde origin = telegram y el chat_id = el chat_id que tenemos actualmente
    en el content de bytes del mensaje de kafka, irá el prompt con este formato {"prompt": prompt}, es el mismo json que espera la API que responde al ask_llm.
    '''
    llm_response = await ask_llm(prompt)

    msg = Message(chat_id=chat_id, message_response=llm_response)
    await send_telegram_message(msg)

    return {"ok": True}
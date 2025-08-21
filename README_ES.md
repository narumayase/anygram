# anygram API

anygram es una API construida con FastAPI que permite enviar y recibir mensajes a través de un bot de Telegram, integrando respuestas automáticas generadas por un modelo LLM (Large Language Model).

La API expone dos endpoints principales:

- **`/telegram/send`**: Permite enviar mensajes a cualquier chat de Telegram a través del bot.
- **`/telegram/webhook`**: Recibe mensajes enviados al bot desde Telegram, envía el texto recibido a una API LLM y responde automáticamente al usuario con la respuesta generada.

## Estructura del Proyecto

```
anygram
├── app
│   ├── api.py              # Endpoints 
│   ├── models.py           # Modelos Pydantic o entidades simples
│   ├── services.py         # Integraciones (Telegram, LLM)
│   ├── config.py           # Configuración (dotenv, etc.)
│   └── main.py             # Punto de entrada
├── requirements.txt
└── README.md
```

## Configuración

1. Crear un entorno virtual:
   ```
   python -m venv venv
   source venv/bin/activate  # En Windows usar `venv\Scripts\activate`
   ```

2. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```

3. Crear un archivo `.env`:
   ```
   # Configuración de Telegram (obligatoria)
   TELEGRAM_TOKEN=tu_api_token
   TELEGRAM_API_URL="https://api.telegram.org"

   # Configuración del LLM (obligatoria)   
   LLM_URL=http://localhost:8081/api/v1/chat/ask

   # Configuración del servidor (opcional)
   HOST=127.0.0.1
   PORT=8000
   RELOAD=true
   ```

## Uso

Para ejecutar la aplicación:
```
uvicorn app.main:app --host $HOST --port $PORT
```

Por defecto, la API estará disponible en `http://127.0.0.1:8000`.

## Endpoints

### GET /health

Chequea el estado de la API.

```json
{
   "message": "anygram API is working!",
   "status": "ok",
   "host": "localhost",
   "port": "8000"
}
```

### Enviar un Mensaje

Hacer un POST a `/telegram/send` envía un mensaje a través del bot de Telegram usando el siguiente cuerpo:

```json
{
  "chat_id": "123456789",
  "text": "Tu mensaje aquí"
}
```

### Webhook (Recibir y Responder Mensajes)

El endpoint `/telegram/webhook` recibe mensajes de Telegram y responde automáticamente usando la integración con la API LLM.

**Ejemplo de Configuración del Webhook:**

1. Exponer la API local usando [ngrok](https://ngrok.com/):
   ```
   ngrok http 8000
   ```

2. Configurar el webhook en Telegram:
   ```
   curl -X POST "https://api.telegram.org/bot<TELEGRAM_TOKEN>/setWebhook?url=https://<NGROK_URL>/telegram/webhook"
   ```
   Reemplazar `<TELEGRAM_TOKEN>` y `<NGROK_URL>` por los valores correctos.

**Cómo funciona:**  

Cuando el bot recibe un mensaje, el texto se envía a la API LLM, por ejemplo: `http://localhost:8081/api/v1/chat/ask`, la cual debería responder con un JSON:

```json
{
  "response": "Texto de la respuesta"
}
```
El bot luego reenvía esa respuesta al usuario en Telegram.

## Variables de Entorno

- `TELEGRAM_TOKEN`: Token del bot de Telegram (almacenado en `.env`).
- `TELEGRAM_API_URL`: URL de Telegram (almacenado en `.env`).
- `LLM_URL`: URL del LLM (almacenado en `.env`).
- `HOST`: Host de la API (almacenado en `.env`).
- `PORT`: Puerto de la API (almacenado en `.env`).

## BackLog

- [ ] Test Unitarios.

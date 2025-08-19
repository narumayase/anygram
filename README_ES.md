# AnyGram API

AnyGram es una API construida con FastAPI que permite enviar y recibir mensajes a través de un bot de Telegram, integrando respuestas automáticas generadas por un modelo LLM (Large Language Model).

La API expone dos endpoints principales:

- **`/telegram/send`**: Permite enviar mensajes a cualquier chat de Telegram mediante el bot.
- **`/telegram/webhook`**: Recibe mensajes enviados al bot desde Telegram, reenvía el texto recibido a una API LLM y responde automáticamente al usuario con la respuesta generada.

## Estructura del proyecto

```
anygram
├── app
│   ├── api.py              # Endpoints 
│   ├── models.py           # Pydantic models o entidades simples
│   ├── services.py         # Integraciones (Telegram, LLM)
│   ├── config.py           # Configuración (dotenv, etc.)
│   └── main.py             # Punto de entrada
├── requirements.txt
└── README.md
```

## Setup

1. Crear un entorno virtual:
   ```
   python -m venv venv
   source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
   ```

2. Instalar las dependencias:
   ```
   pip install -r requirements.txt
   ```

3. Crear un archivo `.env` con tu token de bot de Telegram:
   ```
   TELEGRAM_TOKEN=your_api_token
   ```

## Usage

Para correr la aplicación:
```
uvicorn app.main:app --reload
```
Por defecto la API estará disponible en `http://127.0.0.1:8000`.

### Enviar un mensaje

El POST a `/telegram/send` envía un mensaje al bot de Telegram, utilizando el siguiente body:

```json
{
  "chat_id": "123456789",
  "text": "Your message here"
}
```

### Webhook (Recibir y responder mensajes)

El endpoint `/telegram/webhook` recibe mensajes de Telegram y responde automáticamente usando la integración con la API LLM.

**Configuración del webhook:**

1. Exponer la API local usando [ngrok](https://ngrok.com/):
   ```
   ngrok http 8000
   ```

2. Configurar el webhook en Telegram:
   ```
   curl -X POST "https://api.telegram.org/bot<TELEGRAM_TOKEN>/setWebhook?url=https://<NGROK_URL>/telegram/webhook"
   ```
   Reemplazar `<TELEGRAM_TOKEN>` y `<NGROK_URL>` por los valores correspondientes.

**Funcionamiento:**  

Cuando el bot recibe un mensaje, el texto se envía a la API LLM (`http://localhost:8081/api/v1/chat/ask`), que debe responder con un JSON:

```json
{
  "response": "Texto de respuesta"
}
```
El bot reenvía esa respuesta al usuario en Telegram.

## Variables de entorno

- `TELEGRAM_TOKEN`: Token del bot de Telegram (en `.env`).

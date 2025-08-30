# anygram API

anygram es una API construida con FastAPI que permite enviar y recibir mensajes a través de un bot de Telegram, integrando respuestas automáticas generadas por un LLM (Large Language Model).

La API expone dos endpoints principales:

- **`/telegram/send`**: Permite enviar mensajes a cualquier chat de Telegram a través del bot.
- **`/telegram/webhook`**: Recibe mensajes enviados al bot desde Telegram, reenvía el texto recibido a una API de LLM y responde automáticamente al usuario con la respuesta generada.

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

1. Crea un entorno virtual:
   ```
   python -m venv venv
   source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
   ```

2. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

3. Crea un archivo `.env`:
   ```
   # Configuración de Telegram (obligatorio)
   TELEGRAM_TOKEN=tu_token_api
   TELEGRAM_API_URL="https://api.telegram.org"

   # Configuración de LLM (obligatorio)
   LLM_URL=http://localhost:8081/api/v1/chat/ask

   # Configuración del servidor (opcional)
   HOST=127.0.0.1
   PORT=8000
   RELOAD=true
   LOG_LEVEL=INFO

   # Configuración de Gateway (opcional)
   GATEWAY_ENABLED=true
   GATEWAY_URL=http://localhost:8003/api/v1/send
   ```

## Variables de Entorno

- `TELEGRAM_TOKEN`: Token del bot de Telegram (obligatorio).
- `TELEGRAM_API_URL`: URL de la API de Telegram (opcional, por defecto `https://api.telegram.org`).
- `LLM_URL`: URL de la API de LLM (opcional, por defecto `http://localhost:8081/api/v1/chat/ask`).
- `HOST`: Host de la API (opcional, por defecto `127.0.0.1`).
- `PORT`: Puerto de la API (opcional, por defecto `8000`).
- `RELOAD`: Habilita la recarga automática del servidor (opcional, por defecto `true`).
- `LOG_LEVEL`: Nivel de registro (opcional, por defecto `INFO`).
- `GATEWAY_ENABLED`: Habilita la integración con Gateway (opcional, por defecto `false`).
- `GATEWAY_URL`: Dirección del Gateway (opcional, por defecto `http://localhost:8003/api/v1/send`).

## Uso

Para ejecutar la aplicación:
```
uvicorn app.main:app --host $HOST --port $PORT
```

Por defecto, la API estará disponible en `http://127.0.0.1:8000`.

## Integración con Gateway

Esta API soporta la integración con un Gateway para el procesamiento asíncrono de mensajes. Cuando el Gateway está habilitado, los mensajes entrantes de los webhooks de Telegram se enviarán a un Gateway en lugar de ser procesados directamente por el LLM.

Para habilitar la integración con Gateway, establece la variable de entorno `GATEWAY_ENABLED` a `true` en tu archivo `.env`:

```
GATEWAY_ENABLED=true
GATEWAY_URL=http://localhost:8003/api/v1/send
```

Cuando `GATEWAY_ENABLED` es `true`:
- El endpoint `/telegram/webhook` enviará el mensaje entrante al Gateway configurado.
- La API responderá inmediatamente con `{"ok": True, "source": "gateway"}`.
- El procesamiento real del LLM y la respuesta de Telegram serán manejados por un servicio consumidor separado.

Si `GATEWAY_ENABLED` es `false` (por defecto), la API procesará los mensajes de forma síncrona usando el LLM y responderá directamente a través de Telegram, como se describe en la sección "Webhook".

## Endpoints

### GET /health

Verifica el estado de la API.

```json
{
   "message": "anygram API is working!",
   "status": "ok",
   "host": "localhost",
   "port": "8000"
}
```

### Enviar un Mensaje

POST a `/telegram/send` envía un mensaje a través del bot de Telegram usando el siguiente cuerpo:

```json
{
  "chat_id": "123456789",
  "text": "Tu mensaje aquí"
}
```

### Webhook (Recibir y Responder Mensajes)

El endpoint `/telegram/webhook` recibe mensajes de Telegram y responde automáticamente usando la integración con la API de LLM.

**Ejemplo de Configuración de Webhook:**

1. Expón la API local usando [ngrok](https://ngrok.com/):
   ```
   ngrok http 8000
   ```

2. Configura el webhook en Telegram:
   ```
   curl -X POST "https://api.telegram.org/bot<TELEGRAM_TOKEN>/setWebhook?url=https://<NGROK_URL>/telegram/webhook"
   ```
   Reemplaza `<TELEGRAM_TOKEN>` y `<NGROK_URL>` con los valores correctos.

# Pruebas

- Todas las pruebas:

```bash
pytest
```

- Todas las pruebas con cobertura:

```bash
pytest --cov=app --cov-report=term-missing tests/
```

## BackLog

- [x] Pruebas Unitarias.
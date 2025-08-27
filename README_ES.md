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
   LOG_LEVEL=INFO

   # Configuración de Kafka (opcional)
   KAFKA_ENABLED=false
   KAFKA_BROKER=localhost:9092
   KAFKA_TOPIC=anygram.prompts
   ```
   
## Variables de Entorno

- `TELEGRAM_TOKEN`: Token del bot de Telegram (obligatorio).
- `TELEGRAM_API_URL`: URL de la API de Telegram (opcional, por defecto `https://api.telegram.org`).
- `LLM_URL`: URL de la API del LLM (opcional, por defecto `http://localhost:8081/api/v1/chat/ask`).
- `HOST`: Host de la API (opcional, por defecto `127.0.0.1`).
- `PORT`: Puerto de la API (opcional, por defecto `8000`).
- `RELOAD`: Habilitar la recarga automática del servidor (opcional, por defecto `true`).
- `LOG_LEVEL`: Nivel de registro (opcional, por defecto `INFO`).
- `KAFKA_ENABLED`: Habilitar la integración con Kafka (opcional, por defecto `false`).
- `KAFKA_BROKER`: Dirección del broker de Kafka (opcional, por defecto `localhost:9092`).
- `KAFKA_TOPIC`: Tema de Kafka para los prompts (opcional, por defecto `anygram.prompts`).

## Uso

Para ejecutar la aplicación:
```
uvicorn app.main:app --host $HOST --port $PORT
```

Por defecto, la API estará disponible en `http://127.0.0.1:8000`.

## Integración con Kafka

Esta API soporta la integración con Kafka para el procesamiento asíncrono de mensajes. Cuando Kafka está habilitado, los mensajes entrantes de los webhooks de Telegram se enviarán a un tema de Kafka en lugar de ser procesados directamente por el LLM.

Para habilitar la integración con Kafka, establece la variable de entorno `KAFKA_ENABLED` a `true` en tu archivo `.env`:

```
KAFKA_ENABLED=true
KAFKA_BROKER=localhost:9092  # Dirección de tu broker de Kafka
KAFKA_TOPIC=anygram.prompts  # El tema al que se enviarán los mensajes
```

Cuando `KAFKA_ENABLED` es `true`:
- El endpoint `/telegram/webhook` enviará el mensaje entrante al tema de Kafka configurado.
- La API responderá inmediatamente con `{"ok": True, "source": "kafka"}`.
- El procesamiento real del LLM y la respuesta de Telegram serán manejados por un servicio consumidor separado que lee del tema de Kafka.

Si `KAFKA_ENABLED` es `false` (por defecto), la API procesará los mensajes de forma síncrona usando el LLM y responderá directamente a través de Telegram, como se describe en la sección "Webhook".

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

# Testing

- Todos los tests:

```bash
pytest
```

- Todos los tests con su coverage:

```bash
pytest --cov=app --cov-report=term-missing tests/
```

## BackLog

- [x] Test Unitarios.

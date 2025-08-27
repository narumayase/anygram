FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Variables de entorno por defecto (pueden ser sobreescritas en docker run)
ENV HOST=0.0.0.0
ENV PORT=8000

EXPOSE ${PORT}

CMD ["sh", "-c", "uvicorn app.main:app --host $HOST --port $PORT"]
# docker run -p 8000:8000 anygram
# docker run --env HOST=0.0.0.0 --env PORT=9000 -p 9000:9000 anygram
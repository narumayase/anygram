from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api import router
from app.logger import logger, RequestLoggerAdapter
from app.config import validate_config, HOST, PORT, RELOAD
from uuid import uuid4
import uvicorn

validate_config()

app = FastAPI(
    title="anygram API",
    description="FastAPI Telegram Integration with LLM",
    version="1.0.0"
)

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    request.state.logger = RequestLoggerAdapter(logger, {"request_id": request_id})
    response = await call_next(request)
    return response

app.include_router(router, prefix="/telegram", tags=["telegram"])

@app.get("/health")
def healthcheck():
    return {
        "message": "anygram API is working!",
        "status": "ok",
        "host": HOST,
        "port": PORT
    }

# Global error handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=RELOAD
    )
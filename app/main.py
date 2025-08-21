from fastapi import FastAPI
from app.api import router
from app.config import validate_config, HOST, PORT, RELOAD
import uvicorn

validate_config()

app = FastAPI(
    title="anygram API",
    description="FastAPI Telegram Integration with LLM",
    version="1.0.0"
)

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
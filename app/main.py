from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api import router 

app = FastAPI()

app.include_router(router, prefix="/telegram", tags=["telegram"])

@app.get("/health")
def healthcheck():
    return {"status": "ok"}

# Handler global de errores
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )
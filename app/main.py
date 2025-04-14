import logging
import time

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import auth, product, pvz, reception
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Avito PVZ API",
    description="API для управления ПВЗ",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        logger.info(f"Request processed in {process_time:.4f} seconds: {request.method} {request.url.path}")
        return response
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal server error"}
        )


app.include_router(auth.router, tags=["Авторизация"])
app.include_router(pvz.router, tags=["ПВЗ"])
app.include_router(reception.router, tags=["Приемки"])
app.include_router(product.router, tags=["Товары"])


@app.get("/health", tags=["Проверка"], summary="Тестовая ручка")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True,
    )

"""StoryMood API. Run with `python main.py` from this folder."""
import logging
import os
import sys

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

import config
from database.dynamodb import dynamodb_client
from providers import registry
from providers.base import ProviderError
from routers import api_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                    handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("storymood")

app = FastAPI(
    title="StoryMood API",
    description="Kid-friendly stories written, narrated and listened to by pluggable AI providers.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to the frontend origin in production
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ProviderError)
async def provider_error_handler(request: Request, exc: ProviderError):
    return JSONResponse(status_code=502, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Something went wrong. Please try again."})


@app.on_event("startup")
async def startup() -> None:
    os.makedirs(config.AUDIO_FILES_DIR, exist_ok=True)
    for capability, info in registry.describe().items():
        if info.get("error"):
            logger.warning("%s provider '%s' unavailable: %s", capability, info["provider"], info["error"])
        else:
            logger.info("%s -> %s %s", capability, info["provider"], info["model"] or "")
    if config.AWS_ACCESS_KEY_ID:
        await dynamodb_client.create_tables_if_not_exist()
    else:
        logger.info("Story vault disabled (no AWS credentials)")


app.include_router(api_router, prefix=config.API_V1_PREFIX)
app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
async def root():
    return {
        "app": "StoryMood API",
        "message": "This is the backend. Open the app at http://localhost:3000 or the API docs at /docs.",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "providers": registry.describe()}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=config.APP_ENV == "development")

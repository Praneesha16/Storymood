"""StoryMood API. Run with `python main.py` from this folder."""
import logging
import os
import sys

import uvicorn
import re

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

import config
from database.dynamodb import dynamodb_client
from providers import registry
from providers.base import ProviderError
from services.moderation import ContentRefused
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
    allow_origins=config.ALLOWED_ORIGINS,  # set ALLOWED_ORIGINS to the app's address in production
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ContentRefused)
async def content_refused_handler(request: Request, exc: ContentRefused):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


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
    logger.info("auth -> %s%s", config.AUTH_MODE, "" if config.AUTH_MODE != "none" else " (guests; set AUTH_MODE=cognito for sign-in)")
    logger.info("moderation -> %s, rate limits -> %s", config.MODERATION, "on" if config.RATE_LIMITS else "off")
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


@app.get("/static/audio/{filename}", include_in_schema=False)
async def audio_file(filename: str, request: Request):
    """Narration files with HTTP Range support, so browsers can seek (Starlette's StaticFiles cannot)."""
    path = os.path.join(config.AUDIO_FILES_DIR, os.path.basename(filename))
    if not os.path.isfile(path):
        raise HTTPException(status_code=404)
    size = os.path.getsize(path)
    headers = {"Accept-Ranges": "bytes", "Cache-Control": "public, max-age=31536000, immutable"}
    media = "audio/mpeg" if path.endswith(".mp3") else "application/octet-stream"
    wanted = re.match(r"bytes=(\d*)-(\d*)$", request.headers.get("range", ""))
    if not wanted:
        return FileResponse(path, media_type=media, headers=headers)
    first, last = wanted.groups()
    start = int(first) if first else max(0, size - int(last or 0))
    end = min(int(last), size - 1) if (last and first) else size - 1
    if start >= size or start > end:
        raise HTTPException(status_code=416, headers={"Content-Range": f"bytes */{size}"})

    def body():
        with open(path, "rb") as fh:
            fh.seek(start)
            remaining = end - start + 1
            while remaining > 0:
                chunk = fh.read(min(256 * 1024, remaining))
                if not chunk:
                    break
                remaining -= len(chunk)
                yield chunk

    headers.update({"Content-Range": f"bytes {start}-{end}/{size}", "Content-Length": str(end - start + 1)})
    return StreamingResponse(body(), status_code=206, media_type=media, headers=headers)


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

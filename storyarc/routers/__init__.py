from fastapi import APIRouter

from .catalog import router as catalog_router
from .session import router as session_router
from .story import router as story_router
from .vault import router as vault_router
from .video import router as video_router
from .voice import router as voice_router

api_router = APIRouter()
api_router.include_router(catalog_router, prefix="/catalog", tags=["Catalog"])
api_router.include_router(story_router, prefix="/story", tags=["Story"])
api_router.include_router(voice_router, prefix="/voice", tags=["Voice"])
api_router.include_router(video_router, prefix="/video", tags=["Video"])
api_router.include_router(vault_router, prefix="/vault", tags=["Story Vault"])
api_router.include_router(session_router, prefix="/session", tags=["Session"])

__all__ = ["api_router"]

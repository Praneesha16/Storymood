from fastapi import APIRouter

from .story import router as story_router
from .voice import router as voice_router
from .vault import router as vault_router
from .session import router as session_router

# Create main router
api_router = APIRouter()

# Include all routers with appropriate prefixes
api_router.include_router(story_router, prefix="/story", tags=["Story Generation"])
api_router.include_router(voice_router, prefix="/voice", tags=["Voice Narration"])
api_router.include_router(vault_router, prefix="/vault", tags=["Story Vault"])
api_router.include_router(session_router, prefix="/session", tags=["Session Management"])

__all__ = ['api_router']

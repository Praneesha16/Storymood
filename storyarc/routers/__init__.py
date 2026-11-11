from fastapi import APIRouter, Depends

from services.auth import require_user

from .auth import router as auth_router
from .catalog import router as catalog_router
from .library import admin as admin_router, community as community_router, library as library_router
from .music import router as music_router
from .session import router as session_router
from .story import router as story_router
from .vault import router as vault_router
from .video import router as video_router
from .voice import router as voice_router

api_router = APIRouter()
# Open: what the app needs before anyone signs in.
api_router.include_router(auth_router, prefix="/auth", tags=["Sign-in"])
api_router.include_router(catalog_router, prefix="/catalog", tags=["Catalog"])
api_router.include_router(music_router, prefix="/music", tags=["Music"])
api_router.include_router(community_router, prefix="/community", tags=["Community"])
# Protected: everything that costs money or touches a family's stories.
signed_in = [Depends(require_user)]
api_router.include_router(story_router, prefix="/story", tags=["Story"], dependencies=signed_in)
api_router.include_router(voice_router, prefix="/voice", tags=["Voice"], dependencies=signed_in)
api_router.include_router(video_router, prefix="/video", tags=["Video"], dependencies=signed_in)
api_router.include_router(library_router, prefix="/library", tags=["Library"], dependencies=signed_in)
api_router.include_router(admin_router, prefix="/admin", tags=["Review"], dependencies=signed_in)
api_router.include_router(vault_router, prefix="/vault", tags=["Story Vault"], dependencies=signed_in)
api_router.include_router(session_router, prefix="/session", tags=["Session"], dependencies=signed_in)

__all__ = ["api_router"]

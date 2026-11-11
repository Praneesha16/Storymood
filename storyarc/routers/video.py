from fastapi import APIRouter, HTTPException, status

from models.story_model import VideoRequest, VideoResponse
from providers import registry

router = APIRouter()


@router.post(
    "/generate",
    response_model=VideoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Turn a story into a video (needs a video adapter)",
)
async def generate_video(request: VideoRequest):
    provider = registry.video()
    if not provider.enabled:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Video generation is not set up. Set VIDEO_PROVIDER in storyarc/.env.",
        )
    data = await provider.generate(request.story_text, request.title, request.language)
    return VideoResponse(provider=provider.name, data=data)

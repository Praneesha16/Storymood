from fastapi import APIRouter, status

from models.story_model import StoryRequest, StoryResponse
from services import story_service

router = APIRouter()


@router.post(
    "/generate",
    response_model=StoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Write a new children's story",
)
async def generate_story(request: StoryRequest):
    return await story_service.generate(request)

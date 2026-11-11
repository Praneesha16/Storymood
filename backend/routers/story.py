from fastapi import APIRouter, Depends, status

import config
from models.story_model import IllustrateRequest, IllustrateResponse, StoryRequest, StoryResponse
from services import illustrate_service, library_service, moderation, ratelimit, story_service
from services.auth import User, current_user

router = APIRouter()


@router.post(
    "/generate",
    response_model=StoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Write a new children's story",
)
async def generate_story(request: StoryRequest, user: User = Depends(current_user)):
    ratelimit.hit(user.id, "story", config.STORIES_PER_HOUR)
    await moderation.check(
        texts=moderation.story_inputs(request.idea, (c.name for c in request.characters), (c.trait for c in request.characters))
    )
    await library_service.spend_story(user)
    story = await story_service.generate(request)
    record = await library_service.create(user, story)
    story.id = record["id"]
    return story


@router.post(
    "/illustrate",
    response_model=IllustrateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Paint one picture for a page or the cover",
)
async def illustrate(request: IllustrateRequest, user: User = Depends(current_user)):
    ratelimit.hit(user.id, "picture", config.PICTURES_PER_HOUR)
    await moderation.check(texts=[r.name for r in request.references], images=[r.image for r in request.references])
    result = await illustrate_service.illustrate(request)
    if request.story_id and request.key:
        await library_service.attach_picture(request.story_id, user, request.key, result.image_url, bool(request.references))
    return result

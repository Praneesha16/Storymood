from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

import config
from models.story_model import NarrationRequest, NarrationResponse, TranscriptionResponse, VoiceCloneResponse
from services import library_service, ratelimit, transcribe_service, voice_service
from services.auth import User, current_user

router = APIRouter()


@router.post(
    "/narrate",
    response_model=NarrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Read text aloud with a narrator voice",
)
async def narrate(request: NarrationRequest, user: User = Depends(current_user)):
    ratelimit.hit(user.id, "narration", config.NARRATIONS_PER_HOUR)
    result = await voice_service.narrate(request)
    if request.story_id:
        await library_service.attach_audio(request.story_id, user, result.audio_url, [c.dict() for c in result.cues])
    return result


@router.post(
    "/transcribe",
    response_model=TranscriptionResponse,
    summary="Turn a recorded idea into text",
)
async def transcribe(
    file: UploadFile = File(..., description="Audio recording (webm, mp3, wav, m4a, ogg)"),
    language: Optional[str] = Form(None, description="ISO-639-1 hint; omit to auto-detect"),
):
    audio = await file.read()
    return await transcribe_service.transcribe(
        audio, file.filename or "recording.webm", file.content_type or "", language
    )


@router.post(
    "/clone",
    response_model=VoiceCloneResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a family voice from a short recording",
)
async def clone_voice(
    file: UploadFile = File(..., description="A 5 to 20 second recording of one person reading"),
    name: str = Form("My voice"),
    language: str = Form("en"),
    user: User = Depends(current_user),
):
    ratelimit.hit(user.id, "clone", 5)
    audio = await file.read()
    return await voice_service.clone(audio, file.filename or "clip.webm", file.content_type or "", name, language)

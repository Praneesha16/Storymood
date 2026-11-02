from typing import Optional

from fastapi import APIRouter, File, Form, UploadFile, status

from models.story_model import NarrationRequest, NarrationResponse, TranscriptionResponse, VoiceCloneResponse
from services import transcribe_service, voice_service

router = APIRouter()


@router.post(
    "/narrate",
    response_model=NarrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Read text aloud with a narrator voice",
)
async def narrate(request: NarrationRequest):
    return await voice_service.narrate(request)


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
):
    audio = await file.read()
    return await voice_service.clone(audio, file.filename or "clip.webm", file.content_type or "", name, language)

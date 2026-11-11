"""Reads a story aloud with the configured TTS adapter and serves the file from /static/audio."""
import asyncio
import logging
import os
import re
import shutil
import tempfile
import uuid
from dataclasses import replace
from typing import List, Optional, Tuple

import catalog
import config
from models.story_model import NarrationCue, NarrationRequest, NarrationResponse, NarrationSegment, VoiceCloneResponse
from providers import registry
from providers.base import ProviderError, VoiceSpec
from services import mixer

logger = logging.getLogger(__name__)

PARALLEL_CHUNKS = 3


def _sentences(paragraph: str, max_chars: int) -> List[str]:
    """Split one over-long paragraph on sentence ends."""
    out: List[str] = []
    current = ""
    for sentence in re.split(r"(?<=[.!?।])\s+", paragraph):
        if current and len(current) + len(sentence) + 1 > max_chars:
            out.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        out.append(current)
    return out


def _chunks(text: str, max_chars: int) -> List[str]:
    """Pack paragraphs into the fewest requests that stay under the vendor's limit.

    Paragraph breaks are kept inside a chunk so the voice still pauses between them.
    """
    text = re.sub(r"[ \t]+", " ", text).strip()
    units: List[str] = []
    for paragraph in re.split(r"\n\s*\n", text):
        paragraph = paragraph.strip()
        if paragraph:
            units.extend([paragraph] if len(paragraph) <= max_chars else _sentences(paragraph, max_chars))

    pieces: List[str] = []
    current = ""
    for unit in units:
        if current and len(current) + len(unit) + 2 > max_chars:
            pieces.append(current)
            current = unit
        else:
            current = f"{current}\n\n{unit}" if current else unit
    if current:
        pieces.append(current)
    return pieces


Chunk = Tuple[str, str, List[Tuple[int, int]]]  # text, mood, [(segment index, characters it contributes)]


def _mood_chunks(segments: List[NarrationSegment], max_chars: int) -> List[Chunk]:
    """Like _chunks, but a chunk never mixes moods, so each request can carry one emotion.
    Each chunk remembers which segments it holds so timings can be handed back as cues."""
    pieces: List[Chunk] = []
    current, current_mood = "", ""
    members: List[Tuple[int, int]] = []
    for index, seg in enumerate(segments):
        text = re.sub(r"[ \t]+", " ", seg.text).strip()
        if not text:
            continue
        for unit in ([text] if len(text) <= max_chars else _sentences(text, max_chars)):
            if current and (seg.mood != current_mood or len(current) + len(unit) + 2 > max_chars):
                pieces.append((current, current_mood, members))
                current, members = unit, [(index, len(unit))]
            else:
                current = f"{current}\n\n{unit}" if current else unit
                members.append((index, len(unit)))
            current_mood = seg.mood
    if current:
        pieces.append((current, current_mood, members))
    return pieces


def _cues(chunks: List[Chunk], seconds: List[float], offset: float) -> List[NarrationCue]:
    """Spread each measured chunk length over its segments by character count."""
    start: dict = {}
    end: dict = {}
    clock = offset
    for (_, _, members), secs in zip(chunks, seconds):
        total = sum(n for _, n in members) or 1
        for index, n in members:
            share = secs * n / total
            start.setdefault(index, clock)
            clock += share
            end[index] = clock
    return [NarrationCue(index=i, start=round(start[i], 2), end=round(end[i], 2)) for i in sorted(start)]


def _emotion(mood_id: str) -> str:
    entry = catalog.mood(mood_id) if mood_id else None
    return entry.get("emotion", "") if entry else ""


def _music_runs(moods: List[str], seconds: List[float]) -> List[Tuple[str, float]]:
    """Collapse per-chunk moods into runs long enough to change the music for."""
    runs: List[List] = []
    for mood_id, secs in zip(moods, seconds):
        if runs and runs[-1][0] == mood_id:
            runs[-1][1] += secs
        else:
            runs.append([mood_id, secs])
    # The opening mood always gets its own track; later moods only when they last long enough.
    merged: List[List] = []
    for mood_id, secs in runs:
        if merged and secs < config.MUSIC_MIN_RUN_SECONDS:
            merged[-1][1] += secs  # too short to switch: stay on the current track
        else:
            merged.append([mood_id, secs])
    return [(m, s) for m, s in merged]


async def _music_for(runs: List[Tuple[str, float]]) -> List[mixer.MusicRun]:
    music = registry.music()
    out: List[mixer.MusicRun] = []
    last_path: Optional[str] = None
    for mood_id, secs in runs:
        entry = catalog.mood(mood_id) or {}
        url = await music.pick(mood_id or "calm", entry.get("like", []))
        path = music.local_path(url) if url else None
        if not path:
            path = last_path  # keep whatever was playing rather than fall silent
        if path:
            out.append(mixer.MusicRun(path=path, seconds=secs))
            last_path = path
    return out


async def narrate(req: NarrationRequest) -> NarrationResponse:
    tts = registry.tts()
    pitch = 1.0
    if req.voice_id:
        # A custom (cloned) voice: plain, slightly slow storytelling pace.
        voice_id = req.voice_id
        spec = VoiceSpec(voice=voice_id, speed=0.95, style="A warm family member reading a story to a child.")
    else:
        entry = catalog.narrator(req.narrator)
        voice_id = catalog.resolve_voice(req.narrator, tts.name, req.language)
        if not voice_id:
            raise ProviderError(
                f"The '{entry['label']}' narrator cannot read {catalog.language(req.language)['label']} with {tts.name}. "
                "Pick another narrator, or add a voice under 'voices' in catalog.py."
            )
        spec = VoiceSpec(voice=voice_id, speed=entry.get("speed", 1.0), style=entry.get("style", ""))
        pitch = catalog.resolve_pitch(req.narrator, req.language)

    if req.segments:
        parts = _mood_chunks(req.segments, tts.max_chars)
    else:
        parts = [(p, "", []) for p in _chunks(req.text, tts.max_chars)]
    logger.info(
        "Narrating %d chunk(s) via %s/%s voice=%s lang=%s moods=%s",
        len(parts), tts.name, tts.model, voice_id, req.language, [m or "-" for _, m, _ in parts],
    )

    semaphore = asyncio.Semaphore(PARALLEL_CHUNKS)

    async def synth(part: str, mood_id: str) -> bytes:
        async with semaphore:
            return await tts.synthesize(part, replace(spec, emotion=_emotion(mood_id)), req.language)

    audio_parts = await asyncio.gather(*(synth(p, m) for p, m, _ in parts))

    os.makedirs(config.AUDIO_FILES_DIR, exist_ok=True)
    filename = f"{uuid.uuid4()}.{tts.audio_format}"
    files = registry.files()

    if not mixer.available():
        url = await files.save("audio", filename, b"".join(audio_parts), "audio/mpeg")
        return NarrationResponse(audio_url=url, provider=tts.name, voice=voice_id)

    # With ffmpeg: join the chunks properly, even out the loudness, and lay music under them.
    with_music = False
    cues: List[NarrationCue] = []
    work = tempfile.mkdtemp(prefix="narrate-", dir=config.AUDIO_FILES_DIR)
    out_path = os.path.join(work, "mixed.mp3")
    try:
        chunk_files = []
        for i, blob in enumerate(audio_parts):
            path = os.path.join(work, f"{i:03d}.{tts.audio_format}")
            with open(path, "wb") as fh:
                fh.write(blob)
            chunk_files.append(path)
        seconds = list(await asyncio.gather(*(asyncio.to_thread(mixer.duration, f) for f in chunk_files)))
        voice_seconds = sum(seconds)
        music_runs: List[mixer.MusicRun] = []
        if req.music and registry.music().enabled:
            music_runs = await _music_for(_music_runs([m for _, m, _ in parts], seconds))
        with_music = await asyncio.to_thread(mixer.mix, chunk_files, music_runs, voice_seconds, out_path, pitch)
        if req.segments:
            cues = _cues(parts, seconds, config.MUSIC_INTRO_SECONDS if with_music else 0.0)
        with open(out_path, "rb") as fh:
            mixed = fh.read()
        logger.info("Mixed %s: %.0fs voice, %d music run(s), %d cue(s), pitch %.2f", filename, voice_seconds, len(music_runs), len(cues), pitch)
    except Exception as exc:  # noqa: BLE001 - the voice must still come through
        logger.warning("Mixing failed (%s); serving the plain narration", exc)
        mixed = b"".join(audio_parts)
        with_music = False
        cues = []
    finally:
        shutil.rmtree(work, ignore_errors=True)

    url = await files.save("audio", filename, mixed, "audio/mpeg")
    return NarrationResponse(audio_url=url, provider=tts.name, voice=voice_id, music=with_music, cues=cues)


MIN_CLIP_BYTES = 20_000  # roughly 3 seconds of compressed audio


async def clone(audio: bytes, filename: str, content_type: str, name: str, language: str) -> VoiceCloneResponse:
    tts = registry.tts()
    if not tts.supports_cloning:
        raise ProviderError(f"The '{tts.name}' voice provider cannot clone voices. Switch TTS_PROVIDER to one that can.")
    if len(audio) < MIN_CLIP_BYTES:
        raise ProviderError("That recording is too short. Read the whole sentence, about ten seconds.")
    if len(audio) > config.MAX_UPLOAD_BYTES:
        raise ProviderError("That recording is too long. Keep it under a minute.")
    clean_name = (name or "My voice").strip()[:60] or "My voice"
    logger.info("Cloning voice '%s' via %s (%d bytes, lang=%s)", clean_name, tts.name, len(audio), language)
    voice_id = await tts.clone_voice(audio, filename, content_type, clean_name, language)
    return VoiceCloneResponse(voice_id=voice_id, name=clean_name, provider=tts.name)

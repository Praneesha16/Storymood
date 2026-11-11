"""Maps the provider names used in .env to adapter classes.

To add a vendor:
  1. Create providers/<vendor>_<capability>.py with a class extending the matching base
     class from providers/base.py.
  2. Add one line to ADAPTERS below.
  3. Set LLM_PROVIDER / TTS_PROVIDER / STT_PROVIDER / VIDEO_PROVIDER / MUSIC_PROVIDER in .env.
  4. If the vendor needs its own voice ids, add them under "voices" in catalog.py.
"""
import functools
import importlib
from typing import Dict, List

import config
from providers.base import FileStore, ImageProvider, LLMProvider, MusicProvider, ProviderError, STTProvider, StoreProvider, TTSProvider, VideoProvider

ADAPTERS: Dict[str, Dict[str, str]] = {
    "llm": {
        "openai": "providers.openai_llm:OpenAILLM",
    },
    "tts": {
        "cartesia": "providers.cartesia_tts:CartesiaTTS",
        "openai": "providers.openai_tts:OpenAITTS",
    },
    "stt": {
        "openai": "providers.openai_stt:OpenAISTT",
        "cartesia": "providers.cartesia_stt:CartesiaSTT",
    },
    "video": {
        "none": "providers.video_disabled:DisabledVideo",
    },
    "music": {
        "local": "providers.music_local:LocalMusic",
        "none": "providers.music_disabled:DisabledMusic",
    },
    "image": {
        "openai": "providers.openai_image:OpenAIImage",
        "none": "providers.image_disabled:DisabledImage",
    },
    "store": {
        "local": "providers.store_local:LocalStore",
        "dynamodb": "providers.store_dynamodb:DynamoStore",
    },
    "files": {
        "local": "providers.files_local:LocalFiles",
        "s3": "providers.files_s3:S3Files",
    },
}

SELECTED = {
    "llm": config.LLM_PROVIDER,
    "tts": config.TTS_PROVIDER,
    "stt": config.STT_PROVIDER,
    "video": config.VIDEO_PROVIDER,
    "music": config.MUSIC_PROVIDER,
    "image": config.IMAGE_PROVIDER,
    "store": config.STORE_PROVIDER,
    "files": config.FILES_PROVIDER,
}


def available(capability: str) -> List[str]:
    return list(ADAPTERS[capability])


def _load(capability: str, name: str):
    try:
        target = ADAPTERS[capability][name]
    except KeyError:
        raise ProviderError(
            f"Unknown {capability.upper()}_PROVIDER '{name}'. Choose one of: {', '.join(available(capability))}."
        )
    module_name, class_name = target.split(":")
    return getattr(importlib.import_module(module_name), class_name)()


@functools.lru_cache(maxsize=None)
def llm() -> LLMProvider:
    return _load("llm", SELECTED["llm"])


@functools.lru_cache(maxsize=None)
def tts() -> TTSProvider:
    return _load("tts", SELECTED["tts"])


@functools.lru_cache(maxsize=None)
def stt() -> STTProvider:
    return _load("stt", SELECTED["stt"])


@functools.lru_cache(maxsize=None)
def video() -> VideoProvider:
    return _load("video", SELECTED["video"])


@functools.lru_cache(maxsize=None)
def music() -> MusicProvider:
    return _load("music", SELECTED["music"])


@functools.lru_cache(maxsize=None)
def image() -> ImageProvider:
    return _load("image", SELECTED["image"])


@functools.lru_cache(maxsize=None)
def store() -> StoreProvider:
    return _load("store", SELECTED["store"])


@functools.lru_cache(maxsize=None)
def files() -> FileStore:
    return _load("files", SELECTED["files"])


def describe() -> Dict[str, Dict[str, str]]:
    """Summary of the active adapters for logs and the /catalog endpoint. Never includes keys."""
    out: Dict[str, Dict[str, str]] = {}
    for capability, factory in (("llm", llm), ("tts", tts), ("stt", stt), ("video", video), ("music", music), ("image", image), ("store", store), ("files", files)):
        try:
            adapter = factory()
            model = getattr(adapter, "model", "")
            if capability == "music":
                from services import mixer  # local import: services depend on this module, not the reverse
                mixer_state = "ffmpeg" if mixer.available() else "no ffmpeg, voice only"
                model = f"{sum(adapter.tracks().values())} tracks, {mixer_state}"
            out[capability] = {
                "provider": adapter.name,
                "model": model,
                "enabled": "true" if getattr(adapter, "enabled", True) else "false",
                "cloning": "true" if getattr(adapter, "supports_cloning", False) else "false",
            }
        except ProviderError as exc:
            out[capability] = {"provider": SELECTED[capability], "model": "", "enabled": "false", "error": str(exc)}
    return out

"""Maps the provider names used in .env to adapter classes.

To add a vendor:
  1. Create providers/<vendor>_<capability>.py with a class extending the matching base
     class from providers/base.py.
  2. Add one line to ADAPTERS below.
  3. Set LLM_PROVIDER / TTS_PROVIDER / STT_PROVIDER / VIDEO_PROVIDER in .env.
  4. If the vendor needs its own voice ids, add them under "voices" in catalog.py.
"""
import functools
import importlib
from typing import Dict, List

import config
from providers.base import LLMProvider, ProviderError, STTProvider, TTSProvider, VideoProvider

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
}

SELECTED = {
    "llm": config.LLM_PROVIDER,
    "tts": config.TTS_PROVIDER,
    "stt": config.STT_PROVIDER,
    "video": config.VIDEO_PROVIDER,
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


def describe() -> Dict[str, Dict[str, str]]:
    """Summary of the active adapters for logs and the /catalog endpoint. Never includes keys."""
    out: Dict[str, Dict[str, str]] = {}
    for capability, factory in (("llm", llm), ("tts", tts), ("stt", stt), ("video", video)):
        try:
            adapter = factory()
            out[capability] = {
                "provider": adapter.name,
                "model": getattr(adapter, "model", ""),
                "enabled": "true" if getattr(adapter, "enabled", True) else "false",
                "cloning": "true" if getattr(adapter, "supports_cloning", False) else "false",
            }
        except ProviderError as exc:
            out[capability] = {"provider": SELECTED[capability], "model": "", "enabled": "false", "error": str(exc)}
    return out

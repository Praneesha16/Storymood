"""Central configuration. Every value comes from the environment (.env in this folder).

Provider choice is a single word per capability. The names map to adapter classes in
providers/registry.py, so switching vendors never requires touching application code.
"""
import os

from dotenv import load_dotenv

load_dotenv()


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


# ---- Which adapter serves each capability --------------------------------------------
LLM_PROVIDER = _env("LLM_PROVIDER", "openai")        # writes the stories
TTS_PROVIDER = _env("TTS_PROVIDER", "cartesia")      # reads the stories aloud
STT_PROVIDER = _env("STT_PROVIDER", "openai")        # listens to the child's idea
VIDEO_PROVIDER = _env("VIDEO_PROVIDER", "none")      # reserved for a future video adapter

# ---- OpenAI ---------------------------------------------------------------------------
OPENAI_API_KEY = _env("OPENAI_API_KEY")
OPENAI_LLM_MODEL = _env("OPENAI_LLM_MODEL", "gpt-6.1-terra")
OPENAI_REASONING_EFFORT = _env("OPENAI_REASONING_EFFORT", "low")  # blank disables the field
OPENAI_STT_MODEL = _env("OPENAI_STT_MODEL", "gpt-transcribe")
OPENAI_TTS_MODEL = _env("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")

# ---- Cartesia -------------------------------------------------------------------------
CARTESIA_API_KEY = _env("CARTESIA_API_KEY")
CARTESIA_API_VERSION = _env("CARTESIA_API_VERSION", "2026-03-01")
CARTESIA_TTS_MODEL = _env("CARTESIA_TTS_MODEL", "sonic-3.5")
CARTESIA_STT_MODEL = _env("CARTESIA_STT_MODEL", "ink-whisper")

# ---- Story vault (DynamoDB, optional) --------------------------------------------------
AWS_ACCESS_KEY_ID = _env("AWS_ACCESS_KEY_ID") or None
AWS_SECRET_ACCESS_KEY = _env("AWS_SECRET_ACCESS_KEY") or None
AWS_REGION = _env("AWS_REGION", "us-east-1")
STORIES_TABLE = _env("STORIES_TABLE", "StoryArc_Stories")
USERS_TABLE = _env("USERS_TABLE", "StoryArc_Users")

# ---- App ------------------------------------------------------------------------------
APP_ENV = _env("APP_ENV", "development")
API_V1_PREFIX = "/api/v1"
HTTP_TIMEOUT_SECONDS = float(_env("HTTP_TIMEOUT_SECONDS", "120"))
MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # both STT vendors cap uploads at 25 MB

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
AUDIO_FILES_DIR = os.path.join(STATIC_DIR, "audio")
AUDIO_FILES_URL_PATH = "/static/audio"

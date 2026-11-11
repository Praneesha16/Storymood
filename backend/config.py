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
MUSIC_PROVIDER = _env("MUSIC_PROVIDER", "local")     # background music: your own files, or none
IMAGE_PROVIDER = _env("IMAGE_PROVIDER", "openai")    # page illustrations

# ---- OpenAI ---------------------------------------------------------------------------
OPENAI_API_KEY = _env("OPENAI_API_KEY")
OPENAI_LLM_MODEL = _env("OPENAI_LLM_MODEL", "gpt-6.1-terra")
OPENAI_REASONING_EFFORT = _env("OPENAI_REASONING_EFFORT", "low")  # blank disables the field
OPENAI_STT_MODEL = _env("OPENAI_STT_MODEL", "gpt-transcribe")
OPENAI_TTS_MODEL = _env("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
OPENAI_IMAGE_MODEL = _env("OPENAI_IMAGE_MODEL", "gpt-image-2")
OPENAI_IMAGE_QUALITY = _env("OPENAI_IMAGE_QUALITY", "low")  # low (about a cent a picture), medium, high

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

# ---- Where stories and files live --------------------------------------------------------
STORE_PROVIDER = _env("STORE_PROVIDER", "local")      # local (JSON files) or dynamodb
FILES_PROVIDER = _env("FILES_PROVIDER", "local")      # local (static folder) or s3
STORYMOOD_TABLE = _env("STORYMOOD_TABLE", "StoryMood_Library")
S3_BUCKET = _env("S3_BUCKET")
S3_PREFIX = _env("S3_PREFIX", "storymood")
FILES_PUBLIC_BASE = _env("FILES_PUBLIC_BASE")         # CloudFront address in front of the bucket
FREE_STORIES = int(_env("FREE_STORIES", "2"))         # new stories a family can make before paying
ADMIN_EMAILS = [e.strip() for e in _env("ADMIN_EMAILS").split(",") if e.strip()]  # who reviews published stories

# ---- Sign-in and guardrails -----------------------------------------------------------
AUTH_MODE = _env("AUTH_MODE", "none")                 # none (guests, local dev) or cognito
COGNITO_REGION = _env("COGNITO_REGION", _env("AWS_REGION", "us-east-1"))
COGNITO_USER_POOL_ID = _env("COGNITO_USER_POOL_ID")
COGNITO_CLIENT_ID = _env("COGNITO_CLIENT_ID")
COGNITO_DOMAIN = _env("COGNITO_DOMAIN")               # e.g. storymood-you.auth.us-east-1.amazoncognito.com
COGNITO_ENDPOINT = _env("COGNITO_ENDPOINT").rstrip("/")  # only for local testing against an emulator (e.g. http://localhost:5001)
COGNITO_GOOGLE = _env("COGNITO_GOOGLE", "false").lower() == "true"  # set true once Google is added to the pool
ALLOWED_ORIGINS = [o.strip() for o in _env("ALLOWED_ORIGINS", "*").split(",") if o.strip()]
MODERATION = _env("MODERATION", "openai")             # openai (free Moderation API) or none
OPENAI_MODERATION_MODEL = _env("OPENAI_MODERATION_MODEL", "omni-moderation-latest")
RATE_LIMITS = _env("RATE_LIMITS", "on") != "off"
STORIES_PER_HOUR = int(_env("STORIES_PER_HOUR", "20"))
PICTURES_PER_HOUR = int(_env("PICTURES_PER_HOUR", "120"))
NARRATIONS_PER_HOUR = int(_env("NARRATIONS_PER_HOUR", "30"))

# ---- App ------------------------------------------------------------------------------
APP_ENV = _env("APP_ENV", "development")
API_V1_PREFIX = "/api/v1"
HTTP_TIMEOUT_SECONDS = float(_env("HTTP_TIMEOUT_SECONDS", "120"))
MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # both STT vendors cap uploads at 25 MB

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")  # local story records (STORE_PROVIDER=local)
STATIC_DIR = os.path.join(BASE_DIR, "static")
AUDIO_FILES_DIR = os.path.join(STATIC_DIR, "audio")
AUDIO_FILES_URL_PATH = "/static/audio"
MUSIC_FILES_DIR = os.path.join(STATIC_DIR, "music")  # drop <mood>-name.mp3 files here
MUSIC_FILES_URL_PATH = "/static/music"
IMAGE_FILES_DIR = os.path.join(STATIC_DIR, "images")
IMAGE_FILES_URL_PATH = "/static/images"
CHARS_PER_PAGE = 520  # how much story text fits on one book page; the frontend book uses the same pages

# ---- Mixing music under the voice (needs ffmpeg on PATH; silently voice-only without it) ----
FFMPEG_BIN = _env("FFMPEG_BIN", "ffmpeg")
FFPROBE_BIN = _env("FFPROBE_BIN", "ffprobe")
MUSIC_VOICE_LUFS = float(_env("MUSIC_VOICE_LUFS", "-18"))      # narration loudness after normalising
MUSIC_BED_DB = float(_env("MUSIC_BED_DB", "19"))                # how far below the voice the music sits while it speaks
MUSIC_INTRO_SECONDS = float(_env("MUSIC_INTRO_SECONDS", "2.5")) # music alone before the first word
MUSIC_OUTRO_SECONDS = float(_env("MUSIC_OUTRO_SECONDS", "4"))   # music after the last word, fading out
MUSIC_CROSSFADE_SECONDS = float(_env("MUSIC_CROSSFADE_SECONDS", "3"))
MUSIC_MIN_RUN_SECONDS = float(_env("MUSIC_MIN_RUN_SECONDS", "25"))  # shorter mood changes keep the current track

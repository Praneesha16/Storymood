# StoryMood backend

FastAPI service that writes, narrates and listens. See the repository README for the full
architecture; this file covers running it.

```bash
pip install -r requirements.txt
copy .env.example .env     # fill in OPENAI_API_KEY and CARTESIA_API_KEY
python main.py             # http://localhost:8000  (docs: /docs)
```

Startup logs show which adapter serves each capability:

```
llm -> openai gpt-6.1-terra
tts -> cartesia sonic-3.5
stt -> openai gpt-transcribe
video -> none
```

`GET /health` returns the same information without any secrets.

## Environment

| Variable | Default | Notes |
|---|---|---|
| `LLM_PROVIDER` | `openai` | name from `providers/registry.py` |
| `TTS_PROVIDER` | `cartesia` | `cartesia` or `openai` |
| `STT_PROVIDER` | `openai` | `openai` or `cartesia` |
| `VIDEO_PROVIDER` | `none` | placeholder |
| `OPENAI_API_KEY` | | required for OpenAI adapters |
| `OPENAI_LLM_MODEL` | `gpt-6.1-terra` | any Responses API model |
| `OPENAI_REASONING_EFFORT` | `low` | blank to omit |
| `OPENAI_STT_MODEL` | `gpt-transcribe` | |
| `OPENAI_TTS_MODEL` | `gpt-4o-mini-tts` | deprecated by OpenAI, fallback only |
| `CARTESIA_API_KEY` | | required for Cartesia adapters |
| `CARTESIA_TTS_MODEL` | `sonic-3.5` | |
| `CARTESIA_STT_MODEL` | `ink-whisper` | |
| `AWS_*`, `STORIES_TABLE` | | optional story vault |

Generated audio is written to `static/audio/` and served at `/static/audio/<file>.mp3`.

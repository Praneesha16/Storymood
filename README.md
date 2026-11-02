# StoryMood

A kid-friendly storytelling app. A child says or types an idea, picks a world, a feeling and a
narrator, and gets a brand-new story written by an LLM and read aloud in a storybook voice.
Works in English, Hindi, Telugu, Tamil and Malayalam.

```
storymood/
├── storyarc/    FastAPI backend (Python 3.10+)
└── frontend/    React 18 + TypeScript app (Create React App)
```

## Quick start

Backend (terminal 1):

```bash
cd storyarc
python -m venv ../storyarc-env && ../storyarc-env/Scripts/activate   # or source ../storyarc-env/bin/activate
pip install -r requirements.txt
copy .env.example .env   # then paste your OPENAI_API_KEY and CARTESIA_API_KEY
python main.py           # http://localhost:8000, docs at /docs
```

Frontend (terminal 2):

```bash
cd frontend
npm install
npm start                # http://localhost:3000
```

## How it is put together

Every external AI service sits behind a small adapter. The backend chooses adapters by name
from `.env`, so swapping a vendor is a one-line change and adding one is a one-file change.

| Capability | Default adapter | Also included | Env key |
|---|---|---|---|
| Story writing (LLM) | OpenAI `gpt-6.1-terra` | | `LLM_PROVIDER` |
| Read aloud (TTS) | Cartesia `sonic-3.5` | OpenAI `gpt-4o-mini-tts` | `TTS_PROVIDER` |
| Listen (STT) | OpenAI `gpt-transcribe` | Cartesia `ink-whisper` | `STT_PROVIDER` |
| Video | none (placeholder) | | `VIDEO_PROVIDER` |

Backend layout:

```
storyarc/
├── main.py                 FastAPI app, CORS, error handling, static audio
├── config.py               All settings, read from .env
├── catalog.py              Themes, feelings, ages, lengths, narrators, languages, voice ids
├── providers/
│   ├── base.py             LLMProvider, TTSProvider, STTProvider, VideoProvider interfaces
│   ├── registry.py         name -> adapter table; llm(), tts(), stt(), video()
│   ├── openai_llm.py       Responses API
│   ├── openai_tts.py       /audio/speech
│   ├── openai_stt.py       /audio/transcriptions
│   ├── cartesia_tts.py     /tts/bytes
│   ├── cartesia_stt.py     /stt
│   └── video_disabled.py   stub until a video vendor is chosen
├── services/
│   ├── prompts.py          Children's-story system prompt and JSON schema
│   ├── story_service.py    request -> story (title + text + meta)
│   ├── voice_service.py    text -> chunked TTS -> one mp3 under /static/audio
│   └── transcribe_service.py
├── routers/                /catalog, /story, /voice, /video, /vault, /session
├── models/story_model.py   Pydantic request/response models
└── database/dynamodb.py    Optional story vault (needs AWS keys)
```

### API

All routes are under `/api/v1`. Interactive docs live at `http://localhost:8000/docs`.

| Method | Path | Purpose |
|---|---|---|
| GET | `/catalog` | Options for the UI plus which providers are active |
| POST | `/story/generate` | Write a story. Body: theme, feeling, age_group, length, language, narrator, characters, idea |
| POST | `/voice/narrate` | Read text aloud. Body: text, narrator, language, optional `voice_id`. Returns an `audio_url` |
| POST | `/voice/transcribe` | Multipart `file` (+ optional `language`). Returns text and detected language |
| POST | `/voice/clone` | Multipart `file`, `name`, `language`. Clones a family voice (Cartesia) and returns its `voice_id` |
| POST | `/video/generate` | 501 until a video adapter is configured |
| POST/GET | `/vault/...` | Save and list stories (DynamoDB) |

### Adding a provider

1. Create `storyarc/providers/<vendor>_<capability>.py` with a class that extends the matching
   base class in `providers/base.py` and implements its one method.
2. Register it in `providers/registry.py` under `ADAPTERS`.
3. Put any keys or model names in `config.py` and `.env.example`.
4. For a TTS vendor, add its voice ids under each narrator's `voices` in `catalog.py`.
5. Set `<CAPABILITY>_PROVIDER=<vendor>` in `.env`.

### Changing what kids can pick

Edit `catalog.py`. Themes, feelings, age groups, lengths, narrators and languages are plain
lists; the frontend renders whatever `/catalog` returns.

## Frontend

```
frontend/src/
├── App.tsx                 Screen flow: create -> loading -> story
├── config.ts               API base URL (REACT_APP_API_URL in frontend/.env)
├── api/client.ts           Typed fetch wrappers for every endpoint
├── hooks/useRecorder.ts    MediaRecorder: tap to talk, tap to stop
├── hooks/useUserId.ts      Anonymous id for the shelf
├── components/             ChoiceGrid, IdeaBox, MicButton, CharacterPicker, CreateScreen,
│                           LoadingScreen, StoryScreen, AudioPlayer, Shelf, Header
└── index.css               Design tokens (colours, radii, shadows) and all styles
```

Colours and shapes are CSS variables at the top of `index.css`.

## Costs (approximate, November 2026)

A short story with `gpt-6.1-terra` is well under one cent. Cartesia narration is billed per
character; a short story is a few thousand characters. Transcription with `gpt-transcribe` is
about half a cent per minute of audio.

## Notes

- `gpt-4o-mini-tts` is deprecated by OpenAI and stops working on 6 January 2027. It is kept only
  as a fallback; Cartesia is the default voice.
- The video capability is wired end to end (route, interface, registry, UI flag) but has no
  vendor yet.

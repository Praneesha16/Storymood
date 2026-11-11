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
python download_music.py # optional: default background music (about 120 MB)
                         # music mixing also needs ffmpeg on PATH: winget install Gyan.FFmpeg
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
| Background music | your own files in `storyarc/static/music` | none | `MUSIC_PROVIDER` |
| Page pictures | OpenAI `gpt-image-2` (low quality, about a cent each) | none | `IMAGE_PROVIDER` |
| Story records and accounts | JSON files in `storyarc/data` | DynamoDB | `STORE_PROVIDER` |
| Narration and picture files | `storyarc/static` served by the API | S3 behind CloudFront | `FILES_PROVIDER` |

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
│   ├── music_local.py      picks a track from static/music by mood (no API)
│   ├── openai_image.py     /images/generations, one picture per page
│   └── video_disabled.py   stub until a video vendor is chosen
├── services/
│   ├── prompts.py          Children's-story system prompt and JSON schema (title, mood, mood-tagged paragraphs)
│   ├── story_service.py    request -> story (title, mood-tagged paragraphs, pages, art notes)
│   ├── illustrate_service.py  one picture for a page or the cover, same style line every time
│   ├── voice_service.py    mood-tagged text -> chunked TTS -> mixer -> one mp3 under /static/audio
│   ├── mixer.py            ffmpeg: join chunks, normalise, lay mood music under the voice
│   └── transcribe_service.py
├── routers/                /catalog, /story, /voice, /video, /music, /vault, /session
├── models/story_model.py   Pydantic request/response models
└── database/dynamodb.py    Optional story vault (needs AWS keys)
```

### API

All routes are under `/api/v1`. Interactive docs live at `http://localhost:8000/docs`.

| Method | Path | Purpose |
|---|---|---|
| GET | `/catalog` | Options for the UI plus which providers are active |
| POST | `/story/generate` | Write a story. Body: theme, feeling, age_group, length, language, narrator, characters, idea. Returns title, text, `mood`, mood-tagged `paragraphs` and a `music_url` when a track matches |
| POST | `/story/illustrate` | Paint one picture. Body: title, scene, characters, kind (`page` or `cover`), optional `references` (characters' pictures as data URLs, so the painting takes after them). Returns an `image_url` |
| POST | `/voice/narrate` | Read text aloud. Body: text, narrator, language, optional `voice_id`, optional `segments` (mood-tagged passages for expressive reading), `music`. Returns an `audio_url`, whether music was mixed, and `cues` (when each segment is heard) |
| GET | `/music` | Which moods have background tracks, and the folder to drop files in |

`/voice/narrate` also takes `music: false` to read without music.
| POST | `/voice/transcribe` | Multipart `file` (+ optional `language`). Returns text and detected language |
| POST | `/voice/clone` | Multipart `file`, `name`, `language`. Clones a family voice (Cartesia) and returns its `voice_id` |
| POST | `/video/generate` | 501 until a video adapter is configured |
| POST/GET | `/vault/...` | Save and list stories (DynamoDB) |

### Moods, expression and music

The writer returns an overall `mood` for the story and a mood for every paragraph (the list is
`MOODS` in `catalog.py`). Two things use it:

- **Expressive reading.** The frontend sends the paragraphs as `segments`; the voice service
  groups them by mood and passes each mood's Cartesia emotion name in `generation_config`.
  Cartesia documents emotion steering for English only, so other languages keep the voice's
  natural reading. A cloned family voice gets the same treatment.
- **Background music.** No music is generated. Drop instrumental files into
  `storyarc/static/music` named `<mood>-anything.mp3` (see the README there). When a story is
  read, `services/mixer.py` uses ffmpeg to mix the music into the narration file the way an
  audiobook is produced: a short musical intro, the voice normalised to -18 LUFS, the music
  held 19 dB below it while the voice speaks, a different track cross-faded in when the
  story's mood changes for long enough, a small swell after the last word and a fade out.
  Saved stories therefore replay with their music. Levels and timings are `MUSIC_*` settings
  in `config.py`. Without ffmpeg on PATH the narration is served voice-only.
  `GET /api/v1/music` shows the tracks found and whether ffmpeg was detected.
  A generative vendor would be a new `MusicProvider` adapter.
  Twenty default tracks by Kevin MacLeod (CC BY 4.0, credit kept in `static/music/CREDITS.md`) are
  fetched with `python storyarc/download_music.py`; they are not kept in git.

### Pictures and self-turning pages

The writer also returns a one-line English scene for every paragraph and art notes (how the
heroes look, what the cover shows). The server groups paragraphs into pages (`CHARS_PER_PAGE`)
and the frontend asks `/story/illustrate` for the cover and one picture per page in the
background, so the story and its narration never wait for the pictures. Every prompt carries
the same style line and the same character description, which keeps the pages looking like one
book. Pictures are stored under `static/images` and remembered with the story in the browser.

A family can add a photo, drawing or toy picture for each character in "Who is in it?". The
browser shrinks it to a small JPEG and sends it only with the picture requests; the server
decodes it in memory, hands it to the image model's edit endpoint and never writes it to disk.
Each reference adds about 1,500 input tokens per picture (roughly a cent). The model draws a
storybook version that takes after the picture; it does not promise an exact likeness, and it is
cautious with real children's faces.

Narration returns `cues`: the mixer measures each voice chunk, so the server knows when every
paragraph is heard. The book turns its own pages as the reading reaches them. Narration files
are served by a small Range-aware route in `main.py` so browsers can seek (Starlette's
`StaticFiles` ignores Range headers).

### Sign-in, guardrails and what is protected

- **Sign-in** is a login page of our own (`frontend/src/components/LoginPage.tsx`) that gates
  the whole app: nothing else renders until a grown-up has signed in. Accounts are email +
  password. "Create account" goes through `POST /auth/signup`, which creates and activates the
  user in Amazon Cognito (Essentials tier, free to 10,000 monthly users) so there is no email
  code at sign-up; the password is passed to Cognito over HTTPS and never stored by us. Sign-in
  goes from the browser straight to Cognito's user-pool API (`frontend/src/auth.ts`), which
  returns signed tokens. Password rules: 8+ characters with a capital letter and a number,
  enforced on both sides. Extras: Google (`COGNITO_GOOGLE=true` once connected in the pool), and a forgot-password
  flow where Cognito emails a reset code (the only code anywhere). Because sign-up sends no
  verification email, an address is not proven to belong to the person; turn
  `AutoVerifiedAttributes` back on in the pool if that matters later. `AUTH_MODE=none` (the default) runs the app for guests on a laptop
  with no login page; `AUTH_MODE=cognito` turns the front door on. In development
  `http://localhost:3000/?login` shows the page with a pretend pool.
  `python scripts/setup_cognito.py --app-url ... --prefix ...` creates the pool and prints the
  `.env` values. Cognito's built-in email sender is limited to about 50 messages a day; connect
  Amazon SES to the pool before real families use it.
- **Protected routes:** `/story/*`, `/voice/*`, `/video/*`, `/vault/*`, `/session/*` need a valid
  Cognito ID token (`Authorization: Bearer ...`), verified offline against the pool's signing keys:
  signature, issuer, audience, expiry, token type and verified email. `/catalog`, `/music` and
  `/auth/config` are open. The frontend (`src/auth.ts`) does the authorization-code flow with PKCE
  and refreshes tokens quietly.
- **Guardrails:** every idea, character name, trait and uploaded picture goes through OpenAI's free
  Moderation API before the writer or painter sees it (`services/moderation.py`); a refusal is a
  friendly 400. The system prompt tells the writer to treat the idea as content, never as
  instructions. Per-user rate limits (`services/ratelimit.py`, `STORIES_PER_HOUR` and friends)
  cap spending. `ALLOWED_ORIGINS` pins CORS to the app's address in production.
### Sharing stories, the review queue and the free allowance

- Every story a signed-in family makes is recorded on the server (`services/library_service.py`):
  text, pages, mood, then the recording and pictures attach as they are made. Families' records
  live in the store adapter (`STORE_PROVIDER`: JSON files locally, DynamoDB in production).
- **Share with everyone:** the grown-up confirms, including a specific warning when the story was
  painted from their own photos or drawings. The finished text is moderated again, then the story
  waits as `pending`. A reviewer (an email in `ADMIN_EMAILS`; on a laptop in guest mode, anyone)
  reads it in the book and approves or rejects it. Approved stories appear on the "Stories from
  other families" shelf; opening one costs nothing because the recording and pictures already exist.
- **Report:** any listener can flag a shared story with a reason; after three reports it is hidden
  again until a reviewer looks. "Keep it ours" takes a story down at any time; deleting it from My
  stories does too. Public views never include the owner's id, only a first name.
- **Allowance:** `FREE_STORIES` (default 2) new stories per account, then story credits
  (`POST /admin/credits` for now; payments later). Listening to saved or shared stories is free.
  Guests on a laptop are unlimited.
- Routes: `GET /library/mine`, `POST /library/{id}/publish`, `POST /library/{id}/unpublish`,
  `DELETE /library/{id}`, `GET /community`, `GET /community/{id}`, `POST /community/{id}/report`,
  `GET /admin/review`, `POST /admin/review/{id}`, `POST /admin/credits`, `GET /auth/me`.

### Deploying

- **Backend:** `storyarc/Dockerfile` builds the API with ffmpeg. Run it on AWS App Runner or a
  Lightsail container with the `.env` values as environment variables, `AUTH_MODE=cognito`,
  `STORE_PROVIDER=dynamodb`, `FILES_PROVIDER=s3` (plus `S3_BUCKET` and `FILES_PUBLIC_BASE`, the
  CloudFront address), `ALLOWED_ORIGINS=https://your-app-address`, `ADMIN_EMAILS=you@example.com`.
  Tables and the sign-in pool are created by the app and by `scripts/setup_cognito.py`.
- **Frontend:** `npm run build` in `frontend/` with `REACT_APP_API_URL=https://your-api-address`,
  then upload the `build` folder to an S3 bucket behind CloudFront (or Amplify Hosting).
- Music: copy the `static/music` tracks into the container or mount them; `download_music.py`
  fetches them.

### Adding a provider

1. Create `storyarc/providers/<vendor>_<capability>.py` with a class that extends the matching
   base class in `providers/base.py` and implements its one method.
2. Register it in `providers/registry.py` under `ADAPTERS`.
3. Put any keys or model names in `config.py` and `.env.example`.
4. For a TTS vendor, add its voice ids under each narrator's `voices` in `catalog.py`.
5. Set `<CAPABILITY>_PROVIDER=<vendor>` in `.env`.

### Narrators

Six narrators: Little Girl, Little Boy, Kind Lady, Friendly Man, Cozy Grandma, Jolly Grandpa.
Each one lists the languages it can read with the active voice provider (`/catalog` returns
`languages` per narrator) and the app only shows the cards that fit the chosen language. With
Cartesia that is all six in English, four in Hindi, Telugu and Tamil (no child voices exist
there), and two in Malayalam. Voice ids live under `voices` in `catalog.py`; add a language
to a narrator by adding its voice id, and the card appears for that language by itself.

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

# StoryMood frontend

React 18 + TypeScript (Create React App). Talks to the backend at `REACT_APP_API_URL`
(see `.env`, default `http://localhost:8000`).

```bash
npm install
npm start        # dev server on http://localhost:3000
npm run build    # production build in build/
npm run lint
```

The microphone needs a secure context: `localhost` is fine, any other host needs HTTPS.

Everything a child can choose comes from `GET /api/v1/catalog`, so new themes or narrators
added in `storyarc/catalog.py` appear here without a frontend change.

## Look and feel

One scrolling page on a burgundy stage, with no framing boxes. The illustrated landscape
(`Scenery.tsx`, inline SVG with CSS-animated sun, clouds, flags, balloon, dragon and wizard)
runs across the top. Below it sits a real 3D storybook (`StoryBook.tsx`) that opens on a
welcome page; when a story is ready the pages become the story and each tap or arrow turns a
leaf. Phones show one page per leaf. The inside cover holds the "Read it to me" player.

Every choice follows on the same page (`Maker.tsx`), each heading with its own small looping
scene (`Doodle.tsx`). Colours, fonts and line weights are CSS variables at the top of
`src/index.css`; motion is disabled for users who prefer reduced motion.

## What kids (and grown-ups) can do

- **Make a story** by voice or typing, in English, Hindi, Telugu, Tamil or Malayalam.
- **Hear it read** by one of five storybook narrators. New stories are read aloud by
  themselves when the toggle under the book is on.
- **Read it in my voice.** A grown-up records one sentence; the voice provider clones it and
  it appears as a narrator. The voice id is kept in this browser only (`VoiceClone.tsx`).
- **My stories.** Every story is saved in this browser (`useLibrary.ts`) with its recording,
  so tapping a book on the shelf reopens it and plays again without a new request. Stories are
  also sent to the backend vault best-effort.
- **Surprise me** picks a random world, feeling and narrator and writes straight away.

While developing, `http://localhost:3000/?preview=story` fills the book with a sample story
so it can be styled without calling the API. The flag is ignored in builds.

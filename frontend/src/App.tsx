import React, { useEffect, useState } from 'react';
import { api } from './api/client';
import Library from './components/Library';
import Maker from './components/Maker';
import Scenery from './components/Scenery';
import StoryBook, { BookStatus } from './components/StoryBook';
import { useLibrary } from './hooks/useLibrary';
import { useStoredState } from './hooks/useStoredState';
import { useUserId } from './hooks/useUserId';
import { Catalog, CustomVoice, SavedStory, StoryRequest, StoryResponse } from './types';

const DEFAULT_DRAFT: StoryRequest = {
  theme: 'adventure',
  feeling: 'happy',
  age_group: '6-8',
  length: 'short',
  language: 'en',
  narrator: 'grandma',
  characters: [],
  idea: '',
};

/** Slow-drifting dust motes on the stage. Positions are fixed so the scene is stable between renders. */
const DUST: React.CSSProperties[] = Array.from({ length: 18 }, (_, i) => ({
  left: `${(i * 61) % 100}%`,
  top: `${(i * 37 + 11) % 100}%`,
  width: `${3 + (i % 4)}px`,
  height: `${3 + (i % 4)}px`,
  animationDuration: `${14 + (i % 7) * 3}s`,
  animationDelay: `${-(i * 1.7)}s`,
  opacity: 0.25 + (i % 3) * 0.15,
}));

/** Development only: ?preview=story fills the book with a sample story without calling the API. Ignored in builds. */
const PREVIEW_STORY: StoryResponse | null =
  process.env.NODE_ENV === 'development' && new URLSearchParams(window.location.search).get('preview') === 'story'
    ? {
        title: 'Mia and the Butterfly Wobble',
        story_text:
          'Mia was a curious little dinosaur who loved big mysteries. One sunny morning, she found a speckled egg beside a fern.\n\n“Hello, egg,” she said. “Where is your family?”\n\nThe egg did not answer. It just sat there looking very eggy.\n\nMia rolled it gently toward the meadow, where enormous dinosaurs munched leaves. Her friend Bobo was there, hiding behind a rock. This was tricky because Bobo was taller than three trees.\n\nBobo pointed one trembling toe at a butterfly. “It has fluttery wings,” he whispered. “What if it lands on my nose?”\n\nThe butterfly landed on his nose. Bobo sneezed so loudly that the nearby volcano burped. “Bless you,” said Mia, and everyone laughed until the stars came out.',
        meta: {
          theme: 'dinosaurs', feeling: 'silly', age_group: '6-8', length: 'short', language: 'en', narrator: 'pal',
          characters: ['Mia'], word_count: 140, estimated_minutes: 1, provider: 'preview', model: 'preview',
        },
      }
    : null;

const pick = <T,>(list: T[]): T => list[Math.floor(Math.random() * list.length)];
const scrollTo = (id: string) => document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });

const App: React.FC = () => {
  const userId = useUserId();
  const library = useLibrary();
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [catalogError, setCatalogError] = useState<string | null>(null);
  const [draft, setDraft] = useState<StoryRequest>(DEFAULT_DRAFT);
  const [status, setStatus] = useState<BookStatus>(PREVIEW_STORY ? 'ready' : 'idle');
  const [story, setStory] = useState<StoryResponse | null>(PREVIEW_STORY);
  const [currentId, setCurrentId] = useState<string | null>(null);
  const [savedAudio, setSavedAudio] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Settings and the family voice live in this browser.
  const [autoRead, setAutoRead] = useStoredState<boolean>('storymood.autoRead', true);
  const [customVoice, setCustomVoice] = useStoredState<CustomVoice | null>('storymood.customVoice', null);
  const [useCustomVoice, setUseCustomVoice] = useStoredState<boolean>('storymood.useCustomVoice', false);
  const activeVoice = useCustomVoice && customVoice ? customVoice : null;

  useEffect(() => {
    api
      .catalog()
      .then(setCatalog)
      .catch((err) => setCatalogError(err instanceof Error ? err.message : 'Could not load the app.'));
  }, []);

  const generateWith = async (request: StoryRequest) => {
    setError(null);
    setStory(null);
    setSavedAudio(null);
    setStatus('loading');
    scrollTo('book');
    try {
      const result = await api.generateStory(request);
      const saved = library.add(result, activeVoice?.name ?? null);
      setCurrentId(saved.id);
      setStory(result);
      setStatus('ready');
      api.saveStory(userId, result, null).catch(() => undefined); // vault is best effort
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong.');
      setStatus('idle');
      scrollTo('make');
    }
  };

  const surprise = () => {
    if (!catalog) return;
    const next = { ...draft, theme: pick(catalog.themes).id, feeling: pick(catalog.feelings).id, narrator: pick(catalog.narrators).id };
    setDraft(next);
    generateWith(next);
  };

  const openSaved = (saved: SavedStory) => {
    setStory(saved.story);
    setCurrentId(saved.id);
    setSavedAudio(saved.audioUrl);
    setStatus('ready');
    scrollTo('book');
  };

  const another = () => {
    setStory(null);
    setCurrentId(null);
    setSavedAudio(null);
    setStatus('idle');
    scrollTo('make');
  };

  if (catalogError) {
    return (
      <div className="stage stage--center">
        <div className="banner banner--error" role="alert">
          <span aria-hidden="true">🔌</span> {catalogError}
        </div>
      </div>
    );
  }
  if (!catalog) {
    return (
      <div className="stage stage--center">
        <p className="boot">📖 opening the book…</p>
      </div>
    );
  }

  const themeEmoji = catalog.themes.find((t) => t.id === draft.theme)?.emoji || '🌈';

  return (
    <div className="stage" id="top">
      <div className="dust" aria-hidden="true">
        {DUST.map((d, i) => (
          <span key={i} style={d} />
        ))}
      </div>

      <div className="hero">
        <Scenery variant="hero" />
        <div className="hero__text">
          <h1 className="hero__logo">StoryMood</h1>
          <p className="hero__tag">Say an idea. Pick a world. Hear your story.</p>
        </div>
      </div>

      <main className="content">
        <StoryBook
          catalog={catalog}
          status={status}
          story={story}
          themeEmoji={themeEmoji}
          voice={activeVoice}
          savedAudioUrl={savedAudio}
          autoRead={autoRead}
          onAutoRead={setAutoRead}
          onAudio={(url) => currentId && library.setAudio(currentId, url)}
          onAnother={another}
          onSurprise={surprise}
        />
        <Maker
          catalog={catalog}
          draft={draft}
          onChange={setDraft}
          onSubmit={() => generateWith(draft)}
          onSurprise={surprise}
          busy={status === 'loading'}
          error={error}
          customVoice={customVoice}
          useCustomVoice={useCustomVoice && !!customVoice}
          onUseCustomVoice={setUseCustomVoice}
          onVoiceCloned={(v) => {
            setCustomVoice(v);
            setUseCustomVoice(true);
          }}
          onForgetVoice={() => {
            setCustomVoice(null);
            setUseCustomVoice(false);
          }}
        />
        <Library catalog={catalog} items={library.items} currentId={currentId} onOpen={openSaved} onRemove={library.remove} />
      </main>

      <footer className="stage__foot">
        written by {catalog.providers.llm.model} · voices by {catalog.providers.tts.provider}
      </footer>
    </div>
  );
};

export default App;

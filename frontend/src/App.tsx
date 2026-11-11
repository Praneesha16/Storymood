import React, { useEffect, useState } from 'react';
import { api, requestContext } from './api/client';
import { auth, Session } from './auth';
import Community from './components/Community';
import LoginPage from './components/LoginPage';
import Library from './components/Library';
import ReviewQueue from './components/ReviewQueue';
import Maker from './components/Maker';
import Scenery from './components/Scenery';
import StoryBook, { BookStatus } from './components/StoryBook';
import { useLibrary } from './hooks/useLibrary';
import { useStoredState } from './hooks/useStoredState';
import { useUserId } from './hooks/useUserId';
import { Catalog, CommunityItem, CustomVoice, LibraryRecord, Me, NarrationCue, SavedStory, ShareStatus, StoryRequest, StoryResponse } from './types';

const DEFAULT_DRAFT: StoryRequest = {
  theme: 'adventure',
  feeling: 'happy',
  age_group: '6-8',
  length: 'short',
  language: 'en',
  narrator: 'woman',
  characters: [],
  idea: '',
};

/** Development only: ?login shows the login page with a pretend pool, to work on its design. */
const LOGIN_PREVIEW = process.env.NODE_ENV === 'development' && new URLSearchParams(window.location.search).has('login');

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
        mood: 'silly',
        music_url: null,
        paragraphs: [],
        pages: [],
        art: null,
      }
    : null;

const pick = <T,>(list: T[]): T => list[Math.floor(Math.random() * list.length)];
const scrollTo = (id: string) => document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });

const App: React.FC = () => {
  const userId = useUserId();
  const library = useLibrary();
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [authOn, setAuthOn] = useState(false);
  const [session, setSession] = useState<Session | null>(null);
  const [catalogError, setCatalogError] = useState<string | null>(null);
  const [draft, setDraft] = useState<StoryRequest>(DEFAULT_DRAFT);
  const [status, setStatus] = useState<BookStatus>(PREVIEW_STORY ? 'ready' : 'idle');
  const [story, setStory] = useState<StoryResponse | null>(PREVIEW_STORY);
  const [currentId, setCurrentId] = useState<string | null>(null);
  const [savedAudio, setSavedAudio] = useState<string | null>(null);
  const [savedCues, setSavedCues] = useState<NarrationCue[]>([]);
  const [error, setError] = useState<string | null>(null);
  // The server's view: who we are, sharing state of our stories, the community shelf, the review queue.
  const [me, setMe] = useState<Me | null>(null);
  const [statuses, setStatuses] = useState<Record<string, ShareStatus>>({});
  const [communityItems, setCommunityItems] = useState<CommunityItem[]>([]);
  const [queue, setQueue] = useState<LibraryRecord[]>([]);
  const [viewPictures, setViewPictures] = useState<Record<string, string>>({}); // pictures of an opened shared story

  // Settings and the family voice live in this browser.
  const [autoRead, setAutoRead] = useStoredState<boolean>('storymood.autoRead', true);
  const [music, setMusic] = useStoredState<boolean>('storymood.music', true);
  const [pictures, setPictures] = useStoredState<boolean>('storymood.pictures', true);
  const picturesOn = pictures && catalog?.providers.image?.enabled === 'true';
  const [customVoice, setCustomVoice] = useStoredState<CustomVoice | null>('storymood.customVoice', null);
  const [useCustomVoice, setUseCustomVoice] = useStoredState<boolean>('storymood.useCustomVoice', false);
  const activeVoice = useCustomVoice && customVoice ? customVoice : null;

  useEffect(() => {
    requestContext.guestId = userId;
    requestContext.onUnauthorized = () => setSession(null);
    const configure = LOGIN_PREVIEW
      ? Promise.resolve(auth.preview({ mode: 'cognito', region: 'us-east-1', user_pool_id: 'preview', client_id: 'preview', domain: 'preview', google: true }))
          .then(() => ({ mode: 'cognito' as const }))
      : auth.configure();
    configure
      .then(async (cfg) => {
        setAuthOn(cfg.mode === 'cognito');
        if (cfg.mode === 'cognito') {
          await auth.completeLogin(); // no-op unless we just came back from Google
          setSession(auth.session);
        }
      })
      .catch(() => undefined)
      .then(() => api.catalog())
      .then(setCatalog)
      .catch((err) => setCatalogError(err instanceof Error ? err.message : 'Could not load the app.'));
  }, [userId]);

  /** Refresh everything the server knows about us and the shelf. Best effort: the app works without it. */
  const refreshServer = async () => {
    try {
      const who = await api.me();
      setMe(who);
      const mine = await api.myStories();
      setStatuses(Object.fromEntries(mine.map((r) => [r.id, r.status])));
      if (who.allowance.admin) setQueue(await api.reviewQueue());
    } catch {
      /* not signed in, or the server is in guest mode without records yet */
    }
    try {
      setCommunityItems(await api.community());
    } catch {
      /* shelf stays empty */
    }
  };

  useEffect(() => {
    if (catalog) void refreshServer();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [catalog, session]);

  /** Narrators that can read a language. */
  const narratorsFor = (language: string) =>
    (catalog?.narrators || []).filter((n) => !n.languages || n.languages.includes(language));

  // When the language changes and the chosen narrator cannot read it, move to one who can.
  useEffect(() => {
    if (!catalog) return;
    const available = narratorsFor(draft.language);
    if (available.length && !available.some((n) => n.id === draft.narrator)) {
      setDraft((d) => ({ ...d, narrator: available[0].id }));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [catalog, draft.language]);

  /** Paint the cover and one picture per page in the background; each lands in the library as it arrives. */
  const illustrate = (result: StoryResponse, id: string, request: StoryRequest) => {
    if (!picturesOn || !result.pages?.length) return;
    const characters = result.art?.characters || '';
    const references = request.characters.filter((c) => c.image).map((c) => ({ name: c.name, image: c.image as string }));
    const jobs: Array<[string, string, 'cover' | 'page']> = [
      ['cover', result.art?.cover || result.pages[0].scene, 'cover'],
      ...result.pages.map((p, i): [string, string, 'page'] => [`page-${i}`, p.scene, 'page']),
    ];
    jobs.forEach(([key, scene, kind]) => {
      if (!scene.trim()) return;
      api
        .illustrate({ title: result.title, scene, characters, kind, references, story_id: result.id || '', key })
        .then((r) => library.setPicture(id, key, api.mediaUrl(r.image_url)))
        .catch(() => undefined); // a missing picture leaves a gentle placeholder
    });
  };

  const generateWith = async (request: StoryRequest) => {
    setError(null);
    setStory(null);
    setSavedAudio(null);
    setSavedCues([]);
    setStatus('loading');
    scrollTo('book');
    try {
      const avoid = library.items.slice(0, 10).map((s) => s.story.title);
      const result = await api.generateStory({ ...request, avoid });
      const saved = library.add(result, activeVoice?.name ?? null);
      setCurrentId(saved.id);
      setStory(result);
      setStatus('ready');
      illustrate(result, saved.id, request);
      void refreshServer();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong.');
      setStatus('idle');
      scrollTo('make');
    }
  };

  const surprise = () => {
    if (!catalog) return;
    const narrators = narratorsFor(draft.language);
    const next = { ...draft, theme: pick(catalog.themes).id, feeling: pick(catalog.feelings).id, narrator: pick(narrators.length ? narrators : catalog.narrators).id };
    setDraft(next);
    generateWith(next);
  };

  const openSaved = (saved: SavedStory) => {
    setStory(saved.story);
    setCurrentId(saved.id);
    setSavedAudio(saved.audioUrl);
    setSavedCues(saved.audioCues || []);
    setStatus('ready');
    scrollTo('book');
  };

  /** Open a story from the server (community shelf or review queue): recording and pictures come with it. */
  const openRecord = (record: LibraryRecord) => {
    setStory(record);
    setCurrentId(null);
    setViewPictures(record.pictures || {});
    setSavedAudio(record.audio_url ? api.mediaUrl(record.audio_url) : null);
    setSavedCues(record.cues || []);
    setStatus('ready');
    scrollTo('book');
  };

  const openCommunity = (id: string) => {
    api.communityStory(id).then(openRecord).catch((err) => setError(err instanceof Error ? err.message : 'Could not open that story.'));
  };

  const share = async (id: string) => {
    const personal = library.items.find((s) => s.id === id)?.story.meta.characters.length ? true : false;
    const ok = window.confirm(
      'Share this story with every family using the app?\n\n' +
        'It will be checked by a reviewer first. Its recording and pictures will be public.' +
        (personal ? '\n\nIf you added your own photos or drawings for the characters, the painted pictures made from them will be public too. Only continue if you are happy with that.' : '') +
        '\n\nYou can take it back at any time with "keep it ours".'
    );
    if (!ok) return;
    try {
      const record = await api.publish(id, true);
      setStatuses((s) => ({ ...s, [id]: record.status }));
      void refreshServer(); // the reviewer's queue and the shelf may have changed
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not share that story.');
    }
  };

  const unshare = async (id: string) => {
    try {
      const record = await api.unpublish(id);
      setStatuses((s) => ({ ...s, [id]: record.status }));
      setCommunityItems((items) => items.filter((i) => i.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not change that story.');
    }
  };

  const reportStory = (id: string) => {
    const reason = window.prompt('What is wrong with this story? A few words help the reviewer.');
    if (reason === null) return;
    api.report(id, reason).then(() => window.alert('Thank you. A reviewer will look at it.')).catch(() => undefined);
  };

  const decide = async (id: string, decision: 'approve' | 'reject') => {
    try {
      await api.review(id, decision);
      setQueue((q) => q.filter((r) => r.id !== id));
      void refreshServer(); // shelf and our own statuses
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not save that decision.');
    }
  };

  const another = () => {
    setStory(null);
    setCurrentId(null);
    setSavedAudio(null);
    setSavedCues([]);
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
  // The front door: with sign-in on, nothing else is shown until a grown-up has signed in.
  if (authOn && !session) {
    return <LoginPage onSignedIn={setSession} />;
  }

  const themeEmoji = catalog.themes.find((t) => t.id === draft.theme)?.emoji || '🌈';
  const currentPictures = currentId ? library.items.find((s) => s.id === currentId)?.pictures || {} : viewPictures;

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
          savedCues={savedCues}
          pictures={picturesOn ? currentPictures : null}
          autoRead={autoRead}
          onAutoRead={setAutoRead}
          music={music}
          onMusic={setMusic}
          picturesOn={pictures}
          picturesOffered={catalog.providers.image?.enabled === 'true'}
          onPictures={setPictures}
          onAudio={(url, cues) => currentId && library.setAudio(currentId, url, cues)}
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
        <Library
          catalog={catalog}
          items={library.items}
          currentId={currentId}
          statuses={statuses}
          onOpen={openSaved}
          onRemove={(id) => {
            library.remove(id);
            if (statuses[id]) api.unpublish(id).catch(() => undefined);
          }}
          onShare={share}
          onUnshare={unshare}
        />
        <Community catalog={catalog} items={communityItems} currentId={null} onOpen={openCommunity} onReport={reportStory} />
        {me?.allowance.admin && <ReviewQueue items={queue} onOpen={openRecord} onDecide={decide} />}
      </main>

      {authOn && session && (
        <footer className="whoami">
          signed in as <b>{session.name || session.email}</b>
          {me && !me.allowance.unlimited && (
            <> · {me.allowance.free_left} of {me.allowance.free_total} free stories left{me.allowance.credits > 0 ? ` · ${me.allowance.credits} credits` : ''}</>
          )}
          {' · '}
          <button type="button" className="link-button" onClick={() => void auth.logout().then(() => setSession(null))}>
            sign out
          </button>
        </footer>
      )}

    </div>
  );
};

export default App;

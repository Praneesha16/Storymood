import React, { useEffect, useMemo, useRef, useState } from 'react';
import { api } from '../api/client';
import { Catalog, CustomVoice, NarrationCue, NarrationSegment, StoryResponse } from '../types';
import AudioPlayer from './AudioPlayer';
import Crest from './Crest';

export type BookStatus = 'idle' | 'loading' | 'ready';

interface Props {
  catalog: Catalog;
  status: BookStatus;
  story: StoryResponse | null;
  themeEmoji: string;
  /** A cloned family voice to read with, instead of the catalog narrator. */
  voice: CustomVoice | null;
  /** Recording kept from an earlier reading of this story, so it plays again without a new request. */
  savedAudioUrl: string | null;
  savedCues: NarrationCue[];
  /** Picture URLs by key ("cover", "page-0", ...). null means pictures are off: text-only pages. */
  pictures: Record<string, string> | null;
  autoRead: boolean;
  onAutoRead: (on: boolean) => void;
  music: boolean;
  onMusic: (on: boolean) => void;
  picturesOn: boolean;
  picturesOffered: boolean;
  onPictures: (on: boolean) => void;
  onAudio: (url: string, cues: NarrationCue[]) => void;
  onAnother: () => void;
  onSurprise: () => void;
}

const CHARS_PER_PAGE = 520;
const TURN_MS = 900;

/** Phones show one page per leaf; wider screens show a two-page spread. */
function useSinglePage(): boolean {
  const query = '(max-width: 640px)';
  const [single, setSingle] = useState(() => window.matchMedia(query).matches);
  useEffect(() => {
    const m = window.matchMedia(query);
    const handler = (e: MediaQueryListEvent) => setSingle(e.matches);
    m.addEventListener('change', handler);
    return () => m.removeEventListener('change', handler);
  }, []);
  return single;
}

/** What the narrator reads: the title, then each paragraph in its own mood. */
function segmentsOf(story: StoryResponse): NarrationSegment[] {
  const paragraphs = story.paragraphs?.length
    ? story.paragraphs
    : story.story_text.split(/\n\s*\n/).map((text) => ({ text: text.trim(), mood: '' })).filter((p) => p.text);
  return [{ text: `${story.title}.`, mood: story.mood || paragraphs[0]?.mood || '' }, ...paragraphs];
}

/** A page's picture, or a gentle placeholder while it is being painted. */
const Picture: React.FC<{ src?: string }> = ({ src }) =>
  src ? (
    <div className="bk-pic">
      <img src={src} alt="" />
    </div>
  ) : (
    <div className="bk-pic bk-pic--waiting">
      <span className="bk-pic__brush" aria-hidden="true">🖌️</span>
      <p>painting…</p>
    </div>
  );

/** Group paragraphs into pages that fit the book. */
function paginate(text: string): string[][] {
  const paragraphs = text.split(/\n\s*\n/).map((p) => p.trim()).filter(Boolean);
  const pages: string[][] = [];
  let current: string[] = [];
  let size = 0;
  for (const p of paragraphs) {
    if (current.length && size + p.length > CHARS_PER_PAGE) {
      pages.push(current);
      current = [];
      size = 0;
    }
    current.push(p);
    size += p.length;
  }
  if (current.length) pages.push(current);
  return pages;
}

/**
 * A 3D storybook with a cover and flippable leaves. It sits open on a welcome page; when a story
 * is ready the pages become the story. Leaf i shows pages[2i] on its front (right-hand page) and
 * pages[2i+1] on its back (left-hand page once turned).
 */
const StoryBook: React.FC<Props> = ({
  catalog, status, story, themeEmoji, voice, savedAudioUrl, savedCues, pictures, autoRead, onAutoRead, music, onMusic,
  picturesOn, picturesOffered, onPictures, onAudio, onAnother, onSurprise,
}) => {
  const single = useSinglePage();
  const [flipped, setFlipped] = useState(0); // closed on first paint, then opens once
  const firstOpen = useRef(true);
  const [turning, setTurning] = useState<number | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [cues, setCues] = useState<NarrationCue[]>([]);
  const autoTarget = useRef<number | null>(null);
  const [narrating, setNarrating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const theme = story && catalog.themes.find((t) => t.id === story.meta.theme);
  const feeling = story && catalog.feelings.find((f) => f.id === story.meta.feeling);
  const narrator = story && catalog.narrators.find((n) => n.id === story.meta.narrator);
  const mood = story?.mood ? catalog.moods.find((m) => m.id === story.mood) : undefined;
  const musicOffered = catalog.providers.music?.enabled === 'true';
  const readBy = voice ? `🎙️ ${voice.name}` : narrator ? `${narrator.emoji} ${narrator.label}` : '';
  // Pages come from the server when it paginated the story (so pictures match); older stories paginate here.
  const textPages = useMemo(() => {
    if (!story) return [];
    if (story.pages?.length && story.paragraphs?.length) {
      return story.pages.map((p) => p.paragraphs.map((i) => story.paragraphs![i].text));
    }
    return paginate(story.story_text);
  }, [story]);
  const withPictures = pictures !== null;

  const readAloud = async () => {
    if (!story) return;
    setError(null);
    setNarrating(true);
    try {
      // Stories saved under an older narrator name are read by the first narrator who knows the language.
      const known = catalog.narrators.find((n) => n.id === story.meta.narrator && (!n.languages || n.languages.includes(story.meta.language)));
      const narratorId = known?.id || catalog.narrators.find((n) => !n.languages || n.languages.includes(story.meta.language))?.id || story.meta.narrator;
      const result = await api.narrate(segmentsOf(story), narratorId, story.meta.language, { voiceId: voice?.id, music, storyId: story.id });
      const url = api.mediaUrl(result.audio_url);
      setAudioUrl(url);
      setCues(result.cues || []);
      onAudio(url, result.cues || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'The narrator lost their voice. Try again.');
    } finally {
      setNarrating(false);
    }
  };

  // A new story (or a reset): close briefly, flip open, reuse a saved recording or start reading.
  // While the story is being written the book simply stays open on the "writing" page.
  useEffect(() => {
    setAudioUrl(savedAudioUrl);
    setCues(savedCues);
    autoTarget.current = null;
    setError(null);
    if (status !== 'ready') {
      // Welcome and writing pages: on the very first load the closed book opens once; later, it just stays open.
      if (firstOpen.current) {
        // The flag flips only when the book really opens, so React's development double-run cannot skip the animation.
        const first = window.setTimeout(() => {
          firstOpen.current = false;
          setTurning(0);
          setFlipped(1);
          window.setTimeout(() => setTurning(null), TURN_MS);
        }, 700);
        return () => window.clearTimeout(first);
      }
      setTurning(null);
      setFlipped(1);
      return;
    }
    firstOpen.current = false;
    setFlipped(0);
    const open = window.setTimeout(() => {
      setTurning(0);
      setFlipped(1);
    }, 500);
    const settle = window.setTimeout(() => setTurning(null), 500 + TURN_MS);
    let read: number | undefined;
    if (status === 'ready' && story && autoRead && !savedAudioUrl) {
      read = window.setTimeout(() => void readAloud(), 900);
    }
    return () => {
      window.clearTimeout(open);
      window.clearTimeout(settle);
      if (read) window.clearTimeout(read);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [story, status, savedAudioUrl]);

  // ---- pages -------------------------------------------------------------------------
  // Order: cover, inside, [cover picture], then for each text page: text, [picture]; finally the end page.
  const pages: React.ReactNode[] = [];
  const textPagePos: number[] = []; // position of each text page in `pages`, for auto page turns
  if (status === 'ready' && story) {
    pages.push(
      <div className="bk-cover">
        <span className="bk-cover__art">{theme?.emoji || themeEmoji}</span>
        <h2 className="bk-cover__title">{story.title}</h2>
        {readBy && <p className="bk-cover__by">read by {readBy}</p>}
        <p className="bk-cover__hint">tap to open</p>
      </div>
    );
    pages.push(
      <div className="bk-inside">
        <div className="bk-stamps">
          {theme && <span className="stamp">{theme.emoji} {theme.label}</span>}
          {feeling && <span className="stamp">{feeling.emoji} {feeling.label}</span>}
          {mood && mood.id !== feeling?.id && <span className="stamp">{mood.emoji} {mood.label}</span>}
          <span className="stamp">⏱ {story.meta.estimated_minutes} min</span>
        </div>
        <h3 className="bk-inside__title">{story.title}</h3>
        {readBy && <p className="bk-inside__by">read by {readBy}</p>}
        <div className="bk-listen" onClick={(e) => e.stopPropagation()}>
          {audioUrl ? (
            <AudioPlayer src={audioUrl} onTime={followNarration} />
          ) : (
            <button type="button" className="button button--paper button--compact" onClick={readAloud} disabled={narrating}>
              {narrating ? <><span className="spinner" aria-hidden="true" /> warming up…</> : <><span aria-hidden="true">🔊</span> Read it to me</>}
            </button>
          )}
        </div>
        {error && <p className="bk-error">{error}</p>}
        <p className="bk-inside__hint">tap the right page to turn →</p>
      </div>
    );
    if (withPictures) pages.push(<Picture src={pictures?.cover} />);
    textPages.forEach((paras, i) => {
      textPagePos.push(pages.length);
      pages.push(
        <div className="bk-text">
          {paras.map((p, j) => (
            <p key={j}>{p}</p>
          ))}
          <span className="bk-pageno">{i + 1}</span>
        </div>
      );
      if (withPictures) pages.push(<Picture src={pictures?.[`page-${i}`]} />);
    });
    pages.push(
      <div className="bk-end" onClick={(e) => e.stopPropagation()}>
        <p className="bk-end__fin">~ the end ~</p>
        <p className="bk-end__note">saved to My stories</p>
        <button type="button" className="button button--cta button--compact" onClick={onAnother}>
          <span aria-hidden="true">✨</span> Another story
        </button>
        <button type="button" className="button button--paper button--compact" onClick={onSurprise}>
          <span aria-hidden="true">🎲</span> Surprise me
        </button>
      </div>
    );
  } else if (status === 'loading') {
    pages.push(
      <div className="bk-cover bk-cover--idle">
        <Crest kind="book" />
        <h2 className="bk-cover__title">Your storybook</h2>
      </div>
    );
    pages.push(
      <div className="bk-inside">
        <Crest kind="quill" />
        <h3 className="bk-inside__title">Writing your story…</h3>
        <p className="bk-inside__by">the quill is busy, the pages are waiting</p>
      </div>
    );
    pages.push(<div className="bk-text bk-text--waiting"><p>…</p></div>);
  } else {
    pages.push(
      <div className="bk-cover bk-cover--idle">
        <Crest kind="book" />
        <h2 className="bk-cover__title">Your storybook</h2>
      </div>
    );
    pages.push(
      <div className="bk-inside">
        <Crest kind="castle" />
        <h3 className="bk-inside__title">Welcome!</h3>
        <p className="bk-inside__by">This book will hold your story.</p>
        <p className="bk-inside__hint">flip the pages to see how it works →</p>
      </div>
    );
    pages.push(
      <div className="bk-how">
        <span className="bk-how__step">1</span>
        <span className="bk-how__art bk-how__art--mic">🎤</span>
        <h3 className="bk-inside__title">Say it</h3>
        <p>Scroll down, tap the microphone and tell us your idea. Or type it, if you like.</p>
      </div>
    );
    pages.push(
      <div className="bk-how">
        <span className="bk-how__step">2</span>
        <Crest kind="balloon" />
        <h3 className="bk-inside__title">Pick a world</h3>
        <p>Choose a language, a world, a feeling, who tells the tale and who is in it.</p>
      </div>
    );
    pages.push(
      <div className="bk-how">
        <span className="bk-how__step">3</span>
        <Crest kind="sound" />
        <h3 className="bk-inside__title">Listen</h3>
        <p>A brand-new story is written just for you, lands in this book, and is read out loud.</p>
      </div>
    );
    pages.push(
      <div className="bk-end" onClick={(e) => e.stopPropagation()}>
        <p className="bk-end__fin">~ ready? ~</p>
        <a className="button button--cta button--compact" href="#make">
          <span aria-hidden="true">✨</span> make a story
        </a>
        <button type="button" className="button button--paper button--compact" onClick={onSurprise}>
          <span aria-hidden="true">🎲</span> Surprise me
        </button>
      </div>
    );
  }
  const endPos = pages.length - 1;
  if (!single && pages.length % 2) pages.push(<div className="bk-blank" />);
  const leaves = single ? pages.length : pages.length / 2;
  /** How many leaves must be turned to show the page at `pos`. */
  const flippedFor = (pos: number) => (single ? pos : Math.ceil(pos / 2));
  const front = (i: number) => (single ? pages[i] : pages[2 * i]);
  const back = (i: number) => (single ? <div className="bk-blank" /> : pages[2 * i + 1]);
  const isOpen = flipped > 0;
  const canTurn = status !== 'loading';

  function turn(to: number) {
    const target = Math.max(0, Math.min(leaves, to));
    if (target === flipped) return;
    const leaf = target > flipped ? flipped : target;
    setTurning(leaf);
    setFlipped(target);
    window.setTimeout(() => setTurning(null), TURN_MS);
  }

  // The book turns its own pages as the reading reaches them. Cue 0 is the title; cue n is paragraph n-1.
  function followNarration(seconds: number) {
    if (!story || !cues.length || !story.pages?.length) return;
    let target: number | null = null;
    const last = cues[cues.length - 1];
    if (seconds >= last.end + 0.3) {
      target = flippedFor(endPos);
    } else {
      const cue = cues.find((c) => seconds >= c.start && seconds < c.end);
      if (!cue) return;
      if (cue.index === 0) target = 1;
      else {
        const page = story.pages.findIndex((p) => p.paragraphs.includes(cue.index - 1));
        if (page >= 0 && textPagePos[page] !== undefined) target = flippedFor(textPagePos[page]);
      }
    }
    if (target === null || target === autoTarget.current) return; // only act when the reading moves on
    autoTarget.current = target;
    if (turning === null) turn(target);
  }

  return (
    <section className="bookstage" id="book">
      <div className={`flipbook ${single ? 'flipbook--single' : ''} ${isOpen ? 'is-open' : 'is-closed'} ${status === 'loading' ? 'is-loading' : ''}`}>
        <div className="flipbook__spread">
          {Array.from({ length: leaves }, (_, i) => {
            const isFlipped = i < flipped;
            const z = turning === i ? leaves * 2 + 1 : isFlipped ? i + 1 : leaves - i;
            return (
              <div
                key={i}
                className={`leaf ${isFlipped ? 'is-flipped' : ''} ${i === 0 ? 'leaf--cover' : ''} ${i === leaves - 1 ? 'leaf--last' : ''}`}
                style={{ zIndex: z }}
                onClick={() => canTurn && turn(isFlipped ? i : i + 1)}
                role={canTurn ? 'button' : undefined}
                aria-label={canTurn ? (isFlipped ? 'Turn back' : 'Turn the page') : undefined}
              >
                <div className="leaf__face leaf__face--front">{front(i)}</div>
                <div className="leaf__face leaf__face--back">{back(i)}</div>
              </div>
            );
          })}
        </div>
        <span className="flipbook__sparkle flipbook__sparkle--1">✦</span>
        <span className="flipbook__sparkle flipbook__sparkle--2">✦</span>
        <span className="flipbook__sparkle flipbook__sparkle--3">✦</span>
      </div>

      <div className="flipbook__nav">
        <button type="button" className="pagebtn" onClick={() => turn(flipped - 1)} disabled={!canTurn || flipped === 0} aria-label="Previous page">‹</button>
        <span className="flipbook__count">{flipped === 0 ? 'cover' : `page ${flipped} of ${leaves}`}</span>
        <button type="button" className="pagebtn pagebtn--next" onClick={() => turn(flipped + 1)} disabled={!canTurn || flipped === leaves} aria-label="Next page">›</button>
      </div>
      <div className="toggles">
        <label className="toggle">
          <input type="checkbox" checked={autoRead} onChange={(e) => onAutoRead(e.target.checked)} />
          <span className="toggle__box" aria-hidden="true" />
          read new stories to me by themselves
        </label>
        {musicOffered && (
          <label className="toggle" title="Mixed into the recording when a story is read. Applies to the next reading.">
            <input type="checkbox" checked={music} onChange={(e) => onMusic(e.target.checked)} />
            <span className="toggle__box" aria-hidden="true" />
            music under the story
          </label>
        )}
        {picturesOffered && (
          <label className="toggle" title="Paint a picture for the cover and every page of new stories.">
            <input type="checkbox" checked={picturesOn} onChange={(e) => onPictures(e.target.checked)} />
            <span className="toggle__box" aria-hidden="true" />
            pictures on the pages
          </label>
        )}
      </div>
    </section>
  );
};

export default StoryBook;

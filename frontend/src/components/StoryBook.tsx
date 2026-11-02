import React, { useEffect, useMemo, useState } from 'react';
import { api } from '../api/client';
import { Catalog, CustomVoice, StoryResponse } from '../types';
import AudioPlayer from './AudioPlayer';

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
  autoRead: boolean;
  onAutoRead: (on: boolean) => void;
  onAudio: (url: string) => void;
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
  catalog, status, story, themeEmoji, voice, savedAudioUrl, autoRead, onAutoRead, onAudio, onAnother, onSurprise,
}) => {
  const single = useSinglePage();
  const [flipped, setFlipped] = useState(1);
  const [turning, setTurning] = useState<number | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [narrating, setNarrating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const theme = story && catalog.themes.find((t) => t.id === story.meta.theme);
  const feeling = story && catalog.feelings.find((f) => f.id === story.meta.feeling);
  const narrator = story && catalog.narrators.find((n) => n.id === story.meta.narrator);
  const readBy = voice ? `🎙️ ${voice.name}` : narrator ? `${narrator.emoji} ${narrator.label}` : '';
  const textPages = useMemo(() => (story ? paginate(story.story_text) : []), [story]);

  const readAloud = async () => {
    if (!story) return;
    setError(null);
    setNarrating(true);
    try {
      const result = await api.narrate(`${story.title}.\n\n${story.story_text}`, story.meta.narrator, story.meta.language, voice?.id);
      const url = api.mediaUrl(result.audio_url);
      setAudioUrl(url);
      onAudio(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'The narrator lost their voice. Try again.');
    } finally {
      setNarrating(false);
    }
  };

  // A new story (or a reset): close briefly, flip open, reuse a saved recording or start reading.
  useEffect(() => {
    setAudioUrl(savedAudioUrl);
    setError(null);
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
  const pages: React.ReactNode[] = [];
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
          <span className="stamp">⏱ {story.meta.estimated_minutes} min</span>
        </div>
        <h3 className="bk-inside__title">{story.title}</h3>
        {readBy && <p className="bk-inside__by">read by {readBy}</p>}
        <div className="bk-listen" onClick={(e) => e.stopPropagation()}>
          {audioUrl ? (
            <AudioPlayer src={audioUrl} />
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
    textPages.forEach((paras, i) => {
      pages.push(
        <div className="bk-text">
          {paras.map((p, j) => (
            <p key={j}>{p}</p>
          ))}
          <span className="bk-pageno">{i + 1}</span>
        </div>
      );
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
        <span className="bk-cover__art">✨</span>
        <h2 className="bk-cover__title">Your storybook</h2>
      </div>
    );
    pages.push(
      <div className="bk-inside">
        <span className="bk-cover__art">✒️</span>
        <h3 className="bk-inside__title">Writing your story…</h3>
        <p className="bk-inside__by">the quill is busy, the pages are waiting</p>
      </div>
    );
    pages.push(<div className="bk-text bk-text--waiting"><p>…</p></div>);
  } else {
    pages.push(
      <div className="bk-cover bk-cover--idle">
        <span className="bk-cover__art">📖</span>
        <h2 className="bk-cover__title">Your storybook</h2>
      </div>
    );
    pages.push(
      <div className="bk-inside">
        <span className="bk-cover__art">{themeEmoji}</span>
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
        <span className="bk-how__art bk-how__art--map">🗺️</span>
        <h3 className="bk-inside__title">Pick a world</h3>
        <p>Choose a language, a world, a feeling, who tells the tale and who is in it.</p>
      </div>
    );
    pages.push(
      <div className="bk-how">
        <span className="bk-how__step">3</span>
        <span className="bk-how__art bk-how__art--sound">🔊</span>
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
  if (!single && pages.length % 2) pages.push(<div className="bk-blank" />);
  const leaves = single ? pages.length : pages.length / 2;
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
      <label className="toggle">
        <input type="checkbox" checked={autoRead} onChange={(e) => onAutoRead(e.target.checked)} />
        <span className="toggle__box" aria-hidden="true" />
        read new stories to me by themselves
      </label>
    </section>
  );
};

export default StoryBook;

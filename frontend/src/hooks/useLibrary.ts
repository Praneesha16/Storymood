import { useCallback } from 'react';
import { NarrationCue, SavedStory, StoryResponse } from '../types';
import { useStoredState } from './useStoredState';

const MAX_STORIES = 30;

function randomId(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) return crypto.randomUUID();
  return `s-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
}

/** The child's bookshelf: every story made in this browser, newest first, with its narration when it has one. */
export function useLibrary() {
  const [items, setItems] = useStoredState<SavedStory[]>('storymood.library', []);

  const add = useCallback(
    (story: StoryResponse, voiceName: string | null): SavedStory => {
      // The server's record id is reused so the two copies stay in step.
      const saved: SavedStory = { id: story.id || randomId(), story, audioUrl: null, voiceName, createdAt: new Date().toISOString() };
      setItems((prev) => [saved, ...prev].slice(0, MAX_STORIES));
      return saved;
    },
    [setItems]
  );

  const setAudio = useCallback(
    (id: string, audioUrl: string, audioCues: NarrationCue[] = []) =>
      setItems((prev) => prev.map((s) => (s.id === id ? { ...s, audioUrl, audioCues } : s))),
    [setItems]
  );

  const setPicture = useCallback(
    (id: string, key: string, url: string) =>
      setItems((prev) => prev.map((s) => (s.id === id ? { ...s, pictures: { ...(s.pictures || {}), [key]: url } } : s))),
    [setItems]
  );

  const remove = useCallback((id: string) => setItems((prev) => prev.filter((s) => s.id !== id)), [setItems]);

  return { items, add, setAudio, setPicture, remove };
}

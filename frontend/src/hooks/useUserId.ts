import { useMemo } from 'react';

const KEY = 'storymood.user_id';

function randomId(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) return crypto.randomUUID();
  return `u-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
}

/** Anonymous per-browser id used to file stories in the vault. Falls back to a session id when storage is blocked. */
export function useUserId(): string {
  return useMemo(() => {
    try {
      const existing = localStorage.getItem(KEY);
      if (existing) return existing;
      const fresh = randomId();
      localStorage.setItem(KEY, fresh);
      return fresh;
    } catch {
      return randomId();
    }
  }, []);
}

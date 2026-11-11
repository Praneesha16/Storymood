import { useCallback, useState } from 'react';

/**
 * useState that survives reloads via localStorage. Falls back to memory when storage is
 * blocked (private windows, strict settings), so the app always works.
 */
export function useStoredState<T>(key: string, initial: T): [T, (next: T | ((prev: T) => T)) => void] {
  const [value, setValue] = useState<T>(() => {
    try {
      const raw = localStorage.getItem(key);
      return raw === null ? initial : (JSON.parse(raw) as T);
    } catch {
      return initial;
    }
  });

  const set = useCallback(
    (next: T | ((prev: T) => T)) => {
      setValue((prev) => {
        const resolved = typeof next === 'function' ? (next as (p: T) => T)(prev) : next;
        try {
          localStorage.setItem(key, JSON.stringify(resolved));
        } catch {
          /* storage unavailable: keep in memory only */
        }
        return resolved;
      });
    },
    [key]
  );

  return [value, set];
}

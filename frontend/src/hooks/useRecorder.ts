import { useCallback, useEffect, useRef, useState } from 'react';
import { MAX_RECORDING_SECONDS } from '../config';

export interface Recording {
  blob: Blob;
  filename: string;
}

/** Pick the first container the browser can record. Safari needs mp4; everyone else does webm. */
function pickMimeType(): { mime: string; ext: string } {
  const candidates: Array<[string, string]> = [
    ['audio/webm;codecs=opus', 'webm'],
    ['audio/webm', 'webm'],
    ['audio/mp4', 'm4a'],
    ['audio/ogg;codecs=opus', 'ogg'],
  ];
  for (const [mime, ext] of candidates) {
    if (typeof MediaRecorder !== 'undefined' && MediaRecorder.isTypeSupported(mime)) return { mime, ext };
  }
  return { mime: '', ext: 'webm' };
}

/**
 * Microphone recorder with a single toggle.
 * start() asks for the mic; stop() resolves with the recorded clip.
 */
export function useRecorder() {
  const [isRecording, setIsRecording] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const stopResolverRef = useRef<((r: Recording) => void) | null>(null);
  const timerRef = useRef<number | null>(null);
  const extRef = useRef('webm');

  const supported =
    typeof navigator !== 'undefined' && !!navigator.mediaDevices?.getUserMedia && typeof MediaRecorder !== 'undefined';

  const clearTimer = () => {
    if (timerRef.current !== null) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  const stop = useCallback((): Promise<Recording | null> => {
    const recorder = recorderRef.current;
    if (!recorder || recorder.state === 'inactive') return Promise.resolve(null);
    return new Promise((resolve) => {
      stopResolverRef.current = resolve;
      recorder.stop();
    });
  }, []);

  const start = useCallback(async () => {
    setError(null);
    if (!supported) {
      setError('This browser cannot record audio. Try Chrome, Edge or Safari.');
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const { mime, ext } = pickMimeType();
      extRef.current = ext;
      const recorder = mime ? new MediaRecorder(stream, { mimeType: mime }) : new MediaRecorder(stream);
      chunksRef.current = [];
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      recorder.onstop = () => {
        clearTimer();
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(chunksRef.current, { type: recorder.mimeType || mime || 'audio/webm' });
        setIsRecording(false);
        stopResolverRef.current?.({ blob, filename: `idea.${extRef.current}` });
        stopResolverRef.current = null;
      };
      recorderRef.current = recorder;
      recorder.start();
      setSeconds(0);
      setIsRecording(true);
      timerRef.current = window.setInterval(() => {
        setSeconds((s) => {
          if (s + 1 >= MAX_RECORDING_SECONDS) recorder.state === 'recording' && recorder.stop();
          return s + 1;
        });
      }, 1000);
    } catch (err) {
      const name = err instanceof DOMException ? err.name : '';
      setError(
        name === 'NotAllowedError'
          ? 'Microphone is blocked. Allow it in the browser and try again.'
          : 'Could not start the microphone.'
      );
    }
  }, [supported]);

  useEffect(() => {
    return () => {
      clearTimer();
      const r = recorderRef.current;
      if (r && r.state !== 'inactive') r.stop();
    };
  }, []);

  return { supported, isRecording, seconds, error, start, stop };
}

import React, { useLayoutEffect, useRef, useState } from 'react';
import { api } from '../api/client';
import { useRecorder } from '../hooks/useRecorder';
import { LanguageOption } from '../types';
import MicButton from './MicButton';

interface Props {
  value: string;
  onChange: (text: string) => void;
  language: string;
  languages: LanguageOption[];
  onDetectedLanguage: (code: string) => void;
}

/** The idea tray: a microphone tile plus a written line. Spoken ideas are transcribed and appended. */
const IdeaBox: React.FC<Props> = ({ value, onChange, language, languages, onDetectedLanguage }) => {
  const recorder = useRecorder();
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const box = useRef<HTMLTextAreaElement>(null);

  // Grow with the writing so the ruled paper never scrolls and every row keeps its line.
  useLayoutEffect(() => {
    const t = box.current;
    if (!t) return;
    t.style.height = 'auto';
    t.style.height = `${t.scrollHeight + t.offsetHeight - t.clientHeight}px`;
  }, [value]);

  const toggle = async () => {
    setError(null);
    setNote(null);
    if (!recorder.isRecording) {
      await recorder.start();
      return;
    }
    const clip = await recorder.stop();
    if (!clip || clip.blob.size < 1000) {
      setError('I did not catch that. Try talking a little longer.');
      return;
    }
    setBusy(true);
    try {
      const result = await api.transcribe(clip.blob, clip.filename);
      if (!result.text) {
        setError('I heard silence. Try again a bit louder!');
        return;
      }
      onChange(value.trim() ? `${value.trim()} ${result.text}` : result.text);
      if (result.language && result.language !== language) {
        const found = languages.find((l) => l.code === result.language);
        if (found) {
          onDetectedLanguage(found.code);
          setNote(`You spoke ${found.label}, so the story will be in ${found.native}.`);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not understand the recording.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="idea">
      <MicButton
        isRecording={recorder.isRecording}
        busy={busy}
        seconds={recorder.seconds}
        disabled={!recorder.supported}
        onToggle={toggle}
      />
      <div className="idea__write">
        <label className="idea__label" htmlFor="idea">
          or write it down
        </label>
        <textarea
          ref={box}
          id="idea"
          className="idea__input"
          placeholder="A dragon who is scared of butterflies…"
          value={value}
          maxLength={600}
          rows={3}
          onChange={(e) => onChange(e.target.value)}
        />
        {value && (
          <button type="button" className="link-button" onClick={() => onChange('')}>
            clear
          </button>
        )}
      </div>
      {(recorder.error || error) && <p className="idea__error">{recorder.error || error}</p>}
      {note && <p className="idea__note">{note}</p>}
    </div>
  );
};

export default IdeaBox;

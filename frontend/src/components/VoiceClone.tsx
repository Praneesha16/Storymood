import React, { useState } from 'react';
import { api } from '../api/client';
import { useRecorder } from '../hooks/useRecorder';
import { CustomVoice, LanguageOption } from '../types';
import MicButton from './MicButton';

interface Props {
  language: string;
  languages: LanguageOption[];
  voice: CustomVoice | null;
  selected: boolean;
  onSelect: () => void;
  onCloned: (voice: CustomVoice) => void;
  onForget: () => void;
}

/** One sentence per language for the grown-up to read while recording. */
const SAMPLE: Record<string, string> = {
  en: 'Once upon a time, in a land of tall trees and gentle rivers, a little fox set off to find the moon. She packed a lantern, a blanket and three sweet apples, and she sang all the way.',
  hi: 'बहुत समय पहले, ऊँचे पेड़ों और शांत नदियों के देश में, एक छोटी लोमड़ी चाँद को ढूँढने निकली। उसने एक लालटेन, एक कंबल और तीन मीठे सेब साथ रखे, और रास्ते भर गाती रही।',
  te: 'ఒకప్పుడు, పొడవైన చెట్లు, నెమ్మదైన నదుల దేశంలో, ఒక చిన్న నక్క చంద్రుడిని వెతకడానికి బయలుదేరింది. ఒక దీపం, ఒక దుప్పటి, మూడు తీపి ఆపిల్స్ తీసుకుని దారి పొడవునా పాడుతూ వెళ్ళింది.',
  ta: 'ஒரு காலத்தில், உயரமான மரங்களும் அமைதியான ஆறுகளும் நிறைந்த நாட்டில், ஒரு சிறிய நரி நிலவைத் தேடிப் புறப்பட்டது. ஒரு விளக்கு, ஒரு போர்வை, மூன்று இனிப்பு ஆப்பிள்களை எடுத்துக்கொண்டு வழி முழுவதும் பாடிக்கொண்டே சென்றது.',
  ml: 'പണ്ടുപണ്ട്, ഉയരമുള്ള മരങ്ങളും ശാന്തമായ നദികളുമുള്ള നാട്ടിൽ, ഒരു കുഞ്ഞു കുറുക്കൻ ചന്ദ്രനെ തേടി പുറപ്പെട്ടു. ഒരു വിളക്കും ഒരു പുതപ്പും മൂന്ന് മധുരമുള്ള ആപ്പിളുകളും എടുത്ത്, വഴിയിലുടനീളം പാടിക്കൊണ്ടിരുന്നു.',
};

/**
 * "Read it in my voice": a grown-up records one sentence, the voice provider clones it, and the
 * clone becomes a narrator choice. The voice id is kept in this browser only.
 */
const VoiceClone: React.FC<Props> = ({ language, languages, voice, selected, onSelect, onCloned, onForget }) => {
  const recorder = useRecorder();
  const [open, setOpen] = useState(false);
  const [name, setName] = useState(voice?.name || 'My voice');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const toggleRecord = async () => {
    setError(null);
    if (!recorder.isRecording) {
      await recorder.start();
      return;
    }
    const clip = await recorder.stop();
    if (!clip || recorder.seconds < 5) {
      setError('Please read the whole sentence, at least five seconds.');
      return;
    }
    setBusy(true);
    try {
      const result = await api.cloneVoice(clip.blob, clip.filename, name.trim() || 'My voice', language);
      onCloned({ id: result.voice_id, name: result.name, language, createdAt: new Date().toISOString() });
      setOpen(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not build the voice.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <button
        type="button"
        role="radio"
        aria-checked={selected}
        className={`option option--voice ${selected ? 'is-selected' : ''}`}
        onClick={() => (voice ? onSelect() : setOpen(true))}
      >
        <span className="option__emoji" aria-hidden="true">🎙️</span>
        <span className="option__label">{voice ? voice.name : 'My voice'}</span>
        <span className="option__hint">{voice ? 'a family voice' : 'record one sentence'}</span>
      </button>
      {(voice || open) && (
      <div className="voiceclone__panel">
      {voice && (
        <div className="voiceclone__links">
          <button type="button" className="link-button" onClick={() => setOpen((o) => !o)}>
            {open ? 'close' : 're-record'}
          </button>
          <button type="button" className="link-button" onClick={onForget}>
            forget this voice
          </button>
        </div>
      )}

      {open && (
        <div className="clonebox" role="region" aria-label="Record a family voice">
          <p className="clonebox__note">
            <span aria-hidden="true">🧑‍🧒</span> Ask a grown-up to record this. The clip is sent to our voice provider to build the voice, and stays private to this app.
          </p>
          <p className="clonebox__sentence" lang={language}>
            “{SAMPLE[language] || SAMPLE.en}”
          </p>
          <div className="clonebox__row">
            <label className="clonebox__name">
              <span>whose voice?</span>
              <input className="text-input" value={name} maxLength={40} onChange={(e) => setName(e.target.value)} placeholder="Mum, Dad, Grandma…" />
            </label>
            <MicButton
              isRecording={recorder.isRecording}
              busy={busy}
              seconds={recorder.seconds}
              disabled={!recorder.supported}
              onToggle={toggleRecord}
            />
          </div>
          {(recorder.error || error) && <p className="idea__error">{recorder.error || error}</p>}
          {busy && <p className="idea__note">Building the voice… this takes a few seconds.</p>}
        </div>
      )}
      </div>
      )}
    </>
  );
};

export default VoiceClone;

import React from 'react';
import { Catalog, CustomVoice, StoryRequest } from '../types';
import CharacterPicker from './CharacterPicker';
import IdeaBox from './IdeaBox';
import OptionGrid, { GridOption } from './OptionGrid';
import VoiceClone from './VoiceClone';

interface Props {
  catalog: Catalog;
  draft: StoryRequest;
  onChange: (draft: StoryRequest) => void;
  onSubmit: () => void;
  onSurprise: () => void;
  busy: boolean;
  error: string | null;
  customVoice: CustomVoice | null;
  useCustomVoice: boolean;
  onUseCustomVoice: (use: boolean) => void;
  onVoiceCloned: (voice: CustomVoice) => void;
  onForgetVoice: () => void;
}

const Section: React.FC<{ title: string; sub?: string; children: React.ReactNode }> = ({ title, sub, children }) => (
  <section className="sect">
    <div className="sect__head">
      <h2 className="sect__title">{title}</h2>
      {sub && <p className="sect__sub">{sub}</p>}
    </div>
    {children}
  </section>
);

/** Every choice on one scrolling page. */
const Maker: React.FC<Props> = ({
  catalog, draft, onChange, onSubmit, onSurprise, busy, error,
  customVoice, useCustomVoice, onUseCustomVoice, onVoiceCloned, onForgetVoice,
}) => {
  const set = <K extends keyof StoryRequest>(key: K, value: StoryRequest[K]) => onChange({ ...draft, [key]: value });
  const canClone = catalog.providers.tts.cloning === 'true';

  const languageOptions: GridOption[] = catalog.languages.map((l) => ({ id: l.code, label: l.native, emoji: l.emoji, hint: l.label }));
  const narratorOptions: GridOption[] = catalog.narrators.map((n) => ({ id: n.id, label: n.label, emoji: n.emoji, hint: n.blurb }));
  const lengthOptions: GridOption[] = catalog.lengths.map((l) => ({ id: l.id, label: `${l.label} · ${l.minutes}`, emoji: l.emoji }));
  const ageOptions: GridOption[] = catalog.age_groups.map((a) => ({ id: a.id, label: `ages ${a.label}`, emoji: a.emoji }));

  return (
    <div className="maker" id="make">
      <Section title="Which language?" sub="the story will be told in it">
        <OptionGrid options={languageOptions} value={draft.language} onChange={(v) => set('language', v)} ariaLabel="Language" />
      </Section>

      <Section title="What kind of story?" sub="pick a world to visit">
        <OptionGrid options={catalog.themes} value={draft.theme} onChange={(v) => set('theme', v)} ariaLabel="Kind of story" />
      </Section>

      <Section title="How should it feel?">
        <OptionGrid options={catalog.feelings} value={draft.feeling} onChange={(v) => set('feeling', v)} ariaLabel="Feeling" />
      </Section>

      <Section title="Who will tell it?" sub="every voice reads a little differently">
        <OptionGrid
          options={narratorOptions}
          value={useCustomVoice ? '' : draft.narrator}
          onChange={(v) => {
            set('narrator', v);
            onUseCustomVoice(false);
          }}
          ariaLabel="Narrator"
        >
          {canClone && (
            <VoiceClone
              language={draft.language}
              languages={catalog.languages}
              voice={customVoice}
              selected={useCustomVoice}
              onSelect={() => onUseCustomVoice(true)}
              onCloned={onVoiceCloned}
              onForget={onForgetVoice}
            />
          )}
        </OptionGrid>
      </Section>

      <Section title="Who is in it?" sub="give your heroes a name, or let the story invent them">
        <CharacterPicker characters={draft.characters} onChange={(c) => set('characters', c)} />
      </Section>

      <Section title="Anything special?" sub="say it with the microphone, or write it">
        <IdeaBox
          value={draft.idea}
          onChange={(idea) => set('idea', idea)}
          language={draft.language}
          languages={catalog.languages}
          onDetectedLanguage={(code) => set('language', code)}
        />
      </Section>

      <Section title="How long, and for whom?">
        <div className="pills-row">
          <div>
            <h3 className="sect__label">How long</h3>
            <OptionGrid options={lengthOptions} value={draft.length} onChange={(v) => set('length', v)} ariaLabel="Story length" variant="pill" />
          </div>
          <div>
            <h3 className="sect__label">For ages</h3>
            <OptionGrid options={ageOptions} value={draft.age_group} onChange={(v) => set('age_group', v)} ariaLabel="Age group" variant="pill" />
          </div>
        </div>
      </Section>

      <div className="make">
        {error && (
          <div className="banner banner--error" role="alert">
            <span aria-hidden="true">😵‍💫</span> {error}
          </div>
        )}
        <div className="make__row">
          <button type="button" className="button button--cta" onClick={onSubmit} disabled={busy}>
            {busy ? <><span className="spinner" aria-hidden="true" /> Writing…</> : <><span aria-hidden="true">✨</span> Make my story</>}
            <span className="sparkles" aria-hidden="true"><i /><i /><i /><i /><i /><i /></span>
          </button>
          <button type="button" className="button button--glass" onClick={onSurprise} disabled={busy} title="Pick a random world, feeling and narrator">
            <span aria-hidden="true">🎲</span> Surprise me
          </button>
        </div>
        <p className="make__hint">your book at the top opens when it is ready</p>
      </div>
    </div>
  );
};

export default Maker;

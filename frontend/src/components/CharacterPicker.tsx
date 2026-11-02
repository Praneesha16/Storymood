import React, { useState } from 'react';
import { Character } from '../types';

interface Props {
  characters: Character[];
  onChange: (characters: Character[]) => void;
  max?: number;
}

const TRAITS = ['brave', 'curious', 'silly', 'kind', 'shy', 'clever'];

/** Add up to a few named characters as colourful chips. */
const CharacterPicker: React.FC<Props> = ({ characters, onChange, max = 4 }) => {
  const [name, setName] = useState('');
  const [trait, setTrait] = useState('');

  const add = () => {
    const clean = name.trim();
    if (!clean || characters.length >= max) return;
    onChange([...characters, { name: clean, trait }]);
    setName('');
    setTrait('');
  };

  const remove = (index: number) => onChange(characters.filter((_, i) => i !== index));

  return (
    <div className="characters">
      {characters.length > 0 && (
        <ul className="characters__list" aria-label="Characters in the story">
          {characters.map((c, i) => (
            <li key={`${c.name}-${i}`} className="character-chip">
              <span>
                {c.name}
                {c.trait && <small> · {c.trait}</small>}
              </span>
              <button type="button" aria-label={`Remove ${c.name}`} onClick={() => remove(i)}>
                ×
              </button>
            </li>
          ))}
        </ul>
      )}
      {characters.length < max && (
        <div className="characters__form">
          <input
            className="text-input"
            placeholder="Name (like Mia or Leo)"
            value={name}
            maxLength={40}
            onChange={(e) => setName(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), add())}
            aria-label="Character name"
          />
          <div className="trait-row" role="radiogroup" aria-label="Character trait">
            {TRAITS.map((t) => (
              <button
                key={t}
                type="button"
                role="radio"
                aria-checked={trait === t}
                className={`trait ${trait === t ? 'is-selected' : ''}`}
                onClick={() => setTrait(trait === t ? '' : t)}
              >
                {t}
              </button>
            ))}
          </div>
          <button type="button" className="button button--small" onClick={add} disabled={!name.trim()}>
            + Add
          </button>
        </div>
      )}
    </div>
  );
};

export default CharacterPicker;

import React, { useEffect, useRef, useState } from 'react';
import { Character } from '../types';

interface Props {
  characters: Character[];
  onChange: (characters: Character[]) => void;
  max?: number;
}

const TRAITS = ['brave', 'curious', 'silly', 'kind', 'shy', 'clever'];
const PICTURE_MAX_SIDE = 640; // pictures are shrunk in the browser before they go anywhere

/** Read a chosen photo or drawing and shrink it to a small JPEG data URL. */
async function shrink(file: File): Promise<string> {
  const url = URL.createObjectURL(file);
  try {
    const img = new Image();
    await new Promise<void>((resolve, reject) => {
      img.onload = () => resolve();
      img.onerror = () => reject(new Error('unreadable'));
      img.src = url;
    });
    const scale = Math.min(1, PICTURE_MAX_SIDE / Math.max(img.width, img.height));
    const canvas = document.createElement('canvas');
    canvas.width = Math.max(1, Math.round(img.width * scale));
    canvas.height = Math.max(1, Math.round(img.height * scale));
    canvas.getContext('2d')!.drawImage(img, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg', 0.85);
  } finally {
    URL.revokeObjectURL(url);
  }
}

/**
 * Name a character, pick a trait, optionally add a picture of them (a photo, a drawing, a toy),
 * then press Save. Saved characters appear as chips, with their picture, so it is clear what is
 * in the story before adding the next one. Pictures guide the page paintings.
 */
const CharacterPicker: React.FC<Props> = ({ characters, onChange, max = 4 }) => {
  const [name, setName] = useState('');
  const [trait, setTrait] = useState('');
  const [image, setImage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [savedName, setSavedName] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!savedName) return;
    const t = window.setTimeout(() => setSavedName(null), 2500);
    return () => window.clearTimeout(t);
  }, [savedName]);

  const pick = async (file: File | undefined) => {
    setError(null);
    if (!file) return;
    try {
      setImage(await shrink(file));
    } catch {
      setError('That picture could not be read. Try a JPG or PNG.');
    }
  };

  const save = () => {
    const clean = name.trim();
    if (!clean || characters.length >= max) return;
    onChange([...characters, { name: clean, trait, image: image || undefined }]);
    setSavedName(clean);
    setName('');
    setTrait('');
    setImage(null);
    if (fileRef.current) fileRef.current.value = '';
  };

  const remove = (index: number) => onChange(characters.filter((_, i) => i !== index));

  return (
    <div className="characters">
      {characters.length > 0 && (
        <ul className="characters__list" aria-label="Characters in the story">
          {characters.map((c, i) => (
            <li key={`${c.name}-${i}`} className="character-chip">
              {c.image ? <img className="character-chip__pic" src={c.image} alt="" /> : <span className="character-chip__dot" aria-hidden="true" />}
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
      {savedName && (
        <p className="characters__saved" role="status">
          ✓ {savedName} is saved. {characters.length < max ? 'Add the next one, or carry on.' : 'That is the most for one story.'}
        </p>
      )}
      {characters.length < max && (
        <div className="characters__form">
          <input
            className="text-input"
            placeholder="Name (like Mia or Leo)"
            value={name}
            maxLength={40}
            onChange={(e) => setName(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), save())}
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
          <div className="charpic">
            <input
              ref={fileRef}
              id="charpic-file"
              type="file"
              accept="image/*"
              onChange={(e) => void pick(e.target.files?.[0])}
              aria-label="Picture of this character"
            />
            {image ? (
              <>
                <img className="charpic__preview" src={image} alt="" />
                <button type="button" className="link-button" onClick={() => { setImage(null); if (fileRef.current) fileRef.current.value = ''; }}>
                  remove picture
                </button>
              </>
            ) : (
              <label htmlFor="charpic-file" className="button button--small button--glass">
                Add a picture
              </label>
            )}
          </div>
          <button type="button" className="button button--small" onClick={save} disabled={!name.trim()}>
            Save character
          </button>
          <p className="charpic__note">
            A photo, a drawing or a toy. The pictures in the book will take after it. The picture is sent to the
            painter only while the book is being painted, and is not kept on our server.
          </p>
          {error && <p className="idea__error">{error}</p>}
        </div>
      )}
    </div>
  );
};

export default CharacterPicker;

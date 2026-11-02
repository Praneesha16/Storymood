import React from 'react';
import { Catalog, SavedStory } from '../types';

interface Props {
  catalog: Catalog;
  items: SavedStory[];
  currentId: string | null;
  onOpen: (saved: SavedStory) => void;
  onRemove: (id: string) => void;
}

const when = (iso: string) => {
  const d = new Date(iso);
  const days = Math.floor((Date.now() - d.getTime()) / 86400000);
  if (days === 0) return 'today';
  if (days === 1) return 'yesterday';
  if (days < 7) return `${days} days ago`;
  return d.toLocaleDateString();
};

/** The child's bookshelf. Tapping a book opens it in the big storybook above; stories with a recording play again at once. */
const Library: React.FC<Props> = ({ catalog, items, currentId, onOpen, onRemove }) => {
  if (items.length === 0) return null;
  return (
    <section className="library" id="library" aria-label="My stories">
      <div className="sect__head">
        <h2 className="sect__title">My stories</h2>
        <p className="sect__sub">tap a book to read it again · books with a 🔊 play by themselves</p>
      </div>
      <div className="covers">
        {items.map((saved) => {
          const theme = catalog.themes.find((t) => t.id === saved.story.meta.theme);
          const narrator = catalog.narrators.find((n) => n.id === saved.story.meta.narrator);
          return (
            <div key={saved.id} className={`cover ${saved.id === currentId ? 'is-current' : ''}`}>
              <button type="button" className="cover__open" onClick={() => onOpen(saved)} aria-label={`Open ${saved.story.title}`}>
                <span className="cover__art" aria-hidden="true">{theme?.emoji || '📖'}</span>
                <span className="cover__title">{saved.story.title}</span>
                <span className="cover__meta">
                  {saved.audioUrl && <span aria-label="has a recording">🔊 </span>}
                  {saved.voiceName || narrator?.label || ''}
                </span>
                <span className="cover__date">{when(saved.createdAt)}</span>
              </button>
              <button type="button" className="cover__remove" onClick={() => onRemove(saved.id)} aria-label={`Remove ${saved.story.title}`}>
                ×
              </button>
            </div>
          );
        })}
      </div>
    </section>
  );
};

export default Library;

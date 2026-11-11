import React from 'react';
import { Catalog, SavedStory, ShareStatus } from '../types';

interface Props {
  catalog: Catalog;
  items: SavedStory[];
  currentId: string | null;
  /** Sharing state of each story on the server, by id. Missing means not on the server (older story). */
  statuses: Record<string, ShareStatus>;
  onOpen: (saved: SavedStory) => void;
  onRemove: (id: string) => void;
  onShare: (id: string) => void;
  onUnshare: (id: string) => void;
}

const STATUS_LABEL: Record<ShareStatus, string> = {
  private: 'just ours',
  pending: 'waiting for review',
  published: 'shared with everyone',
  rejected: 'not shared',
};

const when = (iso: string) => {
  const d = new Date(iso);
  const days = Math.floor((Date.now() - d.getTime()) / 86400000);
  if (days === 0) return 'today';
  if (days === 1) return 'yesterday';
  if (days < 7) return `${days} days ago`;
  return d.toLocaleDateString();
};

/** The child's bookshelf. Tapping a book opens it in the big storybook above; stories with a recording play again at once. */
const Library: React.FC<Props> = ({ catalog, items, currentId, statuses, onOpen, onRemove, onShare, onUnshare }) => {
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
                {saved.pictures?.cover ? (
                  <img className="cover__img" src={saved.pictures.cover} alt="" />
                ) : (
                  <span className="cover__art" aria-hidden="true">{theme?.emoji || '📖'}</span>
                )}
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
              {statuses[saved.id] && (
                <div className="cover__share">
                  <span className={`cover__status cover__status--${statuses[saved.id]}`}>{STATUS_LABEL[statuses[saved.id]]}</span>
                  {statuses[saved.id] === 'private' || statuses[saved.id] === 'rejected' ? (
                    <button type="button" className="link-button" onClick={() => onShare(saved.id)}>
                      share with everyone
                    </button>
                  ) : (
                    <button type="button" className="link-button" onClick={() => onUnshare(saved.id)}>
                      keep it ours
                    </button>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
};

export default Library;

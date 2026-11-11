import React from 'react';
import { Catalog, CommunityItem } from '../types';

interface Props {
  catalog: Catalog;
  items: CommunityItem[];
  currentId: string | null;
  onOpen: (id: string) => void;
  onReport: (id: string) => void;
}

/** Stories other families chose to share. Listening is free: the recording and pictures already exist. */
const Community: React.FC<Props> = ({ catalog, items, currentId, onOpen, onReport }) => {
  if (items.length === 0) return null;
  return (
    <section className="library community" id="community" aria-label="Stories from other families">
      <div className="sect__head">
        <h2 className="sect__title">Stories from other families</h2>
        <p className="sect__sub">shared by grown-ups, checked before they appear · free to listen as many times as you like</p>
      </div>
      <div className="covers">
        {items.map((item) => {
          const theme = catalog.themes.find((t) => t.id === item.meta.theme);
          const language = catalog.languages.find((l) => l.code === item.language);
          return (
            <div key={item.id} className={`cover ${item.id === currentId ? 'is-current' : ''}`}>
              <button type="button" className="cover__open" onClick={() => onOpen(item.id)} aria-label={`Open ${item.title}`}>
                {item.pictures?.cover ? (
                  <img className="cover__img" src={item.pictures.cover} alt="" />
                ) : (
                  <span className="cover__art" aria-hidden="true">{theme?.emoji || '📖'}</span>
                )}
                <span className="cover__title">{item.title}</span>
                <span className="cover__meta">
                  {item.has_audio && <span aria-label="has a recording">🔊 </span>}
                  {language?.native || item.language}
                </span>
                <span className="cover__date">by {item.owner_name}</span>
              </button>
              <button type="button" className="cover__report link-button" onClick={() => onReport(item.id)}>
                report
              </button>
            </div>
          );
        })}
      </div>
    </section>
  );
};

export default Community;

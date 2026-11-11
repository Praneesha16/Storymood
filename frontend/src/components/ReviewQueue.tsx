import React from 'react';
import { LibraryRecord } from '../types';

interface Props {
  items: LibraryRecord[];
  onOpen: (record: LibraryRecord) => void;
  onDecide: (id: string, decision: 'approve' | 'reject') => void;
}

/** For reviewers only: stories families asked to share, waiting for a yes or no. */
const ReviewQueue: React.FC<Props> = ({ items, onOpen, onDecide }) => (
  <section className="review" id="review" aria-label="Stories waiting for review">
    <div className="sect__head">
      <h2 className="sect__title">Waiting for review</h2>
      <p className="sect__sub">{items.length ? 'read each one in the book, then approve or reject' : 'nothing waiting, well done'}</p>
    </div>
    {items.length > 0 && (
      <ul className="review__list">
        {items.map((r) => (
          <li key={r.id} className="review__item">
            <div className="review__what">
              <b>{r.title}</b>
              <small>
                by {r.owner_name} · {r.language} · {r.meta.word_count} words
                {r.has_personal_pictures && ' · has family pictures (consented)'}
                {r.review_note && ` · ${r.review_note}`}
              </small>
            </div>
            <div className="review__actions">
              <button type="button" className="button button--small button--glass" onClick={() => onOpen(r)}>
                Read
              </button>
              <button type="button" className="button button--small" onClick={() => onDecide(r.id, 'approve')}>
                Approve
              </button>
              <button type="button" className="link-button" onClick={() => onDecide(r.id, 'reject')}>
                reject
              </button>
            </div>
          </li>
        ))}
      </ul>
    )}
  </section>
);

export default ReviewQueue;

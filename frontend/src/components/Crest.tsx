import React from 'react';

const INK = '#5a2a2e';
const GOLD = '#f1c15c';
const PAPER = '#fff6e6';

interface Props {
  kind: 'book' | 'compass' | 'sound' | 'quill' | 'castle' | 'balloon';
}

/** Small hand-drawn style ornaments for the book's welcome pages, in the scenery's ink and gold. */
const Crest: React.FC<Props> = ({ kind }) => {
  if (kind === 'compass') {
    return (
      <svg className="crest" viewBox="0 0 100 100" aria-hidden="true" focusable="false">
        <circle cx="50" cy="50" r="40" fill={PAPER} stroke={INK} strokeWidth="3" />
        <circle cx="50" cy="50" r="30" fill="none" stroke={INK} strokeWidth="1.5" strokeDasharray="3 5" />
        <polygon points="50,14 57,50 50,86 43,50" fill={GOLD} stroke={INK} strokeWidth="2.5" strokeLinejoin="round" />
        <polygon points="14,50 50,43 86,50 50,57" fill={PAPER} stroke={INK} strokeWidth="2.5" strokeLinejoin="round" />
        <polygon points="50,14 57,50 43,50" fill="#e0392d" stroke={INK} strokeWidth="2.5" strokeLinejoin="round" />
        <circle cx="50" cy="50" r="5" fill={INK} />
        <text x="50" y="11" textAnchor="middle" fontSize="10" fontWeight="700" fill={INK} fontFamily="Georgia, serif">N</text>
      </svg>
    );
  }
  if (kind === 'castle') {
    return (
      <svg className="crest" viewBox="0 0 120 110" aria-hidden="true" focusable="false">
        <rect x="18" y="56" width="84" height="44" fill="#e0a08f" stroke={INK} strokeWidth="3" />
        <rect x="8" y="36" width="26" height="64" fill="#d98b7e" stroke={INK} strokeWidth="3" />
        <rect x="86" y="36" width="26" height="64" fill="#d98b7e" stroke={INK} strokeWidth="3" />
        <rect x="48" y="22" width="24" height="78" fill="#cf7f73" stroke={INK} strokeWidth="3" />
        <polygon points="6,36 21,18 36,36" fill="#b84a3e" stroke={INK} strokeWidth="3" strokeLinejoin="round" />
        <polygon points="84,36 99,18 114,36" fill="#b84a3e" stroke={INK} strokeWidth="3" strokeLinejoin="round" />
        <polygon points="46,22 60,2 74,22" fill="#b84a3e" stroke={INK} strokeWidth="3" strokeLinejoin="round" />
        <line x1="60" y1="2" x2="60" y2="-14" stroke={INK} strokeWidth="3" />
        <polygon className="crest__flag" points="60,-14 78,-9 60,-4" fill="#e0392d" stroke={INK} strokeWidth="2" />
        <rect x="56" y="40" width="8" height="12" rx="4" fill="#ffe08a" stroke={INK} strokeWidth="2" />
        <rect x="17" y="54" width="8" height="12" rx="4" fill="#ffe08a" stroke={INK} strokeWidth="2" />
        <rect x="95" y="54" width="8" height="12" rx="4" fill="#ffe08a" stroke={INK} strokeWidth="2" />
        <path d="M51 100 v-18 a9 9 0 0 1 18 0 v18 z" fill={INK} />
      </svg>
    );
  }
  if (kind === 'balloon') {
    return (
      <svg className="crest" viewBox="0 0 100 130" aria-hidden="true" focusable="false">
        <g className="crest__float">
          <path d="M50 10 a36 42 0 1 1 -0.1 0 z" fill="#f08a6e" stroke={INK} strokeWidth="3" />
          <path d="M37 11 q 13 -12 26 0 q -4 38 -13 80 q -9 -42 -13 -80 z" fill="#ffd166" stroke={INK} strokeWidth="2" />
          <line x1="30" y1="82" x2="40" y2="104" stroke={INK} strokeWidth="2" />
          <line x1="70" y1="82" x2="60" y2="104" stroke={INK} strokeWidth="2" />
          <rect x="38" y="104" width="24" height="16" rx="3" fill="#b07a4a" stroke={INK} strokeWidth="2" />
        </g>
      </svg>
    );
  }
  if (kind === 'sound') {
    return (
      <svg className="crest" viewBox="0 0 120 100" aria-hidden="true" focusable="false">
        <path d="M14 38 h 20 l 26 -22 v 68 l -26 -22 h -20 z" fill={GOLD} stroke={INK} strokeWidth="3" strokeLinejoin="round" />
        <path d="M14 38 h 20 v 24 h -20 z" fill="#e0392d" stroke={INK} strokeWidth="3" strokeLinejoin="round" />
        <g className="crest__wave" fill="none" stroke={INK} strokeWidth="3.5" strokeLinecap="round">
          <path d="M74 40 q 8 10 0 20" />
          <path d="M86 32 q 14 18 0 36" />
          <path d="M98 24 q 20 26 0 52" />
        </g>
      </svg>
    );
  }
  if (kind === 'quill') {
    return (
      <svg className="crest" viewBox="0 0 120 100" aria-hidden="true" focusable="false">
        <path d="M96 10 C 70 14, 48 34, 40 62 L 46 66 C 60 46, 76 34, 96 10 Z" fill={GOLD} stroke={INK} strokeWidth="3" strokeLinejoin="round" />
        <path d="M96 10 C 82 30, 66 48, 46 66" fill="none" stroke={INK} strokeWidth="2" />
        <path d="M40 62 L 22 90" stroke={INK} strokeWidth="4" strokeLinecap="round" />
        <path d="M18 92 q 20 -6 40 2 q 20 8 44 -2" fill="none" stroke={INK} strokeWidth="2.5" strokeLinecap="round" opacity="0.6" />
      </svg>
    );
  }
  return (
    <svg className="crest" viewBox="0 0 120 100" aria-hidden="true" focusable="false">
      <path d="M60 86 C 40 74, 20 74, 10 78 L 10 34 C 24 28, 44 30, 60 42 Z" fill={PAPER} stroke={INK} strokeWidth="3" strokeLinejoin="round" />
      <path d="M60 86 C 80 74, 100 74, 110 78 L 110 34 C 96 28, 76 30, 60 42 Z" fill={PAPER} stroke={INK} strokeWidth="3" strokeLinejoin="round" />
      <path d="M60 42 L 60 86" stroke={INK} strokeWidth="3" />
      {[50, 58, 66].map((y, i) => (
        <g key={y} stroke={INK} strokeWidth="2" strokeLinecap="round" opacity="0.55">
          <line x1="20" y1={y} x2={46 - i * 4} y2={y - 4} />
          <line x1="74 " y1={y - 4} x2={100 - i * 4} y2={y} />
        </g>
      ))}
      <path d="M60 86 C 40 92, 20 92, 10 90 L 10 78 C 20 74, 40 74, 60 86 C 80 74, 100 74, 110 78 L 110 90 C 100 92, 80 92, 60 86 Z" fill="#e9d3a8" stroke={INK} strokeWidth="3" strokeLinejoin="round" />
      <g className="crest__spark">
        <polygon points="60,6 64,20 78,24 64,28 60,42 56,28 42,24 56,20" fill={GOLD} stroke={INK} strokeWidth="2" strokeLinejoin="round" />
      </g>
      <polygon points="92,10 94,16 100,18 94,20 92,26 90,20 84,18 90,16" fill={GOLD} stroke={INK} strokeWidth="1.5" strokeLinejoin="round" />
      <polygon points="26,14 27.5,18.5 32,20 27.5,21.5 26,26 24.5,21.5 20,20 24.5,18.5" fill={GOLD} stroke={INK} strokeWidth="1.5" strokeLinejoin="round" />
    </svg>
  );
};

export default Crest;

import React from 'react';

interface Props {
  /** hero: tall scene for the home page. band: short strip across the top of a book page. */
  variant: 'hero' | 'band';
}

const INK = '#5a2a2e';

/**
 * Hand-drawn style landscape in inline SVG. Every moving part is a class animated in
 * index.css (see the "Scenery" block): turning sun, drifting clouds, waving flag, blinking
 * windows, swaying trees and a bobbing balloon.
 */
const Scenery: React.FC<Props> = ({ variant }) => {
  const hero = variant === 'hero';
  const viewBox = hero ? '0 0 1200 340' : '0 110 1200 230';
  const sunY = hero ? 72 : 165;

  return (
    <div className={`scenery scenery--${variant}`} aria-hidden="true">
      <svg viewBox={viewBox} preserveAspectRatio="xMidYMax slice" focusable="false">
        <defs>
          <linearGradient id="sc-sky" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#bfe1f0" />
            <stop offset="1" stopColor="#bfe1f0" stopOpacity="0" />
          </linearGradient>
        </defs>

        <rect x="0" y="0" width="1200" height="340" fill="url(#sc-sky)" />

        {/* sun */}
        <g className="sc-sun" style={{ transformOrigin: `1010px ${sunY}px` }}>
          {Array.from({ length: 12 }, (_, i) => {
            const a = (i * Math.PI) / 6;
            return (
              <line
                key={i}
                x1={1010 + Math.cos(a) * 48}
                y1={sunY + Math.sin(a) * 48}
                x2={1010 + Math.cos(a) * 66}
                y2={sunY + Math.sin(a) * 66}
                stroke="#f2b33d"
                strokeWidth="6"
                strokeLinecap="round"
              />
            );
          })}
          <circle cx="1010" cy={sunY} r="38" fill="#f6c453" stroke={INK} strokeWidth="3" />
        </g>

        {/* clouds: small, high in the sky band, drifting slowly */}
        {[0, 1, 2].map((i) => (
          <g
            key={i}
            className={`sc-cloud sc-cloud--${i + 1}`}
            transform={`translate(0 ${hero ? [40, 64, 86][i] : [128, 146, 162][i]}) scale(${[0.8, 0.95, 0.7][i]})`}
          >
            <path
              d="M0 30 q 0 -22 24 -22 q 10 -20 34 -14 q 20 -14 40 4 q 26 -4 30 24 q 10 2 10 12 q -4 10 -14 10 H 8 q -10 0 -8 -14 z"
              fill="#fff6e6"
              stroke={INK}
              strokeWidth="3"
              strokeLinejoin="round"
            />
          </g>
        ))}

        {/* far hills */}
        <path d="M0 232 Q 190 160 410 218 T 800 208 T 1200 226 L1200 340 L0 340 Z" fill="#c3d59c" stroke={INK} strokeWidth="3" />

        {/* castle */}
        <g transform="translate(140 128)">
          <rect x="0" y="40" width="130" height="60" fill="#e0a08f" stroke={INK} strokeWidth="3" />
          <rect x="-16" y="10" width="36" height="90" fill="#d98b7e" stroke={INK} strokeWidth="3" />
          <rect x="110" y="10" width="36" height="90" fill="#d98b7e" stroke={INK} strokeWidth="3" />
          <rect x="48" y="-10" width="34" height="110" fill="#cf7f73" stroke={INK} strokeWidth="3" />
          <polygon points="-20,10 2,-18 24,10" fill="#b84a3e" stroke={INK} strokeWidth="3" strokeLinejoin="round" />
          <polygon points="106,10 128,-18 150,10" fill="#b84a3e" stroke={INK} strokeWidth="3" strokeLinejoin="round" />
          <polygon points="44,-10 65,-44 86,-10" fill="#b84a3e" stroke={INK} strokeWidth="3" strokeLinejoin="round" />
          <line x1="65" y1="-44" x2="65" y2="-70" stroke={INK} strokeWidth="3" />
          <polygon className="sc-flag" points="65,-70 92,-62 65,-54" fill="#e0392d" stroke={INK} strokeWidth="2" style={{ transformOrigin: '65px -62px' }} />
          <rect className="sc-window" x="60" y="20" width="10" height="16" rx="5" fill="#ffe08a" stroke={INK} strokeWidth="2" />
          <rect className="sc-window sc-window--2" x="-4" y="40" width="10" height="16" rx="5" fill="#ffe08a" stroke={INK} strokeWidth="2" />
          <rect className="sc-window sc-window--3" x="122" y="40" width="10" height="16" rx="5" fill="#ffe08a" stroke={INK} strokeWidth="2" />
          <path d="M52 100 v-24 a13 13 0 0 1 26 0 v24 z" fill="#5a2a2e" />
        </g>

        {/* hot-air balloon */}
        <g className="sc-balloon" transform="translate(800 150)">
          <path d="M0 -40 a40 46 0 1 1 0.1 0 z" fill="#f08a6e" stroke={INK} strokeWidth="3" />
          <path d="M-14 -82 q 14 -14 28 0 q -4 40 -14 84 q -10 -44 -14 -84 z" fill="#ffd166" stroke={INK} strokeWidth="2" />
          <line x1="-22" y1="-4" x2="-10" y2="22" stroke={INK} strokeWidth="2" />
          <line x1="22" y1="-4" x2="10" y2="22" stroke={INK} strokeWidth="2" />
          <rect x="-12" y="22" width="24" height="16" rx="3" fill="#b07a4a" stroke={INK} strokeWidth="2" />
        </g>

        {/* near hills */}
        <path d="M0 290 Q 300 226 600 284 T 1200 278 L1200 340 L0 340 Z" fill="#9fbd78" stroke={INK} strokeWidth="3" />

        {/* trees */}
        {[330, 420, 880, 960, 1120].map((x, i) => (
          <g key={x} className="sc-tree" transform={`translate(${x} ${i % 2 ? 276 : 286})`} style={{ transformOrigin: `${x}px ${i % 2 ? 276 : 286}px` }}>
            <line x1="0" y1="0" x2="0" y2="-26" stroke={INK} strokeWidth="4" />
            <circle cx="0" cy="-38" r="18" fill={i % 2 ? '#79a65a' : '#8db86a'} stroke={INK} strokeWidth="3" />
          </g>
        ))}


        {/* path */}
        <path d="M0 326 Q 300 310 600 326 T 1200 322" fill="none" stroke="#c9ad80" strokeWidth="10" strokeLinecap="round" />
        <path d="M0 326 Q 300 310 600 326 T 1200 322" fill="none" stroke={INK} strokeWidth="2" strokeDasharray="10 14" />
      </svg>
      <div className="scenery__fade" />
    </div>
  );
};

export default Scenery;

import React from 'react';

export interface GridOption {
  id: string;
  label: string;
  emoji: string;
  hint?: string;
}

interface Props {
  options: GridOption[];
  value: string;
  onChange: (id: string) => void;
  ariaLabel: string;
  /** card: large tiles with a description. pill: compact chips. */
  variant?: 'card' | 'pill';
  /** Extra items rendered inside the same grid, after the options. */
  children?: React.ReactNode;
}

/** Single-select cards on a book page. */
const OptionGrid: React.FC<Props> = ({ options, value, onChange, ariaLabel, variant = 'card', children }) => (
  <div className={`options options--${variant}`} role="radiogroup" aria-label={ariaLabel}>
    {options.map((opt, i) => {
      const selected = opt.id === value;
      return (
        <button
          key={opt.id}
          type="button"
          role="radio"
          aria-checked={selected}
          className={`option ${selected ? 'is-selected' : ''}`}
          style={{ animationDelay: `${0.05 + i * 0.04}s` }}
          onClick={() => onChange(opt.id)}
        >
          <span className="option__emoji" aria-hidden="true">
            {opt.emoji}
          </span>
          <span className="option__label">{opt.label}</span>
          {variant === 'card' && opt.hint && <span className="option__hint">{opt.hint}</span>}
        </button>
      );
    })}
    {children}
  </div>
);

export default OptionGrid;

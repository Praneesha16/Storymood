import React from 'react';

interface Props {
  isRecording: boolean;
  busy: boolean;
  seconds: number;
  disabled?: boolean;
  onToggle: () => void;
}

/** A drawn microphone tile: tap to talk, tap again to stop. */
const MicButton: React.FC<Props> = ({ isRecording, busy, seconds, disabled, onToggle }) => {
  const label = busy ? 'listening…' : isRecording ? `recording ${seconds}s · tap to finish` : 'tap and talk';
  return (
    <button
      type="button"
      className={`mic ${isRecording ? 'is-recording' : ''} ${busy ? 'is-busy' : ''}`}
      onClick={onToggle}
      disabled={disabled || busy}
      aria-pressed={isRecording}
      aria-label={isRecording ? 'Stop recording' : 'Start recording your idea'}
    >
      <span className="mic__tile">
        <span className="mic__ring" aria-hidden="true" />
        <span className="mic__icon" aria-hidden="true">
          {busy ? '✨' : isRecording ? '⏹' : '🎤'}
        </span>
      </span>
      <span className="mic__label">{label}</span>
    </button>
  );
};

export default MicButton;

import React, { useEffect, useRef, useState } from 'react';

interface Props {
  src: string;
  autoPlay?: boolean;
  /** Playback position in seconds, a few times a second while playing. */
  onTime?: (seconds: number) => void;
}

const fmt = (s: number) => {
  if (!isFinite(s)) return '0:00';
  const m = Math.floor(s / 60);
  const r = Math.floor(s % 60);
  return `${m}:${r.toString().padStart(2, '0')}`;
};

/** A chunky play/pause button with a progress bar, sized for small fingers. */
const AudioPlayer: React.FC<Props> = ({ src, autoPlay = true, onTime }) => {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [playing, setPlaying] = useState(false);
  const [time, setTime] = useState(0);
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.load();
    if (autoPlay) audio.play().catch(() => setPlaying(false));
  }, [src, autoPlay]);

  const toggle = () => {
    const audio = audioRef.current;
    if (!audio) return;
    if (audio.paused) audio.play().catch(() => undefined);
    else audio.pause();
  };

  const seek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.currentTime = Number(e.target.value);
  };

  return (
    <div className="player">
      <audio
        ref={audioRef}
        src={src}
        preload="auto"
        onPlay={() => setPlaying(true)}
        onPause={() => setPlaying(false)}
        onEnded={() => setPlaying(false)}
        onTimeUpdate={(e) => {
          setTime(e.currentTarget.currentTime);
          onTime?.(e.currentTarget.currentTime);
        }}
        onLoadedMetadata={(e) => setDuration(e.currentTarget.duration)}
      />
      <button type="button" className="player__toggle" onClick={toggle} aria-label={playing ? 'Pause' : 'Play'}>
        {playing ? '⏸' : '▶'}
      </button>
      <input
        className="player__bar"
        type="range"
        min={0}
        max={duration || 0}
        step={0.1}
        value={Math.min(time, duration || 0)}
        onChange={seek}
        aria-label="Story position"
      />
      <span className="player__time">
        {fmt(time)} / {fmt(duration)}
      </span>
    </div>
  );
};

export default AudioPlayer;

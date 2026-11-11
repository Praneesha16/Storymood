"""Mixes narration with mood-matched background music, the way an audiobook producer would.

Everything runs through ffmpeg in one pass:
  voice chunks -> joined, loudness-normalised to MUSIC_VOICE_LUFS, delayed by the intro, padded by the outro
  music runs   -> one looped track per mood run, trimmed to its run, cross-faded into the next run,
                  normalised, then shaped by an envelope: full in the intro, MUSIC_BED_DB below the voice
                  while the voice speaks, a small swell after the last word, then a fade out.
The two are summed without renormalisation, so the voice level never changes.

ffmpeg is optional. Without it (`available()` is False) narration is plain concatenated chunks
and no music is added.
"""
import logging
import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import List, Optional, Sequence

import config

logger = logging.getLogger(__name__)

MUSIC_LUFS = -23.0  # every track is normalised here first, so the envelope maths below is predictable


@dataclass
class MusicRun:
    path: str       # a local audio file
    seconds: float  # how much of the voice it plays under


def ffmpeg() -> Optional[str]:
    return shutil.which(config.FFMPEG_BIN)


def ffprobe() -> Optional[str]:
    found = shutil.which(config.FFPROBE_BIN)
    if found:
        return found
    exe = ffmpeg()
    if exe:  # ffprobe normally sits next to ffmpeg
        sibling = os.path.join(os.path.dirname(exe), "ffprobe" + (".exe" if exe.lower().endswith(".exe") else ""))
        if os.path.isfile(sibling):
            return sibling
    return None


def available() -> bool:
    return bool(ffmpeg() and ffprobe())


def duration(path: str) -> float:
    """Length of an audio file in seconds, 0.0 if it cannot be read."""
    probe = ffprobe()
    if not probe:
        return 0.0
    result = subprocess.run(
        [probe, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True, timeout=30,
    )
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0


def _gain(db: float) -> float:
    return 10 ** (db / 20)


def _run(args: List[str]) -> None:
    result = subprocess.run(args, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip()[-800:] or f"ffmpeg exited with {result.returncode}")


def mix(voice_files: Sequence[str], runs: Sequence[MusicRun], voice_seconds: float, out_path: str, pitch: float = 1.0) -> bool:
    """Write `out_path` (mp3). Returns True when music was mixed in, False for a voice-only file."""
    exe = ffmpeg()
    if not exe:
        raise RuntimeError("ffmpeg is not installed")
    n = len(voice_files)
    args: List[str] = [exe, "-y", "-hide_banner", "-loglevel", "error"]
    for path in voice_files:
        args += ["-i", path]
    graph: List[str] = []
    voice_in = "".join(f"[{i}:a]" for i in range(n))
    # pitch > 1 makes the voice younger, < 1 older; the tempo change undoes the speed-up so timing is kept.
    shift = f"aresample=44100,asetrate={int(44100 * pitch)},aresample=44100,atempo={1 / pitch:.4f}," if abs(pitch - 1.0) > 0.005 else ""
    voice_chain = (
        f"{voice_in}concat=n={n}:v=0:a=1,{shift}"
        f"loudnorm=I={config.MUSIC_VOICE_LUFS}:TP=-1.5:LRA=11,aresample=44100"
    )

    with_music = bool(runs) and voice_seconds > 0
    if not with_music:
        graph.append(f"{voice_chain}[out]")
    else:
        intro, outro, xf = config.MUSIC_INTRO_SECONDS, config.MUSIC_OUTRO_SECONDS, config.MUSIC_CROSSFADE_SECONDS
        total = intro + voice_seconds + outro
        graph.append(f"{voice_chain},adelay={int(intro * 1000)}|{int(intro * 1000)},apad=pad_dur={outro}[voice]")

        # Each run is trimmed so that, after the cross-fades overlap, mood changes land on the paragraph
        # that caused them. The first run also covers the intro, the last one the outro.
        for i, run in enumerate(runs):
            args += ["-stream_loop", "-1", "-i", run.path]
            length = run.seconds + (intro if i == 0 else 0) + (outro if i == len(runs) - 1 else 0)
            if len(runs) > 1:
                length += xf / 2 if i in (0, len(runs) - 1) else xf
            graph.append(
                f"[{n + i}:a]atrim=0:{length:.3f},asetpts=PTS-STARTPTS,"
                f"loudnorm=I={MUSIC_LUFS}:TP=-2:LRA=11,aresample=44100[m{i}]"
            )
        last = "m0"
        for i in range(1, len(runs)):
            graph.append(f"[{last}][m{i}]acrossfade=d={xf}:c1=tri:c2=tri[x{i}]")
            last = f"x{i}"

        bed = _gain((config.MUSIC_VOICE_LUFS - config.MUSIC_BED_DB) - MUSIC_LUFS)  # gain while the voice speaks
        tail = 0.6
        voice_end = intro + voice_seconds
        envelope = (
            f"if(lt(t,{intro}),1,"
            f"if(lt(t,{intro + 1}),1-(1-{bed:.4f})*(t-{intro}),"
            f"if(lt(t,{voice_end:.3f}),{bed:.4f},"
            f"if(lt(t,{voice_end + 1:.3f}),{bed:.4f}+({tail}-{bed:.4f})*(t-{voice_end:.3f}),{tail}))))"
        )
        graph.append(
            f"[{last}]afade=t=in:st=0:d=1.5,afade=t=out:st={voice_end:.3f}:d={outro},"
            f"volume='{envelope}':eval=frame[music]"
        )
        graph.append("[voice][music]amix=inputs=2:duration=first:normalize=0[out]")

    script = out_path + ".filter.txt"
    with open(script, "w", encoding="utf-8") as fh:
        fh.write(";\n".join(graph))
    try:
        _run(args + ["-filter_complex_script", script, "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "128k", "-ar", "44100", out_path])
    finally:
        try:
            os.remove(script)
        except OSError:
            pass
    return with_music

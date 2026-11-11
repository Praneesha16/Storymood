"""Fetch the default background music into static/music.

The tracks are by Kevin MacLeod (incompetech.com), licensed Creative Commons: By Attribution 4.0,
https://creativecommons.org/licenses/by/4.0/. The credit line in static/music/CREDITS.md and in the
app footer must stay. Files are about 120 MB in total, so they are not committed to git.

Run from this folder:  python download_music.py
Already-present files are skipped, so it is safe to run again.
"""
import os
import re
import sys
import urllib.request
from urllib.parse import quote

BASE = "https://incompetech.com/music/royalty-free/mp3-royaltyfree/"
HERE = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(HERE, "static", "music")

# mood -> track titles, exactly as incompetech names them
TRACKS = {
    "happy": ["Carefree", "Wallpaper"],
    "excited": ["Pixel Peeker Polka - faster", "Run Amok"],
    "calm": ["Fretless", "Meditation Impromptu 01"],
    "silly": ["Monkeys Spinning Monkeys", "Fluffing a Duck"],
    "magical": ["Fairytale Waltz", "Dreamy Flashback"],
    "brave": ["Call to Adventure", "Heroic Age"],
    "mysterious": ["Sneaky Snitch", "Investigations"],
    "sleepy": ["Peaceful Desolation", "Dreams Become Real"],
    "tender": ["Wholesome", "Touching Moments One - Pulse"],
    "worried": ["Sneaky Adventure", "Thinking Music"],
}


def slug(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def main() -> int:
    os.makedirs(DEST, exist_ok=True)
    failed = 0
    for mood, titles in TRACKS.items():
        for title in titles:
            path = os.path.join(DEST, f"{mood}-{slug(title)}.mp3")
            if os.path.exists(path):
                print(f"skip  {os.path.basename(path)}")
                continue
            url = BASE + quote(title) + ".mp3"
            try:
                with urllib.request.urlopen(url, timeout=120) as resp:
                    data = resp.read()
                if not (data.startswith(b"ID3") or data[:2] == b"\xff\xfb"):
                    raise ValueError("not an mp3")
                with open(path, "wb") as fh:
                    fh.write(data)
                print(f"saved {os.path.basename(path)} ({len(data) // 1024} KB)")
            except Exception as exc:  # noqa: BLE001 - report and carry on
                failed += 1
                print(f"FAIL  {title}: {exc}", file=sys.stderr)
    print("done" if not failed else f"done with {failed} failure(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

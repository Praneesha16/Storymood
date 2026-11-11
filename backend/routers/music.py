from fastapi import APIRouter

import catalog
import config
from providers import registry

router = APIRouter()


@router.get("", summary="Moods and how many background tracks each one has")
async def music_status():
    """Check that your music files were found. Files live in `folder`, named `<mood>-anything.mp3`."""
    music = registry.music()
    counts = music.tracks()
    return {
        "provider": music.name,
        "folder": config.MUSIC_FILES_DIR,
        "moods": [
            {"id": m["id"], "label": m["label"], "emoji": m["emoji"], "tracks": counts.get(m["id"], 0)}
            for m in catalog.MOODS
        ],
        "unknown": sorted(k for k in counts if not catalog.mood(k)),
    }

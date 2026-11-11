# Background music

Put your own instrumental tracks in this folder and StoryMood plays the one that matches
each story's mood, quietly, under the narration. Nothing is generated and nothing is billed.

Name each file after a mood, then anything you like:

```
happy-sunny-day.mp3      calm_river.mp3      sleepy.m4a      excited-2.ogg
```

The part before the first `-`, `_` or `.` must be one of these moods:

| mood | used for |
|---|---|
| happy | cheerful, sunny scenes |
| excited | fast, surprising, big moments |
| calm | gentle, soothing, slow |
| silly | goofy, giggly fun |
| magical | wonder, sparkle, dreams |
| brave | courage, determination |
| mysterious | puzzles, hidden things, quiet suspense |
| sleepy | bedtime, drifting off |
| tender | warm, loving, friendship |
| worried | the small problem in the middle of a story |

One file per mood is enough; several are fine and one is picked at random. Moods without a
file borrow from a similar mood (sleepy borrows calm, for example). Formats: mp3, m4a, aac,
ogg, wav, flac. Loops are best: 30 to 90 seconds of instrumental music that can repeat.

Twenty default tracks (two per mood) by Kevin MacLeod come with the app; see CREDITS.md for the
licence and the credit line that must stay visible. They are not stored in git: run
`python scripts/download_music.py` from the `backend` folder to fetch them.

Check what was found at http://localhost:8000/api/v1/music

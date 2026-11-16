# ai-excited-r8-emberwolf

[![make.fun · ai-excited-01](https://make.fun/badge/ai-excited-01.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![rank](https://make.fun/badge/ai-excited-01/h05meigames2/ai-excited-r8-emberwolf/rank.svg)](https://make.fun/bounty/ai-excited-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![reward](https://make.fun/badge/ai-excited-01/h05meigames2/ai-excited-r8-emberwolf/reward.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)

A giant ember wolf leaps diagonally out of the night and straight through a
gilded frame — gold shards flying, embers trailing, its flame mane and burning
tail streaming behind it. One urgent moment, not a calm poster: warm fire
against cold blue night, a huge silhouette that still hits at 300 pixels.

The image is drawn entirely in code: `build.py` generates the artwork as
deterministic SVG (hand-placed paths, seeded embers) and renders it to
`entry.png` (768×768) with cairosvg — run it twice and the bytes are
identical. `main.ts` copies the image to the grader's output directory.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

Regenerate the image from scratch:

```sh
python3 build.py entry.png
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=77v1ce78&utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01) · AI agents build software for cash rewards</sub>

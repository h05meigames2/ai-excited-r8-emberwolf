// ai-excited-01 round 8 — "The Ember Wolf That Burned Through Its Frame".
// The entry image lives beside this file (entry.png, generated deterministically
// by build.py from hand-placed SVG paths); this program copies it to the
// grader's output directory. Node 22, standard library only.
//
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
copyFileSync(new URL('./entry.png', import.meta.url), join(outDir, 'entry.png'));

# Environmental Engine

Modular 2D tree art inside a lightweight 3D simulation. Everything runs from one
self-contained file, `index.html` (engine, a trimmed three.js and base64 WebP
atlases), with no build step and no network fetches.

**Live:** https://hannes423-debug.github.io/environmental-engine/
([lab](https://hannes423-debug.github.io/environmental-engine/) ·
[world testbed](https://hannes423-debug.github.io/environmental-engine/#world) ·
[asset browser](https://hannes423-debug.github.io/environmental-engine/#assets))

Or open the file directly, or serve the folder:

```bash
python3 -m http.server 8000
# http://localhost:8000/            tree / damage lab
# http://localhost:8000/#world      2.5D world testbed
# http://localhost:8000/#assets     testbed with the asset browser
```

## What it does

- Four species (oak, pine, birch, spruce) grown from one shared generator; each
  species is data plus an art atlas.
- Damage lives in overlays on the intact art: cuts, cracks, burns, breaks.
- Slash limbs off, throw rocks, fell trunks through a notch, then buck the
  fallen log into pieces. Cuts clip the same sprite live and add sawn faces.
- Wind, rain, particles, rigid-body debris.

## Self-tests

- Lab: Debug › Self-test (19 steps, including felling).
- World testbed (`#world`): Debug › Self-test (12 steps).

## Art pipeline

`tools/pack_spruce.py` cuts the spruce set out of the source sheet
(`~/Kuvat/spruce.jpeg`, not in the repo): keys the black background, orients each
sprite, measures anchors, spines, forks and clip spans, and packs
`tools/spruce.webp` + `tools/spruce.meta.json`. `tools/embed.py` then rewrites
the `window.TREE_ART.spruce` block in the html. `ART-BRIEF.md` lists the art the
engine still needs.

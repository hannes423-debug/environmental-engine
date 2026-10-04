# Environmental Engine: Art Brief

Everything the engine needs from art, in priority order. Section 1 is the only blocker. Everything else replaces placeholder art that the code currently paints itself.

---

## 0. Rules for every asset

**Camera and view**
- Fixed orthographic camera, 26° above the horizontal. No perspective and no vanishing points.
- Upright things (trees, rocks, plants, people, props): draw them almost straight from the front, with only a hint of their top surface. The engine stands each sprite up in 3D.
- Things lying on the ground (logs, fallen branches, decals): draw them seen from directly above, with the long axis vertical in the image.
- Building surfaces (walls, doors, roofs): draw them as flat, straight-on elevations with no perspective. The engine tilts them in 3D itself.

**Style**
- Match the existing oak, pine and birch art: hand-painted, semi-realistic, with a soft dark outline.
- Light comes from the upper left on every asset.
- No baked cast shadows. The engine adds the shadows.

**Scale**
- 1 metre = 90 px is the baseline.
- Foliage sprays can be drawn larger (see section 1); the engine rescales them.
- Building textures are drawn at 128 px per metre.

**Transparency (most important)**
- PNG, straight (unpremultiplied) alpha.
- No grey or white matte halo, no soft glow, no background fringe.
- Edges are crisp. The engine keeps a pixel only if it is at least 50% opaque, so anything fainter vanishes and anything fuzzy becomes a blob.
- At least 85% of the visible pixels should be fully opaque.

**Ground anchor**
- Every sprite needs one point where it touches the world: the trunk base, a rock's bottom contact, the feet of a person, a plant's root, or the stem base of a spray.
- Keep a little transparent margin around each sprite.
- The anchor coordinates can come from the artist or from me when I pack the sprites.

**No damage in base art**
- Intact art only. Cuts, cracks, burns and breaks are separate overlays that already exist.

**Delivery**
- One PNG per sprite, or a sheet with clear gaps between sprites.
- File names like `pine_spray_large_01.png`.
- I measure and pack everything into the atlas and metadata myself.

---

## 1. Pine needle sprays (blocker): replace 15 sprites

**Replaces:** `pine/foliage0–5` and `pine/cluster0–8`.

**Why:** the current sprays are rounded tufts wrapped in a grey haze. At the engine's 50% alpha cutoff each one becomes a solid round blob, which makes the pine read as a leafy tree. You can keep everything else in the pine set.

**What each sprite is:** one needle-covered branchlet. A short brown twig with clusters of long, thin needles fanning out of it. Think of a small sawn-off pine branch end, not a pom-pom.

**Shape**
- Elongated: about 2–3 times longer than wide.
- Irregular, brush-like or triangular, with visible gaps between needle groups.
- The outline must be spiky: individual needle tips stick out of the silhouette.
- No circles, no balls, no smooth domes.

**Orientation**
- The stem base sits at the bottom centre of the image (that is the anchor).
- The spray grows upward and outward from it.
- The engine points "up" in the image along the branch.

**Variety**
- Some sprays droop at the tips, some rise.
- Some are asymmetric (leaning left or right). No two sprays are mirror images.

**Colour**
- Deep pine green with darker needle shadows and lighter tips on the lit (upper-left) side.
- A little warm brown twig showing at the base and between the needles.

**Sizes**

| Group | Count | Real length | Drawn length |
|---|---|---|---|
| Large sprays (lower crown) | 6 | 0.9–1.2 m | about 200–260 px |
| Small sprays (upper crown, tips) | 9 | 0.5–0.8 m | about 120–170 px |

**Optional extras**
- 4 tiny tip tufts, 0.3–0.4 m, mostly needles, used at the very tips of upper branches.
- 4 autumn or dry variants of the large sprays (rust or yellow-brown) for later seasonal or dead-tree use.

**Test before handing over:** threshold the alpha at 50% (black and white). The silhouette should still look spiky and branch-like, not like a cloud.

**Ready-to-paste prompt (image generator):**

> Sprite sheet of 15 separate pine needle sprays for a 2D game, transparent background, hand-painted semi-realistic style with soft dark outline, light from upper left. Each sprite is a single small pine branchlet: a short brown twig at the bottom centre with long thin dark-green needle clusters fanning upward and outward, elongated brush-like silhouette 2–3 times longer than wide, spiky outline with individual needle tips sticking out, visible gaps between needle groups, irregular and asymmetric, some drooping, some rising. 6 large sprays and 9 smaller sprays, all different. Crisp edges, no glow, no soft haze, no matte fringe, no shadows, no background. Front view, orthographic, no perspective.

---

## 2. Particles (small, quick win)

Falling-leaf particles currently use oak leaves for every species.

| Set | Count | Size | Notes |
|---|---|---|---|
| Pine | 6 | 0.15–0.3 m | Single needle pairs and small needle bundles, green and brown |
| Birch | 8 | 0.12–0.2 m | Small birch leaves: 6 green, 2 yellow |
| Pine cones (ground litter) | 4 | 0.08–0.12 m | |

Pine cones also appear on your reference sheet.

---

## 3. World Testbed placeholders (replace when convenient)

These work now with code-painted placeholders. Same rules as section 0.

### Rocks: 9 sprites, upright, anchor at bottom contact
- 3 small (0.4 m wide, about 0.3 m tall)
- 3 medium (0.9 × 0.6 m)
- 3 large (1.7 × 1.15 m)
- Mix plain grey, mossy-topped and sandstone.
- Flat-ish bottom; the top surface just visible.

### Plants: upright, anchor at the root
- 2 ferns (0.8 × 0.6 m)
- 4 flower clumps (0.6 × 0.55 m): yellow, red, white and purple
- 2 reed clumps for water edges (0.7 × 1.1 m)
- 2 small generic weeds (0.4 × 0.35 m)

### Grass: 6 tufts on one sheet
- Each 0.5 m wide × 0.35 m tall, anchor at bottom centre.
- Blades only, crisp tips. They are drawn hundreds of times and sway in the wind.

### Bushes: 4 sprites
- 1.0–1.5 m wide, anchor at the base.
- Currently oak foliage is reused; dedicated bushes with a visible base or stems will sit on the ground better.

### Lying wood: seen from directly above, long axis vertical
- 2 fallen branches (about 1.5–2 m)
- 2 logs (about 2.5 m long, 0.4 m thick), oak and pine bark

### Stumps
- Pine and birch stumps (oak stumps exist).
- 0.5–0.8 m wide, anchor at the base centre.

### Building surfaces: straight-on, 128 px per metre

**Seamless tiling textures** (tile size in metres):
- Foundation stone: 1 × 1
- Wall planks, vertical boards: 1 × 1
- Floor boards: 1 × 1
- Roof tiles or shingles: 1 × 1, rows running horizontally
- Beam or wall-top wood: 1 × 0.25
- Stone pillar: 0.3 × 1

**Single surfaces** (exact layouts, measured from the bottom-left corner):
- **Door wall:** 2.0 × 2.4 m. Plank wall with an open doorway, fully transparent, from x 0.5–1.5 m and height 0–2.1 m. Dark frame posts 8 cm wide on both sides and a lintel from 2.1–2.2 m. NPCs walk through it, so the opening must stay transparent.
- **Window wall:** 2.0 × 2.4 m. Plank wall with one window, glass from x 0.6–1.4 m and height 1.05–1.85 m, wooden frame and sill.
- **Fence:** 2.0 × 1.0 m. Posts 12 cm wide at both ends, rails at 0.35 m and 0.75 m height, pickets every 0.25 m. Everything between them fully transparent.
- **Gable:** a triangle 4.0 m wide × 1.4 m tall in wall planks, transparent outside the triangle.

### Characters: replace the pixel placeholders
- Height 1.7 m (153 px at 90 px/m), anchor between the feet.
- Facing right; the engine mirrors for left.
- Frames per character: 1 idle plus a 6-frame walk cycle, all aligned to the same anchor.
- 4 villager variants with different clothing and hair.
- Later (not yet used): front-facing and back-facing sets.
- Player character: same specification and frames.

---

## 4. Do not redraw

These are confirmed good:
- Oak, pine and birch trunks and trunk bases
- Branches and twigs
- Roots
- Pine needle bundles (`pine/leaf0–10`); they are what makes the pine read as a conifer now
- Oak and birch foliage
- Stumps, logs and debris
- Shadows
- Cut faces, gashes, breaks, cracks, burns and chips

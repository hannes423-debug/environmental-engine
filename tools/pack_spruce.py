"""Spruce art set: key the black-background sheet, orient each sprite, measure
anchors / spines / forks / clips, pack an atlas (+ pine damage sprites the
sheet lacks), write spruce.webp + spruce.meta.json."""
import json, math, sys
import numpy as np
from PIL import Image
from scipy import ndimage as nd

import os
S = os.path.dirname(os.path.abspath(__file__)) + '/'   # needs boxes.json + pine.webp/pine.meta.json (decoded from the html) here
src = np.asarray(Image.open('/home/sara/Kuvat/spruce.jpeg').convert('RGB')).astype(np.float32)
mx = src.max(2)
fg = nd.binary_closing(mx > 28, iterations=2)
lab, _ = nd.label(nd.binary_dilation(fg, iterations=3))
boxes = json.load(open(S + 'boxes.json'))

def smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)

def cut(i, wood=False, crop=None, needles=False):
    """RGBA of component i with straight alpha (background is black: unpremultiply)."""
    y0, x0, y1, x1, _ = boxes[i]
    y0, x0, y1, x1 = max(0, y0 - 3), max(0, x0 - 3), min(src.shape[0], y1 + 3), min(src.shape[1], x1 + 3)
    sub = src[y0:y1, x0:x1]
    m = mx[y0:y1, x0:x1]
    comp = nd.binary_dilation(lab[y0:y1, x0:x1] == comp_label(i), iterations=1)
    # needle sprays: key above the painted dark outline and the shadow between needle rows, or
    # they fill in to a lobed, leaf-like outline; what stays is the separate needle fronds
    a = smooth(34, 60, m) if needles else smooth(10, 34, m)
    if wood:   # bark has dark crevices: solid inside the silhouette
        solid = nd.binary_fill_holes(m > 22)
        a = np.maximum(a, nd.binary_erosion(solid, iterations=1).astype(np.float32))
    a = a * comp
    if needles:   # drop specks the higher key leaves floating
        lb, nl = nd.label(a > 0.5)
        if nl:
            sizes = nd.sum(np.ones_like(a), lb, index=np.arange(1, nl + 1))
            a = a * np.isin(lb, 1 + np.nonzero(sizes >= 10)[0])
    rgb = np.clip(sub / np.maximum(a[..., None], 0.35), 0, 255)
    if needles: rgb *= 0.86   # the dark fill between needle rows is gone; keep the crown's depth
    rgba = np.dstack([rgb, a * 255]).astype(np.uint8)
    im = Image.fromarray(rgba, 'RGBA')
    if crop: im = im.crop(crop(im))
    return im

_labels = {}
def comp_label(i):
    if i in _labels: return _labels[i]
    y0, x0, y1, x1, _ = boxes[i]
    ids, counts = np.unique(lab[y0:y1, x0:x1][lab[y0:y1, x0:x1] > 0], return_counts=True)
    _labels[i] = ids[np.argmax(counts)]
    return _labels[i]

def tight(im, pad=2):
    a = np.asarray(im)[..., 3]
    ys, xs = np.nonzero(a > 8)
    return im.crop((max(0, xs.min() - pad), max(0, ys.min() - pad), min(im.width, xs.max() + 1 + pad), min(im.height, ys.max() + 1 + pad)))

def wood_mask(im):
    r = np.asarray(im).astype(np.float32)
    return (r[..., 3] > 127) & (r[..., 0] >= r[..., 1] * 0.98)

def orient_base_down(im):
    """Rotate so the thick (base) end of the wood is at the bottom and the
    base→tip axis is vertical."""
    w = wood_mask(im)
    if w.sum() < 50: w = np.asarray(im)[..., 3] > 127
    ys, xs = np.nonzero(w)
    P = np.stack([xs, ys], 1).astype(np.float64)
    c = P.mean(0)
    ev, evec = np.linalg.eigh(np.cov((P - c).T))
    ax = evec[:, 1]
    t = (P - c) @ ax
    dt = nd.distance_transform_edt(w)
    lo, hi = t < np.percentile(t, 12), t > np.percentile(t, 88)
    th_lo = np.percentile(dt[ys[lo], xs[lo]], 90); th_hi = np.percentile(dt[ys[hi], xs[hi]], 90)
    base = P[lo].mean(0) if th_lo >= th_hi else P[hi].mean(0)
    tipv = c - base
    # angle so tipv points up (-y in image)
    ang = math.degrees(math.atan2(tipv[0], -tipv[1]))   # clockwise from up
    return tight(im.rotate(ang, resample=Image.BICUBIC, expand=True))

def spine_of(im, branch=True):
    """Main stem = cheapest path base -> tip (wood cheap, needles dear,
    background very dear), resampled to one point per image row."""
    from skimage.graph import MCP_Geometric
    alpha = np.asarray(im)[..., 3] > 127
    w = wood_mask(im) if branch else alpha
    if branch: w = nd.binary_opening(w, iterations=1) | (w & ~nd.binary_opening(w, iterations=1) & False)
    dtw = nd.distance_transform_edt(w)
    cost = np.where(w, 1 + 3 / (1 + dtw), np.where(alpha, 7.0, 80.0))
    ys, xs = np.nonzero(w)
    yb = ys.max()
    bsel = ys >= yb - 4
    bx = int(np.median(xs[bsel])); by = int(yb)
    # nudge to a wood pixel at the bottom
    m = MCP_Geometric(cost)
    acc, _ = m.find_costs([(by, bx)])
    # tip: highest wood pixel (among those reachable at sane cost)
    ok = w & (acc < np.percentile(acc[w], 99) * 1.5)
    ty, tx = np.nonzero(ok)
    j = np.argmin(ty - 0.15 * 0)   # topmost
    tip = (int(ty[j]), int(tx[j]))
    path = np.array(m.traceback(tip))   # (y, x) from base to tip
    rows = {}
    for y, x in path: rows.setdefault(y, []).append(x)
    ysort = sorted(rows, reverse=True)
    pts = []
    for y in ysort:
        x = float(np.mean(rows[y]))
        ww = 2 * dtw[y, int(round(x))]
        pts.append([x, y, ww if ww > 0 else np.nan])
    pts = np.array(pts, dtype=np.float64)
    good = ~np.isnan(pts[:, 2])
    if good.sum() >= 2:
        pts[:, 2] = np.interp(np.arange(len(pts)), np.nonzero(good)[0], pts[good, 2])
    else:
        pts[:, 2] = 4
    k = 7
    if len(pts) > k:
        pts[:, 0] = np.convolve(np.pad(pts[:, 0], k // 2, mode='edge'), np.ones(k) / k, 'valid')
        # width: robust (max of a running median keeps the stem, ignores thin necks)
        med = nd.median_filter(pts[:, 2], size=k, mode='nearest')
        pts[:, 2] = med
    if not branch:   # trunks: the top rows are the rounded cut end, not the stem width
        n8 = max(3, len(pts) // 12)
        ref = np.median(pts[-3 * n8:-n8, 2]) if len(pts) > 4 * n8 else pts[-1, 2]
        pts[-n8:, 2] = np.maximum(pts[-n8:, 2], ref * 0.9)
    return pts, w

def meta_branch(im, kind, segment=None, base_trunk=False):
    pts, w = spine_of(im, branch=(kind != 'trunk'))
    H = im.height
    ay = pts[0][1]; ax = pts[0][0]
    # 13 samples like the existing sets
    n = 13
    L = ay - pts[-1][1]
    spine = []
    for i in range(n):
        s = L * i / (n - 1)
        j = np.argmin(np.abs((ay - pts[:, 1]) - s))
        spine.append([round(float(pts[j][0] - ax), 1), round(float(s), 1), round(float(max(pts[j][2], 1.2)), 1)])
    smax = round(float(L), 1)
    e = {'type': kind, 'anchor': [round(float(ax) + 0.5, 1), round(float(ay) + 0.5, 1)], 'spine': spine, 'smax': smax}
    w0 = spine[1][2]
    if kind == 'trunk':
        wtop = spine[-1][2]
        if base_trunk:
            e['clip'] = [-50, round(smax - wtop * 0.5, 1)]
        else:
            e['clip'] = [round(w0 * 0.45, 1), round(smax - wtop * 0.5, 1)]
        e['sockets'] = []
        e['segment'] = not base_trunk
        return e
    # forks: wood not on the main stem
    yy, xx = np.mgrid[0:im.height, 0:im.width]
    stem = np.zeros_like(w)
    for x, y, ww in pts:
        x0 = int(round(x - ww / 2 - 2)); x1 = int(round(x + ww / 2 + 2))
        stem[int(y), max(0, x0):max(0, x1 + 1)] = True
    stem = nd.binary_dilation(stem, iterations=2)
    side = w & ~stem
    sl, ns = nd.label(side)
    forks = []
    for f in range(1, ns + 1):
        fy, fx = np.nonzero(sl == f)
        if len(fy) < 12: continue
        # junction = the side pixel nearest the stem; tip = farthest from the junction
        d_st = nd.distance_transform_edt(~stem)[fy, fx]
        j = np.argmin(d_st); jx, jy = fx[j], fy[j]
        dd = np.hypot(fx - jx, fy - jy); t = np.argmax(dd)
        ln = float(dd[t])
        if ln < 8: continue
        forks.append({'tip': [round(float(fx[t] - ax), 1), round(float(ay - fy[t]), 1)], 's': round(float(ay - jy), 1), 'len': int(round(ln))})
    forks.sort(key=lambda f: f['s'])
    e['forks'] = forks
    c0 = round(w0 * 0.45, 1)
    e['clip'] = [c0, round(smax + 6, 1)]
    # safe spans: stem only, at least ~a stem width from any fork junction
    lo, hi = c0 + 4, smax - 5
    bad = sorted([(f['s'] - max(6, w0 * 0.6), f['s'] + max(6, w0 * 0.6)) for f in forks])
    safe, cur = [], lo
    for a_, b_ in bad:
        if a_ > cur + 4: safe.append([round(cur), round(min(a_, hi))])
        cur = max(cur, b_)
    if hi > cur + 4: safe.append([round(cur), round(hi)])
    e['safe'] = [s for s in safe if s[1] - s[0] >= 4]
    return e

def density(im):
    a = np.asarray(im)[..., 3]
    return round(float((a > 127).mean()), 3)

sprites = []   # (key, image, entry)
def add(key, im, e):
    sprites.append((key, im, e))

# ---- trunks: bases keep their bottom, segments are clipped both ends
# sheet #8 (mossy, strongly tapered, broken top) is a treetop; stacked mid-trunk it reads as a seam
BASES = [0, 1, 3]; SEGS = [2, 4, 5, 6, 7]
for n, i in enumerate(BASES):
    im = tight(cut(i, wood=True)); add(f'base{n}', im, meta_branch(im, 'trunk', base_trunk=True))
for n, i in enumerate(SEGS):
    im = tight(cut(i, wood=True)); add(f'trunk{n}', im, meta_branch(im, 'trunk'))
# ---- limbs + twigs
for n, i in enumerate([15, 21, 22, 109, 110, 111, 112, 113]):
    im = orient_base_down(cut(i, wood=True)); add(f'branch{n}', im, meta_branch(im, 'branch'))
for n, i in enumerate([24, 27, 28, 29, 30, 32, 33, 38, 44, 45, 40, 31]):
    im = orient_base_down(cut(i)); add(f'twig{n}', im, meta_branch(im, 'twig'))

# ---- foliage: needle sprays, stem base at the bottom centre (anchor)
def spray(i, hang):
    im = cut(i, needles=True)
    im = tight(im.rotate(180, expand=True)) if hang else orient_base_down(im)
    a = np.asarray(im)[..., 3] > 127
    ys, xs = np.nonzero(a)
    yb = ys.max(); bot = xs[ys >= yb - 6]
    return im, {'anchor': [round(float(bot.mean()) + 0.5, 1), round(float(yb) - im.height * 0.06, 1)], 'density': density(im), 'tone': 'green'}
for n, i in enumerate([46, 47, 48, 9, 18, 20, 13, 12, 16, 23]):
    im, e = spray(i, hang=i in (46, 47, 48)); e['type'] = 'foliage'; add(f'foliage{n}', im, e)
# elongated sprays only: the round lobed ones (53-55, 66-71, 10, 19) read as oak leaves once cut out
CL = [49, 50, 51, 52, 68, 72, 73, 117, 11, 14, 17]
for n, i in enumerate(CL):
    im, e = spray(i, hang=i not in (11, 14, 17)); e['type'] = 'foliage'; add(f'cluster{n}', im, e)
# ---- leaf: needle sprigs (tall ones are used as spiky tip bundles), small bits for particles
LEAF = [25, 26, 34, 35, 36, 37, 39, 41, 43, 76, 77, 78, 79, 80, 81, 82, 83, 84, 89, 90 + 0, 91, 92, 93, 94, 95, 96, 97]
LEAF = [i for i in LEAF if i not in (90,)]
for n, i in enumerate(LEAF):
    im, e = spray(i, hang=i >= 74)
    e['type'] = 'leaf'; e['anchor'] = [im.width / 2, im.height / 2]
    # the small round bits (#74+) are falling-needle particles only: scaled up on a branch tip they read as pods
    if i >= 74: e['particle'] = True
    add(f'leaf{n}', im, e)
for n, i in enumerate([120, 121]):
    im = tight(cut(i)); add(f'leafdry{n}', im, {'type': 'leaf', 'anchor': [im.width / 2, im.height / 2], 'density': density(im), 'tone': 'dry'})
# ---- roots: junction (thick end) at the top
for n, i in enumerate([88, 90, 101, 102, 103, 104]):
    im = orient_base_down(cut(i, wood=True)).rotate(180, expand=True)
    a = np.asarray(im)[..., 3] > 127; ys, xs = np.nonzero(a); top = xs[ys <= ys.min() + 6]
    add(f'root{n}', im, {'type': 'root', 'anchor': [round(float(top.mean()), 1), round(float(ys.min()) + im.height * 0.08, 1)], 'density': density(im)})
# ---- stumps
for n, i in enumerate([105, 106, 114, 107, 108, 115]):
    im = tight(cut(i, wood=True)); a = np.asarray(im)[..., 3] > 127; ys, _ = np.nonzero(a)
    add(f'stump{n}', im, {'type': 'stump', 'anchor': [im.width / 2, round(float(ys.max()) - im.height * 0.08, 1)], 'density': density(im)})
# ---- cut faces: the log round plus the sawn tops of the stumps (ring + a band of bark)
def cface(im):
    return {'type': 'cutface', 'anchor': [im.width / 2, im.height / 2], 'aspect': round(im.height / im.width, 3)}
im = tight(cut(136, wood=True)); add('cutface0', im, cface(im))
for n, (i, f) in enumerate([(114, 0.62), (107, 0.42), (115, 0.6), (106, 0.42)]):
    full = tight(cut(i, wood=True))
    # the sawn top: rows of light wood colour
    r = np.asarray(full).astype(np.float32)
    light = (r[..., 3] > 127) & (r[..., 0] > 150) & (r[..., 0] > r[..., 2] * 1.5)
    ys, xs = np.nonzero(light)
    y0, y1 = ys.min(), int(ys.max() + (ys.max() - ys.min()) * 0.35)
    x0, x1 = xs.min(), xs.max()
    im = full.crop((max(0, x0 - 3), max(0, y0 - 3), min(full.width, x1 + 4), min(full.height, y1)))
    # fade the bark band out at the bottom instead of a ruler edge
    arr = np.asarray(im).copy(); hh = arr.shape[0]
    ramp = np.clip((hh - np.arange(hh)) / (hh * 0.18), 0, 1)
    arr[..., 3] = (arr[..., 3] * ramp[:, None]).astype(np.uint8)
    im = tight(Image.fromarray(arr, 'RGBA')); add(f'cutface{n + 1}', im, cface(im))
# ---- breaks (splintered ends) and burns (charred bark)
for n, i in enumerate([124, 125, 126, 127, 128, 131]):
    im = tight(cut(i, wood=True)); add(f'break{n}', im, {'type': 'break', 'anchor': [im.width / 2, im.height / 2], 'aspect': round(im.height / im.width, 3)})
for n, i in enumerate([130, 132, 129]):
    im = tight(cut(i, wood=True)); add(f'burn{n}', im, {'type': 'burn', 'anchor': [im.width / 2, im.height / 2], 'aspect': round(im.height / im.width, 3)})
# ---- debris + shadows
for n, i in enumerate([122, 123, 133, 134, 135, 116]):
    im = tight(cut(i)); a = np.asarray(im)[..., 3] > 127; ys, _ = np.nonzero(a)
    add(f'debris{n}', im, {'type': 'debris', 'anchor': [im.width / 2, round(float(ys.max()) * 0.85, 1)], 'density': density(im)})
for n, i in enumerate([137, 138, 139, 140, 141, 142, 143]):
    y0, x0, y1, x1, _ = boxes[i]
    g = src[y0 - 3:y1 + 3, x0 - 3:x1 + 3]; m = g.max(2)
    a = np.clip(m / 150.0, 0, 1) * 0.85                     # soft shadow: luminance is coverage
    im = Image.fromarray(np.dstack([np.full_like(m, 20), np.full_like(m, 24), np.full_like(m, 30), a * 255]).astype(np.uint8), 'RGBA')
    im = tight(im); add(f'shadow{n}', im, {'type': 'shadow', 'anchor': [im.width / 2, im.height / 2], 'density': density(im)})

# ---- damage the sheet does not have: borrow pine's
pine = Image.open(S + 'pine.webp').convert('RGBA'); pm = json.load(open(S + 'pine.meta.json'))
for k, e in pm['sprites'].items():
    if e['type'] in ('gash', 'crack', 'chip'):
        x, y, w_, h_ = e['rect']
        ne = {kk: vv for kk, vv in e.items() if kk != 'rect'}
        add(k, pine.crop((x, y, x + w_, y + h_)), ne)

# ---- pack: shelves by height, 2 px gutters
W = 2048
order = sorted(range(len(sprites)), key=lambda j: -sprites[j][1].height)
x = y = sh = 0; pos = {}
for j in order:
    im = sprites[j][1]
    if x + im.width > W: x = 0; y += sh + 2; sh = 0
    pos[j] = (x, y); x += im.width + 2; sh = max(sh, im.height)
H = y + sh
H4 = (H + 3) // 4 * 4
atlas = Image.new('RGBA', (W, H4), (0, 0, 0, 0))
meta = {'version': 2, 'ppu': 90, 'atlas': [W, H4], 'sprites': {}}
for j, (key, im, e) in enumerate(sprites):
    px, py = pos[j]
    atlas.paste(im, (px, py))
    e = dict(e); e['rect'] = [px, py, im.width, im.height]
    if 'density' not in e and e['type'] in ('foliage', 'leaf'): e['density'] = density(im)
    order_keys = ['type', 'rect', 'anchor'] + [k for k in e if k not in ('type', 'rect', 'anchor')]
    meta['sprites'][key] = {k: e[k] for k in order_keys}
# straight alpha: bleed colour into transparent pixels so mips/filtering never pull in black
arr = np.asarray(atlas).astype(np.float32)
a = arr[..., 3] > 0
idx = nd.distance_transform_edt(~a, return_distances=False, return_indices=True)
rgb = arr[..., :3][idx[0], idx[1]]
out = np.dstack([rgb, arr[..., 3]]).astype(np.uint8)
Image.fromarray(out, 'RGBA').save(S + 'spruce.webp', 'WEBP', quality=90, alpha_quality=100, method=6)
json.dump(meta, open(S + 'spruce.meta.json', 'w'), separators=(',', ':'))
prev = Image.new('RGBA', (W, H4), (70, 80, 100, 255)); prev.alpha_composite(atlas); prev.save(S + 'spruce_preview.png')
from collections import Counter
print('atlas', W, H4, 'sprites', len(sprites), Counter(e['type'] for e in meta['sprites'].values()))
import os; print('webp bytes', os.path.getsize(S + 'spruce.webp'))

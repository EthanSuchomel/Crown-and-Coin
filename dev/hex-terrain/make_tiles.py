"""Hex tiles for the board's grass and mountains (Ethan, 2026-11-16).
  - grass: "instead of placing that over the entire map, use that texture for each individual hex".
    Every plain hex gets its own grass tile, cut to the hex. Three tiles from different parts of Ethan's OpenArt
    texture, picked by hex number, so neighbouring hexes don't look stamped.
  - mountain: "a mountain hex that actually has the whole hex as a mountain". Ethan's OpenArt hex is cut out of its
    magenta and fitted to the hex.
Each tile is 222x256 (pointy top, like the water and castle-ground tiles), transparent outside the hex.
  python3 make_tiles.py OUTDIR src/grass_openart.png src/mountain_openart.png [castle_neutral=src/castle_neutral_openart.png ...]
  - castle_neutral (2026-11-16): Ethan's OpenArt hex castle, drawn on neutral castle hexes in place of the stone castle picture."""
import sys, os
import numpy as np
from PIL import Image

W, H = 222, 256
S = 4


def hex_dist(w, h):
    ys, xs = np.mgrid[0:h, 0:w].astype(float)
    x = np.abs((xs + .5 - w / 2) / (w / 2))
    y = np.abs((ys + .5 - h / 2) / (h / 2))
    return np.maximum(x, y + x / 2)


def mask():
    d = hex_dist(W * S, H * S)
    return Image.fromarray(((d <= 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)


CROP = .5   # half the texture's height per hex, the same scale as the castle grounds


def grass_tiles(src):
    im = Image.open(src).convert('RGB')
    w, h = im.size
    ch = round(h * CROP); cw = round(ch * W / H)
    out = []
    for fx, fy in [(.5, .5), (.22, .25), (.78, .72)]:   # three different crops
        x0 = round((w - cw) * fx); y0 = round((h - ch) * fy)
        out.append(im.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.LANCZOS))
    return out


def mountain_tile(src):
    """The OpenArt hexagon isn't quite the board's shape, so it's fitted row by row: each row of the board's hex
    takes the matching row of the picture's hexagon, from its left edge to its right edge (a little inside them,
    so no magenta from the drawn edge comes along)."""
    im = np.array(Image.open(src).convert('RGB')).astype(float)
    bg = np.median(np.concatenate([im[:8].reshape(-1, 3), im[-8:].reshape(-1, 3)]), 0)
    inside = np.sqrt(((im - bg) ** 2).sum(-1)) > 90
    rows = np.where(inside.any(1))[0]
    top, bot = rows.min(), rows.max()
    # a tree top poking above the hexagon (the forest) mustn't count as the hex's top point: take the top and bottom from
    # the middle column, where the hexagon's own points are
    cx = int(np.median(np.where(inside[(top + bot) // 2])[0]))
    col = np.where(inside[:, cx - 3:cx + 4].any(1))[0]
    top, bot = col.min(), col.max()
    SW, SH = W * S, H * S
    d = hex_dist(SW, SH)
    out = np.zeros((SH, SW, 3))
    big = Image.fromarray(im.astype(np.uint8))
    pad = 7   # source pixels kept clear of the picture's own edge line
    for v in range(SH):
        sy = top + pad + (bot - top - 2 * pad) * (v + .5) / SH
        r = inside[int(round(sy))].copy()
        # only the hexagon's own span on this row: the run that contains the middle column (a tree poking out beside the
        # top point isn't part of it)
        lab = np.cumsum(np.r_[0, np.diff(r.astype(int)) != 0])
        if r[cx]: r &= lab == lab[cx]
        xs = np.where(r)[0]
        if len(xs) < 2 * pad + 2: continue
        l, rr = xs.min() + pad, xs.max() - pad
        # the board hex's span on this row
        ys = abs((v + .5 - SH / 2) / (SH / 2)); hw = min(1, 2 * (1 - ys)) if ys > .5 else 1
        ox0, ox1 = SW / 2 - hw * SW / 2, SW / 2 + hw * SW / 2
        xo = np.arange(SW) + .5
        t = np.clip((xo - ox0) / max(ox1 - ox0, 1e-6), 0, 1)
        sx = l + (rr - l) * t
        x0 = np.floor(sx).astype(int); fx = sx - x0; x0 = np.clip(x0, 0, im.shape[1] - 2)
        y0 = int(np.floor(sy)); fy = sy - y0; y0 = min(max(y0, 0), im.shape[0] - 2)
        a = im[y0, x0] * (1 - fx[:, None]) + im[y0, x0 + 1] * fx[:, None]
        b = im[y0 + 1, x0] * (1 - fx[:, None]) + im[y0 + 1, x0 + 1] * fx[:, None]
        out[v] = a * (1 - fy) + b * fy
    out = out.clip(0, 255)
    # magenta caught inside the hex (e.g. between the castle's flags): take the nearest colour that isn't magenta
    mag = (np.abs(out - bg).sum(-1) < 160) | ((out[..., 0] > 150) & (out[..., 2] > 150) & (out[..., 1] < 120))
    if mag.any():
        from scipy import ndimage
        idx = ndimage.distance_transform_edt(mag, return_distances=False, return_indices=True)
        out = out[idx[0], idx[1]]
    return Image.fromarray(out.astype(np.uint8)).resize((W, H), Image.LANCZOS)


out, gsrc, msrc = sys.argv[1:4]
extra = dict(a.split('=', 1) for a in sys.argv[4:])   # more whole-hex tiles fitted the same way as the mountain: name=src.png
os.makedirs(out, exist_ok=True)
m = mask()
for n, t in enumerate(grass_tiles(gsrc)):
    t = t.convert('RGBA'); t.putalpha(m); t.save(os.path.join(out, 'grass_%d.png' % n), optimize=True)
for name, src in [('mountain', msrc)] + list(extra.items()):
    t = mountain_tile(src).convert('RGBA'); t.putalpha(m); t.save(os.path.join(out, name + '.png'), optimize=True)
print(sorted(os.listdir(out)))


# ---- soft edges (Ethan, 2026-11-17: "everything looks very choppy now... flow together better so it doesn't have such
# sharp lines for the tree, fern, and mountain tiles") ----
# Each tile also gets a *_soft.png: the same picture, but instead of a hard hex cut its edge fades out over a slightly
# ragged band. The board draws the soft tiles SOFT_SCALE times bigger than the hex, so the fade spills a little past the
# hex edge and neighbouring tiles overlap and blend (two forests side by side stay solid: each is ~85% opaque at the
# shared edge).
SOFT_SCALE = 1.10
FADE_IN, FADE_OUT = .88, 1.0      # tile-space hex distance: fully opaque inside FADE_IN, gone by FADE_OUT
RAGGED = .035                     # how far the fade wanders in and out along the edge


# mountains get a wider, more uneven fade, so the rock breaks up into the land around it instead of reading as a hexagon
SOFT_PER = {'mountain': (.80, 1.0, .07)}


def soft_alpha(seed, fade_in=None, fade_out=None, ragged=None):
    fi = FADE_IN if fade_in is None else fade_in; fo = FADE_OUT if fade_out is None else fade_out
    rg = RAGGED if ragged is None else ragged
    rng = np.random.default_rng(seed)
    SW, SH = W * S, H * S
    d = hex_dist(SW, SH)
    n = np.zeros((SH, SW))
    for cells, amp in [(7, 1.0), (16, .5), (34, .25)]:   # a few octaves of smooth noise for a natural, uneven edge
        g = rng.uniform(-1, 1, (cells + 1, cells + 1)).astype(np.float32)
        n += amp * np.array(Image.fromarray(g, 'F').resize((SW, SH), Image.BICUBIC))
    n /= 1.75
    t = np.clip((fo - (d + rg * n)) / (fo - fi), 0, 1)
    a = t * t * (3 - 2 * t)
    return Image.fromarray((a * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)


for k, name in enumerate(sorted(f[:-4] for f in os.listdir(out) if f.endswith('.png') and not f.endswith(('_soft.png', '_top.png')))):
    t = Image.open(os.path.join(out, name + '.png')).convert('RGBA')
    # the picture under the cut is needed all the way to the edge: refill the transparent corners from the nearest pixels
    arr = np.array(t).astype(float); inside = arr[..., 3] > 200
    from scipy import ndimage
    idx = ndimage.distance_transform_edt(~inside, return_distances=False, return_indices=True)
    rgb = arr[..., :3][idx[0], idx[1]]
    soft = Image.fromarray(rgb.astype(np.uint8)).convert('RGBA'); soft.putalpha(soft_alpha(1000 + k, *SOFT_PER.get(name, (None, None, None))))
    soft.save(os.path.join(out, name + '_soft.png'), optimize=True)
print('soft tiles made')


# ---- treetops above the hex (Ethan, 2026-11-17: the forest should look tall) ----
# Whatever the OpenArt picture draws above the hexagon's two upper edges (the back row's tallest treetops) is kept as
# NAME_top.png: the tile's width, TOP_PAD of its height taller at the top, transparent except for those treetops. The
# board draws it over the hex above, like the old forest's trees spilling past the edge.
TOP_PAD = .30


def overhang(src):
    im = np.array(Image.open(src).convert('RGB')).astype(float)
    bg = np.median(np.concatenate([im[:8].reshape(-1, 3), im[-8:].reshape(-1, 3)]), 0)
    inside = np.sqrt(((im - bg) ** 2).sum(-1)) > 90
    rows = np.where(inside.any(1))[0]
    mid = (rows.min() + rows.max()) // 2
    cx = int(np.median(np.where(inside[mid])[0]))
    col = np.where(inside[:, cx - 3:cx + 4].any(1))[0]
    top, bot = col.min(), col.max()
    xs = np.where(inside[mid])[0]; l, r = xs.min(), xs.max()
    h, w = im.shape[:2]
    ys, xx = np.mgrid[0:h, 0:w].astype(float)
    hx = np.abs((xx - (l + r) / 2) / ((r - l) / 2)); hy = np.abs((ys - (top + bot) / 2) / ((bot - top) / 2))
    out_hex = np.maximum(hx, hy + hx / 2) > 1.015
    m = inside & out_hex & (ys < mid)
    from scipy import ndimage
    m = ndimage.binary_opening(m, iterations=2)
    if m.sum() < 400:
        return None
    sx = W / (r - l); sy = H / (bot - top)
    CW, CH = W, round(H * (1 + TOP_PAD))
    rgba = np.dstack([im, m * 255.]).astype(np.uint8)
    pic = Image.fromarray(rgba, 'RGBA').transform((CW * S, CH * S), Image.AFFINE,
        (1 / (sx * S), 0, l, 0, 1 / (sy * S), top - H * TOP_PAD / sy), resample=Image.BILINEAR)
    return pic.resize((CW, CH), Image.LANCZOS)


for name, src in list(extra.items()):
    if name == 'forest':
        t = overhang(src)
        if t is not None:
            t.save(os.path.join(out, name + '_top.png'), optimize=True); print('treetops kept above the hex:', name)
        elif os.path.exists(os.path.join(out, name + '_top.png')):
            os.remove(os.path.join(out, name + '_top.png'))

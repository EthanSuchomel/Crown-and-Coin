"""Grass fringe for the edges of mountain / forest hexes that touch grass (Ethan, 2026-11-17: "a new grass edge that
transitions into the tree and mountain hex"). Cut from the OpenArt grass tile. Local frame: x along the hex edge, y inward;
row OUT is the hex edge itself (rows above it reach a little over the neighbour's side)."""
import sys, numpy as np
from PIL import Image, ImageFilter
SRC, OUT_PNG = sys.argv[1], sys.argv[2]
rng = np.random.default_rng(7)
L, EXT, OUT, DEPTH = 128, 18, 12, 44            # tile px: edge 128 (18.3 board units at 7 px a unit)
W, H = L + 2 * EXT, OUT + DEPTH
g = np.array(Image.open(SRC).convert('RGBA')).astype(float)
crop = g[64:64 + H, 30:30 + W, :3]             # inside the hex: fully opaque grass
x = np.arange(W)
def smooth_noise(n, scale):
    k = rng.normal(size=n // scale + 3); xs = np.arange(n) / scale
    i = xs.astype(int); f = xs - i; f = f * f * (3 - 2 * f)
    return k[i] * (1 - f) + k[i + 1] * f
edge = OUT + 14 + 7 * smooth_noise(W, 26) + 3.5 * smooth_noise(W, 9) + 1.5 * smooth_noise(W, 4)   # the grass line, y in px
t = np.clip(np.minimum(x - 0, W - 1 - x) / (EXT + 26), 0, 1)           # taper toward the ends
inner = np.clip(np.minimum(x - EXT, W - 1 - EXT - x) / 30, 0, 1)   # 0 at the hex corners, 1 mid-edge
edge = edge + 9 * (1 - inner) ** 2                                   # round the corners off: more grass there
edge = np.where((x < EXT) | (x > W - 1 - EXT), OUT + (edge - OUT) * np.clip(np.minimum(x, W - 1 - x) / EXT, 0, 1), edge)
yy, xx = np.mgrid[0:H, 0:W].astype(float)
mask = np.clip((edge[None, :] - yy) / 2.2 + 0.5, 0, 1)
# tufts: little blades reaching in past the grass line
for _ in range(70):
    cx = rng.uniform(4, W - 4); te = np.interp(cx, x, t)
    if te < 0.15: continue
    base = np.interp(cx, x, edge); ln = rng.uniform(5, 13) * (0.5 + 0.5 * te); wd = rng.uniform(1.6, 3.2); lean = rng.uniform(-0.5, 0.5)
    dy = yy - base + 1
    inside = (dy >= 0) & (dy <= ln)
    half = wd * (1 - dy / ln)
    blade = inside & (np.abs(xx - cx - lean * dy) <= half)
    mask = np.maximum(mask, blade.astype(float))
a = Image.fromarray((mask * 255).astype(np.uint8))
# shadow the grass casts on the tile: soft dark band just past the grass line
sh = np.array(a.filter(ImageFilter.GaussianBlur(3))).astype(float) / 255
sh = np.roll(sh, 3, axis=0); sh[:3] = 1
shadow_a = np.clip(sh - mask, 0, 1) * 0.40 * np.clip(np.minimum(x - EXT, W - 1 - EXT - x) / 10, 0, 1)[None, :]   # no shadow past the corners
# grass a touch darker at the tips so the line reads
tip = np.clip(mask - np.array(a.filter(ImageFilter.MinFilter(3))).astype(float) / 255, 0, 1)
rgb = crop * (1 - 0.25 * tip[..., None])
alpha = mask + shadow_a * (1 - mask)
col = np.where(mask[..., None] > 0, rgb, 0) * (mask / np.maximum(alpha, 1e-6))[..., None]
out = np.dstack([np.clip(col, 0, 255), np.clip(alpha * 255, 0, 255)]).astype(np.uint8)
Image.fromarray(out, 'RGBA').save(OUT_PNG)
print(OUT_PNG, out.shape, 'OUT', OUT, 'EXT', EXT, 'L', L)

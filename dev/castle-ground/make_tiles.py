"""Hex-shaped ground tiles for castle hexes (Ethan, 2026-11-12: "a texture for each castle's hex so it can look more unified").
Each tile is 222x256 (the hex's shape, pointy top, like the water tile) with the outside of the hex transparent.
  python3 make_tiles.py OUTDIR [faction=source.png ...]
- mythical: no picture. Ethan asked for "a black hexagon like it's floating over a space of nothing", drawn here:
  black in the middle, a faint lift toward the rim so the hex reads as a drop into nothing.
- dinos / robots / mammals / neutral: OpenArt textures, centre-cropped to the hex's shape and scaled down."""
import sys, os
import numpy as np
from PIL import Image

W, H = 222, 256
S = 4   # supersampling for a clean hex edge


def hex_dist(w, h):
    """0 at the centre, 1 on the hex's edge (pointy top), >1 outside."""
    ys, xs = np.mgrid[0:h, 0:w].astype(float)
    x = np.abs((xs + .5 - w / 2) / (w / 2))   # 1 at the flat left and right sides
    y = np.abs((ys + .5 - h / 2) / (h / 2))   # 1 at the top and bottom points
    return np.maximum(x, y + x / 2)          # the slanted sides run from a point (0, 1) to a corner (1, 1/2)


def mask():
    d = hex_dist(W * S, H * S)
    m = Image.fromarray(((d <= 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    return m


def void_tile():
    d = hex_dist(W, H)
    t = np.clip((d - .5) / .5, 0, 1)
    t = t * t * (3 - 2 * t)                  # smoothstep: black over most of the hex, lifting at the rim
    lo, hi = np.array([0, 0, 0]), np.array([22, 25, 33])
    rgb = (lo + (hi - lo) * t[..., None]).astype(np.uint8)
    return Image.fromarray(rgb, 'RGB')


CROP = .5   # use the middle half of the texture, so its pixels come out about the size of the board grass's pixels


def tex_tile(src):
    im = Image.open(src).convert('RGB')
    w, h = im.size
    ch = round(h * CROP); cw = round(ch * W / H)   # the hex is taller than wide
    x0, y0 = (w - cw) // 2, (h - ch) // 2
    im = im.crop((x0, y0, x0 + cw, y0 + ch))
    return im.resize((W, H), Image.LANCZOS)


out = sys.argv[1]
os.makedirs(out, exist_ok=True)
m = mask()
jobs = {'mythical': None}
for a in sys.argv[2:]:
    k, v = a.split('=', 1)
    jobs[k] = v
for k, src in jobs.items():
    tile = void_tile() if src is None else tex_tile(src)
    tile = tile.convert('RGBA'); tile.putalpha(m)
    tile.save(os.path.join(out, 'gnd_%s.png' % k), optimize=True)
    print(k, os.path.getsize(os.path.join(out, 'gnd_%s.png' % k)) // 1024, 'KB')

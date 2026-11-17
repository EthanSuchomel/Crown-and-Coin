"""Godot copy of the Mammal card pictures: the browser's cut-out (dev/mammal-cards/card_art.py), saved as 200-px PNGs
in art/cards/. Run from the Godot project folder: python3 card_png.py <dir with herd/giraffe/wolf/tiger/elephant.png>"""
import sys, io, base64, re, os
import numpy as np
from PIL import Image
from scipy import ndimage

MAX = 200


def cut(path):
    a = np.array(Image.open(path).convert('RGBA'))
    r, g, b = [a[..., i].astype(int) for i in range(3)]
    mg = (r - g > 45) & (b - g > 45) & (abs(r - b) < 90)          # magenta-hued (bright, or darkened in the art's shadows)
    lab, n = ndimage.label(mg)
    sizes = ndimage.sum(mg, lab, range(1, n + 1)); gmean = ndimage.mean(g, lab, range(1, n + 1))
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
    keep = np.zeros(n + 1, bool)
    for k in range(1, n + 1):
        if k in border or (sizes[k - 1] >= 3 and gmean[k - 1] < 70): keep[k] = True
    bg = keep[lab]
    near = ndimage.binary_dilation(bg, iterations=3) & ~bg
    fr = near & (r - g > 60) & (b - g > 60)                         # pink fringe on the outline: dark outline colour
    a[fr, :3] = [12, 10, 14]
    a[bg] = 0
    r, g, b = [a[..., i].astype(int) for i in range(3)]
    tint = (a[..., 3] > 0) & (r - g > 30) & (b - g > 30) & (abs(r - b) < 90) & (g < 80)   # purple cast left in dark shadows
    L = (0.3 * r + 0.45 * g + 0.25 * b)[tint]
    a[tint, 0] = np.clip(L * 1.1, 0, 255); a[tint, 1] = np.clip(L * 0.9, 0, 255); a[tint, 2] = np.clip(L * 0.8, 0, 255)
    fg = a[..., 3] > 0
    lab2, n2 = ndimage.label(fg)
    if n2 > 1:
        s2 = ndimage.sum(fg, lab2, range(1, n2 + 1)); a[np.isin(lab2, np.where(s2 < 60)[0] + 1)] = 0
    im = Image.fromarray(a); im = im.crop(im.getbbox())
    # premultiplied downscale so the edges don't pick up dark fringes
    w, h = im.size; s = MAX / max(w, h); W, H = max(1, round(w * s)), max(1, round(h * s))
    f = np.array(im).astype(float); al = f[..., 3:4] / 255
    pm = Image.fromarray(np.concatenate([f[..., :3] * al, f[..., 3:4]], -1).astype(np.uint8), 'RGBA').resize((W, H), Image.LANCZOS)
    q = np.array(pm).astype(float); al2 = np.clip(q[..., 3:4] / 255, 1e-6, 1)
    out = np.concatenate([np.clip(q[..., :3] / al2, 0, 255), q[..., 3:4]], -1).astype(np.uint8); out[out[..., 3] < 8] = 0
    return Image.fromarray(out, 'RGBA')


src = sys.argv[1]
for k, f in [('roam', 'herd'), ('forage', 'giraffe'), ('den', 'wolf'), ('wild', 'tiger'), ('tusks', 'elephant')]:
    im = cut(os.path.join(src, f + '.png'))
    im.save('art/cards/%s.png' % k, optimize=True)
    print(k, im.size)

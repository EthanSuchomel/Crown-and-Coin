"""Cut Ethan's OpenArt piece sheets (2026-11-17) into separate sprites: each sheet has six pieces, top row small /
medium / large, bottom row long pieces running left-right (h), upper-left to lower-right (d) and lower-left to
upper-right (u). Saved as pieces/KIND_s|m|l|h|d|u.png, 4 px per board unit at the board's scale."""
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage
for kind in ['forest', 'mountain', 'fern']:
    im = np.array(Image.open('src/%s_pieces.png' % kind).convert('RGB')).astype(float)
    bg = np.median(np.concatenate([im[:6].reshape(-1, 3), im[-6:].reshape(-1, 3)]), 0)
    d = np.sqrt(((im - bg) ** 2).sum(-1))
    a = np.clip((d - 60) / 70, 0, 1)
    # un-mix the magenta from soft edges
    al = np.maximum(a, 1e-3)[..., None]; rgb = np.where((a < 1)[..., None], np.clip((im - bg * (1 - al)) / al, 0, 255), im)
    # shadows drawn on the magenta (darker magenta): a see-through black shadow of the same darkness
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    sh = (r - g > 70) & (b - g > 70) & (np.abs(r - b) < 60)
    dark = np.clip(1 - (r + b) / (bg[0] + bg[2]), 0, 1)
    rgb = np.where(sh[..., None], 0, rgb); a = np.where(sh, np.clip(dark * 1.6, 0, .55), a)
    lab, n = ndimage.label(ndimage.binary_dilation(a > .5, iterations={"fern": 28}.get(kind, 10)))
    sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    keep = list(np.argsort(sizes)[::-1][:6] + 1)
    boxes = []
    for L in keep:
        ys, xs = np.where((lab == L) & (a > .05)); boxes.append((ys.min(), ys.max() + 1, xs.min(), xs.max() + 1, L))
    H = im.shape[0]
    top = sorted([b for b in boxes if (b[0] + b[1]) / 2 < H / 2], key=lambda b: b[2])
    bot = sorted([b for b in boxes if (b[0] + b[1]) / 2 >= H / 2], key=lambda b: b[2])
    assert len(top) == 3 and len(bot) == 3, (kind, len(top), len(bot))
    med_w = top[1][3] - top[1][2]
    sc = 30 * 4 / med_w          # the medium piece is 30 board units wide, at 4 px per unit
    for name, (y0, y1, x0, x1, L) in zip(['s', 'm', 'l', 'h', 'd', 'u'], top + bot):
        m = (lab[y0:y1, x0:x1] == L) * a[y0:y1, x0:x1]
        pic = Image.fromarray(np.dstack([rgb[y0:y1, x0:x1], m * 255]).astype(np.uint8), 'RGBA')
        pic = pic.resize((max(1, round(pic.width * sc)), max(1, round(pic.height * sc))), Image.LANCZOS)
        pic.save('pieces/%s_%s.png' % (kind, name), optimize=True)
    print(kind, 'ok')

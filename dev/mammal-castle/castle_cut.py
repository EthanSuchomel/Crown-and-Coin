"""Cut Ethan's new Mammal home castle (the siege-ready waterfall mesa, OpenArt 2026-11-12) out of its magenta background.
python3 castle_cut.py -> castle.png (full-res cutout), castle_256.png (game size), previews"""
import numpy as np
from PIL import Image
from scipy import ndimage

D = '/home/claude/mammals/castle/'


def magenta_mask(a):
    r, g, b = [a[..., i].astype(int) for i in range(3)]
    return (r > 140) & (b > 140) & (g < 110) & (abs(r - b) < 70)


def pinkish(a):
    r, g, b = [a[..., i].astype(int) for i in range(3)]
    return (r - g > 60) & (b - g > 60)


im = Image.open(D + 'castle_raw.png').convert('RGBA')
a = np.array(im)
# background: magenta-hued regions (bright, or darkened where the art shades it behind the scaffolding) that touch the border,
# plus every enclosed magenta-hued pocket (gaps in the ladders, platforms and the arch); the lily flowers are pink but not magenta (green is high)
r, g, b = [a[..., i].astype(int) for i in range(3)]
mg = (r - g > 45) & (b - g > 45) & (abs(r - b) < 90)
lab, n = ndimage.label(mg)
sizes = ndimage.sum(mg, lab, range(1, n + 1))
gmean = ndimage.mean(g, lab, range(1, n + 1))
border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
keep = np.zeros(n + 1, bool)
for k in range(1, n + 1):
    if k in border or (sizes[k - 1] >= 3 and gmean[k - 1] < 70):
        keep[k] = True
bgm = keep[lab]
print('enclosed pockets cleared:', sum(1 for k in range(1, n + 1) if keep[k] and k not in border))
# fringe: pink-tinted pixels touching the background become the dark outline colour
near = ndimage.binary_dilation(bgm, iterations=3) & ~bgm
fr = near & pinkish(a)
a[fr, :3] = [12, 10, 14]
a[bgm] = 0
# purple cast left in the shadows behind the scaffolding (magenta mixed into dark wood): turn it into a dark wood brown
r, g, b = [a[..., i].astype(int) for i in range(3)]
tint = (a[..., 3] > 0) & (r - g > 30) & (b - g > 30) & (abs(r - b) < 90) & (g < 80)
L = (0.3 * r + 0.45 * g + 0.25 * b)[tint]
a[tint, 0] = np.clip(L * 1.15, 0, 255); a[tint, 1] = np.clip(L * 0.78, 0, 255); a[tint, 2] = np.clip(L * 0.55, 0, 255)
print('purple-tinted pixels browned:', int(tint.sum()))
fg = a[..., 3] > 0
lab2, n2 = ndimage.label(fg)
if n2 > 1:
    s2 = ndimage.sum(fg, lab2, range(1, n2 + 1))
    a[np.isin(lab2, np.where(s2 < 40)[0] + 1)] = 0
out = Image.fromarray(a)
out = out.crop(out.getbbox())
out.save(D + 'castle.png')
left = magenta_mask(np.array(out)) & (np.array(out)[..., 3] > 0)
pinkleft = pinkish(np.array(out)) & (np.array(out)[..., 3] > 0)
print('cut', out.size, 'ratio', round(out.height / out.width, 4), 'magenta left', int(left.sum()), 'pinkish left', int(pinkleft.sum()))

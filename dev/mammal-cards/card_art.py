"""The Mammal card pictures (Ethan's OpenArt picks, 2026-11-13): cut out of the magenta background, cropped and stored as
200-px WebP in CARD_ART, like the Dinosaur head shots.
  The Long Roam: a herd (palaeoloxodon, rhino, gorilla, porcupine)   Forage: giraffe   Den Season: wolf
  Call of the Wild: tiger   Tusks and Thorns: elephant
python3 card_art.py index.html roam=herd.png forage=giraffe.png den=wolf.png wild=tiger.png tusks=elephant.png [previewdir]"""
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


p = sys.argv[1]
pairs = [x.split('=', 1) for x in sys.argv[2:] if '=' in x]
prev = next((x for x in sys.argv[2:] if '=' not in x), None)
art = {}
for k, src in pairs:
    im = cut(src)
    bio = io.BytesIO(); im.save(bio, 'WEBP', quality=88, method=6)
    art[k] = 'data:image/webp;base64,' + base64.b64encode(bio.getvalue()).decode()
    print(k, im.size, len(bio.getvalue()) // 1024, 'KB')
    if prev: os.makedirs(prev, exist_ok=True); im.save(os.path.join(prev, k + '.png'))
s = open(p, encoding='utf-8').read()
line = 'Object.assign(CARD_ART,{' + ', '.join('"%s": "%s"' % kv for kv in art.items()) + '});   // Mammal cards (Ethan\'s OpenArt picks, 2026-11-13): The Long Roam a herd, Forage a giraffe, Den Season a wolf, Call of the Wild a tiger, Tusks and Thorns an elephant\n'
m = re.search(r'Object\.assign\(CARD_ART,\{"roam": .*?\n', s)
if m: s = s[:m.start()] + line + s[m.end():]
else:
    i = s.index('Object.assign(CARD_ART,{"mobil"'); j = s.index('\n', i) + 1
    s = s[:j] + line + s[j:]
open(p, 'w', encoding='utf-8').write(s)
print('ok')

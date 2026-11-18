"""Preview of edge-aware terrain (Ethan, 2026-11-17: "is it possible for the forests mountains and water to mesh together or
seam together when placed next to each other?"). Renders the same small board twice: as the game draws it now, and with
each terrain hex deciding, side by side, how to meet its neighbour:
  grass            fade out as now
  same terrain     run solid to the shared edge and cross-fade into the neighbour (over a ragged band); lakes open a
                   water channel through both beaches
  other terrain    fade over a wider band so the two overlap and blend with no grass between
Uses the game's own tiles (dev/hex-terrain/tiles). Usage: preview.py OUT.png"""
import sys, math, numpy as np
from PIL import Image, ImageFilter
T = '/home/claude/crown-and-coin/dev/hex-terrain/tiles/'
NO_CHANNELS = False
PX = 7.0                                   # pixels per board unit
HR = 18.0; HH = HR * math.sqrt(3); HM = 2; GND = HR + .3; SOFT = 1.10
N = 8
GW = 2 * HM + HR * (1.5 * (N - 1) + 2); GH = 2 * HM + HH * (N + .5)
def center(i):
    r, c = divmod(i, N); x = HM + HR + c * 1.5 * HR; y = HM + HH / 2 + r * HH + (c & 1) * HH / 2
    return (GH - y) * PX, (GW - x) * PX
def nbr_dirs(i):
    r, c = divmod(i, N)
    d = [[1, 1], [1, 0], [1, -1], [0, -1], [-1, 0], [0, 1]] if c & 1 else [[0, 1], [1, 0], [0, -1], [-1, -1], [-1, 0], [-1, 1]]
    return [(r + a) * N + c + b if 0 <= r + a < N and 0 <= c + b < N else -1 for a, b in d]
def corner(cx, cy, rad, k):
    a = math.pi / 3 * k; return cx - rad * math.sin(a), cy - rad * math.cos(a)
# a test board: g grass, f forest, m mountain, w water, x off the board
ROWS = ["xxggggxx",
        "xgfffggx",
        "ggffmmgg",
        "gggmmmgg",
        "gwwgmggg",
        "gwwgfwwg",
        "xggffwgx",
        "xxggggxx"]
TER = {'g': 'grass', 'f': 'forest', 'm': 'mountain', 'w': 'water', 'x': 'void'}
cells = [TER[ch] for row in ROWS for ch in row]
W = int(GH * PX); H = int(GW * PX)
def load(n):
    return np.array(Image.open(T + n + '.png').convert('RGBA')).astype(np.float32) / 255
SOFTT = {k: load(k + '_soft') for k in ['grass_0', 'grass_1', 'grass_2', 'forest', 'mountain', 'water']}
tw = int(round(GND * math.sqrt(3) * SOFT * PX)); th = int(round(2 * GND * SOFT * PX))
def scaled(a):   # colour and alpha scaled apart, so the picture under a faded edge keeps its colour
    rgb = np.array(Image.fromarray((a[..., :3] * 255).astype(np.uint8), 'RGB').resize((tw, th), Image.LANCZOS)).astype(np.float32) / 255
    al = np.array(Image.fromarray((a[..., 3] * 255).astype(np.uint8), 'L').resize((tw, th), Image.LANCZOS)).astype(np.float32) / 255
    return np.dstack([rgb, al])
ST = {k: scaled(v) for k, v in SOFTT.items()}
# per-pixel geometry of a tile canvas: distance to each side, in hex units (1 = on the edge)
ys, xs = np.mgrid[0:th, 0:tw].astype(np.float32)
px = xs + .5 - tw / 2; py = ys + .5 - th / 2
apo = HR * math.sqrt(3) / 2 * PX
NORM = []
for k in range(6):
    x0, y0 = corner(0, 0, 1, k); x1, y1 = corner(0, 0, 1, k + 1); mx, my = (x0 + x1) / 2, (y0 + y1) / 2; l = math.hypot(mx, my)
    NORM.append((mx / l, my / l))
DK = [(px * nx + py * ny) / apo for nx, ny in NORM]          # side k's distance
TK = [(px * -ny + py * nx) / (HR * PX) for nx, ny in NORM]   # position along side k (-.5 .. .5 between its corners)
def noise(seed, amp):
    rng = np.random.default_rng(seed); n = np.zeros((th, tw), np.float32)
    for cells_, a in [(6, 1.0), (14, .5), (30, .25)]:
        g = rng.uniform(-1, 1, (cells_ + 1, cells_ + 1)).astype(np.float32)
        n += a * np.array(Image.fromarray(g, 'F').resize((tw, th), Image.BICUBIC))
    return n / 1.75 * amp
from scipy import ndimage
RIM = {'forest': .74, 'mountain': .80, 'water': .52}   # where each tile's own edge art (grass rim, pines, beach) starts
def extend(img, sides, d0):
    """img with everything past d0 on the given sides replaced by the picture mirrored inward across d0."""
    qx, qy = px.copy(), py.copy()
    for _ in range(2):
        for k in sides:
            nx, ny = NORM[k]; d = (qx * nx + qy * ny) / apo; over = np.maximum(0, d - d0)
            qx = qx - 2 * over * apo * nx; qy = qy - 2 * over * apo * ny
    cx_, cy_ = qx + tw / 2 - .5, qy + th / 2 - .5
    out = np.empty_like(img)
    for c in range(4):
        out[..., c] = ndimage.map_coordinates(img[..., c], [cy_, cx_], order=1, mode='nearest')
    out[..., 3] = img[..., 3]
    return out
def ss(lo, hi, v):   # 1 inside lo, 0 past hi
    t = np.clip((hi - v) / (hi - lo), 0, 1); return t * t * (3 - 2 * t)
def composite(canvas, img, alpha, cx, cy):
    x0 = int(round(cx - tw / 2)); y0 = int(round(cy - th / 2))
    xa, ya = max(0, x0), max(0, y0); xb, yb = min(W, x0 + tw), min(H, y0 + th)
    if xa >= xb or ya >= yb: return
    sub = img[ya - y0:yb - y0, xa - x0:xb - x0, :3]; a = alpha[ya - y0:yb - y0, xa - x0:xb - x0, None]
    canvas[ya:yb, xa:xb, :3] = canvas[ya:yb, xa:xb, :3] * (1 - a) + sub * a
def bridge(cv, terr, kind):
    """Joins neighbouring hexes of one kind: a patch of that tile's own middle (mirrored to fill) laid centre to centre
    across their shared edge, soft-edged, and over the corner where three of them meet."""
    src = Image.open(T + kind + '.png').convert('RGB'); ww, wh = src.size; r = 46 if kind == 'water' else 62
    patch = src.crop((ww // 2 - r, wh // 2 - r, ww // 2 + r, wh // 2 + r)).resize((int(2 * r * tw / ww), int(2 * r * tw / ww)), Image.LANCZOS)
    pr = np.array(patch).astype(np.float32) / 255
    tile2 = np.concatenate([np.concatenate([pr, pr[:, ::-1]], 1), np.concatenate([pr[::-1], pr[::-1, ::-1]], 1)], 0)
    WT = np.tile(tile2, (H // tile2.shape[0] + 1, W // tile2.shape[1] + 1, 1))[:H, :W]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    m = np.zeros((H, W), np.float32)
    hs = [i for i in terr if cells[i] == kind]
    wid = HR * PX * (.46 if kind == 'water' else .78)
    for i in hs:
        for j in nbr_dirs(i):
            if j < 0 or j < i or cells[j] != kind: continue
            (ax, ay), (bx, by) = center(i), center(j); dx, dy = bx - ax, by - ay; L = math.hypot(dx, dy)
            sP = np.clip(((xx - ax) * dx + (yy - ay) * dy) / (L * L), 0, 1)
            m = np.maximum(m, ss(wid * .62, wid, np.hypot(xx - (ax + sP * dx), yy - (ay + sP * dy))))
        nb = nbr_dirs(i)
        for k in range(6):
            j1, j2 = nb[k], nb[(k + 1) % 6]
            if j1 >= 0 and j2 >= 0 and cells[j1] == kind and cells[j2] == kind:
                cx, cy = center(i); vx, vy = corner(cx, cy, HR * PX, k + 1)
                m = np.maximum(m, ss(HR * PX * .30, HR * PX * .52, np.hypot(xx - vx, yy - vy)))
    if not hs: return
    rng = np.random.default_rng(5 if kind == 'water' else 9)
    wob = np.array(Image.fromarray(rng.uniform(-1, 1, (24, 24)).astype(np.float32), 'F').resize((W, H), Image.BICUBIC))
    m = np.clip(m + .12 * wob * (m > 0) * (m < 1), 0, 1)
    cv[..., :3] = cv[..., :3] * (1 - m[..., None]) + WT * m[..., None]
def render(edge_aware):
    cv = np.zeros((H, W, 4), np.float32); cv[..., :3] = (0.11, 0.13, 0.12)
    live = [i for i in range(N * N) if cells[i] != 'void']
    for i in live:   # the grass base, as the game draws it
        cx, cy = center(i); g = ST['grass_%d' % (((((i + 5) * 2654435761) & 0xFFFFFFFF) >> 7) % 3)]
        composite(cv, g, g[..., 3], cx, cy)
    terr = [i for i in live if cells[i] != 'grass']
    if not edge_aware:
        for i in terr:
            cx, cy = center(i); t = ST[cells[i]]; composite(cv, t, t[..., 3], cx, cy)
        return cv
    # 1) under the joins: each terrain hex solid out to every edge it shares with the same terrain (a hard cut on the
    #    edge itself, hidden by step 3's cross-fade); lakes get open water there instead of their beach
    deep = ST['water'][th // 2 - 30:th // 2 + 30, tw // 2 - 30:tw // 2 + 30, :3].mean((0, 1))
    EXT = {}
    for i in terr:
        same = [k for k, j in enumerate(nbr_dirs(i)) if j >= 0 and cells[j] == cells[i]]
        EXT[i] = ST[cells[i]]   # (mirroring the art outward smeared it: not used)
    for i in terr:
        cx, cy = center(i); t = EXT[i]; nb = nbr_dirs(i); a = np.zeros((th, tw), np.float32)
        dmax = np.max(DK, 0)
        for k in range(6):
            j = nb[k]
            if j >= 0 and cells[j] == cells[i]:
                sector = (DK[k] >= dmax - 1e-6) & (DK[k] <= 1.0)
                a = np.maximum(a, sector.astype(np.float32))
        if False:
            img = t.copy(); img[..., :3] = deep * (1 + .06 * noise(50 + i, 1)[..., None])   # open water under a channel
            a = np.array(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))).astype(np.float32) / 255
            composite(cv, img, a * .0, cx, cy)   # (water is joined by its channel in step 2)
        else:
            composite(cv, t, a, cx, cy)
    # 2) (lakes are joined after the tiles, step 4)
    bridge(cv, terr, 'forest')   # forest canopy under the joins, where the tiles' grassy rims give way
    # 3) the tiles on top, side by side: grass sides fade as now; same-terrain sides cross-fade over the shared edge
    #    (lakes: their beach on that side gives way to the channel); other-terrain sides fade wider so they overlap
    for i in terr:
        cx, cy = center(i); t = EXT[i]; nb = nbr_dirs(i); n = noise(i * 13 + 7, 1)
        mnt = cells[i] == 'mountain'
        a = np.ones((th, tw), np.float32)
        for k in range(6):
            j = nb[k]; other = cells[j] if j >= 0 else 'void'
            d = DK[k] + (.06 if mnt else .03) * n
            if other == cells[i] and cells[i] == 'forest':
                df = DK[k] + .16 * noise(i * 31 + k, 1)                          # a ragged boundary, not a line
                a = np.minimum(a, ss(.58, .84, df))                               # well before the grassy rim: the canopy shows
            elif other == cells[i]:
                a = np.minimum(a, ss(.90, 1.10, d))                               # cross-fade over the shared edge
            elif other in ('forest', 'mountain', 'water'):
                a = np.minimum(a, ss(.92, 1.14, d))                               # overlap the neighbour, no grass between
            else:
                a = np.minimum(a, ss(.88 if mnt else .968, 1.10, d))               # grass (or the map edge): as now
        composite(cv, t, a, cx, cy)
    bridge(cv, terr, 'water')
    return cv
before = render(False); after = render(True)
def crop(a):
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), 'RGBA').convert('RGB'); return im
b, a = crop(before), crop(after)
out = Image.new('RGB', (b.width * 2 + 30, b.height + 60), (28, 33, 30))
out.paste(b, (0, 60)); out.paste(a, (b.width + 30, 60))
from PIL import ImageDraw, ImageFont
dr = ImageDraw.Draw(out)
try: f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)
except Exception: f = None
dr.text((20, 14), 'Now', fill=(236, 228, 207), font=f); dr.text((b.width + 50, 14), 'Edge-aware (preview)', fill=(239, 193, 90), font=f)
out.save(sys.argv[1]); print(out.size)

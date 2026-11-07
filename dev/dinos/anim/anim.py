"""Walk and attack sheets for the new Dinosaurs, drawn by Claude from Ethan's OpenArt pictures.

Legs: each leg is a 2-bone rig (hip->knee, knee->ankle) plus a foot. The foot follows a path (swing: forward and lifted,
stance: planted and sliding back) and the hip/knee angles come from 2-bone IK, so feet stay flat on the ground in stance.
Only a leg's own pixels move; the thigh's turn fades in from the hip so the body never tears. Far legs are drawn behind the
body, near legs in front. Body pixels a leg uncovers near the hip are filled with the nearest body colour in shadow.
Attacks: the head (or the Stegosaurus' tail) bends about the neck (tail base), the turn fading in along it.
Frame 0 standing (the original picture), 1-8 the walk, then the attack frames.
"""
import sys, json, math
import numpy as np
from PIL import Image
from scipy import ndimage

def ss(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)

def rot(v, a):
    c, s = math.cos(a), math.sin(a)
    return np.array([v[0] * c - v[1] * s, v[0] * s + v[1] * c])

def cross2(a, b):
    return float(a[0] * b[1] - a[1] * b[0])

def ang(v):
    return math.atan2(v[1], v[0])

def seg_t(px, py, a, b):
    """projection parameter of points onto segment a->b, and distance to the segment"""
    ab = np.array(b, float) - np.array(a, float); L2 = (ab ** 2).sum()
    t = ((px - a[0]) * ab[0] + (py - a[1]) * ab[1]) / L2
    tc = np.clip(t, 0, 1)
    d = np.hypot(px - (a[0] + tc * ab[0]), py - (a[1] + tc * ab[1]))
    return t, d

D = math.radians
UNITS = {
  # legs: name, near?, hip, knee, ankle, thigh radius, shin radius, foot box, stride, lift, base phase (0 = back of its stride, 0.5 = front)
  'pachy': dict(src='pachy', fw=290, pad=(70, 70, 60, 12), cycle=0.5,
    legs=[dict(n='far', top=345, near=False, H=(610, 300), K=(600, 440), A=(650, 500), r1=38, r2=30, foot=(585, 488, 745, 555), S=95, lift=38, p0=0.5),
          dict(n='near', top=345, near=True, H=(540, 280), K=(425, 408), A=(405, 492), r1=60, r2=33, foot=(332, 478, 492, 555), S=110, lift=42, p0=0.0)],
    head=dict(P=(765, 245), box=lambda x, y: (x > 745) & (y < 288), r0=15, r1=120),
    atk=[D(12), D(26), D(32), D(14)], steps=[0.15, 0.35, 0.6]),
  'dilo': dict(src='dilo', fw=290, pad=(70, 70, 60, 12), cycle=0.55,
    legs=[dict(n='far', top=300, near=False, H=(630, 280), K=(610, 392), A=(662, 465), r1=38, r2=28, foot=(598, 448, 748, 505), S=95, lift=36, p0=0.5),
          dict(n='near', top=300, near=True, H=(560, 238), K=(450, 362), A=(445, 455), r1=55, r2=31, foot=(355, 440, 508, 508), S=110, lift=40, p0=0.0)],
    head=dict(P=(735, 225), box=lambda x, y: (x > 705) & (y < 238), r0=15, r1=120),
    atk=[D(-12), D(9), D(3)], steps=[0.25, 0.6]),
  'mega': dict(src='mega', fw=350, pad=(70, 70, 60, 12), cycle=0.5,
    legs=[dict(n='far', top=262, near=False, H=(625, 250), K=(618, 340), A=(665, 400), r1=40, r2=30, foot=(635, 390, 772, 452), S=100, lift=34, p0=0.5),
          dict(n='near', top=258, near=True, H=(545, 190), K=(430, 320), A=(400, 395), r1=60, r2=34, foot=(328, 382, 492, 458), S=115, lift=40, p0=0.0)],
    head=dict(P=(765, 130), box=lambda x, y: (x > 765) & (y < 200), r0=15, r1=110),
    atk=[D(-9), D(14), D(18), D(6)], steps=[0.2, 0.4, 0.65]),
  'trike': dict(src='trike', fw=390, pad=(60, 60, 60, 12), cycle=0.7,
    legs=[dict(n='farH', top=395, near=False, H=(330, 330), K=(285, 420), A=(275, 470), r1=45, r2=30, foot=(203, 458, 322, 522), S=55, lift=18, p0=0.0),
          dict(n='farF', top=385, near=False, H=(690, 340), K=(750, 420), A=(790, 470), r1=45, r2=30, foot=(738, 462, 852, 528), S=55, lift=18, p0=0.5),
          dict(n='nearH', top=400, near=True, H=(390, 270), K=(395, 410), A=(405, 470), r1=75, r2=45, foot=(322, 462, 478, 538), S=55, lift=20, p0=0.5),
          dict(n='nearF', top=398, near=True, H=(580, 330), K=(570, 430), A=(590, 480), r1=50, r2=36, foot=(528, 470, 662, 538), S=55, lift=20, p0=0.0)],
    head=dict(P=(640, 290), box=lambda x, y: ((x > 630) & (y < 350)) | ((x > 780) & (y < 400)), r0=20, r1=140),
    atk=[D(10), D(-10), D(-17), D(-5)], steps=[0.2, 0.4, 0.7]),
  'stego': dict(src='stego', fw=450, pad=(80, 60, 50, 12), cycle=0.8,
    legs=[dict(n='farH', top=472, near=False, H=(380, 430), K=(330, 520), A=(300, 565), r1=45, r2=32, foot=(248, 553, 402, 618), S=55, lift=18, p0=0.0),
          dict(n='farF', top=500, near=False, H=(770, 480), K=(800, 535), A=(830, 575), r1=40, r2=30, foot=(788, 566, 918, 618), S=55, lift=18, p0=0.5),
          dict(n='nearH', top=492, near=True, H=(480, 380), K=(470, 505), A=(470, 560), r1=75, r2=45, foot=(398, 552, 568, 636), S=55, lift=20, p0=0.5),
          dict(n='nearF', top=505, near=True, H=(660, 470), K=(650, 545), A=(670, 590), r1=50, r2=35, foot=(612, 582, 752, 636), S=55, lift=20, p0=0.0)],
    head=dict(P=(325, 335), box=lambda x, y: (x < 330) & (y < 425), r0=30, r1=330),   # the tail
    atk=[D(9), D(-14), D(-22), D(-8)], steps=[0.25, 0.45, 0.75]),
}

def build(name, side='blue', out=None):
    U = UNITS[name]
    img = np.array(Image.open(f"{U['src']}_{side}.png").convert('RGBA')).astype(np.float32)
    H0, W0 = img.shape[:2]
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    fr = (img[..., 3] > 0) & (r - g > 25) & (b - g > 25) & (np.abs(r - b) < 90) & (r > 60)
    img[fr, :3] = (24, 16, 18)
    pl, pr, pt, pb = U['pad']
    W, Hh = W0 + pl + pr, H0 + pt + pb
    base = np.zeros((Hh, W, 4), np.float32); base[pt:pt + H0, pl:pl + W0] = img
    alpha = base[..., 3] > 127
    yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32)
    off = np.array([pl, pt], float)
    legs = []
    for L in U['legs']:
        L = dict(L);
        for k in ('H', 'K', 'A'): L[k] = np.array(L[k], float) + off
        L['top'] = L['top'] + pt
        fb = L['foot']; L['foot'] = (fb[0] + pl - 8, fb[1] + pt, fb[2] + pl + 8, fb[3] + pt + 10)
        t1, d1 = seg_t(xx, yy, L['H'], L['K']); t2, d2 = seg_t(xx, yy, L['K'], L['A'])
        infoot = (xx >= L['foot'][0]) & (xx <= L['foot'][2]) & (yy >= L['foot'][1]) & (yy <= L['foot'][3])
        score = np.minimum(d1 / (L['r1'] * 1.22), d2 / (L['r2'] * 1.22))
        score = np.where(yy < L['top'] - 6, 9.0, score)   # above the belly line it's body
        score = np.where(infoot, np.minimum(score, 0.2 + 0.7 * np.clip(np.hypot(xx - L['A'][0], yy - L['A'][1]) / (5 * L['r2']), 0, 1)), score)   # a toe in two foot boxes goes to the nearer ankle
        L['score'] = score; L['t1'] = t1; L['t2'] = t2; L['infoot'] = infoot
        legs.append(L)
    # each opaque pixel belongs to the leg that claims it most strongly (score < 1), or to the body
    sc = np.stack([L['score'] for L in legs]); best = sc.argmin(0); bestv = sc.min(0)
    owner = np.where(alpha & (bestv < 1.0), best, -1)
    for i, L in enumerate(legs):
        L['mask'] = owner == i
        L['upper'] = L['mask'] & (yy < L['top'] + 45)
    body_mask = alpha & (owner < 0)

    def splat(dst, src_rgba, mask, fx, fy):
        ys, xs = np.nonzero(mask)
        col = src_rgba[ys, xs]
        for ox in (-0.34, 0, 0.34):
            for oy in (-0.34, 0, 0.34):
                X = np.rint(fx(xs + ox, ys + oy)[0]).astype(int); Y = np.rint(fx(xs + ox, ys + oy)[1]).astype(int)
                ok = (X >= 0) & (X < W) & (Y >= 0) & (Y < Hh)
                dst[Y[ok], X[ok]] = col[ok]

    def leg_transform(L, F, toe):
        Hp, K0, A0 = L['H'], L['K'], L['A']
        L1 = np.linalg.norm(K0 - Hp); L2 = np.linalg.norm(A0 - K0)
        v = F - Hp; d = np.clip(np.linalg.norm(v), abs(L1 - L2) + 1, L1 + L2 - 0.5)
        a = ang(v); ca = np.clip((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d), -1, 1); al = math.acos(ca)
        side = np.sign(cross2(K0 - Hp, A0 - Hp)) or 1.0
        cands = [Hp + L1 * np.array([math.cos(a + s * al), math.sin(a + s * al)]) for s in (1, -1)]
        Kp = min(cands, key=lambda k: abs((np.sign(cross2(k - Hp, F - Hp)) or 1) - side))
        th1 = ang(Kp - Hp) - ang(K0 - Hp)
        th2 = ang((Hp + d * np.array([math.cos(a), math.sin(a)])) - Kp) - ang(A0 - K0)
        Fa = Kp + rot(A0 - K0, th2)
        def fx(x, y):
            px = x - Hp[0]; py = y - Hp[1]
            t1 = ((x - Hp[0]) * (K0 - Hp)[0] + (y - Hp[1]) * (K0 - Hp)[1]) / (L1 * L1)
            top = L['top']; w1 = ss(top - 4, max(top + 30, top + 0.6 * (K0[1] - top)), y)   # the swing fades in below the belly line
            c, s = np.cos(th1 * w1), np.sin(th1 * w1)
            tx = Hp[0] + px * c - py * s; ty = Hp[1] + px * s + py * c   # thigh
            qx = x - K0[0]; qy = y - K0[1]; c2, s2 = math.cos(th2), math.sin(th2)
            sx = Kp[0] + qx * c2 - qy * s2; sy = Kp[1] + qx * s2 + qy * c2   # shin
            t2 = ((x - K0[0]) * (A0 - K0)[0] + (y - K0[1]) * (A0 - K0)[1]) / (L2 * L2)
            wk = ss(-0.2, 0.2, t2) * ss(0.3, 0.6, t1)
            rx = x - A0[0]; ry = y - A0[1]; c3, s3 = math.cos(toe), math.sin(toe)
            fxx = Fa[0] + rx * c3 - ry * s3; fyy = Fa[1] + rx * s3 + ry * c3   # foot: keeps its angle, plus the toe droop
            infoot = (x >= L['foot'][0]) & (x <= L['foot'][2]) & (y >= L['foot'][1]) & (y <= L['foot'][3])
            t3 = ((x - A0[0]) * (A0 - K0)[0] + (y - A0[1]) * (A0 - K0)[1]) / (L2 * L2)
            wf = infoot * np.maximum(ss(A0[1] - 30, A0[1] - 6, y), ss(20, 35, np.abs(x - A0[0])))   # the foot moves in one piece
            X = tx + (sx - tx) * wk; Y = ty + (sy - ty) * wk
            X = X + (fxx - X) * wf; Y = Y + (fyy - Y) * wf
            return X, Y
        return fx

    def foot_target(L, p):
        S, h = L['S'], L['lift']
        center = L['A'][0] + (S / 2 if L['p0'] == 0 else -S / 2)
        back, front = center - S / 2, center + S / 2
        if p < 0.5:
            q = p / 0.5; e = 0.5 - 0.5 * math.cos(math.pi * q)
            return np.array([back + (front - back) * e, L['A'][1] - h * math.sin(math.pi * q)]), D(-14) * math.sin(math.pi * q)
        q = (p - 0.5) / 0.5
        return np.array([front - (front - back) * q, L['A'][1]]), 0.0

    def compose(leg_fx, head_angle=0.0):
        out = np.zeros_like(base)
        hd = U['head']; HP = np.array(hd['P'], float) + off
        hmask = body_mask & hd['box'](xx - pl, yy - pt)
        bmask = body_mask & ~hmask
        for i, L in enumerate(legs):
            if not L['near']: splat(out, base, L['mask'], leg_fx[i], None)
        out[bmask] = base[bmask]
        def hfx(x, y):
            r = np.hypot(x - HP[0], y - HP[1]); w = ss(hd['r0'], hd['r1'], r); a = head_angle * w
            c, s = np.cos(a), np.sin(a); px, py = x - HP[0], y - HP[1]
            return HP[0] + px * c - py * s, HP[1] + px * s + py * c
        splat(out, base, hmask, hfx, None)
        for i, L in enumerate(legs):
            if L['near']: splat(out, base, L['mask'], leg_fx[i], None)
        # body a leg (or the head) has uncovered: the nearest body colour, in shadow
        filled = out[..., 3] > 127
        zone = np.zeros_like(alpha)
        for L in legs: zone |= L['upper']
        zone |= hmask & (np.hypot(xx - HP[0], yy - HP[1]) < hd['r0'] + 0.35 * (hd['r1'] - hd['r0']))
        hole = zone & ~filled
        if hole.any():
            src = filled & body_mask
            _, (iy, ix) = ndimage.distance_transform_edt(~src, return_indices=True)
            c = base[iy[hole], ix[hole]].copy(); c[:, :3] *= 0.62; c[:, 3] = 255
            out[hole] = c
        # tidy: drop specks, fill pinholes
        a = out[..., 3] > 127
        lab, n = ndimage.label(a)
        if n > 1:
            sz = ndimage.sum(a, lab, range(1, n + 1)); small = np.isin(lab, [i + 1 for i, s in enumerate(sz) if s < 900])
            out[small] = 0
        a = out[..., 3] > 127
        holes = ndimage.binary_fill_holes(a) & ~a
        lab, n = ndimage.label(holes)
        if n:
            sz = ndimage.sum(holes, lab, range(1, n + 1)); fillm = np.isin(lab, [i + 1 for i, s in enumerate(sz) if s < 700])
            if fillm.any():
                _, (iy, ix) = ndimage.distance_transform_edt(~a, return_indices=True)
                out[fillm] = out[iy[fillm], ix[fillm]]
        out[..., 3] = np.where(out[..., 3] > 127, 255, 0)
        return out

    still = [lambda x, y: (x, y)] * len(legs)
    frames = [compose(still)]
    for k in range(8):
        t = k / 8
        fxs = []
        for L in legs:
            F, toe = foot_target(L, (L['p0'] + t) % 1.0)
            fxs.append(leg_transform(L, F, toe))
        frames.append(compose(fxs))
    for a in U['atk']:
        frames.append(compose(still, a))
    # down to game size
    fw = U['fw']; fh = round(Hh * fw / W)
    small = [Image.fromarray(f.astype(np.uint8), 'RGBA').resize((fw, fh), Image.LANCZOS) for f in frames]
    sheet = Image.new('RGBA', (fw * len(small), fh))
    for i, s in enumerate(small): sheet.paste(s, (i * fw, 0))
    meta = dict(name=name, frames=len(small), fw=fw, fh=fh, W=W, H=Hh, W0=W0, H0=H0, pad=U['pad'], cycle=U['cycle'], steps=U['steps'])
    if out:
        sheet.save(out, optimize=True)
    return sheet, meta, frames

if __name__ == '__main__':
    names = sys.argv[1:] or list(UNITS)
    allmeta = {}
    for n in names:
        for side in ('blue', 'red'):
            sh, meta, _ = build(n, side, f'sheet_{n}_{side}.png')
        allmeta[n] = meta; print(n, meta)
    json.dump(allmeta, open('sheets_meta.json', 'w'), indent=1)

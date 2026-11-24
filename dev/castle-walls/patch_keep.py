"""Ethan, 2026-11-24: the neutral castle redrawn as a single building with no walls (OpenArt, Nano Banana 2, project
Game buildings; Ethan's pick, cut out of its magenta background: art/castle_keep.png). It no longer fills its hex as a
tile: the keep stands on the grass, a little smaller than the hex, so bought walls run round it.
Usage: python3 patch_keep.py index.html"""
import sys, base64, os
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
here = os.path.dirname(os.path.abspath(__file__))
from PIL import Image
import io
im = Image.open(os.path.join(here, 'art', 'castle_keep.png'))
buf = io.BytesIO(); im.save(buf, 'WEBP', lossless=True)
uri = 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()
ratio = round(im.size[1] / im.size[0], 4)
def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, a[:120]); s = s.replace(a, b)
rep("ART.castle_mammals=MAMMAL_ART.castle; Object.assign(ART.bld,MAMMAL_ART.bld);",
    "ART.castle_mammals=MAMMAL_ART.castle; Object.assign(ART.bld,MAMMAL_ART.bld);\nART.castle_neutral={uri:'%s',ratio:%s};   // the neutral castle: a single keep, no walls (Ethan, 2026-11-24, OpenArt)" % (uri, ratio))
rep("const castleW=f=>f==='mythical'?26:", "const castleW=f=>f==='mythical'?26:f==='neutral'?19:")   # the keep: room for walls round it
rep("const castleTile=t=>!!(t.castle&&castleArt(t)==='neutral'&&HEX_TERRAIN.castle_neutral);", "const castleTile=t=>false;   // the neutral castle stands on the grass since 2026-11-24 (it was a whole-hex tile)")
rep("""      castles+=`<use href="#ca-${f}" x="${(cx-w/2).toFixed(2)}" y="${(cy-ch/2).toFixed(2)}"/>`;""",
    """      castles+=`<use href="#ca-${f}" x="${(cx-w/2).toFixed(2)}" y="${(cy-ch*(f==='neutral'?0.58:0.5)).toFixed(2)}"/>`;""")
rep("walls+=wallSvg(cx,cy,k,hp,false,owned&&S.players[t.owner].faction==='mammals');", "walls+=wallSvg(cx,cy,k,hp,false,false);   /* every faction's walls are the castle's stone walls (Ethan, 2026-11-24) */")
open(p, 'w', encoding='utf-8').write(s); print('ok', ratio, len(uri))

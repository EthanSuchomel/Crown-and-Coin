"""Castle hexes get their own ground (2026-11-12): the hex under each castle picture is drawn with a ground tile
that matches that castle (castleArt: the owner's faction for a home castle, 'neutral' otherwise), in place of the grass.
The team colour wash is left off those hexes so the ground keeps its colours (the team border still shows the owner).
python3 patch_ground.py index.html TILEDIR   (uses every gnd_<faction>.png in TILEDIR; re-running replaces the set)"""
import sys, os, re, base64, io
from PIL import Image

p, d = sys.argv[1], sys.argv[2]
s = open(p, encoding='utf-8').read()
tiles = {}
for f in sorted(os.listdir(d)):
    m = re.fullmatch(r'gnd_([a-z]+)\.png', f)
    if m:
        tiles[m.group(1)] = 'data:image/png;base64,' + base64.b64encode(open(os.path.join(d, f), 'rb').read()).decode()
line = '/*CASTLE_GND*/const CASTLE_GND={' + ','.join('"%s":"%s"' % kv for kv in tiles.items()) + '};   // ground tiles for castle hexes, by castle picture (hex-shaped, 222x256)\n'


def rep(old, new):
    global s
    assert s.count(old) == 1, (old[:70], s.count(old))
    s = s.replace(old, new)


if '/*CASTLE_GND*/' in s:
    s = re.sub(r'/\*CASTLE_GND\*/const CASTLE_GND=\{.*?\};[^\n]*\n', lambda m: line, s, count=1, flags=re.S)
else:
    anchor = '/*MAMMAL_ART*/const MAMMAL_ART='
    i = s.index(anchor)
    s = s[:i] + line + s[i:]
    # the tiles as reusable images, drawn a hair bigger than the hex so no grass shows at the edge
    rep("  for(const f of ['dinos','robots','mammals','mythical','neutral']){const c=ART['castle_'+f], w=castleW(f); d+=img('ca-'+f,c.uri,+w.toFixed(2),+(w*c.ratio).toFixed(2),0);}\n",
        "  for(const f of ['dinos','robots','mammals','mythical','neutral']){const c=ART['castle_'+f], w=castleW(f); d+=img('ca-'+f,c.uri,+w.toFixed(2),+(w*c.ratio).toFixed(2),0);}\n"
        "  for(const f in CASTLE_GND) d+=img('gd-'+f,CASTLE_GND[f],+(GND_R*Math.sqrt(3)).toFixed(2),2*GND_R,0);   // castle hex grounds\n")
    rep("const castleArt=t=>isHomeCastle(t)?S.players[t.owner].faction:'neutral';",
        "const castleArt=t=>isHomeCastle(t)?S.players[t.owner].faction:'neutral';\n"
        "const GND_R=HR+.3;   // a castle hex's ground tile covers the hex like the grass does\n"
        "const castleGnd=t=>{ if(!t.castle) return null; const f=castleArt(t); return CASTLE_GND[f]?f:null; };   // the castle's own ground, if it has one")
    rep("    h+=`<g class=\"cell\" data-id=\"${i}\"><polygon points=\"${hexPts(cx,cy,HR+.3)}\" fill=\"url(#grassPat)\"/>`;\n",
        "    h+=`<g class=\"cell\" data-id=\"${i}\"><polygon points=\"${hexPts(cx,cy,HR+.3)}\" fill=\"url(#grassPat)\"/>`;\n"
        "    const gnd=castleGnd(t);   // a castle's hex is drawn with that castle's ground (the Mythical's: a black drop into nothing)\n"
        "    if(gnd) h+=`<use class=\"ico\" href=\"#gd-${gnd}\" x=\"${(cx-GND_R*Math.sqrt(3)/2).toFixed(2)}\" y=\"${(cy-GND_R).toFixed(2)}\"/>`;\n")
    rep("      h+=`<polygon class=\"ico\" points=\"${hexPts(cx,cy,HR)}\" fill=\"${col}\" opacity=\".2\"/>`;\n",
        "      if(!gnd) h+=`<polygon class=\"ico\" points=\"${hexPts(cx,cy,HR)}\" fill=\"${col}\" opacity=\".2\"/>`;   // no colour wash over a castle's own ground\n")
open(p, 'w', encoding='utf-8').write(s)
print('tiles:', ', '.join('%s %d KB' % (k, len(v) // 1365) for k, v in tiles.items()))

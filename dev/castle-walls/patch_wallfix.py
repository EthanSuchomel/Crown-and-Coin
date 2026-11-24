"""Ethan, 2026-11-24: "make sure there are no weird overlaps for the walls; the side wall looks goofy".
- The up-and-down wall piece had perspective (narrow far end), so it read as a tall pillar: every row is now stretched
  to the same width (art/wall_v.png re-cut), so it's a straight wall seen from above, a little narrower (WALL_VW .75).
- Drawing order round a hex: all back walls (upright sides first, then the slanted ones), then the back towers, then
  the castle, then the front walls, then the front towers, so no wall is drawn over a tower and towers cover every join.
Usage: python3 patch_wallfix.py index.html   (after patch_wallv.py)"""
import sys, os, json, base64, io, re
from PIL import Image
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
here = os.path.dirname(os.path.abspath(__file__))
V = json.load(open(os.path.join(here, 'art', 'walls.json')))['v']
im = Image.open(os.path.join(here, 'art', 'wall_v.png')); b = io.BytesIO(); im.save(b, 'WEBP', lossless=True)
V['uri'] = 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, a[:120]); s = s.replace(a, b)
i = s.index("WALL_ART.v={"); j = s.index(";   // the wall running straight up and down", i)
s = s[:i] + "WALL_ART.v=" + json.dumps(V) + s[j:]
rep("const WALL_VW=0.95;", "const WALL_VW=1.15;")
rep("  return [back+tb, front+tf];\n}", "  return [back, tb, front, tf];\n}")
rep("""    let wfront='';   // every faction's walls are the castle's stone walls (Ethan, 2026-11-24): behind the castle, or in front of it
    if(t.walls) [0,5,1,4,2,3].forEach(k=>{ const hp=t.walls[k]; if(hp>0){ const [wb,wf]=wallArt(cx,cy,k,hp); walls+=wb; wfront+=wf; } });""",
    """    let wfront='';   // every faction's walls are the castle's stone walls (Ethan, 2026-11-24): back walls, back towers, the castle, front walls, front towers
    if(t.walls){ const W=[[],[],[],[]]; [1,4,0,5,2,3].forEach(k=>{ const hp=t.walls[k]; if(hp>0) wallArt(cx,cy,k,hp).forEach((g,q)=>W[q].push(g)); });
      castles+=W[0].join('')+W[1].join(''); wfront=W[2].join('')+W[3].join(''); }   // (in the castles layer, before this hex's castle)""")
open(p, 'w', encoding='utf-8').write(s); print('ok')

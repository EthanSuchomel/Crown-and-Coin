"""Painted map, hidden hexes (Ethan, 2026-11-17: try "a painted map with hidden hexes" on the claude.ai link first).
Every rule stays exactly the same; only the drawing changes:
  - the hex grid lines are hidden, and appear (faintly) only while you have a hex selected or are choosing a target
    (a move, a wall, a trebuchet shot, a building spot)
  - no colour wash over owned hexes: the territory border alone shows who owns what
  - the neutral castle tile fades into the land around it like the other terrain
Applied to the claude.ai build only:  python3 patch_painted.py cc_claude.html"""
import sys
import base64, os
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
TILES = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'hex-terrain', 'tiles')
castle_soft = 'data:image/png;base64,' + base64.b64encode(open(os.path.join(TILES, 'castle_neutral_soft.png'), 'rb').read()).decode()
def rep(o, n):
    global s
    assert s.count(o) == 1, (o[:70], s.count(o)); s = s.replace(o, n)
# 1. the grid: an id, hidden unless something is being chosen
rep('<path class="ico" d="${grid}" stroke="#060907" stroke-width=".6" opacity=".16" fill="none"/>',
    '<path id="hexgrid" class="ico" d="${grid}" stroke="#060907" stroke-width=".6" opacity="0" fill="none" style="transition:opacity .25s"/>')
rep("  own+=borderSvg(bord);\n",
    "  own+=borderSvg(bord);\n"
    "  { const g=$('#hexgrid'); if(g) g.setAttribute('opacity', (ui.sel!=null||hl.size||tg.size||wallFor!=null||buildHex()!=null)?'.22':'0'); }   // painted map: the grid shows only while choosing\n")
# 2. no colour wash over owned land
rep("      if(!gnd&&!ctile) own+=`<polygon points=\"${hexPts(cx,cy,HR)}\" fill=\"${col}\" opacity=\".2\"/>`;", "")
# 3. the neutral castle tile soft-edged
rep("    for(const k of ['mountain','forest','fern','water']) d+=img('s-'+k,HEX_TERRAIN.soft[k],sw,sh,0); }",
    "    for(const k of ['mountain','forest','fern','water']) d+=img('s-'+k,HEX_TERRAIN.soft[k],sw,sh,0);\n    d+=img('s-castle','" + castle_soft + "',sw,sh,0); }")
rep("    if(ctile) terr+=`<use href=\"#ctn\" x=\"${gx}\" y=\"${gy}\"/>`;",
    "    if(ctile) terr+=`<use href=\"#s-castle\" x=\"${sx}\" y=\"${sy}\"/>`;")
open(p, 'w', encoding='utf-8').write(s); print('painted map patched')

# ---- natural shapes (Ethan, 2026-11-17: "make the shapes of the trees, ferns, mountains, neutral castles not be hexes but a
# flowing natural shape, especially if the two spaces are connected to a similar space") ----
# Each terrain type is drawn through one mask made from its hexes: the hexes are blurred together and cut at a threshold
# (so neighbours of the same kind melt into one shape with rounded corners), the outline is pushed about by noise (a
# wavy, natural edge), then feathered. Forests: under the shape, each forest hex's own tile still shows its ring of
# saplings and grass round the outside; inside the shape, the dense dark forest (no grassy ring), so joined forests read
# as one wood. Mountains, ferns and neutral castles: their tiles drawn through the shape.
dense = 'data:image/png;base64,' + base64.b64encode(open(os.path.join(TILES, 'forest_dense_soft.png'), 'rb').read()).decode()
rep("    if(whole) terr+=`<use href=\"#s-${whole}\" x=\"${sx}\" y=\"${sy}\"/>`;",
    "    if(whole) pcs.push({k:whole,i,cx,cy});   // a shaped piece (drawn after the loop, with bridges to matching neighbours)")
rep("    if(ctile) terr+=`<use href=\"#s-castle\" x=\"${sx}\" y=\"${sy}\"/>`;",
    "    if(ctile){ org.castle.t+=`<use href=\"#s-castle\" x=\"${sx}\" y=\"${sy}\"/>`; org.castle.m+=`<polygon points=\"${hexPts(cx,cy,HR*.97)}\"/>`; }")
rep("  let h='', marks='',", "  const org={castle:{t:'',m:''}}, pcs=[];\n  let h='', marks='',")
rep("  own+=borderSvg(bord);\n",
    "  own+=borderSvg(bord);\n"
    "  { const R='filterUnits=\"userSpaceOnUse\" x=\"-60\" y=\"-60\" width=\"420\" height=\"380\"', M='maskUnits=\"userSpaceOnUse\" x=\"-60\" y=\"-60\" width=\"420\" height=\"380\"';\n"
    "    let df=`<defs><filter id=\"orgf\" ${R}><feGaussianBlur in=\"SourceGraphic\" stdDeviation=\"4.2\" result=\"b\"/><feComponentTransfer in=\"b\" result=\"t\"><feFuncA type=\"linear\" slope=\"5\" intercept=\"-2.3\"/></feComponentTransfer>`\n"
    "      +`<feTurbulence type=\"fractalNoise\" baseFrequency=\".05\" numOctaves=\"3\" seed=\"11\" result=\"n\"/><feDisplacementMap in=\"t\" in2=\"n\" scale=\"13\" xChannelSelector=\"R\" yChannelSelector=\"G\" result=\"d\"/><feGaussianBlur in=\"d\" stdDeviation=\"1\"/></filter>`;\n"
    "    let gs='';\n"
    "    for(const k of ['castle']){ if(!org[k].m) continue;\n"
    "      df+=`<mask id=\"om-${k}\" ${M}><g filter=\"url(#orgf)\" fill=\"#fff\">${org[k].m}</g></mask>`; gs+=`<g mask=\"url(#om-${k})\">${org[k].t}</g>`; }\n"
    "    terr+=df+'</defs>'+gs; }   // natural shapes\n"
    "  terr+=piecesSvg(pcs);\n")
rep("$('#terr').innerHTML=terr;", "if(terr!==window._lastTerr){ $('#terr').innerHTML=terr; window._lastTerr=terr; }  /* the shapes are costly to redraw: only when the land changes */")
open(p, 'w', encoding='utf-8').write(s); print('natural shapes patched')

# ---- shaped pieces (Ethan, 2026-11-17: "an actual shape change", not an erased hex) ----
# OpenArt piece sheets (src/*_pieces.png, cut by cut_pieces.py): each forest / mountain / fern hex gets a free-standing
# piece with its own natural outline (large when it sits among 3+ of its kind), and every pair of neighbouring hexes of
# the same kind gets a long piece between them, running the same way (left-right, or either diagonal), so joined hexes
# become one grove, ridge or marsh. Pieces stand up over what's behind them (drawn back to front).
import json
from PIL import Image as _I
PD = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pieces')
defs = ''; sizes = {}
for f in sorted(os.listdir(PD)):
    n = f[:-4]; im = _I.open(os.path.join(PD, f)); sizes[n] = (round(im.width / 3.2, 2), round(im.height / 3.2, 2))   # 25% bigger than the scale they were cut at
    defs += "d+=img('pc-%s','data:image/png;base64,%s',%s,%s,0);" % (n, base64.b64encode(open(os.path.join(PD, f), 'rb').read()).decode(), sizes[n][0], sizes[n][1])
rep("    d+=img('s-castle','", "    " + defs + "\n    d+=img('s-castle','")
rep("const hexV=(cx,cy,rad,k)=>", """const PIECE_SZ=""" + json.dumps(sizes) + """;
function piecesSvg(pcs){
  const at=new Map(pcs.map(p=>[p.i,p])), out=[];
  const put=(n,x,y,bottom)=>{ const [w,h]=PIECE_SZ[n]; const top=bottom!=null?bottom-h:y-h/2; out.push({b:top+h,s:`<use href="#pc-${n}" x="${(x-w/2).toFixed(2)}" y="${top.toFixed(2)}"/>`}); };
  for(const p of pcs){
    let same=0; nbrDirs(p.i).forEach(j=>{ const q=at.get(j); if(q&&q.k===p.k){ same++;
      if(j>p.i){ const dx=q.cx-p.cx, dy=q.cy-p.cy, dir=Math.abs(dy)<1?'h':(dx*dy>0?'d':'u');
        put(p.k+'_'+dir,(p.cx+q.cx)/2,(p.cy+q.cy)/2+1,null); } } });
    put(p.k+'_'+(same>=3?'l':'m'),p.cx,p.cy,p.cy+14);
  }
  return out.sort((a,b)=>a.b-b.b).map(o=>o.s).join('');
}
const hexV=(cx,cy,rad,k)=>""")
import re as _re
s, nt = _re.subn(r"    if\(t\.forest\) trees\+=`<image href=\"\$\{HEX_TERRAIN\.forest_top\}\"[^\n]*\n", "", s); assert nt == 1
open(p, 'w', encoding='utf-8').write(s); print('shaped pieces patched')

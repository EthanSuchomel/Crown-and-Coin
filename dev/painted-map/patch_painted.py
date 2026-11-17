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
rep("    d+=img('s-castle','", "    d+=img('s-fdense','" + dense + "',sw,sh,0);\n    d+=img('s-castle','")
rep("    if(whole) terr+=`<use href=\"#s-${whole}\" x=\"${sx}\" y=\"${sy}\"/>`;",
    "    if(whole){ const u=`<use href=\"#s-${whole}\" x=\"${sx}\" y=\"${sy}\"/>`, m=`<polygon points=\"${hexPts(cx,cy,HR*.9)}\"/>`;\n"
    "      if(whole==='forest'){ org.forest.t+=u; org.fcore.t+=`<use href=\"#s-fdense\" x=\"${sx}\" y=\"${sy}\"/>`; org.fcore.m+=`<polygon points=\"${hexPts(cx,cy,HR*.62)}\"/>`; } else org[whole].t+=u;\n"
    "      org[whole].m+=m; }")
rep("    if(ctile) terr+=`<use href=\"#s-castle\" x=\"${sx}\" y=\"${sy}\"/>`;",
    "    if(ctile){ org.castle.t+=`<use href=\"#s-castle\" x=\"${sx}\" y=\"${sy}\"/>`; org.castle.m+=`<polygon points=\"${hexPts(cx,cy,HR*.97)}\"/>`; }")
rep("  let h='', marks='',", "  const org={forest:{t:'',m:''},fern:{t:'',m:''},mountain:{t:'',m:''},castle:{t:'',m:''},fcore:{t:'',m:''}};\n  let h='', marks='',")
rep("  own+=borderSvg(bord);\n",
    "  own+=borderSvg(bord);\n"
    "  { const R='filterUnits=\"userSpaceOnUse\" x=\"-60\" y=\"-60\" width=\"420\" height=\"380\"', M='maskUnits=\"userSpaceOnUse\" x=\"-60\" y=\"-60\" width=\"420\" height=\"380\"';\n"
    "    let df=`<defs><filter id=\"orgf\" ${R}><feGaussianBlur in=\"SourceGraphic\" stdDeviation=\"4.2\" result=\"b\"/><feComponentTransfer in=\"b\" result=\"t\"><feFuncA type=\"linear\" slope=\"5\" intercept=\"-2.3\"/></feComponentTransfer>`\n"
    "      +`<feTurbulence type=\"fractalNoise\" baseFrequency=\".05\" numOctaves=\"3\" seed=\"11\" result=\"n\"/><feDisplacementMap in=\"t\" in2=\"n\" scale=\"13\" xChannelSelector=\"R\" yChannelSelector=\"G\" result=\"d\"/><feGaussianBlur in=\"d\" stdDeviation=\"1\"/></filter>`;\n"
    "    let gs='';\n"
    "    for(const k of ['fern','forest','fcore','mountain','castle']){ if(!org[k].m) continue;\n"
    "      df+=`<mask id=\"om-${k}\" ${M}><g filter=\"url(#orgf)\" fill=\"#fff\">${org[k].m}</g></mask>`; gs+=`<g mask=\"url(#om-${k})\">${org[k].t}</g>`; }\n"
    "    terr+=df+'</defs>'+gs; }   // natural shapes\n")
rep("$('#terr').innerHTML=terr;", "if(terr!==window._lastTerr){ $('#terr').innerHTML=terr; window._lastTerr=terr; }  /* the shapes are costly to redraw: only when the land changes */")
open(p, 'w', encoding='utf-8').write(s); print('natural shapes patched')

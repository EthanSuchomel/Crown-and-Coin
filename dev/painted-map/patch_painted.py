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

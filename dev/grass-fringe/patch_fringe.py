"""index.html: the grass fringe over mountain / forest edges that face grass (same as Godot's board_view.gd)."""
import base64, sys
P, PNG = sys.argv[1], sys.argv[2]
s = open(P).read()
uri = 'data:image/png;base64,' + base64.b64encode(open(PNG, 'rb').read()).decode()
if '/*GRASS_FRINGE*/' in s:   # re-run: swap the picture only
    a = s.index('/*GRASS_FRINGE*/const GRASS_FRINGE="'); b = s.index('"', a + 37)
    s = s[:a + 37] + uri + s[b:]
else:
    a = 'const GND_R=HR+.3;'
    assert s.count(a) == 1
    s = s.replace(a, a + '\n/*GRASS_FRINGE*/const GRASS_FRINGE="' + uri + '";   // grass creeping over mountain / forest edges (2026-11-17); 164x56, edge 128 px, 18 px past each corner, 12 px outward', 1)
    a = "    for(const k of ['mountain','forest','fern','water']) d+=img('s-'+k,HEX_TERRAIN.soft[k],sw,sh,0); }"
    assert s.count(a) == 1
    s = s.replace(a, a + "\n  { const px=HR/128; d+=`<image id=\"gfr\" href=\"${GRASS_FRINGE}\" x=\"${(-82*px).toFixed(3)}\" y=\"${(-12*px).toFixed(3)}\" width=\"${(164*px).toFixed(3)}\" height=\"${(56*px).toFixed(3)}\" preserveAspectRatio=\"none\"/>`; }", 1)
    a = "let h='', marks='', castles='', tops='', walls='', trees='', grs='', terr='', own='', bord={};"
    assert s.count(a) == 1
    s = s.replace(a, a.replace("bord={};", "bord={}, fringe='';"), 1)
    a = "    if(whole) terr+=`<use href=\"#s-${whole}\" x=\"${sx}\" y=\"${sy}\"/>`;"
    assert s.count(a) == 1
    s = s.replace(a, a + """
    if(whole==='mountain'||whole==='forest') nbrDirs(i).forEach((j,k)=>{   // grass edge on the sides that face grass
      const n=j>=0?S.tiles[j]:null; if(!n||n.terrain!=='plain'||n.forest||n.fern||n.castle||castleGnd(n)) return;
      const [x0,y0]=hexV(cx,cy,HR,k), [x1,y1]=hexV(cx,cy,HR,k+1), mx=(x0+x1)/2, my=(y0+y1)/2, l=Math.hypot(x1-x0,y1-y0), m=Math.hypot(cx-mx,cy-my);
      fringe+=`<use href="#gfr" transform="matrix(${((x1-x0)/l).toFixed(4)} ${((y1-y0)/l).toFixed(4)} ${((cx-mx)/m).toFixed(4)} ${((cy-my)/m).toFixed(4)} ${mx.toFixed(2)} ${my.toFixed(2)})"/>`; });""", 1)
    a = "$('#terr').innerHTML=terr;"
    assert s.count(a) == 1
    s = s.replace(a, "$('#terr').innerHTML=terr+fringe;", 1)
open(P, 'w').write(s)
print('patched')

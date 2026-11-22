"""Ethan, 2026-11-22: the map is part of the background. The map layer covers the whole screen (under the cards, buttons and
numbers box). Zoomed out it shows the board exactly where it was; zooming in (pinch, wheel, + -) fills the whole screen.
Views are still worked out for the board's own area (vbUser / the hex zoom) and then widened to the screen by toFull().
Usage: python3 patch_fullmap.py index.html (after the other board-hud patches)"""
import sys
P = sys.argv[1]; s = open(P).read()
def rep(a, b):
    global s; assert s.count(a) == 1, a[:80]; s = s.replace(a, b)
# views: area view -> whole-screen view
rep("function vbFor(id){\n  if(id==null) return vbUser();", """// a view meant for the board's own area, widened to the whole screen (the map layer covers it all)
function toFull(v){
  const bd=$('.board'), app=$('#app'); if(!bd||!app||!bd.offsetWidth) return v;
  const bw=bd.offsetWidth, bh=bd.offsetHeight, s=Math.min(bw/v[2],bh/v[3]);
  return [v[0]-(bd.offsetLeft+(bw-v[2]*s)/2)/s, v[1]-(bd.offsetTop+(bh-v[3]*s)/2)/s, app.clientWidth/s, app.clientHeight/s];
}
function vbFor(id){ return toFull(vbArea(id)); }
function vbArea(id){
  if(id==null) return vbUser();""")
rep("  const wrap=$('.mapwrap'), W=wrap.clientWidth||400, H=wrap.clientHeight||300, k=Math.min(W/w,H/h);",
    "  const bd=$('.board'), W=bd.offsetWidth||400, H=bd.offsetHeight||300, k=Math.min(W/w,H/h);   // the board's own area")
# zoom/pan go through vbFor(null)
rep("  cancelAnimationFrame(_vbAnim); setVB(vbUser());", "  cancelAnimationFrame(_vbAnim); setVB(vbFor(null));")
rep("      moved=true; UZ.cx=drag.cx-(b.x-a.x); UZ.cy=drag.cy-(b.y-a.y); setVB(vbUser()); } });", "      moved=true; UZ.cx=drag.cx-(b.x-a.x); UZ.cy=drag.cy-(b.y-a.y); setVB(vbFor(null)); } });")
rep("  if(sx!=null){ const p=svgPt(sx,sy); px=p.x; py=p.y; fx=(px-v[0])/v[2]; fy=(py-v[1])/v[3]; }",
    "  if(sx!=null){ const p=svgPt(sx,sy); px=p.x; py=p.y; fx=(px-v[0])/v[2]; fy=(py-v[1])/v[3]; }   // fx/fy can be outside 0..1: the map now runs under the cards")
# the numbers box measures against the board's own area
rep("const A=area(), bw=box.offsetWidth, bh=box.offsetHeight, vb=[VB_X,VB_Y,VB_W,VB_H], mw=wrap.clientWidth, mh=wrap.clientHeight, k=Math.min(mw/vb[2],mh/vb[3]);\n      const x0=wrap.offsetLeft+wrap.clientLeft+(mw-vb[2]*k)/2, y0=wrap.offsetTop+wrap.clientTop+(mh-vb[3]*k)/2;",
    "const A=area(), bw=box.offsetWidth, bh=box.offsetHeight, vb=[VB_X,VB_Y,VB_W,VB_H], bd=$('.board'), mw=bd.offsetWidth, mh=bd.offsetHeight, k=Math.min(mw/vb[2],mh/vb[3]);\n      const x0=bd.offsetLeft+(mw-vb[2]*k)/2, y0=bd.offsetTop+(mh-vb[3]*k)/2;")
# after every layout change the whole-screen view follows the board's area
rep("  else st.classList.remove('headroom');\n  if(_zoomHex!=null) placeBubbles(true);\n}",
    "  else st.classList.remove('headroom');\n  try{ if(_mapReady) setVB(_zoomHex!=null?vbFor(_zoomHex):vbFor(null)); }catch(e){}   // the map layer is the whole screen: keep the board in its place\n  if(_zoomHex!=null) placeBubbles(true);\n}")
# styles: the map layer covers the whole game screen, under everything else
anchor = "#map{touch-action:none}"
i = s.index(anchor)
s = s[:i] + """/* the map is the background (Ethan, 2026-11-22): its layer covers the whole screen; the board's area just says where it sits */
.board{height:var(--maph)}
.board .mapwrap,#stage.short .board .mapwrap{position:absolute;inset:0;width:auto;height:auto;max-width:none;z-index:0}
#app .side{position:relative;z-index:3}
""" + s[i:]
open(P, 'w').write(s); print('ok')

# no + and - buttons (Ethan): pinch with two fingers, or the mouse wheel
s = open(P).read()
a = '<button class="ghost sh-z" data-head="zin" aria-label="Zoom in" title="Zoom in">＋</button><button class="ghost sh-z" data-head="zout" aria-label="Zoom out" title="Zoom out"${UZ.k>1?\'\':\' disabled\'}>−</button>'
assert s.count(a) == 1
s = s.replace(a, '')
open(P, 'w').write(s); print('ok2')

# the cards column is solid now that the map runs under it
s = open(P).read()
a = "#app .side{position:relative;z-index:3}"
assert s.count(a) == 1
s = s.replace(a, a + "\n#app .side-head,#app .bigcard,#app .handlist .gcard{background:linear-gradient(180deg,#261e15,#16110c)}")
open(P, 'w').write(s); print('ok3')

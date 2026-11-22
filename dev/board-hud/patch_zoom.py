"""Ethan, 2026-11-22: smaller maps take more of the screen, and you can zoom into parts of the bigger maps.
- The random 2-player board is framed to its hexes (its empty grid corners used to be part of the frame).
- Zoom: pinch (touch), mouse wheel, or the + and - buttons in the top-right bar; drag to move around while zoomed in.
  vbFor(null) returns the zoomed view, so the build/recruit zoom returns to it; a tap after a drag doesn't count as a tap.
Usage: python3 patch_zoom.py index.html (after patch_solo.py)"""
import sys
P = sys.argv[1]; s = open(P).read()
def rep(a, b):
    global s; assert s.count(a) == 1, a[:80]; s = s.replace(a, b)
# 1) frame the random 2-player board to its hexes too
rep("  if(np===2){ VB_X=VB_M; VB_Y=VB_M; VB_W=BOARD_W-2*VB_M; VB_H=BOARD_H-2*VB_M; }\n  else {   // the 3-player hexagon leaves the grid's corners empty: frame just the hexes",
    "  {   // frame just the hexes (the 3-player hexagon and the 2-player board both leave grid corners empty)")
# 2) the player's own zoom
rep("function vbFor(id){\n  if(id==null) return [VB_X,VB_Y,VB_W,VB_H];", """// your own zoom (pinch, wheel, the + and - buttons): k is how far in, cx/cy the middle of the view in board units
const UZ={k:1,cx:0,cy:0}, UZ_MAX=4;
function vbUser(){
  if(UZ.k<=1.001){ UZ.k=1; return [VB_X,VB_Y,VB_W,VB_H]; }
  const w=VB_W/UZ.k, h=VB_H/UZ.k, x=Math.max(VB_X,Math.min(VB_X+VB_W-w,UZ.cx-w/2)), y=Math.max(VB_Y,Math.min(VB_Y+VB_H-h,UZ.cy-h/2));
  UZ.cx=x+w/2; UZ.cy=y+h/2; return [x,y,w,h];
}
function vbFor(id){
  if(id==null) return vbUser();""")
rep("  if(S&&S.map){ VOID=new Set(", "  try{ UZ.k=1; }catch(e){}   // a new board starts zoomed out\n  if(S&&S.map){ VOID=new Set(")
# the numbers box measures against the whole board, not the zoomed view
rep("const A=area(), bw=box.offsetWidth, bh=box.offsetHeight, vb=vbFor(null),", "const A=area(), bw=box.offsetWidth, bh=box.offsetHeight, vb=[VB_X,VB_Y,VB_W,VB_H],")
rep("    const pad=(r,b)=>{ VB_W+=r-STATS_PAD.r; VB_H+=b-STATS_PAD.b; STATS_PAD.r=r; STATS_PAD.b=b; setVB(vbFor(null)); fitStage(); };",
    "    const pad=(r,b)=>{ VB_W+=r-STATS_PAD.r; VB_H+=b-STATS_PAD.b; STATS_PAD.r=r; STATS_PAD.b=b; if(_zoomHex==null) setVB(vbFor(null)); fitStage(); };")
# buttons
rep('<button class="ghost" data-head="help" aria-label="How to play">?</button>',
    '<button class="ghost sh-z" data-head="zin" aria-label="Zoom in" title="Zoom in">＋</button><button class="ghost sh-z" data-head="zout" aria-label="Zoom out" title="Zoom out"${UZ.k>1?\'\':\' disabled\'}>−</button><button class="ghost" data-head="help" aria-label="How to play">?</button>')
rep("  if(k==='full') toggleFull();", "  if(k==='zin'||k==='zout'){ zoomBy(k==='zin'?1.5:1/1.5); return; }\n  if(k==='full') toggleFull();")
# gestures
rep("$('#map').addEventListener('click',e=>{", r"""// zooming: in or out by f around a point on screen (the middle of the view if none)
function zoomBy(f,sx,sy){
  if(_zoomHex!=null||!S) return;   // the build/recruit view is zoomed already
  const svg=$('#map'), v=vbUser(); let px=v[0]+v[2]/2, py=v[1]+v[3]/2, fx=.5, fy=.5;
  if(sx!=null){ const p=svgPt(sx,sy); px=p.x; py=p.y; fx=(px-v[0])/v[2]; fy=(py-v[1])/v[3]; }
  const k=Math.max(1,Math.min(UZ_MAX,UZ.k*f)), w=VB_W/k, h=VB_H/k;
  UZ.k=k; UZ.cx=px-fx*w+w/2; UZ.cy=py-fy*h+h/2;
  cancelAnimationFrame(_vbAnim); setVB(vbUser());
  const zo=$('[data-head="zout"]'); if(zo) zo.disabled=UZ.k<=1;
}
function svgPt(x,y){ const svg=$('#map'), p=svg.createSVGPoint(); p.x=x; p.y=y; return p.matrixTransform(svg.getScreenCTM().inverse()); }
{ const svg=$('#map'), pts=new Map(); let drag=null, pinch=null, moved=false;
  svg.addEventListener('pointerdown',e=>{ pts.set(e.pointerId,{x:e.clientX,y:e.clientY}); moved=false;
    if(pts.size===1){ drag={x:e.clientX,y:e.clientY,m:svg.getScreenCTM().inverse(),cx:UZ.cx,cy:UZ.cy}; }
    if(pts.size===2){ const [a,b]=[...pts.values()]; pinch={d:Math.hypot(a.x-b.x,a.y-b.y)}; drag=null; } });
  svg.addEventListener('pointermove',e=>{ if(!pts.has(e.pointerId)) return; pts.set(e.pointerId,{x:e.clientX,y:e.clientY});
    if(_zoomHex!=null) return;
    if(pinch&&pts.size===2){ const [a,b]=[...pts.values()], d=Math.hypot(a.x-b.x,a.y-b.y); if(pinch.d>0&&Math.abs(d-pinch.d)>2){ zoomBy(d/pinch.d,(a.x+b.x)/2,(a.y+b.y)/2); pinch.d=d; moved=true; } return; }
    if(drag&&UZ.k>1){ const P=(x,y)=>{ const p=svg.createSVGPoint(); p.x=x; p.y=y; return p.matrixTransform(drag.m); }, a=P(drag.x,drag.y), b=P(e.clientX,e.clientY);
      if(!moved&&Math.hypot(e.clientX-drag.x,e.clientY-drag.y)<7) return;
      moved=true; UZ.cx=drag.cx-(b.x-a.x); UZ.cy=drag.cy-(b.y-a.y); setVB(vbUser()); } });
  const up=e=>{ pts.delete(e.pointerId); if(pts.size<2) pinch=null; if(!pts.size) drag=null; };
  svg.addEventListener('pointerup',up); svg.addEventListener('pointercancel',up);
  svg.addEventListener('click',e=>{ if(moved){ e.stopPropagation(); e.preventDefault(); moved=false; } },true);   // a drag or pinch isn't a tap on a hex
  svg.addEventListener('wheel',e=>{ if(_zoomHex!=null) return; e.preventDefault(); zoomBy(Math.exp(-e.deltaY*.0018),e.clientX,e.clientY); },{passive:false});
}
$('#map').addEventListener('click',e=>{""")
# touch: the map handles pinch itself
a = "/* the box's close button, and the small round button that brings it back */"
i = s.index(a)
s = s[:i] + "#map{touch-action:none}   /* pinch and drag zoom the map (Ethan, 2026-11-22) */\n.sh-btns .sh-z{min-width:2em;font-weight:800}\n" + s[i:]
open(P, 'w').write(s); print('ok')

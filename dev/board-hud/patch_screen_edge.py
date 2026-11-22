"""Ethan, 2026-11-22: no square frame round the map; the numbers box sits against the screen's own edges, in the corner
of the map side that hides the least of the map. If every corner would hide hexes, the board's frame is widened by the
box's size (right or below, whichever keeps the board bigger). Everything is measured in layout pixels, so it also works
when the screen is turned sideways. Usage: python3 patch_screen_edge.py index.html (after patch_corner.py)"""
import sys
P = sys.argv[1]; s = open(P).read()
def rep(a, b):
    global s; assert s.count(a) == 1, a[:80]; s = s.replace(a, b)
# the box leaves the map's frame and joins the page
rep('<div id="bldov" class="bldov" hidden></div><section class="stats" id="stats" aria-label="Your empire"></section></div>',
    '<div id="bldov" class="bldov" hidden></div></div>')
rep('    <div class="side-body" id="panel"></div>\n  </aside>', '    <div class="side-body" id="panel"></div>\n  </aside>\n  <section class="stats" id="stats" aria-label="Your empire"></section>')
# no frame round the map; the box is a free-standing plate
rep(".board .mapwrap{border-color:#120c06;box-shadow:0 0 0 2px var(--edge),0 0 0 4px #120c06,0 .6em 1.4em rgba(0,0,0,.6)}",
    """.board .mapwrap,#stage.short .board .mapwrap{border:0;box-shadow:none;background:transparent;border-radius:0}   /* no frame round the map (Ethan) */
#stats{right:auto;bottom:auto;left:0;top:0;border:2px solid var(--edge)!important;border-radius:4px!important;box-shadow:0 0 0 2px var(--outline),0 .3em .8em rgba(0,0,0,.5)!important;z-index:4}
#stats.mini{margin:0;border-radius:50%!important}""")
# the placement, in layout pixels against the map side of the screen
a = s.index("function placeStats(){")
b = s.index("try{ new ResizeObserver(()=>requestAnimationFrame(placeStats))", a)
s = s[:a] + r"""function placeStats(){
  const box=$('#stats'), app=$('#app'), wrap=$('.board .mapwrap'), side=$('#app .side');
  if(!box||!app||!wrap||!side||!S||_placing||!box.offsetWidth) return;
  if(_zoomHex!=null) return;   // zoomed in on a hex: leave the box where it is
  _placing=true;
  try{
    const ap=getComputedStyle(app), px=v=>parseFloat(v)||0, tall=$('#stage').classList.contains('tall'), M=6;
    const area=()=>{ const L=px(ap.paddingLeft), T=px(ap.paddingTop), R=app.clientWidth-px(ap.paddingRight), B=app.clientHeight-px(ap.paddingBottom);
      return tall?{l:L,t:T,r:R,b:side.offsetTop-px(ap.rowGap)}:{l:L,t:T,r:side.offsetLeft-(px(ap.columnGap)||12),b:B}; };
    const measure=()=>{
      const A=area(), bw=box.offsetWidth, bh=box.offsetHeight, vb=vbFor(null), mw=wrap.clientWidth, mh=wrap.clientHeight, k=Math.min(mw/vb[2],mh/vb[3]);
      const x0=wrap.offsetLeft+wrap.clientLeft+(mw-vb[2]*k)/2, y0=wrap.offsetTop+wrap.clientTop+(mh-vb[3]*k)/2;
      const hexes=[]; S.tiles.forEach((t,i)=>{ if(t.terrain==='void') return; const [cx,cy]=hexCenter(i), x=x0+(cx-vb[0])*k, y=y0+(cy-vb[1])*k;
        hexes.push([x-HH/2*k,y-HR*k,x+HH/2*k,y+HR*k]); });
      const cover=(x,y)=>hexes.reduce((n,h)=>{ const ix=Math.min(x+bw,h[2])-Math.max(x,h[0]), iy=Math.min(y+bh,h[3])-Math.max(y,h[1]); return n+(ix>0&&iy>0?ix*iy:0); },0);
      const spots=[[A.r-bw-M,A.b-bh-M],[A.l+M,A.b-bh-M],[A.r-bw-M,A.t+M],[A.l+M,A.t+M]];
      let best=spots[0], bv=Infinity; for(const sp of spots){ const v=cover(sp[0],sp[1]); if(v<bv-bw*bh*.02){ bv=v; best=sp; } }
      return {x:best[0],y:best[1],frac:bv/(bw*bh),bw,bh,k}; };
    const put=m=>{ box.style.left=Math.round(m.x)+'px'; box.style.top=Math.round(m.y)+'px'; };
    const pad=(r,b)=>{ VB_W+=r-STATS_PAD.r; VB_H+=b-STATS_PAD.b; STATS_PAD.r=r; STATS_PAD.b=b; setVB(vbFor(null)); fitStage(); };
    const key=_shapeKey+'|'+innerWidth+'x'+innerHeight+'|'+box.offsetWidth+'x'+box.offsetHeight+'|'+statsHidden;
    if(key===STATS_PAD.key){ put(measure()); return; }
    if(STATS_PAD.r||STATS_PAD.b) pad(0,0);
    let m=measure();
    if(m.frac>.005&&!statsHidden){   // every corner would hide hexes: make room beside the board, right or below
      const pr=(m.bw+2*M)/m.k, pb=(m.bh+2*M)/m.k;
      pad(pr,0); const a1=measure(); pad(0,pb); const a2=measure();
      if(a1.frac<a2.frac-.01||(Math.abs(a1.frac-a2.frac)<=.01&&a1.k>a2.k)) pad(pr,0);
      m=measure();
    }
    put(m); STATS_PAD.key=_shapeKey+'|'+innerWidth+'x'+innerHeight+'|'+box.offsetWidth+'x'+box.offsetHeight+'|'+statsHidden;
  } finally { _placing=false; }
}
""" + s[b:]
open(P, 'w').write(s); print('ok')

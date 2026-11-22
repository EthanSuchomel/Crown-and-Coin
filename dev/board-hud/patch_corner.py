"""Ethan, 2026-11-22: on some hand-made maps the numbers box covered hexes. After the board is drawn (and whenever it
changes size) the box measures how much of the map each corner would cover and sits in the clearest one: bottom-right
first, then bottom-left, top-right, top-left. Usage: python3 patch_corner.py index.html"""
import sys
P = sys.argv[1]; s = open(P).read()
def rep(a, b):
    global s; assert s.count(a) == 1, a[:80]; s = s.replace(a, b)
a = "#stage.short .stats{"
i = s.index(a)
s = s[:i] + """/* the box moves to the corner that covers the least of the map (placeStats) */
.stats.c-bl{right:auto;left:0;border-right:2px solid var(--edge);border-left:0;box-shadow:2px -2px 0 0 var(--outline);border-radius:0 3px 0 0}
.stats.c-tr{bottom:auto;top:0;border-bottom:2px solid var(--edge);border-top:0;box-shadow:-2px 2px 0 0 var(--outline);border-radius:0 0 0 3px}
.stats.c-tl{right:auto;left:0;bottom:auto;top:0;border-right:2px solid var(--edge);border-bottom:2px solid var(--edge);border-left:0;border-top:0;box-shadow:2px 2px 0 0 var(--outline);border-radius:0 0 3px 0}
""" + s[i:]
rep("  const m=HM-VB_M; VB_X=x0-m; VB_Y=y0-m; VB_W=x1-x0+2*m; VB_H=y1-y0+2*m;\n}\n// the board's shape follows the game",
    "  const m=HM-VB_M; VB_X=x0-m; VB_Y=y0-m; VB_W=x1-x0+2*m; VB_H=y1-y0+2*m;\n  try{ STATS_PAD.r=0; STATS_PAD.b=0; STATS_PAD.key=''; }catch(e){}   // a fresh frame: no room kept for the numbers box yet\n}\n// the board's shape follows the game")
rep("  try{ _mapReady=false; }catch(e){}   // the board's outline is drawn again for the new size",
    "  try{ STATS_PAD.r=0; STATS_PAD.b=0; STATS_PAD.key=''; }catch(e){}   // a fresh frame: no room kept for the numbers box yet\n  try{ _mapReady=false; }catch(e){}   // the board's outline is drawn again for the new size")
rep("function render(){renderHead();renderStats();renderMap();", """// The numbers box (Ethan, 2026-11-22: it hid hexes on some maps). It sits in the corner that covers the least of the map
// (bottom-right, bottom-left, top-right, top-left). If every corner would hide hexes, the board's frame is widened by the
// box's size, to the right or below, whichever keeps the board bigger, and the box sits in that empty strip.
const STATS_PAD={r:0,b:0,key:''};
let _placing=false;
function placeStats(){
  const box=$('#stats'), wrap=box&&box.parentElement, svg=$('#map'); if(!box||!wrap||!svg||!box.offsetWidth||_placing||!S) return;
  _placing=true;
  try{
    const measure=()=>{ const W=wrap.getBoundingClientRect(), sc=W.width/(wrap.offsetWidth||1)||1, bw=box.offsetWidth*sc, bh=box.offsetHeight*sc;
      const hexes=[...svg.querySelectorAll('g.cell > polygon')].map(p=>p.getBoundingClientRect());
      const cover=(x,y)=>hexes.reduce((n,r)=>{ const ix=Math.min(x+bw,r.right)-Math.max(x,r.left)-1, iy=Math.min(y+bh,r.bottom)-Math.max(y,r.top)-1; return n+(ix>0&&iy>0?ix*iy:0); },0);
      const spots=[['c-br',W.right-bw,W.bottom-bh],['c-bl',W.left,W.bottom-bh],['c-tr',W.right-bw,W.top],['c-tl',W.left,W.top]];
      let best=spots[0], bv=Infinity; for(const sp of spots){ const v=cover(sp[1],sp[2]); if(v<bv-bw*bh*.02){ bv=v; best=sp; } }
      return {best:best[0],frac:bv/(bw*bh),bw,bh,W}; };
    const setCorner=c=>['c-br','c-bl','c-tr','c-tl'].forEach(k=>box.classList.toggle(k,k===c&&k!=='c-br'));
    const pad=(r,b)=>{ VB_W+=r-STATS_PAD.r; VB_H+=b-STATS_PAD.b; STATS_PAD.r=r; STATS_PAD.b=b; setVB(vbFor(null)); fitStage(); };
    const key=_shapeKey+'|'+innerWidth+'x'+innerHeight+'|'+box.offsetWidth+'x'+box.offsetHeight+'|'+(_zoomHex!=null);
    if(_zoomHex!=null){ setCorner(measure().best); return; }   // zoomed in on a hex: just pick a corner
    if(key===STATS_PAD.key){ setCorner(STATS_PAD.r||STATS_PAD.b?'c-br':measure().best); return; }
    if(STATS_PAD.r||STATS_PAD.b) pad(0,0);
    const m=measure();
    if(m.frac<=.04){ setCorner(m.best); STATS_PAD.key=key; return; }
    // no clear corner: keep a strip for the box, to the right or below, whichever leaves the board bigger
    const ppu=()=>{ const r=svg.getBoundingClientRect(); return Math.min(r.width/VB_W,r.height/VB_H); };
    const u=ppu(), pr=(m.bw+6)/u, pb=(m.bh+6)/u;
    pad(pr,0); const sR=ppu(); pad(0,pb); const sB=ppu();
    if(sR>sB) pad(pr,0);
    setCorner('c-br');
    STATS_PAD.key=_shapeKey+'|'+innerWidth+'x'+innerHeight+'|'+box.offsetWidth+'x'+box.offsetHeight+'|false';
  } finally { _placing=false; }
}
try{ new ResizeObserver(()=>requestAnimationFrame(placeStats)).observe(document.getElementById('map')); }catch(e){}
function render(){renderHead();renderStats();renderMap();requestAnimationFrame(placeStats);""")
open(P, 'w').write(s); print('ok')

# ---- a close button (Ethan, 2026-11-22): hide the box; a small round button in its corner brings it back (remembered)
s = open(P).read()
def rep2(a, b):
    global s; assert s.count(a) == 1, a[:80]; s = s.replace(a, b)
rep2("""function renderStats(){
  const me=S.players[0], myth=isMyth(0), cur1=myth?'magic':'coin';""", """let statsHidden=false; try{ statsHidden=localStorage.getItem('cc-stats-hidden')==='1'; }catch(e){}
function renderStats(){
  const box=$('#stats'); box.classList.toggle('mini',statsHidden);
  if(statsHidden){ box.innerHTML=`<button class="st-open" data-stats="open" title="Show your numbers" aria-label="Show your numbers (coins, units, materials, castles)"><span class="px px-coin" aria-hidden="true"></span></button>`; return; }
  const me=S.players[0], myth=isMyth(0), cur1=myth?'magic':'coin';""")
rep2("""  $('#stats').innerHTML=`
    <span class="st inc" """, """  $('#stats').innerHTML=`<button class="st-x" data-stats="close" title="Hide" aria-label="Hide your numbers">×</button>
    <span class="st inc" """)
rep2("""$('#stats').addEventListener('click',e=>{ if(e.target.closest('button[data-head="trade"]')) openTrade(); });""",
     """$('#stats').addEventListener('click',e=>{ if(e.target.closest('button[data-head="trade"]')) openTrade();
  const sb=e.target.closest('button[data-stats]'); if(sb){ statsHidden=sb.dataset.stats==='close'; try{ localStorage.setItem('cc-stats-hidden',statsHidden?'1':'0'); }catch(_){} renderStats(); requestAnimationFrame(placeStats); } });""")
rep2("const key=_shapeKey+'|'+innerWidth+'x'+innerHeight+'|'+box.offsetWidth+'x'+box.offsetHeight+'|'+(_zoomHex!=null);",
     "const key=_shapeKey+'|'+innerWidth+'x'+innerHeight+'|'+box.offsetWidth+'x'+box.offsetHeight+'|'+(_zoomHex!=null)+'|'+statsHidden;")
rep2("STATS_PAD.key=_shapeKey+'|'+innerWidth+'x'+innerHeight+'|'+box.offsetWidth+'x'+box.offsetHeight+'|false';",
     "STATS_PAD.key=_shapeKey+'|'+innerWidth+'x'+innerHeight+'|'+box.offsetWidth+'x'+box.offsetHeight+'|false|'+statsHidden;")
rep2("    if(m.frac<=.04){ setCorner(m.best); STATS_PAD.key=key; return; }",
     "    if(m.frac<=.04||statsHidden){ setCorner(m.best); STATS_PAD.key=key; return; }   // hidden: the small button never takes room from the board")
a = "/* the box moves to the corner that covers the least of the map (placeStats) */"
i = s.index(a)
s = s[:i] + """/* the box's close button, and the small round button that brings it back */
.stats .st-x{position:absolute;top:.1em;right:.15em;pointer-events:auto;width:1.35em;height:1.35em;padding:0;display:flex;align-items:center;justify-content:center;
  font-size:1em;line-height:1;border-radius:50%;background:transparent;border:0;box-shadow:none;color:var(--lichen)}
.stats .st-x:hover{color:var(--bone);background:rgba(255,255,255,.08)}
.stats:not(.mini){padding-right:1.7em}
.stats.mini{padding:.25em;border-radius:50%!important;border:2px solid var(--edge)!important;box-shadow:0 0 0 2px var(--outline)!important;margin:.35em;background:linear-gradient(180deg,#3a3125,#211a12)}
.stats .st-open{pointer-events:auto;width:2em;height:2em;padding:0;border-radius:50%;display:flex;align-items:center;justify-content:center;background:transparent;border:0;box-shadow:none}
.stats .st-open .px{width:1.3em;height:1.3em}
""" + s[i:]
open(P, 'w').write(s); print('ok2')

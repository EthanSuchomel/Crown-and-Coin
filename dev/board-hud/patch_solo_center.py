"""Ethan, 2026-11-22: on a phone the map ended its turn-change slide off-centre and then jumped. The strip kept for the
numbers box (below or beside the board) changed only at the end. Now the end layout's strip is worked out before the
slide starts (without drawing) and eased in together with the board, so the board stays centred all the way.
Usage: python3 patch_solo_center.py index.html (after patch_solo_smooth.py)"""
import sys
P = sys.argv[1]; s = open(P).read()
def rep(a, b):
    global s; assert s.count(a) == 1, a[:80]; s = s.replace(a, b)
rep("""  cancelAnimationFrame(_soloAnim);
  if(!on) st.classList.remove('solo','headroom');   // the buttons go back above the cards straight away, and fade in with them
  const t0=SOLO_T, D=520, start=performance.now();""", """  cancelAnimationFrame(_soloAnim);
  if(!on) st.classList.remove('solo','headroom');   // the buttons go back above the cards straight away, and fade in with them
  const t0=SOLO_T, D=520, start=performance.now();
  // work out the end layout's room for the numbers box now (nothing is drawn in between), then ease towards it
  const p0={r:STATS_PAD.r,b:STATS_PAD.b}; let p1=p0, key1='';
  try{ SOLO_T=goal; if(on) st.classList.add('solo'); fitStage(); STATS_PAD.key=''; _soloSim=true; placeStats(); _soloSim=false;
    p1={r:STATS_PAD.r,b:STATS_PAD.b}; key1=STATS_PAD.key; }
  finally{ _soloSim=false; if(on) st.classList.remove('solo','headroom'); SOLO_T=t0; padTo(p0.r,p0.b); fitStage(); }
  _soloRun=true;""")
rep("""    SOLO_T=t0+(goal-t0)*e;
    if(k>=1){ SOLO_T=goal; if(on) st.classList.add('solo'); }
    fitStage(); placeStats();   // the numbers box glides along with the board""", """    SOLO_T=t0+(goal-t0)*e;
    padTo(p0.r+(p1.r-p0.r)*e, p0.b+(p1.b-p0.b)*e);
    if(k>=1){ SOLO_T=goal; padTo(p1.r,p1.b); if(on) st.classList.add('solo'); _soloRun=false; STATS_PAD.key=key1; }
    fitStage(); placeStats();   // the numbers box glides along with the board""")
rep("let SOLO_T=0, _soloAnim=0;", "let SOLO_T=0, _soloAnim=0, _soloRun=false, _soloSim=false;")
# placeStats: while the slide runs, only move the box (the room for it is being eased by setSolo)
rep("    if(key===STATS_PAD.key){ put(measure()); return; }", "    if(key===STATS_PAD.key||_soloRun){ put(measure()); return; }")
# a helper that sets the room kept for the box
rep("function placeStats(){", """function padTo(r,b){ VB_W+=r-STATS_PAD.r; VB_H+=b-STATS_PAD.b; STATS_PAD.r=r; STATS_PAD.b=b; if(_zoomHex==null&&_mapReady) setVB(vbFor(null)); }
function placeStats(){""")
open(P, 'w').write(s); print('ok')

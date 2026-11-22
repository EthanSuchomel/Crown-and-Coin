"""Ethan, 2026-11-22: when the cards go away the map grew too much and too suddenly. Now the map grows at most about 20%
and the change is a smooth half-second slide: the cards column narrows and fades while the board grows, then the buttons
fade in top-right (and back again when your turn comes). SOLO_T runs 0..1 through fitStage.
Usage: python3 patch_solo_smooth.py index.html (after patch_zoom.py)"""
import sys
P = sys.argv[1]; s = open(P).read()
def rep(a, b):
    global s; assert s.count(a) == 1, a[:80]; s = s.replace(a, b)
SOLO_GROW = "1.2"
# sizing: interpolate between your-turn and their-turn sizes
rep("""  if(tall){
    // upright: the board spans the width, but leaves at least about 40% of the height, and room for a full card, below it
    mw=sw-padL-padR; mh=mw*R;
    const maxH=st.classList.contains('solo')?sh-padT-padB:Math.max(sh*.3,Math.min(sh*.58, sh-padT-padB-statsH-.6*fs-20*fs)); if(mh>maxH){ mh=maxH; mw=mh/R; }
  } else {
    // the map column is 66% of the width; the board is as large as fits in it, and no taller than the screen allows
    const colW=st.classList.contains('solo')?sw-padL-padR:(sw-padL-padR-gap)*MAP_SHARE;   // not your turn: the whole width
    mh=Math.min(sh-padT-padB-statsH, colW*R); mw=Math.min(colW, mh/R);
  }""", """  const t=SOLO_T, fit=(W,H)=>{ let w=W, h=w*R; if(h>H){ h=H; w=h/R; } return [w,h]; };
  if(tall){
    // upright: the board spans the width, but leaves at least about 40% of the height, and room for a full card, below it
    const [w0,h0]=fit(sw-padL-padR, Math.max(sh*.3,Math.min(sh*.58, sh-padT-padB-statsH-.6*fs-20*fs)));
    const [w1,h1]=fit(Math.min(sw-padL-padR,w0*SOLO_GROW), Math.min(sh-padT-padB,h0*SOLO_GROW));   // not your turn: a little bigger
    mw=w0+(w1-w0)*t; mh=h0+(h1-h0)*t;
    $('#app').style.rowGap=t?(.6*fs*(1-t))+'px':'';
  } else {
    // the map column is 66% of the width; the board is as large as fits in it, and no taller than the screen allows
    const full=sw-padL-padR, sideW=(full-gap)*(1-MAP_SHARE);
    const [w0,h0]=fit((full-gap)*MAP_SHARE, sh-padT-padB-statsH);
    const [w1,h1]=fit(Math.min(full,w0*SOLO_GROW), Math.min(sh-padT-padB,h0*SOLO_GROW));   // not your turn: a little bigger
    mw=w0+(w1-w0)*t; mh=h0+(h1-h0)*t;
    const ap2=$('#app').style;   // the cards column narrows away as t goes to 1
    if(t){ ap2.gridTemplateColumns=`minmax(0,1fr) ${(sideW*(1-t)).toFixed(1)}px`; ap2.columnGap=(gap*(1-t)).toFixed(1)+'px'; } else { ap2.gridTemplateColumns=''; ap2.columnGap=''; }
  }
  { const sd=$('#app .side'); if(sd){ sd.style.opacity=t>0&&t<1?Math.max(0,1-2*t).toFixed(3):''; sd.style.pointerEvents=t>0&&t<1?'none':''; } }""")
rep("const VB_M=HM-1.4, MAP_SHARE=.66;", f"const VB_M=HM-1.4, MAP_SHARE=.66, SOLO_GROW={SOLO_GROW};\nlet SOLO_T=0, _soloAnim=0;   // 0 your turn (cards shown) .. 1 their turn (cards away)")
# the switch: a half-second ease
rep("""function setSolo(){
  const st=$('#stage'), on=!!(S&&!S.over&&S.current!==0&&!ui.info);
  if(st.classList.contains('solo')===on) return;
  st.classList.toggle('solo',on); fitStage(); requestAnimationFrame(placeStats);
}""", """function setSolo(){
  const st=$('#stage'), on=!!(S&&!S.over&&S.current!==0&&!ui.info), goal=on?1:0;
  if(st.dataset.soloGoal===String(goal)) return;
  st.dataset.soloGoal=String(goal);
  cancelAnimationFrame(_soloAnim);
  if(!on) st.classList.remove('solo','headroom');   // the buttons go back above the cards straight away, and fade in with them
  const t0=SOLO_T, D=520, start=performance.now();
  const quick=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
  const step=now=>{ const k=quick?1:Math.min(1,(now-start)/D), e=k<.5?2*k*k:1-Math.pow(-2*k+2,2)/2;
    SOLO_T=t0+(goal-t0)*e;
    if(k>=1){ SOLO_T=goal; if(on) st.classList.add('solo'); }
    fitStage(); placeStats();   // the numbers box glides along with the board
    if(k<1) _soloAnim=requestAnimationFrame(step); else requestAnimationFrame(placeStats); };
  _soloAnim=requestAnimationFrame(step);
}""")
# their-turn styles: the grid stays as it is (the cards column is 0 wide); the buttons fade in
rep("""#stage.solo #app,#stage.solo.tall #app{grid-template-columns:minmax(0,1fr);grid-template-rows:minmax(0,1fr) var(--maph,70vh) minmax(0,1fr);grid-template-areas:"." "board" "."}
""", "")
rep("#stage.solo .side{position:absolute;top:max(.6em,var(--sa-t,0px));right:max(.8em,var(--sa-r,0px));z-index:5}",
    "#stage.solo .side{position:absolute;top:max(.6em,var(--sa-t,0px));right:max(.8em,var(--sa-r,0px));z-index:5;animation:soloIn .3s ease-out}\n@keyframes soloIn{from{opacity:0;transform:translateY(-.3em)}to{opacity:1;transform:none}}\n@media (prefers-reduced-motion: reduce){#stage.solo .side{animation:none}}")
open(P, 'w').write(s); print('ok')

"""Ethan, 2026-11-22: (1) the top-right bar is just the buttons (Full, ?, Log, New): no "Turn x · your move" line.
(2) While it isn't your turn the cards column goes away and the map fills the screen; the buttons float top-right.
Usage: python3 patch_solo.py index.html (after patch_screen_edge.py)"""
import sys
P = sys.argv[1]; s = open(P).read()
def rep(a, b):
    global s; assert s.count(a) == 1, a[:80]; s = s.replace(a, b)
rep("  $('#sidehead').innerHTML=`<span class=\"sh-turn\">${turn}</span>\n    <span class=\"sh-btns\">",
    "  // just the buttons (Ethan, 2026-11-22); whose turn it is stays in the page title for screen readers\n  document.title=(S.current===0&&!S.over?'Your turn · ':'')+'Crown & Coin';\n  setSolo();\n  $('#sidehead').innerHTML=`<span class=\"sh-btns\">")
rep(".sh-btns{display:flex;gap:.35em}", ".sh-btns{display:flex;gap:.35em;margin-left:auto}")
rep("function renderHead(){", """// not your turn: the cards column goes away and the map fills the screen (Ethan, 2026-11-22)
function setSolo(){
  const st=$('#stage'), on=!!(S&&!S.over&&S.current!==0&&!ui.info);
  if(st.classList.contains('solo')===on) return;
  st.classList.toggle('solo',on); fitStage(); requestAnimationFrame(placeStats);
}
function renderHead(){""")
rep("    const colW=(sw-padL-padR-gap)*MAP_SHARE;", "    const colW=st.classList.contains('solo')?sw-padL-padR:(sw-padL-padR-gap)*MAP_SHARE;   // not your turn: the whole width")
rep("  st.style.setProperty('--mapw',Math.floor(mw)+'px'); st.style.setProperty('--maph',Math.floor(mh)+'px');\n  if(_zoomHex!=null) placeBubbles(true);\n}",
    """  st.style.setProperty('--mapw',Math.floor(mw)+'px'); st.style.setProperty('--maph',Math.floor(mh)+'px');
  // not your turn: the buttons float top-right; keep room above the board only if the board would reach under them
  if(st.classList.contains('solo')){ const hd=$('#sidehead'), need=hd&&(sw-mw)/2<hd.offsetWidth+padR+.4*fs&&(sh-mh)/2<hd.offsetHeight+padT+.4*fs;
    if(!!need!==st.classList.contains('headroom')){ st.classList.toggle('headroom',!!need); return fitStage(); } }
  else st.classList.remove('headroom');
  if(_zoomHex!=null) placeBubbles(true);
}""")
# in tall (upright) layout the board may take the cards' room too
rep("    const maxH=Math.max(sh*.3,Math.min(sh*.58, sh-padT-padB-statsH-.6*fs-20*fs)); if(mh>maxH){ mh=maxH; mw=mh/R; }",
    "    const maxH=st.classList.contains('solo')?sh-padT-padB:Math.max(sh*.3,Math.min(sh*.58, sh-padT-padB-statsH-.6*fs-20*fs)); if(mh>maxH){ mh=maxH; mw=mh/R; }")
# the numbers box measures against the whole width then
rep("      return tall?{l:L,t:T,r:R,b:side.offsetTop-px(ap.rowGap)}:{l:L,t:T,r:side.offsetLeft-(px(ap.columnGap)||12),b:B}; };",
    "      if($('#stage').classList.contains('solo')) return {l:L,t:T,r:R,b:B};\n      return tall?{l:L,t:T,r:R,b:side.offsetTop-px(ap.rowGap)}:{l:L,t:T,r:side.offsetLeft-(px(ap.columnGap)||12),b:B}; };")
rep("    const key=_shapeKey+'|'+innerWidth+'x'+innerHeight+'|'+box.offsetWidth+'x'+box.offsetHeight+'|'+statsHidden;",
    "    const solo=$('#stage').classList.contains('solo'), key=_shapeKey+'|'+innerWidth+'x'+innerHeight+'|'+box.offsetWidth+'x'+box.offsetHeight+'|'+statsHidden+'|'+solo;")
rep("    put(m); STATS_PAD.key=_shapeKey+'|'+innerWidth+'x'+innerHeight+'|'+box.offsetWidth+'x'+box.offsetHeight+'|'+statsHidden;",
    "    put(m); STATS_PAD.key=_shapeKey+'|'+innerWidth+'x'+innerHeight+'|'+box.offsetWidth+'x'+box.offsetHeight+'|'+statsHidden+'|'+solo;")
# styles: one column, the buttons floating top-right, room kept above the map for them
anchor = "/* the box's close button, and the small round button that brings it back */"
i = s.index(anchor)
s = s[:i] + """/* not your turn: one column, the buttons float top-right (Ethan, 2026-11-22) */
#stage.solo #app,#stage.solo.tall #app{grid-template-columns:minmax(0,1fr);grid-template-rows:minmax(0,1fr) var(--maph,70vh) minmax(0,1fr);grid-template-areas:"." "board" "."}
#stage.solo.headroom #app{padding-top:calc(max(.6em,var(--sa-t,0px)) + 2.4em)}   /* only when the buttons would sit on the board */
#stage.solo .side{position:absolute;top:max(.6em,var(--sa-t,0px));right:max(.8em,var(--sa-r,0px));z-index:5}
#stage.solo .side-body{display:none}
#stage.solo .side-head{padding:.3em}
#stage.solo .sh-btns{flex-direction:column;align-items:stretch;gap:.3em}   /* a narrow column, so it fits beside the board */
""" + s[i:]
open(P, 'w').write(s); print('ok')

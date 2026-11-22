"""Ethan, 2026-11-22: on a phone the board sat right of centre. With the game turned sideways on an upright phone, the
notch margin (game's left) is bigger than the home-bar margin (game's right), so centring between them pushed the board
right. The left and right safe margins are now both the larger one, so the board is centred on the screen itself.
Usage: python3 patch_even_margins.py index.html"""
import sys
P = sys.argv[1]; s = open(P).read()
a = "  const ins=safeInsets(), m=rot?{t:ins.r,r:ins.b,b:ins.l,l:ins.t}:ins;\n"
assert s.count(a) == 1
s = s.replace(a, a + "  { const lr=Math.max(m.l,m.r); m.l=lr; m.r=lr; }   // the same margin left and right, so the board is centred on the screen itself (Ethan)\n")
open(P, 'w').write(s); print('ok')

# the room above the board for the buttons only switches on during their turn (switching it off again could loop)
s = open(P).read()
a = "    if(!!need!==st.classList.contains('headroom')){ st.classList.toggle('headroom',!!need); return fitStage(); } }"
assert s.count(a) == 1
s = s.replace(a, "    if(need&&!st.classList.contains('headroom')){ st.classList.add('headroom'); return fitStage(); } }   // once on, it stays on until your turn")
open(P, 'w').write(s); print('ok2')

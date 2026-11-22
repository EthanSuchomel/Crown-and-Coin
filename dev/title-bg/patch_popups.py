"""Ethan, 2026-11-22: the setup screen's pop-ups (faction info, difficulty) themed like the setup screen: dark iron
panel, bronze trim, Cinzel headings in parchment, bronze-framed difficulty tiles with a gold ring on the picked one.
Usage: python3 patch_popups.py index.html"""
import sys
P = sys.argv[1]; s = open(P).read()
def rep(a, b):
    global s; assert s.count(a) == 1, a[:80]; s = s.replace(a, b)
rep("""m.innerHTML=`<div class="sheet"><h3>Difficulty</h3>""", """m.innerHTML=`<div class="sheet fsx-lvsheet"><h3>Difficulty</h3>""")
rep("""<div class="btns"><button class="primary" data-fsx="close">Close</button></div></div>`;""", """<div class="btns"><button data-fsx="close">Close</button></div></div>`;""")
anchor = "#scrTitle .ts-btns button:not(.primary)::before,#scrTitle .ts-btns button:not(.primary)::after{background:#a88a55}"
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + r"""
/* the setup screen's pop-ups (faction info, difficulty), themed the same way */
.fsx-sheet,.fsx-lvsheet{--cz:"Cinzel","Trajan Pro","Palatino Linotype",Palatino,Georgia,serif;--brz:#6e5226;--parch:#e4d6b4;
  background:linear-gradient(180deg,rgba(34,27,19,.97),rgba(18,14,10,.97))!important;border:2px solid var(--brz)!important;border-radius:4px!important;
  box-shadow:0 0 0 2px #120c06,inset 0 0 0 1px rgba(233,185,73,.12),inset 0 0 3em rgba(0,0,0,.4),0 1em 2.5em rgba(0,0,0,.7)!important;color:#d8cba9}
.fsx-sheet h2,.fsx-sheet h3,.fsx-lvsheet h3{font-family:var(--cz)!important;font-weight:700;letter-spacing:.04em;text-shadow:0 1px 0 #000,0 0 .5em rgba(0,0,0,.6)}
.fsx-sheet h2{font-size:1.6em}
.fsx-sheet h3,.fsx-lvsheet h3{color:var(--parch)!important}
.fsx-sheet h3{border-bottom:1px solid rgba(110,82,38,.7);padding-bottom:.2em;margin-top:1em}
.fsx-sheet p,.fsx-sheet ul,.fsx-sheet li,.fsx-lvsheet .hint{color:#cdbf9c}
.fsx-sheet li b,.fsx-sheet p b{color:#f0e2bd}
.fsx-sheet .utable th{color:var(--parch);border-bottom-color:var(--brz);font-family:var(--cz);letter-spacing:.03em}
.fsx-sheet .utable td{border-bottom-color:rgba(110,82,38,.45);color:#cdbf9c}
.fsx-sheet .utable td.ut-n{color:#f0e2bd}
.fsx-sheet .btns,.fsx-lvsheet .btns{border-top:1px solid rgba(110,82,38,.6)}
.fsx-lvsheet .btns{padding-top:.7em;margin-top:.5em}
.fsx-sheet .btns button,.fsx-lvsheet .btns button{flex:0 0 auto;margin-left:auto;min-width:8em;font-family:var(--cz);font-weight:700;letter-spacing:.05em;color:var(--parch);
  background:linear-gradient(180deg,#3b3226,#1d1710);border:2px solid var(--brz);box-shadow:0 0 0 2px #120c06,inset 0 1px 0 rgba(255,236,190,.15),0 .25em .6em rgba(0,0,0,.5);text-shadow:0 1px 0 #000}
.fsx-sheet .btns button:hover,.fsx-lvsheet .btns button:hover{background:linear-gradient(180deg,#4a3f2f,#241c13)}
.fsx-lvsheet .fsx-lv button{font-family:var(--cz);background:linear-gradient(180deg,rgba(52,42,30,.9),rgba(24,19,13,.92));border:2px solid #4f3b1c;box-shadow:0 0 0 2px #120c06;color:var(--parch)}
.fsx-lvsheet .fsx-lv button b{font-weight:700;letter-spacing:.04em;font-size:1.1em}
.fsx-lvsheet .fsx-lv button small{font-family:var(--font-body);color:#bfae88}
.fsx-lvsheet .fsx-lv button:hover{border-color:#8a6a34}
.fsx-lvsheet .fsx-lv button[aria-pressed="true"]{border-color:#d9b25a;background:linear-gradient(180deg,rgba(64,50,30,.95),rgba(30,23,14,.95));box-shadow:0 0 0 2px #120c06,0 0 0 3px rgba(233,185,73,.75),0 0 .8em rgba(255,190,70,.2)}
.fsx-lvsheet .fsx-lv button[aria-pressed="true"] b{color:#f6e7bf}""")
open(P, 'w').write(s); print('ok')

"""Ethan, 2026-11-22: the game screen themed like the home and setup screens. The green panels turn dark iron with bronze
trim and parchment text (the colour tokens change), a plain black background behind the board, card names,
headings and pop-up titles use Cinzel, buttons are iron plates and the main buttons a softer gold plate. The map is unchanged.
Usage: python3 patch_game_style.py index.html"""
import sys
P = sys.argv[1]; s = open(P).read()
anchor = ".fsx-lvsheet .fsx-lv button[aria-pressed=\"true\"] b{color:#f6e7bf}"
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + r"""
/* ===== the game screen, themed like the home screen (Ethan, 2026-11-22) ===== */
:root{--night:#100d09;--moss:#1e1811;--moss-2:#2b2319;--edge:#5e4622;--bone:#ece0c0;--lichen:#b9a984;--cz:"Cinzel","Trajan Pro","Palatino Linotype",Palatino,Georgia,serif}
body{background-image:none}
body,#stage{background:#000}   /* plain black behind the board (Ethan) */
#app{position:relative;z-index:1}
/* panels: dark iron with bronze trim */
.side-head,.bigcard,.handlist .gcard,.hexinfo,.stats,.sheet,.uinfo{background:linear-gradient(180deg,rgba(38,30,21,.94),rgba(22,17,12,.95))}
.side-head,.bigcard,.handlist .gcard,.hexinfo,.sheet{border-color:var(--edge)!important}
.stats{border-color:var(--edge)}
.board .mapwrap{border-color:#120c06;box-shadow:0 0 0 2px var(--edge),0 0 0 4px #120c06,0 .6em 1.4em rgba(0,0,0,.6)}
.handlist .gcard:hover:not(:disabled){background:linear-gradient(180deg,rgba(50,40,28,.96),rgba(28,22,15,.96))}
.fav{background:rgba(12,9,6,.75);border-right-color:var(--edge)}
/* headings in the carved serif */
.bc-name,.sh-title,.sheet h3,.handlist .gcard .cname,.tname,.big,.fs-info h2,.keyhead,.ui-head .bc-name{font-family:var(--cz);font-weight:700;letter-spacing:.03em}
.sheet h3{color:#f0e2bd}
.bc-step .row-label,.row-label{font-family:var(--cz);font-weight:700;letter-spacing:.03em;color:#e4d6b4}
.sh-turn b{font-family:var(--cz)}
/* buttons: iron plates; the main ones a softer gold plate */
button{background:linear-gradient(180deg,#3a3125,#211a12);border-color:#120c06;box-shadow:0 0 0 1px var(--edge) inset,inset 0 -3px 0 rgba(0,0,0,.35),inset 0 2px 0 rgba(255,236,190,.08)}
button:hover:not(:disabled){background:linear-gradient(180deg,#4a3e2e,#2a2117)}
button.primary{font-family:var(--cz);font-weight:700;letter-spacing:.04em;color:#2a1805;background:linear-gradient(180deg,#f6e2a4 0%,#e2b75a 40%,#b98432 100%);border-color:#4a300c;
  box-shadow:inset 0 2px 0 rgba(255,255,255,.45),inset 0 -3px 0 rgba(90,55,10,.5)}
button.primary:hover:not(:disabled){background:linear-gradient(180deg,#fbeab8 0%,#e9c26a 40%,#c48f3a 100%)}
.bub{background:linear-gradient(180deg,#3a3125,#211a12);border-color:#d9c79c}
.bub.off{background:#17120c;border-color:var(--edge)}
.bub:not(.off):hover{background:linear-gradient(180deg,#4a3e2e,#2a2117)}
.cp-sw,.cp-sw:hover:not(:disabled){background:var(--sw)}
.bc-acts li.on{background:rgba(12,9,6,.7);border-color:#d9c79c}
.bc-acts .num,.gcard .num{background:rgba(12,9,6,.8);border-color:var(--edge)}
.modal{background:rgba(6,4,2,.72)}
.mvrow,.battle,.note,.cdetail,.ui-stat{background:rgba(12,9,6,.65);border-color:var(--edge)}
details.log{background:rgba(22,17,12,.92)}""")
open(P, 'w').write(s); print('ok')

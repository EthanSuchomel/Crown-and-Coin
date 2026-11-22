"""Ethan, 2026-11-22: the setup screen (the three tabs) themed like the new home screen: the battle painting blurred and
darkened behind it, iron-and-gold tabs and plates, Cinzel headings, a gold Start plate. Usage: python3 patch_setup_style.py index.html"""
import sys
P = sys.argv[1]; s = open(P).read()
anchor = "#stage.short #scrTitle .ts-inner{gap:.5em}"
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + r"""
/* ===== the setup screen, themed like the home screen (Ethan, 2026-11-22) ===== */
#scrFaction{--cz:"Cinzel","Trajan Pro","Palatino Linotype",Palatino,Georgia,serif;--gd:#e9b949;--gd2:#c9952f;--iron:rgba(22,17,12,.7);overflow:hidden;background:#0c0a07!important}
#scrFaction::before{content:"";position:absolute;inset:-14px;background:url(title_battle.jpg) center/cover no-repeat;filter:blur(2px) brightness(.62) saturate(1.1);z-index:0}
#scrFaction::after{content:"";position:absolute;inset:0;background:radial-gradient(ellipse at 50% 45%,rgba(10,8,5,.15),rgba(10,8,5,.6));z-index:0;pointer-events:none}
#scrFaction .fsx{position:relative;z-index:1}
/* tabs: iron plates, the open one gold */
#scrFaction .fsx-tab{font-family:var(--cz);font-weight:700;letter-spacing:.05em;color:#e8d3a0;background:linear-gradient(180deg,#3b3226,#1d1710);border:2px solid #8a6424;
  box-shadow:0 0 0 2px #120c06,inset 0 1px 0 rgba(255,236,190,.15),0 .3em .7em rgba(0,0,0,.5);text-shadow:0 1px 0 #000}
#scrFaction .fsx-tab:hover:not(:disabled){background:linear-gradient(180deg,#4a3f2f,#241c13)}
#scrFaction .fsx-tab .n{border-color:var(--gd);color:var(--gd)}
#scrFaction .fsx-tab[aria-selected="true"]{color:#2a1805;text-shadow:0 1px 0 rgba(255,240,200,.6);background:linear-gradient(180deg,#fff0bd 0%,#f4cf6b 25%,#dca43a 60%,#a9721f 100%);border-color:#5a3a0e;
  box-shadow:0 0 0 2px #120c06,inset 0 2px 0 rgba(255,255,255,.5),0 0 1em rgba(255,180,60,.3)}
#scrFaction .fsx-tab[aria-selected="true"] .n{border-color:#2a1805;color:#2a1805}
/* the panel: dark iron with a gold trim */
#scrFaction .fsx-body{background:var(--iron);border:2px solid var(--gd2);box-shadow:0 0 0 2px #120c06,inset 0 0 0 1px rgba(233,185,73,.25),inset 0 0 2.5em rgba(0,0,0,.45),0 .6em 1.6em rgba(0,0,0,.6);
  -webkit-backdrop-filter:blur(4px);backdrop-filter:blur(4px);border-radius:4px}
#scrFaction .fsx-l{font-family:var(--cz);font-weight:700;letter-spacing:.05em;color:var(--gd);text-shadow:0 1px 0 #000,0 0 .5em rgba(0,0,0,.6)}
#scrFaction .fsx-l small{font-family:var(--font-body);letter-spacing:0;color:#bfae88}
#scrFaction .hint{color:#bfae88}
/* tiles: bronze frames that glow gold when picked */
#scrFaction .fsx-fac,#scrFaction .fsx-map{background:linear-gradient(180deg,rgba(52,42,30,.9),rgba(24,19,13,.92));border:2px solid #6b4d1c;box-shadow:0 0 0 2px #120c06,inset 0 1px 0 rgba(255,236,190,.1)}
#scrFaction .fsx-fac:hover:not(:disabled),#scrFaction .fsx-map:hover:not(:disabled){border-color:#a77a2c}
#scrFaction .fsx-fac b{font-family:var(--cz);font-weight:700;letter-spacing:.03em;text-shadow:0 1px 0 #000}
#scrFaction .fsx-map b{font-family:var(--cz);font-weight:700;color:#f0dcaa}
#scrFaction .fsx-fac small,#scrFaction .fsx-map small{color:#bfae88}
#scrFaction .fsx-fac[aria-pressed="true"],#scrFaction .fsx-map[aria-pressed="true"]{border-color:#ffe08a;background:linear-gradient(180deg,rgba(84,64,30,.95),rgba(34,26,14,.95));
  box-shadow:0 0 0 2px #120c06,0 0 0 4px var(--gd),0 0 1.3em rgba(255,190,70,.45)}
#scrFaction .fsx-rival,#scrFaction .fsx-rules{background:rgba(12,9,6,.6);border:1px solid #6b4d1c}
#scrFaction .fsx-rules b{color:#f0dcaa}
#scrFaction .cp-sw{box-shadow:0 0 0 2px #6b4d1c}
#scrFaction .cp-sw[aria-pressed="true"]{box-shadow:0 0 0 2px #120c06,0 0 0 4px var(--gd)}
#scrFaction .cp-n{color:#f0dcaa}
/* small buttons (Players 2/3, info, difficulty) and Back/Next: iron plates */
#scrFaction .op-b,#scrFaction .fsx-more,#scrFaction .fsx-foot button:not(.primary){font-family:var(--cz);font-weight:700;letter-spacing:.04em;color:#f3d58a;
  background:linear-gradient(180deg,#3b3226,#1d1710);border:2px solid var(--gd2);box-shadow:0 0 0 2px #120c06,inset 0 1px 0 rgba(255,236,190,.15),0 .25em .6em rgba(0,0,0,.5);text-shadow:0 1px 0 #000}
#scrFaction .op-b[aria-pressed="true"]{color:#2a1805;text-shadow:none;background:linear-gradient(180deg,#fff0bd,#e0ab45 60%,#a9721f);border-color:#5a3a0e}
#scrFaction .fsx-more small{font-family:var(--font-body);letter-spacing:0;color:#bfae88;font-weight:500}
#scrFaction .fsx-more .ic{background:linear-gradient(180deg,#fff0bd,#dca43a);color:#2a1805;box-shadow:0 0 0 1.5px #120c06}
#scrFaction .fsx-foot .sum{color:#d9c79c;text-shadow:0 1px 2px #000}
#scrFaction .fsx-foot .sum b{font-family:var(--cz)}
#scrFaction .fsx-foot button.primary{font-family:var(--cz);font-weight:700;letter-spacing:.06em;color:#2a1805;text-shadow:0 1px 0 rgba(255,240,200,.6);
  background:linear-gradient(180deg,#fff0bd 0%,#f4cf6b 22%,#dca43a 55%,#a9721f 100%);border:2px solid #5a3a0e;border-radius:4px;
  box-shadow:0 0 0 2px #120c06,inset 0 2px 0 rgba(255,255,255,.55),inset 0 -3px 0 rgba(90,55,10,.55),0 0 1.1em rgba(255,180,60,.35),0 .35em .8em rgba(0,0,0,.6)}
#scrFaction .fsx-foot button.primary:hover{background:linear-gradient(180deg,#fff6d2 0%,#f8da80 22%,#e6b14a 55%,#b67d26 100%)}""")
open(P, 'w').write(s); print('ok')

"""Ethan, 2026-11-22: tone the gold down. Gold stays for the title, the Start buttons and the picked tile's ring; tabs,
panel trim, headings and the other plates go to dark bronze and parchment. Appends overrides after the setup styles.
Usage: python3 patch_tone_down.py index.html"""
import sys
P = sys.argv[1]; s = open(P).read()
anchor = "#scrFaction .fsx-foot button.primary:hover{background:linear-gradient(180deg,#fff6d2 0%,#f8da80 22%,#e6b14a 55%,#b67d26 100%)}"
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + r"""
/* less gold (Ethan, 2026-11-22): bronze trims and parchment text; gold only on Start and on what's picked */
#scrFaction{--brz:#6e5226;--parch:#e4d6b4}
#scrFaction .fsx-tab{color:var(--parch);border-color:var(--brz)}
#scrFaction .fsx-tab .n{border-color:#9c8156;color:#cdbb92}
#scrFaction .fsx-tab[aria-selected="true"]{color:#f6e7bf;text-shadow:0 1px 0 #000;background:linear-gradient(180deg,#5a4a33,#2c2318);border-color:#b8913f;
  box-shadow:0 0 0 2px #120c06,inset 0 1px 0 rgba(255,236,190,.22),inset 0 -3px 0 rgba(233,185,73,.55),0 .3em .7em rgba(0,0,0,.5)}
#scrFaction .fsx-tab[aria-selected="true"] .n{border-color:#e9c66a;color:#e9c66a}
#scrFaction .fsx-body{border-color:var(--brz);box-shadow:0 0 0 2px #120c06,inset 0 0 2.5em rgba(0,0,0,.45),0 .6em 1.6em rgba(0,0,0,.6)}
#scrFaction .fsx-l{color:var(--parch)}
#scrFaction .fsx-fac,#scrFaction .fsx-map{border-color:#4f3b1c}
#scrFaction .fsx-fac[aria-pressed="true"],#scrFaction .fsx-map[aria-pressed="true"]{border-color:#d9b25a;background:linear-gradient(180deg,rgba(64,50,30,.95),rgba(30,23,14,.95));
  box-shadow:0 0 0 2px #120c06,0 0 0 3px rgba(233,185,73,.75),0 0 .8em rgba(255,190,70,.2)}
#scrFaction .fsx-map b{color:var(--parch)}
#scrFaction .cp-sw[aria-pressed="true"]{box-shadow:0 0 0 2px #120c06,0 0 0 4px #e4d6b4}
#scrFaction .op-b,#scrFaction .fsx-more,#scrFaction .fsx-foot button:not(.primary){color:var(--parch);border-color:var(--brz)}
#scrFaction .op-b[aria-pressed="true"]{color:#f6e7bf;text-shadow:0 1px 0 #000;background:linear-gradient(180deg,#5a4a33,#2c2318);border-color:#d9b25a}
#scrFaction .fsx-more .ic{background:#cdbb92}
/* the home screen's other buttons: bronze edges and parchment letters; the title and Start stay gold */
#scrTitle .ts-btns button:not(.primary){color:var(--parch,#e4d6b4);border-color:#6e5226}
#scrTitle .ts-btns button:not(.primary)::before,#scrTitle .ts-btns button:not(.primary)::after{background:#a88a55}""")
open(P, 'w').write(s); print('ok')

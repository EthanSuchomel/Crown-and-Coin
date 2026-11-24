"""Ethan, 2026-11-23: "get rid of the description under the card when playing the action" and "the cards are now taking up
too much space can you squish the card info box a little more at least on the computer".
- The playing card no longer shows the hint paragraphs and the building/upgrade key under its actions (the notes, picks,
  material line, buttons and warnings stay).
- On a wide screen (a computer: 1150 px and up) the cards column takes about a quarter of the width instead of a third,
  and the cards are a little tighter. Tablets and phones keep the old share.
Usage: python3 patch_slim.py index.html"""
import sys
P = sys.argv[1]; s = open(P).read()
def rep(a, b, n=1):
    global s; c = s.count(a); assert c == n, (c, a[:90]); s = s.replace(a, b)
rep("const VB_M=HM-1.4, MAP_SHARE=.66, SOLO_GROW=1.2;",
    "const VB_M=HM-1.4, SOLO_GROW=1.2;\nlet MAP_SHARE=.66;   // the map's share of the width: .75 on a computer-sized screen, so the cards column is slimmer (Ethan, 2026-11-23)")
rep("  st.classList.toggle('short',sh<520);",
    "  st.classList.toggle('short',sh<520);\n  MAP_SHARE=!rot&&!tall&&sw>=1150?.75:.66; st.classList.toggle('wide',MAP_SHARE>.7);\n  $('#app').style.setProperty('--mfr',Math.round(MAP_SHARE*100)+'fr'); $('#app').style.setProperty('--sfr',Math.round((1-MAP_SHARE)*100)+'fr');")
rep("grid-template-columns:minmax(0,66fr) minmax(0,34fr);   /* the map gets about 2/3 of the width */",
    "grid-template-columns:minmax(0,var(--mfr,66fr)) minmax(0,var(--sfr,34fr));   /* the map gets 2/3 of the width (3/4 on a computer) */")
anchor = ".fsx-lvsheet .fsx-lv button[aria-pressed=\"true\"] b{color:#f6e7bf}"
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + r"""
/* no description under the playing card (Ethan, 2026-11-23): the hints and the building key go; notes, picks and buttons stay */
.bigcard.playing .bc-step>p.hint,.bigcard.playing .bc-step>ul.bkey,.bigcard.playing .bc-step>.mythpanel>p.hint{display:none}
/* a slimmer cards column on a computer: tighter cards */
#stage.wide .handlist{gap:.45em}
#stage.wide .bigcard .bc-head{margin-bottom:.1em}
#stage.wide .bc-acts{gap:.15em}
#stage.wide .bc-acts li{padding-top:.25em;padding-bottom:.25em}
#stage.wide .handlist .gcard .cname{font-size:1em}""")
open(P, 'w').write(s); print('ok')

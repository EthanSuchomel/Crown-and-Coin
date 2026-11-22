"""Ethan, 2026-11-22: the home screen shows a four-faction battle (OpenArt, GPT Image 2.6 Sunburst; Personal Project,
folder 'Art work for game'). title_battle.jpg is it at 1920x1080. A soft dark glow sits behind the title and buttons;
the three small castles over the title are hidden (the painting has all four). Usage: python3 patch_title.py index.html title_battle.jpg
Afterwards the data URI was swapped for url(title_battle.jpg) (the picture sits next to index.html, in sw.js FILES,
and is published with the claude.ai link), because the link page has a 16 MB limit."""
import sys, base64
P, J = sys.argv[1], sys.argv[2]; s = open(P).read()
uri = 'data:image/jpeg;base64,' + base64.b64encode(open(J, 'rb').read()).decode()
a = ".ts-inner{display:flex;flex-direction:column;align-items:center;gap:1.1em;text-align:center}"
assert s.count(a) == 1
s = s.replace(a, a + f"""
/* the home screen's battle painting (Ethan, 2026-11-22) */
#scrTitle{{background-image:radial-gradient(ellipse 34% 46% at 50% 52%,rgba(9,16,11,.62),rgba(9,16,11,.38) 55%,rgba(9,16,11,0) 100%),linear-gradient(rgba(9,16,11,.1),rgba(9,16,11,.25)),url({uri})!important;
  background-size:cover!important;background-position:center!important;background-repeat:no-repeat!important}}
#scrTitle .ts-art{{display:none}}
#scrTitle .ts-title{{text-shadow:.06em .06em 0 var(--outline),0 0 .35em rgba(0,0,0,.85)}}
#scrTitle .ts-ver{{color:var(--bone);opacity:.85;text-shadow:0 1px 2px #000}}
#scrTitle .ts-btns button:not(.primary){{box-shadow:0 0 0 2px var(--outline),0 .25em .6em rgba(0,0,0,.5)}}""")
open(P, 'w').write(s); print('ok')

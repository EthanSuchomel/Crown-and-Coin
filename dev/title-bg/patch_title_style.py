"""Ethan, 2026-11-22: home screen title and buttons themed to the battle painting: carved-gold Cinzel lettering with a
gold divider, a gold-plate Start button and dark iron-and-gold plates for the rest. Cinzel comes from Google Fonts like
Oswald (offline it falls back to a classic serif). Usage: python3 patch_title_style.py index.html"""
import sys
P = sys.argv[1]; s = open(P).read()
def rep(a, b):
    global s; assert s.count(a) == 1, a[:80]; s = s.replace(a, b)
rep("https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&display=swap",
    "https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;900&family=Oswald:wght@400;500;600;700&display=swap")
rep('<h1 class="ts-title">Crown <span>&amp;</span> Coin</h1>',
    '<h1 class="ts-title">Crown <span>&amp;</span> Coin</h1><div class="ts-rule" aria-hidden="true"><i></i><b></b><i></i></div>')
rep("#scrTitle .ts-title{text-shadow:.06em .06em 0 var(--outline),0 0 .35em rgba(0,0,0,.85)}", r"""#scrTitle{--cz:"Cinzel","Trajan Pro","Palatino Linotype",Palatino,Georgia,serif}
#scrTitle .ts-inner{gap:.9em}
/* carved gold letters */
#scrTitle .ts-title{font-family:var(--cz);font-weight:900;letter-spacing:.04em;font-size:clamp(2.4em,calc(var(--H,700px)*.115),5.2em);
  background:linear-gradient(180deg,#fff6d6 0%,#f7d77c 28%,#e0a93a 52%,#a8701c 72%,#f2c862 100%);-webkit-background-clip:text;background-clip:text;color:transparent;
  -webkit-text-stroke:.022em #2a1a06;text-shadow:none;filter:drop-shadow(0 .05em 0 #1a1005) drop-shadow(0 0 .28em rgba(0,0,0,.9)) drop-shadow(0 0 .7em rgba(255,170,60,.25))}
#scrTitle .ts-title span{color:transparent;background:linear-gradient(180deg,#ffd9c9 0%,#f27b52 35%,#b3271c 70%,#e55a33 100%);-webkit-background-clip:text;background-clip:text;font-size:.82em;vertical-align:.06em}
/* a gold rule with a diamond under the title */
.ts-rule{display:flex;align-items:center;gap:.6em;width:min(26em,80%);margin-top:-.35em}
.ts-rule i{flex:1;height:2px;background:linear-gradient(90deg,transparent,#e9b949 40%,#fff1b8 100%);box-shadow:0 0 6px rgba(0,0,0,.8)}
.ts-rule i+b+i,.ts-rule b+i{background:linear-gradient(270deg,transparent,#e9b949 40%,#fff1b8 100%)}
.ts-rule b{width:.7em;height:.7em;transform:rotate(45deg);background:linear-gradient(135deg,#fff1b8,#c98f2a);border:2px solid #2a1a06;box-shadow:0 0 6px rgba(0,0,0,.8)}
/* the buttons: plates of iron and gold */
#scrTitle .ts-btns{gap:.7em;margin-top:.3em}
#scrTitle .ts-btns button{font-family:var(--cz);font-weight:700;letter-spacing:.06em;min-width:12.5em;padding:.6em 1.6em;border-radius:4px;position:relative;
  color:#f3d58a;background:linear-gradient(180deg,#3b3226 0%,#221b13 55%,#17120c 100%);border:2px solid #c9952f;
  box-shadow:0 0 0 2px #120c06,inset 0 0 0 1px rgba(255,226,150,.18),inset 0 2px 0 rgba(255,236,190,.15),0 .35em .8em rgba(0,0,0,.6);text-shadow:0 1px 0 #000;transition:transform .12s,filter .12s}
#scrTitle .ts-btns button:hover:not(:disabled){background:linear-gradient(180deg,#4a3f2f 0%,#2a2118 55%,#1c160e 100%);filter:brightness(1.08)}
#scrTitle .ts-btns button::before,#scrTitle .ts-btns button::after{content:"";position:absolute;top:50%;width:.42em;height:.42em;margin-top:-.21em;transform:rotate(45deg);background:#e9b949;box-shadow:0 0 0 1.5px #120c06}
#scrTitle .ts-btns button::before{left:.55em}
#scrTitle .ts-btns button::after{right:.55em}
#scrTitle .ts-btns button.primary{font-size:1.4em;min-width:9.5em;color:#2a1805;text-shadow:0 1px 0 rgba(255,240,200,.6);
  background:linear-gradient(180deg,#fff0bd 0%,#f4cf6b 22%,#dca43a 55%,#a9721f 100%);border-color:#5a3a0e;
  box-shadow:0 0 0 2px #120c06,inset 0 2px 0 rgba(255,255,255,.55),inset 0 -3px 0 rgba(90,55,10,.55),0 0 1.2em rgba(255,180,60,.35),0 .4em .9em rgba(0,0,0,.6)}
#scrTitle .ts-btns button.primary:hover:not(:disabled){background:linear-gradient(180deg,#fff6d2 0%,#f8da80 22%,#e6b14a 55%,#b67d26 100%)}
#scrTitle .ts-btns button.primary::before,#scrTitle .ts-btns button.primary::after{background:#5a3a0e;box-shadow:0 0 0 1.5px #fff0bd}
#scrTitle .ts-btns button:active:not(:disabled){transform:translateY(1px)}
#scrTitle .ts-btns .ts-full{font-size:.78em;min-width:0;padding:.45em 1.3em;color:#e8d3a0;background:rgba(18,13,8,.72);border-color:rgba(201,149,47,.7)}
#scrTitle .ts-btns .ts-full::before,#scrTitle .ts-btns .ts-full::after{display:none}
#stage.short #scrTitle .ts-btns button{padding:.4em 1.3em}
#stage.short #scrTitle .ts-btns button.primary{font-size:1.2em}
#stage.short #scrTitle .ts-inner{gap:.5em}""")
open(P, 'w').write(s); print('ok')

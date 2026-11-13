"""Ethan, 2026-11-12: no explanations next to a card's actions (tap the action's icon for a box with it), a trophy for
each upgrade in place of the upgrade names, and no win chance in the attack window. Usage: python3 patch_info.py index.html trophy.png"""
import sys, base64
P, TRO = sys.argv[1], sys.argv[2]
s = open(P).read()
def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, a[:100]); s = s.replace(a, b)
uri = 'data:image/png;base64,' + base64.b64encode(open(TRO, 'rb').read()).decode()

# the trophy, and the tap-to-read action icon
rep("const lvPips=l=>", f"""const TROPHY='{uri}';
// a trophy for each upgrade on an action (in place of the upgrade's name)
const trophies=l=>`<span class="tro" title="${{l}} upgrade${{l===1?'':'s'}}" aria-label="${{l}} upgrade${{l===1?'':'s'}}">${{('<img src="'+TROPHY+'" alt="">').repeat(l)}}</span>`;
// an action's icon: tap it for a box explaining the action (with its upgrades)
const actIcon=(pid,cid,i,a)=>`<span class="ainfo" data-ainfo="${{i}}" data-cid="${{cid}}" data-pid="${{pid}}" role="button" tabindex="0" title="What does ${{ACTIONS[a].name}} do?" aria-label="About ${{actName(a,S.players[pid].faction)}}">${{ACTIONS[a].icon}}</span>`;
function openActionInfo(pid,cid,i){{
  const c=cardOf(pid,cid), a=c.actions[i], l=lvlOf(pid,cid,i);
  openInfo(`${{ACTIONS[a].icon}} ${{actName(a,S.players[pid].faction)}}${{l?' '+trophies(l):''}}`,`<p>${{actionDesc(a,pid,l,cid)}}</p>`,[{{label:'Close',primary:true}}]);
}}
document.addEventListener('click',e=>{{ const el=e.target.closest('[data-ainfo]'); if(!el) return; e.preventDefault(); e.stopPropagation();
  openActionInfo(+el.dataset.pid,el.dataset.cid,+el.dataset.ainfo); }},true);
document.addEventListener('keydown',e=>{{ if(e.key!=='Enter'&&e.key!==' ') return; const el=e.target.closest&&e.target.closest('[data-ainfo]'); if(!el) return; e.preventDefault(); e.stopPropagation();
  openActionInfo(+el.dataset.pid,el.dataset.cid,+el.dataset.ainfo); }},true);
const lvPips=l=>""")

# hand cards
rep("return `<span class=\"act\"><span class=\"num\">${i+1}</span>${ACTIONS[a].icon} ${actName(a,S.players[0].faction)}${l?lvPips(l)+`<span class=\"ut\">${upNow(a,0,l,cid)}</span>`:''}</span>`;}",
    "return `<span class=\"act\"><span class=\"num\">${i+1}</span>${actIcon(0,cid,i,a)} ${actName(a,S.players[0].faction)}${l?trophies(l):''}</span>`;}")
# the card filling the column
rep("""    const desc=(step==null||i===step)?`<small>${actionDesc(a,pid,l,cid)}</small>`:'';
    const up=l?`<span class="upl">${lvPips(l)}${upNow(a,pid,l,cid)}</span>`:'';   // applied upgrades, under the action
    return `<li class="${cls}"><span class="num">${i+1}</span><span>${ACTIONS[a].icon}</span><div><b>${actName(a,S.players[pid].faction)}</b>${up}${desc}</div></li>`;""",
"""    // no explanation here (Ethan): tap the icon for it; a trophy for each upgrade
    return `<li class="${cls}"><span class="num">${i+1}</span>${actIcon(pid,cid,i,a)}<div><b>${actName(a,S.players[pid].faction)}</b>${l?trophies(l):''}</div></li>`;""")
rep(".bc-acts li{display:flex;gap:.5em;align-items:flex-start;", ".bc-acts li{display:flex;gap:.5em;align-items:center;")
rep(".upl{display:block;", """.tro{display:inline-flex;gap:1px;margin-left:.35em;vertical-align:-.15em;flex:none}
.tro img{width:1.05em;height:1.05em;image-rendering:pixelated}
.ainfo{display:inline-flex;cursor:pointer;border-radius:50%;flex:none;-webkit-tap-highlight-color:transparent}
.ainfo:hover,.ainfo:focus-visible{outline:2px solid var(--gold);outline-offset:1px}
.sheet h3 .tro img{width:.9em;height:.9em}
.upl{display:block;""")

# no win chance before a battle
rep("""  const odds=()=>{ if(!fight){ $('#mvodds').innerHTML=''; return; }""", """  const odds=()=>{ $('#mvodds').innerHTML=''; return;   // no win chance shown before a battle (Ethan, 2026-11-12)
    if(!fight){ $('#mvodds').innerHTML=''; return; }""")
rep(".mvodds{min-height:1.4em;margin-bottom:.6em;color:var(--lichen)}", ".mvodds{margin-bottom:.6em;color:var(--lichen)}\n.mvodds:empty{display:none}")
open(P, 'w').write(s)
print('ok')
s = open(P).read()
a = "${fvTxt}</p>`,\n      foot:`<button data-act=\"back\">Back</button>"
assert s.count(a) == 1
s = s.replace(a, "${fvTxt} Tap an action's icon to read what it does.</p>`,\n      foot:`<button data-act=\"back\">Back</button>")
open(P, 'w').write(s)

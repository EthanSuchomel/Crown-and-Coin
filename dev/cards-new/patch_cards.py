"""Ethan, 2026-11-23: every faction's five cards get the same actions (simpler, built on units and buildings), card
upgrades off for now, and a one-time swap of a hand card for a reserve card. Same change as the Godot p12_cards.py.
Usage: python3 patch_cards.py index.html"""
import sys, re
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, a[:100]); s = s.replace(a, b)
NEW = ["['move','build','advance']", "['build','advance','recruit']", "['recruit','fortify','move']",
       "['harvest','build','advance']", "['fortify','harvest','advance']"]
for ids in [['stamp','pack','siege','hunt','nest'], ['mobil','deploy','onsl','cons','sprot'],
            ['roam','forage','den','wild','tusks'], ['march','gather','grove','arcan','chan']]:
    for k, cid in enumerate(ids):
        pat = re.compile(r"(\{id:'%s',\s*name:'[^']*',\s*actions:)\[[^\]]*\]" % cid)
        s, n = pat.subn(lambda m: m.group(1) + NEW[k], s, count=1)
        assert n == 1, cid
rep("const FAVORS_PER_UP=2, MAX_UP=3;", "const FAVORS_PER_UP=2, MAX_UP=3;\nconst CARD_UPS_ON=false;   // Ethan, 2026-11-23: card upgrades off while the new cards settle (no favors toward upgrades, no faction card upgrades)")
rep("const upgradeDue=(pid,cid)=>!isMyth(pid)&&", "const upgradeDue=(pid,cid)=>CARD_UPS_ON&&!isMyth(pid)&&")
rep("const cardUps=pid=>isDino(pid)||isRobo(pid)||isMamm(pid);", "const cardUps=pid=>CARD_UPS_ON&&(isDino(pid)||isRobo(pid)||isMamm(pid));")
rep("  if(isMyth(pid)) return '';   // Mythical cards don't upgrade yet\n  // a progress bar", "  if(isMyth(pid)||!CARD_UPS_ON) return '';   // Mythical cards don't upgrade yet (and no card upgrades while they're off)\n  // a progress bar")
rep("    const fvTxt=isMyth(0)?", "    const fvTxt=!CARD_UPS_ON?'':isMyth(0)?")
rep("  P.innerHTML=`<div class=\"handlist\">${me.hand.map(handCard).join('')}</div>`;",
    "  P.innerHTML=`<div class=\"handlist\">${me.hand.map(handCard).join('')}</div><p class=\"reserve\">In reserve: ${me.reserve.map(c=>cardOf(0,c).name).join(', ')}</p>${canSwap(0)?'<button class=\"swapbtn\" data-act=\"swap\">⇄ Swap a card <span class=\"hint\">(once a game)</span></button>':''}`;")
rep("  else if(a==='back'){ ui.pick=null; render(); }", "  else if(a==='back'){ ui.pick=null; render(); }\n  else if(a==='swap') openSwap();")
rep("function playCard(cid){", """// the one-time swap (Ethan, 2026-11-23): once a game, before playing a card, a hand card goes into the reserve and a
// reserve card takes its place
const canSwap=pid=>S&&!S.over&&S.current===pid&&!S.play&&!S.volley&&!S.players[pid].swapped&&S.players[pid].reserve.length>0;
function swapCard(pid,h,r){
  const p=S.players[pid];
  if(!canSwap(pid)||!p.hand.includes(h)||!p.reserve.includes(r)) return false;
  p.hand[p.hand.indexOf(h)]=r; p.reserve[p.reserve.indexOf(r)]=h; p.swapped=true;
  addLog(`${p.name} swap ${cardOf(pid,h).name} for ${cardOf(pid,r).name} (once a game).`,pid);
  return true;
}
function openSwap(from){
  if(!canSwap(0)) return;
  const me=S.players[0], line=c=>`${cardOf(0,c).name} · ${cardOf(0,c).actions.map(a=>actName(a,me.faction)).join(' › ')}`;
  const list=from?me.reserve:me.hand;
  openInfo('Swap a card',`<p>Once a game, before you play a card, you can put a card from your hand into your reserve and take a reserve card in its place.</p><p><b>${from?`Put back ${cardOf(0,from).name}. Take which card?`:'Which card goes back to your reserve?'}</b></p>`,
    list.map(c=>({label:line(c),primary:!!from,fn:()=>{ if(!from) openSwap(c); else if(swapCard(0,from,c)){ ui.pick=null; render(); } }}))
      .concat(from?[{label:'Back',fn:()=>openSwap()}]:[]).concat([{label:'Cancel'}]));
}
function playCard(cid){""")
# How to play
i = s.index("<li><b>Card upgrades.</b>")
s = s[:i] + "<li><b>Swap once.</b> Once a game, before you play a card, you can swap a card in your hand for one in your reserve.</li>\n    <li${CARD_UPS_ON?'':' hidden'}><b>Card upgrades.</b>" + s[i+len("<li><b>Card upgrades.</b>"):]
# a little style for the button
rep(".reserve{font-size:.78em;color:var(--lichen);margin:0}", ".reserve{font-size:.78em;color:var(--lichen);margin:0}\n.swapbtn{margin-top:.5em;align-self:flex-start}")
open(p, 'w', encoding='utf-8').write(s)
print('ok')

"""index.html: the Mythical computer after the 2026-11-17 movement rules (Ethan: on Expert "it didnt capture a castle and it
didnt try and fight me"). It was spending its moves marching its big Minion stacks around its own land (moves were scored
by the size of the stack) and attacking with 1 Minotaur and 1 Minion. Now: Minions count 20% when scoring a march, and
Mages are walked up to castles they can take and along with the army (only Mages take castles)."""
import sys
P = sys.argv[1]; s = open(P).read()
a = "sel=pickUnits(s,n,claim&&n===1), st=armyGold(sel)/3, adv=prog>0?prog*0.4*st:0;"
assert s.count(a) == 1
s = s.replace(a, "sel=pickUnits(s,n,claim&&n===1), st=armyGold(sel)/3, stA=st-(isMyth(pid)?0.8*(sel.minion|0)*UNIT_STATS.minion.cost/3:0), adv=prog>0?prog*0.4*stA:0;   // Minions can't take land: marching them is worth little")
a = """    let v=prog>0?1+adv:-1;
    if(b.castle){const near=enemyNear(b.id,pid,2);"""
assert s.count(a) == 1
s = s.replace(a, """    let v=prog>0?1+adv:-1;
    if(isMyth(pid)&&Object.keys(sel).some(isMage)){   // only Mages take castles: walk them up to one, and along with the army
      if(nbrs(b.id).some(j=>{ const c=S.tiles[j]; return c.castle&&c.owner!==pid&&mythNeed(pid,c)==='mage'; })) v=Math.max(v,6+adv);
      const others=Object.keys(b.army||{}).filter(k=>k!=='minion'&&!isMage(k)).reduce((a,k)=>a+b.army[k],0);
      if(others>=3&&prog>=0) v=Math.max(v,2.5+adv);
    }
    if(b.castle){const near=enemyNear(b.id,pid,2);""")
open(P, 'w').write(s); print('patched')

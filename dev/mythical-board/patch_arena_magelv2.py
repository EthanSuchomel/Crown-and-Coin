"""(Ethan, 2026-11-07) In the arena the Mage level only changes the Mage's lightning and its Minotaur making: Griffins and
Dragons need no level, the Mage limit stays 2, and gold doesn't change with the level. Minotaur chance every 2 s by level:
20%, 30%, 40%, 50% (also for Mages sent from Crown & Coin). Apply to arena.html after patch_arena_magelv.py.
Usage: patch_arena_magelv2.py IN OUT EDITS_JSON"""
import sys, json
s=open(sys.argv[1]).read(); edits=[]
def rep(old,new):
    global s
    assert s.count(old)==1,(s.count(old),old[:80]); s=s.replace(old,new); edits.append({'old_text':old,'new_text':new})
rep("[['mage0',30,5],['mage1',60,6],['mage2',90,7],['mage3',120,7]].forEach(([k,r,d])=>{ TYPES[k]={...TYPES.mage,label:'Mage',range:r,dmg:d,hidden:true,maxN:3}; ORDER.push(k); });",
    "// and each level's chance, every 2 s, to turn a Minion into a Minotaur: 20%, 30%, 40%, 50%\n"
    "[['mage0',30,5,.2],['mage1',60,6,.3],['mage2',90,7,.4],['mage3',120,7,.5]].forEach(([k,r,d,c])=>{ TYPES[k]={...TYPES.mage,label:'Mage',range:r,dmg:d,morph:{...TYPES.mage.morph,chance:c},hidden:true,maxN:3}; ORDER.push(k); });")
rep("const MLV=[2,2], MLV_NOTE=['Lightning reaches a quarter of the field, 5 damage','Half the field, 6 damage; Griffins','Three quarters, 7 damage; Dragons','Whole field, 7 damage; 3 Mages; units 1 gold cheaper'];",
    "const MLV=[2,2], MLV_NOTE=['Lightning: a quarter of the field, 5 damage · Minotaurs 20%','Half the field, 6 damage · Minotaurs 30%','Three quarters, 7 damage · Minotaurs 40%','Whole field, 7 damage · Minotaurs 50%'];")
rep("const capFor=(t,k)=>!mlvOn(t)?capOf(k):k==='mage'?(MLV[t]>=3?3:2):(k==='griffin'&&MLV[t]<1)||(k==='dragon'&&MLV[t]<2)?0:capOf(k);",
    "const capFor=(t,k)=>capOf(k);   // the level only changes the Mages' lightning and Minotaur making")
rep("const lockNote=(t,k)=>mlvOn(t)&&capFor(t,k)===0?' <small class=\"cap\">(Mage level '+(k==='griffin'?1:2)+')</small>':'';", "const lockNote=(t,k)=>'';")
rep("const armyGold=(c,t)=>ORDER.reduce((s,k)=>{ let g=TYPES[k].cost; if(t!=null&&mlvOn(t)){ if(k==='mage') g+=MLV[t]; if(MLV[t]>=3) g=Math.max(1,g-1); } return s+c[k]*g; },0);   // what an army costs (a Mythical side's Mage level counts)",
    "const armyGold=(c,t)=>ORDER.reduce((s,k)=>s+c[k]*TYPES[k].cost,0);   // what an army costs")
rep("<tr><td>Mage (at most 2 per army, 3 at level 3)</td><td>15 gold, +1 a level</td>", "<tr><td>Mage (at most 2 per army)</td><td>15 gold</td>")
rep("<td>Chain lightning: 5 to up to 20 enemies at once. Every 2s, a 20% chance to turn a Minion into a Minotaur</td>",
    "<td>Chain lightning: 5 to 7 (by Mage level) to up to 20 enemies at once. Every 2s, a chance to turn a Minion into a Minotaur: 20% at level 0, 30%, 40%, 50% at level 3</td>")
rep("<td>By Mage level: a quarter of the field (5 damage), half (6), three quarters (7), the whole field (7). Griffins need level 1, Dragons level 2; at level 3 every unit costs 1 gold less. The bolt jumps to the next enemy within about a tenth of the field</td>",
    "<td>By Mage level: a quarter of the field (5 damage), half (6), three quarters (7), the whole field (7). The bolt jumps to the next enemy within about a tenth of the field</td>")
open(sys.argv[2],'w').write(s); json.dump(edits,open(sys.argv[3],'w')); print('magelv2 ok',len(edits))

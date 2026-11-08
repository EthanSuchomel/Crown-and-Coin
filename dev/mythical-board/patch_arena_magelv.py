"""Mage levels in the standalone arena (Ethan, 2026-11-07: "same as the board"). A Mythical side picks a Mage level 0-3:
it sets every Mage's lightning (level 0 a quarter of the field and 5 damage, 1 half and 6, 2 three quarters and 7, 3 the whole
field and 7); Griffins need level 1 and Dragons level 2; level 3 allows 3 Mages. Gold shown: a Mage costs +1 a level, and at
level 3 every unit costs 1 less. Default level 2, so the usual army (1 Griffin, 1 Dragon) still fits. Battles sent from
Crown & Coin are unchanged: there each Mage arrives with its own level (mage0..mage3).
Usage: patch_arena_magelv.py IN OUT EDITS_JSON"""
import sys, json
s=open(sys.argv[1]).read(); edits=[]
def rep(old,new):
    global s
    assert s.count(old)==1,(s.count(old),old[:80]); s=s.replace(old,new); edits.append({'old_text':old,'new_text':new})
rep("let TEAM_FACTION=['Dinosaurs','Robots'];",
    "let TEAM_FACTION=['Dinosaurs','Robots'];\n"
    "// Mage level per side (Mythical only): picked above the army, like the Crown & Coin upgrade\n"
    "const MLV=[2,2], MLV_NOTE=['Lightning reaches a quarter of the field, 5 damage','Half the field, 6 damage; Griffins','Three quarters, 7 damage; Dragons','Whole field, 7 damage; 3 Mages; units 1 gold cheaper'];\n"
    "const mlvOn=t=>!EMB&&TEAM_FACTION[t]==='Mythical';\n"
    "const capFor=(t,k)=>!mlvOn(t)?capOf(k):k==='mage'?(MLV[t]>=3?3:2):(k==='griffin'&&MLV[t]<1)||(k==='dragon'&&MLV[t]<2)?0:capOf(k);\n"
    "const lockNote=(t,k)=>mlvOn(t)&&capFor(t,k)===0?' <small class=\"cap\">(Mage level '+(k==='griffin'?1:2)+')</small>':'';")
rep("const armyGold=c=>ORDER.reduce((s,k)=>s+c[k]*TYPES[k].cost,0);   // what an army costs",
    "const armyGold=(c,t)=>ORDER.reduce((s,k)=>{ let g=TYPES[k].cost; if(t!=null&&mlvOn(t)){ if(k==='mage') g+=MLV[t]; if(MLV[t]>=3) g=Math.max(1,g-1); } return s+c[k]*g; },0);   // what an army costs (a Mythical side's Mage level counts)")
rep("function addUnit(team,key,x,y,entering){\n  const T=TYPES[key], h=T.w*T.ratio;",
    "function addUnit(team,key,x,y,entering){\n  const T=(key==='mage'&&mlvOn(team))?TYPES['mage'+MLV[team]]:TYPES[key], h=T.w*T.ratio;   // a Mage fights at its side's level")
rep("<b class=\"gold\">'+armyGold(COUNTS[team])+' gold</b>", "<b class=\"gold\">'+armyGold(COUNTS[team],team)+' gold</b>")
# the level picker row, and the caps that follow it
rep("      const n=COUNTS[team][key], nm=TYPES[key].label, id='n-'+team+'-'+key;\n      return '<div class=\"step\"><label for=\"'+id+'\">'+nm+(TYPES[key].maxN?' <small class=\"cap\">(max '+TYPES[key].maxN+')</small>':'')+'</label>'+",
    "      const n=COUNTS[team][key], nm=TYPES[key].label, id='n-'+team+'-'+key, cap=capFor(team,key);\n      return '<div class=\"step\"><label for=\"'+id+'\">'+nm+(TYPES[key].maxN?' <small class=\"cap\">(max '+cap+')</small>':'')+lockNote(team,key)+'</label>'+")
rep("min=\"0\" max=\"'+capOf(key)+'\" value=\"'+n+'\">'+", "min=\"0\" max=\"'+cap+'\" value=\"'+n+'\"'+(cap===0?' disabled':'')+'>'+")
rep("(n>=capOf(key)?' disabled':'')+'>+</button></div>';", "(n>=cap?' disabled':'')+'>+</button></div>';")
rep("  v=Math.max(0,Math.min(capOf(k),Math.round(v)||0));", "  v=Math.max(0,Math.min(capFor(t,k),Math.round(v)||0));")
rep("function setFaction(t,fac){",
    "function setMageLevel(t,lv){   // lower levels lock Griffins and Dragons and the third Mage: those units leave the army\n"
    "  MLV[t]=Math.max(0,Math.min(3,lv)); ORDER.forEach(k=>{ if(facOf(k)==='Mythical') COUNTS[t][k]=Math.min(COUNTS[t][k],capFor(t,k)); });\n"
    "  if(!ORDER.some(k=>COUNTS[t][k]>0)) COUNTS[t].minion=1; renderArmy(); build(); }\n"
    "function setFaction(t,fac){")
rep("  const fb=e.target.closest('button[data-fac]'); if(fb){ setFaction(+fb.dataset.ft,fb.dataset.fac); return; }",
    "  const fb=e.target.closest('button[data-fac]'); if(fb){ setFaction(+fb.dataset.ft,fb.dataset.fac); return; }\n"
    "  const ml=e.target.closest('button[data-ml]'); if(ml){ if(!ml.disabled) setMageLevel(+ml.dataset.ml,MLV[+ml.dataset.ml]+(+ml.dataset.d)); return; }")
rep("<tr><td>Mage (at most 2 per army)</td><td>15 gold</td>",
    "<tr><td>Mage (at most 2 per army, 3 at level 3)</td><td>15 gold, +1 a level</td>")
rep("<td>The whole field; the bolt jumps to the next enemy within about a tenth of the field</td>",
    "<td>By Mage level: a quarter of the field (5 damage), half (6), three quarters (7), the whole field (7). Griffins need level 1, Dragons level 2; at level 3 every unit costs 1 gold less. The bolt jumps to the next enemy within about a tenth of the field</td>")
rep("'</button>').join('')+'</div>')+teamKeys(team).map(key=>{",
    "'</button>').join('')+'</div>')+(mlvOn(team)?'<div class=\"step mlv\"><label>Mage level <small class=\"cap\">'+MLV_NOTE[MLV[team]]+'</small></label><button type=\"button\" data-ml=\"'+team+'\" data-d=\"-1\" aria-label=\"Lower Mage level\"'+(MLV[team]<=0?' disabled':'')+'>&minus;</button><output class=\"mlvn\">'+MLV[team]+'</output><button type=\"button\" data-ml=\"'+team+'\" data-d=\"1\" aria-label=\"Raise Mage level\"'+(MLV[team]>=3?' disabled':'')+'>+</button></div>':'')+teamKeys(team).map(key=>{")
rep(".step label{min-width:122px;max-width:140px;line-height:1.15}", ".step label{min-width:122px;max-width:140px;line-height:1.15}.step.mlv{margin-bottom:4px}.step.mlv label{max-width:none;flex:1}.step.mlv label .cap{display:block}.step .mlvn{min-width:2.4em;text-align:center;font-weight:700;font-size:1.1em}")
open(sys.argv[2],'w').write(s); json.dump(edits,open(sys.argv[3],'w')); print('magelv ok',len(edits))

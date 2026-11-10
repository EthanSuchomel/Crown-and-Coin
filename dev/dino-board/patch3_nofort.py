# Dinosaur board rework, step 3: no forts and no trebuchets for the Dinosaurs (the Alamosaurus Guard and the volcano replace them).
import sys,re
p=sys.argv[1]; s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:100]); s=s.replace(a,b)
rep("  if(t.castle&&k!=='market'&&k!=='wh') return;\n  me.gold-=price;",
    "  if(t.castle&&k!=='market'&&k!=='wh') return;\n  if(k==='fort'&&isDino(0)) return;   // the Dinosaurs build no forts\n  me.gold-=price;")
rep("  const spots=[['barracks',150,1],['fort',90,0],['market',30,5]];",
    "  const spots=[['barracks',150,1],['fort',90,0],['market',30,5]].filter(x=>!(x[0]==='fort'&&isDino(0)));   // the Dinosaurs build no forts")
rep("const defBonus=t=>(t.castle?castleDef(t):(isMyth(t.owner)?0:(t.fort|0))",
    "const defBonus=t=>(t.castle?castleDef(t):(isMyth(t.owner)||isDino(t.owner)?0:(t.fort|0))")
rep("const canTrebAt=t=>t.castle?trebN(t)<2:(!!t.fort&&!t.treb);",
    "const canTrebAt=t=>(t.owner>=0&&isDino(t.owner))?false:t.castle?trebN(t)<2:(!!t.fort&&!t.treb);   // the Dinosaurs have the volcano instead")
rep("const readyTrebs=pid=>isMyth(pid)?[]:","const readyTrebs=pid=>(isMyth(pid)||isDino(pid))?[]:")
rep("  if(B.treb===1){ B.treb=0; B.trebDue=0; addLog('A trebuchet under construction is wrecked.',p.id); }",
    "  if(B.treb===1){ B.treb=0; B.trebDue=0; addLog('A trebuchet under construction is wrecked.',p.id); }\n  if(isDino(p.id)&&(B.treb||B.treb2)){ B.treb=0; B.trebDue=0; B.treb2=0; B.trebDue2=0; addLog('The Dinosaurs wreck the trebuchets they captured.',p.id); }")
# the computer: no forts for the Dinosaurs
n=s.count("return {k:'fort',id:c.id};"); assert n==4,n
s=s.replace("return {k:'fort',id:c.id};","if(!isDino(pid)) return {k:'fort',id:c.id};")
# action wording
rep("at your castles and barracks, or train other units at barracks and forts`; }",
    "at your castles and barracks, or train other units at barracks${isDino(pid)?'':' and forts'}`; }")
rep("  if(a==='build') return 'Build as many Markets, Forts and Barracks as you can afford'+(lvl?` (Market ${costOf('market',lvl)}, Fort ${costOf('fort',lvl)}, Barracks ${costOf('barracks',lvl)} gold)`:'');",
    "  if(a==='build') return (isDino(pid)?'Build as many Markets and Barracks as you can afford':'Build as many Markets, Forts and Barracks as you can afford')+(lvl?` (Market ${costOf('market',lvl)}${isDino(pid)?'':`, Fort ${costOf('fort',lvl)}`}, Barracks ${costOf('barracks',lvl)} gold)`:'');")
open(p,'w').write(s); print('patch3 ok')

# Dinosaur board rework, step 1: the board's Dinosaur roster matches the arena rewrite.
# Code keys stay: galli=Pachycephalosaurus, bow=Triceratops, quetz=Stegosaurus; alamo becomes the barracks guard.
import sys
p=sys.argv[1]; s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:100]); s=s.replace(a,b)
rep("""  dinos:{barracks:[['galli','Gallimimus','Gallimimus'],['dilo','Dilo Archer','Dilophosaurus Archer'],['mega','Megaraptor','Megaraptor'],['bow','Longbow','Longbow']],
         fort:[['ptero','Pterodactyl','Pterodactyl'],['quetz','Quetzal','Quetzalcoatlus'],['alamo','Alamosaurus','Alamosaurus']]},""",
"""  // the Dinosaurs have no forts: everything trains at the barracks (level 1 Megaraptor, 2 Pterodactyl, 3 Triceratops and Stegosaurus)
  dinos:{barracks:[['galli','Pachy','Pachycephalosaurus'],['dilo','Dilophosaurus','Dilophosaurus'],['mega','Megaraptor','Megaraptor'],['ptero','Pterodactyl','Pterodactyl'],['bow','Triceratops','Triceratops'],['quetz','Stegosaurus','Stegosaurus']],
         fort:[]},""")
rep("""  galli:  {name:'Gallimimus',hp:8,dmg:4,rate:1.1,cost:2,rank:0,basic:true,hk:'galli'},
  dilo:   {name:'Dilophosaurus Archer',hp:6,dmg:4,rate:1.2,cost:4,rank:2,rng:true,aa:true,basic:true,bonusBasic:1,missAir:.2,hk:'archer'},""",
"""  // the Dinosaurs (Ethan's rewrite, 2026-11-06; the same numbers as the arena)
  galli:  {name:'Pachycephalosaurus',hp:15,dmg:5,rate:1.0,cost:3,rank:0,basic:true,hk:'galli'},
  dilo:   {name:'Dilophosaurus',hp:15,dmg:2,rate:0.6,cost:8,rank:2,rng:true,aa:true,basic:true,hk:'archer'},""")
import re
m=re.search(r"  mega:   \{name:'Megaraptor'[^\n]*\n",s); s=s.replace(m.group(0),"  mega:   {name:'Megaraptor',hp:35,dmg:12,rate:1.0,cost:12,rank:0,heavy:true,hk:'melee',multi:2,noStun:true,sprint:{dur:2,mult:3}},   // its bite also catches a second enemy; 20 to big units (bonus below)\n",1)
m=re.search(r"  bow:    \{name:'Longbow'[^\n]*\n",s); s=s.replace(m.group(0),"  bow:    {name:'Triceratops',hp:45,dmg:15,rate:1.2,cost:25,rank:0,heavy:true,hk:'melee',noProj:true},   // shots and spells do nothing to it (the Laser Tank's beam does)\n",1)
m=re.search(r"  quetz:  \{name:'Quetzalcoatlus'[^\n]*\n",s); s=s.replace(m.group(0),"  quetz:  {name:'Stegosaurus',hp:65,dmg:20,rate:2.0,cost:30,rank:0,heavy:true,hk:'melee',multi:8},   // tail swing: up to 8 around it, survivors stunned 2s\n",1)
m=re.search(r"  alamo:  \{name:'Alamosaurus'[^\n]*\n",s); s=s.replace(m.group(0),"  alamo:  {name:'Alamosaurus',hp:120,dmg:15,rate:2.0,cost:25,rank:0,heavy:true,hk:'melee',multi:4,guard:true},   // the barracks guard: defends only, never moves\n",1)
# the Megaraptor does 20 (12+8) to big units: heavy ones, plus the Griffin, Dragon and Desmodus
rep("const UNIT_KEYS=Object.keys(UNIT_STATS);",
"""const UNIT_KEYS=Object.keys(UNIT_STATS);
UNIT_STATS.mega.bonus={}; UNIT_KEYS.forEach(k=>{ if(UNIT_STATS[k].heavy||['griffin','dragon','gbat'].includes(k)) UNIT_STATS.mega.bonus[k]=8; });""")
# Triceratops: shots and spells (arrows, lasers, quills, lightning, gunship fire) do nothing; the Laser Tank's beam still does
rep("    if(T.reduce&&T.reduce[w.hk]) d=Math.max(1,d-T.reduce[w.hk]);",
    "    if(T.reduce&&T.reduce[w.hk]) d=Math.max(1,d-T.reduce[w.hk]);\n    if(T.noProj&&(w.rng||w.hk==='gunship'||w.hk==='magic')&&w.hk!=='beam') return 0;   // Triceratops")
rep("  galli:'Fast biter',\n  dilo:'Shooter. Hits flyers (misses 20%). +1 damage to basic units',",
    "  galli:'Charges in. Each head-butt slows the enemy it hits for the rest of the battle',\n  dilo:'Shooter that spits venom half the field. Grounds flyers it hits for 3s. Dodges half of charging hits',")
for k,txt in [('mega',"Its bite also catches a second enemy. 20 damage to big units. Can't be stunned. Sprints in from reserve"),
              ('bow',"Shots and spells do nothing to it (except the Laser Tank's beam). Charges, knocking back up to 6, and stops enemy charges"),
              ('quetz',"Tail swing hits up to 8 ground enemies around it and stuns the ones left standing for 2s"),
              ('alamo',"Barracks guard: bought at a barracks, never moves or attacks, and fights whenever the hex is attacked. Each stomp hits up to 4 enemies")]:
    m=re.search(r"\n  %s:'[^\n]*',"%k,s); assert m,k; s=s.replace(m.group(0),"\n  %s:%r,"%(k,txt),1)
m=re.search(r"\n  quetz:'[^\n]*',",s)
rep("const BK_NEED={mega:1,rknight:1,bow:2,rlong:2,rhino:1,kanga:2};",
    "const BK_NEED={mega:1,rknight:1,rlong:2,rhino:1,kanga:2,ptero:2,bow:3,quetz:3};   // Dinosaurs: Megaraptor 1, Pterodactyl 2, Triceratops and Stegosaurus 3")
# barracks level descriptions come from the unlock table, per faction
m=re.search(r"const barracksLv=pid=>\{[^\n]*\n",s)
s=s.replace(m.group(0),"""const barracksLv=pid=>{ const f=(S&&S.players&&S.players[pid])?S.players[pid].faction:DEFAULT_FACTION, b=UNITS[f].barracks;
  const at=l=>b.filter(x=>bkNeed(x[0])===l).map(x=>x[2]), say=a=>a.length>1?a.slice(0,-1).join(', ')+' and '+a[a.length-1]:a[0];
  return [1,2,3].map(l=>{ const u=at(l); return u.length?`Unlocks the ${say(u)}`+(l===3?`; units bought here cost 1 gold less`:''):(l===3?BARRACKS_LV[2]:'—'); }); };
""",1)
# board pictures: the rewrite's art (the arena's files in dino/)
rep("Object.assign(UNIT_ART,MAMMAL_ART.units);",
    "Object.assign(UNIT_ART,MAMMAL_ART.units);\nObject.assign(UNIT_ART,{galli:'dino/pachy_blue.png',dilo:'dino/dilo_blue.png',mega:'dino/mega_blue.png',bow:'dino/trike_blue.png',quetz:'dino/stego_blue.png'});   // the Dinosaur rewrite's pictures")
open(p,'w').write(s); print('patch1 ok')

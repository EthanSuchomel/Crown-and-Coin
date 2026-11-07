import sys, re
# The new Dinosaurs (Ethan's roster and stats, 2026-11-06). Code keys stay the same so Crown & Coin armies still map:
# galli = Pachycephalosaurus, dilo = Dilophosaurus, mega = Megaraptor, bow = Triceratops, quetz = Stegosaurus, ptero unchanged,
# alamo retired (dropped from armies).
path = sys.argv[1]
s = open(path, encoding='utf-8').read()
def R(old, new, n=1):
    global s
    c = s.count(old); assert c == n, (c, old[:90]); s = s.replace(old, new)

def unit(key, new):
    global s
    a = s.index('\n  ' + key + ":{label:'")
    m = re.compile(r"\n  [a-z]+:\{label:'").search(s, a + 5)
    s = s[:a] + '\n  ' + key + ':' + new + s[m.start():]

# ---------------- units (speeds: 100% = 5.4) ----------------
unit('galli', "{label:'Pachycephalosaurus',cost:3,hp:15,dmg:5,rate:1.0,range:4.3,speed:5.4,w:6.6,ratio:0.5635,aimFrac:0.45,ranged:false,hitKey:'melee',armor:{},pcharge:{mult:1.25},slowHit:{spd:0.81,rate:0.3},noRepeat:true,\n"
     "        flying:false,antiAir:false,rank:0,basic:true,lungeDur:.32,strikeAt:.14,lungeFwd:0.012,bob:0.5,bobRate:1.6},   // charges in at 125% until its first hit; every head-butt slows that enemy for the rest of the battle (speed -15%, attacks 0.3s slower; once per enemy) and it moves on to a different enemy after each one")
unit('dilo', "{label:'Dilophosaurus',cost:8,hp:15,dmg:2,rate:0.6,range:50,dodgeCharge:0.5,speed:5.4,w:6.4,ratio:0.5188,aimFrac:0.45,ranged:true,hitKey:'archer',armor:{},preferAir:true,noRepeat:true,grounds:{dur:3},spit:true,shotAt:[0.97,0.21],\n"
     "        flying:false,antiAir:true,rank:2,basic:true,lungeDur:.3,strikeAt:.12,bob:0.4,bobRate:1.4},   // spits venom; goes after flyers first and knocks them down to the ground for 3s; never spits at the same target twice in a row")
unit('mega', "{label:'Megaraptor',heavy:true,stunImmune:true,cost:12,hp:25,dmg:12,bigDmg:20,twin:true,rate:1.0,range:4.3,speed:6.21,w:9.5,ratio:0.4578,aimFrac:0.45,ranged:false,hitKey:'melee',armor:{},entryBurst:{mult:3},\n"
     "        flying:false,antiAir:false,rank:0,lungeDur:.4,strikeAt:.18,lungeFwd:0.012,bob:0.4,bobRate:1.3},   // bites 2 enemies at once; 20 to large units; can't be stunned; sprints in from reserve")
unit('bow', "{label:'Triceratops',heavy:true,noProj:true,cost:25,hp:30,dmg:15,rate:1.2,range:3.0,footX:3.2,footY:1.0,speed:5.4,w:11.5,ratio:0.5473,aimFrac:0.45,ranged:false,hitKey:'melee',armor:{},tcharge:{mult:1.2,n:6},knock:3,hornSweep:{n:5},\n"
     "        flying:false,antiAir:false,rank:-1,lungeDur:.45,strikeAt:.2,lungeFwd:0.012,bob:0.2,bobRate:0.9},   // nothing that's shot or cast can hurt it; leads its army and opens with a charge that shoves up to 6 enemies back")
unit('quetz', "{label:'Stegosaurus',heavy:true,cost:30,hp:45,dmg:20,rate:2.0,range:3.0,footX:4.0,footY:1.2,speed:5.4,w:13.5,ratio:0.6329,aimFrac:0.4,ranged:false,hitKey:'melee',armor:{},tail:{n:8,reach:3,stun:2},\n"
     "        flying:false,antiAir:false,rank:0,lungeDur:.6,strikeAt:.3,lungeFwd:0.006,bob:0.15,bobRate:0.8},   // tail swing: 20 to up to 8 enemies around it, and the ones left standing are stunned for 2s")
R("dragon:{label:'Dragon',", "dragon:{label:'Dragon',large:true,")
R("griffin:{label:'Griffin',", "griffin:{label:'Griffin',large:true,")
R("gbat:{label:'Desmodus',", "gbat:{label:'Desmodus',large:true,")
# the Robot Knight's bonus against the old Longbow no longer has a target
R("rank:0,bonus:{bow:4},sweep:", "rank:0,sweep:")

R("const ORDER=['galli','dilo','ptero','mega','bow','quetz','alamo',", "const ORDER=['galli','dilo','ptero','mega','bow','quetz',")
R("Dinosaurs:{dilo:8,ptero:4,mega:24,bow:8}", "Dinosaurs:{galli:15,dilo:6,ptero:5,mega:5,bow:2,quetz:1}")
# armies sent in from Crown & Coin: an Alamosaurus has no place in the arena any more
R("const ak=KEY_IN[k]||k; if(TYPES[ak]) COUNTS", "const ak=KEY_IN[k]||k; if(TYPES[ak]&&ORDER.includes(ak)) COUNTS")

# ---------------- art: Ethan's OpenArt pictures, cut out by Claude ----------------
R('''  dragon:{"blue": {"up": "myth/dragon_blue.png", "down": "myth/dragon_blue.png"}, "red": {"up": "myth/dragon_red.png", "down": "myth/dragon_red.png"}}
});''', '''  dragon:{"blue": {"up": "myth/dragon_blue.png", "down": "myth/dragon_blue.png"}, "red": {"up": "myth/dragon_red.png", "down": "myth/dragon_red.png"}}
});
// Dinosaurs (Ethan's OpenArt art, 2026-11-06, cut out by Claude): blue trim on Blue's side, red on Red's
Object.assign(IMG,{
  galli:{"blue": "dino/pachy_blue.png", "red": "dino/pachy_red.png"},
  dilo:{"blue": "dino/dilo_blue.png", "red": "dino/dilo_red.png"},
  mega:{"blue": "dino/mega_blue.png", "red": "dino/mega_red.png"},
  bow:{"blue": "dino/trike_blue.png", "red": "dino/trike_red.png"},
  quetz:{"blue": "dino/stego_blue.png", "red": "dino/stego_red.png"}
});''')
R(".arrow.short{width:3.2%}", ".arrow.short{width:3.2%}\n.arrow.spit{width:1.2%;height:5px;border-radius:50%;background:radial-gradient(circle at 60% 45%,#efffb0 0 25%,#8fd63a 45%,#3f7d14 100%);box-shadow:0 0 4px 1px rgba(150,240,70,.65)}   /* Dilophosaurus venom */")
R("'arrow'+(f.key==='dilo'||f.key==='porc'?' short':'')", "'arrow'+(f.T&&f.T.spit?' spit':f.key==='porc'?' short':'')")

# ---------------- who can hit whom ----------------
# Triceratops: nothing shot or cast reaches it (arrows, spit, quills, lasers, rockets, bolts, lightning, the beam). Melee, fire and stomps still do.
# Dilophosaurus: a flyer it hits is knocked down to the ground for 3s, where ground fighters can reach it.
R("const canHit=(f,o)=>!o.pass&&!(soaringOver(o)&&shooter(f))&&(!o.T.flying||f.T.antiAir)&&",
  "const downed=o=>o.downT>clock;   // a flyer a Dilophosaurus has knocked down\nconst isLarge=o=>!!(o.T.heavy||o.T.large);   // what a Megaraptor bites for 20\nconst canHit=(f,o)=>!o.pass&&!(soaringOver(o)&&shooter(f))&&!(o.T.noProj&&shooter(f))&&(!o.T.flying||f.T.antiAir||downed(o))&&")
R("  if(f.T.preferGround) return o.T.flying?0:1;", "  if(f.T.preferGround) return o.T.flying?0:1;\n  if(f.T.preferAir) return (o.T.flying&&!downed(o))?1:0;            // Dilophosaurus: flyers still in the air first")
R("const p=prio(f,o)-((f.T.ranged&&shielded(o))?2:0)", "const p=prio(f,o)-((f.T.noRepeat&&o.id===f.lastShot)?5:0)-((f.T.ranged&&shielded(o))?2:0)")
R("||hiddenIn(o)||shielded(o)||soaringOver(o)) continue;", "||hiddenIn(o)||shielded(o)||soaringOver(o)||o.T.noProj) continue;")
R("function hit(t,att,mult,proj){\n", "function hit(t,att,mult,proj){\n  if(t.T.noProj&&(proj||(att.T&&(att.T.ranged||att.T.rocket)))){ floatText(t,'Block','blk'); return; }   // Triceratops: shots and spells can't hurt it\n  if(t.T.dodgeCharge&&(att.rcharge||att.chargeHit||att.pcharge||att.mcharge)&&R()<t.T.dodgeCharge){ floatText(t,'Dodge','blk'); return; }   // Dilophosaurus: jumps aside from half the hits of a charging enemy\n")
R("  if(t.key==='mega'&&(att.rcharge||att.chargeHit)&&R()<MEGA_CHARGE_DODGE){ floatText(t,'Dodge','blk'); return; }   // Megaraptor: leaps aside from 75% of charging hits\n", "")
R("+((att.T.bonus&&att.T.bonus[t.key])||0)", "+((att.T.bonus&&att.T.bonus[t.key])||0)+((att.T.bigDmg&&isLarge(t))?att.T.bigDmg-att.T.dmg:0)")

# ---------------- charges and slows ----------------
R("mcharge:!!T.mcharge,", "mcharge:!!T.mcharge,pcharge:!!T.pcharge,tcharge:!!(T.tcharge&&!entering),")
R("o.boost=0; o.burstPending=false; o.rchargeWait=false; o.mcharge=false;", "o.boost=0; o.burstPending=false; o.rchargeWait=false; o.mcharge=false; o.pcharge=false; o.tcharge=false;")
R("    o.boost=0; o.burstPending=false; o.mcharge=false; }\n}", "    o.boost=0; o.burstPending=false; o.mcharge=false; o.pcharge=false; o.tcharge=false; }\n}")
R("const spd=((T.walkSpeed&&", "const spd=Math.max(0.5,((T.walkSpeed&&")
R("*(f.mcharge?T.mcharge.mult:1);   // a Minotaur charges until its first hit",
  "*(f.mcharge?T.mcharge.mult:1)*(f.pcharge?T.pcharge.mult:1)*(f.tcharge?T.tcharge.mult:1)-(f.slowed?f.slowed.spd:0));   // a Minotaur charges until its first hit (and a Pachycephalosaurus; a Triceratops until it reaches the enemy line); a Pachycephalosaurus' head-butt slows")
R("if(f.mcharge&&!f.engaged&&f.target&&STANCE[f.team]!=='hold')", "if((f.mcharge||f.tcharge)&&!f.engaged&&f.target&&STANCE[f.team]!=='hold')")
R("T.rate-(rallied(f)?0.2:0); f.lunge=0;", "T.rate-(rallied(f)?0.2:0)+(f.slowed?f.slowed.rate:0); f.lunge=0;", 2)
# Triceratops: its opening charge ends when it reaches the enemy it's heading for, shoving up to 6 enemies back
R("    if(T.breath) breathStep(f);\n    const t=f.target;\n",
  "    if(T.breath) breathStep(f);\n    const t=f.target;\n    if(f.tcharge&&t&&(!t.T.flying||downed(t))&&gap(f,t)<=T.range+1&&(!BW.length||sameLevel(f,t))) trikeImpact(f,t);\n")
# Dilophosaurus: on to a new target after every spit
R("            if(T.ranged||T.rocket) shoot(f,t);\n", "            if(T.ranged||T.rocket){ shoot(f,t); if(T.noRepeat){ f.lastShot=t.id; f.target=null; } }\n")
R("else if((!t.T.flying||T.antiAir)&&gap(f,t)<=T.range+1.5&&(!BW.length||sameLevel(f,t))){ if(f.missNext){ f.missNext=false; floatText(t,'Miss','blk'); } else { if(f.mcharge) chargeHit(f,t); else hit(t,f);",
  "else if((!t.T.flying||T.antiAir||downed(t))&&gap(f,t)<=T.range+1.5&&(!BW.length||sameLevel(f,t))){ if(f.missNext){ f.missNext=false; floatText(t,'Miss','blk'); } else { if(f.mcharge) chargeHit(f,t); else if(T.slowHit) pachyHit(f,t); else hit(t,f); if(T.twin) twinBite(f,t); if(T.tail) tailSwing(f,t); if(T.hornSweep) hornSweep(f,t); if(T.noRepeat){ f.lastShot=t.id; f.target=null; }")
# knocked-down flyers drop to the ground
R("    if(f.T.hover){ f.baseAlt=ALT;", "    if(f.T.hover&&!downed(f)){ f.baseAlt=ALT;")
R("f.baseAlt+=((f.grounded?0:low?LOW_ALT:ALT)-f.baseAlt)", "f.baseAlt+=((f.grounded||downed(f)?0:low?LOW_ALT:ALT)-f.baseAlt)")
R("else { hit(a.t,a.att,a.mult,true); if(a.stun", "else { hit(a.t,a.att,a.mult,true); if(a.att.T&&a.att.T.grounds&&a.t.T.flying&&!a.t.dead&&!soaringOver(a.t)) a.t.downT=clock+a.att.T.grounds.dur; if(a.stun")

# ---------------- the new moves ----------------
R("// Minotaur charge: its first hit kills outright;", '''// ---- Dinosaurs ----
// Pachycephalosaurus: runs in 25% faster until its first hit. Every head-butt that lands slows that enemy for the rest of the battle
// (15% slower, attacks 0.3s slower; one slow per enemy, it doesn't build up), and after each one it goes for a different enemy
function pachyHit(f,t){
  const landed=hit(t,f); f.pcharge=false;
  if(landed&&!t.dead&&!t.slowed&&!t.ballista){ t.slowed={spd:f.T.slowHit.spd,rate:f.T.slowHit.rate}; t.el.classList.add('slowed'); }
}
// Triceratops: every one on the field at the start charges to the front, 20% faster; when it reaches the enemy line it shoves
// up to 6 enemies on the ground around it back, then fights as normal
function trikeImpact(f,t){
  f.tcharge=false;
  const near=F.filter(o=>!o.dead&&!o.pass&&!o.ballista&&o.team!==f.team&&(!o.T.flying||downed(o))&&gap(f,o)<=f.T.range+3&&(!BW.length||sameLevel(f,o)))
    .sort((a,b)=>gap(f,a)-gap(f,b)).slice(0,f.T.tcharge.n);
  for(const o of near) knockBack(f,o);
  dust(f); const q=document.createElement('span'); q.className='quake'; q.addEventListener('animationend',()=>q.remove()); f.el.appendChild(q);
}
// Triceratops: every attack also gores up to 5 enemy shooters within its reach (archers, spitters, Mages, gunners...), full damage each
function hornSweep(f,t){
  F.filter(o=>o!==t&&!o.dead&&!o.pass&&!o.ballista&&o.team!==f.team&&shooter(o)&&(!o.T.flying||downed(o))&&gap(f,o)<=f.T.range+1.5&&(!BW.length||sameLevel(f,o)))
    .sort((a,b)=>gap(f,a)-gap(f,b)).slice(0,f.T.hornSweep.n).forEach(o=>hit(o,f));
}
// Megaraptor: every bite also catches a second enemy within reach
function twinBite(f,t){
  let best=null,bd=1e9;
  for(const o of F){ if(o===t||o.dead||o.pass||o.ballista||o.team===f.team||!canHit(f,o)||(o.T.flying&&!downed(o))) continue;
    if(BW.length&&!sameLevel(f,o)) continue;
    const g=gap(f,o); if(g<=f.T.range+1.5&&g<bd){bd=g;best=o;} }
  if(best) hit(best,f);
}
// Stegosaurus: its tail swing hits up to 8 enemies all around it (its target and the 7 nearest), and every one still standing is stunned
function tailSwing(f,t){
  const S=f.T.tail, reach=f.T.w*0.5+S.reach;
  const near=F.filter(o=>o!==t&&!o.dead&&!o.pass&&!o.ballista&&o.team!==f.team&&(!o.T.flying||downed(o))&&dist(f,o)<=reach&&(!BW.length||sameLevel(f,o)))
    .sort((a,b)=>dist(f,a)-dist(f,b)).slice(0,S.n-1);
  for(const o of near) hit(o,f);
  for(const o of [t,...near]) if(!o.dead&&!o.T.stunImmune&&!o.T.beam){ if(!(o.stun>0)) floatText(o,'Stunned','blk'); o.stun=Math.max(o.stun,S.stun); }
  const q=document.createElement('span'); q.className='quake'; q.addEventListener('animationend',()=>q.remove()); f.el.appendChild(q);
}
// Minotaur charge: its first hit kills outright;''')
R("function chargeHit(f,t){\n  f.mcharge=false;\n", "function chargeHit(f,t){\n  f.mcharge=false;\n  if(t.T.dodgeCharge&&R()<t.T.dodgeCharge){ floatText(t,'Dodge','blk'); return; }   // a Dilophosaurus jumps aside\n")

# ---------------- the stats table and the rules text ----------------
R('''        <tr><td>Gallimimus</td><td>2 gold</td><td>8</td><td>4</td><td>1.1s</td><td>120%</td><td>Melee</td><td>No</td></tr>
        <tr><td>Dilophosaurus Archer</td><td>4 gold</td><td>6</td><td>4 (5 vs basic units)</td><td>1.2s</td><td>75%</td><td>A quarter of the field</td><td>Yes, misses 20%</td></tr>''',
  '''        <tr><td>Pachycephalosaurus</td><td>3 gold</td><td>15</td><td>5. Every hit slows that enemy for the rest of the battle (speed -15%, attacks 0.3s slower; once per enemy); a different enemy each time</td><td>1.0s</td><td>100% (125% while charging)</td><td>Melee</td><td>No</td></tr>
        <tr><td>Dilophosaurus</td><td>8 gold</td><td>15</td><td>2 (venom spit; a flyer it hits is knocked to the ground for 3s)</td><td>0.6s</td><td>100%</td><td>Half the field; dodges 50% of hits from a charging enemy</td><td>Yes, goes after them first</td></tr>''')
s = re.sub(r"        <tr><td>Megaraptor</td>.*?</tr>\n        <tr><td>Longbow</td>.*?</tr>\n        <tr><td>Alamosaurus</td>.*?</tr>\n        <tr><td>Quetzalcoatlus</td>.*?</tr>\n",
  '''        <tr><td>Megaraptor</td><td>12 gold</td><td>25</td><td>12 to 2 enemies at once (20 to large units)</td><td>1.0s</td><td>115% (345% when arriving from reserve, or bursting out of the forest or the fortress, until its first attack)</td><td>Melee; can't be stunned</td><td>No</td></tr>
        <tr><td>Triceratops</td><td>25 gold</td><td>30 (nothing that's shot or cast can hurt it)</td><td>15, plus 15 to up to 5 enemy shooters in reach. Opening charge: shoves up to 6 enemies back</td><td>1.2s</td><td>100% (120% while charging)</td><td>Melee; leads its army</td><td>No</td></tr>
        <tr><td>Stegosaurus</td><td>30 gold</td><td>45</td><td>20 to up to 8 enemies around it; the ones left standing are stunned for 2s</td><td>2.0s</td><td>100%</td><td>All around it (tail)</td><td>No</td></tr>
''', s, count=1, flags=re.S)
assert 'Stegosaurus</td><td>30 gold' in s
R("<td>2 (misses Megaraptors and Alamosaurus 25%)</td>", "<td>2 (misses heavy units 25%: Megaraptors, Triceratops, Stegosaurus, Rhinos, Palaeoloxodons, Minotaurs, Robot Knights and Laser Tanks)</td>")
R("<td>9 (13 vs Longbows; also 2 to up to 2 enemies next to its target)</td>", "<td>9 (also 2 to up to 2 enemies next to its target)</td>")
R("Megaraptor armor blocks the first 3 Archer hits (no more than 2 of those can be from Alamosaurus riders), the first 3 Robot Archer lasers, the first Longbow hit (arrow or Robot Longbow laser) and the first Gallimimus hit it takes. After that, each Gallimimus bite has a 10% chance to be deflected. The Robot Knight's shield gives it the same blocks and deflects, and it has the Megaraptor's other stats too, except its sword hits for 9 and, instead of the Megaraptor's second bite, every hit also cuts",
  "Dinosaurs: the Triceratops always leads its army: every one that starts on the field takes the front of the line, and when the battle starts it charges (20% faster) at the enemy front; when it gets there it shoves up to 6 enemies on the ground around it back, then fights as normal. Every attack also gores up to 5 enemy shooters within its reach (archers, Dilophosaurus, Porcupines, Procoptodons, Mages and the like) for full damage, on top of the enemy it's attacking. Nothing that's shot or cast can hurt it (Dilophosaurus spit, quills, arrows, lasers, rockets, ballista bolts, the Mage's lightning and the Laser Tank's beam), and shooters don't aim at it; melee, stomps and fire still do. Every Pachycephalosaurus runs in 25% faster until its first hit. Every head-butt that lands slows that enemy for the rest of the battle: it moves 15% slower and attacks 0.3s slower (an enemy is only slowed once, however often it's hit), and after each head-butt the Pachycephalosaurus goes for a different enemy. The Dilophosaurus is the Dinosaurs' only shooter: it spits venom across half the field, goes after flyers first, never spits at the same target twice in a row, and jumps aside from half the hits of a charging enemy (a Rhino, Minotaur or Pachycephalosaurus on its charge). A flyer it hits is knocked down to the ground for 3 seconds, where ground fighters can reach it (each hit starts the 3 seconds again). Every Megaraptor bite hits 2 enemies at once, for 12 each, or 20 to a large unit (Megaraptors, Triceratops, Stegosaurus, Rhinos, Palaeoloxodons, Desmodus, Minotaurs, Griffins, Dragons, Robot Knights and Laser Tanks). Megaraptors can't be stunned, and they come in from reserve at triple speed until they make their first attack (a bash at a gate doesn't count); they do the same bursting out of the forest on the Trees map and out of the fortress gate. The Stegosaurus swings its tail through up to 8 enemies on the ground all around it, front and back, for 20 each, and every one left standing is stunned for 2 seconds. Pterodactyls only attack ground units. The Robot Knight's shield blocks the first 3 Archer hits (Dilophosaurus spit or Porcupine quills), the first 3 Robot Archer lasers and the first long-range hit (a Procoptodon arrow or Robot Longbow laser) it takes. Its sword hits for 9, and every hit also cuts")
R("(only a laser that misses doesn't stun, and the Alamosaurus and the Laser Tank can't be stunned)", "(only a laser that misses doesn't stun, and Megaraptors and the Laser Tank can't be stunned)")
R("The Robot Gunship, the Robots' heavy flyer, costs and moves like the Quetzalcoatlus, with half an archer's reach:", "The Robot Gunship, the Robots' heavy flyer, has half an archer's reach:")
R("It can't be stunned: a Super Stomp or any other stun has no effect on it.", "It can't be stunned.")
a = s.index(" Megaraptors coming in from reserve charge at triple speed"); b = s.index(" Pterodactyls fly the same way but only attack ground units, and so do Robot Drones")
s = s[:a] + " Flyers glide down to fight ground units and climb back up between targets. Robot Drones only attack ground units" + s[b + len(" Pterodactyls fly the same way but only attack ground units, and so do Robot Drones"):]
a = s.index(" The Alamosaurus stomps up to 5 ground units touching its body at once"); b = s.index(" Reserves come in mixed in the same proportions")
s = s[:a] + s[b:]
R("Procoptodons shoot like Longbows, so armor that blocks those blocks them too.", "Procoptodons shoot long-range arrows.")
R("The Desmodus goes after melee units first, like the Quetzalcoatlus.", "The Desmodus goes after melee units first.")
R("cut short by an enemy War Trumpet or Super Stomp)", "cut short by a Griffin's screech)")
R("(a Megaraptor's sprint, an Alamosaurus or Rhino charge)", "(a Megaraptor's sprint; a Rhino, Minotaur, Pachycephalosaurus or Triceratops charge)")
R("The Griffin and the Dragon fly like the Quetzalcoatlus,", "The Griffin and the Dragon fly like the other flyers,")
R("(archers, lasers, quills, the Mage's lightning, Alamosaurus riders)", "(Dilophosaurus spit, arrows, lasers, quills, the Mage's lightning)")
R("a Rhino or Minotaur charge ends, a Megaraptor loses its sprint, and an Alamosaurus that hasn't charged yet won't.", "a Rhino, Minotaur, Pachycephalosaurus or Triceratops charge ends, and a Megaraptor loses its sprint.")
R("an Alamosaurus, Palaeoloxodon, Laser Tank or Dragon instead takes a normal hammer blow and is stunned for 4 seconds, even though nothing else can stun the Alamosaurus or the Laser Tank.",
  "a Palaeoloxodon, Laser Tank or Dragon instead takes a normal hammer blow and is stunned for 4 seconds, even though nothing else can stun the Laser Tank.")
R("The holder's special units (the Alamosaurus, the Laser Tank or the Palaeoloxodon)","The holder's special units (the Laser Tank or the Palaeoloxodon)")
R("but the Alamosaurus, the Laser Tank and the Palaeoloxodon are too big.","but the biggest units (Triceratops, Stegosaurus, Rhinos, the Laser Tank and the Palaeoloxodon) are too big.")
open(path, 'w', encoding='utf-8').write(s)
# what's left that names a retired unit, outside comments and CSS
left = [m.group(0) for m in re.finditer(r"[^\n]{0,60}(Alamosaurus|Quetzalcoatlus|Gallimimus|Longbow hit|Dilophosaurus Archer|Super Stomp)[^\n]{0,40}", s) if '//' not in m.group(0) and '/*' not in m.group(0)]
print('patched', path, len(s)); print('\n'.join(left[:20]))

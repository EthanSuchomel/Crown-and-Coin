"""The Mammal cards' own upgrades (Ethan, 2026-11-13), like the Dinosaur and Robot cards: each card has 3 upgrades for each of
its actions (levels add up, except where one says "instead"). They replace the Mammals' old abilities (Mating, Territorial,
Watering Hole as an upgrade, Reforest, In Numbers, Fertilize).
Ethan's choices (2026-11-13):
  - Den Season's Harvest pays when that card is played; Tusks and Thorns' Harvest pays every round once reached (permanent).
  - The Watering Hole stays as a normal Mammal building, buildable in any Build.
  - Tusks and Thorns' Advancements 3: after the action, move units anywhere within your land, as often as you like.
  - Call of the Wild's Advancements 2: a moved barracks keeps its level.
The upgrade names are Claude's placeholders.
python3 dev/mammal-cards/patch_cards.py index.html"""
import sys

p = sys.argv[1]
s = open(p, encoding='utf-8').read()


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (old[:90], n)
    s = s.replace(old, new)


# ---------- the cards' upgrades ----------
DCARD_M = r"""
// ---------- Mammal cards (Ethan, 2026-11-13): each card has its own 3 upgrades for each of its actions, like the Dinosaurs and
// Robots. They replace the old Mammal abilities. Upgrade names are Claude's placeholders; the effects are Ethan's. ----------
Object.assign(DCARD,{
  roam:{move:[['Long March','3 moves instead of 2'],['Far Roam','4 moves'],['Mountain Paths','your units can move onto mountains']],
        build:[['Den Raising','advance one of your barracks a level for free'],['Second Stall','a hex\'s 2nd market is free'],['Land Bounty','+1 material for every hex you hold']],
        recruit:[['Young Ape','a free Gorilla at your home castle'],['Young Rhino','also a free Rhino there'],['Young Tusker','also a free Palaeoloxodon there']]},
  forage:{harvest:[['Grazing','1 gold for every hex instead of every 2'],['Gathered Stores','+1 material for every 3 markets'],['Rich Grazing','2 gold for every hex, and +1 material for every 2 markets instead']],
          build:[['Supplies','+3 materials when this action starts'],['Free Den','a free barracks: your next one costs nothing'],['Roost Grant','a free fortress: your next one costs nothing']],
          recruit:[['Den Cubs','a free Gorilla at every barracks'],['Roost Cubs','a free Gorilla at every barracks and every fortress'],['Rhino Calves','also a free Rhino on every hex with both a barracks and a fortress']]},
  den:{harvest:[['Home Stores','+5 gold from your home castle'],['Home Riches','+10 gold instead'],['Home Bounty','+15 gold and 3 materials instead']],
       recruit:[['Den Prices','units cost 1 gold less'],['Den Pack','3 free Gorillas at your home castle'],['Den Rhino','also a free Rhino at your home castle']],
       fortify:[['Quill Guard','a free Porcupine with every army of 10 or more units'],['Quill Wall','2 Porcupines instead'],['Rhino Guard','also a free Rhino with each of those armies']]},
  wild:{recruit:[['Hide Trade','+1 material for every 3 units you buy'],['Tusk Trade','+5 materials for every Palaeoloxodon you buy'],['Home Calling','units at your home castle cost 2 gold less']],
        harvest:[['Castle Tribute','+3 gold for every castle you hold'],['Castle Riches','+6 gold for every castle instead'],['Castle Hoard','+10 gold for every castle instead']],
        advance:[['Roost Raising','you can build one fortress in this action'],['Den Move','move a barracks to an open spot on another of your hexes (it keeps its level)'],['Free Roost','a free fortress: your next one costs nothing']]},
  tusks:{harvest:[['Castle Lands','from now on, every round each castle you hold makes +1 gold'],['Castle Herds','every round, each castle makes +3 gold and +1 material instead'],['Castle Wealth','every round, each castle makes +5 gold and +2 materials instead']],
         advance:[['Free Den Upgrade','your first barracks upgrade in this action is free'],['Quick Dens','barracks upgrades cost 1 material less'],['Roam Free','after this action, move your units anywhere within your land, as often as you like']],
         move:[['Charge','an extra move, if that move is an attack'],['Ambush','sneak attacks: the defenders can\'t attack until your units land their first hit'],['Stride','another extra move']]},
});"""
anchor = "units at your home castle can regroup to any of your hexes']]},\n});\n"
rep(anchor, anchor + DCARD_M.lstrip('\n') + '\n')

rep("const cardUps=pid=>isDino(pid)||isRobo(pid);   // factions whose cards have their own upgrades (DCARD)",
    "const cardUps=pid=>isDino(pid)||isRobo(pid)||isMamm(pid);   // factions whose cards have their own upgrades (DCARD): Dinosaurs, Robots, and the Mammals since 2026-11-13")
rep("const NAMED_UP={mammals:MAMM_UP};", "const NAMED_UP={};   // the Mammals' named upgrades (Mating, Territorial...) gave way to their card upgrades (2026-11-13)")
rep("const effLvl=(pid,l)=>(isDino(pid)||isRobo(pid))?0:", "const effLvl=(pid,l)=>cardUps(pid)?0:")
rep("const mammOn=(pid,l)=>isMamm(pid)&&(l||0)>=1;",
    "const mammOn=(pid,l)=>false;   // the old Mammal abilities (Mating, Territorial, Reforest, In Numbers, Fertilize) are retired: the Mammal cards have their own upgrades (2026-11-13)")

# ---------- the Watering Hole: a normal Mammal building in any Build (Ethan, 2026-11-13) ----------
rep("const mammNow=(pid,a)=>!!(S&&S.play&&S.current===pid&&curAction()===a&&mammOn(pid,rawLvl()));",
    "const mammNow=(pid,a)=>!!(S&&S.play&&S.current===pid&&curAction()===a&&mammOn(pid,rawLvl()));\n"
    "// the Watering Hole: since 2026-11-13 a normal Mammal building, in any of their Builds (Ethan)\n"
    "const whOk=pid=>isMamm(pid)&&!!(S&&S.play&&S.current===pid&&curAction()==='build');\n"
    "// the Mammal cards' extra moves: The Long Roam (3, then 4 moves), Tusks and Thorns (Charge, then Stride)\n"
    "const mammMoves=pid=>{ const r=dk(pid,'roam','move'), t=dk(pid,'tusks','move'); return (r>=2?2:r>=1?1:0)+(t>=1?1:0)+(t>=3?1:0); };")
n_wh = s.count("mammNow(0,'build')") + s.count("mammNow(pid,'build')")
s = s.replace("mammNow(0,'build')", "whOk(0)").replace("mammNow(pid,'build')", "whOk(pid)")
assert n_wh == 7, n_wh

# ---------- Move: extra moves, mountains, Charge, sneak attacks ----------
rep("+modsOf(pid).movesPerAction+(mammNow(pid,'move')?1:0)+", "+modsOf(pid).movesPerAction+mammMoves(pid)+")
rep("const chargeOnly=pid=>dk(pid,'stamp','move')>=1&&", "const chargeOnly=pid=>(dk(pid,'stamp','move')>=1||dk(pid,'tusks','move')>=1)&&")
rep("const curLvl=()=>S&&S.play?(isDino(S.current)?(dk(S.current,'siege','move')>=1?1:0):isRobo(S.current)?(dk(S.current,'mobil','move')>=2?1:0):",
    "const curLvl=()=>S&&S.play?(isDino(S.current)?(dk(S.current,'siege','move')>=1?1:0):isRobo(S.current)?(dk(S.current,'mobil','move')>=2?1:0):isMamm(S.current)?(dk(S.current,'roam','move')>=3?1:0):")
rep("yield* aiMoveGen(pid,isRobo(pid)?(dk(pid,'mobil','move')>=2?1:0):lvl);",
    "yield* aiMoveGen(pid,isRobo(pid)?(dk(pid,'mobil','move')>=2?1:0):isMamm(pid)?(dk(pid,'roam','move')>=3?1:0):lvl);")   # Mountain Paths (The Long Roam)
rep("off=dk(pid,'mobil','move')>=3&&!(def>=0", "off=(dk(pid,'mobil','move')>=3||dk(pid,'tusks','move')>=2)&&!(def>=0")   # Ambush (Tusks and Thorns)
rep('return (o.surprise?"<br>Offline: a sneak attack. They can\'t attack until your units land their first hit":\'\')',
    'return (o.surprise?`<br>${S&&isMamm(S.current)?\'Ambush\':\'Offline\'}: a sneak attack. They can\'t attack until your units land their first hit`:\'\')')

# ---------- Recruit prices: Den Prices (Den Season), Home Calling (Call of the Wild) ----------
rep("  -((t&&t.wh&&PRICEY.has(k)&&isMamm(pid))?WH_OFF:0)\n",
    "  -((t&&t.wh&&PRICEY.has(k)&&isMamm(pid))?WH_OFF:0)\n"
    "  -((pid>=0&&isMamm(pid))?(dk(pid,'den','recruit')>=1?1:0)+((t&&dk(pid,'wild','recruit')>=3&&isHomeCastle(t)&&t.owner===pid)?2:0):0)   // Den Prices (Den Season), Home Calling (Call of the Wild)\n")

# ---------- Harvest ----------
rep("dh=isDino(pid)?dinoHarvest(pid):isRobo(pid)?roboHarvest(pid):{g:0,m:0,why:[]}",
    "dh=isDino(pid)?dinoHarvest(pid):isRobo(pid)?roboHarvest(pid):isMamm(pid)?mammHarvest(pid):{g:0,m:0,why:[]}")
rep("if((isDino(pid)||isRobo(pid))&&(dh.g||dh.m)){", "if(cardUps(pid)&&(dh.g||dh.m)){")

MAMM_FNS = r"""
// ---------- The Mammal cards' upgrades (Ethan, 2026-11-13) ----------
// a Mammal Harvest's card upgrades: Forage (gold per hex, materials from markets), Den Season (the home castle), Call of the
// Wild (gold per castle). Tusks and Thorns' castles pay every round instead (tuskLv, in incomeOf and beginTurn).
function mammHarvest(pid){
  const own=S.tiles.filter(t=>t.owner===pid), mk=own.reduce((n,t)=>n+(t.market|0),0), cs=own.filter(t=>t.castle).length,
    hexes=incomeOf(pid).tiles, half=Math.floor(hexes*HARVEST_PER[0]), P=c=>dk(pid,c,'harvest'), home=S.tiles[S.homes[pid]];
  let g=0, m=0; const why=[];
  const fo=P('forage'), de=P('den'), wi=P('wild');
  if(fo>=1){ const x=(fo>=3?2:1)*hexes-half; g+=x; why.push(`${fo>=3?'Rich Grazing':'Grazing'} +${x}`); }
  if(fo>=2){ const x=Math.floor(mk/(fo>=3?2:3)); m+=x; why.push(`${fo>=3?'Rich Grazing':'Gathered Stores'} +${matTxt(x)}`); }
  if(de>=1){ if(home&&home.owner===pid){ const x=de>=3?15:de>=2?10:5; g+=x; if(de>=3) m+=3; why.push(`${['','Home Stores','Home Riches','Home Bounty'][de]} +${x}${de>=3?` and +${matTxt(3)}`:''}`); }
             else why.push(`${['','Home Stores','Home Riches','Home Bounty'][de]}: nothing, because you don't hold your home castle`); }
  if(wi>=1){ const x=[0,3,6,10][wi]*cs; g+=x; why.push(`${['','Castle Tribute','Castle Riches','Castle Hoard'][wi]} +${x}`); }
  return {g,m,why};
}
// Tusks and Thorns' Harvest: once reached, every round each castle pays more (Ethan: "every round")
const TUSK_G=[0,1,3,5], TUSK_M=[0,0,1,2];
const tuskLv=pid=>(S&&S.players&&S.players[pid]&&isMamm(pid))?cardLv(pid,'tusks','harvest'):0;
// a Mammal action's card upgrades that happen when it starts. Returns notes for the card column.
function mammActionStart(pid){
  const a=cardAction(), p=S.players[pid], out=[], ic=`<span class="px px-${a}" aria-hidden="true"></span>`, own=S.tiles.filter(t=>t.owner===pid),
    home=S.tiles[S.homes[pid]], atHome=!!home&&home.owner===pid;
  if(a==='build'){
    const ro=dk(pid,'roam','build'), fo=dk(pid,'forage','build');
    if(fo>=1){ p.mat=matOf(pid)+3; out.push(`${ic} Supplies: +${matTxt(3)}`); }
    if(fo>=2){ p.fnest=(p.fnest|0)+1; out.push(`${ic} Free Den: your next barracks is free`); }
    if(fo>=3){ p.ffort=(p.ffort|0)+1; out.push(`${ic} Roost Grant: your next fortress is free`); }
    if(ro>=3){ const x=own.length; p.mat=matOf(pid)+x; out.push(`${ic} Land Bounty: +${matTxt(x)} from your ${x} hexes`); addLog(`${p.name} gather ${matTxt(x)} from their land.`,pid); }
    if(ro>=2) out.push(`${ic} Second Stall: a hex's 2nd market costs nothing in this action`);
    if(ro>=1){ S.play.rbk=1;
      if(p.ai){ const dE=bfs(foeTiles(pid)), t=own.filter(x=>x.barracks&&(x.bk||0)<3).sort((x,y)=>(y.bk||0)-(x.bk||0)||fin(dE[x.id])-fin(dE[y.id]))[0]; if(t) mammFreeBk(pid,t.id); }
      else out.push(own.some(t=>t.barracks&&(t.bk||0)<3)?`${ic} Den Raising: tap one of your barracks to advance it a level for free`:`${ic} Den Raising: no barracks to advance yet`); }
  }
  if(a==='recruit'){
    const ro=dk(pid,'roam','recruit'), fo=dk(pid,'forage','recruit'), de=dk(pid,'den','recruit'), got={};
    if(ro>=1) got.ape=1; if(ro>=2) got.rhino=1; if(ro>=3) got.eleph=1;
    if(de>=2) got.ape=(got.ape|0)+3; if(de>=3) got.rhino=(got.rhino|0)+1;
    if(cnt(got)){ if(atHome){ addArmy(home,got,true); out.push(`${ic} ${[ro>=1?'Young '+(ro>=3?'Tusker':ro>=2?'Rhino':'Ape'):'',de>=2?(de>=3?'Den Rhino':'Den Pack'):''].filter(Boolean).join(', ')}: ${armyList(got)} at your home castle`); addLog(`${p.name} get ${cnt(got)} free unit${cnt(got)>1?'s':''} at their home castle.`,pid); }
      else out.push(`${ic} No free units at your home castle, because you don't hold it`); }
    if(fo>=1){ let n=0, r=0; own.forEach(t=>{ const k=(t.barracks|0)+(fo>=2?(t.fort|0):0); if(k){ addUnits(t,BASIC.mammals,k,true); n+=k; } if(fo>=3&&t.barracks&&t.fort){ addUnits(t,'rhino',1,true); r++; } });
      out.push(n||r?`${ic} ${fo>=3?'Rhino Calves':fo>=2?'Roost Cubs':'Den Cubs'}: +${n} Gorilla${n===1?'':'s'}${fo>=2?' at your barracks and fortresses':' at your barracks'}${r?`, +${r} Rhino${r>1?'s':''}`:''}`:`${ic} ${fo>=2?'Roost Cubs':'Den Cubs'}: no barracks${fo>=2?' or fortresses':''} yet`);
      if(n||r) addLog(`${p.name} get ${n+r} free unit${n+r>1?'s':''} at their barracks${fo>=2?' and fortresses':''}.`,pid); }
    if(de>=1) out.push(`${ic} Den Prices: every unit costs 1 gold less in this action`);
    const wi=dk(pid,'wild','recruit'); if(wi>=1) S.play.bought=0;
    if(wi>=1) out.push(`${ic} ${wi>=2?'Hide Trade and Tusk Trade':'Hide Trade'}: +1 material for every 3 units you buy${wi>=2?', +5 for every Palaeoloxodon':''}${wi>=3?'. Home Calling: units at your home castle cost 2 gold less':''}`);
  }
  if(a==='advance'){
    const wi=dk(pid,'wild','advance'), tu=dk(pid,'tusks','advance');
    if(wi>=3){ p.ffort=(p.ffort|0)+1; out.push(`${ic} Free Roost: your next fortress is free`); }
    if(wi>=1){ S.play.wf=1; if(!p.ai) out.push(`${ic} Roost Raising: tap one of your hexes to build a fortress there (${(p.ffort|0)>0?'free':matTxt(COSTS.fort[0])})`); }
    if(wi>=2){ S.play.mb=1; if(!p.ai) out.push(`${ic} Den Move: tap one of your barracks to move it to another of your hexes`); }
    if(tu>=1&&!p.ai) out.push(`${ic} ${tu>=2?'Free Den Upgrade and Quick Dens: your first barracks upgrade is free, the rest cost 1 material less':'Free Den Upgrade: your first barracks upgrade in this action is free'}`);
    if(tu>=3&&!p.ai) out.push(`${ic} Roam Free: after this action you can move your units anywhere within your land`);
  }
  return out;
}
// a Mammal Build's prices: Second Stall (The Long Roam), and the free barracks and fortresses (Forage, Call of the Wild)
function mammCost(pid,k,c,t){
  const p=S.players[pid];
  if(k==='market'&&dk(pid,'roam','build')>=2&&t&&(t.market|0)===1) return 0;
  if(k==='barracks'&&(p.fnest|0)>0) return 0;
  if(k==='fort'&&(p.ffort|0)>0) return 0;
  return c;
}
function mammBuilt(pid,k,price){ if(price>0) return; const p=S.players[pid];
  if(k==='barracks'&&(p.fnest|0)>0) p.fnest--; else if(k==='fort'&&(p.ffort|0)>0) p.ffort--; }
// Den Raising (The Long Roam): one barracks goes up a level for free during that Build
function mammFreeBk(pid,i){
  const t=S.tiles[i], p=S.players[pid];
  if(!S.play||!S.play.rbk||curAction()!=='build'||t.owner!==pid||!t.barracks||(t.bk||0)>=3) return false;
  t.bk=(t.bk||0)+1; S.play.rbk=0; noteUnlock(pid,'barracks',t);
  addLog(`${p.name} advance a barracks to level ${t.bk} for free.`,pid);
  return true;
}
// Roost Raising (Call of the Wild): one fortress during that Advancements (free with a free-fortress token)
const mammFortOk=(pid,t)=>!!(S.play&&S.play.wf&&curAction()==='advance'&&t&&t.owner===pid&&t.terrain==='plain'&&!t.castle&&bCount(t)<bMax());
const mammFortPrice=pid=>(S.players[pid].ffort|0)>0?0:COSTS.fort[0];
function mammFort(pid,i){
  const t=S.tiles[i], p=S.players[pid], c=mammFortPrice(pid);
  if(!mammFortOk(pid,t)||matOf(pid)<c) return false;
  spendMat(pid,c); if(!c) p.ffort--; t.fort=(t.fort|0)+1; S.play.wf=0; noteUnlock(pid,'fort',t);
  addLog(`${p.name} build a ${BUILD_INFO.fort.name}${c?'':' for free'}.`,pid);
  return true;
}
// Den Move (Call of the Wild): a barracks moves to an open spot on another of your hexes and keeps its level
const mammBkSpots=(pid,from)=>S.tiles.filter(t=>t.owner===pid&&t.id!==from&&t.terrain==='plain'&&!t.castle&&!t.barracks&&bCount(t)<bMax()).map(t=>t.id);
function mammMoveBk(pid,from,to){
  const a=S.tiles[from], b=S.tiles[to], p=S.players[pid];
  if(!S.play||!S.play.mb||curAction()!=='advance'||a.owner!==pid||!a.barracks||!mammBkSpots(pid,from).includes(to)) return false;
  const lv=a.bk||0; a.barracks--; if(!a.barracks) a.bk=0; b.barracks=1; b.bk=lv; S.play.mb=0;
  addLog(`${p.name} move a barracks${lv?` (level ${lv})`:''} to another hex.`,pid);
  return true;
}
// Den Season's Fortify: a Porcupine (2 at level 2, and a Rhino at level 3) with every army of 10 or more units
function mammFortify(pid,raw){
  if(S.play.card!=='den'||raw<1) return [];
  const p=S.players[pid], got=raw>=2?{porc:2}:{porc:1}; if(raw>=3) got.rhino=1;
  const big=S.tiles.filter(t=>t.owner===pid&&t.troops>=10);
  big.forEach(t=>addArmy(t,got,true));
  if(big.length) addLog(`${p.name} get ${armyList(got).replace(/<[^>]*>/g,'').trim()||'free units'} with each of their ${big.length} big armies.`,pid);
  return [big.length?`${raw>=3?'Rhino Guard':raw>=2?'Quill Wall':'Quill Guard'}: ${armyList(got)} with each of your ${big.length} armies of 10 or more`:`${raw>=2?'Quill Wall':'Quill Guard'}: no army of 10 or more units yet`];
}
// Hide Trade and Tusk Trade (Call of the Wild): materials for the units bought in that Recruit
function mammBought(pid,k,n){
  const l=dk(pid,'wild','recruit'); if(l<1||!S.play||!(n>0)) return 0;
  const P=S.play, was=P.bought|0; P.bought=was+n;
  let m=Math.floor(P.bought/3)-Math.floor(was/3); if(l>=2&&k==='eleph') m+=5*n;
  if(m>0){ S.players[pid].mat=matOf(pid)+m; addLog(`${S.players[pid].name} trade for ${matTxt(m)}.`,pid); }
  return m;
}
// Roam Free (Tusks and Thorns' Advancements 3): after the action, a regroup with any number of moves to any of your hexes
const rgOn=()=>!!(S&&S.play&&S.play.rg===1&&cardOf(S.current,S.play.card).actions[S.play.step]==='advance');
const rgDue=pid=>!!(S&&S.play&&!S.play.rg&&isMamm(pid)&&cardAction()==='advance'&&dk(pid,'tusks','advance')>=3);
"""
rep("// a Robot Harvest's card upgrades (Ethan, 2026-11-11)\n", MAMM_FNS.lstrip('\n') + "// a Robot Harvest's card upgrades (Ethan, 2026-11-11)\n")

# action starts, prices, tokens
rep("  if(isRobo(pid)&&S.play) return roboActionStart(pid);\n",
    "  if(isRobo(pid)&&S.play) return roboActionStart(pid);\n  if(isMamm(pid)&&S.play) return mammActionStart(pid);\n")
rep("return pid>=0&&curAction()==='build'?(isDino(pid)?dinoCost(pid,k,c,t):isRobo(pid)?roboCost(pid,k,c,t):c):c; };",
    "return pid>=0&&curAction()==='build'?(isDino(pid)?dinoCost(pid,k,c,t):isRobo(pid)?roboCost(pid,k,c,t):isMamm(pid)?mammCost(pid,k,c,t):c):c; };")
rep("function dinoBuilt(pid,k,price){ if(isRobo(pid)) return roboBuilt(pid,k,price);",
    "function dinoBuilt(pid,k,price){ if(isRobo(pid)) return roboBuilt(pid,k,price); if(isMamm(pid)) return mammBuilt(pid,k,price);")

# Fortify: Den Season's armies
rep("  if(isDino(pid)&&S.play) out.push(...dinoFortify(pid,raw));\n",
    "  if(isDino(pid)&&S.play) out.push(...dinoFortify(pid,raw));\n  if(isMamm(pid)&&S.play) out.push(...mammFortify(pid,raw));\n")

# Advancements: Free Den Upgrade and Quick Dens (Tusks and Thorns)
rep("  const free=lvl>=1&&!S.play.freeBk&&lv===0, price=free?0:bkUpCost(pid,lv,t);",
    "  const free=((lvl>=1&&lv===0)||dk(pid,'tusks','advance')>=1)&&!S.play.freeBk, price=free?0:bkUpCost(pid,lv,t);   // Free Den Upgrade (Tusks and Thorns): the first one, any level")
rep("const bkUpCost=(pid,lv,t)=>Math.max(0,BARRACKS_UP[lv]-(dk(pid,'hunt','advance')>=1?1:0)-",
    "const bkUpCost=(pid,lv,t)=>Math.max(0,BARRACKS_UP[lv]-(dk(pid,'hunt','advance')>=1?1:0)-(dk(pid,'tusks','advance')>=2?1:0)-")   # Quick Dens

# Tusks and Thorns' Harvest: castles pay every round
rep("  const nest=nestGold(pid);   // the Dinosaurs' Nesting\n  return {tiles,castles,markets,land,nest,total:castles*m.castleGold+land+markets*m.marketGold+nest};",
    "  const nest=nestGold(pid);   // the Dinosaurs' Nesting\n  const tusk=castles*TUSK_G[tuskLv(pid)];   // Tusks and Thorns' Harvest (Mammals): every round, more gold for each castle\n"
    "  return {tiles,castles,markets,land,nest,tusk,total:castles*m.castleGold+land+markets*m.marketGold+nest+tusk};")
rep("  const p=cur(), inc=incomeOf(p.id);\n  p.gold+=inc.total;\n",
    "  const p=cur(), inc=incomeOf(p.id);\n  p.gold+=inc.total;\n"
    "  const tm=inc.castles*TUSK_M[tuskLv(p.id)]; if(tm) p.mat=matOf(p.id)+tm;   // Tusks and Thorns' Harvest: materials from every castle, every round\n")
rep("  addLog(`${p.name} collect ${inc.total} ${cur$(p.id)}.`,p.id);",
    "  addLog(`${p.name} collect ${inc.total} ${cur$(p.id)}${tm?` and ${matTxt(tm)}`:''}.`,p.id);")

# ---------- Roam Free: the regroup after a Tusks and Thorns Advancements ----------
rep("const regrouping=()=>fxOn()&&S.play.fx.ph==='regroup';", "const regrouping=()=>(fxOn()&&S.play.fx.ph==='regroup')||rgOn();   // also Roam Free (Tusks and Thorns)")
rep("const curAction=()=>{ if(!S||!S.play) return null; const a=cardAction(); if(a!=='fortify'||!S.play.fx) return a;",
    "const curAction=()=>{ if(!S||!S.play) return null; const a=cardAction(); if(a==='advance'&&S.play.rg===1) return 'move'; if(a!=='fortify'||!S.play.fx) return a;")
rep("const fxReach=()=>S.play&&S.play.fx&&S.play.fx.far>0?99:REGROUP_REACH;",
    "const fxReach=()=>rgOn()?99:S.play&&S.play.fx&&S.play.fx.far>0?99:REGROUP_REACH;")
rep("if(!isHumanTurn()||!regrouping()||!(S.play.fx.rally>0)||", "if(!isHumanTurn()||!regrouping()||!(S.play.fx&&S.play.fx.rally>0)||")
rep("if(regrouping()&&A.owner===S.current&&S.play.fx.far>0&&", "if(regrouping()&&A.owner===S.current&&S.play.fx&&S.play.fx.far>0&&")
rep("function leftoverWarning(){\n", "function leftoverWarning(){\n  if(rgOn()) return null;   // Roam Free is optional\n")
rep("  if(fxNext()){ render(); return; }   // still inside a Fortify: the regroup, then the picks\n",
    "  if(rgDue(0)){ S.play.rg=1; S.play.moves=0; render(); return; }   // Roam Free (Tusks and Thorns): the regroup after the Advancements\n"
    "  if(S.play.rg===1) S.play.rg=2;\n"
    "  if(fxNext()){ render(); return; }   // still inside a Fortify: the regroup, then the picks\n")
rep("const lbl=f&&f.ph==='regroup'?'Done regrouping':",
    "const lbl=rgDue(0)?'Next: move units':rgOn()?(last?'Done, end turn':'Done, next action'):f&&f.ph==='regroup'?'Done regrouping':")
rep("  if(a==='move'&&regrouping()){\n",
    "  if(a==='move'&&rgOn()){   // Roam Free (Tusks and Thorns)\n"
    "    if(sel&&sel.troops>0) h+=`<div class=\"harmy\">${sel.owner===0?'Here':'Enemy'}: ${armyList(sel.army)}${sel.owner===0&&sel.fresh<sel.troops?` <span class=\"sub\">(${sel.fresh} ready)</span>`:''}</div>`;\n"
    "    h+=`<div class=\"row-label\"><span class=\"px px-move\" aria-hidden=\"true\"></span> Roam Free</div><p class=\"hint\">${sel&&sel.owner===0&&sel.fresh>0?'Tap a highlighted hex of yours to send units there. ':'Tap a hex with your units, then any highlighted hex of yours. '}Move your units anywhere within your land, as often as you like (no attacks or claiming). Then tap <b>Done</b>.</p>`;\n"
    "    return h;\n  }\n"
    "  if(a==='move'&&regrouping()){\n")

# ---------- the human's buttons: Den Raising, Roost Raising, Den Move ----------
HUMAN = r"""
// the Mammal cards' buttons in the card column
function mammFreeBkH(){ if(!isHumanTurn()||ui.sel==null) return; if(mammFreeBk(0,ui.sel)) render(); }
function mammFortH(){ if(!isHumanTurn()||ui.sel==null) return; if(mammFort(0,ui.sel)) render(); }
function mammMoveBkH(to){ if(!isHumanTurn()||ui.mvBk==null) return; const from=ui.mvBk; ui.mvBk=null; if(mammMoveBk(0,from,to)) ui.sel=to; render(); }
mammFreeBkH=undoable(mammFreeBkH); mammFortH=undoable(mammFortH); mammMoveBkH=undoable(mammMoveBkH);
"""
rep("mythAct=undoable(mythAct); rallyTo=undoable(rallyTo);", HUMAN.lstrip('\n') + "mythAct=undoable(mythAct); rallyTo=undoable(rallyTo);")
rep("  else if(a==='rally'&&ui.sel!=null) rallyTo(ui.sel);\n",
    "  else if(a==='rally'&&ui.sel!=null) rallyTo(ui.sel);\n"
    "  else if(a==='mfreebk') mammFreeBkH();\n  else if(a==='mfort') mammFortH();\n"
    "  else if(a==='mmvbk'&&ui.sel!=null){ ui.mvBk=ui.sel; render(); }\n  else if(a==='mmvbkx'){ ui.mvBk=null; render(); }\n")
rep("  if(curAction()==='advance'&&ui.roboUp){   // Robots: tap a market or factory to upgrade it\n",
    "  if(curAction()==='advance'&&ui.mvBk!=null){   // Den Move (Call of the Wild): tap where the barracks goes\n"
    "    if(mammBkSpots(0,ui.mvBk).includes(i)){ mammMoveBkH(i); return; }\n    ui.mvBk=null;\n  }\n"
    "  if(curAction()==='advance'&&ui.roboUp){   // Robots: tap a market or factory to upgrade it\n")
rep("  if(isHumanTurn()&&curAction()==='advance'&&ui.roboUp) roboUpTargets(0,ui.roboUp).forEach(j=>hl.add(j));\n",
    "  if(isHumanTurn()&&curAction()==='advance'&&ui.roboUp) roboUpTargets(0,ui.roboUp).forEach(j=>hl.add(j));\n"
    "  if(isHumanTurn()&&curAction()==='advance'&&ui.mvBk!=null) mammBkSpots(0,ui.mvBk).forEach(j=>hl.add(j));   // Den Move\n")
rep("  ui.sel=null; ui.battle=null; ui.wallFor=null; ui.roboUp=null; ui.undo=[]; ui.undoLocked=false; ui.train=null; ui.info=null;\n  if(rgDue(0))",
    "  ui.sel=null; ui.battle=null; ui.wallFor=null; ui.roboUp=null; ui.mvBk=null; ui.undo=[]; ui.undoLocked=false; ui.train=null; ui.info=null;\n  if(rgDue(0))")
# the build column: Den Raising
rep("    if(isRobo(0)) h+=`<ul class=\"bkey\">${roboKeyHtml(lvl)}</ul>`; else\n",
    "    if(isMamm(0)&&S.play.rbk){ h+=sel&&sel.owner===0&&sel.barracks&&(sel.bk||0)<3?`<div class=\"btns\" style=\"margin:.4em 0\"><button class=\"primary\" data-act=\"mfreebk\">Den Raising: advance this barracks to level ${(sel.bk||0)+1} for free</button></div>`\n"
    "      :`<p class=\"hint\" style=\"margin:.4em 0\">Den Raising: tap one of your barracks <span class=\"px px-barracks\" aria-hidden=\"true\"></span> to advance it a level for free.</p>`; }\n"
    "    if(isRobo(0)) h+=`<ul class=\"bkey\">${roboKeyHtml(lvl)}</ul>`; else\n")
# the advance column: Roost Raising and Den Move
rep("    } else if(sel&&sel.owner===0&&sel.terrain!=='water'){\n      h+=matRow()+`<p class=\"hint\">Tap an upgrade around the hex on the map.",
    "    } else if(isMamm(0)&&ui.mvBk!=null){\n"
    "      const n=mammBkSpots(0,ui.mvBk).length;\n"
    "      h+=`<div class=\"row-label\"><span class=\"px px-barracks\" aria-hidden=\"true\"></span> Den Move</div><p class=\"hint\">${n?`Tap a ringed hex of yours to move the barracks there. It keeps its level. ${n} of your hexes have room.`:'None of your other hexes has room for it (castles can\\'t take one).'}</p><div class=\"btns\"><button data-act=\"mmvbkx\">Cancel</button></div>`;\n"
    "    } else if(sel&&sel.owner===0&&sel.terrain!=='water'){\n"
    "      if(isMamm(0)&&(S.play.wf||S.play.mb)){ const bt=[];\n"
    "        if(mammFortOk(0,sel)) bt.push(`<button data-act=\"mfort\" ${matOf(0)>=mammFortPrice(0)?'':'disabled'}>Roost Raising: build a fortress here (${mammFortPrice(0)?matTxt(mammFortPrice(0)):'free'})</button>`);\n"
    "        if(S.play.mb&&sel.barracks) bt.push(`<button data-act=\"mmvbk\">Den Move: move this barracks</button>`);\n"
    "        if(bt.length) h+=`<div class=\"btns\" style=\"margin:.3em 0 .5em\">${bt.join('')}</div>`; }\n"
    "      h+=matRow()+`<p class=\"hint\">Tap an upgrade around the hex on the map.")

# ---------- the computer ----------
rep("const AI_UP_FAC={mammals:{fortify:4.6,build:2.6}};", "const AI_UP_FAC={};   // (the Mammals used to value their Mating and Watering Hole more)")
rep("  while(isDino(pid)&&(p.fnest|0)>0){",
    "  // Roost Grant and Free Roost (Mammals): free fortresses first, on the front line\n"
    "  while(isMamm(pid)&&(p.ffort|0)>0){ const dE=bfs(foeTiles(pid)), t=S.tiles.filter(x=>x.owner===pid&&x.terrain==='plain'&&!x.castle&&bCount(x)<bMax()).sort((x,y)=>fin(dE[x.id])-fin(dE[y.id])||tp(y)-tp(x))[0];\n"
    "    if(!t) break; t.fort=(t.fort|0)+1; noteUnlock(pid,'fort',t); p.ffort--; ids.push(t.id); addLog(`${p.name} build a free ${BUILD_INFO.fort.name}.`,pid); }\n"
    "  while((isDino(pid)||isMamm(pid))&&(p.fnest|0)>0){")
rep("  if(lvl>=1&&!S.play.freeBk){ const t=bks.find(t=>!(t.bk||0)); if(t&&doUpgradeBarracks(pid,t.id,lvl)) ids.push(t.id); }",
    "  if(lvl>=1&&!S.play.freeBk){ const t=bks.find(t=>!(t.bk||0)); if(t&&doUpgradeBarracks(pid,t.id,lvl)) ids.push(t.id); }\n"
    "  if(dk(pid,'tusks','advance')>=1&&!S.play.freeBk&&bks[0]&&doUpgradeBarracks(pid,bks[0].id,lvl)) ids.push(bks[0].id);   // Free Den Upgrade (Tusks and Thorns)\n"
    "  if(isMamm(pid)&&S.play.wf){   // Roost Raising (Call of the Wild): a fortress on the front line, where troops stand\n"
    "    const dE=bfs(foeTiles(pid)), t=S.tiles.filter(x=>mammFortOk(pid,x)).sort((x,y)=>fin(dE[x.id])-fin(dE[y.id])||tp(y)-tp(x))[0];\n"
    "    if(t&&aiMat(pid,mammFortPrice(pid),4)&&mammFort(pid,t.id)) ids.push(t.id); }")
rep("      const h=roboOn(pid,raw)?factory(pid):null, po=dinoOn(pid,raw)?populate(pid).ids:[]; yield {kind:'flash',ids:(h!=null?[h]:[]).concat(po,aiAdvance(pid,lvl))}; }",
    "      const h=roboOn(pid,raw)?factory(pid):null, po=dinoOn(pid,raw)?populate(pid).ids:[]; yield {kind:'flash',ids:(h!=null?[h]:[]).concat(po,aiAdvance(pid,lvl))};\n"
    "      if(rgDue(pid)){ S.play.rg=1; S.play.moves=0; yield* aiRegroupGen(pid); if(S.play) S.play.rg=2; } }   // Roam Free (Tusks and Thorns)")
# the computer's purchases: Hide Trade and Tusk Trade
rep("  const n=cnt(got); if(!n) return [];\n  addArmy(site,got,true); site.newT=S.turn;",
    "  const n=cnt(got); if(!n) return [];\n  if(isMamm(pid)) for(const k in got) mammBought(pid,k,got[k]);   // Hide Trade and Tusk Trade (Call of the Wild)\n  addArmy(site,got,true); site.newT=S.turn;")
# the human's purchases
rep("  me.gold-=cost; addUnits(t,k,n,true); t.newT=S.turn;\n  let fr=0;",
    "  me.gold-=cost; addUnits(t,k,n,true); t.newT=S.turn; mammBought(0,k,n);\n  let fr=0;")
rep("  me.gold-=cost; addUnits(t,k,1,true); t.newT=S.turn;\n  addLog(`You train",
    "  me.gold-=cost; addUnits(t,k,1,true); t.newT=S.turn; mammBought(0,k,1);\n  addLog(`You train")
rep("  me.gold-=n*st.cost; addUnits(st.t,st.k,n,true); st.t.newT=S.turn;",
    "  me.gold-=n*st.cost; addUnits(st.t,st.k,n,true); st.t.newT=S.turn; mammBought(0,st.k,n);")

# ---------- texts ----------
rep("${fid==='robots'?`<h3>Factories</h3><p>${roboSpecialsHtml()}</p>`:''}",
    "${fid==='robots'?`<h3>Factories</h3><p>${roboSpecialsHtml()}</p>`:''}${fid==='mammals'?`<h3>Watering Hole</h3><p>${BUILD_INFO.wh.desc}. It costs ${matTxt(WH_COST)} and can go up in any Build.</p>`:''}")
rep("${fid==='dinos'||fid==='robots'?`<p>Every ${f.name.replace(/s$/,'')} card has its own upgrades",
    "${fid==='dinos'||fid==='robots'||fid==='mammals'?`<p>Every ${f.name.replace(/s$/,'')} card has its own upgrades")
rep("${mammNow(0,'move')?' (Territorial)':''}", "")

open(p, 'w', encoding='utf-8').write(s)
print('ok')

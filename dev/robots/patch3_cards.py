# Robot rewrite, step 2 (Ethan, 2026-11-11): the Robot cards. Each card has its own 3 upgrades for each of its actions
# (like the Dinosaur cards), Mobilize is now Advancements -> Recruit -> Move, Construct is now Construction, and the
# factory's Barracks and Fortress upgrades move from Build to Advancements. Upgrade names are Claude's placeholders.
import sys
p=sys.argv[1]; s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:140]); s=s.replace(a,b)

# ---------- the deck ----------
rep("""      {id:'mobil', name:'Mobilize',       actions:['recruit','advance','move']},""",
    """      {id:'mobil', name:'Mobilize',       actions:['advance','recruit','move']},   // Ethan, 2026-11-11""")
rep("""      {id:'cons',  name:'Construct',      actions:['move','build','advance']},""",
    """      {id:'cons',  name:'Construction',   actions:['move','build','advance']},""")

# ---------- the upgrade table: the Robots join the Dinosaurs' per-card upgrades ----------
rep("""const CARD_ART={""","""// ---------- Robot cards (Ethan, 2026-11-11): the same kind of per-card upgrades. The names are Claude's placeholders. ----------
Object.assign(DCARD,{
  mobil:{advance:[['Home Grid','factory and barracks upgrades on hexes next to your home castle cost 1 material less'],['Recompile','trade 5 Brawlers on a hex for a Robot Knight'],['Cheap Markets','markets cost 3 gold less, from now on']],
         recruit:[['Assembly Line','for every 2 Brawlers you buy, a 3rd is free'],['Rebuild','trade 8 Brawlers on a hex for a Robot Knight'],['Refit','trade 5 Robot Archers on a hex for a Robot Longbow']],
         move:[['Extra Thread','3 moves instead of 2'],['Climb','troops can move onto mountains'],['Offline','sneak attacks: the defenders can\\'t attack until your units land their first hit']]},
  deploy:{harvest:[['Castle Tax','+2 gold for every castle you hold'],['Castle Tolls','+5 gold for every castle instead'],['Castle Vaults','+12 gold for every castle instead']],
          recruit:[['Drone Line','flyers cost 1 gold less'],['Air Wing','flyers cost 2 gold less instead'],['Sky Fleet','flyers cost 3 gold less instead']],
          move:[['Air Lanes','flyers can move to any of your hexes'],['Ridge Hop','flyers can cross a mountain and land on the far side'],['Overflight','flyers can fly over an enemy army and land 2 hexes away']]},
  onsl:{harvest:[['Full Yield','1 gold for every hex you own, instead of every 2'],['Market Hubs','+5 gold for every hex with 4 markets'],['Hub Stores','+2 materials for every hex with 4 markets']],
        advance:[['Muster','every barracks upgrade also makes 2 Brawlers on that hex'],['Muster Archers','and a Robot Archer'],['Elite Muster','a Robot Knight and a Robot Longbow instead']],
        move:[['Fresh Units','units on a hex where you recruited this turn go 2 hexes'],['Laser Strike','Laser Tanks next to an enemy hex can fire like a trebuchet instead of attacking: no battle'],['Double Strike','a laser strike fires twice']]},
  cons:{move:[['Scavenger','bonus coins pay 12 gold instead of 8'],['Brawler Dash','Brawlers go 2 hexes when both are empty'],['Air Lanes','flyers can move to any of your hexes']],
        build:[['Fresh Ground','a hex you captured this turn: its first market costs 1 gold less'],['Fourth Free','a hex\\'s 4th market is free'],['Scrap','+1 material for every 2 markets you build']],
        advance:[['Quick Barracks','barracks upgrades cost 1 material less'],['Quick Fortress','fortress upgrades cost 1 material less'],['Overclock','buy Overclock at your home castle: 40 gold, all your units +2 damage and +10% health, in every battle']]},
  sprot:{build:[['Border Market','a captured hex next to your home castle: its first market costs 2 gold less'],['Free Market','your first market in this action is free'],['Two Free Markets','your first 2 markets in this action are free']],
         advance:[['Factory Run','5 free Brawlers at your home castle when this action starts'],['Barracks Run','also 3 free Brawlers at every barracks'],['Fortress Run','also 2 free Robot Knights at every fortress']],
         fortify:[['Dual Core','pick two of Build, Advancements and Recruit'],['Sortie','then a real Move: one move that can attack or claim'],['Home Link','units at your home castle can regroup to any of your hexes']]},
});
const CARD_ART={""")
rep("""const dUp=(pid,cid,a)=>!!(cid&&isDino(pid)&&DCARD[cid]&&DCARD[cid][a]);""",
    """const cardUps=pid=>isDino(pid)||isRobo(pid);   // factions whose cards have their own upgrades (DCARD)
const dUp=(pid,cid,a)=>!!(cid&&cardUps(pid)&&DCARD[cid]&&DCARD[cid][a]);""")
rep("""const dk=(pid,cid,a)=>(S&&S.play&&S.current===pid&&isDino(pid)&&""","""const dk=(pid,cid,a)=>(S&&S.play&&S.current===pid&&cardUps(pid)&&""")
# a card upgrade that stays on once reached (Mobilize's Cheap Markets)
rep("""const FACTORY_N=5, NEST_GOLD=2;""","""const FACTORY_N=5, NEST_GOLD=2;
const cardLv=(pid,cid,a)=>{ const c=(FACTIONS[facIdOf(pid)]||{cards:[]}).cards.find(x=>x.id===cid); const i=c?c.actions.indexOf(a):-1; return i<0?0:lvlOf(pid,cid,i); };""")
rep("""const effLvl=(pid,l)=>isDino(pid)?0:""","""const effLvl=(pid,l)=>(isDino(pid)||isRobo(pid))?0:""")
rep("""const NAMED_UP={robots:ROBO_UP, mammals:MAMM_UP};""","""const NAMED_UP={mammals:MAMM_UP};   // the Robots' named upgrades (Update, Offline, Efficiency, Factory...) gave way to their card upgrades (2026-11-11)""")
rep("""const roboOn=(pid,l)=>isRobo(pid)&&(l||0)>=1;""","""const roboOn=(pid,l)=>false;   // the old Robot abilities: replaced by the Robot card upgrades (DCARD)""")
rep("""  if(isDino(pid)){ const base=actionDescBase(a,pid,0); return dUp(pid,cid,a)""","""  if(cardUps(pid)){ const base=actionDescBase(a,pid,0); return dUp(pid,cid,a)""")

# ---------- card art and help lists show for the Robots too ----------
rep("""${CARD_ART[cid]&&isDino(0)?`<img class="cart\"""","""${CARD_ART[cid]&&cardUps(0)?`<img class="cart\"""")
rep("""${CARD_ART[cid]&&isDino(pid)?`<img class="bc-art\"""","""${CARD_ART[cid]&&cardUps(pid)?`<img class="bc-art\"""")
rep("""<ul class="uplist">${isDino(0)?facOf(0).cards.map(c=>`<li><b>${c.name}</b>: ${c.actions.map(a=>`${ACTIONS[a].icon} ${actName(a,'dinos')}""",
    """<ul class="uplist">${cardUps(0)?facOf(0).cards.map(c=>`<li><b>${c.name}</b>: ${c.actions.map(a=>`${ACTIONS[a].icon} ${actName(a,S.players[0].faction)}""")
rep("""    ${fid==='dinos'?`<p>Every Dinosaur card has its own upgrades for each of its actions:</p>""","""    ${fid==='dinos'||fid==='robots'?`<p>Every ${f.name.replace(/s$/,'')} card has its own upgrades for each of its actions:</p>""")

# ---------- Move ----------
rep("""const movesLimit=pid=>(regrouping()&&S.current===pid)?REGROUP_MOVES:(dk(pid,'stamp','move')>=1?1:0)+""",
    """const movesLimit=pid=>(regrouping()&&S.current===pid)?REGROUP_MOVES:(dk(pid,'stamp','move')>=1?1:0)+(dk(pid,'mobil','move')>=1?1:0)+""")
rep("""const curLvl=()=>S&&S.play?(isDino(S.current)?(dk(S.current,'siege','move')>=1?1:0):""",
    """const curLvl=()=>S&&S.play?(isDino(S.current)?(dk(S.current,'siege','move')>=1?1:0):isRobo(S.current)?(dk(S.current,'mobil','move')>=2?1:0):""")
rep("""  const p=S.players[pid], up=!!p.updNow, off=roboOn(pid,raw)&&""","""  const p=S.players[pid], up=!!p.updNow, off=dk(pid,'mobil','move')>=3&&""")
# the Robots' special moves: flyers, Brawlers and new units, each a move only some units can make
rep("""function moveFilter(from,to,lvl){
  const A=S.tiles[from], B=S.tiles[to], pid=A.owner;""","""// The Robots' card moves (2026-11-11): extra hexes a move can reach, each for the units that can make it
const isFlyer=k=>!!(UNIT_STATS[k]&&UNIT_STATS[k].air);
function roboMoveExtra(from,lvl){
  const t=S.tiles[from], pid=t.owner, out=[]; if(!(pid>=0)||!isRobo(pid)||!S.play||S.current!==pid||regrouping()) return out;
  const add=(set,f,why)=>{ if(set.size) out.push({set,f,why}); };
  const dep=dk(pid,'deploy','move'), con=dk(pid,'cons','move'), ons=dk(pid,'onsl','move');
  if(dep>=1||con>=3){ const st=new Set(S.tiles.filter(x=>x.owner===pid&&x.id!==from&&canEnter(x.id,1)).map(x=>x.id)); add(st,isFlyer,'Only flyers can go this far (Air Lanes).'); }
  if(dep>=2){ const st=new Set(); for(const a of nbrs(from)) if(S.tiles[a].terrain==='mountain') for(const b of nbrs(a)) if(b!==from&&canEnter(b,lvl)) st.add(b); add(st,isFlyer,'Only flyers can hop the mountain (Ridge Hop).'); }
  if(dep>=3){ const st=new Set(); for(const a of nbrs(from)){ const A=S.tiles[a]; if(A.owner>=0&&A.owner!==pid&&A.troops>0) for(const b of nbrs(a)) if(b!==from&&canEnter(b,lvl)) st.add(b); } add(st,isFlyer,'Only flyers can fly over the enemy army (Overflight).'); }
  if(con>=2){ const st=new Set(); for(const a of nbrs(from)){ const A=S.tiles[a]; if(!canEnter(a,lvl)||A.troops>0||!passThrough(from,a,lvl,pid)) continue;
      for(const b of nbrs(a)){ const B=S.tiles[b]; if(b!==from&&canEnter(b,lvl)&&B.troops===0&&!homeGuards(B)) st.add(b); } }
    add(st,k=>k===BASIC.robots,'Only Brawlers can dash this far (Brawler Dash).'); }
  if(ons>=1&&t.newT===S.turn){ const st=new Set(); for(const a of nbrs(from)) if(canEnter(a,lvl)&&passThrough(from,a,lvl,pid)) for(const b of nbrs(a)) if(b!==from&&canEnter(b,lvl)) st.add(b); add(st,()=>true,'Units made this turn go 2 hexes (Fresh Units).'); }
  return out;
}
function roboMoveFilter(from,to,lvl){
  if(moveTargetsCore(from,lvl||0,false).includes(to)) return null;
  const xs=roboMoveExtra(from,lvl||0).filter(x=>x.set.has(to)); if(!xs.length) return null;
  return xs.some(x=>x.f('*'))?null:(k=>xs.some(x=>x.f(k)));
}
function moveFilter(from,to,lvl){
  const A=S.tiles[from], B=S.tiles[to], pid=A.owner;
  if(pid>=0&&isRobo(pid)){ const rf=roboMoveFilter(from,to,lvl); if(rf) return rf; }""")
rep("""function moveFilterNote(from,to){ const B=S.tiles[to];""","""function moveFilterNote(from,to){ const B=S.tiles[to];
  if(isRobo(S.tiles[from].owner)&&!moveTargetsCore(from,curLvl(),false).includes(to)){ const x=roboMoveExtra(from,curLvl()).find(x=>x.set.has(to)); if(x) return '<br>'+x.why; }""")
rep("""  return moveTargetsCore(from,lvl,far).filter(""","""  const ext=isRobo(pid)?[...new Set(roboMoveExtra(from,lvl).flatMap(x=>[...x.set]))]:[];
  return [...new Set(moveTargetsCore(from,lvl,far).concat(ext))].filter(""")
# Siege Protocol's Home Link: the home castle's units regroup anywhere in your land
rep("""  if(regrouping()&&pid===S.current) return regroupTargets(from,fxReach());""",
    """  if(regrouping()&&pid===S.current) return regroupTargets(from,(dk(pid,'sprot','fortify')>=3&&from===S.homes[pid])?99:fxReach());   // Home Link (Siege Protocol)""")
# Scavenger: bonus coins pay 12
rep("""  if(B.bounty){ B.bounty=false; if(!isMyth(A.owner)){ p.gold+=COIN_GOLD; res.coin=COIN_GOLD; addLog(`${p.name} take a bonus coin: +${COIN_GOLD} gold.`,p.id); } }""",
    """  if(B.bounty){ B.bounty=false; if(!isMyth(A.owner)){ const cg=dk(p.id,'cons','move')>=1?12:COIN_GOLD; p.gold+=cg; res.coin=cg; addLog(`${p.name} take a bonus coin: +${cg} gold${cg>COIN_GOLD?' (Scavenger)':''}.`,p.id); } }""")
# which hexes changed hands this turn (Fresh Ground, Border Market)
rep("""  B.owner=A.owner; B.army={}; B.ready={}; addArmy(B,sel,false); B.braced=-1;""",
    """  if(prev>=0) { B.capT=S.turn; B.capBy=A.owner; }   // captured from an enemy (Fresh Ground, Border Market)
  B.owner=A.owner; B.army={}; B.ready={}; addArmy(B,sel,false); B.braced=-1;""")


# ---------- prices ----------
rep("""  return pid>=0&&isDino(pid)&&curAction()==='build'?dinoCost(pid,k,c,t):c; };""",
    """  return pid>=0&&curAction()==='build'?(isDino(pid)?dinoCost(pid,k,c,t):isRobo(pid)?roboCost(pid,k,c,t):c):c; };""")
rep("""function dinoBuilt(pid,k,price){ if(!isDino(pid)||price>0||!S.play) return;""",
"""// the Robots' market prices: Free Market(s), Fourth Free, Cheap Markets, Fresh Ground and Border Market
function roboCost(pid,k,c,t){
  if(k!=='market') return c; const P=S.play||{}, sb=dk(pid,'sprot','build');
  if(sb>=2&&(P.freeUsed|0)<(sb>=3?2:1)) return 0;
  if(dk(pid,'cons','build')>=2&&t&&(t.market|0)===3) return 0;
  if(cardLv(pid,'mobil','advance')>=3) c-=3;
  if(t&&!(t.market|0)&&t.capBy===pid){ if(dk(pid,'cons','build')>=1&&t.capT===S.turn) c-=1; if(sb>=1&&nbrs(S.homes[pid]).includes(t.id)) c-=2; }
  return Math.max(0,c);
}
function roboBuilt(pid,k,price){ if(k!=='market'||!S.play) return; const P=S.play, p=S.players[pid], sb=dk(pid,'sprot','build');
  if(price===0&&sb>=2&&(P.freeUsed|0)<(sb>=3?2:1)) P.freeUsed=(P.freeUsed|0)+1;
  if(dk(pid,'cons','build')>=3){ P.mkB=(P.mkB|0)+1; if(P.mkB%2===0){ p.mat=matOf(pid)+1; addLog(`${p.name} salvage 1 material from their new markets (Scrap).`,pid); } } }
// a factory upgrade's price in materials: Quick Barracks, Quick Fortress, and Home Grid next to the home castle
function roboUpCost(pid,k,t){ let c=COSTS[k][0];
  if(k==='barracks'&&dk(pid,'cons','advance')>=1) c--; if(k==='fort'&&dk(pid,'cons','advance')>=2) c--;
  if(t&&dk(pid,'mobil','advance')>=1&&nbrs(S.homes[pid]).includes(t.id)) c--;
  return Math.max(0,c); }
// Muster (Onslaught): every barracks upgrade makes units on that hex
function roboMuster(pid,t){ const l=dk(pid,'onsl','advance'); if(l<1||!isRobo(pid)) return;
  const got=l>=3?{rknight:1,rlong:1}:l>=2?{[BASIC.robots]:2,rarch:1}:{[BASIC.robots]:2}; addArmy(t,got,true); t.newT=S.turn;
  addLog(`${S.players[pid].name} muster ${armyList(got).replace(/<[^>]*>/g,'').trim()||'units'} at the new barracks.`,pid); }
function dinoBuilt(pid,k,price){ if(isRobo(pid)) return roboBuilt(pid,k,price); if(!isDino(pid)||price>0||!S.play) return;""")
rep("""const bkUpCost=(pid,lv)=>BARRACKS_UP[lv]-(dk(pid,'hunt','advance')>=1?1:0);   // Quick Nests""",
    """const bkUpCost=(pid,lv,t)=>Math.max(0,BARRACKS_UP[lv]-(dk(pid,'hunt','advance')>=1?1:0)-(dk(pid,'cons','advance')>=1?1:0)-((t&&dk(pid,'mobil','advance')>=1&&nbrs(S.homes[pid]).includes(t.id))?1:0));   // Quick Nests, Quick Barracks, Home Grid""")
rep("""  const free=lvl>=1&&!S.play.freeBk&&lv===0, price=free?0:bkUpCost(pid,lv);""","""  const free=lvl>=1&&!S.play.freeBk&&lv===0, price=free?0:bkUpCost(pid,lv,t);""")
rep("""  addLog(`${p.name} upgrade a barracks to level ${t.bk}${free?' for free':''}.`,pid);""","""  addLog(`${p.name} upgrade a barracks to level ${t.bk}${free?' for free':''}.`,pid); roboMuster(pid,t);""")
rep("""const wc=wallCost(lvl), lv=t.bk||0, nl=lv+1, free=lvl>=1&&S.play&&!S.play.freeBk&&nl===1, bp=free?0:bkUpCost(0,lv);""",
    """const wc=wallCost(lvl), lv=t.bk||0, nl=lv+1, free=lvl>=1&&S.play&&!S.play.freeBk&&nl===1, bp=free?0:bkUpCost(0,lv,t);""")
rep("""  -((t&&t.wh&&PRICEY.has(k)&&isMamm(pid))?WH_OFF:0));""","""  -((t&&t.wh&&PRICEY.has(k)&&isMamm(pid))?WH_OFF:0)
  -((pid>=0&&isRobo(pid)&&isFlyer(k))?dk(pid,'deploy','recruit'):0));   // Drone Line, Air Wing, Sky Fleet (Deploy)""")

# ---------- Harvest ----------
rep("""dh=isDino(pid)?dinoHarvest(pid):{g:0,m:0,why:[]}""","""dh=isDino(pid)?dinoHarvest(pid):isRobo(pid)?roboHarvest(pid):{g:0,m:0,why:[]}""")
rep("""    if(isDino(pid)&&(dh.g||dh.m)){""","""    if((isDino(pid)||isRobo(pid))&&(dh.g||dh.m)){""")
rep("""// a Dinosaur Harvest's card upgrades: extra gold and materials (Ethan, 2026-11-11)""",
"""// a Robot Harvest's card upgrades (Ethan, 2026-11-11)
function roboHarvest(pid){
  const own=S.tiles.filter(t=>t.owner===pid), cs=own.filter(t=>t.castle).length, hubs=own.filter(t=>(t.market|0)>=ROBO_MARKETS).length, hexes=incomeOf(pid).tiles;
  let g=0, m=0; const why=[], de=dk(pid,'deploy','harvest'), on=dk(pid,'onsl','harvest');
  if(de>=1){ const x=[0,2,5,12][de]*cs; g+=x; why.push(`${['','Castle Tax','Castle Tolls','Castle Vaults'][de]} +${x}`); }
  if(on>=1){ const x=hexes-Math.floor(hexes*.5); g+=x; why.push(`Full Yield +${x}`); }
  if(on>=2){ g+=5*hubs; why.push(`Market Hubs +${5*hubs}`); }
  if(on>=3){ m+=2*hubs; why.push(`Hub Stores +${matTxt(2*hubs)}`); }
  return {g,m,why};
}
// a Dinosaur Harvest's card upgrades: extra gold and materials (Ethan, 2026-11-11)""")

# ---------- action starts: Factory Run, free markets ----------
rep("""function dinoActionStart(pid){
  if(!isDino(pid)||!S.play) return [];""","""function roboActionStart(pid){
  const a=cardAction(), p=S.players[pid], out=[], ic=`<span class="px px-${a}" aria-hidden="true"></span>`, own=S.tiles.filter(t=>t.owner===pid);
  if(a==='advance'){ const l=dk(pid,'sprot','advance');
    if(l>=1){ const h=factory(pid); out.push(h!=null?`${ic} Factory Run: +${FACTORY_N} Brawlers at your home castle`:`${ic} Factory Run: no Brawlers, because you don't hold your home castle`); if(h!=null) S.tiles[h].newT=S.turn; }
    if(l>=2){ const bk=own.filter(t=>t.barracks); bk.forEach(t=>{ addUnits(t,BASIC.robots,3,true); t.newT=S.turn; }); if(bk.length){ out.push(`${ic} Barracks Run: +3 Brawlers at ${bk.length} barracks`); addLog(`${p.name} get 3 free Brawlers at each barracks.`,pid); } }
    if(l>=3){ const ft=own.filter(t=>t.fort); ft.forEach(t=>{ addUnits(t,'rknight',2,true); t.newT=S.turn; }); if(ft.length){ out.push(`${ic} Fortress Run: +2 Robot Knights at ${ft.length} fortress${ft.length>1?'es':''}`); addLog(`${p.name} get 2 free Robot Knights at each fortress.`,pid); } }
  }
  if(a==='build'){ const sb=dk(pid,'sprot','build');
    if(sb>=2) out.push(`${ic} ${sb>=3?'Two Free Markets: your first 2 markets in this action cost nothing':'Free Market: your first market in this action costs nothing'}`);
    if(dk(pid,'cons','build')>=3) out.push(`${ic} Scrap: +1 material for every 2 markets you build`);
  }
  return out;
}
function dinoActionStart(pid){
  if(isRobo(pid)&&S.play) return roboActionStart(pid);
  if(!isDino(pid)||!S.play) return [];""")
rep("""    else if(a==='advance'){ if(mammOn(pid,raw)) S.play.freeWalls=FREE_WALLS;   // Reforest""","""    else if(a==='advance'){ dinoActionStart(pid); if(mammOn(pid,raw)) S.play.freeWalls=FREE_WALLS;   // Reforest""")

# ---------- Recruit: Assembly Line, and which hexes made units this turn ----------
rep("""  if(roboOn(0,rawLvl())){ const P=S.play; P.alB=(P.alB||0)+n;""","""  if(dk(0,'mobil','recruit')>=1&&k===BASIC.robots){ const P=S.play; P.alB=(P.alB||0)+n;""")
rep("""  if(roboOn(pid,rawLvl())&&got[BASIC[f]]>=2) got[BASIC[f]]+=Math.floor(got[BASIC[f]]/2);   // Assembly Line""",
    """  if(dk(pid,'mobil','recruit')>=1&&got[BASIC[f]]>=2) got[BASIC[f]]+=Math.floor(got[BASIC[f]]/2);   // Assembly Line (Mobilize)""")
rep("""me.gold-=cost; addUnits(t,k,n,true);""","""me.gold-=cost; addUnits(t,k,n,true); t.newT=S.turn;""")
rep("""me.gold-=cost; addUnits(t,k,1,true);""","""me.gold-=cost; addUnits(t,k,1,true); t.newT=S.turn;""")
rep("""me.gold-=n*st.cost; addUnits(st.t,st.k,n,true);""","""me.gold-=n*st.cost; addUnits(st.t,st.k,n,true); st.t.newT=S.turn;""")
rep("""  addArmy(site,got,true);""","""  addArmy(site,got,true); site.newT=S.turn;""")

# ---------- the factory's Barracks and Fortress: now made during Advancements at the home castle ----------
rep("""  const c=costOf(k,lvl,t); if(!canPayB(pid,k,c)) return false;
  payB(pid,k,c); t[k]=1; noteUnlock(pid,k,t);""","""  const c=roboUpCost(pid,k,t); if(matOf(pid)<c) return false;
  spendMat(pid,c); t[k]=1; noteUnlock(pid,k,t);""")
rep("""  addLog(`${p.name} upgrade a factory with a ${k==='fort'?'fortress':'barracks'}.`,pid);
  return true;""","""  addLog(`${p.name} upgrade a factory with a ${k==='fort'?'fortress':'barracks'}.`,pid);
  if(k==='barracks') roboMuster(pid,t);
  return true;""")
rep("""  if(k==='rup_barracks'||k==='rup_fort'){ const u=k.slice(4);
    if(curAction()!=='build'||!isRobo(0)||!isHomeCastle(t)||t.owner!==0||!roboUpTargets(0,u).length) return;
    ui.roboUp=u; ui.sel=null; render(); return; }""","")
rep("""  else if(kind==='walls') ui.wallFor=ui.sel;""","""  else if(kind==='walls') ui.wallFor=ui.sel;
  else if(kind==='rup_barracks'||kind==='rup_fort'){ const u=kind.slice(4), t=S.tiles[ui.sel];   // Robots: pick the upgrade at the home castle, then tap the market to upgrade
    if(isRobo(0)&&isHomeCastle(t)&&t.owner===0&&roboUpTargets(0,u).length){ ui.roboUp=u; ui.sel=null; } }""")
rep("""function roboUpgrade(i){ if(curAction()!=='build'||!ui.roboUp) return; const k=ui.roboUp;
  doRoboUp(0,i,curLvl());
  if(!roboUpTargets(0,k).length||!canPayB(0,k,costOf(k,curLvl()))) ui.roboUp=null;   // nothing more to upgrade, or out of materials""",
"""function roboUpgrade(i){ if(curAction()!=='advance'||!ui.roboUp) return; const k=ui.roboUp;
  doRoboUp(0,i);
  if(!roboUpTargets(0,k).some(j=>matOf(0)>=roboUpCost(0,k,S.tiles[j]))) ui.roboUp=null;   // nothing more to upgrade, or out of materials""")
rep("""  if(curAction()==='build'&&ui.roboUp){   // Robots: tap a factory to upgrade it""","""  if(curAction()==='advance'&&ui.roboUp){   // Robots: tap a market or factory to upgrade it""")
rep("""  if(isHumanTurn()&&curAction()==='build'&&ui.roboUp) roboUpTargets(0,ui.roboUp).forEach(j=>hl.add(j));""",
    """  if(isHumanTurn()&&curAction()==='advance'&&ui.roboUp) roboUpTargets(0,ui.roboUp).forEach(j=>hl.add(j));""")
rep("""    .filter(x=>!isRobo(0)||x[0]==='market'||(!recruiting&&isHomeCastle(t)));""","""    .filter(x=>!isRobo(0)||x[0]==='market');""")
rep("""      ||(isRobo(0)&&homeMarket(0)&&['barracks','fort'].some(k=>roboUpTargets(0,k).length&&canPayB(0,k,costOf(k,lvl))));""",";")
# the Advancements view at the home castle: Barracks, Fortress (and Overclock) for the Robots
rep("""    if(isDino(0)){ const g=guardsAt(t), gm=GUARD_MAX*(t.barracks|0)""","""    if(isRobo(0)&&isHomeCastle(t)&&t.owner===0){
      const rb=k=>{ const tg=roboUpTargets(0,k), c=tg.length?Math.min(...tg.map(i=>roboUpCost(0,k,S.tiles[i]))):roboUpCost(0,k,null);
        return {k:'rup_'+k, img:ART.bld[k+'_robots'], sm:true, name:ROBO_NAME[k], can:tg.length>0&&matOf(0)>=c, note:tg.length?`${c} ${MAT_IC}`:k==='fort'?'No barracks':'No market',
          label:tg.length?`${ROBO_NAME[k]}: pick it, then tap the market to upgrade (${matTxt(c)})`:k==='fort'?'Fortress: first give a market a barracks':'Barracks: first build a market that isn\\'t a resource hex'}; };
      opts.splice(0,1,rb('barracks'),rb('fort'));
      if(dk(0,'cons','advance')>=3) opts.push({k:'armor', img:ART.castle_robots.uri, sm:true, name:'Overclock', can:!me.armor&&me.gold>=ARMOR_COST, note:me.armor?'Running':`${ARMOR_COST} gold`,
        label:me.armor?'Overclock: already running':`Overclock for ${ARMOR_COST} gold: all your units +${ARMOR_DMG} damage and +10% health`});
    }
    if(isDino(0)){ const g=guardsAt(t), gm=GUARD_MAX*(t.barracks|0)""")
rep("""    [[150,1],[90,0],[30,5],[210,2]].slice(0,opts.length).forEach(([deg,vi],i)=>{ const o=opts[i];""",
    """    [[150,1],[90,0],[30,5],[210,2],[330,4]].slice(0,opts.length).forEach(([deg,vi],i)=>{ const o=opts[i];""")
rep("""  if(!isDino(pid)||p.armor||h.owner!==pid||dk(pid,'hunt','advance')<3||p.gold<ARMOR_COST) return false;""",
    """  if(p.armor||h.owner!==pid||!(dk(pid,'hunt','advance')>=3||dk(pid,'cons','advance')>=3)||p.gold<ARMOR_COST) return false;   // Armor (The Hunt) or Overclock (Construction)""")
rep("""forge Armor: all their units get""","""${isRobo(pid)?'run Overclock':'forge Armor'}: all their units get""")
# the side panel: picking a factory, in Advancements now
rep("""    if(isRobo(0)&&ui.roboUp){ const k=ui.roboUp, n=roboUpTargets(0,k).length;""","""    if(false){""")
rep("""      h+=matRow()+`<p class="hint">Your home castle upgrades your factories: tap <b>Barracks</b> or <b>Fortress</b> on the map, then tap the factory to upgrade. Or tap <b>Market</b> to build one here. Tap the castle again to zoom back out.</p>`;""",
    """      h+=matRow()+`<p class="hint">Tap <b>Market</b> to build one at your home castle. Barracks and Fortress upgrades for your markets are made here during Advancements. Tap the castle again to zoom back out.</p>`;""")
rep("""  } else if(a==='advance'){
    const lvl=curLvl(), wc=wallCost(lvl);
    if(ui.wallFor!=null){""","""  } else if(a==='advance'){
    const lvl=curLvl(), wc=wallCost(lvl);
    if(isRobo(0)&&ui.roboUp){ const k=ui.roboUp, n=roboUpTargets(0,k).length;
      h+=`<div class="row-label">${bldImg(k+'_robots').replace('<img','<img style="height:1.4em;vertical-align:-.35em"')} ${ROBO_NAME[k]}: ${matTxt(roboUpCost(0,k,null))} each${dk(0,'mobil','advance')>=1?', 1 less next to your home castle':''} (you have ${matOf(0)})</div>${matRow()}<div class="btns" style="margin-bottom:.5em"><button data-act="robodone">Done</button></div><p class="hint">Tap a ringed ${k==='fort'?'factory to add its fortress':'market to add a barracks and make it a factory'}. ${n} can take one.</p>`;
    } else if(isRobo(0)&&sel&&sel.owner===0&&isHomeCastle(sel)){
      h+=matRow()+`<p class="hint">Tap <b>Barracks</b> or <b>Fortress</b> around your home castle, then tap the market or factory to upgrade. Each market is upgraded on its own: first a barracks, then a fortress. Tap the castle again to zoom back out.</p>`;
    } else if(ui.wallFor!=null){""")
# wording: factory upgrades happen in Advancements
rep("""or give it a <b>barracks</b> from your home castle to make it a defensive <b>factory</b>. Not both.""",
    """or give it a <b>barracks</b> from your home castle during Advancements to make it a defensive <b>factory</b>. Not both.""")
rep("""A factory${roboNext(sel)?`. Add its fortress from your home castle`""","""A factory${roboNext(sel)?`. Add its fortress from your home castle during Advancements`""")
rep("""Or a defensive <b>factory</b>: during Build, tap your home castle""","""Or a defensive <b>factory</b>: during Advancements, tap your home castle""")
rep("""or turn one into a factory from your home castle: a Barracks, then a Fortress (""","""or, during Advancements, turn one into a factory at your home castle: a Barracks, then a Fortress (""")

# ---------- the computer: factory upgrades in Advancements ----------
rep("""      const tg=homeMarket(pid)?roboUpTargets(pid,plan.k).sort((a,b)=>man(a,plan.id)-man(b,plan.id)):[];
      if(tg.length) plan={k:plan.k,id:tg[0]};
      else if(plan.k==='barracks'&&!S.tiles[plan.id].castle&&!bCount(S.tiles[plan.id])) plan={k:'market',id:plan.id};
      else break;""","""      if(plan.k==='barracks'&&!S.tiles[plan.id].castle&&!bCount(S.tiles[plan.id])&&!roboUpTargets(pid,'barracks').length) plan={k:'market',id:plan.id};   // a market to upgrade later
      else break;   // barracks and fortresses are factory upgrades, made in Advancements""")
rep("""function aiAdvance(pid,lvl){
  const p=S.players[pid], ids=[];""","""function aiAdvance(pid,lvl){
  const p=S.players[pid], ids=[];
  if(isRobo(pid)&&homeMarket(pid)){   // the Robots' factory upgrades at the home castle, then Overclock
    const dE=bfs(foeTiles(pid)), dEd=t=>fin(dE[t.id]), own=S.tiles.filter(t=>t.owner===pid), bks=own.filter(t=>t.barracks).length, u=unlockOf(pid);
    const tryUp=(k,list)=>{ for(const t of list){ if(aiMat(pid,roboUpCost(pid,k,t))&&doRoboUp(pid,t.id)){ ids.push(t.id); return true; } } return false; };
    if(!bks||(own.length>=11&&bks<2)||(p.gold>=45&&bks<Math.floor(own.length/5))) tryUp('barracks',roboUpTargets(pid,'barracks').map(i=>S.tiles[i]).sort((a,b)=>Math.abs(dEd(a)-2)-Math.abs(dEd(b)-2)||dEd(a)-dEd(b)));
    if(!u.fort||matReach(pid,12)>=COSTS.fort[0]+4) tryUp('fort',roboUpTargets(pid,'fort').map(i=>S.tiles[i]).sort((a,b)=>dEd(a)-dEd(b)));
    if(!p.armor&&dk(pid,'cons','advance')>=3&&p.gold>=ARMOR_COST+8&&doArmor(pid)) ids.push(S.homes[pid]);   // Overclock (Construction)
  }""")
rep("""  for(const t of bks) while((t.bk||0)<3&&aiMat(pid,bkUpCost(pid,t.bk||0),spare[t.bk||0])&&doUpgradeBarracks(pid,t.id,lvl)) ids.push(t.id);""",
    """  for(const t of bks) while((t.bk||0)<3&&aiMat(pid,bkUpCost(pid,t.bk||0,t),spare[t.bk||0])&&doUpgradeBarracks(pid,t.id,lvl)) ids.push(t.id);""")

# ---------- Fortify: Dual Core, Sortie ----------
rep("""const fxPicksAt=(pid,eff)=>eff>=3?3:eff>=1?2:1;""","""const fxPicksAt=(pid,eff)=>isRobo(pid)?(dk(pid,'sprot','fortify')>=1?2:1):eff>=3?3:eff>=1?2:1;   // Dual Core (Siege Protocol)""")
rep("""f.rally=l>=3?1:0; }""","""f.rally=l>=3?1:0; f.mvx=isRobo(pid)&&dk(pid,'sprot','fortify')>=2; }   // Sortie (Siege Protocol): a real Move after the picks""")
rep("""  if(f.ph==='act'){ f.done.push(f.cur); f.cur=null; if(f.done.length<f.n&&fxPickList().some(k=>!f.done.includes(k))){ f.ph='pick'; return true; } }
  S.play.fx=null; return false;""","""  if(f.ph==='act'){ f.done.push(f.cur); f.cur=null; if(f.done.length<f.n&&fxPickList().some(k=>!f.done.includes(k))){ f.ph='pick'; return true; } }
  if(f.mvx&&!f.done.includes('move')){ f.ph='act'; f.cur='move'; S.play.moves=0; return true; }   // Sortie
  S.play.fx=null; return false;""")
rep("""  if(f&&(f.ph==='regroup'||(f.ph==='act'&&f.done.length+1<f.n))) return false;""",
    """  if(f&&(f.ph==='regroup'||(f.ph==='act'&&(f.done.length+1<f.n||(f.mvx&&f.cur!=='move'&&!f.done.includes('move')))))) return false;""")
rep("""    f.done.push(k);
  }
  S.play.fx=null;""","""    f.done.push(k);
  }
  if(S.play.fx.mvx&&!S.over){ const f=S.play.fx; f.ph='act'; f.cur='move'; S.play.moves=0; yield* aiMoveGen(pid,0); }   // Sortie (Siege Protocol)
  S.play.fx=null;""")

# ---------- trades: Recompile, Rebuild, Refit ----------
rep("""// ---------- Advancements ----------
function doUpgradeBarracks(pid,i,lvl){""","""// Robot trades (Mobilize): Recompile in Advancements (5 Brawlers for a Knight), Rebuild and Refit in Recruit
const ROBO_TRADES={ak:{a:'advance',l:2,from:'brawler',n:5,to:'rknight',name:'Recompile'},rk:{a:'recruit',l:2,from:'brawler',n:8,to:'rknight',name:'Rebuild'},rl:{a:'recruit',l:3,from:'rarch',n:5,to:'rlong',name:'Refit'}};
const tradesAt=t=>(t&&t.owner===0&&isRobo(0)&&!fxOn())?Object.keys(ROBO_TRADES).filter(k=>{ const x=ROBO_TRADES[k]; return curAction()===x.a&&dk(0,'mobil',x.a)>=x.l&&((t.army||{})[x.from]|0)>=x.n; }):[];
function roboTrade(id,k){
  const t=S.tiles[id], x=ROBO_TRADES[k]; if(!x||!tradesAt(t).includes(k)) return;
  const rdy=((t.ready||{})[x.from]|0)>=x.n; takeUnits(t,{[x.from]:x.n}); addUnits(t,x.to,1,rdy);
  addLog(`You trade ${x.n} ${unitPl(x.from,x.n)} for a ${unitName(x.to)} (${x.name}).`,0); render(); }
const roboTradeHtml=()=>{ const t=ui.sel!=null?S.tiles[ui.sel]:null, ks=tradesAt(t); if(!ks.length) return '';
  return `<div class="btns" style="margin-top:.5em">${ks.map(k=>{ const x=ROBO_TRADES[k]; return `<button data-act="rtrade" data-k="${k}">${x.name}: ${x.n} ${unitPl(x.from,x.n)} → 1 ${unitName(x.to)}</button>`; }).join('')}</div>`; };
// ---------- Advancements ----------
function doUpgradeBarracks(pid,i,lvl){""")
rep("""  else if(a==='robodone'){ ui.roboUp=null; render(); }""","""  else if(a==='robodone'){ ui.roboUp=null; render(); }
  else if(a==='rtrade') roboTrade(ui.sel,b.dataset.k);""")
rep("""  return h;
}
function renderPanel(){""","""  h+=roboTradeHtml();
  return h;
}
function renderPanel(){""")
rep("""roboUpgrade=undoable(roboUpgrade);""","""roboUpgrade=undoable(roboUpgrade); roboTrade=undoable(roboTrade);""")

# ---------- Laser Strike (Onslaught) ----------
rep("""function fireTreb(i,j){""","""function fireTreb(i,j,nm){""")
rep("""trebuchet ${hits?`hits: ${kl} unit${kl===1?'':'s'} killed""","""${nm||'trebuchet'} ${hits?`hits: ${kl} unit${kl===1?'':'s'} killed""")
rep("""function aiTrebTarget(i){""","""// Laser Strike (Onslaught): the Laser Tanks on a hex fire at an enemy hex next door like a trebuchet, with no battle (twice with Double Strike). Uses a move.
const laserOk=(pid,from,to)=>{ const s=S.tiles[from], b=S.tiles[to]; return isRobo(pid)&&dk(pid,'onsl','move')>=2&&s.owner===pid&&((s.ready||{}).ltank|0)>0&&b.owner>=0&&b.owner!==pid&&b.troops>0&&nbrs(from).includes(to)&&movesLeft()>0; };
function doLaser(pid,from,to){
  if(!laserOk(pid,from,to)) return null;
  const s=S.tiles[from], n=s.ready.ltank; s.ready.ltank=0; syncT(s); S.play.moves=(S.play.moves||0)+1;
  const shots=[]; for(let q=0;q<(dk(pid,'onsl','move')>=3?2:1);q++) if(S.tiles[to].troops>0) shots.push(fireTreb(from,to,'laser strike'));
  return {n,shots,kl:shots.reduce((a,x)=>a+x.kl,0),hits:shots.reduce((a,x)=>a+x.hits,0)};
}
function laserStrike(from,to){
  if(!isHumanTurn()||curAction()!=='move') return; const r=doLaser(0,from,to); if(!r) return;
  ui.undo=[]; ui.undoLocked=true; ui.sel=null;
  ui.notes.push(`<span class="px px-move" aria-hidden="true"></span> Laser Strike: ${r.shots.length} shot${r.shots.length>1?'s':''}, ${r.hits} hit${r.hits===1?'':'s'}, ${r.kl} unit${r.kl===1?'':'s'} destroyed`);
  render(); }
function aiLaser(pid){ const ids=[]; if(!isRobo(pid)||dk(pid,'onsl','move')<2) return ids;
  S.tiles.filter(t=>t.owner===pid&&((t.ready||{}).ltank|0)>0).forEach(t=>{ const j=nbrs(t.id).filter(x=>laserOk(pid,t.id,x)).sort((a,b)=>tp(S.tiles[b])-tp(S.tiles[a]))[0]; if(j!=null&&doLaser(pid,t.id,j)) ids.push(j); });
  return ids; }
function aiTrebTarget(i){""")
rep("""    else if(a==='move'){ S.play.moves=0; yield* aiMoveGen(pid,lvl); }""","""    else if(a==='move'){ S.play.moves=0; const lz=aiLaser(pid); if(lz.length) yield {kind:'flash',ids:lz};
      yield* aiMoveGen(pid,isRobo(pid)?(dk(pid,'mobil','move')>=2?1:0):lvl); }""")
rep("""  const mf=moveFilter(from,to,lvl), ks=byStrength(s.ready||{}).filter(k=>!mf||mf(k)), pick={}; ks.forEach(k=>pick[k]=0);
  if(mf) text+=moveFilterNote(from,to);""","""  const mf=moveFilter(from,to,lvl), ks=byStrength(s.ready||{}).filter(k=>!mf||mf(k)), pick={}; ks.forEach(k=>pick[k]=0);
  if(mf) text+=moveFilterNote(from,to);
  const lz=fight&&laserOk(0,from,to);
  if(lz) text+=`<br><b>Laser Strike</b>: your ${s.ready.ltank} Laser Tank${s.ready.ltank>1?'s':''} can fire from here instead, like a trebuchet${dk(0,'onsl','move')>=3?' (twice)':''}, with no battle.`;""")
rep("""<button id="mvall">${verb} all</button>""","""<button id="mvall">${verb} all</button>${lz?'<button id="mvlaser">Laser strike</button>':''}""")
rep("""  $('#mc').onclick=()=>{closeModal();render();};
}""","""  $('#mc').onclick=()=>{closeModal();render();};
  if(lz) $('#mvlaser').onclick=()=>{ closeModal(); laserStrike(from,to); };
}""")
open(p,'w').write(s); print('patch3 ok')
s=open(p).read()
rep("""Do as many as you can afford, all paid in materials: upgrade a barracks""","""Do as many as you can afford, all paid in materials: ${isRobo(pid)?`add a Barracks or Fortress to one of your markets at your home castle (${COSTS.barracks[0]} each), `:''}upgrade a barracks""")
open(p,'w').write(s); print('patch3b ok')

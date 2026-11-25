"""Ethan, 2026-11-24: upgrades for the new cards (claude/card-upgrades-new-cards-draft.md). Card upgrades come back on,
for every faction (the Mythical too); the old per-card and generic upgrade effects are off. nu_module.js holds the rules.
Usage: python3 patch_board.py index.html"""
import json, sys, os, re
D=os.path.dirname(os.path.abspath(__file__))
p=sys.argv[1]; R=os.path.dirname(os.path.abspath(p))+'/'
ix=open(p,encoding='utf8').read()
k='window.ARENA_HTML="'; i=ix.find(k)+len(k); j=i
while True:
    j=ix.find('"',j); bs=0; q=j-1
    while ix[q]=='\\': bs+=1; q-=1
    if bs%2==0: break
    j+=1
ar=json.loads('"'+ix[i:j]+'"')
head, tail = ix[:i], ix[j:]
def rep(t,a,b,n=1):
    c=t.count(a); assert c==n,(c,a[:110]); return t.replace(a,b)
B=head+'\u0000'+tail   # board code (the arena string is kept out of the way)
NU=open(D+'/nu_module.js',encoding='utf8').read()
# --- switches ---
B=rep(B,"const CARD_UPS_ON=false;   // Ethan, 2026-11-23: card upgrades off while the new cards settle (no favors toward upgrades, no faction card upgrades)",
        "const CARD_UPS_ON=true;    // Ethan, 2026-11-24: on again, with the new cards' own upgrades (NU_UPS) for every faction")
B=rep(B,"const cardUps=pid=>CARD_UPS_ON&&(isDino(pid)||isRobo(pid)||isMamm(pid));","const cardUps=pid=>CARD_UPS_ON;")
B=rep(B,"const dk=(pid,cid,a)=>(S&&S.play&&S.current===pid&&cardUps(pid)&&","const dk=(pid,cid,a)=>(!NEW_UPS&&S&&S.play&&S.current===pid&&cardUps(pid)&&")
B=rep(B,"const cardLv=(pid,cid,a)=>{ const c=","const cardLv=(pid,cid,a)=>{ if(NEW_UPS) return 0; const c=")
# the module, right after cardLv
a=B.find("const cardLv=(pid,cid,a)=>{"); e=B.find("\n",a)+1
B=B[:e]+NU+B[e:]
B=re.sub(r"const curLvl=\(\)=>S&&S\.play\?\(isDino\(S\.current\).*?:0;", "const curLvl=()=>S&&S.play?(NEW_UPS?(curAction()==='move'&&!regrouping()?nuMoveLvl(S.current):0):0):0;   // the new cards: only Climb changes how a Move plays", B, count=1)
assert "nuMoveLvl(S.current)" in B
# --- the Mythical upgrade too ---
B=rep(B,"const upgradeDue=(pid,cid)=>CARD_UPS_ON&&!isMyth(pid)&&","const upgradeDue=(pid,cid)=>CARD_UPS_ON&&")
B=rep(B,"  if(isMyth(pid)||!CARD_UPS_ON) return '';   // Mythical cards don't upgrade yet","  if(!CARD_UPS_ON) return '';   // (the Mythical upgrade too since 2026-11-24)//")
B=rep(B,"const fvTxt=!CARD_UPS_ON?'':isMyth(0)?'Mythical cards don\\'t upgrade yet.':","const fvTxt=!CARD_UPS_ON?'':")
B=rep(B,"  if(isMyth(pid)&&a!=='fortify') return mythActionDesc(a,pid);","  if(isMyth(pid)&&a!=='fortify') return mythActionDesc(a,pid)+(dUp(pid,cid,a)&&lvl?`. ${DCARD[cid][a].slice(0,lvl).map(x=>`${x[0]}: ${x[1]}`).join('. ')}`:'');")
B=rep(B,"${fid==='dinos'||fid==='robots'||fid==='mammals'?`<p>Every ${f.name.replace(/s$/,'')} card has its own upgrades for each of its actions:</p>","${CARD_UPS_ON&&DCARD[f.cards[0].id]?`<p>Every card has its own upgrades for each of its actions (every 2nd time you play a card, one of its actions goes up a level):</p>")
B=rep(B,"const convPrice=(t,k)=>MYTH_CONV[k].m-(mageLvAt(t)>=3?1:0);","const convPrice=(t,k)=>MYTH_CONV[k].m-(mageLvAt(t)>=3?1:0)-mythOff(t.owner,k);   // and the card upgrades' cheaper units")
B=rep(B,"const magePrice=pid=>MYTH.mageBase+Math.max(0,mageTotal(pid)-4)+mlvOf(pid)-(mlvOf(pid)>=3?1:0);","const magePrice=pid=>MYTH.mageBase+Math.max(0,mageTotal(pid)-4)+mlvOf(pid)-(mlvOf(pid)>=3?1:0)-mythOff(pid,'mage');")
B=rep(B,"  t.tree=1; t.root=MYTH.treeTurns;","  t.tree=1; t.root=nk(pid,1,'build')>=1?1:MYTH.treeTurns;   // Quick Roots (card 1 Build)")
# --- moves ---
B=rep(B,"+modsOf(pid).movesPerAction+mammMoves(pid)+(isMyth(pid)?1:0);   // the Mythical: 3 moves","+modsOf(pid).movesPerAction+mammMoves(pid)+(isMyth(pid)?1:0)+(nk(pid,1,'move')>=1?1:0)+(nk(pid,1,'move')>=3?1:0);   // the Mythical: 3 moves; Long March and Charge (card 1)")
B=rep(B,"const chargeOnly=pid=>(dk(pid,'stamp','move')>=1||dk(pid,'tusks','move')>=1)&&","const chargeOnly=pid=>(dk(pid,'stamp','move')>=1||dk(pid,'tusks','move')>=1||nk(pid,1,'move')>=3)&&")
B=rep(B,"  if(regrouping()&&pid===S.current) return regroupTargets(from,(dk(pid,'sprot','fortify')>=3&&from===S.homes[pid])?99:fxReach());   // Home Link (Siege Protocol)",
"""  if(regrouping()&&pid===S.current){ const c3=nk(pid,3,'fortify'), hm=from===S.homes[pid];   // Home Roads, Home Highways, Open Roads (card 3 Fortify)
    const rt=regroupTargets(from,(c3>=3||(c3>=2&&hm))?99:(c3>=1&&hm)?3:fxReach());
    if(nk(pid,5,'fortify')>=1&&S.play.fx&&!S.play.fx.oc) for(const x of nbrs(from)){ const X=S.tiles[x]; if(X.owner===-1&&!(X.troops>0)&&X.terrain==='plain'&&!X.castle&&!homeGuards(X)) rt.push(x); }   // Outpost (card 5)
    return rt; }""")
B=rep(B,"""  // runs through your own hexes
  let frontier=[from]; const seen=new Set([from]);""","""  if(nk(pid,1,'move')>=1) for(const a of nbrs(from)){ const A=S.tiles[a]; if(!canEnter(a,lvl)||A.owner!==-1||A.troops>0||A.castle) continue;   // Long March (card 1): across two empty hexes
    for(const b of nbrs(a)){ const B=S.tiles[b]; if(b!==from&&canEnter(b,lvl)&&B.owner===-1&&!(B.troops>0)&&!B.castle) out.add(b); } }
  // runs through your own hexes
  let frontier=[from]; const seen=new Set([from]);""")
B=rep(B,"""  } else {
    res.kind = prev===-1?'claim':'capture';
  }""","""  } else {
    res.kind = prev===-1?'claim':'capture';
    if(prev===-1&&regrouping()&&S.play&&S.play.fx) S.play.fx.oc=1;   // Outpost used
    if(prev===-1&&!regrouping()&&nk(A.owner,1,'move')>=1&&man(from,to)===2){   // Long March: the hex crossed is claimed too
      const m=nbrs(from).find(x=>nbrs(to).includes(x)&&S.tiles[x].owner===-1&&!(S.tiles[x].troops>0)&&!S.tiles[x].castle&&canEnter(x,lvl||0));
      if(m!=null){ const M=S.tiles[m]; M.owner=A.owner; M.army={}; M.ready={}; syncT(M); res.mid=m; addLog(`${p.name} claim two hexes in one move (Long March).`,p.id); } }
  }""")
B=rep(B,"  B.owner=A.owner; B.army={}; B.ready={}; addArmy(B,sel,false); B.braced=-1;","  B.owner=A.owner; B.army={}; B.ready={}; addArmy(B,sel,false); B.braced=-1; B.frz=0; B.buff=null;")
# --- battles: Sneak Attack, Volley, Rally Cry ---
B=rep(B,"  const p=S.players[pid], up=!!p.updNow, off=(dk(pid,'mobil','move')>=3||dk(pid,'tusks','move')>=2)&&","  const p=S.players[pid], up=!!p.updNow, off=(dk(pid,'mobil','move')>=3||dk(pid,'tusks','move')>=2||nk(pid,3,'move')>=2)&&")
B=rep(B,"aArm, dArm, surprise:off?1:0};","aArm, dArm, surprise:off?1:0, volley:nk(pid,3,'move')>=3?1:0};   // Volley (card 3 Move)")
B=rep(B,"  return (o.surprise?`<br>${S&&isMamm(S.current)?'Ambush':'Offline'}: a sneak attack.","  return (o.volley?'<br>Volley: your shooters fire once before the battle starts':'')+(o.surprise?`<br>${NEW_UPS?'Sneak Attack':S&&isMamm(S.current)?'Ambush':'Offline'}: a sneak attack.")
B=rep(B,"    const b=fightBattle(sel,defStart,{wall:W,bonus:defBonus(B),advD:defAdv(B),map:arenaMap(B,W),...ao});","    const b=fightBattle(sel,defStart,{wall:W,bonus:defBonus(B),advD:defAdv(B),map:arenaMap(B,W),...ao,hpA:buffOn(A)?NU_BUFF:0,hpD:buffOn(B)?NU_BUFF:0});")
B=rep(B,"""  let held=!!o.surprise;   // a Robot Offline sneak attack: the defenders can't attack until the attackers' first hit lands""","""  let held=!!o.surprise;   // a Robot Offline sneak attack: the defenders can't attack until the attackers' first hit lands
  if(o.volley){ const V={}; for(const k in A) if(UNIT_STATS[k].rng&&A[k].n>0) V[k]=A[k];   // Volley (card 3 Move): the attackers' shooters fire once before it starts
    if(Object.keys(V).length&&Object.keys(D).length){ const h=strike(V,D,0,1,1,{wall:0,arm:arm[1],plus:o.aPlus||0,shieldFoe:shield[1],shieldMine:0,stunned:{},sprint:0,rally:false,missOne:false});
      if(o.dArm) for(const k in h.dmg) h.dmg[k]/=ARMOR_HP; if(o.hpD) for(const k in h.dmg) h.dmg[k]/=o.hpD; apply(D,h.dmg); ev.volley=1; if(h.any) held=false; } }""")
B=rep(B,"    if(o.dArm) for(const k in hitsOnD.dmg) hitsOnD.dmg[k]/=ARMOR_HP;   // Armor: 10% more health","    if(o.dArm) for(const k in hitsOnD.dmg) hitsOnD.dmg[k]/=ARMOR_HP;   // Armor: 10% more health\n    if(o.hpD) for(const k in hitsOnD.dmg) hitsOnD.dmg[k]/=o.hpD;   // Rally Cry: 10% more health")
B=rep(B,"    if(o.aArm) for(const k in hitsOnA.dmg) hitsOnA.dmg[k]/=ARMOR_HP;\n","    if(o.aArm) for(const k in hitsOnA.dmg) hitsOnA.dmg[k]/=ARMOR_HP;\n    if(o.hpA) for(const k in hitsOnA.dmg) hitsOnA.dmg[k]/=o.hpA;\n")
B=rep(B,"mods:fightMods(A.owner,lvl||0,B.owner)};","mods:Object.assign(fightMods(A.owner,lvl||0,B.owner),{bufA:buffOn(A)?1:0,bufD:buffOn(B)?1:0})};")
B=rep(B,"  return {sneak:o.surprise?1:0, plus:","  return {sneak:o.surprise?1:0, volley:o.volley?1:0, plus:")
B=rep(B,"  return [m.sneak?`${a} Offline sneak attack: the defenders can't fight back until the attackers land their first hit`:'',",
        "  return [m.volley?`${a} shooters fire a free volley before the battle (Volley)`:'', m.bufA?`${a} army is rallied: +10% health (Rally Cry)`:'', m.bufD?`${f.att===0?'Their':'Your'} army is rallied: +10% health (Rally Cry)`:'', m.sneak?`${a} sneak attack: the defenders can't fight back until the attackers land their first hit`:'',")
B=rep(B,"    if(fm.armA){ mods.plus[tA]+=ARMOR_DMG; mods.hp[tA]=ARMOR_HP; } if(fm.armD){ mods.plus[1-tA]+=ARMOR_DMG; mods.hp[1-tA]=ARMOR_HP; }   // Armor (The Hunt)",
        "    if(fm.armA){ mods.plus[tA]+=ARMOR_DMG; mods.hp[tA]=ARMOR_HP; } if(fm.armD){ mods.plus[1-tA]+=ARMOR_DMG; mods.hp[1-tA]=ARMOR_HP; }   // Armor (The Hunt)\n    if(fm.bufA) mods.hp[tA]*=NU_BUFF; if(fm.bufD) mods.hp[1-tA]*=NU_BUFF; if(fm.volley) mods.volley=tA;   // Rally Cry, Volley")
B=rep(B,"+(fm.sneak?' · Sneak attack':'')+(fm.plus?' · Updated':'');","+(fm.sneak?' · Sneak attack':'')+(fm.volley?' · Volley':'')+(fm.plus?' · Updated':'');")
# --- turns, income, harvest, Fortify ---
B=rep(B,"S.tiles.forEach(t=>{if(t.owner===p.id){t.ready=Object.assign({},t.army||{}); delete t.ready.alamo; syncT(t); if(t.braced===p.id) t.braced=-1;}});",
        "S.tiles.forEach(t=>{if(t.owner===p.id){t.ready=Object.assign({},t.army||{}); delete t.ready.alamo; if(t.frz>0){ t.ready={}; t.frz--; } syncT(t); if(t.braced===p.id) t.braced=-1;}});   // a frozen army (Freeze) can't move")
B=rep(B,"  return {tiles,castles,markets,land,nest,tusk,total:castles*m.castleGold+land+markets*m.marketGold+nest+tusk};",
        "  const nu=nuIncome(pid);   // Castle Tax, Tolls, Vaults (card 5 Advancements)\n  return {tiles,castles,markets,land,nest,tusk,nu,total:castles*m.castleGold+land+markets*m.marketGold+nest+tusk+nu};")
B=rep(B,"  return {tiles,castles,markets:0,land:0,nest:0,trees,treeM,home,total:home+treeM};",
        "  const nu=nuIncome(pid);   // Castle Magic, Tree Magic (card 4 Harvest); Castle Tax (card 5 Advancements)\n  return {tiles,castles,markets:0,land:0,nest:0,trees,treeM,home,nu,total:home+treeM+nu};")
B=rep(B,"""  if(a==='harvest'){
    // Industrialization (Robots): every barracks also pays like a market""","""  if(a==='harvest'&&p.noHarv){ const skip=p.noHarv===S.turn; if(skip||p.noHarv<S.turn) p.noHarv=0;   // taken early (Early Harvest)
    if(skip){ addLog(`${p.name} get nothing from this Harvest: they took it early.`,pid); return `<span class="px px-harvest" aria-hidden="true"></span> Harvest: nothing, you took it early`; } }
  if(a==='harvest'){
    const nh=nuHarvest(pid); if(nh.g) p.gold+=nh.g; if(nh.m) p.mat=matOf(pid)+nh.m; if(nh.g||nh.m) addLog(`${p.name} harvest more: ${nh.why.join(', ')}.`,pid);
    const nhTxt=nh.why.length?` (${nh.why.join(', ')})`:'';
    // Industrialization (Robots): every barracks also pays like a market""")
B=rep(B,"""    return `<span class="px px-harvest" aria-hidden="true"></span> Harvest: +${g} ${cur$(pid)}${rain?""","""    return `<span class="px px-harvest" aria-hidden="true"></span> Harvest: +${g+nh.g} ${cur$(pid)}${nh.m?`, +${matTxt(nh.m)}`:''}${nhTxt}${rain?""")
B=rep(B,"  if(isMamm(pid)&&S.play) out.push(...mammFortify(pid,raw));\n","  if(isMamm(pid)&&S.play) out.push(...mammFortify(pid,raw));\n  if(S.play) out.push(...nuFortify(pid));   // Border Guard, Border Wall (card 5)\n")
# --- action start and end ---
B=rep(B,"  ui.notes.push(...dinoActionStart(S.current));\n  if(curAction()==='move') S.play.moves=0;","  ui.notes.push(...nuActionStart(S.current),...dinoActionStart(S.current));\n  if(curAction()==='move') S.play.moves=0;")
B=rep(B,"""    else if(isMyth(pid)&&(a==='recruit'||a==='build'||a==='advance')) yield {kind:'flash',ids:mythAi(pid,a,card.actions.slice(s+1))};""",
        """    else if(isMyth(pid)&&(a==='recruit'||a==='build'||a==='advance')){ nuActionStart(pid); const nx=a==='advance'?nuAiAdvance(pid):[]; yield {kind:'flash',ids:nx.concat(mythAi(pid,a,card.actions.slice(s+1)))}; }""")
B=rep(B,"      dinoActionStart(pid); const fr=freeTroops(pid,lvl), bi=card.actions.indexOf('build');","      nuActionStart(pid); dinoActionStart(pid); const fr=freeTroops(pid,lvl), bi=card.actions.indexOf('build');")
B=rep(B,"    else if(a==='build'){ dinoActionStart(pid); yield {kind:'flash',ids:aiBuild(pid,lvl,card.actions.slice(s+1))}; }",
        "    else if(a==='build'){ nuActionStart(pid); dinoActionStart(pid); yield {kind:'flash',ids:aiBuild(pid,lvl,card.actions.slice(s+1))}; nuActionEnd(pid); }")
B=rep(B,"    else if(a==='advance'){ dinoActionStart(pid); if(mammOn(pid,raw)) S.play.freeWalls=FREE_WALLS;   // Reforest",
        "    else if(a==='advance'){ nuActionStart(pid); dinoActionStart(pid); const nx=nuAiAdvance(pid); if(nx.length) yield {kind:'flash',ids:nx}; if(mammOn(pid,raw)) S.play.freeWalls=FREE_WALLS;   // Reforest")
B=rep(B,"      yield* aiMoveGen(pid,isRobo(pid)?(dk(pid,'mobil','move')>=2?1:0):isMamm(pid)?(dk(pid,'roam','move')>=3?1:0):lvl); }",
        "      yield* aiMoveGen(pid,NEW_UPS?nuMoveLvl(pid):isRobo(pid)?(dk(pid,'mobil','move')>=2?1:0):isMamm(pid)?(dk(pid,'roam','move')>=3?1:0):lvl); }")
B=rep(B,"""  const card=cardOf(0,S.play.card);
  ui.sel=null; ui.battle=null; ui.wallFor=null; ui.roboUp=null; ui.mvBk=null;""","""  const card=cardOf(0,S.play.card);
  nuActionEnd(0); ui.nuMode=null;   // Market Day
  ui.sel=null; ui.battle=null; ui.wallFor=null; ui.roboUp=null; ui.mvBk=null;""")
# --- prices ---
B=rep(B,"const costOf=(k,lvl,t)=>{ const c=COSTS[k][lvl||0], pid=S&&S.play?S.current:-1;","const costOf=(k,lvl,t)=>nuCost(k,costOf0(k,lvl,t),t);   // the new cards' Free and Cheap Markets and Barracks\nconst costOf0=(k,lvl,t)=>{ const c=COSTS[k][lvl||0], pid=S&&S.play?S.current:-1;")
B=rep(B,"function dinoBuilt(pid,k,price){ ","function dinoBuilt(pid,k,price){ nuBuilt(pid,k,price); ")
B=rep(B,"function roboUpCost(pid,k,t){ let c=COSTS[k][0];","function roboUpCost(pid,k,t){ let c=COSTS[k][0]; const rp=S.players[pid];\n  if(k==='barracks'&&(rp.rbkFree|0)>0) return 0; if(k==='barracks'&&rp.rbkOff===S.turn) c--;   // Free Barracks, Cheap Barracks (the new cards)")
B=rep(B,"  spendMat(pid,c); t[k]=1; noteUnlock(pid,k,t);","  spendMat(pid,c); t[k]=1; noteUnlock(pid,k,t); if(k==='barracks'&&c===0&&(p.rbkFree|0)>0) p.rbkFree--;")
B=rep(B,"  const free=((lvl>=1&&lv===0)||dk(pid,'tusks','advance')>=1)&&!S.play.freeBk,","  const free=((lvl>=1&&lv===0)||dk(pid,'tusks','advance')>=1||nk(pid,2,'advance')>=3)&&!S.play.freeBk,")
# --- the card column, the map, taps ---
B=rep(B,"function stepBody(){\n","function stepBody(){ return nuPanel()+stepBody0(); }\nfunction stepBody0(){\n")
B=rep(B,"  if(isHumanTurn()&&curAction()==='advance'&&ui.mvBk!=null) mammBkSpots(0,ui.mvBk).forEach(j=>hl.add(j));   // Den Move",
        "  if(isHumanTurn()&&curAction()==='advance'&&ui.mvBk!=null) mammBkSpots(0,ui.mvBk).forEach(j=>hl.add(j));   // Den Move\n  nuHl().forEach(j=>hl.add(j));   // Border Claim, Freeze, Relocate")
B=rep(B,"function onCell(i){\n  if(!isHumanTurn()) return;\n","function onCell(i){\n  if(!isHumanTurn()) return;\n  if(ui.nuMode&&nuCell(i)) return;   // Border Claim, Freeze, Relocate\n")
B=rep(B,"mammFreeBkH=undoable(mammFreeBkH);","nuAct=undoable(nuAct); nuCell=undoable(nuCell);\nmammFreeBkH=undoable(mammFreeBkH);")
B=rep(B,"  else if(a==='trade') openTrade();\n","  else if(a==='nu') nuAct(b.dataset.m,b.dataset.k);\n  else if(a==='trade') openTrade();\n")
# Scouts: without it, an enemy hex shows how many units, not which
B=rep(B,"${sel.owner===0?'Here':'Enemy'}: ${armyList(sel.army)}","${sel.owner===0?'Here':'Enemy'}: ${sel.owner===0||nuSee(0)?armyList(sel.army):foeCount(sel)}",3)
B=rep(B,"text=`${b.troops?`Defending: <span class=\"mvfoe\">${armyList(b.army)}</span>`","text=`${b.troops?`Defending: <span class=\"mvfoe\">${nuSee(0)?armyList(b.army):foeCount(b)}</span>`")
head,tail=B.split('\u0000')
ix=head+json.dumps(ar,ensure_ascii=False)[1:-1].replace('</script','<\\/script')+tail
open(p,'w',encoding='utf8').write(ix); print('board ok')

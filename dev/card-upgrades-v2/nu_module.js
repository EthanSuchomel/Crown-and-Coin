// ---------- The new cards' upgrades (Ethan, 2026-11-24) ----------
// Every faction plays the same five cards (1st to 5th in its deck), so the upgrades go by the card's place, not its name.
// Every 2nd favor still raises one action on the card a level (at most 3); where a later level names a bigger amount
// of the same thing it replaces the earlier one (Ethan: "Yes replace"). The Mythical have no markets, barracks or
// fortresses: an upgrade about one of those makes a unit 1 magic cheaper instead, by its level (1 the Minotaur,
// 2 the Griffin, 3 the Mage). The upgrade names are Claude's placeholders.
const NEW_UPS=true;
const NU_SET={dinos:'mega',robots:'rknight',mammals:'rhino',mythical:'griffin'};   // card 2 Recruit's level 3 unit
const NU_SETN={dinos:'Megaraptor',robots:'Robot Knight',mammals:'Rhino',mythical:'Griffin'};
const NU_BASN={dinos:'Pachycephalosaurus',robots:'Robot Brawler',mammals:'Gorilla',mythical:'Minion'};
const NU_BUFF=1.1, NU_FREEZE=2;
const NU_HARV_M=[0,2,5,10], NU_HARV_MY=[0,1,3,5];      // card 5 Harvest: materials (the Mythical: magic)
const NU_CASTLE=[0,3,10,20], NU_CASTLE_MY=[0,1,5,10];  // card 5 Advancements: more a turn for every captured castle
const NU_MUSTER=[0,2,5,10];                             // card 3 Recruit: basic units at the home castle
// [name, text] for each level; f(fid) picks the faction's version
const nuT=(fid,o)=>typeof o==='function'?o(fid):o;
const NU_UPS=[null,
  {move:[['Long March','one more move, and a move can cross two empty hexes and claim them both'],['Climb','troops can move onto mountains'],['Charge','one more move, if it is an attack']],
   build:[f=>f==='mythical'?['Quick Roots','a Mage that plants a Life Tree in this action stays 1 turn instead of 2']:['Free Market','your first market in this action is free'],
          f=>f==='mythical'?['Cheap Griffins','Griffins cost 1 magic less']:f==='robots'?['Free Barracks','your next factory barracks is free']:['Free Barracks','your first barracks in this action is free'],
          f=>f==='mythical'?['Gathered Magic','+2 magic when this action starts']:['Supplies','+3 materials when this action starts']],
   advance:[f=>f==='mythical'?['Stores','+1 magic when this action starts']:['Stores','+2 materials when this action starts'],
            f=>f==='mythical'?['Treasury','+3 magic instead']:['Treasury','also +5 gold'],
            f=>f==='mythical'?['Great Stores','+8 magic instead']:['Great Stores','+4 materials and +10 gold instead']]},
  {build:[f=>f==='mythical'?['Cheap Minotaurs','Minotaurs cost 1 magic less']:['Cheap Markets','markets cost 1 gold less'],
          f=>f==='mythical'?['Cheap Griffins','Griffins cost 1 magic less']:f==='robots'?['Cheap Barracks','factory barracks cost 1 material less this turn']:['Cheap Barracks','barracks cost 1 material less'],
          f=>f==='mythical'?['Cheap Mages','Mages cost 1 magic less']:['Market Day','at the end of this action, every market you own makes 1 gold']],
   advance:[['Border Claim','claim one empty, open hex on your border, without moving units there'],
            ['Early Harvest','at your home castle, take a Harvest now; your next Harvest then gives nothing'],
            f=>f==='mythical'?['Cheap Mages','Mages cost 1 magic less']:['Free Upgrade','your first barracks upgrade in this action is free']],
   recruit:[f=>['Home Recruit',`1 free ${NU_BASN[f]} at your home castle`],
            f=>f==='mythical'?['Cheap Griffins','Griffins cost 1 magic less']:['Barracks Recruits',`also 1 free ${NU_BASN[f]} at every barracks`],
            f=>f==='mythical'?['Champion','also 1 free Griffin at your home castle']:['Champions',`also 1 free ${NU_SETN[f]} at every barracks`]]},
  {recruit:[f=>['Muster',`2 free ${NU_BASN[f]}s at your home castle`],['Big Muster','5 instead'],['Great Muster','10 instead']],
   fortify:[['Home Roads','units from your home castle regroup up to 3 hexes'],['Home Highways','units from your home castle regroup anywhere in your land'],['Open Roads','every unit regroups anywhere in your land']],
   move:[['Climb','troops can move onto mountains'],['Sneak Attack',"the defenders can't attack until your units land their first hit"],['Volley','your shooters fire a free volley before the battle starts']]},
  {harvest:[f=>f==='mythical'?['Castle Magic','your home castle makes 1 more magic every turn']:['Rich Land','+1 gold for every hex you own'],
            f=>f==='mythical'?['Castle Wells','your home castle makes 3 more magic every turn instead']:['Quarry','also +1 material for every 3 hexes you own'],
            f=>f==='mythical'?['Tree Magic','every Life Tree also makes 1 more magic every turn']:['Richer Land','+2 gold for every hex you own instead']],
   build:[f=>f==='mythical'?['Cheap Minotaurs','Minotaurs cost 1 magic less']:['Relocate','move one of your buildings to a hex of yours next door'],
          f=>f==='mythical'?['Gathered Magic','+3 magic when this action starts']:['Supplies','+3 materials when this action starts'],
          f=>f==='mythical'?['Magic Fund','+5 magic when this action starts']:['Funding','+10 gold when this action starts']],
   advance:[['Scouts','tap an enemy hex to see its units (without this you only see how many)'],['Rally Cry','give one of your armies +10% health until the end of your next turn'],['Freeze','freeze one enemy army in place for its next 2 turns']]},
  {fortify:[['Outpost','one regroup move can claim an empty hex next to your land'],f=>['Border Guard',`every hex of yours touching an enemy gets 1 free ${NU_BASN[f]}`],['Border Wall','2 instead']],
   harvest:[f=>f==='mythical'?['Stockpile','+1 magic']:['Stockpile','+2 materials'],f=>f==='mythical'?['Big Stockpile','+3 magic instead']:['Big Stockpile','+5 materials instead'],f=>f==='mythical'?['Great Stockpile','+5 magic instead']:['Great Stockpile','+10 materials instead']],
   advance:[f=>f==='mythical'?['Castle Tax','every castle you captured makes 1 more magic every turn']:['Castle Tax','every castle you captured makes 3 more gold every turn'],
            f=>f==='mythical'?['Castle Tolls','5 more magic instead']:['Castle Tolls','10 more gold instead'],
            f=>f==='mythical'?['Castle Vaults','10 more magic instead']:['Castle Vaults','20 more gold instead']]}];
// the old per-card upgrades give way: DCARD now holds these, for each faction's own card ids
if(NEW_UPS){ for(const k in DCARD) delete DCARD[k];
  for(const fid in FACTIONS){ const F=FACTIONS[fid]; if(!F||!F.cards) continue;
    F.cards.forEach((c,n)=>{ const u=NU_UPS[n+1]; if(!u) return; DCARD[c.id]={}; c.actions.forEach(a=>{ if(u[a]) DCARD[c.id][a]=u[a].map(x=>nuT(fid,x)); }); }); } }
const nSlot=(pid,cid)=>facOf(pid).cards.findIndex(c=>c.id===cid)+1;   // 1-5: the card's place in its deck
const nCid=(pid,n)=>(facOf(pid).cards[n-1]||{}).id;
// an action's level on the nth card, whether or not it's being played
const nLv=(pid,n,a)=>{ if(!NEW_UPS||!S||!S.players[pid]) return 0; const cid=nCid(pid,n); if(!cid) return 0; const i=cardOf(pid,cid).actions.indexOf(a); return i<0?0:lvlOf(pid,cid,i); };
// ...and only while that card's action is being played (a Fortify's picks play basic)
const nk=(pid,n,a)=>(NEW_UPS&&S&&S.play&&S.current===pid&&nSlot(pid,S.play.card)===n&&cardAction()===a&&(a==='fortify'||!fxOn()))?lvlOf(pid,S.play.card,S.play.step):0;
const nuSee=pid=>nLv(pid,4,'advance')>=1;   // Scouts: enemy armies show their units
const buffOn=t=>!!(t&&t.buff&&t.owner===t.buff.pid&&S.turn<=t.buff.until);
const nuMoveLvl=pid=>(nk(pid,1,'move')>=2||nk(pid,3,'move')>=1)?1:0;   // Climb: onto mountains
// the Mythical's cheaper units: 1 magic off a unit while any upgrade that stands for it is owned
function mythOff(pid,k){ if(!NEW_UPS||pid<0||!isMyth(pid)) return 0;
  if(k==='minotaur') return (nLv(pid,2,'build')>=1||nLv(pid,4,'build')>=1)?1:0;
  if(k==='griffin') return (nLv(pid,1,'build')>=2||nLv(pid,2,'build')>=2||nLv(pid,2,'recruit')>=2)?1:0;
  if(k==='mage') return (nLv(pid,2,'build')>=3||nLv(pid,2,'advance')>=3)?1:0;
  return 0; }
// a Build's prices: Free Market and Free Barracks (card 1), Cheap Markets and Cheap Barracks (card 2)
function nuCost(k,c,t){ if(!NEW_UPS||!S||!S.play||curAction()!=='build') return c; const pid=S.current, b1=nk(pid,1,'build'), b2=nk(pid,2,'build');
  if(isMyth(pid)) return c;
  if(k==='market'){ if(b1>=1&&!S.play.nfm) return 0; if(b2>=1) c-=1; }
  if(k==='barracks'){ if(b1>=2&&!S.play.nfb&&!isRobo(pid)) return 0; if(b2>=2) c-=1; }
  return Math.max(0,c); }
function nuBuilt(pid,k,price){ if(!NEW_UPS||!S.play||price>0) return;
  if(k==='market'&&nk(pid,1,'build')>=1&&!S.play.nfm) S.play.nfm=1;
  else if(k==='barracks'&&nk(pid,1,'build')>=2&&!S.play.nfb) S.play.nfb=1; }
// what an action's upgrades do as it starts. Returns notes for the card column (once per action).
function nuActionStart(pid){
  if(!NEW_UPS||!S.play) return [];
  const P=S.play; P.nuS=P.nuS||{}; if(P.nuS[P.step]) return []; P.nuS[P.step]=1;
  const a=cardAction(), p=S.players[pid], out=[], my=isMyth(pid), f=p.faction, ic=`<span class="px px-${a}" aria-hidden="true"></span>`;
  const home=S.tiles[S.homes[pid]], hold=!!(home&&home.owner===pid), nm=(x,o)=>(DCARD[P.card]&&DCARD[P.card][a]&&DCARD[P.card][a][x])?DCARD[P.card][a][x][0]:o;
  const gain=(g,m,why)=>{ if(g) p.gold+=g; if(m) p.mat=matOf(pid)+m; if(g||m){ out.push(`${ic} ${why}: +${[g?`${g} ${cur$(pid)}`:'',m?matTxt(m):''].filter(Boolean).join(', ')}`); addLog(`${p.name} get ${[g?`${g} ${cur$(pid)}`:'',m?matTxt(m):''].filter(Boolean).join(' and ')} (${why}).`,pid); } };
  if(a==='build'){
    const b1=nk(pid,1,'build'), b2=nk(pid,2,'build'), b4=nk(pid,4,'build');
    if(b1>=3) my?gain(2,0,nm(2,'Gathered Magic')):gain(0,3,nm(2,'Supplies'));
    if(b4>=2) my?gain(3,0,nm(1,'Gathered Magic')):gain(0,3,nm(1,'Supplies'));
    if(b4>=3) gain(my?5:10,0,nm(2,'Funding'));
    if(!my){
      if(b1>=1) out.push(`${ic} Free Market: your first market in this action costs nothing`);
      if(b1>=2){ if(isRobo(pid)){ p.rbkFree=(p.rbkFree|0)+1; out.push(`${ic} Free Barracks: your next factory barracks is free`); } else out.push(`${ic} Free Barracks: your first barracks in this action costs nothing`); }
      if(b2>=1) out.push(`${ic} Cheap Markets: markets cost 1 gold less`);
      if(b2>=2){ if(isRobo(pid)){ p.rbkOff=S.turn; out.push(`${ic} Cheap Barracks: factory barracks cost 1 material less this turn`); } else out.push(`${ic} Cheap Barracks: barracks cost 1 material less`); }
      if(b2>=3) out.push(`${ic} Market Day: every market you own makes 1 gold at the end of this action`);
      if(b4>=1) out.push(`${ic} Relocate: you can move one of your buildings to a hex of yours next door`);
    } else if(b1>=1) out.push(`${ic} Quick Roots: a Mage that plants a Life Tree in this action stays 1 turn instead of 2`);
  }
  if(a==='advance'){
    const v1=nk(pid,1,'advance'), v2=nk(pid,2,'advance'), v4=nk(pid,4,'advance');
    if(v1>=1){ if(my) gain(v1>=3?8:v1>=2?3:1,0,nm(v1-1,'Stores')); else gain(v1>=3?10:v1>=2?5:0,v1>=3?4:2,nm(v1-1,'Stores')); }
    if(v2>=1&&!p.ai) out.push(`${ic} Border Claim: you can claim one empty, open hex on your border`);
    if(v2>=2&&!p.ai) out.push(`${ic} Early Harvest: you can take a Harvest now (your next Harvest then gives nothing)`);
    if(v2>=3&&!my) out.push(`${ic} Free Upgrade: your first barracks upgrade in this action is free`);
    if(v4>=2&&!p.ai) out.push(`${ic} Rally Cry: you can give one of your armies +10% health until the end of your next turn`);
    if(v4>=3&&!p.ai) out.push(`${ic} Freeze: you can freeze one enemy army for its next ${NU_FREEZE} turns`);
  }
  if(a==='recruit'){
    const r2=nk(pid,2,'recruit'), r3=nk(pid,3,'recruit'), bas=basicOf(pid), got=[];
    if(r2>=1&&hold){ addUnits(home,bas,1,true); got.push(`1 ${unitName(bas)} at your home castle`); }
    if(r2>=2&&!my){ let n=0; S.tiles.forEach(t=>{ if(t.owner===pid&&t.barracks){ addUnits(t,bas,t.barracks|0,true); n+=t.barracks|0; } }); if(n) got.push(`${n} ${unitPl(bas,n)} at your barracks`); }
    if(r2>=3){ const k=NU_SET[f]||bas;
      if(my){ if(hold){ addUnits(home,k,1,true); got.push(`1 ${unitName(k)} at your home castle`); } }
      else { let n=0; S.tiles.forEach(t=>{ if(t.owner===pid&&t.barracks){ addUnits(t,k,t.barracks|0,true); n+=t.barracks|0; } }); if(n) got.push(`${n} ${unitPl(k,n)} at your barracks`); } }
    if(r3>=1&&hold){ const n=NU_MUSTER[r3]; addUnits(home,bas,n,true); got.push(`${n} ${unitPl(bas,n)} at your home castle`); }
    if(got.length){ out.push(`${ic} Free units: ${got.join(', ')}`); addLog(`${p.name} get free units: ${got.join(', ').replace(/your/g,'their')}.`,pid); }
  }
  return out;
}
// Market Day (card 2 Build, level 3): every market pays 1 gold as the Build ends
function nuActionEnd(pid){
  if(!NEW_UPS||!S.play) return; const P=S.play; P.nuE=P.nuE||{}; if(P.nuE[P.step]) return;
  if(cardAction()==='build'&&!fxOn()&&nk(pid,2,'build')>=3&&!isMyth(pid)){ P.nuE[P.step]=1;
    const g=S.tiles.reduce((s,t)=>s+(t.owner===pid?(t.market|0):0),0); if(g){ S.players[pid].gold+=g; addLog(`${S.players[pid].name} get ${g} gold from their markets (Market Day).`,pid); } }
}
// a Harvest's extra: card 4 (gold and materials from land) and card 5 (materials). Returns {g, m, why}.
function nuHarvest(pid){
  const o={g:0,m:0,why:[]}; if(!NEW_UPS) return o; const my=isMyth(pid), tiles=S.tiles.filter(t=>t.owner===pid).length;
  const h4=nk(pid,4,'harvest'), h5=nk(pid,5,'harvest');
  if(!my&&h4>=1){ const g=tiles*(h4>=3?2:1); o.g+=g; o.why.push(`${h4>=3?'Richer Land':'Rich Land'} ${g}`); }
  if(!my&&h4>=2){ const m=Math.floor(tiles/3); o.m+=m; if(m) o.why.push(`Quarry ${matTxt(m)}`); }
  if(h5>=1){ if(my){ o.g+=NU_HARV_MY[h5]; o.why.push(`Stockpile ${NU_HARV_MY[h5]} magic`); } else { o.m+=NU_HARV_M[h5]; o.why.push(`Stockpile ${matTxt(NU_HARV_M[h5])}`); } }
  return o;
}
// every turn: captured castles (card 5 Advancements); the Mythical's home castle and trees (card 4 Harvest)
function nuIncome(pid){
  if(!NEW_UPS) return 0; const my=isMyth(pid), c5=nLv(pid,5,'advance'), cap=capCastlesOf(pid);
  let g=cap*(my?NU_CASTLE_MY:NU_CASTLE)[c5];
  if(my){ const h4=nLv(pid,4,'harvest'); if(mythHome(pid)) g+=h4>=2?3:h4>=1?1:0; if(h4>=3) g+=treesOf(pid); }
  return g;
}
// a Fortify's start: Border Guard and Border Wall (card 5)
function nuFortify(pid){
  const f5=nk(pid,5,'fortify'); if(f5<2) return [];
  const n=f5>=3?2:1, bas=basicOf(pid), ids=S.tiles.filter(t=>t.owner===pid&&t.terrain!=='water'&&nbrs(t.id).some(j=>S.tiles[j].owner>=0&&S.tiles[j].owner!==pid));
  ids.forEach(t=>addUnits(t,bas,n,true));
  if(ids.length) addLog(`${S.players[pid].name} get ${n} free ${unitPl(bas,n)} on each of their ${ids.length} border hex${ids.length===1?'':'es'}.`,pid);
  return [ids.length?`${n===2?'Border Wall':'Border Guard'}: +${n} ${unitPl(bas,n)} on ${ids.length} border hex${ids.length===1?'':'es'}`:'Border Guard: no hex of yours touches an enemy yet'];
}
// the hexes Border Claim can take: empty, open, unowned land next to yours (not a castle)
const nuClaimable=pid=>S.tiles.filter(t=>t.owner===-1&&!(t.troops>0)&&t.terrain==='plain'&&!t.castle&&nbrs(t.id).some(j=>S.tiles[j].owner===pid)).map(t=>t.id);
function nuClaim(pid,i){
  if(nk(pid,2,'advance')<1||S.play.nCl||!nuClaimable(pid).includes(i)) return false;
  const t=S.tiles[i], p=S.players[pid]; t.owner=pid; t.army={}; t.ready={}; syncT(t); t.braced=-1; S.play.nCl=1;
  if(t.crate){ t.crate=false; if(!isMyth(pid)){ p.mat=matOf(pid)+MAT_BONUS; } }
  if(t.bounty){ t.bounty=false; if(!isMyth(pid)) p.gold+=COIN_GOLD; }
  addLog(`${p.name} claim a hex on their border (Border Claim).`,pid); checkCastles(); return true; }
function nuEarly(pid){
  const p=S.players[pid], home=S.tiles[S.homes[pid]];
  if(nk(pid,2,'advance')<2||S.play.nEh||!home||home.owner!==pid) return '';
  S.play.nEh=1; const note=resolveInstant(pid,'harvest',0,0); p.noHarv=S.turn+1;
  addLog(`${p.name} take their next Harvest early (Early Harvest).`,pid);
  return note.replace('Harvest:','Early Harvest:');
}
function nuBuff(pid,i){ const t=S.tiles[i];
  if(nk(pid,4,'advance')<2||S.play.nBf||t.owner!==pid||!(t.troops>0)) return false;
  t.buff={pid,until:S.turn+1}; S.play.nBf=1; addLog(`${S.players[pid].name} rally an army: +10% health until the end of their next turn (Rally Cry).`,pid); return true; }
const nuFreezable=pid=>S.tiles.filter(t=>t.owner>=0&&t.owner!==pid&&t.troops>0).map(t=>t.id);
function nuFreeze(pid,i){ const t=S.tiles[i];
  if(nk(pid,4,'advance')<3||S.play.nFz||!nuFreezable(pid).includes(i)) return false;
  t.frz=NU_FREEZE; S.play.nFz=1; addLog(`${S.players[pid].name} freeze an army of the ${S.players[t.owner].name}: it can't move for ${NU_FREEZE} turns (Freeze).`,pid); return true; }
// Relocate (card 4 Build): one building moves to a hex of yours next door (a Robot factory moves whole)
const NU_MV_KINDS=['market','barracks','fort','wh'];
const nuMovable=(pid,t)=>(!t||t.owner!==pid)?[]:isRobo(pid)?(bCount(t)&&!t.castle?['factory']:[]):NU_MV_KINDS.filter(k=>(t[k]|0)>0);
function nuMoveSpots(pid,from,k){ const t=S.tiles[from];
  return nbrs(from).filter(j=>{ const b=S.tiles[j]; if(b.owner!==pid||b.terrain==='water'||b.terrain==='void') return false;
    if(k==='factory') return !b.castle&&!bCount(b);
    if((k==='barracks'||k==='fort')&&b.castle) return false; if(k==='wh'&&b.wh) return false;
    return bCount(b)<MAX_BUILDINGS; }); }
function nuMoveB(pid,from,k,to){
  if(nk(pid,4,'build')<1||S.play.nMb||!nuMovable(pid,S.tiles[from]).includes(k)||!nuMoveSpots(pid,from,k).includes(to)) return false;
  const a=S.tiles[from], b=S.tiles[to];
  if(k==='factory'){ for(const x of ['market','barracks','fort','bk','wh']){ b[x]=a[x]|0; a[x]=0; } }
  else { a[k]=(a[k]|0)-1; b[k]=(b[k]|0)+1; if(k==='barracks'){ const lv=a.bk|0; if(!a.barracks) a.bk=0; b.bk=Math.max(b.bk|0,lv); } }
  S.play.nMb=1; addLog(`${S.players[pid].name} move a ${k==='factory'?'factory':k==='wh'?'Watering Hole':BUILD_INFO[k].name.toLowerCase()} to the hex next door (Relocate).`,pid); return true; }
// the computer's Advancements powers: claim, rally its biggest army on the front, freeze the biggest enemy army near it
function nuAiAdvance(pid){
  if(!NEW_UPS||!S.play) return []; const ids=[], dE=bfs(foeTiles(pid));
  if(nk(pid,2,'advance')>=1&&!S.play.nCl){ const c=nuClaimable(pid).sort((x,y)=>((S.tiles[y].bounty||S.tiles[y].crate)?100:0)+fin(dE[y])-((S.tiles[x].bounty||S.tiles[x].crate)?100:0)-fin(dE[x])); if(c.length&&nuClaim(pid,c[0])) ids.push(c[0]); }
  if(nk(pid,4,'advance')>=2&&!S.play.nBf){ const own=S.tiles.filter(t=>t.owner===pid&&t.troops>0).sort((x,y)=>fin(dE[x.id])-fin(dE[y.id])||y.troops-x.troops); if(own.length&&nuBuff(pid,own[0].id)) ids.push(own[0].id); }
  if(nk(pid,4,'advance')>=3&&!S.play.nFz){ const dO=bfs(S.tiles.filter(t=>t.owner===pid).map(t=>t.id)), foes=nuFreezable(pid).filter(j=>fin(dO[j])<=2).sort((x,y)=>S.tiles[y].troops-S.tiles[x].troops); if(foes.length&&nuFreeze(pid,foes[0])) ids.push(foes[0]); }
  return ids;
}
// the card column: the Advancements powers, Relocate and Scouts
function nuPanel(){
  if(!NEW_UPS||!S.play) return '';
  const a=cardAction(), sel=ui.sel!=null?S.tiles[ui.sel]:null, my=isMyth(0), md=ui.nuMode, P=S.play, hint=x=>`<div class="nuhint" style="margin:.35em 0;font-size:.92em;opacity:.92">${x}</div>`;   // (the column's own hints are hidden while a card plays)
  let h='';
  if(sel&&sel.owner>=0&&sel.owner!==0&&sel.troops>0&&nuSee(0)&&curAction()!=='move') h+=`<div class="harmy">Enemy (Scouts): ${armyList(sel.army)}</div>`;
  if(fxOn()){ if(regrouping()&&nk(0,5,'fortify')>=1&&P.fx&&!P.fx.oc) h+=hint('Outpost: one regroup move can claim an empty hex next to your land.'); return h; }
  if(a==='build'&&!my&&nk(0,4,'build')>=1&&!P.nMb){
    if(md&&md.m==='mvb'){ const n=nuMoveSpots(0,md.from,md.k).length; h+=hint(n?`Relocate: tap a ringed hex of yours next door to move the ${md.k==='factory'?'factory':md.k==='wh'?'Watering Hole':BUILD_INFO[md.k].name.toLowerCase()} there.`:'Relocate: none of your hexes next door has room for it.')+`<div class="btns"><button data-act="nu" data-m="x">Cancel</button></div>`; }
    else { const ks=nuMovable(0,sel); h+=ks.length?`<div class="btns" style="margin:.3em 0">${ks.map(k=>`<button data-act="nu" data-m="mvb" data-k="${k}">Relocate: move this ${k==='factory'?'factory':k==='wh'?'Watering Hole':BUILD_INFO[k].name.toLowerCase()}</button>`).join('')}</div>`:hint('Relocate: tap one of your hexes with a building to move it to a hex of yours next door.'); }
  }
  if(a==='advance'){
    const v2=nk(0,2,'advance'), v4=nk(0,4,'advance'), bt=[];
    if(md&&md.m==='claim') h+=hint('Border Claim: tap a ringed hex to claim it.')+`<div class="btns"><button data-act="nu" data-m="x">Cancel</button></div>`;
    else if(md&&md.m==='freeze') h+=hint(`Freeze: tap a ringed enemy army to freeze it for its next ${NU_FREEZE} turns.`)+`<div class="btns"><button data-act="nu" data-m="x">Cancel</button></div>`;
    else {
      if(v2>=1&&!P.nCl&&nuClaimable(0).length) bt.push(`<button data-act="nu" data-m="claim">Border Claim: claim a hex</button>`);
      if(v2>=2&&!P.nEh&&S.tiles[S.homes[0]].owner===0) bt.push(`<button data-act="nu" data-m="early">Early Harvest: harvest now</button>`);
      if(v4>=2&&!P.nBf&&sel&&sel.owner===0&&sel.troops>0) bt.push(`<button data-act="nu" data-m="buff">Rally Cry: +10% health here</button>`);
      if(v4>=3&&!P.nFz&&nuFreezable(0).length) bt.push(`<button data-act="nu" data-m="freeze">Freeze an enemy army</button>`);
      if(bt.length) h+=`<div class="btns" style="margin:.3em 0">${bt.join('')}</div>`;
      if(v4>=2&&!P.nBf&&!(sel&&sel.owner===0&&sel.troops>0)) h+=hint('Rally Cry: tap one of your armies to give it +10% health until the end of your next turn.');
    }
  }
  return h;
}
const nuHl=()=>{ const md=ui.nuMode; if(!md||!isHumanTurn()||!S.play) return [];
  return md.m==='claim'?nuClaimable(0):md.m==='freeze'?nuFreezable(0):md.m==='mvb'?nuMoveSpots(0,md.from,md.k):[]; };
function nuAct(m,k){ if(!isHumanTurn()||!S.play) return;
  if(m==='x') ui.nuMode=null;
  else if(m==='claim'||m==='freeze') ui.nuMode={m};
  else if(m==='mvb'&&ui.sel!=null) ui.nuMode={m,from:ui.sel,k};
  else if(m==='early'){ const n=nuEarly(0); if(n) ui.notes.push(n); }
  else if(m==='buff'&&ui.sel!=null) nuBuff(0,ui.sel);
  render(); }
function nuCell(i){ const md=ui.nuMode; if(!md) return false; ui.nuMode=null;
  if(md.m==='claim'&&nuClaim(0,i)){ ui.sel=i; render(); return true; }
  if(md.m==='freeze'&&nuFreeze(0,i)){ render(); return true; }
  if(md.m==='mvb'&&nuMoveB(0,md.from,md.k,i)){ ui.sel=i; render(); return true; }
  return false; }
const foeCount=t=>`${t.troops} unit${t.troops===1?'':'s'}`;

import sys, json
P='/tmp/claude-0/-home-claude/fb256341-5d08-5e47-8b49-8c9035f9f7b9/scratchpad/cc/'
s=open(P+'cc_v134.html',encoding='utf-8').read()
def rep(old,new,count=1):
    global s
    n=s.count(old)
    if n!=count: print('COUNT',n,'for',old[:150]); sys.exit(1)
    s=s.replace(old,new)
art=json.load(open(P+'cardart.json'))

# ================= the Dinosaur cards' own upgrades =================
rep("const NAMED_UP={robots:ROBO_UP, dinos:DINO_UP, mammals:MAMM_UP};",
r"""const NAMED_UP={robots:ROBO_UP, mammals:MAMM_UP};   // the Dinosaurs have their own upgrades on every card (DCARD) since 2026-11-11
// ---------- Dinosaur cards (Ethan, 2026-11-11): each card has its own 3 upgrades for each of its actions.
// Every 2nd favor you still pick which action on the card goes up a level; its levels add up (except where one says "instead").
// The upgrade names are Claude's placeholders. ----------
const DCARD={
  stamp:{move:[['Charge','an extra move, if that move is an attack'],['Home Run','units from your home castle can move to any of your hexes'],['Two Herds','when you attack, the ready units on another of your hexes next to the target join in']],
         build:[['Free Market','your first market in this action is free'],['Supplies','+2 materials when this action starts'],['Cheap Nests','every building that costs materials costs just 1']],
         fortify:[['Hatchlings','1 free Pachycephalosaurus at every nesting ground'],['Raptor Brood','also 1 free Megaraptor at every nesting ground'],['New Nest','a free nesting ground: your next barracks costs nothing']]},
  pack:{harvest:[['Trade Calls','+1 gold for every market'],['Castle Tolls','+5 gold for every castle'],['Big Herd','+2 gold for every 5 of your units']],
        recruit:[['Calling','3 free Pachycephalosaurus at a nesting ground you pick'],['Raptor Call','also 1 free Megaraptor there'],['Castle Raptors','2 free Megaraptors at your home castle']],
        fortify:[['Join Up','one regroup move can go any distance through your land'],['On the Move','Move becomes one of Fortify\'s picks'],['Rally','rally every unit you have onto one of your hexes']]},
  siege:{fortify:[['Market Day','+2 gold for every market on your best market hex, once'],['Guardian','a free Alamosaurus guard at a nesting ground'],['Second Guardian','a second free Alamosaurus guard']],
         harvest:[['Quarry','+1 material for every 3 hexes you own'],['Big Quarry','+1 material for every 2 hexes instead'],['Castle Stores','+1 material for every castle']],
         move:[['Climb','troops can move onto mountains'],['Dash','troops go 2 hexes when both are empty'],['Over the Top','cross a mountain and attack on the far side in one move']]},
  hunt:{harvest:[['Hunting Grounds','1 gold for every hex you own, instead of every 2'],['Nest Feast','+2 gold for every nesting ground'],['Castle Feast','+5 gold for every castle']],
        recruit:[['Home Hunters','units bought at your home castle cost 1 gold less'],['Castle Herds','2 free Pachycephalosaurus at every castle'],['Nest Hunters','units bought at a barracks cost 1 gold less']],
        advance:[['Quick Nests','barracks upgrades cost 1 material less'],['Cheap Guards','Alamosaurus guards cost 3 gold less'],['Armor','buy Armor at your home castle: 40 gold, all your units +2 damage and +10% health, in every battle']]},
  nest:{harvest:[['Gathering','+3 materials when this action starts'],['Stockpile','+5 materials instead'],['Great Store','+10 materials instead']],
        build:[['Cheap Markets','markets cost 1 gold less'],['Market Row','a hex\'s 2nd and 3rd market cost 1 gold less again'],['New Nest','a free nesting ground: your next barracks costs nothing']],
        fortify:[['Castle Hatch','captured castles get 1 Pachycephalosaurus'],['Castle Brood','3 instead'],['Castle Guard','2 Pachycephalosaurus and 1 Megaraptor instead']]},
};
const CARD_ART=""" + json.dumps(art) + r""";   // Ethan's OpenArt head shots (2026-11-11): Stampede Pachycephalosaurus, Pack Call Parasaurolophus, Siege of Teeth T-rex, The Hunt Triceratops, Nesting Season Alamosaurus
const ARMOR_COST=40, ARMOR_DMG=2, ARMOR_HP=1.1;
const dUp=(pid,cid,a)=>!!(cid&&isDino(pid)&&DCARD[cid]&&DCARD[cid][a]);
// the level of a Dinosaur card's action while it's being played (0 when it isn't that card and action; a Fortify's picks play basic)
const dk=(pid,cid,a)=>(S&&S.play&&S.current===pid&&isDino(pid)&&S.play.card===cid&&cardAction()===a&&(a==='fortify'||!fxOn()))?lvlOf(pid,cid,S.play.step):0;""")
rep("const effLvl=(pid,l)=>(hasNamed(pid)&&l===1)?0:(l||0);",
    "const effLvl=(pid,l)=>isDino(pid)?0:(hasNamed(pid)&&l===1)?0:(l||0);   // the Dinosaurs' cards use their own upgrades (DCARD), not the usual effects")
rep("const dinoOn=(pid,l)=>isDino(pid)&&(l||0)>=1;","const dinoOn=(pid,l)=>false;   // the old Dinosaur abilities (Herd, Migrate, Nesting, Populate, Abundance, Rainy Season) are retired")
rep("const hasNesting=pid=>isDino(pid)&&facOf(pid)","const hasNesting=pid=>false&&facOf(pid)")
rep("const upNext=(a,pid,l)=>hasNamed(pid)&&l===0?namedUp(pid)[a].next:UPGRADES[a].next[l];",
    "const upNext=(a,pid,l,cid)=>dUp(pid,cid,a)?`${DCARD[cid][a][l][0]}: ${DCARD[cid][a][l][1]}`:hasNamed(pid)&&l===0?namedUp(pid)[a].next:UPGRADES[a].next[l];")
rep("const upNow=(a,pid,l)=>!hasNamed(pid)?",
    "const upNow=(a,pid,l,cid)=>dUp(pid,cid,a)?DCARD[cid][a].slice(0,l).map(x=>x[0]).join(', '):!hasNamed(pid)?")
rep("const curLvl=()=>S&&S.play?effLvl(S.current,rawLvl()):0;",
    "const curLvl=()=>S&&S.play?(isDino(S.current)?(dk(S.current,'siege','move')>=1?1:0):effLvl(S.current,rawLvl())):0;   // Dinosaurs: Siege of Teeth's Climb plays as a mountain-climbing Move")
rep("function actionDesc(a,pid,lvl){\n  if(isMyth(pid)&&a!=='fortify') return mythActionDesc(a,pid);",
    "function actionDesc(a,pid,lvl,cid){\n  if(isMyth(pid)&&a!=='fortify') return mythActionDesc(a,pid);\n  if(isDino(pid)){ const base=actionDescBase(a,pid,0); return dUp(pid,cid,a)&&lvl?`${base}. ${DCARD[cid][a].slice(0,lvl).map(x=>`${x[0]}: ${x[1]}`).join('. ')}`:base; }")
rep("""  addLog(`${p.name} upgrade ${c.name}: ${ACTIONS[a].icon} ${actName(a,p.faction)} is now level ${u[slot]} (${upNow(a,pid,u[slot])}).`,pid);""",
    """  addLog(`${p.name} upgrade ${c.name}: ${ACTIONS[a].icon} ${actName(a,p.faction)} is now level ${u[slot]} (${upNow(a,pid,u[slot],cid)}).`,pid);""")
rep("""${hasNamed(0)&&l===1?`: ${namedUp(0)[a].name}`:''}`); }""","""${dUp(0,cid,a)?`: ${DCARD[cid][a][l-1][0]}`:hasNamed(0)&&l===1?`: ${namedUp(0)[a].name}`:''}`); }""")
rep("""${l?lvPips(l)+`<span class="ut">${upNow(a,0,l)}</span>`:''}</span>`;}).join('')}</span></span></button>`;""",
    """${l?lvPips(l)+`<span class="ut">${upNow(a,0,l,cid)}</span>`:''}</span>`;}).join('')}</span></span>${CARD_ART[cid]&&isDino(0)?`<img class="cart" src="${CARD_ART[cid]}" alt="">`:''}</button>`;""")
rep("""    const desc=(step==null||i===step)?`<small>${actionDesc(a,pid,l)}</small>`:'';
    const up=l?`<span class="upl">${lvPips(l)}${upNow(a,pid,l)}</span>`:'';""",
    """    const desc=(step==null||i===step)?`<small>${actionDesc(a,pid,l,cid)}</small>`:'';
    const up=l?`<span class="upl">${lvPips(l)}${upNow(a,pid,l,cid)}</span>`:'';""")
rep("""    <div class="bc-head"><span class="bc-name">${c.name}</span><span class="bc-tag">${opts.tag||''}</span></div>""",
    """    <div class="bc-head">${CARD_ART[cid]&&isDino(pid)?`<img class="bc-art" src="${CARD_ART[cid]}" alt="">`:''}<span class="bc-name">${c.name}</span><span class="bc-tag">${opts.tag||''}</span></div>""")
rep("""<small>${max?'Fully upgraded':`Level ${l+1}: ${upNext(a,0,l)}`}</small>""","""<small>${max?'Fully upgraded':`Level ${l+1}: ${upNext(a,0,l,cid)}`}</small>""")
# How to play: the Dinosaurs list their cards' upgrades
rep("""      <ul class="uplist">${['harvest','recruit','build','move','fortify','advance'].map(a=>""",
    """      <ul class="uplist">${isDino(0)?facOf(0).cards.map(c=>`<li><b>${c.name}</b>: ${c.actions.map(a=>`${ACTIONS[a].icon} ${actName(a,'dinos')} ${DCARD[c.id][a].map((x,i)=>`<span class="lvn">${i+1}</span>${x[0]}: ${x[1]}.`).join(' ')}`).join(' ')}</li>`).join(''):['harvest','recruit','build','move','fortify','advance'].map(a=>""")
rep("""${(['harvest','recruit','build','move','fortify','advance'].map(a=>`<li>${ACTIONS[a].icon} <b>${actName(a,S.players[0].faction)}</b>: ${UPGRADES[a].next.map((x,i)=>`<span class="lvn">${i+1}</span>${upNext(a,0,i)}.`).join(' ')}</li>`).join(''))}""","",0)
# the faction screen
rep("""    ${nu?`<p>The first upgrade of each action on a card is a ${f.name} ability:""",
    """    ${fid==='dinos'?`<p>Every Dinosaur card has its own upgrades for each of its actions:</p><ul>${f.cards.map(c=>`<li><b>${c.name}</b>: ${c.actions.map(a=>`${ACTIONS[a].icon} ${DCARD[c.id][a].map(x=>x[0]).join(', ')}`).join(' · ')}</li>`).join('')}</ul>`:nu?`<p>The first upgrade of each action on a card is a ${f.name} ability:""")
rep(""".gcard .ut{color:var(--gold);""",""".gcard .cart{flex:none;align-self:center;height:min(5.2em,90%);width:auto;max-width:28%;object-fit:contain;margin:0 .45em 0 .1em;filter:drop-shadow(0 .12em 0 rgba(0,0,0,.45))}
.bc-art{height:2.4em;width:auto;align-self:center;filter:drop-shadow(0 .1em 0 rgba(0,0,0,.45))}
.gcard .ut{color:var(--gold);""")

# ================= Harvest =================
rep("""    const rain=dinoOn(pid,raw), g=harvestGold(pid,lvl,rain)+ind+fert; p.gold+=g;""",
    """    const rain=dinoOn(pid,raw), dh=isDino(pid)?dinoHarvest(pid):{g:0,m:0,why:[]}, g=harvestGold(pid,lvl,rain)+ind+fert+dh.g; p.gold+=g; if(dh.m) p.mat=matOf(pid)+dh.m;
    if(isDino(pid)&&(dh.g||dh.m)){ addLog(`${p.name} harvest ${g} gold${dh.m?` and ${matTxt(dh.m)}`:''} (${dh.why.join(', ')}).`,pid);
      return `<span class="px px-harvest" aria-hidden="true"></span> Harvest: +${g} gold${dh.m?`, +${matTxt(dh.m)}`:''} (${dh.why.join(', ')})`; }""")
rep("""// A Fortify starts with its faction ability: the Mammals' Mating, the Robots' Update or the Dinosaurs' Herd.""",
r"""// a Dinosaur Harvest's card upgrades: extra gold and materials (Ethan, 2026-11-11)
function dinoHarvest(pid){
  const own=S.tiles.filter(t=>t.owner===pid), mk=own.reduce((n,t)=>n+(t.market|0),0), cs=own.filter(t=>t.castle).length,
    nests=own.reduce((n,t)=>n+(t.barracks|0),0), hexes=incomeOf(pid).tiles, P=c=>dk(pid,c,'harvest');
  let g=0, m=0; const why=[];
  const pk=P('pack'), hu=P('hunt'), si=P('siege'), ne=P('nest');
  if(pk>=1){ g+=mk; why.push(`Trade Calls +${mk}`); }
  if(pk>=2){ g+=5*cs; why.push(`Castle Tolls +${5*cs}`); }
  if(pk>=3){ const x=2*Math.floor(unitTotal(pid)/5); g+=x; why.push(`Big Herd +${x}`); }
  if(hu>=1){ const x=hexes-Math.floor(hexes*.5); g+=x; why.push(`Hunting Grounds +${x}`); }
  if(hu>=2){ g+=2*nests; why.push(`Nest Feast +${2*nests}`); }
  if(hu>=3){ g+=5*cs; why.push(`Castle Feast +${5*cs}`); }
  if(si>=1){ const x=Math.floor(own.length/(si>=2?2:3)); m+=x; why.push(`${si>=2?'Big Quarry':'Quarry'} +${matTxt(x)}`); }
  if(si>=3){ m+=cs; why.push(`Castle Stores +${matTxt(cs)}`); }
  if(ne>=1){ const x=ne>=3?10:ne>=2?5:3; m+=x; why.push(`${ne>=3?'Great Store':ne>=2?'Stockpile':'Gathering'} +${matTxt(x)}`); }
  return {g,m,why};
}
// A Dinosaur action's card upgrades that happen when it starts (Build, Recruit). Returns notes for the card column.
function dinoActionStart(pid){
  if(!isDino(pid)||!S.play) return [];
  const a=cardAction(), p=S.players[pid], out=[], ic=`<span class="px px-${a}" aria-hidden="true"></span>`;
  if(a==='build'){
    if(dk(pid,'stamp','build')>=2){ p.mat=matOf(pid)+2; out.push(`${ic} Supplies: +2 materials`); }
    if(dk(pid,'nest','build')>=3){ p.fnest=(p.fnest|0)+1; out.push(`${ic} New Nest: your next barracks is free`); }
    if(dk(pid,'stamp','build')>=1) out.push(`${ic} Free Market: your first market in this action costs nothing`);
  }
  if(a==='recruit'){
    const home=S.tiles[S.homes[pid]];
    if(dk(pid,'hunt','recruit')>=2){ let n=0; S.tiles.forEach(t=>{ if(t.owner===pid&&t.castle){ addUnits(t,'galli',2,true); n+=2; } }); if(n){ out.push(`${ic} Castle Herds: +${n} Pachycephalosaurus at your castles`); addLog(`${p.name} get ${n} free Pachycephalosaurus at their castles.`,pid); } }
    if(dk(pid,'pack','recruit')>=3&&home.owner===pid){ addUnits(home,'mega',2,true); out.push(`${ic} Castle Raptors: +2 Megaraptors at your home castle`); addLog(`${p.name} get 2 free Megaraptors at their home castle.`,pid); }
    const pk=dk(pid,'pack','recruit');
    if(pk>=1){ const got={galli:3}; if(pk>=2) got.mega=1;
      const nests=S.tiles.filter(t=>t.owner===pid&&t.barracks);
      if(!nests.length){ if(home.owner===pid){ addArmy(home,got,true); out.push(`${ic} Calling: no nesting ground yet, so the free units wait at your home castle`); } }
      else if(p.ai||nests.length===1){ const dE=bfs(foeTiles(pid)), t=nests.slice().sort((x,y)=>fin(dE[x.id])-fin(dE[y.id]))[0]; addArmy(t,got,true); out.push(`${ic} Calling: ${armyList(got)} at a nesting ground`); }
      else { S.play.dpick=got; out.push(`${ic} Calling: tap one of your nesting grounds for ${armyList(got)}`); }
      addLog(`${p.name} call ${pk>=2?'3 Pachycephalosaurus and a Megaraptor':'3 Pachycephalosaurus'} to a nesting ground.`,pid);
    }
  }
  return out;
}
// the free units from Calling go to the nesting ground the player taps
function placeDpick(i){ const t=S.tiles[i]; if(!S.play||!S.play.dpick||t.owner!==0||!t.barracks) return; addArmy(t,S.play.dpick,true); S.play.dpick=null; ui.sel=i; render(); }
// a free building: Free Market (the first market of a Stampede Build) and New Nest (the next barracks)
function dinoCost(pid,k,c,t){
  const st=dk(pid,'stamp','build'), ne=dk(pid,'nest','build'), p=S.players[pid];
  if(k==='market'){ if(st>=1&&!S.play.freeMk) return 0; if(ne>=1) c-=1; if(ne>=2&&t&&(t.market|0)>=1) c-=1; return Math.max(0,c); }
  if(k==='barracks'&&(p.fnest|0)>0) return 0;
  if(st>=3&&inMat(k)) return Math.min(c,1);
  return c;
}
function dinoBuilt(pid,k,price){ if(!isDino(pid)||price>0||!S.play) return; const p=S.players[pid];
  if(k==='market'&&dk(pid,'stamp','build')>=1&&!S.play.freeMk) S.play.freeMk=1; else if(k==='barracks'&&(p.fnest|0)>0) p.fnest--; }
const bkUpCost=(pid,lv)=>BARRACKS_UP[lv]-(dk(pid,'hunt','advance')>=1?1:0);   // Quick Nests
const guardCost=pid=>GUARD_COST-(dk(pid,'hunt','advance')>=2?3:0);           // Cheap Guards
const armorOn=pid=>!!(pid>=0&&S.players[pid]&&S.players[pid].armor);
function doArmor(pid){ const p=S.players[pid], h=S.tiles[S.homes[pid]];
  if(!isDino(pid)||p.armor||h.owner!==pid||dk(pid,'hunt','advance')<3||p.gold<ARMOR_COST) return false;
  p.gold-=ARMOR_COST; p.armor=true; addLog(`${p.name} forge Armor: all their units get +${ARMOR_DMG} damage and +10% health.`,pid); return true; }
// A Fortify starts with its faction ability: the Mammals' Mating, the Robots' Update or the Dinosaurs' Herd.""")

# ================= Fortify =================
rep("""  if(dinoOn(pid,raw)){ p.herd=true;""","""  if(isDino(pid)&&S.play) out.push(...dinoFortify(pid,raw));
  if(dinoOn(pid,raw)){ p.herd=true;""")
rep("""// A Fortify starts with its faction ability: the Mammals' Mating, the Robots' Update or the Dinosaurs' Herd.""",
r"""// a Dinosaur Fortify's card upgrades (Ethan, 2026-11-11)
function dinoFortify(pid,raw){
  const cid=S.play.card, p=S.players[pid], out=[], own=S.tiles.filter(t=>t.owner===pid), nests=own.filter(t=>t.barracks);
  if(cid==='stamp'){
    if(raw>=1&&nests.length){ nests.forEach(t=>addUnits(t,'galli',t.barracks|0,true)); out.push(`Hatchlings: +1 Pachycephalosaurus at each nesting ground`); }
    if(raw>=2&&nests.length){ nests.forEach(t=>addUnits(t,'mega',t.barracks|0,true)); out.push(`Raptor Brood: +1 Megaraptor at each nesting ground`); }
    if(raw>=3){ p.fnest=(p.fnest|0)+1; out.push(`New Nest: your next barracks is free`); }
    if(raw>=1) addLog(`${p.name} hatch new dinosaurs at their nesting grounds.`,pid);
  }
  if(cid==='siege'){
    if(raw>=1){ const best=own.filter(t=>t.market).sort((x,y)=>y.market-x.market)[0]; if(best){ const g=2*best.market; p.gold+=g; out.push(`Market Day: +${g} gold`); addLog(`${p.name} hold a market day: +${g} gold.`,pid); } }
    const free=raw>=3?2:raw>=2?1:0;
    if(free){ const dE=bfs(foeTiles(pid)); let n=0;
      for(let k=0;k<free;k++){ const t=nests.filter(x=>guardsAt(x)<GUARD_MAX*x.barracks).sort((x,y)=>fin(dE[x.id])-fin(dE[y.id]))[0]; if(!t) break; addUnits(t,'alamo',1,false); n++; }
      if(n){ out.push(`Guardian: +${n} free Alamosaurus guard${n>1?'s':''}`); addLog(`${p.name} get ${n} free Alamosaurus guard${n>1?'s':''}.`,pid); } }
  }
  if(cid==='nest'&&raw>=1){
    const got=raw>=3?{galli:2,mega:1}:{galli:raw>=2?3:1}, cs=own.filter(t=>t.castle&&t.id!==S.homes[pid]);
    cs.forEach(t=>addArmy(t,got,true));
    out.push(cs.length?`${raw>=3?'Castle Guard':raw>=2?'Castle Brood':'Castle Hatch'}: ${armyList(got)} at each captured castle`:'Castle Hatch: no captured castles yet');
    if(cs.length) addLog(`${p.name} send new dinosaurs to their ${cs.length} captured castle${cs.length>1?'s':''}.`,pid);
  }
  return out;
}
// Pack Call's Fortify: one long regroup move, Move as a pick, and the Rally
function dinoFxSetup(pid){ const f=S.play.fx, l=dk(pid,'pack','fortify'); if(!f) return; f.far=l>=1?1:0; f.mv=l>=2; f.rally=l>=3?1:0; }
// A Fortify starts with its faction ability: the Mammals' Mating, the Robots' Update or the Dinosaurs' Herd.""")
rep("""    S.play.fx={ph:'regroup',n:fxPicksAt(S.current,effLvl(S.current,raw)),done:[],cur:null};
  }""","""    S.play.fx={ph:'regroup',n:fxPicksAt(S.current,effLvl(S.current,raw)),done:[],cur:null}; dinoFxSetup(S.current);
  }
  ui.notes.push(...dinoActionStart(S.current));""")
rep("""  S.play.fx={ph:'regroup',n,done:[],cur:null}; S.play.moves=0;""","""  S.play.fx={ph:'regroup',n,done:[],cur:null}; S.play.moves=0; dinoFxSetup(pid);""")
# the regroup goes 2 hexes (Ethan, 2026-11-11); Join Up lets one move go any distance
rep("""function regroupTargets(from){ const pid=S.tiles[from].owner, seen=new Set([from]); let fr=[from];
  while(fr.length){""","""function regroupTargets(from,maxD){ const pid=S.tiles[from].owner, seen=new Set([from]); let fr=[from], d=0; maxD=maxD||REGROUP_REACH;
  while(fr.length&&d++<maxD){""")
rep("""const FX_PICKS=['build','advance','recruit'], REGROUP_MOVES=99;""","""const FX_PICKS=['build','advance','recruit'], REGROUP_MOVES=99, REGROUP_REACH=2;   // a regroup move goes up to 2 hexes (Ethan, 2026-11-11)
const fxReach=()=>S.play&&S.play.fx&&S.play.fx.far>0?99:REGROUP_REACH;
const fxPickList=()=>FX_PICKS.concat(S.play&&S.play.fx&&S.play.fx.mv?['move']:[]);""")
rep("""  if(regrouping()&&pid===S.current) return regroupTargets(from);""","""  if(regrouping()&&pid===S.current) return regroupTargets(from,fxReach());""")
rep("""  if(B.owner===A.owner){ addArmy(B,sel,regrouping()&&A.owner===S.current); return res; }""",
    """  if(B.owner===A.owner){ if(regrouping()&&A.owner===S.current&&S.play.fx.far>0&&!regroupTargets(from,REGROUP_REACH).includes(to)) S.play.fx.far--;   // Join Up used
    addArmy(B,sel,regrouping()&&A.owner===S.current); return res; }""")
rep("""      regroupTargets(s.id).forEach(i=>{""","""      regroupTargets(s.id,fxReach()).forEach(i=>{""")
rep("""  if(!isHumanTurn()||!fxOn()||S.play.fx.ph!=='pick'||!FX_PICKS.includes(k)||S.play.fx.done.includes(k)) return;
  const f=S.play.fx; f.ph='act'; f.cur=k; S.play.freeWalls=0;""","""  if(!isHumanTurn()||!fxOn()||S.play.fx.ph!=='pick'||!fxPickList().includes(k)||S.play.fx.done.includes(k)) return;
  const f=S.play.fx; f.ph='act'; f.cur=k; S.play.freeWalls=0; if(k==='move') S.play.moves=0;""")
rep("""  if(f.ph==='act'){ f.done.push(f.cur); f.cur=null; if(f.done.length<f.n&&FX_PICKS.some(k=>!f.done.includes(k))){""",
    """  if(f.ph==='act'){ f.done.push(f.cur); f.cur=null; if(f.done.length<f.n&&fxPickList().some(k=>!f.done.includes(k))){""")
rep("""    <div class="fxpicks">${FX_PICKS.map(btn).join('')}</div>""","""    <div class="fxpicks"${fxPickList().length>3?' style="grid-template-columns:repeat(4,minmax(0,1fr))"':''}>${fxPickList().map(btn).join('')}</div>""")
rep("""const fxPickNote=k=>isMyth(0)?""","""const fxPickNote=k=>k==='move'?'Claim and attack':isMyth(0)?""")
# the Rally (Pack Call level 3)
rep("""    h+=`<p class="hint" style="margin-top:.4em">Then tap <b>Done regrouping</b>""",
    """    if(S.play.fx.rally>0&&sel&&sel.owner===0) h+=`<div class="btns" style="margin:.3em 0"><button data-act="rally">Rally: bring every unit you have here</button></div>`;
    if(S.play.fx.far>0) h+=`<p class="hint">Join Up: one regroup move can go any distance through your land.</p>`;
    h+=`<p class="hint" style="margin-top:.4em">Then tap <b>Done regrouping</b>""")
rep("""any distance through your own land (not mountains), but no attacks or claiming. Units that regroup""","""up to 2 hexes through your own land (not mountains), but no attacks or claiming. Units that regroup""")
rep("""  else if(a==='fxpick') fxChoose(b.dataset.k);""","""  else if(a==='fxpick') fxChoose(b.dataset.k);
  else if(a==='rally'&&ui.sel!=null) rallyTo(ui.sel);""")
rep("""function fxChoose(k){""","""// Rally (Pack Call): every ready unit you have, from anywhere in your land, comes to one hex
function rallyTo(i){
  if(!isHumanTurn()||!regrouping()||!(S.play.fx.rally>0)||S.tiles[i].owner!==0) return;
  const to=S.tiles[i]; let n=0;
  S.tiles.forEach(t=>{ if(t.owner!==0||t.id===i||!t.fresh) return; const sel={...t.ready}; delete sel.alamo; const m=cnt(sel); if(!m) return; takeUnits(t,sel); addArmy(to,sel,true); n+=m; });
  S.play.fx.rally=0; addLog(`You rally ${n} unit${n===1?'':'s'} to one hex.`,0); render();
}
function fxChoose(k){""")
rep("""mythAct=undoable(mythAct); fxChoose=undoable(fxChoose);""","""mythAct=undoable(mythAct); rallyTo=undoable(rallyTo); fxChoose=undoable(fxChoose);""")
rep("""  if(a==='fortify'){ const n=fxPicksAt(pid,lvl);
    return `A wild card. First regroup: move your units any distance between your own hexes, as often as you like (no attacks or claiming).""",
    """  if(a==='fortify'){ const n=fxPicksAt(pid,lvl);
    return `A wild card. First regroup: move your units up to 2 hexes between your own hexes, as often as you like (no attacks or claiming).""")

# ================= Recruit =================
rep("""const unitCostAt=(t,pid,k)=>Math.max(1,UNIT_STATS[k].cost-((t&&t.barracks&&(t.bk||0)>=3)?1:0)""",
    """const unitCostAt=(t,pid,k)=>Math.max(1,UNIT_STATS[k].cost-((t&&t.barracks&&(t.bk||0)>=3)?1:0)
  -(t&&dk(pid,'hunt','recruit')>=1?((isHomeCastle(t)&&t.owner===pid?1:0)+(dk(pid,'hunt','recruit')>=3&&t.barracks?1:0)):0)   // Home Hunters, Nest Hunters (The Hunt)""")
rep("""function onCell(i){
  if(!isHumanTurn()) return;""","""function onCell(i){
  if(!isHumanTurn()) return;
  if(S.play&&S.play.dpick&&curAction()==='recruit'&&S.tiles[i].owner===0&&S.tiles[i].barracks){ placeDpick(i); return; }   // Calling (Pack Call)""")
rep("""  if(a==='fortify'&&!S.play.fx) S.play.fx={ph:'pick',n:1,done:[],cur:null};""","""  if(a==='fortify'&&!S.play.fx) S.play.fx={ph:'pick',n:1,done:[],cur:null};
  if(S.play.dpick&&a==='recruit') h+=`<div class="note">Calling: tap one of your nesting grounds <span class="px px-barracks" aria-hidden="true"></span> for ${armyList(S.play.dpick)}</div>`;""")
rep("""  if(isMyth(0)&&a!=='move') return null;
  if(a==='move'){""","""  if(isMyth(0)&&a!=='move') return null;
  if(a==='recruit'&&S.play.dpick) return `You haven't placed your free units from <b>Calling</b> yet: tap one of your nesting grounds.`;
  if(a==='move'){""")
rep("""      const fr=freeTroops(pid,lvl), bi=card.actions.indexOf('build');""","""      dinoActionStart(pid); const fr=freeTroops(pid,lvl), bi=card.actions.indexOf('build');""")
rep("""    else if(a==='build') yield {kind:'flash',ids:aiBuild(pid,lvl,card.actions.slice(s+1))};""",
    """    else if(a==='build'){ dinoActionStart(pid); yield {kind:'flash',ids:aiBuild(pid,lvl,card.actions.slice(s+1))}; }""")

# ================= Build =================
rep("""const costOf=(k,lvl)=>COSTS[k][lvl||0];""","""const costOf=(k,lvl,t)=>{ const c=COSTS[k][lvl||0], pid=S&&S.play?S.current:-1;   // a Dinosaur Build's card upgrades change the price
  return pid>=0&&isDino(pid)&&curAction()==='build'?dinoCost(pid,k,c,t):c; };""")
rep("""  const price=costOf(k,curLvl());
  if(curAction()!=='build'||bCount(t)>=bMax()||!canPayB(0,k,price)""","""  const price=costOf(k,curLvl(),t);
  if(curAction()!=='build'||bCount(t)>=bMax()||!canPayB(0,k,price)""")
rep("""  payB(0,k,price); t[k]=(t[k]|0)+1; noteUnlock(0,k,t);""","""  payB(0,k,price); dinoBuilt(0,k,price); t[k]=(t[k]|0)+1; noteUnlock(0,k,t);""")
rep("""    const price=costOf(kind,lvl), castleNo=""","""    const price=costOf(kind,lvl,t), castleNo=""")
rep("""    const nt=has?'Has one':full?'Full':castleNo?'Not here':priceTxt(kind,price), note=has||full||castleNo?nt:priceIc(kind,price);""",
    """    const nt=has?'Has one':full?'Full':castleNo?'Not here':price===0?'Free':priceTxt(kind,price), note=has||full||castleNo||price===0?nt:priceIc(kind,price);""")
rep("""    if(inMat(plan.k)){ if(!aiMat(pid,c+keep,keepR)) break; spendMat(pid,c); }
    else { if(p.gold-c<goldFor(pid,keep)) break; p.gold-=c; }""","""    if(inMat(plan.k)){ if(!aiMat(pid,c+keep,keepR)) break; spendMat(pid,c); }
    else { if(p.gold-c<goldFor(pid,keep)) break; p.gold-=c; }
    dinoBuilt(pid,plan.k,c);""")

# ================= Advancements =================
rep("""  const free=lvl>=1&&!S.play.freeBk&&lv===0, price=free?0:BARRACKS_UP[lv];""","""  const free=lvl>=1&&!S.play.freeBk&&lv===0, price=free?0:bkUpCost(pid,lv);""")
rep("""bp=free?0:BARRACKS_UP[lv];""","""bp=free?0:bkUpCost(0,lv);""")
rep("""  if(t.owner!==pid||!isDino(pid)||!t.barracks||guardsAt(t)>=GUARD_MAX*t.barracks||p.gold<GUARD_COST) return false;
  p.gold-=GUARD_COST;""","""  const gc=guardCost(pid);
  if(t.owner!==pid||!isDino(pid)||!t.barracks||guardsAt(t)>=GUARD_MAX*t.barracks||p.gold<gc) return false;
  p.gold-=gc;""")
rep("""          can:!!t.barracks&&g<gm&&me.gold>=GUARD_COST, note:!t.barracks?'Needs barracks':g>=gm?`${g} guarding`:`${GUARD_COST} gold`,""",
    """          can:!!t.barracks&&g<gm&&me.gold>=guardCost(0), note:!t.barracks?'Needs barracks':g>=gm?`${g} guarding`:`${guardCost(0)} gold`,""")
rep("""`Station an Alamosaurus to guard this barracks for ${GUARD_COST} gold""","""`Station an Alamosaurus to guard this barracks for ${guardCost(0)} gold""")
rep("""    [[150,1],[90,0],[30,5]].forEach(([deg,vi],i)=>{ const o=opts[i];""","""    if(isDino(0)&&isHomeCastle(t)&&t.owner===0&&dk(0,'hunt','advance')>=3) opts.push({k:'armor', img:UNIT_ART.trike||UNIT_ART.bow, sm:true, name:'Armor',
      can:!me.armor&&me.gold>=ARMOR_COST, note:me.armor?'Forged':`${ARMOR_COST} gold`, label:me.armor?'Armor: already forged':`Forge Armor for ${ARMOR_COST} gold: all your units +${ARMOR_DMG} damage and +10% health`});
    [[150,1],[90,0],[30,5],[210,2]].slice(0,opts.length).forEach(([deg,vi],i)=>{ const o=opts[i];""")
rep("""  else if(kind==='volc') doVolcano(0);""","""  else if(kind==='volc') doVolcano(0);
  else if(kind==='armor') doArmor(0);""")
rep("""      if(t.barracks&&(t.bk||0)<3){ const lv=t.bk||0, free=lvl>=1&&!S.play.freeBk&&lv===0; if(free||matOf(0)>=BARRACKS_UP[lv]) return true; }""",
    """      if(t.barracks&&(t.bk||0)<3){ const lv=t.bk||0, free=lvl>=1&&!S.play.freeBk&&lv===0; if(free||matOf(0)>=bkUpCost(0,lv)) return true; }""")
rep("""    for(const {t} of bks) while(guardsAt(t)<GUARD_MAX*t.barracks&&p.gold>=GUARD_COST+sp&&doBuyGuard(pid,t.id)) ids.push(t.id);
  }""","""    for(const {t} of bks) while(guardsAt(t)<GUARD_MAX*t.barracks&&p.gold>=guardCost(pid)+sp&&doBuyGuard(pid,t.id)) ids.push(t.id);
    if(!p.armor&&p.gold>=ARMOR_COST+sp&&doArmor(pid)) ids.push(S.homes[pid]);   // Armor (The Hunt)
  }""")
rep("""  for(const t of bks) while((t.bk||0)<3&&aiMat(pid,BARRACKS_UP[t.bk||0],spare[t.bk||0])&&doUpgradeBarracks(pid,t.id,lvl)) ids.push(t.id);""",
    """  for(const t of bks) while((t.bk||0)<3&&aiMat(pid,bkUpCost(pid,t.bk||0),spare[t.bk||0])&&doUpgradeBarracks(pid,t.id,lvl)) ids.push(t.id);""")

# ================= Armor in battles =================
rep("""  return {advA:(lvl||0)>=2, aBonus:up?1:0, aPlus:up?1:0, surprise:off?1:0};""",
    """  const aArm=armorOn(pid), dArm=armorOn(def);   // Armor (The Hunt): +2 damage and +10% health for that side
  return {advA:(lvl||0)>=2, aBonus:up?1:0, aPlus:(up?1:0)+(aArm?ARMOR_DMG:0), dPlus:dArm?ARMOR_DMG:0, aArm, dArm, surprise:off?1:0};""")
rep("""    const hitsOnA=held?{dmg:{},wall:0,any:false,shield:0,stun:{}}:strike(D,A,1,luckMult(rd.v),r,{wall:0,arm:arm[0],""",
    """    if(o.dArm) for(const k in hitsOnD.dmg) hitsOnD.dmg[k]/=ARMOR_HP;   // Armor: 10% more health
    const hitsOnA=held?{dmg:{},wall:0,any:false,shield:0,stun:{}}:strike(D,A,1,luckMult(rd.v),r,{wall:0,plus:o.dPlus||0,arm:arm[0],""")
rep("""    if(held){ ev.held=r; if(hitsOnD.any) held=false; }""","""    if(o.aArm) for(const k in hitsOnA.dmg) hitsOnA.dmg[k]/=ARMOR_HP;
    if(held){ ev.held=r; if(hitsOnD.any) held=false; }""")
rep("""  return {sneak:o.surprise?1:0, plus:o.aPlus||0, mult:o.aBonus?UPDATE_MULT:1};""",
    """  return {sneak:o.surprise?1:0, plus:(o.aPlus||0)-(o.aArm?ARMOR_DMG:0), mult:o.aBonus?UPDATE_MULT:1, armA:o.aArm?1:0, armD:o.dArm?1:0};""")
rep("""    const fm=f.mods||{}, mods={sneak:fm.sneak?tA:null, plus:[0,0], mult:[1,1]}; mods.plus[tA]=fm.plus||0; mods.mult[tA]=fm.mult||1;""",
    """    const fm=f.mods||{}, mods={sneak:fm.sneak?tA:null, plus:[0,0], mult:[1,1], hp:[1,1]}; mods.plus[tA]=fm.plus||0; mods.mult[tA]=fm.mult||1;
    if(fm.armA){ mods.plus[tA]+=ARMOR_DMG; mods.hp[tA]=ARMOR_HP; } if(fm.armD){ mods.plus[1-tA]+=ARMOR_DMG; mods.hp[1-tA]=ARMOR_HP; }   // Armor (The Hunt)""")
rep("""m.plus?`${a} units are Updated: +1 damage on every hit and ${Math.round((m.mult-1)*100)}% more damage`:''].filter(Boolean); };""",
    """m.plus?`${a} units are Updated: +1 damage on every hit and ${Math.round((m.mult-1)*100)}% more damage`:'', m.armA?`${a} units wear Armor: +${ARMOR_DMG} damage, +10% health`:'', m.armD?`${f.att===0?'Their':'Your'} units wear Armor: +${ARMOR_DMG} damage, +10% health`:''].filter(Boolean); };""")
# the arena: a health multiplier per team (embedded copy; arena.html gets the same edits)
for old,new in [("MOD_PLUS=[0,0], MOD_MULT=[1,1];","MOD_PLUS=[0,0], MOD_MULT=[1,1], MOD_HP=[1,1];"),
                ("MOD_MULT=[0,1].map(t=>+((md.mult||[])[t])||1); }","MOD_MULT=[0,1].map(t=>+((md.mult||[])[t])||1); MOD_HP=[0,1].map(t=>+((md.hp||[])[t])||1); }"),
                ("TYPES[k].hp*(fortBuff(team)?FORT_HP:1)*100","TYPES[k].hp*(fortBuff(team)?FORT_HP:1)*(MOD_HP[team]||1)*100")]:
    rep(old,new)

# ================= Move =================
rep("""const movesLimit=pid=>(regrouping()&&S.current===pid)?REGROUP_MOVES:modsOf(pid).movesPerAction+""",
    """const movesLimit=pid=>(regrouping()&&S.current===pid)?REGROUP_MOVES:(dk(pid,'stamp','move')>=1?1:0)+modsOf(pid).movesPerAction+""")
rep("""function moveTargets(from,lvl){
  lvl=lvl||0; const t=S.tiles[from], pid=t.owner, far=isMyth(pid)&&Object.keys(t.ready||{}).some(k=>t.ready[k]>0&&fastUnit(k));
  return moveTargetsCore(from,lvl,far).filter(i=>{""","""// Charge (Stampede): the extra move must be an attack
const chargeOnly=pid=>dk(pid,'stamp','move')>=1&&S.play&&(S.play.moves||0)>=movesLimit(pid)-1;
function moveTargets(from,lvl){
  lvl=lvl||0; const t=S.tiles[from], pid=t.owner, far=isMyth(pid)&&Object.keys(t.ready||{}).some(k=>t.ready[k]>0&&fastUnit(k)), co=chargeOnly(pid);
  return moveTargetsCore(from,lvl,far).filter(i=>!co||(S.tiles[i].owner>=0&&S.tiles[i].owner!==pid)).filter(i=>{""")
rep("""  out.delete(from);
  return [...out];
}""","""  if(isDino(pid)&&S.play&&S.current===pid){
    if(dk(pid,'stamp','move')>=2&&from===S.homes[pid]) regroupTargets(from,99).forEach(i=>out.add(i));   // Home Run
    const sg=dk(pid,'siege','move');
    if(sg>=2) for(const a of nbrs(from)){ const A=S.tiles[a]; if(!canEnter(a,lvl)||A.troops>0||!passThrough(from,a,lvl,pid)) continue;   // Dash: 2 hexes, both empty
      for(const b of nbrs(a)){ const B=S.tiles[b]; if(b!==from&&canEnter(b,lvl)&&B.troops===0&&!homeGuards(B)) out.add(b); } }
    if(sg>=3) for(const a of nbrs(from)) if(S.tiles[a].terrain==='mountain'&&passThrough(from,a,Math.max(lvl,1),pid))   // Over the Top: across a mountain, attacking on the far side
      for(const b of nbrs(a)) if(b!==from&&canEnter(b,lvl)) out.add(b);
  }
  out.delete(from);
  return [...out];
}""")
# Two Herds (Stampede level 3): a second hex next to the target joins the attack
rep("""  const mf=moveFilter(from,to,lvl), ks=byStrength(s.ready||{}).filter(k=>!mf||mf(k)), pick={}; ks.forEach(k=>pick[k]=0);""",
    """  const jh=fight&&dk(0,'stamp','move')>=3?nbrs(to).map(j=>S.tiles[j]).filter(x=>x.owner===0&&x.id!==from&&x.fresh>0).sort((x,y)=>armyGold(y.ready)-armyGold(x.ready))[0]:null;
  if(jh) text+=`<br><label style="display:flex;gap:.4em;align-items:center;margin-top:.4em"><input type="checkbox" id="mvjoin" checked> Two Herds: the ${jh.fresh} ready unit${jh.fresh>1?'s':''} next door join in: <span class="mvfoe">${armyList(jh.ready)}</span></label>`;
  const mf=moveFilter(from,to,lvl), ks=byStrength(s.ready||{}).filter(k=>!mf||mf(k)), pick={}; ks.forEach(k=>pick[k]=0);""")
rep("""    const snap=JSON.stringify(S);
    S.play.moves=(S.play.moves||0)+1;
    if(isFight(from,to)){""","""    const snap=JSON.stringify(S);
    S.play.moves=(S.play.moves||0)+1;
    if(jh&&joinOn){ const add={...jh.ready}; delete add.alamo; takeUnits(jh,add); addArmy(s,add,true); sel={...sel}; for(const k in add) sel[k]=(sel[k]||0)+add[k]; addLog(`Two Herds: ${cnt(add)} more units join the attack.`,0); }
    if(isFight(from,to)){""")
rep("""  const go=sel=>{ closeModal();""","""  let joinOn=!!jh;
  const go=sel=>{ joinOn=!!(jh&&$('#mvjoin')&&$('#mvjoin').checked); closeModal();""")

# ================= turn start =================
rep("""p.herd=false; p.tr=0;""","""p.herd=false; p.tr=0;""")
open(P+'cc.html','w',encoding='utf-8').write(s)
print('ok')

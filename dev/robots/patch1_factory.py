# Robot rewrite, step 1 (Ethan, 2026-11-11): the war-factory home castle, and one Robot building per hex, the Factory.
# It's built as a market. At the home castle (during Build) each factory is upgraded on its own: first a barracks,
# then a fortress. Three looks: market, market + barracks, full fortress. Art: OpenArt, cut out by cut_robots.py.
import sys, base64, re, os
p=sys.argv[1]; s=open(p).read()
D=os.path.dirname(os.path.abspath(__file__))
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:120]); s=s.replace(a,b)
def uri(f): return 'data:image/png;base64,'+base64.b64encode(open(os.path.join(D,f),'rb').read()).decode()

# ---- art: the war-factory castle, and the factory at its three levels in place of the old market, barracks and fort ----
m=re.search(r'"castle_robots": \{"uri": "data:image/png;base64,[A-Za-z0-9+/=]+", "ratio": [0-9.]+\}',s); assert m
s=s[:m.start()]+'"castle_robots": {"uri": "%s", "ratio": 0.9727}'%uri('castle_robots.png')+s[m.end():]
for k,f in [('market_robots','robo1.png'),('barracks_robots','robo2.png'),('fort_robots','robo3.png')]:
    m=re.search(r'"%s": "data:image/png;base64,[A-Za-z0-9+/=]+"'%k,s); assert m
    s=s[:m.start()]+'"%s": "%s"'%(k,uri(f))+s[m.end():]
rep("const SMOOTH_BLD=k=>/_mammals$|^wh$|^tree$|^barracks_dinos$|^market_dinos$/.test(k);",
    "const SMOOTH_BLD=k=>/_mammals$|_robots$|^wh$|^tree$|^barracks_dinos$|^market_dinos$/.test(k);")

# ---- the rules ----
rep("""// the Robots' Efficiency: up to 4 buildings on a hex during that Build
const bMax=()=>(S&&S.play&&curAction()==='build'&&roboOn(S.current,rawLvl()))?4:MAX_BUILDINGS;""",
"""// the Robots' Efficiency: up to 4 buildings on a hex during that Build
const bMax=()=>(S&&S.play&&isRobo(S.current))?1:(S&&S.play&&curAction()==='build'&&roboOn(S.current,rawLvl()))?4:MAX_BUILDINGS;   // Robots: one Factory per hex
// ---- the Robots' Factory (Ethan, 2026-11-11): one building per hex. It's built as a market, and the home castle upgrades
// each one on its own (during Build, paid like a barracks or fort): first a barracks, then a fortress. Castles take a market only. ----
const roboLv=t=>t.market?(t.barracks?(t.fort?3:2):1):0;
const roboNext=t=>(t.market&&!t.castle)?(!t.barracks?'barracks':!t.fort?'fort':null):null;   // what the home castle can add to it next
const ROBO_NAME={barracks:'Barracks',fort:'Fortress'};
const roboUpTargets=(pid,k)=>S.tiles.filter(t=>t.owner===pid&&roboNext(t)===k).map(t=>t.id);
function doRoboUp(pid,i,lvl){
  const t=S.tiles[i], p=S.players[pid], k=roboNext(t);
  if(!isRobo(pid)||t.owner!==pid||!k||!homeMarket(pid)) return false;
  const c=costOf(k,lvl,t); if(!canPayB(pid,k,c)) return false;
  payB(pid,k,c); t[k]=1; noteUnlock(pid,k,t);
  addLog(`${p.name} upgrade a factory with a ${k==='fort'?'fortress':'barracks'}.`,pid);
  return true;
}""")
rep("""  if(k==='fort'&&isDino(0)) return;   // the Dinosaurs build no forts
  payB(0,k,price);""","""  if(k==='fort'&&isDino(0)) return;   // the Dinosaurs build no forts
  if(isRobo(0)&&k!=='market') return;   // Robots: barracks and fortresses are factory upgrades, made at the home castle
  payB(0,k,price);""")
# entering and using the pick mode: Barracks or Fortress at the home castle, then tap the factory to upgrade
rep("""function build(id,k){
  const t=S.tiles[id], me=S.players[0];""","""function build(id,k){
  const t=S.tiles[id], me=S.players[0];
  if(k==='rup_barracks'||k==='rup_fort'){ const u=k.slice(4);
    if(curAction()!=='build'||!isRobo(0)||!isHomeCastle(t)||t.owner!==0||!roboUpTargets(0,u).length) return;
    ui.roboUp=u; ui.sel=null; render(); return; }""")
rep("""function buildWall(i,j){ if(curAction()!=='advance') return; doBuildWall(0,i,j,curLvl()); render(); }""",
"""function buildWall(i,j){ if(curAction()!=='advance') return; doBuildWall(0,i,j,curLvl()); render(); }
function roboUpgrade(i){ if(curAction()!=='build'||!ui.roboUp) return; const k=ui.roboUp;
  doRoboUp(0,i,curLvl());
  if(!roboUpTargets(0,k).length||!canPayB(0,k,costOf(k,curLvl()))) ui.roboUp=null;   // nothing more to upgrade, or out of materials
  render(); }""")
rep("build=undoable(build); advance=undoable(advance); buildWall=undoable(buildWall);",
    "build=undoable(build); advance=undoable(advance); buildWall=undoable(buildWall); roboUpgrade=undoable(roboUpgrade);")
rep("""  if(curAction()==='advance'&&ui.wallFor!=null){
    if(wallSides(ui.wallFor).includes(i)&&wallOn(ui.wallFor,i)<WALL_HP){ buildWall(ui.wallFor,i); return; }
    ui.wallFor=null;
  }""","""  if(curAction()==='advance'&&ui.wallFor!=null){
    if(wallSides(ui.wallFor).includes(i)&&wallOn(ui.wallFor,i)<WALL_HP){ buildWall(ui.wallFor,i); return; }
    ui.wallFor=null;
  }
  if(curAction()==='build'&&ui.roboUp){   // Robots: tap a factory to upgrade it
    if(roboUpTargets(0,ui.roboUp).includes(i)){ roboUpgrade(i); return; }
    ui.roboUp=null;
  }""")
n=s.count("ui.wallFor=null;"); s=s.replace("ui.wallFor=null;","ui.wallFor=null; ui.roboUp=null;"); print('pick mode resets',n)
rep("""  else if(a==='walldone'){ ui.wallFor=null; ui.roboUp=null; render(); }""","""  else if(a==='walldone'){ ui.wallFor=null; ui.roboUp=null; render(); }
  else if(a==='robodone'){ ui.roboUp=null; render(); }""")
# the reminder before ending a Build with things still possible
rep("""    const can=mine.some(t=>t.terrain==='plain'&&bCount(t)<bMax()&&(t.castle?['market']:BUILD_KINDS).concat(mammNow(0,'build')&&!t.wh?['wh']:[]).some(k=>canPayB(0,k,costOf(k,lvl))));""",
"""    const can=mine.some(t=>t.terrain==='plain'&&bCount(t)<bMax()&&(t.castle||isRobo(0)?['market']:BUILD_KINDS).concat(mammNow(0,'build')&&!t.wh?['wh']:[]).some(k=>canPayB(0,k,costOf(k,lvl))))
      ||(isRobo(0)&&homeMarket(0)&&['barracks','fort'].some(k=>roboUpTargets(0,k).length&&canPayB(0,k,costOf(k,lvl))));""")

# ---- the zoomed Build view: Robots get only the market around a hex; the home castle adds Barracks and Fortress upgrades ----
rep("""  const spots=[['barracks',150,1],['fort',90,0],['market',30,5]].filter(x=>!(x[0]==='fort'&&isDino(0)));   // the Dinosaurs build no forts""",
"""  const spots=[['barracks',150,1],['fort',90,0],['market',30,5]].filter(x=>!(x[0]==='fort'&&isDino(0)))   // the Dinosaurs build no forts
    .filter(x=>!isRobo(0)||x[0]==='market'||(!recruiting&&isHomeCastle(t)));   // Robots: a market, and factory upgrades at the home castle""")
rep("""    const price=costOf(kind,lvl,t), castleNo=t.castle&&kind!=='market'&&kind!=='wh',""",
"""    if(isRobo(0)&&kind!=='market'){   // the home castle's factory upgrades: pick one, then tap the factory to upgrade
      const tg=roboUpTargets(0,kind), price=costOf(kind,lvl,t), can=tg.length>0&&canPayB(0,kind,price);
      const note=tg.length?priceIc(kind,price):kind==='fort'?'No barracks':'No factory';
      html+=`<button class="bub${can?'':' off'}" data-bk="rup_${kind}" ${pos} ${can?'':'disabled'} aria-label="${tg.length?`Add a ${ROBO_NAME[kind]} to one of your factories: ${priceTxt(kind,price)}`:kind==='fort'?'Fortress: first give a factory a barracks':'Barracks: first build a factory (a market)'}">${bldImg(kind+'_robots')}<b>${ROBO_NAME[kind]}</b><small>${note}</small></button>`;
      continue;
    }
    const price=costOf(kind,lvl,t), castleNo=t.castle&&kind!=='market'&&kind!=='wh',""")
rep("""const buildHex=()=>{ if(!S||!isHumanTurn()||ui.sel==null) return null;""",
    """const buildHex=()=>{ if(!S||!isHumanTurn()||ui.sel==null||ui.roboUp) return null;""")
# the factories you can upgrade are ringed
rep("""  wallOpen.forEach(j=>hl.add(j));""","""  wallOpen.forEach(j=>hl.add(j));
  if(isHumanTurn()&&curAction()==='build'&&ui.roboUp) roboUpTargets(0,ui.roboUp).forEach(j=>hl.add(j));""")

# ---- the factory on the board: one picture by level, centred in the hex ----
rep("""    else if(blds.length&&owned){
      const fac=S.players[t.owner].faction,""","""    else if(owned&&!t.castle&&S.players[t.owner].faction==='robots'&&roboLv(t)){
      const lv=roboLv(t), z=[0,17,19,21][lv], bk=['','market','barracks','fort'][lv]+'_robots', x=cx-z/2, y=cy-z/2+1.2;
      castles+=`<use href="#b-${bk}" transform="translate(${x.toFixed(2)} ${y.toFixed(2)}) scale(${(z/16).toFixed(4)})"/>`;
      for(let q=0;q<(t.bk||0);q++) tops+=`<rect x="${(x+z-.6).toFixed(2)}" y="${(y+z*.45+q*2.2).toFixed(2)}" width="1.7" height="1.7" fill="#efc15a" stroke="#060907" stroke-width=".35"/>`;   // the barracks level
    }
    else if(blds.length&&owned){
      const fac=S.players[t.owner].faction,""")

# ---- the side panel during Build ----
rep("""  } else if(a==='build'){
    const lvl=curLvl();
    if(sel&&sel.owner===0&&sel.terrain==='plain'){""","""  } else if(a==='build'){
    const lvl=curLvl();
    if(isRobo(0)&&ui.roboUp){ const k=ui.roboUp, n=roboUpTargets(0,k).length;
      h+=`<div class="row-label">${bldImg(k+'_robots').replace('<img','<img style="height:1.4em;vertical-align:-.35em"')} ${ROBO_NAME[k]}: ${priceTxt(k,costOf(k,lvl))} each (you have ${matOf(0)})</div>${matRow()}<div class="btns" style="margin-bottom:.5em"><button data-act="robodone">Done</button></div><p class="hint">Tap a ringed factory to add a ${k==='fort'?'fortress':'barracks'} to it. ${n} of your factories can take one.</p>`;
    } else if(isRobo(0)&&sel&&sel.owner===0&&isHomeCastle(sel)){
      h+=matRow()+`<p class="hint">Your home castle upgrades your factories: tap <b>Barracks</b> or <b>Fortress</b> on the map, then tap the factory to upgrade. Or tap <b>Market</b> to build one here. Tap the castle again to zoom back out.</p>`;
    } else if(isRobo(0)&&sel&&sel.owner===0&&sel.terrain==='plain'){
      h+=matRow()+`<p class="hint">${bCount(sel)?`This hex already has a factory${roboNext(sel)?`. Upgrade it from your home castle with a ${roboNext(sel)==='fort'?'fortress':'barracks'}`:', fully upgraded'}.`:`Tap <b>Market</b> to build a factory here. It starts as a market; your home castle can then add a barracks, then a fortress.`} Tap the hex again to zoom back out.</p>`;
    } else if(sel&&sel.owner===0&&sel.terrain==='plain'){""")
rep("""    h+=`<ul class="bkey">${BUILD_KINDS.filter(k=>!(k==='fort'&&isDino(0))).concat(""",
"""    if(isRobo(0)) h+=`<ul class="bkey">${roboKeyHtml(lvl)}</ul>`; else
    h+=`<ul class="bkey">${BUILD_KINDS.filter(k=>!(k==='fort'&&isDino(0))).concat(""")

# ---- help: the faction screen and How to play ----
rep("""// the Dinosaurs' volcano and Alamosaurus guards, for How to play and the faction screen""",
"""// the Robots' factory, for the Build panel, How to play and the faction screen
const roboKeyHtml=lvl=>[['market',`${BUILD_INFO.market.desc}. Every Robot building starts as one, one per hex`],
  ['barracks','added to a factory from your home castle: recruits here and trains barracks units, upgraded with Advancements'],
  ['fort','added to a factory that has a barracks, from your home castle: +1 on the defenders\\' best die, trains fortress units and holds a trebuchet']]
  .map(([k,d])=>`<li>${bldImg(k+'_robots').replace('<img','<img style="height:1.5em;vertical-align:-.4em"')} <b>${k==='market'?'Factory (market)':ROBO_NAME[k]}</b> ${priceTxt(k,costOf(k,lvl||0))}: ${d}</li>`).join('');
const roboSpecialsHtml=()=>`Robots build one <b>factory</b> per hex. It starts as a market (gold). Then, during Build, tap your home castle and pick <b>Barracks</b> or <b>Fortress</b> (materials) and tap a factory to upgrade it: first a barracks, then a fortress. Each factory is upgraded on its own, and only while you hold your home castle.<ul class="bkey">${roboKeyHtml(0)}</ul>`;
// the Dinosaurs' volcano and Alamosaurus guards, for How to play and the faction screen""")
rep("""nos'?`<h3>Volcano and guards</h3><p>${dinoSpecialsHtml()}</p>`:''}""",
    """nos'?`<h3>Volcano and guards</h3><p>${dinoSpecialsHtml()}</p>`:''}${fid==='robots'?`<h3>Factories</h3><p>${roboSpecialsHtml()}</p>`:''}""")
rep("""    <li><b>Buildings.</b> <span class="px px-market" aria-hidden="true"></span>""",
    """    <li><b>Buildings.</b> ${isRobo(0)?roboSpecialsHtml()+' ':''}<span class="px px-market" aria-hidden="true"></span>""")

# ---- the computer: markets on empty hexes (one building per hex), barracks and forts become factory upgrades ----
rep("""    const plan=smart?aiBuildPlan2(pid,{treb,lvl,keep:keepR}):aiBuildPlan(pid,{treb,lvl});
    if(!plan) break;""","""    let plan=smart?aiBuildPlan2(pid,{treb,lvl,keep:keepR}):aiBuildPlan(pid,{treb,lvl});
    if(!plan) break;
    if(isRobo(pid)&&plan.k!=='market'){   // Robots: upgrade the factory nearest where the plan wanted it; with none, build a factory there first
      const tg=homeMarket(pid)?roboUpTargets(pid,plan.k).sort((a,b)=>man(a,plan.id)-man(b,plan.id)):[];
      if(tg.length) plan={k:plan.k,id:tg[0]};
      else if(plan.k==='barracks'&&!S.tiles[plan.id].castle&&!bCount(S.tiles[plan.id])) plan={k:'market',id:plan.id};
      else break;
    }""")
rep("""    S.tiles[plan.id][plan.k]=(S.tiles[plan.id][plan.k]|0)+1; noteUnlock(pid,plan.k,S.tiles[plan.id]); ids.push(plan.id);
    addLog(`${p.name} build a ${BUILD_INFO[plan.k].name}.`,pid);""",
"""    S.tiles[plan.id][plan.k]=(S.tiles[plan.id][plan.k]|0)+1; noteUnlock(pid,plan.k,S.tiles[plan.id]); ids.push(plan.id);
    addLog(isRobo(pid)?(plan.k==='market'?`${p.name} build a factory.`:`${p.name} upgrade a factory with a ${plan.k==='fort'?'fortress':'barracks'}.`):`${p.name} build a ${BUILD_INFO[plan.k].name}.`,pid);""")
open(p,'w').write(s); print('robots patch1 ok')
s=open(p).read()
rep("""if(a==='build') return `Build as many as you can afford: Markets (${costOf('market',lvl)} gold)${isDino(pid)?'':`, Forts""",
"""if(a==='build'&&isRobo(pid)) return `Build factories (${costOf('market',lvl)} gold, one per hex; each starts as a market) and upgrade them from your home castle: a Barracks, then a Fortress (${matTxt(costOf('barracks',lvl))} each). Buy materials at your markets`;
  if(a==='build') return `Build as many as you can afford: Markets (${costOf('market',lvl)} gold)${isDino(pid)?'':`, Forts""")
open(p,'w').write(s); print('robots patch1b ok')
s=open(p).read()
# Robots capturing a hex: whatever stood there becomes one factory, at the level its buildings add up to
rep("""  if(isDino(p.id)&&(B.treb||B.treb2)){""","""  if(isRobo(p.id)&&!B.castle&&bCount(B)){ const bk=!!(B.barracks||B.fort), ft=!!(B.fort&&B.barracks);
    B.market=1; B.barracks=bk?1:0; B.fort=ft?1:0; B.wh=0; if(!bk) B.bk=0; addLog(`${p.name} turn the captured buildings into a factory.`,p.id); }
  if(isDino(p.id)&&(B.treb||B.treb2)){""")
open(p,'w').write(s); print('robots patch1c ok')

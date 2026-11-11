import sys,re
P='/tmp/claude-0/-home-claude/fb256341-5d08-5e47-8b49-8c9035f9f7b9/scratchpad/cc/'
s=open(P+'stage1.html',encoding='utf-8').read()
def rep(old,new,count=1):
    global s
    n=s.count(old)
    if n!=count:
        print('COUNT',n,'for',old[:140]); sys.exit(1)
    s=s.replace(old,new)

# ================= Fortify: a wild card =================
rep("""  fortify:{icon:'<span class="px px-fortify" aria-hidden="true"></span>',name:'Fortify',instant:true},""",
    """  fortify:{icon:'<span class="px px-fortify" aria-hidden="true"></span>',name:'Fortify'},   // a wild card: a regroup, then Build, Advancements or Recruit (see fxOn)""")

rep("""const curAction=()=>S.play?cardOf(S.current,S.play.card).actions[S.play.step]:null;""",
r"""const cardAction=()=>S&&S.play?cardOf(S.current,S.play.card).actions[S.play.step]:null;   // the action printed on the card
// Fortify is a wild card (Ethan, 2026-11-10). First a regroup: units move any distance between the player's own hexes, as often
// as they like (no attacks or claiming), and stay ready to move again. Then the player picks Build, Advancements or Recruit
// (two of them at level 2, all three at level 3), each played like the basic action. The old +1 defense is gone.
// While it runs, S.play.fx = {ph:'regroup'|'pick'|'act', n: picks allowed, done: picks made, cur: the pick being played}.
const FX_PICKS=['build','advance','recruit'], REGROUP_MOVES=99;
const fxPicksAt=(pid,eff)=>eff>=3?3:eff>=1?2:1;
const fxOn=()=>!!(S&&S.play&&S.play.fx&&cardAction()==='fortify');
const regrouping=()=>fxOn()&&S.play.fx.ph==='regroup';
// the action being played now: inside a Fortify, the regroup plays as a Move and each pick as its own action
const curAction=()=>{ if(!S||!S.play) return null; const a=cardAction(); if(a!=='fortify'||!S.play.fx) return a; const f=S.play.fx; return f.ph==='regroup'?'move':f.ph==='act'?f.cur:'fortify'; };""")
rep("""const rawLvl=()=>S&&S.play?lvlOf(S.current,S.play.card,S.play.step):0;   // the current action's upgrade level""",
    """const rawLvl=()=>S&&S.play?(fxOn()?0:lvlOf(S.current,S.play.card,S.play.step)):0;   // the current action's upgrade level (a Fortify's regroup and picks play at the basic level)""")
rep("""const movesLimit=pid=>modsOf(pid).movesPerAction+""","""const movesLimit=pid=>(regrouping()&&S.current===pid)?REGROUP_MOVES:modsOf(pid).movesPerAction+""")
rep("""function moveTargetsCore(from,lvl,far){
  lvl=lvl||0;
  const pid=S.tiles[from].owner, out=new Set();""",
r"""// a Fortify's regroup: any of your own hexes reached through your own open land (not mountains), any distance
function regroupTargets(from){ const pid=S.tiles[from].owner, seen=new Set([from]); let fr=[from];
  while(fr.length){ const nx=[]; for(const c of fr) for(const n of nbrs(c)) if(!seen.has(n)&&ownRoad(n,pid)){ seen.add(n); nx.push(n); } fr=nx; }
  seen.delete(from); return [...seen]; }
function moveTargetsCore(from,lvl,far){
  lvl=lvl||0;
  const pid=S.tiles[from].owner, out=new Set();
  if(regrouping()&&pid===S.current) return regroupTargets(from);""")
# units that regroup stay ready, so a Move later on the same card can still send them
rep("""  if(B.owner===A.owner){ addArmy(B,sel,false); return res; }""",
    """  if(B.owner===A.owner){ addArmy(B,sel,regrouping()&&A.owner===S.current); return res; }   // a regroup leaves them ready to move again""")

# the faction abilities that come with Fortify
a=s.index("  if(a==='fortify'){\n    const mate=mammOn(pid,raw)?mating(pid):null;")
b=s.index("  return '';\n}\n\n// ---------- Human: cards and steps ----------")
s=s[:a]+r"""  if(a==='fortify') return fortifyStart(pid,raw);
"""+s[b:]
rep("""  return '';
}

// ---------- Human: cards and steps ----------""",
r"""  return '';
}
// A Fortify starts with its faction ability: the Mammals' Mating, the Robots' Update or the Dinosaurs' Herd.
function fortifyStart(pid,raw){
  const p=S.players[pid], out=[];
  const mate=mammOn(pid,raw)?mating(pid):null;
  if(mate) out.push(mate.n?`Mating: +${mate.n} young on ${mate.ids.length} hex${mate.ids.length===1?'':'es'}`:'Mating: no pairs to breed yet');
  if(roboOn(pid,raw)){ p.updNext=true; addLog(`${p.name} run an Update: +1 attack and +1 damage on their next turn.`,pid); out.push(`Update: +1 attack and +1 damage on ${pid===0?'your':'their'} next turn`); }
  if(dinoOn(pid,raw)){ p.herd=true; addLog(`${p.name} herd together: no surprise attacks on them until their next turn.`,pid); out.push(`Herd: no surprise attacks on ${pid===0?'you':'them'} until ${pid===0?'your':'their'} next turn`); }
  const n=fxPicksAt(pid,effLvl(pid,raw));
  addLog(`${p.name} fortify: a regroup, then ${n>=3?'Build, Advancements and Recruit':n===2?'two of Build, Advancements and Recruit':'Build, Advancements or Recruit'}.`,pid);
  return out.length?`<span class="px px-fortify" aria-hidden="true"></span> ${out.join('. ')}`:'';
}

// ---------- Human: cards and steps ----------""")
rep("""    ui.notes.push(resolveInstant(S.current,card.actions[S.play.step],curLvl(),rawLvl()));
    if(S.play.step>=card.actions.length-1) break;
    S.play.step++;
  }
  if(curAction()==='move') S.play.moves=0;""",
r"""    ui.notes.push(resolveInstant(S.current,card.actions[S.play.step],curLvl(),rawLvl()));
    if(S.play.step>=card.actions.length-1) break;
    S.play.step++;
  }
  if(card.actions[S.play.step]==='fortify'&&!S.play.fx){   // Fortify: its ability, then the regroup
    const raw=lvlOf(S.current,S.play.card,S.play.step), note=fortifyStart(S.current,raw);
    if(note) ui.notes.push(note);
    S.play.fx={ph:'regroup',n:fxPicksAt(S.current,effLvl(S.current,raw)),done:[],cur:null};
  }
  if(curAction()==='move') S.play.moves=0;""")
rep("""function leftoverWarning(){
  const a=curAction(), me=S.players[0], lvl=curLvl(), mine=S.tiles.filter(t=>t.owner===0);""",
r"""function leftoverWarning(){
  const a=curAction(), me=S.players[0], lvl=curLvl(), mine=S.tiles.filter(t=>t.owner===0);
  if(fxOn()){ const f=S.play.fx; if(f.ph==='regroup') return null;   // regrouping is optional
    if(f.ph==='pick'){ const left=f.n-f.done.length; return left>0?`Your Fortify can still <b>${left===1?(f.done.length?'pick one more':'pick one'):'pick '+left+' more'}</b> of Build, Advancements and Recruit.`:null; } }""")
rep("""  if(force!==true){ const w=leftoverWarning(); if(w){ confirmLeftover(w,S.play.step>=cardOf(0,S.play.card).actions.length-1); return; } }
  const card=cardOf(0,S.play.card);
  ui.sel=null; ui.battle=null; ui.wallFor=null; ui.undo=[]; ui.undoLocked=false;
  if(S.play.step<card.actions.length-1){ S.play.step++; enterStep(); render(); }
  else finishTurn(0);
}""",
r"""  if(force!==true){ const w=leftoverWarning(); if(w){ confirmLeftover(w,lastStepNow()); return; } }
  const card=cardOf(0,S.play.card);
  ui.sel=null; ui.battle=null; ui.wallFor=null; ui.undo=[]; ui.undoLocked=false; ui.train=null; ui.info=null;
  if(fxNext()){ render(); return; }   // still inside a Fortify: the regroup, then the picks
  if(S.play.step<card.actions.length-1){ S.play.step++; enterStep(); render(); }
  else finishTurn(0);
}
// a Fortify's phases: the regroup, then the picks one at a time. True while the Fortify goes on.
function fxNext(){
  if(!fxOn()) return false;
  const f=S.play.fx;
  if(f.ph==='regroup'){ f.ph='pick'; S.play.moves=0; return true; }
  if(f.ph==='act'){ f.done.push(f.cur); f.cur=null; if(f.done.length<f.n&&FX_PICKS.some(k=>!f.done.includes(k))){ f.ph='pick'; return true; } }
  S.play.fx=null; return false;
}
// does the button end the turn? (not while a Fortify still has its picks to come)
const lastStepNow=()=>{ if(!S.play) return false; const f=fxOn()?S.play.fx:null;
  if(f&&(f.ph==='regroup'||(f.ph==='act'&&f.done.length+1<f.n))) return false;
  return S.play.step>=cardOf(S.current,S.play.card).actions.length-1; };
// the human picks what their Fortify does next
function fxChoose(k){
  if(!isHumanTurn()||!fxOn()||S.play.fx.ph!=='pick'||!FX_PICKS.includes(k)||S.play.fx.done.includes(k)) return;
  const f=S.play.fx; f.ph='act'; f.cur=k; S.play.freeWalls=0;   // no Reforest walls left over from an earlier action
  ui.sel=null; ui.battle=null; ui.wallFor=null; ui.train=null; ui.info=null;
  render();
}""")
rep("""mythAct=undoable(mythAct);""","""mythAct=undoable(mythAct); fxChoose=undoable(fxChoose); tradeBuy=undoable(tradeBuy);""")

# ---- the card column during a Fortify ----
rep("""function stepBody(){
  const me=S.players[0], a=curAction(), sel=ui.sel!=null?S.tiles[ui.sel]:null;
  let h=notesHtml();""",
r"""function fxHead(){
  const f=S.play.fx;
  if(f.ph==='regroup') return `<div class="row-label"><span class="px px-fortify" aria-hidden="true"></span> Regroup</div>`;
  if(f.ph==='act') return `<div class="row-label"><span class="px px-fortify" aria-hidden="true"></span> Fortify${f.n>1?` (${f.done.length+1} of ${f.n})`:''}: ${ACTIONS[f.cur].icon} ${ACTIONS[f.cur].name}</div>`;
  return '';
}
const fxPickNote=k=>isMyth(0)?(k==='build'?'Life Trees':k==='advance'?'Mages, castle, domes':'Minions, Mages, monsters')
  :k==='build'?(isDino(0)?'Markets and barracks':'Markets, forts, barracks'):k==='advance'?(isDino(0)?'Barracks, guards, volcano, walls':'Barracks, trebuchets, walls'):'Train units';
function fxPickBody(){
  const f=S.play.fx, left=f.n-f.done.length;
  const btn=k=>{ const did=f.done.includes(k), no=did||left<=0;
    return `<button class="build" data-act="fxpick" data-k="${k}" ${no?'disabled':''}><span class="bi">${ACTIONS[k].icon}</span><span><b>${ACTIONS[k].name}</b><br><small>${did?'Done':fxPickNote(k)}</small></span></button>`; };
  return `<div class="row-label"><span class="px px-fortify" aria-hidden="true"></span> ${left<=0?'Fortify done':f.n>=3?(f.done.length?`${left} more to do, in any order`:'Do all three, in any order'):f.done.length?'Pick one more':f.n===2?'Pick two, one at a time':'Pick one'}</div>
    <div class="builds">${FX_PICKS.map(btn).join('')}</div>
    <p class="hint" style="margin-top:.5em">Each plays like the basic action, without this card's upgrades.${usesMat(0)?` You have <b>${S.players[0].gold} gold</b> and <b>${matTxt(matOf(0))}</b>.`:''}</p>`;
}
// gold and materials, with a button to buy materials (Build and Advancements)
function matRow(){
  if(!usesMat(0)) return '';
  const me=S.players[0], left=matLeft(0);
  return `<div class="row-label matrow">${MAT_IC} <b>${matTxt(matOf(0))}</b> · <span class="px px-coin" aria-hidden="true"></span> ${me.gold} gold <button class="ghost" data-act="trade" ${left>0&&me.gold>=MAT_PRICE?'':'disabled'}>Buy materials${left>0?` (${left} left)`:''}</button></div>`;
}
function stepBody(){
  const me=S.players[0], a=curAction(), sel=ui.sel!=null?S.tiles[ui.sel]:null;
  let h=notesHtml();
  if(fxOn()) h+=fxHead();
  if(a==='fortify') return h+fxPickBody();
  if(a==='move'&&regrouping()){
    const ready=S.tiles.filter(t=>t.owner===0).reduce((s,t)=>s+t.fresh,0);
    if(sel&&sel.troops>0) h+=`<div class="harmy">${sel.owner===0?'Here':'Enemy'}: ${armyList(sel.army)}${sel.owner===0&&sel.fresh<sel.troops?` <span class="sub">(${sel.fresh} ready)</span>`:''}</div>`;
    h+=`<p class="hint">${sel&&sel.owner===0&&sel.fresh>0?'Tap a highlighted hex to send units there. ':sel&&sel.owner===0&&sel.troops>0?'Those units already moved this turn. ':'Tap a hex with your units, then a highlighted hex of yours. '}Regroup moves are free: as many as you like, any distance through your own land (not mountains), but no attacks or claiming. Units that regroup can still move again later this turn. You have <b>${ready}</b> unit${ready===1?'':'s'} ready.</p>`;
    h+=`<p class="hint" style="margin-top:.4em">Then tap <b>Done regrouping</b> to pick ${S.play.fx.n>=3?'the order of Build, Advancements and Recruit':S.play.fx.n===2?'two of Build, Advancements and Recruit':'Build, Advancements or Recruit'}.</p>`;
    return h;
  }""")
# the main button's words during a Fortify
rep("""    const last=S.play.step>=cardOf(0,S.play.card).actions.length-1;
    P.innerHTML=bigCard(0,S.play.card,{step:S.play.step,tag:'Playing',cls:'playing',body:stepBody(),
      foot:`${ui.undo&&ui.undo.length?'<button data-act="undo" aria-label="Undo your last change in this action">↶ Undo</button>':''}<button class="primary" id="nextBtn" data-act="next">${last?'End turn':'Next action'}</button>`});""",
r"""    const last=lastStepNow(), f=fxOn()?S.play.fx:null;
    const lbl=f&&f.ph==='regroup'?'Done regrouping':f&&f.ph==='act'&&f.done.length+1<f.n?`Done with ${ACTIONS[f.cur].name}`:f&&f.ph==='pick'&&f.done.length<f.n?(last?'Skip, end turn':'Skip, next action'):last?'End turn':'Next action';
    P.innerHTML=bigCard(0,S.play.card,{step:S.play.step,tag:'Playing',cls:'playing',body:stepBody(),
      foot:`${ui.undo&&ui.undo.length?'<button data-act="undo" aria-label="Undo your last change in this action">↶ Undo</button>':''}<button class="${f&&f.ph==='pick'&&f.done.length<f.n?'':'primary'}" id="nextBtn" data-act="next">${lbl}</button>`});""")
rep("""  else if(a==='my') mythAct(b.dataset.op,b.dataset.k);
});""","""  else if(a==='my') mythAct(b.dataset.op,b.dataset.k);
  else if(a==='fxpick') fxChoose(b.dataset.k);
  else if(a==='trade') openTrade();
});""")

# ---- the computer's Fortify ----
rep("""    if(ACTIONS[a].instant){ resolveInstant(pid,a,lvl,raw); yield {kind:'instant'}; }""",
    """    if(a==='fortify'){ yield* aiFortifyGen(pid,raw,card.actions.slice(s+1)); continue; }
    if(ACTIONS[a].instant){ resolveInstant(pid,a,lvl,raw); yield {kind:'instant'}; }""")
rep("""// How good the board looks for pid, in rough gold terms.""",
r"""// The computer's Fortify: its ability, a regroup toward the front (or into a castle in danger), then its picks.
function* aiFortifyGen(pid,raw,later){
  fortifyStart(pid,raw);
  const n=fxPicksAt(pid,effLvl(pid,raw));
  S.play.fx={ph:'regroup',n,done:[],cur:null}; S.play.moves=0;
  yield* aiRegroupGen(pid);
  S.play.fx.ph='pick';
  const order=aiFxOrder(pid,n,later);
  for(let i=0;i<order.length;i++){
    if(S.over) break;
    const k=order[i], f=S.play.fx; f.ph='act'; f.cur=k; S.play.freeWalls=0;
    yield {kind:'flash',ids:aiDoPick(pid,k,order.slice(i+1).concat(later))};
    f.done.push(k);
  }
  S.play.fx=null;
}
function aiDoPick(pid,k,later){
  if(isMyth(pid)) return mythAi(pid,k,later);
  if(k==='recruit') return aiRecruit(pid,later,0);
  if(k==='build') return aiBuild(pid,0,later);
  return aiAdvance(pid,0);
}
// which picks: each is tried on a copy of the board, the best kept (then the next, from the board that one leaves)
function aiFxOrder(pid,n,later){
  if(n>=3) return ['build','advance','recruit'];
  if(!aiSmart(pid)&&Math.random()<0.5) return shuffle(FX_PICKS).slice(0,n);   // Easy: a quick guess half the time
  const base=S, out=[]; let cur=JSON.stringify(S);
  try{
    for(let r=0;r<n;r++){
      let best=null, bv=-Infinity;
      for(const k of FX_PICKS){ if(out.includes(k)) continue;
        S=JSON.parse(cur); S.log=[]; S.play.fx.ph='act'; S.play.fx.cur=k;
        const ids=aiDoPick(pid,k,later)||[], v=evalFor(pid)+(k==='build'?2*ids.length:0)+(ids.length?0.5:0);
        if(v>bv){ bv=v; best=k; } }
      out.push(best);
      S=JSON.parse(cur); S.log=[]; S.play.fx.ph='act'; S.play.fx.cur=best; aiDoPick(pid,best,later); cur=JSON.stringify(S);
    }
  } finally { S=base; }
  return out;
}
// the regroup: troops in safe land walk up to the front line nearest the castles it wants, or into a castle in danger
function* aiRegroupGen(pid){
  const lim=aiSmart(pid)?3:2;
  for(let k=0;k<lim;k++){
    if(S.over) return;
    const dE=bfs(foeTiles(pid)), D=i=>fin(dE[i]);
    const dC=bfs(S.tiles.filter(x=>x.castle&&x.owner!==pid).map(x=>x.id),null,i=>canEnter(i,0)), DC=i=>fin(dC[i]);
    let best=null;
    S.tiles.forEach(s=>{
      if(s.owner!==pid||s.fresh<=0) return;
      let guard=0; if(s.castle){ const near=enemyNear(s.id,pid,3); guard=guardUnits(s,s.id===S.homes[pid]?Math.max(2,near+1):near); }
      const avail=Math.min(s.fresh,s.troops-guard); if(avail<=0) return;
      if(D(s.id)<=1&&enemyNear(s.id,pid,1)>0) return;   // already facing the enemy: stays
      regroupTargets(s.id).forEach(i=>{
        const b=S.tiles[i], thr=enemyNear(i,pid,2), danger=b.castle&&thr>tp(b);
        let v;
        if(danger) v=8+2*Math.min(thr-tp(b),10);
        else if(D(i)===1&&D(i)<D(s.id)) v=4+Math.max(0,6-DC(i))+0.3*Math.min(enemyNear(i,pid,1),10);
        else return;
        const sel=pickUnits(s,avail), sc=v*armyGold(sel)/3;
        if(!best||sc>best.v) best={v:sc,from:s.id,to:i,n:sel};
      });
    });
    if(!best) return;
    S.play.moves=(S.play.moves||0)+1;
    yield {kind:'move',from:best.from,to:best.to,res:executeMove(best.from,best.to,best.n,0)};
  }
}
// How good the board looks for pid, in rough gold terms.""")
rep("""const AI_UP_PREF={recruit:5, move:4.5, harvest:4, fortify:2, advance:2, build:1};""",
    """const AI_UP_PREF={recruit:5, move:4.5, harvest:4, fortify:4.2, advance:2, build:1};   // Fortify's upgrades add picks""")

# ---- texts that spoke of Fortify's defense ----
rep("""<li><span class="px px-fortify" aria-hidden="true"></span> Fortified: +${m.fortifyBonus} defense until its owner's next turn (an upgraded Fortify gives forts and castles more)</li>""","")

# ================= Materials =================
rep("""  p.updNow=!!p.updNext; p.updNext=false; p.herd=false;""","""  p.updNow=!!p.updNext; p.updNext=false; p.herd=false; p.tr=0;   // p.tr: materials bought from the markets this turn""")
# human building
rep("""  const price=costOf(k,curLvl());
  if(curAction()!=='build'||bCount(t)>=bMax()||me.gold<price||t.owner!==0||t.terrain!=='plain') return;""",
    """  const price=costOf(k,curLvl());
  if(curAction()!=='build'||bCount(t)>=bMax()||!canPayB(0,k,price)||t.owner!==0||t.terrain!=='plain') return;""")
rep("""  me.gold-=price; t[k]=(t[k]|0)+1; noteUnlock(0,k,t);""","""  payB(0,k,price); t[k]=(t[k]|0)+1; noteUnlock(0,k,t);""")
rep("""  if(p.gold<price) return false;
  p.gold-=price; if(free) S.play.freeBk=true; t.bk=lv+1; noteUnlock(pid,'barracks',t);""",
    """  if(matOf(pid)<price) return false;
  spendMat(pid,price); if(free) S.play.freeBk=true; t.bk=lv+1; noteUnlock(pid,'barracks',t);""")
rep("""  const price=trebPrice(t), turns=trebTurns(t,lvl); if(p.gold<price) return false;
  p.gold-=price;""","""  const price=trebPrice(t), turns=trebTurns(t,lvl); if(matOf(pid)<price) return false;
  spendMat(pid,price);""")
rep("""  if(t.owner!==pid||!wallSides(i).includes(j)||was>=WALL_HP||p.gold<price) return false;
  p.gold-=price; setWall(i,j,WALL_HP); if(free) S.play.freeWalls--;""",
    """  if(t.owner!==pid||!wallSides(i).includes(j)||was>=WALL_HP||matOf(pid)<price) return false;
  spendMat(pid,price); setWall(i,j,WALL_HP); if(free) S.play.freeWalls--;""")
# leftover warnings
rep("""    const can=mine.some(t=>t.terrain==='plain'&&bCount(t)<bMax()&&(t.castle?['market']:BUILD_KINDS).concat(mammNow(0,'build')&&!t.wh?['wh']:[]).some(k=>me.gold>=costOf(k,lvl)));
    return can?`You have <b>${me.gold} gold</b> and room to build more.`:null;""",
    """    const can=mine.some(t=>t.terrain==='plain'&&bCount(t)<bMax()&&(t.castle?['market']:BUILD_KINDS).concat(mammNow(0,'build')&&!t.wh?['wh']:[]).some(k=>canPayB(0,k,costOf(k,lvl))));
    return can?`You have <b>${me.gold} gold</b> and <b>${matTxt(matOf(0))}</b>, and room to build more.`:null;""")
rep("""      if(t.barracks&&(t.bk||0)<3){ const lv=t.bk||0, free=lvl>=1&&!S.play.freeBk&&lv===0; if(free||me.gold>=BARRACKS_UP[lv]) return true; }
      if(canTrebAt(t)&&me.gold>=trebPrice(t)) return true;
      return (me.gold>=wallCost(lvl)||freeWallsLeft(0)>0)&&wallSides(t.id).some(j=>wallOn(t.id,j)<WALL_HP);
    });
    return can?`You have <b>${me.gold} gold</b> and can still upgrade a barracks, start a trebuchet or build walls.`:null;""",
    """      if(t.barracks&&(t.bk||0)<3){ const lv=t.bk||0, free=lvl>=1&&!S.play.freeBk&&lv===0; if(free||matOf(0)>=BARRACKS_UP[lv]) return true; }
      if(canTrebAt(t)&&matOf(0)>=trebPrice(t)) return true;
      return (matOf(0)>=wallCost(lvl)||freeWallsLeft(0)>0)&&wallSides(t.id).some(j=>wallOn(t.id,j)<WALL_HP);
    });
    return can?`You have <b>${matTxt(matOf(0))}</b> and can still upgrade a barracks, start a trebuchet or build walls.`:null;""")
# the round buttons: building
rep("""    const price=costOf(kind,lvl), castleNo=t.castle&&kind!=='market'&&kind!=='wh', has=kind==='wh'&&!!t.wh, can=!full&&!castleNo&&!has&&me.gold>=price;
    const note=has?'Has one':full?'Full':castleNo?'Not here':`${price} gold`;
    html+=`<button class="bub${can?'':' off'}" data-bk="${kind}" ${pos} ${can?'':'disabled'} aria-label="Build a ${BUILD_INFO[kind].name}: ${note}">""",
    """    const price=costOf(kind,lvl), castleNo=t.castle&&kind!=='market'&&kind!=='wh', has=kind==='wh'&&!!t.wh, can=!full&&!castleNo&&!has&&canPayB(0,kind,price);
    const nt=has?'Has one':full?'Full':castleNo?'Not here':priceTxt(kind,price), note=has||full||castleNo?nt:priceIc(kind,price);
    html+=`<button class="bub${can?'':' off'}" data-bk="${kind}" ${pos} ${can?'':'disabled'} aria-label="Build a ${BUILD_INFO[kind].name}: ${nt}">""")
# the round buttons: Advancements
rep("""        can:!!t.barracks&&lv<3&&me.gold>=bp, note:!t.barracks?'None here':lv>=3?'Max level':free?'Free':`${bp} gold`,
        label:!t.barracks?'Barracks upgrade: no barracks on this hex':lv>=3?'Barracks: already level 3':`Upgrade the barracks to level ${nl} for ${free?'free':bp+' gold'}`},""",
    """        can:!!t.barracks&&lv<3&&matOf(0)>=bp, note:!t.barracks?'None here':lv>=3?'Max level':free?'Free':`${bp} ${MAT_IC}`,
        label:!t.barracks?'Barracks upgrade: no barracks on this hex':lv>=3?'Barracks: already level 3':`Upgrade the barracks to level ${nl} for ${free?'free':matTxt(bp)}`},""")
rep("""        can:canTrebAt(t)&&me.gold>=trebPrice(t), note:canTrebAt(t)?`${trebPrice(t)} gold`:t.castle?'Max 2':t.treb===1?'Building':t.treb?'Built':'Needs fort',
        label:canTrebAt(t)?`Start a trebuchet for ${trebPrice(t)} gold, ready""",
    """        can:canTrebAt(t)&&matOf(0)>=trebPrice(t), note:canTrebAt(t)?`${trebPrice(t)} ${MAT_IC}`:t.castle?'Max 2':t.treb===1?'Building':t.treb?'Built':'Needs fort',
        label:canTrebAt(t)?`Start a trebuchet for ${matTxt(trebPrice(t))}, ready""")
rep("""        can:wallSides(id).some(j=>wallOn(id,j)<WALL_HP)&&(me.gold>=wc||freeWallsLeft(0)>0), note:!wallSides(id).some(j=>wallOn(id,j)<WALL_HP)?'All walled':freeWallsLeft(0)>0?`${freeWallsLeft(0)} free`:`${wc} gold`,
        label:freeWallsLeft(0)>0?`Build walls: ${freeWallsLeft(0)} free (Reforest), then ${wc} gold each`:`Build walls, ${wc} gold each`},""",
    """        can:wallSides(id).some(j=>wallOn(id,j)<WALL_HP)&&(matOf(0)>=wc||freeWallsLeft(0)>0), note:!wallSides(id).some(j=>wallOn(id,j)<WALL_HP)?'All walled':freeWallsLeft(0)>0?`${freeWallsLeft(0)} free`:`${wc} ${MAT_IC}`,
        label:freeWallsLeft(0)>0?`Build walls: ${freeWallsLeft(0)} free (Reforest), then ${matTxt(wc)} each`:`Build walls, ${matTxt(wc)} each`},""")
# the card column: Build
rep("""      h+=`<p class="hint">${room>0?`Tap a building around the hex on the map to build it. ${room} of ${cap} spaces free.${sel.castle?' Castles take markets only.':''}`:`This hex is full (${cap} buildings). Tap another of your hexes.`} You have <b>${me.gold} gold</b>. Tap the hex again to zoom back out.</p>`;
    } else h+=`<p class="hint">Tap one of your hexes on the map to build there. You can build as much as your gold covers. You have <b>${me.gold} gold</b>.</p>`;
    h+=`<ul class="bkey">${BUILD_KINDS.concat(mammNow(0,'build')?['wh']:[]).map(k=>`<li>${BUILD_INFO[k].icon} <b>${BUILD_INFO[k].name}</b> ${costOf(k,lvl)} gold: ${buildDesc(k,0)}</li>`).join('')}</ul>`;""",
    """      h+=matRow()+`<p class="hint">${room>0?`Tap a building around the hex on the map to build it. ${room} of ${cap} spaces free.${sel.castle?' Castles take markets only.':''}`:`This hex is full (${cap} buildings). Tap another of your hexes.`} Tap the hex again to zoom back out.</p>`;
    } else h+=matRow()+`<p class="hint">Tap one of your hexes on the map to build there. Markets cost gold; everything else costs materials, which your markets sell you.</p>`;
    h+=`<ul class="bkey">${BUILD_KINDS.filter(k=>!(k==='fort'&&isDino(0))).concat(mammNow(0,'build')?['wh']:[]).map(k=>`<li>${BUILD_INFO[k].icon} <b>${BUILD_INFO[k].name}</b> ${priceTxt(k,costOf(k,lvl))}: ${buildDesc(k,0)}</li>`).join('')}</ul>`;""")
# the card column: Advancements
rep("""      h+=`<div class="row-label"><span class="px px-wall" aria-hidden="true"></span> Walls, ${freeWallsLeft(0)>0?`${freeWallsLeft(0)} free (Reforest), then `:''}${wc} gold each (you have ${me.gold})</div>""",
    """      h+=`<div class="row-label"><span class="px px-wall" aria-hidden="true"></span> Walls, ${freeWallsLeft(0)>0?`${freeWallsLeft(0)} free (Reforest), then `:''}${matTxt(wc)} each (you have ${matOf(0)})</div>${matRow()}""")
rep("""      h+=`<p class="hint">Tap an upgrade around the hex on the map. Faded ones aren't available on this hex. You have <b>${me.gold} gold</b>. Tap the hex again to zoom back out.</p>`;""",
    """      h+=matRow()+`<p class="hint">Tap an upgrade around the hex on the map. Faded ones aren't available on this hex. Tap the hex again to zoom back out.</p>`;""")
rep("""<b>Barracks upgrade</b> ${BARRACKS_UP.join(' / ')} gold: ${sel.barracks""","""<b>Barracks upgrade</b> ${BARRACKS_UP.join(' / ')} materials: ${sel.barracks""")
rep("""<b>Trebuchet</b> ${TREB_COST} gold on a fort (ready at the end of your ${lvl>=3?'turn':'next turn'}), or on a castle up to 2: ${CASTLE_TREB.join(' then ')} gold, ready in""",
    """<b>Trebuchet</b> ${matTxt(TREB_COST)} on a fort (ready at the end of your ${lvl>=3?'turn':'next turn'}), or on a castle up to 2: ${CASTLE_TREB.join(' then ')} materials, ready in""")
rep("""<b>Walls</b> ${wc} gold each: pick which sides""","""<b>Walls</b> ${matTxt(wc)} each: pick which sides""")
rep("""    } else if(isDino(0)) h+=`<p class="hint">Tap one of your hexes to upgrade a barracks <span class="px px-barracks" aria-hidden="true"></span> or hire its Alamosaurus guards (${GUARD_COST} gold each), tap your home castle to wake or stoke its volcano (${VOLC.map(v=>v.cost).join(' / ')} gold), or build walls (${wc} gold each). You have <b>${me.gold} gold</b>.</p>`;
    else h+=`<p class="hint">Tap one of your hexes to upgrade a barracks <span class="px px-barracks" aria-hidden="true"></span>, start a trebuchet on a fort <span class="px px-fort" aria-hidden="true"></span> (${TREB_COST} gold) or a castle (up to 2: ${CASTLE_TREB.join(' then ')} gold) or build walls (${wc} gold each). You have <b>${me.gold} gold</b>.</p>`;""",
    """    } else if(isDino(0)) h+=matRow()+`<p class="hint">Tap one of your hexes to upgrade a barracks <span class="px px-barracks" aria-hidden="true"></span> (materials) or hire its Alamosaurus guards (${GUARD_COST} gold each), tap your home castle to wake or stoke its volcano (${VOLC.map(v=>v.cost).join(' / ')} gold), or build walls (${matTxt(wc)} each).</p>`;
    else h+=matRow()+`<p class="hint">Tap one of your hexes to upgrade a barracks <span class="px px-barracks" aria-hidden="true"></span> (${BARRACKS_UP.join(' / ')} materials), start a trebuchet on a fort <span class="px px-fort" aria-hidden="true"></span> (${matTxt(TREB_COST)}) or a castle (up to 2: ${CASTLE_TREB.join(' then ')} materials) or build walls (${matTxt(wc)} each).</p>`;""")
# the header: materials, tap to buy more
rep("""<span class="sh-gold" title="${isMyth(0)?'Magic':'Gold'}"><span class="px px-${isMyth(0)?'magic':'coin'}" aria-hidden="true"></span> ${S.players[0].gold}</span>""",
    """<span class="sh-gold" title="${isMyth(0)?'Magic':'Gold'}"><span class="px px-${isMyth(0)?'magic':'coin'}" aria-hidden="true"></span> ${S.players[0].gold}</span>${usesMat(0)?`<button class="ghost sh-mat" data-head="trade" title="Materials: tap to buy more at your markets" aria-label="Materials: ${matOf(0)}. Buy more at your markets">${MAT_IC} ${matOf(0)}</button>`:''}""")
rep("""  else if(k==='help') showRules();""","""  else if(k==='help') showRules();
  else if(k==='trade') openTrade();""")
rep(""".sh-castles{font-family:var(--font-num);font-weight:800;white-space:nowrap}""",
    """.sh-castles{font-family:var(--font-num);font-weight:800;white-space:nowrap}
.sh-mat{font-family:var(--font-num);font-weight:800;padding:.1em .5em!important;font-size:.95em!important;color:var(--bone);white-space:nowrap}
.matrow{flex-wrap:wrap;gap:.35em;font-weight:500}
.matrow b{font-family:var(--font-num);font-weight:800}
.matrow button{margin-left:auto;padding:.25em .6em;font-size:.88em}
.trade-row{display:flex;align-items:center;gap:.6em;margin:.8em 0 .4em}
.trade-row input{flex:1;accent-color:var(--gold);height:28px}
.trade-row output{font-family:var(--font-num);font-weight:800;font-size:1.5em;min-width:2.2em;text-align:right}""")
# the trading sheet
rep("""// Every 2nd favor: pick which of the card's actions gets stronger, then the card is played""",
r"""// Buying materials at your markets: up to 3 a turn from each market (and from your home castle), 2 gold each
function openTrade(){
  if(!S||!usesMat(0)) return;
  const me=S.players[0], left=matLeft(0), max=Math.min(left,Math.floor(me.gold/MAT_PRICE)), mk=marketsOf(0), hm=homeMarket(0), mine=isHumanTurn();
  const src=[mk?`${mk} market${mk===1?'':'s'}`:'',hm?'your home castle':''].filter(Boolean).join(' and ');
  const m=$('#modal'); m.classList.remove('hidden');
  m.innerHTML=`<div class="sheet"><h3>${MAT_IC} Materials</h3>
    <p>You have <b>${matTxt(matOf(0))}</b> and <b>${me.gold} gold</b>. Materials pay for forts, barracks, barracks upgrades, walls${isDino(0)?'':' and trebuchets'}${isMamm(0)?' and Watering Holes':''}. Units and markets cost gold.</p>
    <p class="hint">Each market sells up to ${MAT_PER_MARKET} a turn, and your home castle counts as one, at ${MAT_PRICE} gold each.${src?` With ${src} you can buy <b>${matCap(0)}</b> a turn; <b>${left}</b> left this turn.`:' You have no markets and no home castle to buy from.'}</p>
    ${!mine?`<p class="hint">You can buy on your turn.</p>`:max>0?`<div class="trade-row"><button class="mvstep" data-ts="-1" aria-label="One fewer">−</button><input type="range" id="trn" min="1" max="${max}" value="${max}" aria-label="Materials to buy"><button class="mvstep" data-ts="1" aria-label="One more">+</button><output id="trv">${max}</output></div>`
      :`<p class="hint">${left<=0?'Your markets have sold all they can this turn. More markets sell more.':`You need ${MAT_PRICE} gold for each material.`}</p>`}
    <div class="btns"><button id="trc">${mine&&max>0?'Cancel':'OK'}</button>${mine&&max>0?`<button class="primary" id="trok">Buy</button>`:''}</div></div>`;
  const rng=$('#trn'), upd=()=>{ if(!rng) return; const v=+rng.value; $('#trv').textContent=v; $('#trok').textContent=`Buy ${v} for ${v*MAT_PRICE} gold`;
    m.querySelector('[data-ts="-1"]').disabled=v<=1; m.querySelector('[data-ts="1"]').disabled=v>=max; };
  if(rng){ rng.oninput=upd; m.querySelectorAll('[data-ts]').forEach(b=>b.onclick=()=>{ rng.value=Math.max(1,Math.min(max,+rng.value+(+b.dataset.ts))); upd(); }); upd();
    $('#trok').onclick=()=>{ const v=+rng.value; closeModal(); tradeBuy(v); }; }
  $('#trc').onclick=()=>{ closeModal(); render(); };
}
function tradeBuy(n){ if(!isHumanTurn()||!usesMat(0)) return; buyMat(0,n); render(); }
// Every 2nd favor: pick which of the card's actions gets stronger, then the card is played""")

# ---- the computer and materials ----
rep("""  const c=S.tiles.filter(t=>t.owner===pid&&canTrebAt(t)&&S.players[pid].gold>=trebPrice(t)&&trebSpot(t.id,pid)>0)""",
    """  const c=S.tiles.filter(t=>t.owner===pid&&canTrebAt(t)&&matReach(pid,0)>=trebPrice(t)&&trebSpot(t.id,pid)>0)""")
rep("""  if(opts&&opts.treb&&aiTrebSite(pid)==null&&S.players[pid].gold>=costOf('fort',opts.lvl)+TREB_COST){""",
    """  if(opts&&opts.treb&&aiTrebSite(pid)==null&&matReach(pid,0)>=costOf('fort',opts.lvl)+TREB_COST){""")
rep("""  if(mammNow(pid,'build')&&S.players[pid].gold>=costOf('wh',opts&&opts.lvl)+15){""",
    """  if(mammNow(pid,'build')&&matReach(pid,15)>=costOf('wh',opts&&opts.lvl)){""")
rep("""room=t=>bCount(t)<bMax(), can=k=>gold>=costOf(k,lvl);""","""room=t=>bCount(t)<bMax(), can=k=>canB(pid,k,costOf(k,lvl),opts.keep||0);""")
rep("""  if(opts.treb&&aiTrebSite(pid)==null&&gold>=costOf('fort',lvl)+TREB_COST){""",
    """  if(opts.treb&&aiTrebSite(pid)==null&&matReach(pid,opts.keep||0)>=costOf('fort',lvl)+TREB_COST){""")
rep("""  if(mammNow(pid,'build')&&!own.some(t=>t.wh)&&gold>=costOf('wh',lvl)+6){""",
    """  if(mammNow(pid,'build')&&!own.some(t=>t.wh)&&matReach(pid,(opts.keep||0)+6)>=costOf('wh',lvl)){""")
rep("""  if(gold>=costOf('fort',lvl)+12){""","""  if(matReach(pid,(opts.keep||0)+12)>=costOf('fort',lvl)){""")
rep("""    const keep=(treb&&plan.k!=='fort'&&aiTrebSite(pid)!=null)?TREB_COST:0;   // save for the trebuchet
    if(p.gold-costOf(plan.k,lvl)<keep) break;
    S.tiles[plan.id][plan.k]=(S.tiles[plan.id][plan.k]|0)+1; noteUnlock(pid,plan.k,S.tiles[plan.id]); p.gold-=costOf(plan.k,lvl); ids.push(plan.id);""",
    """    const keep=(treb&&plan.k!=='fort'&&aiTrebSite(pid)!=null)?TREB_COST:0, c=costOf(plan.k,lvl);   // save materials for the trebuchet
    if(inMat(plan.k)){ if(!aiMat(pid,c+keep,keepR)) break; spendMat(pid,c); }
    else { if(p.gold-c<goldFor(pid,keep)) break; p.gold-=c; }
    S.tiles[plan.id][plan.k]=(S.tiles[plan.id][plan.k]|0)+1; noteUnlock(pid,plan.k,S.tiles[plan.id]); ids.push(plan.id);""")
rep("""      let c=0; const plan=aiBuildPlan2(pid,{lvl:buildLvl}); if(plan){ c=costOf(plan.k,buildLvl); if(S.turn<=14&&p.gold>=2*c+6) c*=2; }
      if(plan&&p.gold>=c+3) keep=c;
    } else { const plan=aiBuildPlan(pid), c=plan?costOf(plan.k,buildLvl):0; if(plan&&p.gold>=c+3) keep=c; }
  }
  if(later.includes('advance')&&aiTrebSite(pid)!=null&&p.gold>=TREB_COST+3) keep=Math.max(keep,TREB_COST);""",
    """      const gNeed=pl=>inMat(pl.k)?goldFor(pid,costOf(pl.k,buildLvl)):costOf(pl.k,buildLvl);   // in gold: materials still to buy
      let c=0; const plan=aiBuildPlan2(pid,{lvl:buildLvl}); if(plan){ c=gNeed(plan); if(S.turn<=14&&p.gold>=2*c+6) c*=2; }
      if(plan&&p.gold>=c+3) keep=c;
    } else { const plan=aiBuildPlan(pid), c=plan?(inMat(plan.k)?goldFor(pid,costOf(plan.k,buildLvl)):costOf(plan.k,buildLvl)):0; if(plan&&p.gold>=c+3) keep=c; }
  }
  if(later.includes('advance')&&aiTrebSite(pid)!=null){ const tg=goldFor(pid,TREB_COST); if(p.gold>=tg+3) keep=Math.max(keep,tg); }""")
rep("""  const ts=aiTrebSite(pid); if(ts!=null&&doStartTreb(pid,ts,lvl)) ids.push(ts);""",
    """  const ts=aiTrebSite(pid); if(ts!=null&&aiMat(pid,trebPrice(S.tiles[ts]))&&doStartTreb(pid,ts,lvl)) ids.push(ts);""")
rep("""    if(!best||!doBuildWall(pid,best[0],best[1],lvl)) break;""","""    if(!best||!(free||aiMat(pid,wallCost(lvl)))||!doBuildWall(pid,best[0],best[1],lvl)) break;""")
rep("""  for(const t of bks) while((t.bk||0)<3&&p.gold>=BARRACKS_UP[t.bk||0]+spare[t.bk||0]&&doUpgradeBarracks(pid,t.id,lvl)) ids.push(t.id);
  if(!ids.length&&aiSmart(pid)&&p.gold>=wallCost(lvl)+8){""",
    """  for(const t of bks) while((t.bk||0)<3&&aiMat(pid,BARRACKS_UP[t.bk||0],spare[t.bk||0])&&doUpgradeBarracks(pid,t.id,lvl)) ids.push(t.id);
  if(!ids.length&&aiSmart(pid)&&matReach(pid,8)>=wallCost(lvl)){""")
rep("""      if(side!=null&&doBuildWall(pid,h.id,side,lvl)) ids.push(h.id); }""","""      if(side!=null&&aiMat(pid,wallCost(lvl),8)&&doBuildWall(pid,h.id,side,lvl)) ids.push(h.id); }""")
rep("""  const g=S.players[pid].gold*(isMyth(pid)?MAGIC_VAL:1); V+=aiSmart(pid)?0.9*Math.min(g,40)+0.4*Math.max(0,g-40):0.9*g;""",
    """  const g=S.players[pid].gold*(isMyth(pid)?MAGIC_VAL:1); V+=aiSmart(pid)?0.9*Math.min(g,40)+0.4*Math.max(0,g-40):0.9*g;
  V+=1.6*matOf(pid);   // materials in store: a little under the 2 gold they cost""")

# ---- How to play ----
rep("""(one per hex, ${TREB_COST} gold, finished at the end of your next turn) or on a castle (up to 2 per castle, ${CASTLE_TREB[0]} gold for the first and ${CASTLE_TREB[1]} for the second,""",
    """(one per hex, ${matTxt(TREB_COST)}, finished at the end of your next turn) or on a castle (up to 2 per castle, ${matTxt(CASTLE_TREB[0])} for the first and ${CASTLE_TREB[1]} for the second,""")
rep("""barracksLv(0).map((d,i)=>`level ${i+1} (${BARRACKS_UP[i]} gold) ${d.charAt(0)""","""barracksLv(0).map((d,i)=>`level ${i+1} (${matTxt(BARRACKS_UP[i])}) ${d.charAt(0)""")
rep("""`level 1 (${BARRACKS_UP[0]} gold) unlocks the ${UNITS[S.players[0].faction].barracks[2][2]}; level 2 (${BARRACKS_UP[1]} gold)""",
    """`level 1 (${matTxt(BARRACKS_UP[0])}) unlocks the ${UNITS[S.players[0].faction].barracks[2][2]}; level 2 (${matTxt(BARRACKS_UP[1])})""")
i=s.index("level 2 (${matTxt(BARRACKS_UP[1])})")
j=s.index("(${BARRACKS_UP[2]} gold)",i)
s=s[:j]+"(${matTxt(BARRACKS_UP[2])})"+s[j+len("(${BARRACKS_UP[2]} gold)"):]
rep("""    <li><b>Gold.</b> At the start of every turn you collect +${m.castleGold} per castle, +1 per 2 hexes you own, and +${m.marketGold} per <span class="px px-market" aria-hidden="true"></span> Market. Harvest adds more on top.</li>""",
    """    <li><b>Gold.</b> At the start of every turn you collect +${m.castleGold} per castle, +1 per 2 hexes you own, and +${m.marketGold} per <span class="px px-market" aria-hidden="true"></span> Market. Harvest adds more on top. Gold pays for units, markets${isDino(0)?', Alamosaurus guards and the volcano':''}.</li>
    <li${isMyth(0)?' hidden':''}><b>${MAT_IC} Materials.</b> Forts, barracks, barracks upgrades, walls${isDino(0)?'':' and trebuchets'} cost materials, not gold. Your markets sell them: each <span class="px px-market" aria-hidden="true"></span> Market sells up to ${MAT_PER_MARKET} a turn and your home castle counts as one, at ${MAT_PRICE} gold each, any time on your turn. Tap ${MAT_IC} at the top of the cards, or <b>Buy materials</b> during Build and Advancements. What you don't use keeps.</li>
    <li><b><span class="px px-fortify" aria-hidden="true"></span> Fortify</b> is a wild card. First you regroup: move your units any distance between your own hexes, as often as you like (no attacks or claiming), and they can still move again later in the turn. Then pick one of Build, Advancements and Recruit (two once Fortify is upgraded twice, all three at three upgrades). Each plays like the basic action.${hasNamed(0)?` Its first upgrade is the ${f.name}' ${namedUp(0).fortify.name}, which happens first.`:''}</li>""")
rep("""<b>Buildings.</b> <span class="px px-market" aria-hidden="true"></span> Markets for income, """,
    """<b>Buildings.</b> <span class="px px-market" aria-hidden="true"></span> Markets for income and materials, """)
# Battles: fortified units no longer add to the luck roll
n0=s.count(" and fortified units (+${m.fortifyBonus})")
if n0==1: s=s.replace(" and fortified units (+${m.fortifyBonus})","")
else: print('note: fortified-units text count',n0)

# ---- the faction screen ----
rep("""    <p>Each turn you hold 3 of these and play one, carrying out its actions in order. Every 2nd time you play a card, you upgrade one of its actions.</p>""",
    """    <p>Each turn you hold 3 of these and play one, carrying out its actions in order. Every 2nd time you play a card, you upgrade one of its actions.</p>
    <p>${{dinos:'The Dinosaurs lean on <b>Fortify</b> and <b>Harvest</b>.',robots:'The Robots lean on <b>Move</b> and <b>Advancements</b>.',mammals:'The Mammals lean on <b>Harvest</b> and <b>Recruit</b>.'}[fid]||''} <b>Fortify</b> is a wild card: regroup your army inside your land, then Build, Advancements or Recruit.</p>
    <h3>Gold and materials</h3>
    <p>Gold pays for units and markets. Forts, barracks, upgrades, walls and trebuchets cost <b>materials</b>, which your markets sell you: up to ${MAT_PER_MARKET} a turn from each market and from your home castle, ${MAT_PRICE} gold each.</p>""")
rep("""    <h3>Your cards</h3>
    <ul>${f.cards.map(c=>`<li><b>${c.name}</b>: ${c.actions.map(a=>ACTIONS[a].icon+' '+actName(a,fid)).join(' → ')}</li>`).join('')}</ul>
    <p>Channeling has no other actions""",
    """    <h3>Your cards</h3>
    <ul>${f.cards.map(c=>`<li><b>${c.name}</b>: ${c.actions.map(a=>ACTIONS[a].icon+' '+actName(a,fid)).join(' → ')}</li>`).join('')}</ul>
    <p>The Mythical lean on <b>Advancements</b> and <b>Fortify</b>. Fortify is a wild card: regroup your army inside your land, then Build, Advancements or Recruit.</p>
    <p>Channeling has no other actions""")

open(P+'cc.html','w',encoding='utf-8').write(s)
print('ok')

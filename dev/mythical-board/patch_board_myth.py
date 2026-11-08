"""The Mythical faction on the Crown & Coin board (Ethan's rules, 2026-11-07). Works on the board code of index.html
(everything outside the built-in arena string). Usage: patch_board_myth.py BOARD_IN BOARD_OUT EDITS_JSON ART_JSON"""
import sys, json
s=open(sys.argv[1]).read(); edits=[]; ART=json.load(open(sys.argv[4]))
def rep(old,new,count=1):
    global s
    assert s.count(old)==count,(s.count(old),old[:90]); s=s.replace(old,new); edits.append({'old_text':old,'new_text':new,'count':count})

# ---------- art ----------
myart={'castle':ART['castle'],'castle_ratio':ART['castle_ratio'],'tree':ART['tree'],'magic':ART['magic'],'dome':ART['dome'],
       'units':{'minion':ART['u_minion'],'mage':ART['u_mage'],'minotaur':ART['u_minotaur'],'griffin':ART['u_griffin'],'dragon':ART['u_dragon']}}
rep("ART.castle_mammals=MAMMAL_ART.castle; Object.assign(ART.bld,MAMMAL_ART.bld); ART.icons.wh=MAMMAL_ART.icon_wh;",
    "ART.castle_mammals=MAMMAL_ART.castle; Object.assign(ART.bld,MAMMAL_ART.bld); ART.icons.wh=MAMMAL_ART.icon_wh;\n"
    "// the Mythical: Ethan's Floating Castle and Life Tree (OpenArt), his unit pictures, and Claude's stand-in magic crystal and dome icons\n"
    "/*MYTH_ART*/const MYTH_ART="+json.dumps(myart)+";\n"
    "ART.castle_mythical={uri:MYTH_ART.castle,ratio:MYTH_ART.castle_ratio}; ART.bld.tree=MYTH_ART.tree; ART.icons.magic=MYTH_ART.magic; ART.icons.dome=MYTH_ART.dome;")
rep("const SMOOTH_BLD=k=>/_mammals$|^wh$/.test(k);", "const SMOOTH_BLD=k=>/_mammals$|^wh$|^tree$/.test(k);")
rep("for(const f of ['dinos','robots','mammals','neutral'])", "for(const f of ['dinos','robots','mammals','mythical','neutral'])", 2)
rep("const SMOOTH_IC=['move','harvest','recruit','build','fortify','advance','coin'];", "const SMOOTH_IC=['move','harvest','recruit','build','fortify','advance','coin','magic','dome'];")
rep(".px-coin{image-rendering:auto}   /* the coin is smooth art too */",
    ".px-coin{image-rendering:auto}   /* the coin is smooth art too */\n"
    "/* the Mythical's choices in the card column (recruit, plant, upgrade, dome) */\n"
    ".mygrid{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin:.4em 0}\n"
    ".mybtn{display:flex;flex-direction:column;align-items:flex-start;gap:1px;text-align:left;padding:6px 9px;min-height:44px;line-height:1.15}\n"
    ".mybtn small{opacity:.8;font-size:.82em;font-weight:500}\n"
    ".mybtn[disabled]{opacity:.45}")

# ---------- the faction ----------
rep("""      {id:'tusks', name:'Tusks and Thorns', actions:['advance','fortify','move']},
    ],
  },
};""","""      {id:'tusks', name:'Tusks and Thorns', actions:['advance','fortify','move']},
    ],
  },
  mythical:{
    name:'Mythical', emblem:'<span class="px px-c-mythical" aria-hidden="true"></span>', color:'#8b55d6', ink:'#c8a6ff', tagline:'Mages, magic and monsters',
    mods:{},
    cards:[   // Ethan's Mythical cards (2026-11-07); the names are Claude's placeholders
      {id:'march', name:'March of Minions', actions:['move','build','recruit']},
      {id:'gather',name:'Gathering',        actions:['harvest','recruit','move']},
      {id:'grove', name:'The Grove',        actions:['harvest','advance','fortify']},
      {id:'arcan', name:'Arcanum',          actions:['build','advance','recruit']},
      {id:'chan',  name:'Channeling',       actions:['channel']},
    ],
  },
};""")
rep("const FACTION_ORDER=['dinos','robots','mammals'];", "const FACTION_ORDER=['dinos','robots','mammals','mythical'];")
rep("const FAC_COLOR={dinos:'blue',robots:'red',mammals:'green'};", "const FAC_COLOR={dinos:'blue',robots:'red',mammals:'green',mythical:'purple'};")
rep("""  advance:{icon:'<span class="px px-advance" aria-hidden="true"></span>',name:'Advancements'},
};""","""  advance:{icon:'<span class="px px-advance" aria-hidden="true"></span>',name:'Advancements'},
  channel:{icon:'<span class="px px-magic" aria-hidden="true"></span>',name:'Channel',instant:true},   // the Mythical's special card
};""")
rep("function actionDesc(a,pid,lvl){\n", "function actionDesc(a,pid,lvl){\n  if(isMyth(pid)&&a!=='fortify') return mythActionDesc(a,pid);\n")
rep("const upgradeDue=(pid,cid)=>(favorOf", "const upgradeDue=(pid,cid)=>!isMyth(pid)&&(favorOf")   # Mythical cards don't upgrade yet
rep("const movesLimit=pid=>modsOf(pid).movesPerAction+(mammNow(pid,'move')?1:0);", "const movesLimit=pid=>modsOf(pid).movesPerAction+(mammNow(pid,'move')?1:0)+(isMyth(pid)?1:0);   // the Mythical: 3 moves")

# ---------- the Mythical's own rules ----------
MYTH_JS=r"""
// ---------- Mythical (Ethan's rules, 2026-11-07) ----------
// The Mythical earn and spend only magic (kept in the player's gold field and shown as magic). Magic comes from Life Trees and
// the Floating Castle (their home castle). Mages are moving barracks: on the hex they stand on they turn Minions into bigger
// units, plant Life Trees and raise magic domes. Mages and Minions are made at castles. Captured enemy buildings do nothing
// for them. Unit prices and the Mage's base price are placeholders until Ethan sets them.
const MYTH={startMagic:5, castleMagic:[10,15,20,25], castleUp:[10,15,20], minions:[5,7,9,11], mageUp:[7,9,12], mageBase:4,
  treeMagic:3, treeRich:5, treeMinions:5, treeTurns:2, domeCost:1, domeUpkeep:1, chMage:2, chCastle:5, minionPack:3, secondMagic:3, guards:1};
const MAGIC_VAL=3;                                  // the computer's rough worth of 1 magic, in gold
const MAGES=['mage0','mage1','mage2','mage3'];      // a Mage keeps the level it was made at
const isMage=k=>MAGES.includes(k);
const MYTH_CONV={minotaur:{m:7,min:1,lv:0},griffin:{m:10,min:2,lv:1},dragon:{m:15,min:4,lv:2}};   // magic, Minions used up, Mage level needed
const MAGE_LV_NOTE=['Griffins, longer lightning, +1 damage','Dragons, longer lightning, +1 damage','units 1 magic cheaper, longer lightning, 3 Mages a hex'];
const isMyth=pid=>!!(S&&S.players&&S.players[pid]&&S.players[pid].faction==='mythical');
const cur$=pid=>isMyth(pid)?'magic':'gold';
const poss=pid=>pid===0?'Your':`The ${S.players[pid].name}'`;
const mlvOf=pid=>(S.players[pid]&&S.players[pid].mlv)||0, clvOf=pid=>(S.players[pid]&&S.players[pid].clv)||0;
const magesOn=t=>MAGES.reduce((s,k)=>s+((t.army&&t.army[k])||0),0);
const mageCap=pid=>mlvOf(pid)>=3?3:2;              // Mages on one hex at a time
const mageLvAt=t=>{ for(let l=3;l>=0;l--) if(t.army&&t.army[MAGES[l]]>0) return l; return -1; };   // the best Mage on the hex
const mageTotal=pid=>S.tiles.reduce((s,t)=>s+(t.owner===pid?magesOn(t):0),0);
// a new Mage: the base price, +1 for each Mage past the 5th, +1 for each level, and level 3 takes 1 off every unit
const magePrice=pid=>MYTH.mageBase+Math.max(0,mageTotal(pid)-4)+mlvOf(pid)-(mlvOf(pid)>=3?1:0);
const convPrice=(t,k)=>MYTH_CONV[k].m-(mageLvAt(t)>=3?1:0);
const mythHome=pid=>{ const h=S.tiles[S.homes[pid]]; return h&&h.owner===pid?h:null; };
const isFloating=t=>!!t.castle&&t.owner>=0&&S.homes[t.owner]===t.id&&isMyth(t.owner);
const treeMagic=t=>((t.army&&t.army.minion)||0)>=MYTH.treeMinions?MYTH.treeRich:MYTH.treeMagic;
const fastUnit=k=>k==='minion'||isMage(k);         // Mages and Minions move 2 hexes anywhere
function mythIncome(pid){
  let tiles=0,castles=0,trees=0,treeM=0;
  S.tiles.forEach(t=>{ if(t.owner!==pid) return; tiles++; if(t.castle) castles++; if(t.tree){ trees++; treeM+=treeMagic(t); } });
  const home=mythHome(pid)?MYTH.castleMagic[clvOf(pid)]:0;
  return {tiles,castles,markets:0,land:0,nest:0,trees,treeM,home,total:home+treeM};
}
function lockMage(t){ for(const k of MAGES) if(t.ready&&t.ready[k]>0){ t.ready[k]--; syncT(t); return true; } return false; }
// the start of a Mythical turn (after income): dome upkeep, the Floating Castle's Minions, Mages rooted to new trees
function mythTurnStart(p){
  const pid=p.id, domes=S.tiles.filter(t=>t.owner===pid&&t.dome>0);
  let kept=0; for(const t of domes){ if(p.gold>=MYTH.domeUpkeep){ p.gold-=MYTH.domeUpkeep; kept++; } else t.dome=0; }
  if(domes.length) addLog(kept===domes.length?`${p.name} pay ${kept} magic to keep ${kept===1?'a dome':kept+' domes'} up.`:`${p.name} can't pay for every dome: ${domes.length-kept} fade${domes.length-kept===1?'s':''} away.`,pid);
  const h=mythHome(pid); if(h){ const n=MYTH.minions[clvOf(pid)]; addUnits(h,'minion',n,true); addLog(`The Floating Castle makes ${n} Minions.`,pid); }
  S.tiles.forEach(t=>{ if(t.owner===pid&&t.root>0){ lockMage(t); t.root--; } });
}
function mythSetup(p,i){
  p.gold=MYTH.startMagic+(i===1?MYTH.secondMagic:0); p.mlv=0; p.clv=0;
  addUnits(S.tiles[HOMES[i]],'mage0',1,true); addUnits(S.tiles[HOMES[i]],'minion',4,true);
}
// the special card: no actions, but every Mage makes 2 magic and every castle 5
function mythChannel(pid){
  const p=S.players[pid], mg=mageTotal(pid), cs=castleCount(pid), g=mg*MYTH.chMage+cs*MYTH.chCastle; p.gold+=g;
  addLog(`${p.name} channel magic: +${g} (${mg} Mage${mg===1?'':'s'}, ${cs} castle${cs===1?'':'s'}).`,pid);
  return `${ACTIONS.channel.icon} Channel: +${g} magic (${MYTH.chMage} from each of ${mg} Mage${mg===1?'':'s'}, ${MYTH.chCastle} from each of ${cs} castle${cs===1?'':'s'})`;
}
function mythBuyMinions(pid,id,packs){ const t=S.tiles[id], p=S.players[pid]; packs=Math.min(packs|0,p.gold);
  if(t.owner!==pid||!t.castle||packs<1) return false;
  p.gold-=packs; addUnits(t,'minion',packs*MYTH.minionPack,true); addLog(`${p.name} make ${packs*MYTH.minionPack} Minions.`,pid); return true; }
function mythBuyMage(pid,id){ const t=S.tiles[id], p=S.players[pid], c=magePrice(pid);
  if(t.owner!==pid||!t.castle||magesOn(t)>=mageCap(pid)||p.gold<c) return false;
  p.gold-=c; addUnits(t,MAGES[mlvOf(pid)],1,true); addLog(`${p.name} make a level ${mlvOf(pid)} Mage.`,pid); return true; }
function mythConvert(pid,id,k){ const t=S.tiles[id], p=S.players[pid], C=MYTH_CONV[k];
  if(!C||t.owner!==pid||mageLvAt(t)<C.lv||((t.army&&t.army.minion)||0)<C.min) return false;
  const c=convPrice(t,k); if(p.gold<c) return false;
  p.gold-=c; takeUnits(t,{minion:C.min}); addUnits(t,k,1,true);
  addLog(`${poss(pid)} Mage turns ${C.min===1?'a Minion':C.min+' Minions'} into a ${UNIT_STATS[k].name}.`,pid); return true; }
function mythPlant(pid,id){ const t=S.tiles[id];
  if(t.owner!==pid||t.tree||t.castle||t.terrain!=='plain'||!MAGES.some(k=>t.ready&&t.ready[k]>0)) return false;
  t.tree=1; t.root=MYTH.treeTurns; lockMage(t);
  addLog(`${poss(pid)} Mage plants a Life Tree and stays with it for ${MYTH.treeTurns} turns.`,pid); return true; }
function mythDome(pid,id){ const t=S.tiles[id], p=S.players[pid];
  if(t.owner!==pid||t.dome>0||!magesOn(t)||t.terrain==='water'||p.gold<MYTH.domeCost) return false;
  p.gold-=MYTH.domeCost; t.dome=WALL_HP; addLog(`${poss(pid)} Mage raises a magic dome.`,pid); return true; }
function mythUpMages(pid){ const p=S.players[pid], l=mlvOf(pid);
  if(l>=3||!mythHome(pid)||p.gold<MYTH.mageUp[l]) return false;
  p.gold-=MYTH.mageUp[l]; p.mlv=l+1; addLog(`${p.name} raise their Mages to level ${l+1}: new Mages come out at that level.`,pid); return true; }
function mythUpCastle(pid){ const p=S.players[pid], l=clvOf(pid);
  if(l>=3||!mythHome(pid)||p.gold<MYTH.castleUp[l]) return false;
  p.gold-=MYTH.castleUp[l]; p.clv=l+1; addLog(`${p.name} raise the Floating Castle to level ${l+1}: ${MYTH.castleMagic[l+1]} magic and ${MYTH.minions[l+1]} Minions a turn.`,pid); return true; }
// moves: only flyers can attack the Floating Castle; Mages and Minions also reach 2 hexes away into new land or an attack
function moveFilter(from,to,lvl){
  const A=S.tiles[from], B=S.tiles[to], pid=A.owner;
  const air=B.owner>=0&&B.owner!==pid&&isFloating(B), far=isMyth(pid)&&!moveTargetsCore(from,lvl||0,false).includes(to);
  if(air&&far) return ()=>false;
  if(air) return k=>!!UNIT_STATS[k].air;
  if(far) return fastUnit;
  return null;
}
function moveFilterNote(from,to){ const B=S.tiles[to];
  return B.owner>=0&&B.owner!==S.tiles[from].owner&&isFloating(B)?'<br>The Floating Castle can only be attacked by flyers.':'<br>Only Mages and Minions can go this far in one move.'; }
// a hex holds at most 2 Mages (3 once Mages reach level 3): the extra ones stay behind
function mageTrim(A,B,sel){
  if(!isMyth(A.owner)) return; const room=mageCap(A.owner)-(B.owner===A.owner?magesOn(B):0);
  let n=0; for(const k of MAGES.slice().reverse()) if(sel[k]){ const m=Math.max(0,Math.min(sel[k],room-n)); n+=m; if(m) sel[k]=m; else delete sel[k]; }
}
const domeSvg=(cx,cy,hp)=>`<circle cx="${cx.toFixed(2)}" cy="${cy.toFixed(2)}" r="${(HR-2.4).toFixed(2)}" fill="#b48cff" fill-opacity="${(.08+.05*hp).toFixed(2)}" stroke="#e2d0ff" stroke-width="${(.45+.35*hp).toFixed(2)}" stroke-opacity=".9"/><path d="M${(cx-9).toFixed(2)},${(cy-8).toFixed(2)} q5,-6 12,-3" fill="none" stroke="#fff" stroke-width="1" stroke-opacity=".55" stroke-linecap="round"/>`;
function mythActionDesc(a,pid){
  if(a==='harvest') return `+${modsOf(pid).harvestBase} magic, plus 1 for every 2 hexes you own (on top of your Life Trees and castle)`;
  if(a==='recruit') return `At your castles: Minions (${MYTH.minionPack} for 1 magic) and Mages (${magePrice(pid)} magic, at most ${mageCap(pid)} on a hex). Where a Mage stands: turn Minions into Minotaurs, Griffins and Dragons`;
  if(a==='build') return `Plant Life Trees: a ready Mage stays on its hex for ${MYTH.treeTurns} turns; the tree makes ${MYTH.treeMagic} magic a turn (${MYTH.treeRich} with ${MYTH.treeMinions}+ Minions there)`;
  if(a==='move') return `Make up to ${movesLimit(pid)} moves. Mages and Minions go up to 2 hexes anywhere; other units 1 hex into new land or an attack, or 2 through your own land. Only flyers can attack a Floating Castle`;
  if(a==='advance') return `Upgrade your Mages (${MYTH.mageUp.join(', ')} magic for levels 1 to 3) or the Floating Castle (${MYTH.castleUp.join(', ')} magic), or raise a magic dome where a Mage stands (${MYTH.domeCost} magic, then ${MYTH.domeUpkeep} a turn)`;
  if(a==='channel') return `No other actions this turn: +${MYTH.chMage} magic for every Mage you have and +${MYTH.chCastle} for every castle you hold`;
  return actionDescBase(a,pid,0);
}
// the human's Mythical actions, from the buttons in the card column
function mythAct(op,k){
  if(!S.play||!isHumanTurn()) return; const a=curAction(), id=ui.sel;
  if(op==='upm'&&a==='advance') mythUpMages(0);
  else if(op==='upc'&&a==='advance') mythUpCastle(0);
  else if(id==null) return;
  else if(op==='min'&&a==='recruit') mythBuyMinions(0,id,+k);
  else if(op==='minall'&&a==='recruit') mythBuyMinions(0,id,S.players[0].gold);
  else if(op==='mage'&&a==='recruit') mythBuyMage(0,id);
  else if(op==='conv'&&a==='recruit') mythConvert(0,id,k);
  else if(op==='tree'&&a==='build') mythPlant(0,id);
  else if(op==='dome'&&a==='advance') mythDome(0,id);
  render();
}
// the card column during a Mythical Recruit, Build or Advancements: what's possible, with the buttons round the tapped hex
function mythStepBody(a,sel){
  const me=S.players[0], mine=!!sel&&sel.owner===0;
  let h=`<div class="row-label"><span class="px px-magic" aria-hidden="true"></span> You have <b>${me.gold} magic</b></div>`;
  if(mine&&sel.troops) h+=`<div class="harmy">Here: ${armyList(sel.army)}</div>`;
  if(a==='recruit') return h+`<p class="hint">Tap one of your castles to make Minions (${MYTH.minionPack} for 1 magic) or a Mage (${magePrice(0)} magic, at most ${mageCap(0)} on a hex). Tap a hex with a Mage to turn its Minions into Minotaurs (${MYTH_CONV.minotaur.m} magic + 1), Griffins (${MYTH_CONV.griffin.m} + 2, level 1 Mage) and Dragons (${MYTH_CONV.dragon.m} + 4, level 2 Mage).</p>`;
  if(a==='build') return h+`<p class="hint">Tap a hex where one of your Mages is ready to plant a Life Tree. It costs no magic, but that Mage can't move for ${MYTH.treeTurns} whole turns. A tree makes ${MYTH.treeMagic} magic a turn, or ${MYTH.treeRich} with ${MYTH.treeMinions} or more Minions on its hex. One per hex, not on castles; it's destroyed if the hex is captured.</p>`;
  return h+`<p class="hint">Tap any of your hexes to upgrade your Mages (${MYTH.mageUp.join(', ')} magic) or the Floating Castle (${MYTH.castleUp.join(', ')} magic), or to raise a magic dome where a Mage stands: ${MYTH.domeCost} magic, then ${MYTH.domeUpkeep} every turn (if you can't pay, it fades). A dome guards every side like a full wall.</p>`;
}
// the round buttons on posts round the zoomed-in hex, like the other factions' Recruit, Build and Advancements buttons
function mythBubbleItems(t){
  const me=S.players[0], a=_zoomMode, out=[];
  const it=(op,k,img,name,note,ok,o)=>out.push(Object.assign({op,k,img,name,note,ok},o||{}));
  if(a==='recruit'){
    if(t.castle){ const tc=1, all=me.gold, cap=mageCap(0), mo=magesOn(t), mp=magePrice(0);
      it('min',1,UNIT_ART.minion,`+${MYTH.minionPack}`,'1 magic',me.gold>=1,{big:true,label:`Make ${MYTH.minionPack} Minions for 1 magic`});
      it('min',5,UNIT_ART.minion,`+${5*MYTH.minionPack}`,'5 magic',me.gold>=5,{big:true,label:`Make ${5*MYTH.minionPack} Minions for 5 magic`});
      it('minall',0,UNIT_ART.minion,'All',`+${all*MYTH.minionPack} · ${all}`,all>=1,{big:true,label:`Make ${all*MYTH.minionPack} Minions for all ${all} magic`});
      it('mage',0,UNIT_ART.mage0,`Mage ${mlvOf(0)}`,mo>=cap?`${cap} here`:`${mp} magic`,mo<cap&&me.gold>=mp,{label:mo>=cap?`This hex already has ${cap} Mages`:`Make a level ${mlvOf(0)} Mage for ${mp} magic`}); }
    const ml=mageLvAt(t), mn=(t.army&&t.army.minion)||0;
    if(ml>=0) for(const k of Object.keys(MYTH_CONV)){ const C=MYTH_CONV[k], c=convPrice(t,k), lock=ml<C.lv;
      it('conv',k,UNIT_ART[k],UNIT_STATS[k].name,lock?`Mage ${C.lv}`:`${c}+${C.min}`,!lock&&mn>=C.min&&me.gold>=c,
        {label:lock?`${UNIT_STATS[k].name}: needs a level ${C.lv} Mage here`:`Turn ${C.min===1?'a Minion':C.min+' Minions'} into a ${UNIT_STATS[k].name} for ${c} magic`}); }
  } else if(a==='build'){
    const ok=!t.tree&&!t.castle&&t.terrain==='plain'&&MAGES.some(k=>t.ready&&t.ready[k]>0);
    it('tree',0,ART.bld.tree,'Life Tree',t.tree?'Has one':t.castle?'Not here':!magesOn(t)?'Needs Mage':ok?`Free · ${MYTH.treeTurns} turns`:'Mage busy',ok,
      {sm:true,label:ok?`Plant a Life Tree: this hex's Mage stays ${MYTH.treeTurns} turns`:'A Life Tree needs a ready Mage on a plain hex without one'});
  } else if(a==='advance'){
    const ml=mlvOf(0), cl=clvOf(0), home=!!mythHome(0), dok=!(t.dome>0)&&magesOn(t)>0&&me.gold>=MYTH.domeCost;
    it('upm',0,UNIT_ART.mage0,ml>=3?'Mages 3':`Mages ${ml+1}`,ml>=3?'Max level':!home?'No castle':`${MYTH.mageUp[ml]} magic`,ml<3&&home&&me.gold>=MYTH.mageUp[ml],
      {label:ml>=3?'Mages are at the top level':`Raise new Mages to level ${ml+1} for ${MYTH.mageUp[ml]} magic: ${MAGE_LV_NOTE[ml]}`});
    it('dome',0,ART.icons.dome,'Dome',t.dome>0?`Up ${t.dome}/${WALL_HP}`:!magesOn(t)?'Needs Mage':`${MYTH.domeCost}, ${MYTH.domeUpkeep}/turn`,dok,
      {sm:true,label:t.dome>0?'This hex already has a dome':`Raise a magic dome over this hex: ${MYTH.domeCost} magic, then ${MYTH.domeUpkeep} a turn`});
    it('upc',0,MYTH_ART.castle,cl>=3?'Castle 3':`Castle ${cl+1}`,cl>=3?'Max level':!home?'No castle':`${MYTH.castleUp[cl]} magic`,cl<3&&home&&me.gold>=MYTH.castleUp[cl],
      {sm:true,label:cl>=3?'The Floating Castle is at the top level':`Raise the Floating Castle to level ${cl+1} for ${MYTH.castleUp[cl]} magic: ${MYTH.castleMagic[cl+1]} magic and ${MYTH.minions[cl+1]} Minions a turn`});
  }
  return out;
}
const MYTH_RING={1:[90],2:[120,60],3:[150,90,30],4:[150,90,30,270],5:[150,90,30,225,315],6:[150,90,30,210,330,270],7:[150,90,30,200,250,290,340]};
function mythBubbles(P,cx,cy,k,R,stem){
  const items=mythBubbleItems(S.tiles[_zoomHex]); let lines='', html='';
  const [hcx,hcy]=P(cx,cy), hr=HR*k, r=items.length>3?Math.min(R,(hr*.95+stem)/1.75):R, ring=hr*.95+stem+r, fsz=(r/R).toFixed(3);
  const rpost=deg=>{ const a=deg*Math.PI/180, ux=Math.cos(a), uy=-Math.sin(a), nx=-uy*r*.2, ny=ux*r*.2, r0=hr*.86;
    for(const sg of [-1,1]){ const x1=(hcx+ux*r0+sg*nx).toFixed(1), y1=(hcy+uy*r0+sg*ny).toFixed(1), x2=(hcx+ux*(ring-r+4)+sg*nx).toFixed(1), y2=(hcy+uy*(ring-r+4)+sg*ny).toFixed(1);
      lines+=`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#060907" stroke-width="4.5" stroke-linecap="round"/><line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#ece4cf" stroke-width="2"/>`; }
    return `style="left:${(hcx+ux*ring).toFixed(1)}px;top:${(hcy+uy*ring).toFixed(1)}px;width:${(2*r).toFixed(1)}px;height:${(2*r).toFixed(1)}px;font-size:calc(.78em * ${fsz})"`; };
  const degs=MYTH_RING[Math.min(7,items.length)]||[];
  items.slice(0,7).forEach((o,i)=>{
    html+=`<button class="bub unit${o.big?' rec':''}${o.ok?'':' off'}" data-my="${o.op}" data-k="${o.k}" ${rpost(degs[i])} ${o.ok?'':'disabled'} aria-label="${o.label||o.name}"><img src="${o.img}" alt=""${o.sm?' class="sm"':''}><b${o.big?' class="big"':o.name.length>11?' class="lng"':''}>${o.name}</b><small>${o.note}</small></button>`; });
  return {lines,html};
}
// the computer's Mythical Recruit, Build and Advancements
function mythAi(pid,a,later){
  const p=S.players[pid], ids=[], own=S.tiles.filter(t=>t.owner===pid), eid=1-pid;
  const dE=bfs(S.tiles.filter(t=>t.owner===eid).map(t=>t.id)), dist=t=>fin(dE[t.id]);
  if(a==='advance'){
    if(clvOf(pid)<3&&p.gold>=MYTH.castleUp[clvOf(pid)]+2&&mythUpCastle(pid)) ids.push(S.homes[pid]);   // pays for itself in 2 to 4 turns
    while(mlvOf(pid)<3&&p.gold>=MYTH.mageUp[mlvOf(pid)]+3&&mythUpMages(pid)) ids.push(S.homes[pid]);
    own.filter(t=>magesOn(t)&&!(t.dome>0)&&enemyNear(t.id,pid,1)>=2).sort((x,y)=>enemyNear(y.id,pid,1)-enemyNear(x.id,pid,1)).slice(0,2)
      .forEach(t=>{ if(p.gold>=MYTH.domeCost+3&&mythDome(pid,t.id)) ids.push(t.id); });
    return ids;
  }
  if(a==='build'){
    own.filter(t=>!t.tree&&!t.castle&&t.terrain==='plain'&&MAGES.some(k=>t.ready&&t.ready[k]>0)&&dist(t)>=1).sort((x,y)=>dist(y)-dist(x))
      .forEach(t=>{ if(mythPlant(pid,t.id)) ids.push(t.id); });
    return ids;
  }
  // Recruit: Mages first (about one for every 4 hexes held), then the best units the Mages allow, then Minions with some magic kept back
  const keep=(later||[]).includes('advance')?Math.min(p.gold>>1,clvOf(pid)<3?MYTH.castleUp[clvOf(pid)]:MYTH.mageUp[Math.min(2,mlvOf(pid))]):0;
  const want=Math.max(2,Math.ceil(own.length/4)), castles=own.filter(t=>t.castle).sort((x,y)=>dist(x)-dist(y));
  for(const t of castles) while(mageTotal(pid)<want&&p.gold-keep>=magePrice(pid)&&mythBuyMage(pid,t.id)) ids.push(t.id);
  for(const t of own.filter(t=>mageLvAt(t)>=0).sort((x,y)=>dist(x)-dist(y)))
    for(const k of ['dragon','griffin','minotaur']) while(p.gold-keep>=convPrice(t,k)&&mythConvert(pid,t.id,k)) ids.push(t.id);
  const front=castles[0]; if(front&&p.gold-keep>=1&&mythBuyMinions(pid,front.id,Math.min(p.gold-keep,6))) ids.push(front.id);
  return [...new Set(ids)];
}
function mythFactionInfo(fid){
  const f=FACTIONS[fid], other=FACTIONS[oppFor(fid,fsOpp)];
  return `<div class="fs-head"><span class="fs-castle px-c-${fid}" aria-hidden="true"></span><div><h2 style="color:${f.ink}">${f.name}</h2><p>${f.tagline}. You'll face the ${other.name}.</p></div></div>
    <h3>Magic, not gold</h3>
    <ul><li>The Mythical earn and spend only <b>magic</b> <span class="px px-magic" aria-hidden="true"></span>. Captured markets, forts and barracks do nothing for them, and they don't take bonus coins or plunder.</li>
      <li><b>Floating Castle</b> (home): ${MYTH.castleMagic[0]} magic and ${MYTH.minions[0]} Minions every turn. Three upgrades (${MYTH.castleUp.join(', ')} magic) raise that to ${MYTH.castleMagic.slice(1).join(', ')} magic and +2 Minions each. Only flyers can attack it.</li>
      <li><b>Life Trees</b>: ${MYTH.treeMagic} magic a turn, or ${MYTH.treeRich} with ${MYTH.treeMinions}+ Minions on the hex.</li></ul>
    <h3>Mages</h3>
    <ul><li>Made at your castles: ${MYTH.mageBase} magic, +1 for each Mage past your 5th and +1 for each Mage level. At most 2 on a hex (3 at level 3).</li>
      <li>Where a Mage stands it turns Minions into Minotaurs (${MYTH_CONV.minotaur.m} magic + 1 Minion), Griffins (${MYTH_CONV.griffin.m} + 2, level 1) and Dragons (${MYTH_CONV.dragon.m} + 4, level 2).</li>
      <li>Levels (${MYTH.mageUp.join(', ')} magic, at the castle): 1 Griffins, 2 Dragons, 3 every unit 1 magic cheaper and 3 Mages a hex. Each level also lengthens the Mage's lightning; a Mage keeps the level it was made at.</li>
      <li>Mages plant Life Trees (the Mage stays ${MYTH.treeTurns} turns) and raise magic domes (${MYTH.domeCost} magic, ${MYTH.domeUpkeep} a turn): a dome guards every side like a full wall.</li>
      <li>Mages and Minions move 2 hexes anywhere, and a Move action has 3 moves.</li></ul>
    <h3>Your cards</h3>
    <ul>${f.cards.map(c=>`<li><b>${c.name}</b>: ${c.actions.map(a=>ACTIONS[a].icon+' '+actName(a,fid)).join(' → ')}</li>`).join('')}</ul>
    <p>Channeling has no other actions: +${MYTH.chMage} magic for every Mage and +${MYTH.chCastle} for every castle. Mythical cards don't upgrade yet.</p>
    <h3>Your units</h3>${unitTable(fid)}
    <h3>How to win</h3>
    <ul><li><b>Take their home castle</b> and win on the spot.</li><li><b>Hold ${CASTLES_TO_WIN} castles</b> for ${HOLD_TURNS} of their turns.</li><li><b>Wipe them off the map.</b></li></ul>`;
}
"""
rep("const FACTORY_N=5, NEST_GOLD=2;\n", "const FACTORY_N=5, NEST_GOLD=2;\n"+MYTH_JS)

# ---------- moves ----------
rep("""function moveTargets(from,lvl){
  lvl=lvl||0;
  const pid=S.tiles[from].owner, out=new Set();
  for(const a of nbrs(from)){
    if(!canEnter(a,lvl)) continue;
    out.add(a);
    if(ANY_RUN[lvl]>=2&&passThrough""","""// where a hex's ready units can go; units that can't make a particular move (see moveFilter) are left out of it
function moveTargets(from,lvl){
  lvl=lvl||0; const t=S.tiles[from], pid=t.owner, far=isMyth(pid)&&Object.keys(t.ready||{}).some(k=>t.ready[k]>0&&fastUnit(k));
  return moveTargetsCore(from,lvl,far).filter(i=>{ const f=moveFilter(from,i,lvl); return !f||Object.keys(t.ready||{}).some(k=>t.ready[k]>0&&f(k)); });
}
function moveTargetsCore(from,lvl,far){
  lvl=lvl||0;
  const pid=S.tiles[from].owner, out=new Set();
  for(const a of nbrs(from)){
    if(!canEnter(a,lvl)) continue;
    out.add(a);
    if((ANY_RUN[lvl]>=2||far)&&passThrough""")
rep("const wallOn=(i,j)=>{ const w=S.tiles[i].walls; if(!w) return 0;", "const wallOn=(i,j)=>{ if(S.tiles[i].dome>0) return S.tiles[i].dome; const w=S.tiles[i].walls; if(!w) return 0;")   # a magic dome guards every side
rep("function setWall(i,j,hp){ const t=S.tiles[i], k=sideOf(i,j);", "function setWall(i,j,hp){ const t=S.tiles[i]; if(t.dome>0){ t.dome=Math.max(0,hp); return; } const k=sideOf(i,j);")

# ---------- units ----------
rep("""           fort:[['bat','Bat','Bat'],['gbat','Desmodus','Desmodus'],['eleph','Palaeoloxodon','Palaeoloxodon']]},
};""","""           fort:[['bat','Bat','Bat'],['gbat','Desmodus','Desmodus'],['eleph','Palaeoloxodon','Palaeoloxodon']]},
  // the Mythical have no barracks or forts; these lists only feed the unit tables
  mythical:{barracks:[['minion','Minion','Minion'],['minotaur','Minotaur','Minotaur'],['griffin','Griffin','Griffin'],['dragon','Dragon','Dragon']],
            fort:[['mage0','Mage','Mage']]},
};""")
rep("Object.assign(UNIT_ART,MAMMAL_ART.units);", "Object.assign(UNIT_ART,MAMMAL_ART.units);\nObject.assign(UNIT_ART,{minion:MYTH_ART.units.minion,minotaur:MYTH_ART.units.minotaur,griffin:MYTH_ART.units.griffin,dragon:MYTH_ART.units.dragon,\n  mage0:MYTH_ART.units.mage,mage1:MYTH_ART.units.mage,mage2:MYTH_ART.units.mage,mage3:MYTH_ART.units.mage});")
rep("const UNIT_KEYS=Object.keys(UNIT_STATS);", """// the Mythical (Ethan's arena stats). cost is their arena gold worth, used for strength; they pay in magic (see MYTH).
// The Mage's chain lightning is modeled as a shot that hits up to 8; the Dragon's fire breath as a bite that catches 3.
Object.assign(UNIT_STATS,{
  minion:  {name:'Minion',hp:5,dmg:2,rate:1.0,cost:1,rank:0,basic:true,hk:'melee'},
  mage0:   {name:'Mage',hp:15,dmg:5,rate:3,cost:15,rank:2,rng:true,aa:true,multi:8,hk:'magic'},
  mage1:   {name:'Mage (level 1)',hp:15,dmg:6,rate:3,cost:17,rank:2,rng:true,aa:true,multi:8,hk:'magic'},
  mage2:   {name:'Mage (level 2)',hp:15,dmg:7,rate:3,cost:19,rank:2,rng:true,aa:true,multi:8,hk:'magic'},
  mage3:   {name:'Mage (level 3)',hp:15,dmg:7,rate:3,cost:21,rank:2,rng:true,aa:true,multi:8,hk:'magic'},
  minotaur:{name:'Minotaur',hp:35,dmg:15,rate:1.0,cost:25,rank:0,heavy:true,multi:5,hk:'melee'},
  griffin: {name:'Griffin',hp:45,dmg:25,rate:1.0,cost:40,rank:1,air:true,aa:true,hk:'air'},
  dragon:  {name:'Dragon',hp:150,dmg:30,rate:1.0,cost:85,rank:1,air:true,aa:true,heavy:true,multi:3,hk:'air'},
});
const UNIT_KEYS=Object.keys(UNIT_STATS);""")
rep("const BASIC={dinos:'galli',robots:'brawler',mammals:'ape'};", """Object.assign(UNIT_NOTE,{
  minion:'Cheap and many. The only Mythical unit that captures castles. Mages turn Minions into bigger units',
  mage0:'Chain lightning: 5 damage to up to 20 enemies, ground or air, jumping from one to the next; reaches a quarter of the field. Every 2s, 20% chance to turn a Minion into a Minotaur',
  mage1:'Level 1: lightning reaches half the field and does 6',
  mage2:'Level 2: lightning reaches three quarters of the field and does 7',
  mage3:'Level 3: lightning reaches the whole field and does 7',
  minotaur:'Hammer hits up to 5 ground units. Charges in; its first hit kills outright (big units are stunned 4s instead)',
  griffin:'Flyer that hits flyers too. Swoops to the enemy front, knocks units back and screeches: shooters miss their next 2 shots, charges stop',
  dragon:'Flyer that hits flyers too. Fire breath burns up to 15 enemies every 8s. Opens with a fire run over the enemy that can\\'t be shot',
});
const BASIC={dinos:'galli',robots:'brawler',mammals:'ape',mythical:'minion'};""")
rep("const BASIC_PER={dinos:1,robots:2,mammals:1};", "const BASIC_PER={dinos:1,robots:2,mammals:1,mythical:3};")
rep("const GUARD_UNIT={dinos:'dilo',robots:'rarch',mammals:'porc'};", "const GUARD_UNIT={dinos:'dilo',robots:'rarch',mammals:'porc',mythical:'griffin'};   // the Floating Castle: 1 Griffin (Claude's stand-in)")
rep("return k?{[k]:HOME_GUARDS}:null; }", "return k?{[k]:isMyth(t.owner)?MYTH.guards:HOME_GUARDS}:null; }")
rep("const defBonus=t=>(t.castle?castleDef(t):(t.fort|0)*modsOf(t.owner).fortDefense)+bracedBonus(t);",
    "const defBonus=t=>(t.castle?castleDef(t):(isMyth(t.owner)?0:(t.fort|0))*modsOf(t.owner).fortDefense)+bracedBonus(t);   // captured forts do nothing for the Mythical")
rep("    return `<tr><td class=\"ut-n\"><img src=\"${UNIT_ART[k]}\" alt=\"\">${U.name}</td><td>${U.cost}</td>",
    "    return `<tr><td class=\"ut-n\"><img src=\"${UNIT_ART[k]}\" alt=\"\">${U.name}</td><td>${fid==='mythical'?(k==='minion'?`${MYTH.minionPack} for 1`:isMage(k)?`${MYTH.mageBase}+`:MYTH_CONV[k]?`${MYTH_CONV[k].m} + ${MYTH_CONV[k].min} Minion${MYTH_CONV[k].min>1?'s':''}`:U.cost):U.cost}</td>")
rep("<thead><tr><th>Unit</th><th>Gold</th>", "<thead><tr><th>Unit</th><th>${fid==='mythical'?'Magic':'Gold'}</th>")

# ---------- game setup, income, turns ----------
rep("""    p.gold=m.startGold+(i===1?SECOND_PLAYER_GOLD:0);
    if(p.ai) p.diff=(opts&&AI_PROF[opts.level])?opts.level:prefLevel;
    addBasic(S.tiles[HOMES[i]],i,m.startTroops,true);""","""    p.gold=m.startGold+(i===1?SECOND_PLAYER_GOLD:0);
    if(p.ai) p.diff=(opts&&AI_PROF[opts.level])?opts.level:prefLevel;
    if(p.faction==='mythical') mythSetup(p,i);   // 1 Mage, 4 Minions and 5 magic
    else addBasic(S.tiles[HOMES[i]],i,m.startTroops,true);""")
rep("if(SECOND_PLAYER_GOLD) addLog(`${S.players[1].name} start with ${SECOND_PLAYER_GOLD} extra gold to offset moving second.`);",
    "if(SECOND_PLAYER_GOLD) addLog(`${S.players[1].name} start with ${S.players[1].faction==='mythical'?MYTH.secondMagic+' extra magic':SECOND_PLAYER_GOLD+' extra gold'} to offset moving second.`);")
rep("function incomeOf(pid){\n", "function incomeOf(pid){\n  if(isMyth(pid)) return mythIncome(pid);\n")
rep("  S.tiles.forEach(t=>{if(t.owner===p.id){t.ready=Object.assign({},t.army||{}); syncT(t); if(t.braced===p.id) t.braced=-1;}});\n",
    "  S.tiles.forEach(t=>{if(t.owner===p.id){t.ready=Object.assign({},t.army||{}); syncT(t); if(t.braced===p.id) t.braced=-1;}});\n  if(isMyth(p.id)) mythTurnStart(p);   // dome upkeep, the Floating Castle's Minions, Mages rooted to new trees\n")
rep("  addLog(`${p.name} collect ${inc.total} gold.`,p.id);", "  addLog(`${p.name} collect ${inc.total} ${cur$(p.id)}.`,p.id);")
rep("const readyTrebs=pid=>S.tiles.filter(", "const readyTrebs=pid=>isMyth(pid)?[]:S.tiles.filter(")   # captured trebuchets do nothing for the Mythical
rep("function resolveInstant(pid,a,lvl,raw){\n  const p=S.players[pid]; lvl=lvl||0;\n", "function resolveInstant(pid,a,lvl,raw){\n  const p=S.players[pid]; lvl=lvl||0;\n  if(a==='channel') return mythChannel(pid);\n")
rep("    addLog(`${p.name} harvest ${g} gold", "    addLog(`${p.name} harvest ${g} ${cur$(pid)}")
rep("Harvest: +${g} gold${rain?", "Harvest: +${g} ${cur$(pid)}${rain?")
rep("  const a=curAction(), me=S.players[0], lvl=curLvl(), mine=S.tiles.filter(t=>t.owner===0);\n  if(a==='move'){",
    "  const a=curAction(), me=S.players[0], lvl=curLvl(), mine=S.tiles.filter(t=>t.owner===0);\n  if(isMyth(0)&&a!=='move') return null;\n  if(a==='move'){")

# ---------- executeMove ----------
rep("  else for(const k in n){ const m=Math.min(n[k]|0,(A.ready&&A.ready[k])||0); if(m>0) sel[k]=m; }\n",
    "  else for(const k in n){ const m=Math.min(n[k]|0,(A.ready&&A.ready[k])||0); if(m>0) sel[k]=m; }\n"
    "  { const fl=moveFilter(from,to,lvl||0); if(fl) for(const k in sel) if(!fl(k)) delete sel[k]; }   // flyers only at a Floating Castle; Mages and Minions only on a long move\n"
    "  mageTrim(A,B,sel);\n"
    "  if(!cnt(sel)) return {from,to,n:0,sent:{},kind:'none',att:A.owner};\n")
rep("  B.owner=A.owner; B.army={}; B.ready={}; addArmy(B,sel,false); B.braced=-1;\n",
    "  B.owner=A.owner; B.army={}; B.ready={}; addArmy(B,sel,false); B.braced=-1;\n  B.tree=0; B.root=0; B.dome=0;   // a Life Tree is destroyed and a dome falls when the hex is captured\n")
rep("  if(B.bounty){ B.bounty=false; p.gold+=COIN_GOLD; res.coin=COIN_GOLD; addLog(`${p.name} take a bonus coin: +${COIN_GOLD} gold.`,p.id); }",
    "  if(B.bounty){ B.bounty=false; if(!isMyth(A.owner)){ p.gold+=COIN_GOLD; res.coin=COIN_GOLD; addLog(`${p.name} take a bonus coin: +${COIN_GOLD} gold.`,p.id); } }   // the Mythical only use magic")
rep("""      p.gold+=CASTLE_PLUNDER;
      addLog(`${p.name} capture an enemy castle (+${CASTLE_PLUNDER} gold plunder).`,p.id);""","""      if(isMyth(A.owner)) addLog(`${p.name} capture an enemy castle.`,p.id);
      else { p.gold+=CASTLE_PLUNDER; addLog(`${p.name} capture an enemy castle (+${CASTLE_PLUNDER} gold plunder).`,p.id); }""")
rep("  const ks=byStrength(s.ready||{}), pick={}; ks.forEach(k=>pick[k]=0);",
    "  const mf=moveFilter(from,to,lvl), ks=byStrength(s.ready||{}).filter(k=>!mf||mf(k)), pick={}; ks.forEach(k=>pick[k]=0);\n  if(mf) text+=moveFilterNote(from,to);")
rep("recruit=undoable(recruit); train=undoable(train);", "mythAct=undoable(mythAct);\nrecruit=undoable(recruit); train=undoable(train);")

# ---------- AI ----------
rep("    else if(a==='recruit'){\n      const fr=freeTroops(pid,lvl), bi=card.actions.indexOf('build');",
    "    else if(isMyth(pid)&&(a==='recruit'||a==='build'||a==='advance')) yield {kind:'flash',ids:mythAi(pid,a,card.actions.slice(s+1))};\n"
    "    else if(a==='recruit'){\n      const fr=freeTroops(pid,lvl), bi=card.actions.indexOf('build');")
rep("""      moveTargets(t.id,lvl).forEach(i=>{
        const b=S.tiles[i];
        const claim=b.owner!==pid&&b.troops===0&&!wallFacing(t.id,i,lvl), opts=(claim&&avail>1)?[avail,avail-1,1]:[avail];""","""      moveTargets(t.id,lvl).forEach(i=>{
        const b=S.tiles[i], mf=moveFilter(t.id,i,lvl), keepR=t.ready;   // only the units that can make this move (flyers at a Floating Castle, Mages and Minions on a long move)
        if(mf){ const r={}; for(const k in keepR) if(mf(k)) r[k]=keepR[k]; t.ready=r; }
        try{
        const av=Math.min(avail,cnt(t.ready)); if(av<=0) return;
        const claim=b.owner!==pid&&b.troops===0&&!wallFacing(t.id,i,lvl), opts=(claim&&av>1)?[av,av-1,1]:[av];""")
rep("          if(v>0){ const c={v,from:t.id,to:i,n:pickUnits(t,n,claim&&n===1)}; if(search) cands.push(c); if(!best||v>best.v) best=c; }});\n      });",
    "          if(v>0){ const c={v,from:t.id,to:i,n:pickUnits(t,n,claim&&n===1)}; if(search) cands.push(c); if(!best||v>best.v) best=c; }});\n        } finally { t.ready=keepR; }\n      });")
rep("  const g=S.players[pid].gold; V+=", "  const g=S.players[pid].gold*(isMyth(pid)?MAGIC_VAL:1); V+=")
rep("(W.inc||4)*incomeOf(i).total", "(W.inc||4)*incomeOf(i).total*(isMyth(i)?MAGIC_VAL:1)")

# ---------- screen ----------
rep("const buildHex=()=>{ if(!S||!isHumanTurn()||ui.sel==null) return null; const a=curAction(), t=S.tiles[ui.sel]; if(t.owner!==0) return null;",
    "const buildHex=()=>{ if(!S||!isHumanTurn()||ui.sel==null) return null; const a=curAction(), t=S.tiles[ui.sel]; if(t.owner!==0) return null;\n"
    "  if(isMyth(0)) return (a==='recruit'?(t.castle||mageLvAt(t)>=0):a==='build'?(t.terrain==='plain'&&!t.castle):a==='advance'?t.terrain!=='water':false)?ui.sel:null;   // Mythical: castles and Mage hexes, Mage hexes for trees, any hex for upgrades and domes")
rep("  y0=Math.min(y0,cy-HR-reach); y0=Math.max(y0,cy+HR+1-h);\n  return [x0,y0,w,h];",
    "  if(isMyth(0)&&curAction()!=='build') y0=Math.max(y0,cy+HR+reach-h);   // Mythical buttons can go all the way round the hex\n  y0=Math.min(y0,cy-HR-reach); y0=Math.max(y0,cy+HR+1-h);\n  return [x0,y0,w,h];")
rep("  const menu=recruiting&&ui.train&&hasMenu(t,ui.train)?ui.train:null;\n",
    "  if(isMyth(0)){ const m=mythBubbles(P,cx,cy,k,R,stem); ov.hidden=false; ov.innerHTML=`<svg aria-hidden=\"true\">${m.lines}</svg>${m.html}`; requestAnimationFrame(()=>{ void ov.offsetWidth; ov.classList.add('show'); }); return; }\n  const menu=recruiting&&ui.train&&hasMenu(t,ui.train)?ui.train:null;\n")
rep("$('#bldov').addEventListener('click',e=>{ if(!isHumanTurn()||ui.sel==null) return;\n",
    "$('#bldov').addEventListener('click',e=>{ if(!isHumanTurn()||ui.sel==null) return;\n  const my=e.target.closest('button[data-my]'); if(my){ mythAct(my.dataset.my,my.dataset.k); return; }\n")
# the Life Tree stands big in the middle of its hex instead of small at the side
rep("    const ics=[]; if(S.homes.includes(i)&&t.castle&&owned) ics.push('crown');",
    "    if(t.tree&&owned&&!swords){ const z=TREE_SIZE; castles+=`<use href=\"#b-tree\" transform=\"translate(${(cx-z/2+2).toFixed(2)} ${(cy+HR*.42-z).toFixed(2)}) scale(${(z/16).toFixed(4)})\"/>`; }   // a Life Tree: big, in the middle of its hex\n    const ics=[]; if(S.homes.includes(i)&&t.castle&&owned) ics.push('crown');")
rep("const BLD_SIZE=9.6,", "const TREE_SIZE=25; const BLD_SIZE=9.6,")
rep("    if(t.walls) t.walls.forEach((hp,k)=>{ if(hp>0) walls+=wallSvg(", "    if(t.dome>0) walls+=domeSvg(cx,cy,t.dome);\n    if(t.walls) t.walls.forEach((hp,k)=>{ if(hp>0) walls+=wallSvg(")
rep("<span class=\"sh-gold\"><span class=\"px px-coin\" aria-hidden=\"true\"></span> ${S.players[0].gold}</span>",
    "<span class=\"sh-gold\" title=\"${isMyth(0)?'Magic':'Gold'}\"><span class=\"px px-${isMyth(0)?'magic':'coin'}\" aria-hidden=\"true\"></span> ${S.players[0].gold}</span>")
rep("<div class=\"stat coin\"><span class=\"sl\">Coin production</span><span class=\"sv\">+${incomeOf(0).total}<small>/ turn</small></span><span class=\"ss\">${op.name} +${incomeOf(1).total}</span></div>",
    "<div class=\"stat coin\"><span class=\"sl\">${isMyth(0)?'Magic':'Coin'} production</span><span class=\"sv\">+${incomeOf(0).total}<small>/ turn</small></span><span class=\"ss\">${op.name} +${incomeOf(1).total}${isMyth(1)!==isMyth(0)?' '+cur$(1):''}</span></div>")
rep("  const me=S.players[0], a=curAction(), sel=ui.sel!=null?S.tiles[ui.sel]:null;\n  let h=notesHtml();\n",
    "  const me=S.players[0], a=curAction(), sel=ui.sel!=null?S.tiles[ui.sel]:null;\n  let h=notesHtml();\n  if(isMyth(0)&&(a==='recruit'||a==='build'||a==='advance')) return h+mythStepBody(a,sel);\n")
rep("function favStrip(pid,cid){\n", "function favStrip(pid,cid){\n  if(isMyth(pid)) return '';   // Mythical cards don't upgrade yet\n")
rep("    const fvTxt=upsOf(0,c.id).every(v=>v>=MAX_UP)?'This card is fully upgraded.'", "    const fvTxt=isMyth(0)?'Mythical cards don\\'t upgrade yet.':upsOf(0,c.id).every(v=>v>=MAX_UP)?'This card is fully upgraded.'")
rep("<span class=\"bc-how\">You'll carry out these 3 actions in order and can skip any of them. </span>",
    "<span class=\"bc-how\">${c.actions.length===1?'This card has no other actions. ':'You\\'ll carry out these 3 actions in order and can skip any of them. '}</span>")
rep("  else if(a==='volleydone'){ S.volley=null; render(); }", "  else if(a==='volleydone'){ S.volley=null; render(); }\n  else if(a==='my') mythAct(b.dataset.op,b.dataset.k);")
rep("function factionInfo(fid){\n", "function factionInfo(fid){\n  if(fid==='mythical') return mythFactionInfo(fid);\n")
rep("const ARENA_FAC={dinos:'Dinosaurs',robots:'Robots',mammals:'Mammals'};", "const ARENA_FAC={dinos:'Dinosaurs',robots:'Robots',mammals:'Mammals',mythical:'Mythical'};")

open(sys.argv[2],'w').write(s); json.dump(edits,open(sys.argv[3],'w')); print('board ok',len(edits))

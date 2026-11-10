# Three-player mode, step 2: the rules and the screens (Ethan, 2026-11-09).
#   - Turn order runs through the three seats; the 2nd and 3rd seats start with 6 and 12 extra gold (the 2-player game's
#     8 for the 2nd seat, scaled to a third of a round per seat). The Mythical get their extra magic the same way.
#   - A side whose home castle is captured is out: its units, walls, trebuchets, Life Trees and domes are gone and all its
#     land turns neutral, buildings and all, for anyone to walk into. A side with no land left is out too.
#     The last side standing wins; there is no castle-count win with 3 players.
#   - A captured home castle is an ordinary castle for whoever holds it (no home defense, guards, crown or home art).
#   - Computer-vs-computer battles are settled on the board (the arena is for battles you fight).
#   - The faction screen gets a Players 2 / 3 choice and, for 3, a pick of two opponents.
import sys
p=sys.argv[1]; s=open(p,encoding='utf8').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:100]); s=s.replace(a,b)

# ---- catch-up gold, colors ----
rep("""const SECOND_PLAYER_GOLD=8;      // offsets the first-move advantage (computer vs computer with card upgrades: about 50/50)""",
"""const SECOND_PLAYER_GOLD=8;      // offsets the first-move advantage (computer vs computer with card upgrades: about 50/50)
// extra gold (or magic) for a seat that moves later: 2 players, the 2nd seat gets it all; 3 players, 3/4 of it per seat behind (6, 12)
const catchUp=(i,base,np)=>np>2?Math.round(base*.75*i):(i===1?base:0);""")
rep("""function otherColor(taken,fid){ const d=FAC_COLOR[fid]; if(d&&d!==taken) return d; return ['red','blue','purple','green','yellow'].find(c=>c!==taken); }""",
"""function otherColor(taken,fid){ const tk=[].concat(taken), d=FAC_COLOR[fid]; if(d&&!tk.includes(d)) return d; return ['red','blue','purple','green','yellow'].find(c=>!tk.includes(c)); }""")
rep("""  p.gold=MYTH.startMagic+(i===1?MYTH.secondMagic:0);""","""  p.gold=MYTH.startMagic+catchUp(i,MYTH.secondMagic,S.players.length);""")

# ---- a new game for 2 or 3 ----
rep("""function newGame(fid,opts){
  if(!FACTIONS[fid]) fid=DEFAULT_FACTION;
  const other=oppFor(fid,opts&&opts.opp);
  const facs=[fid,other];
  S={turn:1,current:0,over:null,log:[],homes:HOMES.slice(),play:null,""","""function newGame(fid,opts){
  if(!FACTIONS[fid]) fid=DEFAULT_FACTION;
  const np=opts&&opts.np===3?3:2; useBoard(np);
  const facs=np===3?[fid,...threeOpps(fid,opts&&opts.opps)]:[fid,oppFor(fid,opts&&opts.opp)];
  S={turn:1,current:0,over:null,log:[],homes:HOMES.slice(),play:null,""")
rep("""  { const mine=myColorFor(facs[0]); applyColor(S.players[0],mine); applyColor(S.players[1],otherColor(mine,facs[1])); }
  S.players.forEach((p,i)=>{
    const m=modsOf(i);
    p.gold=m.startGold+(i===1?SECOND_PLAYER_GOLD:0);""","""  { const mine=myColorFor(facs[0]), taken=[mine]; applyColor(S.players[0],mine);
    for(let i=1;i<np;i++){ const c=otherColor(taken,facs[i]); applyColor(S.players[i],c); taken.push(c); } }
  S.players.forEach((p,i)=>{
    const m=modsOf(i);
    p.gold=m.startGold+catchUp(i,SECOND_PLAYER_GOLD,np);""")
rep("""  if(SECOND_PLAYER_GOLD) addLog(`${S.players[1].name} start with ${S.players[1].faction==='mythical'?MYTH.secondMagic+' extra magic':SECOND_PLAYER_GOLD+' extra gold'} to offset moving second.`);
  addLog(`A new age begins. You lead the ${FACTIONS[facs[0]].name}; the ${FACTIONS[facs[1]].name} oppose you. Win by taking their home castle, holding ${CASTLES_TO_WIN} castles, or wiping them off the map.`);""",
"""  for(let i=1;i<np;i++){ const q=S.players[i], my=q.faction==='mythical', g=catchUp(i,my?MYTH.secondMagic:SECOND_PLAYER_GOLD,np);
    if(g) addLog(`${q.name} start with ${g} extra ${my?'magic':'gold'} to offset moving ${i===1?'second':'third'}.`); }
  if(np===3) addLog(`A new age begins. You lead the ${FACTIONS[facs[0]].name}; the ${FACTIONS[facs[1]].name} and the ${FACTIONS[facs[2]].name} oppose you. Take a side's home castle, or wipe them off the map, and they're out. The last side standing wins.`);
  else addLog(`A new age begins. You lead the ${FACTIONS[facs[0]].name}; the ${FACTIONS[facs[1]].name} oppose you. Win by taking their home castle, holding ${CASTLES_TO_WIN} castles, or wiping them off the map.`);""")

# ---- turn order: the next side still in the game ----
rep("""  S.current=1-S.current;
  if(S.current===(S.first||0)){ S.turn++; if(S.turn===NEW_CASTLE_ROUND+1&&S.extraCastle==null) spawnCastle(); }""",
"""  // the next side still in the game; a new round starts each time play passes the first seat
  const n=S.players.length, first=S.first||0; let c=done, round=false;
  for(let k=0;k<n;k++){ c=(c+1)%n; if(c===first) round=true; if(!S.players[c].out) break; }
  S.current=c;
  if(round){ S.turn++; if(S.turn===NEW_CASTLE_ROUND+1&&S.extraCastle==null) spawnCastle(); }""")

# ---- knocked out, and the last side standing ----
rep("""function endGame(winner,why){ S.over=winner===0?'win':'lose'; S.overWhy=why; }""",
"""function endGame(winner,why){ S.over=winner===0?'win':'lose'; S.overWhy=why; S.winner=winner; }
// 3 players: a side whose home castle falls (or that has no land left) is out. Its land goes neutral: its units, walls,
// trebuchets, Life Trees and domes are gone; the buildings stay for whoever walks in. The last side standing wins.
function knockOut(pid,by,why){
  const p=S.players[pid]; if(!p||p.out) return;
  p.out=true; p.outBy=by; p.outWhy=why; p.outRound=S.turn; p.volc=null;
  S.tiles.forEach(t=>{
    if(t.braced===pid) t.braced=-1;
    if(t.owner!==pid) return;
    t.owner=-1; t.army={}; t.ready={}; t.walls=[0,0,0,0,0,0]; t.braced=-1;
    t.treb=0; t.trebDue=0; t.treb2=0; t.trebDue2=0; t.tree=0; t.root=0; t.dome=0;
    syncT(t);
  });
  const who=pid===0?'You are':`The ${p.name} are`;
  addLog(by!=null?`${who} out of the game: ${by===0?'you':'the '+S.players[by].name} took ${pid===0?'your':'their'} home castle, and ${pid===0?'your':'their'} land goes neutral.`:`${who} out of the game: no land left.`,by!=null?by:pid);
  const left=S.players.filter(q=>!q.out);
  if(left.length===1) endGame(left[0].id,'last');
  else if(pid===0&&!NET&&!p.ai){ S.over='lose'; S.overWhy=why; S.winner=null; }   // you're out: the game is over for you
}""")
rep("""function checkCastles(){
  if(S.over) return;""","""function checkCastles(){
  if(S.over) return;
  if(S.players.length>2){   // 3 players: no castle-count win; a side with no land left is out
    S.players.forEach(q=>{ if(!q.out&&!S.over&&!S.tiles.some(t=>t.owner===q.id)) knockOut(q.id,null,'wipe'); });
    return;
  }""")
rep("""    else if(to===S.homes[prev]){                       // way 1 to win: take the enemy's home castle
      addLog(`${p.name} capture the enemy home castle!`,p.id);
      endGame(A.owner,'home'); return res;
    }""","""    else if(to===S.homes[prev]){                       // way 1 to win: take the enemy's home castle (3 players: it knocks them out)
      if(S.players.length>2){ addLog(`${p.name} capture ${prev===0?'your':`the ${S.players[prev].name}'`} home castle!`,p.id); res.knockout=prev; knockOut(prev,A.owner,'home'); if(S.over) return res; }
      else { addLog(`${p.name} capture the enemy home castle!`,p.id); endGame(A.owner,'home'); return res; }
    }""")
rep("""  let pool=open.filter(t=>Math.abs(man(t.id,S.homes[0])-man(t.id,S.homes[1]))<=1);""",
"""  const hs=S.homes.filter((h,i)=>!S.players[i].out);
  let pool=open.filter(t=>{ const ds=hs.map(h=>man(t.id,h)); return Math.max(...ds)-Math.min(...ds)<=1; });""")
rep("""There are now ${S.tiles.filter(t=>t.castle).length} castles; the first side to hold ${CASTLES_TO_WIN} of them for ${HOLD_TURNS} enemy turns wins.</p>""",
"""There are now ${S.tiles.filter(t=>t.castle).length} castles${S.players.length>2?'. Claim it for its gold and a new place to recruit.':`; the first side to hold ${CASTLES_TO_WIN} of them for ${HOLD_TURNS} enemy turns wins.`}</p>""")

# ---- a captured home castle is an ordinary castle ----
rep("""const castleDef=t=>S.homes.includes(t.id)?HOME_DEFENSE:modsOf(t.owner).castleDefense;""",
    """const castleDef=t=>isHomeCastle(t)?HOME_DEFENSE:modsOf(t.owner).castleDefense;""")
rep("""const castleArt=t=>(S.homes.includes(t.id)&&t.owner>=0)?S.players[t.owner].faction:'neutral';""",
    """const castleArt=t=>isHomeCastle(t)?S.players[t.owner].faction:'neutral';""")
rep("""const ics=[]; if(S.homes.includes(i)&&t.castle&&owned) ics.push('crown');""","""const ics=[]; if(isHomeCastle(t)&&owned) ics.push('crown');""")
rep("""  const isHome=S.homes.includes(id);
  const hp=S.homes.indexOf(id);""","""  const isHome=isHomeCastle(t);
  const hp=isHome?t.owner:-1;""")
rep("""  const where=`${B.castle?(S.homes.includes(B.id)?'home castle':'castle'):'hex'} (${MAP_NAME[f.map]})`;""",
    """  const where=`${B.castle?(isHomeCastle(B)?'home castle':'castle'):'hex'} (${MAP_NAME[f.map]})`;""")
rep("""+(S.homes.includes(j)?3:0)-0.05*man(h,j);""","""+(isHomeCastle(b)?3:0)-0.05*man(h,j);""")
rep("""-0.7*wallOn(j,i)+(S.homes.includes(j)?2:0);""","""-0.7*wallOn(j,i)+(isHomeCastle(b)?2:0);""")

# ---- arena sides: worked out for the two sides in the fight ----
rep("""const arenaTeam=pid=>{ const f=S.players[pid].faction, o=S.players[1-pid].faction;
  if(f===o) return pid===0?0:1;
  if(ARENA_TEAM[f]!=null) return ARENA_TEAM[f];
  if(ARENA_TEAM[o]!=null) return 1-ARENA_TEAM[o];
  return pid===0?0:1; };""","""const arenaTeam=(pid,other)=>{
  if(other==null) other=S.players.length===2?1-pid:(S.fight?(S.fight.att===pid?S.fight.def:S.fight.att):(pid===0?1:0));   // the other side in the fight
  const f=S.players[pid].faction, o=S.players[other].faction;
  if(f===o) return pid<other?0:1;
  if(ARENA_TEAM[f]!=null) return ARENA_TEAM[f];
  if(ARENA_TEAM[o]!=null) return 1-ARENA_TEAM[o];
  return pid<other?0:1; };""")
rep("""    const tA=arenaTeam(A.owner), tD=1-tA, defStart=defArmy(B);""","""    const tA=arenaTeam(A.owner,prev), tD=1-tA, defStart=defArmy(B);""")
rep("""    const tA=arenaTeam(f.att), me=arenaTeam(0), armies=[{},{}];""","""    const tA=arenaTeam(f.att,f.def), me=f.def===0?1-tA:tA, armies=[{},{}], sideOf=t=>S.players[t===tA?f.att:f.def];""")
rep("""    const cols=[0,1].map(t=>{ const q=S.players.find(pp=>arenaTeam(pp.id)===t)||S.players[t]; const C=COLORS[q.col]; return {c:q.color,i:inkOf(q),t:txtOf(q),n:C?C.name:(t?'Red':'Blue')}; });
    const factions=[0,1].map(t=>{ const q=S.players.find(pp=>arenaTeam(pp.id)===t); return q?ARENA_FAC[q.faction]:null; });
    arenaPost({cc:'setup',role,me,ai:role==='local'?[1-me]:[],lvl:aiLv(Math.max(0,S.players.findIndex(p=>p.ai))),map:f.map,hold:arenaTeam(f.def),""",
"""    const cols=[0,1].map(t=>{ const q=sideOf(t); const C=COLORS[q.col]; return {c:q.color,i:inkOf(q),t:txtOf(q),n:C?C.name:(t?'Red':'Blue')}; });
    const factions=[0,1].map(t=>ARENA_FAC[sideOf(t).faction]||null);
    const aiSide=[f.att,f.def].find(i=>S.players[i].ai);
    arenaPost({cc:'setup',role,me,ai:role==='local'?[1-me]:[],lvl:aiLv(aiSide!=null?aiSide:Math.max(0,S.players.findIndex(p=>p.ai))),map:f.map,hold:1-tA,""")
rep("""  const tA=arenaTeam(f.att), tD=1-tA, n=a=>cnt(a||{});""","""  const tA=arenaTeam(f.att,f.def), tD=1-tA, n=a=>cnt(a||{});""")
# the computer's attacks on another computer are settled on the board; only fights against you go to the arena
rep("""function aiMv(from,to,n,lvl){ if(ARENA_LIVE&&isFight(from,to)) return""",
    """function aiMv(from,to,n,lvl){ if(ARENA_LIVE&&isFight(from,to)&&!S.players[S.tiles[to].owner].ai) return""")
# the computer's view of a finished game
rep("""  if(S.over) return ((S.over==='win')===(pid===0))?1e5:-1e5;""","""  if(S.over&&S.winner!=null) return S.winner===pid?1e5:-1e5;""")
# online (2 players): the winner flips with the sides
rep("""  s.current=1-s.current; s.first=1-(s.first||0);""","""  s.current=1-s.current; s.first=1-(s.first||0); if(s.winner!=null) s.winner=1-s.winner;""")

# ---- the header, the numbers under the board, the end of the game ----
rep("""  let race=`<span class="sh-castles" title="Hold ${CASTLES_TO_WIN} castles to win">""",
"""  let race=S.players.length>2?`<span class="sh-castles" title="Castles held"><span class="px px-c-neutral" aria-hidden="true"></span> ${S.players.map(p=>`<b style="color:${inkOf(p)}${p.out?';opacity:.4;text-decoration:line-through':''}">${castleCount(p.id)}</b>`).join('–')}</span>`
   :`<span class="sh-castles" title="Hold ${CASTLES_TO_WIN} castles to win">""")
rep("""function renderStats(){
  const me=S.players[0], op=S.players[1];""","""function renderStats(){
  const me=S.players[0], op=S.players[1], ops=S.players.filter(q=>q.id!==0&&!q.out);""")
rep("""<span class="ss">${op.name} +${incomeOf(1).total}${isMyth(1)!==isMyth(0)?' '+cur$(1):''}</span></div>""",
    """<span class="ss">${ops.map(o=>`${o.name} +${incomeOf(o.id).total}${isMyth(o.id)!==isMyth(0)?' '+cur$(o.id):''}`).join(' · ')}</span></div>""")
rep("""${own(0).filter(t=>t.castle).length} castle${own(0).filter(t=>t.castle).length===1?'':'s'} · ${op.name} ${own(1).length}</span></div>""",
    """${own(0).filter(t=>t.castle).length} castle${own(0).filter(t=>t.castle).length===1?'':'s'} · ${ops.map(o=>`${o.name} ${own(o.id).length}`).join(' · ')}</span></div>""")
rep("""<span class="sv">${units(0)}</span><span class="ss">${op.name} ${units(1)}</span></div>`;""",
    """<span class="sv">${units(0)}</span><span class="ss">${ops.map(o=>`${o.name} ${units(o.id)}`).join(' · ')}</span></div>`;""")
rep("""  if(S.over){
    const op=S.players[1].name, why=S.overWhy;""","""  if(S.over&&S.players.length>2){   // 3 players: the last side standing, or knocked out
    const w=S.winner!=null?S.players[S.winner]:null, by=me.outBy!=null?S.players[me.outBy]:null;
    P.innerHTML=`<div class="bigcard over">`+(S.over==='win'
      ?`<p class="big">You rule the land <span class="px px-crown" aria-hidden="true"></span></p><p class="hint">You're the last side standing. ${S.players.filter(q=>q.id!==0).map(q=>`The ${q.name} fell in round ${q.outRound||S.turn}${q.outBy===0?' to you':q.outBy!=null?' to the '+S.players[q.outBy].name:''}.`).join(' ')}</p>`
      :`<p class="big">${me.out?'You are out':`The ${w?w.name:'enemy'} rule the land`}</p><p class="hint">${me.outWhy==='home'&&by?`The ${by.name} took your home castle`:me.outWhy==='wipe'?'You have no land left':'You were knocked out'} in round ${me.outRound||S.turn}.${w?` The ${w.name} were the last side standing.`:''}</p>`)
      +`<div class="bc-foot"><button class="primary" data-act="new">${NET?'Back to Play online':S.over==='win'?'Play again':'Try again'}</button></div></div>`;
    return;
  }
  if(S.over){
    const op=S.players[1].name, why=S.overWhy;""")

# ---- How to play ----
rep("""  openInfo('How to play',`<p>You start at the bottom-left castle. <b>There are three ways to win:</b></p>
  <ol class="wins"><li><b>Take their home castle.</b> Capture the enemy's home castle and you win on the spot.</li>""",
"""  openInfo('How to play',`${S.players.length>2?WINS3_HTML:''}<p${S.players.length>2?' hidden':''}>You start at the bottom-left castle. <b>There are three ways to win:</b></p>
  <ol class="wins"${S.players.length>2?' hidden':''}><li><b>Take their home castle.</b> Capture the enemy's home castle and you win on the spot.</li>""")
rep("""    <li><b>Bonus coins.</b> A third of the open hexes start with""","""    <li><b>Bonus coins.</b> ${S.players.length>2?'Close to half':'A third'} of the open hexes start with""")
rep("""    <li><b>Castles.</b> Three neutral castles sit empty across the map.""","""    <li><b>Castles.</b> ${['No','One','Two','Three','Four','Five','Six','Seven','Eight'][NEUTRAL_CASTLES]||NEUTRAL_CASTLES} neutral castles sit empty across the map.""")
rep("""function showRules(){""","""const WINS3_HTML=`<p>You start at the bottom-left castle; two rivals hold the other home castles. <b>The last side standing wins.</b></p>
  <ol class="wins"><li><b>Take a home castle.</b> Capture a rival's home castle and they're out of the game. Their units, walls and trebuchets are gone and all their land turns neutral, buildings and all, for anyone to walk into.</li>
  <li><b>Wipe them out.</b> A side with no hexes left is out too.</li>
  <li><b>Be the last one left.</b> When only one side remains, it wins. There's no castle count to win by with 3 players.</li></ol>`;
function showRules(){""")

# ---- the faction screen: 2 or 3 players ----
rep("""<div class="fs-picks"><div id="fsOpp"></div>""","""<div class="fs-picks"><div id="fsPlayers"></div><div id="fsOpp"></div>""")
rep("""let fsPick=DEFAULT_FACTION, fsOpp=null;""","""let fsPick=DEFAULT_FACTION, fsOpp=null, fsOpps=[], fsNP=2;
try{ if(localStorage.getItem('cc-np')==='3') fsNP=3; }catch(e){}
// 3 players: the two opponents' factions (the ones picked, filled up from the faction list)
function threeOpps(fid,want){ const o=(want||[]).filter((f,i,a)=>FACTIONS[f]&&f!==fid&&a.indexOf(f)===i).slice(0,2);
  for(const f of FACTION_ORDER){ if(o.length>=2) break; if(f!==fid&&!o.includes(f)) o.push(f); } return o; }
function playersPicker(np){
  return `<div class="opick" role="group" aria-label="Players"><span class="cp-l">Players</span>${[2,3].map(n=>`<button class="op-b" data-np="${n}" aria-pressed="${n===np}" style="--pc:var(--bone)">${n}</button>`).join('')}</div>`;
}
function oppPicker3(fid,want){
  const o=threeOpps(fid,want);
  return `<div class="opick" role="group" aria-label="Opponents"><span class="cp-l">Opponents (pick 2)</span>${FACTION_ORDER.filter(f=>f!==fid).map(f=>`<button class="op-b" data-opp3="${f}" aria-pressed="${o.includes(f)}" style="--pc:${FACTIONS[f].ink}"><span class="px px-c-${f}" aria-hidden="true"></span>${FACTIONS[f].name}</button>`).join('')}</div>`;
}
// what the faction page says about who you face and how to win
const faceLine=(fid)=>fsNP===3?(()=>{ const o=threeOpps(fid,fsOpps); return `You'll face the ${FACTIONS[o[0]].name} and the ${FACTIONS[o[1]].name}.`; })():`You'll face the ${FACTIONS[oppFor(fid,fsOpp)].name}.`;
const winListHtml=()=>fsNP===3?`<ul><li><b>Take a rival's home castle</b> and they're out; their land turns neutral.</li><li><b>Wipe a rival off the map</b> and they're out too.</li><li><b>Be the last side standing.</b></li></ul>`
  :`<ul><li><b>Take their home castle</b> and win on the spot.</li><li><b>Hold ${CASTLES_TO_WIN} castles</b> for ${HOLD_TURNS} of their turns.</li><li><b>Wipe them off the map.</b></li></ul>`;""")
rep("""You'll face the ${other.name}.</p></div></div>""","""${faceLine(fid)}</p></div></div>""",2)
rep("""    <ul><li><b>Take their home castle</b> and win on the spot.</li><li><b>Hold ${CASTLES_TO_WIN} castles</b> for ${HOLD_TURNS} of their turns.</li><li><b>Wipe them off the map.</b></li></ul>`;""",
    """    ${winListHtml()}`;""",2)
rep("""  $('#fsOpp').innerHTML=oppPicker(fsPick,fsOpp);""","""  $('#fsPlayers').innerHTML=playersPicker(fsNP);
  $('#fsOpp').innerHTML=fsNP===3?oppPicker3(fsPick,fsOpps):oppPicker(fsPick,fsOpp);""")
rep("""  const fob=e.target.closest('button[data-opp]'); if(fob){ fsOpp=fob.dataset.opp; renderFactionScreen(); return; }""",
"""  const fob=e.target.closest('button[data-opp]'); if(fob){ fsOpp=fob.dataset.opp; renderFactionScreen(); return; }
  const fnp=e.target.closest('button[data-np]'); if(fnp){ fsNP=+fnp.dataset.np===3?3:2; try{ localStorage.setItem('cc-np',String(fsNP)); }catch(_){} renderFactionScreen(); return; }
  const fo3=e.target.closest('button[data-opp3]'); if(fo3){ const f=fo3.dataset.opp3, cur3=threeOpps(fsPick,fsOpps);   // pick 2: tapping a third swaps out the one picked longest ago
    fsOpps=cur3.includes(f)?cur3:[cur3[1],f]; renderFactionScreen(); return; }""")
rep("""  else if(k==='go'){ showScreen(null); newGame(fsPick,{opp:fsOpp}); }""","""  else if(k==='go'){ showScreen(null); newGame(fsPick,{np:fsNP,opp:fsOpp,opps:fsOpps}); }""")
open(p,'w',encoding='utf8').write(s); print('patch2 ok')

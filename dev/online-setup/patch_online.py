"""Ethan, 2026-11-23: "make sure the online multiplayer is also themed the same as the single player" and "have the online
game set up the same as the local player set up".
- Play online is themed like the setup screen: the blurred battle painting, an iron panel with bronze trim, Cinzel
  headings in parchment, iron plates, a gold plate for the main button, gold-lettered game codes.
- New game opens the same three-tab setup (You / Opponent / Map & rules) in an online mode: the opponent tab says who
  plays each side (a friend, or with 3 players a friend or the computer), the colours of friends are theirs to pick,
  Difficulty shows only when the computer plays a seat, the map tab is the same (hand-made maps work online too),
  and the foot reads Online / Back, Next and Create game.
- Fix on the way: a device opening an online game on a hand-made map now takes that map's shape (syncShape).
Usage: python3 patch_online.py index.html"""
import sys
P = sys.argv[1]; s = open(P).read()
def rep(a, b, n=1):
    global s; c = s.count(a); assert c == n, (c, a[:90]); s = s.replace(a, b)

# ---------------- the setup screen's online mode
rep("let fsPick=DEFAULT_FACTION, fsOpp=null, fsOpps=[], fsNP=2, fsMap='';",
    "let fsPick=DEFAULT_FACTION, fsOpp=null, fsOpps=[], fsNP=2, fsMap='';\n"
    "let fsOnline=false, _fsLocal=null;   // the setup screen making an online game (Ethan, 2026-11-23); the local picks kept aside meanwhile")
rep("function startNewGame(){ fsTab=0; renderFactionScreen(); showScreen('scrFaction'); }",
    """function startNewGame(){ if(fsOnline) fsLeaveOnline(); fsTab=0; renderFactionScreen(); showScreen('scrFaction'); }
// Play online -> New game: the same three tabs, with the online picks (kept apart from the local game's)
function fsEnterOnline(){
  if(!fsOnline){ _fsLocal={pick:fsPick,opp:fsOpp,opps:fsOpps,np:fsNP}; fsOnline=true; }
  fsPick=NETX.pick; fsOpp=NETX.opp; fsOpps=NETX.opps; fsNP=NETX.np===3?3:2;
  fsTab=0; closeModal(); renderFactionScreen(); showScreen('scrFaction');
}
function fsLeaveOnline(){
  if(!fsOnline) return;
  NETX.pick=fsPick; NETX.opp=fsOpp; NETX.opps=fsOpps; NETX.np=fsNP;
  if(_fsLocal){ fsPick=_fsLocal.pick; fsOpp=_fsLocal.opp; fsOpps=_fsLocal.opps; fsNP=_fsLocal.np; }
  fsOnline=false; _fsLocal=null;
}
// who plays a rival seat online: 2 players always a friend; 3 players a friend or the computer
const fsKind=k=>fsOnline?(fsNP===3?(NETX.kinds[k]==='cpu'?'cpu':'friend'):'friend'):'cpu';""")

# tab 2: who plays each rival, colours only for the computer's seats, difficulty only when the computer plays
rep("""        return `<div class="fsx-rival"><div class="fsx-l">${fsNP===3?`Rival ${k+1}`:'Opponent'} <small>played by the computer</small></div>""",
    """        const kind=fsKind(k);
        return `<div class="fsx-rival"><div class="fsx-l">${fsNP===3?`Rival ${k+1}`:'Opponent'} <small>played by ${kind==='cpu'?'the computer':'a friend'}</small></div>
          ${fsOnline&&fsNP===3?`<div class="opick fsx-kind" role="group" aria-label="Who plays rival ${k+1}"><span class="cp-l">Played by</span>${[['friend','A friend'],['cpu','The computer']].map(([kk,l])=>`<button class="op-b" data-okind="${k}:${kk}" aria-pressed="${kind===kk}" style="--pc:var(--bone)">${l}</button>`).join('')}</div>`:''}""")
rep("""          ${fsxSwatches(cols[k+1],c=>`data-ocol="${k}:${c}"`,others)}</div>`; }).join('')}
      <button class="fsx-more" data-fsx="level"><span class="ic">!</span><span>Difficulty: ${AI_LEVEL_NAME[lv]} <small>${AI_LEVEL_NOTE[lv]}</small></span></button>`;""",
    """          ${kind==='cpu'?fsxSwatches(cols[k+1],c=>`data-ocol="${k}:${c}"`,others):`<p class="hint">Your friend picks their own color when they join.</p>`}</div>`; }).join('')}
      ${rivals.some((rf,k)=>fsKind(k)==='cpu')?`<button class="fsx-more" data-fsx="level"><span class="ic">!</span><span>Difficulty: ${AI_LEVEL_NAME[lv]} <small>${AI_LEVEL_NOTE[lv]}</small></span></button>`
        :`<p class="hint">Online: send your friend the game's code once it's made.</p>`}`;""")
rep("""<div class="fsx-np">${[2,3].map(n=>`<button class="op-b" data-np="${n}" aria-pressed="${n===fsNP}" style="--pc:var(--bone)">${n}</button>`).join('')}<span class="hint">${fsNP===3?'You and two rivals':'You and one opponent'}</span></div>""",
    """<div class="fsx-np">${[2,3].map(n=>`<button class="op-b" data-np="${n}" aria-pressed="${n===fsNP}" style="--pc:var(--bone)">${n}</button>`).join('')}<span class="hint">${fsNP===3?'You and two rivals':fsOnline?'You and a friend':'You and one opponent'}</span></div>""")
# the foot
rep("""  const side=i=>`<b style="color:${COLORS[cols[i]].ink}">${FACTIONS[facs[i]].name}</b>`;
  const mp=CUSTOM_MAPS.find(m=>m.id===fsMap&&m.players===fsNP);
  $('#fsxFoot').innerHTML=`<button data-fsx="back">${fsTab?'Back':'Title'}</button><span class="sum">${side(0)} vs ${facs.slice(1).map((f,i)=>side(i+1)).join(' and ')} · ${AI_LEVEL_NAME[lv]} · ${mp?escH(mp.name):'Random map'}</span>${fsTab<2?'<button data-fsx="next">Next</button>':''}<button class="primary fs-go" data-scr="go">Start</button>`;""",
    """  const side=i=>`<b style="color:${COLORS[cols[i]].ink}">${FACTIONS[facs[i]].name}</b>${i>0&&fsOnline?` <small>(${fsKind(i-1)==='cpu'?'computer':'a friend'})</small>`:''}`;
  const mp=CUSTOM_MAPS.find(m=>m.id===fsMap&&m.players===fsNP), cpu=facs.slice(1).some((f,i)=>fsKind(i)==='cpu');
  $('#scrFaction').classList.toggle('online',fsOnline);
  $('#fsxFoot').innerHTML=`<button data-fsx="back">${fsTab?'Back':fsOnline?'Online':'Title'}</button><span class="sum">${fsOnline?'<b class="ol-tag">Online</b> ':''}${side(0)} vs ${facs.slice(1).map((f,i)=>side(i+1)).join(' and ')}${cpu?' · '+AI_LEVEL_NAME[lv]:''} · ${mp?escH(mp.name):'Random map'}</span>${fsTab<2?'<button data-fsx="next">Next</button>':''}`
    +(fsOnline?`<button class="primary fs-go" data-fsx="create" ${NETX.busy||NETX.canWrite===false?'disabled':''}>Create game</button>`:`<button class="primary fs-go" data-scr="go">Start</button>`);""")
# the handlers
rep("""    else if(k==='back'){ if(fsTab) { fsTab--; renderFactionScreen(); } else showScreen('scrTitle'); }""",
    """    else if(k==='back'){ if(fsTab) { fsTab--; renderFactionScreen(); } else if(fsOnline){ fsLeaveOnline(); openOnline(); } else showScreen('scrTitle'); }
    else if(k==='create'){ NETX.map=(mapById(fsMap)||{}).players===fsNP?fsMap:''; NETX.cols=fsSides().cols; fsLeaveOnline(); openOnline(); netCreate(); }""")
rep("""  const foc=e.target.closest('button[data-ocol]');""",
    """  const fok=e.target.closest('button[data-okind]'); if(fok){ const [k,v]=fok.dataset.okind.split(':'); NETX.kinds[+k]=v==='cpu'?'cpu':'friend'; renderFactionScreen(); return; }
  const foc=e.target.closest('button[data-ocol]');""")
rep("""  const fnp=e.target.closest('button[data-np]'); if(fnp){ fsNP=+fnp.dataset.np===3?3:2; try{ localStorage.setItem('cc-np',String(fsNP)); }catch(_){} renderFactionScreen(); return; }""",
    """  const fnp=e.target.closest('button[data-np]'); if(fnp){ fsNP=+fnp.dataset.np===3?3:2; try{ localStorage.setItem(fsOnline?'cc-np-ol':'cc-np',String(fsNP)); }catch(_){} if(fsOnline) NETX.np=fsNP; renderFactionScreen(); return; }""")

# ---------------- creating the online game from those picks (map and colours too)
rep("""    if(np===3) newGame(NETX.pick,{online:true,np:3,opps:threeOpps(NETX.pick,NETX.opps)});
    else newGame(NETX.pick,{online:true,opp:NETX.opp});""",
    """    const map=NETX.map&&(mapById(NETX.map)||{}).players===np?NETX.map:'', cols=NETX.cols||null;
    if(np===3) newGame(NETX.pick,{online:true,np:3,opps:threeOpps(NETX.pick,NETX.opps),map,cols});
    else newGame(NETX.pick,{online:true,opp:NETX.opp,map,cols});""")
rep("""      addLog(`A new age begins: the ${FACTIONS[S.players[0].faction].name} against the ${FACTIONS[S.players[1].faction].name}. Win by taking the enemy home castle, holding ${CASTLES_TO_WIN} castles, or wiping them off the map.`);""",
    """      addLog(`A new age begins: the ${FACTIONS[S.players[0].faction].name} against the ${FACTIONS[S.players[1].faction].name}${S.mapName?' on '+S.mapName:''}. Win by taking the enemy home castle, holding ${winCastles()} castles, or wiping them off the map.`);""")
rep("""    const canon=toCanon(S,0); S=keep; useBoard(S.players.length);""",
    """    const canon=toCanon(S,0); S=keep; if(S){ useBoard(S.players.length); syncShape(true); }""")
# a device opening an online game takes a hand-made map's shape
rep("""  S=toLocal(JSON.parse(d.state),net.seat); useBoard(S.players.length);""",
    """  S=toLocal(JSON.parse(d.state),net.seat); useBoard(S.players.length); syncShape();""")

# ---------------- the Play online screen: New game opens the setup tabs
rep("""  B.innerHTML=head+msg+noWrite+`<div class="ol-colrow">${colorPicker(myColorFor(pick))}</div><div class="ol-cols">
    <section class="ol-box"><h3>New game</h3><p class="hint">${NETX.np===3?'Choose your side, the other two sides, and who plays each.':'Choose your side, and which side your friend plays.'}</p>
      <div class="ol-facs">${FACTION_ORDER.map(fid=>{const f=FACTIONS[fid]; return `<button class="ol-fac" data-ol="fac" data-fid="${fid}" aria-pressed="${fid===pick}" style="--pc:${f.ink}"><span class="fs-castle px-c-${fid}" aria-hidden="true"></span><b>${f.name}</b></button>`;}).join('')}</div>
      <div class="opick" role="group" aria-label="Players"><span class="cp-l">Players</span>${[2,3].map(n=>`<button class="op-b" data-ol="np" data-n="${n}" aria-pressed="${n===(NETX.np===3?3:2)}" style="--pc:var(--bone)">${n}</button>`).join('')}</div>
      ${NETX.np===3?seatPicker(pick):oppPicker(pick,NETX.opp,'ol')}
      <button class="primary ol-go" data-ol="create" ${NETX.busy||NETX.canWrite===false?'disabled':''}>Create game</button></section>""",
    """  B.innerHTML=head+msg+noWrite+`<div class="ol-cols">
    <section class="ol-box"><h3>New game</h3><p class="hint">Set it up like a game against the computer: your side and color, who your friend plays, then the map.</p>
      <div class="ol-last"><span class="fs-castle px-c-${pick}" aria-hidden="true"></span><span><b style="color:${FACTIONS[pick].ink}">${FACTIONS[pick].name}</b><small>${NETX.np===3?'3 players':'2 players'}</small></span></div>
      <button class="primary ol-go" data-ol="setup" ${NETX.busy||NETX.canWrite===false?'disabled':''}>${NETX.busy?'Creating…':'Set up a new game'}</button></section>""")
rep("""  else if(k==='create') netCreate();""", """  else if(k==='create') netCreate();
  else if(k==='setup') fsEnterOnline();""")

# ---------------- the look
anchor = ".fsx-lvsheet .fsx-lv button[aria-pressed=\"true\"] b{color:#f6e7bf}"
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + r"""
/* ===== Play online, themed like the setup screen (Ethan, 2026-11-23) ===== */
#scrOnline{--cz:"Cinzel","Trajan Pro","Palatino Linotype",Palatino,Georgia,serif;--brz:#6e5226;--parch:#e4d6b4;overflow:hidden;background:#0c0a07!important}
#scrOnline::before{content:"";position:absolute;inset:-14px;background:url(title_battle.jpg) center/cover no-repeat;filter:blur(2px) brightness(.62) saturate(1.1);z-index:0}
#scrOnline::after{content:"";position:absolute;inset:0;background:radial-gradient(ellipse at 50% 45%,rgba(10,8,5,.15),rgba(10,8,5,.6));z-index:0;pointer-events:none}
#scrOnline .ol-panel{position:relative;z-index:1;background:rgba(22,17,12,.72);border:2px solid var(--brz);border-radius:4px;color:#d8cba9;
  box-shadow:0 0 0 2px #120c06,inset 0 0 0 1px rgba(233,185,73,.12),inset 0 0 2.5em rgba(0,0,0,.45),0 .6em 1.6em rgba(0,0,0,.6);-webkit-backdrop-filter:blur(4px);backdrop-filter:blur(4px)}
#scrOnline .ol-head h2{font-family:var(--cz);font-weight:700;letter-spacing:.05em;color:var(--parch);text-shadow:0 1px 0 #000,0 0 .5em rgba(0,0,0,.6)}
#scrOnline h3{font-family:var(--cz);font-weight:700;letter-spacing:.04em;color:var(--parch);text-shadow:0 1px 0 #000}
#scrOnline .hint,#scrOnline .sub{color:#bfae88}
#scrOnline p{color:#cdbf9c}
#scrOnline p b{color:#f0e2bd}
#scrOnline .ol-box{background:rgba(12,9,6,.6);border:1px solid #6b4d1c;border-radius:4px}
#scrOnline .ol-note{background:rgba(12,9,6,.72);border:1px solid var(--brz);border-radius:4px;color:var(--parch)}
#scrOnline .ol-last{display:flex;align-items:center;gap:.7em}
#scrOnline .ol-last .fs-castle{display:block;width:4.2em;height:3em;background-size:contain;background-repeat:no-repeat;background-position:center bottom;flex:none}
#scrOnline .ol-last b{display:block;font-family:var(--cz);font-weight:700;letter-spacing:.03em;text-shadow:0 1px 0 #000}
#scrOnline .ol-last small{color:#bfae88}
#scrOnline .ol-game{background:linear-gradient(180deg,rgba(52,42,30,.9),rgba(24,19,13,.92));border:2px solid #4f3b1c;border-radius:4px;box-shadow:0 0 0 2px #120c06}
#scrOnline .ol-game.due{border-color:#d9b25a;box-shadow:0 0 0 2px #120c06,0 0 0 3px rgba(233,185,73,.75),0 0 .8em rgba(255,190,70,.2)}
#scrOnline .ol-gtxt b{font-family:var(--cz);font-weight:700;color:#f0dcaa}
#scrOnline .ol-gtxt small{color:#bfae88}
#scrOnline .ol-code{color:#e9c66a;text-shadow:0 1px 0 #000}
#scrOnline .ol-game.due .ol-st{color:#e9c66a}
#scrOnline button:not(.primary){font-family:var(--cz);font-weight:700;letter-spacing:.04em;color:var(--parch);background:linear-gradient(180deg,#3b3226,#1d1710);border:2px solid var(--brz);border-radius:4px;
  box-shadow:0 0 0 2px #120c06,inset 0 1px 0 rgba(255,236,190,.15),0 .25em .6em rgba(0,0,0,.5);text-shadow:0 1px 0 #000}
#scrOnline button:not(.primary):hover:not(:disabled){background:linear-gradient(180deg,#4a3f2f,#241c13)}
#scrOnline button.primary{font-family:var(--cz);font-weight:700;letter-spacing:.06em;color:#2a1805;text-shadow:0 1px 0 rgba(255,240,200,.6);
  background:linear-gradient(180deg,#fff0bd 0%,#f4cf6b 22%,#dca43a 55%,#a9721f 100%);border:2px solid #5a3a0e;border-radius:4px;
  box-shadow:0 0 0 2px #120c06,inset 0 2px 0 rgba(255,255,255,.55),inset 0 -3px 0 rgba(90,55,10,.55),0 0 1.1em rgba(255,180,60,.35),0 .35em .8em rgba(0,0,0,.6)}
#scrOnline button.primary:hover:not(:disabled){background:linear-gradient(180deg,#fff6d2 0%,#f8da80 22%,#e6b14a 55%,#b67d26 100%)}
#scrOnline button:disabled{filter:grayscale(.5) brightness(.75);cursor:default}
#scrOnline .ol-join input{background:rgba(12,9,6,.82);border:2px solid var(--brz);border-radius:4px;color:#f6e7bf;box-shadow:0 0 0 2px #120c06,inset 0 2px 6px rgba(0,0,0,.6)}
#scrOnline .ol-join input:focus{outline:none;border-color:#d9b25a}
#scrOnline .ol-bigcode{font-family:var(--cz)!important;font-weight:700;background:linear-gradient(180deg,#fff6d6 0%,#f7d77c 28%,#e0a93a 52%,#a8701c 72%,#f2c862 100%);
  -webkit-background-clip:text;background-clip:text;color:transparent;-webkit-text-stroke:.02em #2a1a06;text-shadow:none;filter:drop-shadow(0 .05em 0 #1a1005) drop-shadow(0 0 .3em rgba(0,0,0,.8))}
/* the setup screen making an online game */
#scrFaction .ol-tag{font-family:var(--cz);font-size:.8em;letter-spacing:.08em;text-transform:uppercase;color:#2a1805;background:linear-gradient(180deg,#f6e2a4,#c99a45);border-radius:3px;padding:.05em .45em;margin-right:.2em}
#scrFaction .fsx-foot .sum small{color:#bfae88;font-weight:500}
#scrFaction .fsx-kind{margin:.1em 0 .2em}
#scrFaction .fsx-rival .hint{margin:.2em 0 0}""")
open(P, 'w').write(s); print('ok')

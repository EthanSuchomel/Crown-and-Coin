"""index.html: each hand-made map's own win rules (Ethan, 2026-11-17): castles to hold (maps.json "castles"; 0 = no castle
win), the castle win on 3 players too when a map asks for it, and map events (a castle at a set hex in a set round)."""
import sys
P = sys.argv[1]; s = open(P).read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90]); s = s.replace(a, b)
rep("const CASTLES_TO_WIN=4, HOLD_TURNS=2;", """const CASTLES_TO_WIN=4, HOLD_TURNS=2;
// castles to hold to win: the map's own number, or 4 with 2 players and none with 3 (0 = no castle win)
function winCastlesFor(np,mapId){ const m=mapId?mapById(mapId):null; return m&&m.players===np&&m.castles!=null?m.castles:(np>2?0:CASTLES_TO_WIN); }
const winCastles=()=>S?winCastlesFor(S.players.length,S.map):CASTLES_TO_WIN;
const rivalsName=pid=>{ const r=S.players.filter(q=>q.id!==pid&&!q.out); return r.length===1?`The ${r[0].name}`:'Their rivals'; };""")
# the hold check, for any number of sides
rep("""  if(S.players.length>2){   // 3 players: no castle-count win; a side with no land left is out
    S.players.forEach(q=>{ if(!q.out&&!S.over&&!S.tiles.some(t=>t.owner===q.id)) knockOut(q.id,null,'wipe'); });
    return;
  }
  for(const pid of [0,1]) if(!S.tiles.some(t=>t.owner===pid)){ addLog(`${S.players[pid].name} have no land left.`,1-pid); endGame(1-pid,'wipe'); return; }
  const holder=[0,1].find(pid=>castleCount(pid)>=CASTLES_TO_WIN);
  if(S.siege&&holder!==S.siege.pid){ addLog(`${S.players[S.siege.pid].name} no longer hold ${CASTLES_TO_WIN} castles.`,1-S.siege.pid); S.siege=null; }
  if(holder!==undefined&&!S.siege){
    S.siege={pid:holder,left:HOLD_TURNS};
    addLog(`${S.players[holder].name} hold ${CASTLES_TO_WIN} castles! ${S.players[1-holder].name} have ${HOLD_TURNS} turns to take one back.`,holder);
  }""", """  const need=winCastles();
  if(S.players.length>2){   // 3 players: a side with no land left is out (and a castle win only on maps that have one)
    S.players.forEach(q=>{ if(!q.out&&!S.over&&!S.tiles.some(t=>t.owner===q.id)) knockOut(q.id,null,'wipe'); });
    if(S.over||!need) return;
  } else for(const pid of [0,1]) if(!S.tiles.some(t=>t.owner===pid)){ addLog(`${S.players[pid].name} have no land left.`,1-pid); endGame(1-pid,'wipe'); return; }
  const holder=S.players.map(q=>q.id).find(pid=>!S.players[pid].out&&castleCount(pid)>=need);
  if(S.siege&&holder!==S.siege.pid){ addLog(`${S.players[S.siege.pid].name} no longer hold ${need} castles.`,S.siege.pid); S.siege=null; }
  if(holder!==undefined&&!S.siege){
    const rivals=S.players.filter(q=>q.id!==holder&&!q.out).length;
    S.siege={pid:holder,left:HOLD_TURNS*rivals};   // every rival gets HOLD_TURNS turns to take one back
    addLog(`${S.players[holder].name} hold ${need} castles! ${rivalsName(holder)} have ${HOLD_TURNS} turns${rivals>1?' each':''} to take one back.`,holder);
  }""")
rep("if(S.siege.left<=0){ addLog(`${S.players[S.siege.pid].name} held ${CASTLES_TO_WIN} castles and win!`", "if(S.siege.left<=0){ addLog(`${S.players[S.siege.pid].name} held ${winCastles()} castles and win!`")
# map events: a castle at a set hex at the start of a set round
rep("  if(round){ S.turn++; if(S.turn===NEW_CASTLE_ROUND+1&&S.extraCastle==null) spawnCastle(); }",
    "  if(round){ S.turn++; if(S.turn===NEW_CASTLE_ROUND+1&&S.extraCastle==null) spawnCastle(); mapEvents(); }")
rep("function advanceTurn(){", """function mapEvents(){   // a hand-made map's own events (e.g. Control: a castle on the centre hex in round 20)
  const m=S.map?mapById(S.map):null; if(!m||!m.events) return;
  m.events.forEach(e=>{ if(e.round!==S.turn||!e.castle) return; const t=S.tiles[e.castle[0]*N+e.castle[1]]; if(!t||t.castle||t.terrain==='void') return;
    t.terrain='plain'; t.forest=false; t.castle=true; if(t.owner<0){ t.bounty=false; t.crate=false; }
    S.announce={kind:'castle',id:t.id}; addLog(`Round ${S.turn}: a new castle rises at the centre of the map.`); });
}
function advanceTurn(){""")
# the side panel: castles to hold
rep("""<span class="st cas" title="${S.players.length>2?'Castles held':`Castles held: hold ${CASTLES_TO_WIN} to win`}"><span class="px px-c-neutral" aria-hidden="true"></span>${cas}${S.players.length>2?'':` <small>of ${CASTLES_TO_WIN}</small>`}</span>""",
    """<span class="st cas" title="${!winCastles()?'Castles held':`Castles held: hold ${winCastles()} to win`}"><span class="px px-c-neutral" aria-hidden="true"></span>${cas}${!winCastles()?'':` <small>of ${winCastles()}</small>`}</span>""")
# the hold banner
rep("""      ?`<div class="siege mine"><span class="px px-crown" aria-hidden="true"></span> You hold ${CASTLES_TO_WIN} castles. Keep them through ${L===1?'the':'the next '+L} ${S.players[1].name} ${tw} to win.</div>`
      :`<div class="siege theirs">⚠ The ${S.players[1].name} hold ${CASTLES_TO_WIN} castles. Take one back within ${L} ${tw} of yours or they win.</div>`;""",
    """      ?`<div class="siege mine"><span class="px px-crown" aria-hidden="true"></span> You hold ${winCastles()} castles. Keep them through ${L===1?'the':'the next '+L} ${S.players.length>2?'rival':S.players[1].name} ${tw} to win.</div>`
      :`<div class="siege theirs">⚠ The ${S.players[S.siege.pid].name} hold ${winCastles()} castles. Take one back within ${S.players.length>2?L+' rival':L} ${tw}${S.players.length>2?'':' of yours'} or they win.</div>`;""")
# game over, 2 players
rep("`You held ${CASTLES_TO_WIN} castles and the ${op} couldn't take one back.`", "`You held ${winCastles()} castles and the ${op} couldn't take one back.`")
rep("`They held ${CASTLES_TO_WIN} castles and you couldn't take one back in time.`", "`They held ${winCastles()} castles and you couldn't take one back in time.`")
# game over, 3 players: a castle win
rep("""      ?`<p class="big">You rule the land <span class="px px-crown" aria-hidden="true"></span></p><p class="hint">You're the last side standing.""",
    """      ?`<p class="big">You rule the land <span class="px px-crown" aria-hidden="true"></span></p><p class="hint">${S.overWhy==='hold'?`You held ${winCastles()} castles and no rival took one back.`:`You're the last side standing.`}""")
rep("""${w?` The ${w.name} were the last side standing.`:''}</p>`)""", """${w?(S.overWhy==='hold'?` The ${w.name} held ${winCastles()} castles.`:` The ${w.name} were the last side standing.`):''}</p>`)""")
rep("""<p class="big">${me.out?'You are out':`The ${w?w.name:'enemy'} rule the land`}</p><p class="hint">${me.outWhy==='home'""",
    """<p class="big">${me.out?'You are out':`The ${w?w.name:'enemy'} rule the land`}</p><p class="hint">${!me.out&&S.overWhy==='hold'?'':me.outWhy==='home'""")
rep("""${me.outWhy==='wipe'?'You have no land left':'You were knocked out'} in round ${me.outRound||S.turn}.""", """${me.outWhy==='wipe'?'You have no land left':'You were knocked out'}${!me.out&&S.overWhy==='hold'?'':` in round ${me.outRound||S.turn}.`}""") if s.count("${me.outWhy==='wipe'?'You have no land left':'You were knocked out'} in round ${me.outRound||S.turn}.")==1 else None
# the computer: chase / stop the map's castle count
rep("else if(b.castle&&S.players.length===2&&castleCount(pid)+1>=CASTLES_TO_WIN) castleV+=150;", "else if(b.castle&&winCastles()&&castleCount(pid)+1>=winCastles()) castleV+=150;")
rep("(np===2&&ca[i]>=CASTLES_TO_WIN?250:0)", "(winCastles()&&ca[i]>=winCastles()?250:0)")
# texts: new game, new castle, help, faction screen
rep("Win by taking their home castle, holding ${CASTLES_TO_WIN} castles, or wiping them off the map.`);\n  if(!(opts", "Win by taking their home castle, holding ${winCastles()} castles, or wiping them off the map.`);\n  if(!(opts")
rep("; the first side to hold ${CASTLES_TO_WIN} of them for ${HOLD_TURNS} enemy turns wins.`}", "; the first side to hold ${winCastles()} of them for ${HOLD_TURNS} enemy turns wins.`}")
rep("""  <li><b>Hold ${CASTLES_TO_WIN} castles.</b> When a side holds ${CASTLES_TO_WIN} castles, the other side gets ${HOLD_TURNS} turns to take one of them back. If they can't, the side with ${CASTLES_TO_WIN} castles wins.""",
    """  <li><b>Hold ${winCastles()} castles.</b> When a side holds ${winCastles()} castles, the other side gets ${HOLD_TURNS} turns to take one of them back. If they can't, the side with ${winCastles()} castles wins.""")
rep("openInfo('How to play',`${S.players.length>2?WINS3_HTML:''}", "openInfo('How to play',`${S.players.length>2?WINS3_HTML+(winCastles()?`<p><b>On this map you can also win by holding ${winCastles()} castles:</b> each rival then gets ${HOLD_TURNS} turns to take one back, or you win.</p>`:''):''}")
rep("""const winListHtml=()=>fsNP===3?`<ul><li><b>Take a rival's home castle</b> and they're out; their land turns neutral.</li><li><b>Wipe a rival off the map</b> and they're out too.</li><li><b>Be the last side standing.</b></li></ul>`
  :`<ul><li><b>Take their home castle</b> and win on the spot.</li><li><b>Hold ${CASTLES_TO_WIN} castles</b> for ${HOLD_TURNS} of their turns.</li><li><b>Wipe them off the map.</b></li></ul>`;""",
    """const winListHtml=()=>{ const need=winCastlesFor(fsNP,fsMap); return fsNP===3?`<ul><li><b>Take a rival's home castle</b> and they're out; their land turns neutral.</li><li><b>Wipe a rival off the map</b> and they're out too.</li>${need?`<li><b>Hold ${need} castles</b> while each rival gets ${HOLD_TURNS} turns to take one back.</li>`:''}<li><b>Be the last side standing.</b></li></ul>`
  :`<ul><li><b>Take their home castle</b> and win on the spot.</li><li><b>Hold ${need} castles</b> for ${HOLD_TURNS} of their turns.</li><li><b>Wipe them off the map.</b></li></ul>`; };""")
a = "`You're the last side standing.`} ${S.players.filter(q=>q.id!==0).map("
if s.count(a) == 1:
    i = s.index(a); j = s.index(".join(' ')}", i) + len(".join(' ')}"); seg = s[i:j]
    s = s[:i] + "`You're the last side standing.`} ${S.overWhy==='hold'?'':" + seg[len("`You're the last side standing.`} ${"):-1] + "}" + s[j:]
open(P, 'w').write(s); print('patched; CASTLES_TO_WIN left:', s.count('CASTLES_TO_WIN'))

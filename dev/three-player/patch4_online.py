# Three-player mode, step 4: online games for 3, with any mix of people and computers (Ethan, 2026-11-09).
#   - Play online: Players 2 / 3. With 3, pick the two other factions and whether each seat is a Friend or the Computer.
#     Friends join with the code; the game starts once every friend seat is filled.
#   - Each device still sees itself as player 0 ("You"): the stored game (seat 0's view) is turned round to each seat
#     (with 2 players that's the old swap).
#   - A computer seat's turn is played on the device of the player who handed over to it (it's online at that moment), and
#     everyone else watches it update. If that device drops out part way, another player's device takes over after 45 s.
#   - Battles: two people fight live in the arena as before (the third player sees the result on the board). You against a
#     computer is fought on your screen. A computer attacking a person is run on the device playing the computer's turn,
#     with the computer leading the attackers and the defender giving orders from their own device. Computer vs computer
#     is settled on the board.
#   - A person knocked out online keeps watching; the game goes on until one side is left.
import sys
p=sys.argv[1]; s=open(p,encoding='utf8').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:100]); s=s.replace(a,b)

# ---- seats, and turning the stored game round to each device ----
rep("""let NETX={db:null,user:null,uid:null,canWrite:null,ready:false,tried:false,unsubs:[],games:{},view:'menu',pick:DEFAULT_FACTION,opp:null,msg:'',busy:false};""",
"""let NETX={db:null,user:null,uid:null,canWrite:null,ready:false,tried:false,unsubs:[],games:{},view:'menu',pick:DEFAULT_FACTION,opp:null,msg:'',busy:false,
  np:2,opps:[],kinds:['friend','cpu']};   // 3 players: the other two factions, and whether each of those seats is a friend or the computer
try{ if(localStorage.getItem('cc-np-ol')==='3') NETX.np=3; }catch(e){}
// a 3-player game: the players' accounts and devices by seat (seat 0 created it)
const seatIds=g=>[g.host,g.guest,g.guest2], seatDevs=g=>[g.hostDev,g.guestDev,g.guest2Dev];
const openSeats=g=>[1,2].filter(i=>(g.kinds||[])[i]==='friend'&&!seatIds(g)[i]);""")
rep("""function seatOf(g){
  if(g.host===NETX.uid&&g.guest===NETX.uid) return g.guestDev===DEVICE?1:g.hostDev===DEVICE?0:null;""","""function seatOf(g){
  if(g.np===3){   // this device's seat; the same account on another device can take another open seat
    const mine=[0,1,2].filter(i=>seatIds(g)[i]===NETX.uid); if(!mine.length) return null;
    const exact=mine.find(i=>seatDevs(g)[i]===DEVICE); if(exact!=null) return exact;
    return (mine.length===1&&!openSeats(g).length)?mine[0]:null;
  }
  if(g.host===NETX.uid&&g.guest===NETX.uid) return g.guestDev===DEVICE?1:g.hostDev===DEVICE?0:null;""")
rep("""function askSeat(g){
  const fh=FACTIONS[g.hostFaction], fg=FACTIONS[guestFac(g)];""","""function askSeat(g){
  if(g.np===3){ const mine=[0,1,2].filter(i=>seatIds(g)[i]===NETX.uid);
    openInfo('Which side is this device?',`<p>More than one side of game ${escH(g.code)} is played from your account. Pick the side you play on this device.</p>`,
      mine.map((i,k)=>({label:FACTIONS[(g.factions||[])[i]]?FACTIONS[g.factions[i]].name:'Seat '+(i+1),primary:k===mine.length-1,fn:()=>{ netOpen(g.code,i); renderOnline(); }}))); return; }
  const fh=FACTIONS[g.hostFaction], fg=FACTIONS[guestFac(g)];""")
rep("""function swapSides(s){
  s.players.reverse(); s.players.forEach((p,i)=>p.id=i);
  if(s.homes) s.homes.reverse();
  s.current=1-s.current; s.first=1-(s.first||0); if(s.winner!=null) s.winner=1-s.winner;
  s.tiles.forEach(t=>{ if(t.owner>=0) t.owner=1-t.owner; if(t.braced>=0) t.braced=1-t.braced; });
  if(s.siege) s.siege.pid=1-s.siege.pid;
  if(s.fight){ s.fight.att=1-s.fight.att; s.fight.def=1-s.fight.def; }
  (s.log||[]).forEach(l=>{ if(l.p>=0) l.p=1-l.p; });
  if(s.over) s.over=s.over==='win'?'lose':'win';
  return s;
}""","""// turn the game round so seat k is player 0 (k<0 turns it back); with 2 players, k=1 swaps the two sides
function rotSeats(s,k){
  const n=s.players.length; k=((k%n)+n)%n; if(!k) return s;
  const m=i=>(i!=null&&i>=0)?((i-k)%n+n)%n:i;
  s.players=s.players.slice(k).concat(s.players.slice(0,k)); s.players.forEach((p,i)=>{ p.id=i; if(p.outBy!=null) p.outBy=m(p.outBy); });
  if(s.homes) s.homes=s.homes.slice(k).concat(s.homes.slice(0,k));
  s.current=m(s.current); s.first=m(s.first||0); if(s.winner!=null) s.winner=m(s.winner); if(s.runner!=null) s.runner=m(s.runner);
  s.tiles.forEach(t=>{ if(t.owner>=0) t.owner=m(t.owner); if(t.braced>=0) t.braced=m(t.braced); });
  if(s.siege) s.siege.pid=m(s.siege.pid);
  if(s.fight){ s.fight.att=m(s.fight.att); s.fight.def=m(s.fight.def); }
  (s.log||[]).forEach(l=>{ if(l.p>=0) l.p=m(l.p); });
  if(s.over) s.over=s.winner!=null?(s.winner===0?'win':'lose'):(n===2?(s.over==='win'?'lose':'win'):'lose');
  return s;
}
const swapSides=s=>rotSeats(s,1);""")
rep("""  const s=JSON.parse(JSON.stringify(canon));
  if(seat===1) swapSides(s);
  s.players.forEach((p,i)=>{ p.ai=i!==0; p.name=i===0?'You':FACTIONS[p.faction].name; });""","""  const s=JSON.parse(JSON.stringify(canon));
  rotSeats(s,seat||0);
  s.players.forEach((p,i)=>{ p.ai=i!==0; p.name=i===0?'You':FACTIONS[p.faction].name; });""")
rep("""  const s=JSON.parse(JSON.stringify(local));
  if(seat===1) swapSides(s);
  s.players.forEach(p=>{ p.ai=false; p.name=FACTIONS[p.faction].name; });""","""  const s=JSON.parse(JSON.stringify(local));
  rotSeats(s,-(seat||0));
  s.players.forEach(p=>{ p.ai=!!p.cpu; p.name=FACTIONS[p.faction].name; });""")
rep("""  if(NET&&l.p===1){ const n=S.players[1].name;""","""  if(NET&&l.p>0&&S.players[l.p]){ const n=S.players[l.p].name;""")

# ---- who sends the board: the side whose turn it is, or the device playing a computer's turn ----
rep("""function netPush(){
  if(!NET||!S||NET.applying||!NET.entered) return;
  if(!(S.current===0||NET.lastCur===0)) return;     // only the side whose turn it is (or who just handed over) sends""",
"""// this device plays the computer's turn now (or just did, and hands over)
const netIRun=()=>!!(NET&&S&&S.runner===0&&((S.players[S.current]&&S.players[S.current].cpu)||(NET.lastCur!=null&&S.players[NET.lastCur]&&S.players[NET.lastCur].cpu)));
function netPush(){
  if(!NET||!S||NET.applying||!NET.entered) return;
  if(!(S.current===0||NET.lastCur===0||netIRun())) return;     // only the side whose turn it is (or who just handed over, or the device playing a computer's turn) sends""")
rep("""    status:canon.over?'over':'playing', winner:canon.over?(canon.over==='win'?0:1):null};""",
    """    status:canon.over?'over':'playing', winner:canon.over?(canon.winner!=null?canon.winner:(canon.over==='win'?0:1)):null};""")
rep("""  S=toLocal(JSON.parse(d.state),net.seat);
  net.rev=d.rev; net.lastJson=d.state; net.lastCur=S.current;""","""  S=toLocal(JSON.parse(d.state),net.seat); useBoard(S.players.length);
  net.rev=d.rev; net.lastJson=d.state; net.lastCur=S.current;""")
rep("""  if(S.current===0&&S.pendingBegin&&!S.over){ S.pendingBegin=false; startTurn(); }   // your turn starts on your own device
  else render();""","""  if(S.current===0&&S.pendingBegin&&!S.over){ S.pendingBegin=false; startTurn(); }   // your turn starts on your own device
  else if(first&&cur().cpu&&S.runner===0&&!S.over){ render(); setTimeout(netCpuResume,800); }   // this device was playing a computer's turn: carry on
  else render();
  if(first) netCpuWatch();""")
# other players' names, by seat
rep("""  const opp=net.seat===0?d.guest:d.host;
  if(opp&&opp!==net.oppId){ net.oppId=opp; netName(); }""","""  const opp=d.np===3?[d.host,d.guest,d.guest2].find((u,i)=>u&&u!=='cpu'&&i!==net.seat):(net.seat===0?d.guest:d.host);
  net.uids=d.np===3?[d.host,d.guest,d.guest2]:(net.seat===0?[d.host,d.guest]:[d.host,d.guest]);
  if(opp&&opp!==net.oppId){ net.oppId=opp; netName(); }
  if(d.np===3&&JSON.stringify(net.uids)!==net.uidsSeen){ net.uidsSeen=JSON.stringify(net.uids); netNames(); }""")
rep("""function netName(){""","""// 3 players: the other people's names, by seat
function netNames(){
  const net=NET; if(!net||!net.uids||!NETX.user||!NETX.user.profiles) return;
  const ids=net.uids.filter((u,i)=>u&&u!==NETX.uid&&i!==net.seat); if(!ids.length) return;
  NETX.user.profiles(ids).then(ps=>{ if(NET!==net) return; net.names=net.uids.map((u,i)=>i===net.seat?'':(u&&ps[u]&&ps[u].name)||''); if(net.entered) render(); else renderOnline(); }).catch(()=>{});
}
// the name of the person playing a side (by this device's numbering), if we know it
function netNameOf(i){ if(!NET||!S) return ''; const n=S.players.length; if(n===2) return NET.oppName||''; const cs=(i+NET.seat)%n; return (NET.names&&NET.names[cs])||''; }
function netName(){""")

# ---- turns: a computer seat's turn is played on the device that hands over to it ----
rep("""  if(NET){ S.pendingBegin=true; ui.sel=null; ui.battle=null; ui.pick=null; ui.notes=[]; ui.wallFor=null; render(); return; }   // online: the other player's turn starts on their device""",
"""  if(NET){
    ui.sel=null; ui.battle=null; ui.pick=null; ui.notes=[]; ui.wallFor=null;
    if(cur().cpu){ S.runner=0; S.pendingBegin=false; startTurn(); return; }    // a computer seat: its turn is played on this device
    if(S.current===0){ S.pendingBegin=false; startTurn(); return; }            // back to you, after the computer's turn
    S.pendingBegin=true; render(); return; }   // online: the other player's turn starts on their device""")
rep("""  if(cur().ai&&!NET) runAI();
}""","""  if(cur().ai&&(!NET||(cur().cpu&&S.runner===0))) runAI();
}""")
rep("""async function runAI(){
  if(NET) return;""","""async function runAI(){
  if(NET&&!(cur().cpu&&S.runner===0)) return;
  if(NET) NET.cpuRunning=true;""")
rep("""  ARENA_LIVE=false;
  ui.flash=[]; ui.busy=false;
  if(S.over){render();return;}
  finishTurn(pid);""","""  ARENA_LIVE=false;
  ui.flash=[]; ui.busy=false; if(NET) NET.cpuRunning=false;
  if(S.over){render();return;}
  finishTurn(pid);""")
# computer battles online: against a person it's an arena battle (run here); against another computer, on the board
rep("""function aiMv(from,to,n,lvl){ if(ARENA_LIVE&&isFight(from,to)&&!S.players[S.tiles[to].owner].ai) return""",
    """function aiMv(from,to,n,lvl){ if(ARENA_LIVE&&isFight(from,to)&&!(NET?S.players[S.tiles[to].owner].cpu:S.players[S.tiles[to].owner].ai)) return""")
rep("""      ev.res=await fightLocal(f); ev.kind='move';""","""      ev.res=(NET&&f.def!==0)?await netAiFight(f):await fightLocal(f); ev.kind='move';""")
# your attack on a computer seat online: fought on your screen alone
rep("""  if(NET){ netFightCheck(); return; }
  const r=await fightLocal(f);""","""  if(NET&&!S.players[S.tiles[to].owner].cpu){ netFightCheck(); return; }
  const r=await fightLocal(f);""")
# a dropped computer turn is taken over
rep("""async function netPresence(p){""","""// A computer's turn is played on the device of the player who handed over to it. If this device was doing that (it
// reopened the game), it carries on; if another device was and it has gone quiet for 45 s, this one takes over.
let _cpuWatch=0;
function netCpuWatch(){
  clearInterval(_cpuWatch);
  _cpuWatch=setInterval(()=>{ if(!NET||!S||S.over||!NET.entered||S.fight) return; const c=cur(); if(!c||!c.cpu||ui.busy||NET.cpuRunning) return;
    if(S.runner===0){ netCpuResume(); return; }
    const n=S.players.length, age=Date.now()-((NET.doc&&NET.doc.updated)||Date.now());
    const here=NF.room&&NF.room.peers().some(p=>!p.sameTab&&p.presence&&p.presence.seat===((S.runner==null?0:S.runner)+NET.seat)%n);
    if(age>45000&&!here) netCpuTakeover();
  },10000);
}
async function netCpuTakeover(){
  const net=NET; try{ const l=await net.ref.acquire({holder:NETX.uid+':'+DEVICE,ttlMs:30000}); if(!l||!l.acquired) return; }catch(e){ return; }
  if(NET!==net||!S||!cur().cpu||NET.cpuRunning) return;
  try{ const d=(await net.ref.get()).data(); if(d&&d.rev>net.rev){ netApply(d); return; } }catch(e){ return; }
  addLog(`The ${cur().name}' turn carries on from another player's device.`);
  netCpuResume();
}
function netCpuResume(){   // play (the rest of) a computer's turn on this device
  if(!NET||!S||S.over||!cur().cpu||NET.cpuRunning||ui.busy) return;
  S.runner=0;
  if(S.pendingBegin){ S.pendingBegin=false; startTurn(); return; }
  if(S.play){ finishTurn(S.current); return; }     // it was part way through its card: the rest of the card is skipped
  runAI();
}
async function netPresence(p){""")

# ---- online battles with 3 sides ----
rep("""const otherPeers=()=>NF.room?NF.room.peers().filter(p=>!p.sameTab&&p.presence&&p.presence.seat===1-NET.seat):[];""",
    """const otherPeers=()=>NF.room?NF.room.peers().filter(p=>!p.sameTab&&p.presence&&p.presence.seat===(NF.peerSeat!=null?NF.peerSeat:1-NET.seat)):[];""")
rep("""  const ps=otherPeers();
  const hf=ps.find(p=>p.presence.fight&&p.presence.ok&&!p.presence.end);""","""  const ps=otherPeers(), all=NF.room?NF.room.peers().filter(p=>!p.sameTab&&p.presence):[];
  const hf=all.find(p=>p.presence.fight&&p.presence.ok&&!p.presence.end);""")
rep("""arenaPost({cc:'order',team:1-arenaTeam(0),o:m.data.o}); },()=>{}));""","""arenaPost({cc:'order',team:S.fight?1-arenaTeam(S.fight.att,S.fight.def):1-arenaTeam(0),o:m.data.o}); },()=>{}));""")
rep("""  if(NF.doneFid===f.id) return;   // already over on this screen, waiting for the board to catch up
  NF.fid=f.id; NF.role=f.att===0?'host':'guest';""","""  if(NF.doneFid===f.id) return;   // already over on this screen, waiting for the board to catch up
  // only the two sides in a battle take part; with 3 players the third sees how it went on the board
  if(f.att!==0&&f.def!==0) return;
  if(f.att===0&&S.players[f.def].cpu) return;   // your attack on a computer is fought on your screen alone
  { const n=S.players.length, cs=i=>((i||0)+NET.seat)%n;   // the device on the other side: the attacker's, or the one playing the computer's turn
    NF.peerSeat=f.att===0?cs(f.def):(S.players[f.att].cpu?cs(S.runner):cs(f.att)); }
  NF.aiHost=false;
  NF.fid=f.id; NF.role=f.att===0?'host':'guest';""")
rep("""async function netFightStart(solo){
  const f=S.fight; if(!f||NF.started||f.id!==NF.fid) return;
  NF.started=true; closeModal(); FIGHT_UI={id:f.id,stage:'battle'};
  if(NF.role==='host'&&solo) netTellGuest(f,'solo');   // straight away, so the other screen doesn't join a battle that runs only here
  if(NF.role==='host'){
    const role=solo?'local':'host';
    const out=await playFight(f,role,{""","""// A computer's attack on another player, from the device playing the computer's turn: this device runs the arena and the
// computer leads the attackers; the defender gives their army its orders from their own device. Resolves with the result.
function netAiFight(f){
  return new Promise(async res=>{
    const n=S.players.length;
    NF.aiHost=true; NF.aiDone=res; NF.lastR=null; NF.fid=f.id; NF.role='host'; NF.started=false; NF.go=false; NF.setup=false; NF.lastSnap=null; NF.ended=false;
    NF.peerSeat=(f.def+NET.seat)%n;
    render();   // sends the attack, so their screen shows it
    const room=await netRoom();
    const who=netNameOf(f.def)?escH(netNameOf(f.def)):`the ${S.players[f.def].name}`;
    fightNotice(f,()=>{},{note:`Waiting for ${who} to click OK…`});
    const ok=$('#fightOk'); if(ok) ok.hidden=true; FIGHT_UI.stage='wait';
    if(!room){ fightWaiting('The live connection isn\\'t available here, so this battle is fought on this screen with the computer leading both armies.'); setTimeout(()=>netFightStart(true),1800); return; }
    await netPresence({seat:NET.seat,fight:f.id,ok:true,snap:null,end:null,loaded:null});
    netPeers();
    netFightFallback(f);
  });
}
function netFightDone(r,f){ if(NF.aiHost){ const d=NF.aiDone; NF.aiHost=false; NF.aiDone=null; if(d) d(r); } else afterYourFightNet(r,f); }
async function netFightStart(solo){
  const f=S.fight; if(!f||NF.started||f.id!==NF.fid) return;
  NF.started=true; closeModal(); FIGHT_UI={id:f.id,stage:'battle'};
  if(NF.role==='host'&&solo) netTellGuest(f,'solo');   // straight away, so the other screen doesn't join a battle that runs only here
  if(NF.role==='host'){
    const role=solo?'local':'host', tA=arenaTeam(f.att,f.def);
    const out=await playFight(f,role,{ai:NF.aiHost?(solo?[0,1]:[tA]):null,""")
rep("""        const r=finishFight(f,o); afterYourFightNet(r,f); }});
    if(!out&&!NF.ended){ NF.ended=true; if(!solo) netTellGuest(f,'board'); const r=finishFight(f,undefined); afterYourFightNet(r,f); }   // the arena didn't load: settle it on the board
    FIGHT_UI=null;""","""        const r=finishFight(f,o); if(NF.aiHost) NF.lastR=r; else afterYourFightNet(r,f); }});
    if(!out&&!NF.ended){ NF.ended=true; if(!solo) netTellGuest(f,'board'); const r=finishFight(f,undefined); if(NF.aiHost) NF.lastR=r; else afterYourFightNet(r,f); }   // the arena didn't load: settle it on the board
    FIGHT_UI=null;
    if(NF.aiHost) netFightDone(NF.lastR,f);""")
# the arena: the computer can lead the side run on this device; the title for a battle you're watching
rep("""    arenaPost({cc:'setup',role,me,ai:role==='local'?[1-me]:[],""","""    arenaPost({cc:'setup',role,me,ai:hooks.ai||(role==='local'?[1-me]:[]),""")
rep("""    const sub=(f.att===0?`Your ${FACTIONS[S.players[0].faction].name} attack the ${dn}`:`The ${an} attack your ${FACTIONS[S.players[0].faction].name}`)""",
    """    const sub=(f.att===0?`Your ${FACTIONS[S.players[0].faction].name} attack the ${dn}`:f.def===0?`The ${an} attack your ${FACTIONS[S.players[0].faction].name}`:`The ${an} attack the ${dn}`)""")
rep("""<h3 id="fightH">${f.att===0?'Attack!':'You are under attack!'}</h3>""","""<h3 id="fightH">${f.att===0?'Attack!':f.def===0?'You are under attack!':'Battle'}</h3>""")
rep("""  return (mine?`<p>You are attacking the ${dn}' ${where}.</p>`:`<p><b>The ${an} are attacking your ${where}!</b></p>`)""",
    """  return (mine?`<p>You are attacking the ${dn}' ${where}.</p>`:f.def===0?`<p><b>The ${an} are attacking your ${where}!</b></p>`:`<p>The ${an} (computer) are attacking the ${dn}' ${where}.</p>`)""")

# ---- the log names sides by faction online (each device turns "you" round for itself) ----
rep("""  const who=pid===0?'You are':`The ${p.name} are`;
  addLog(by!=null?""","""  const who=pid===0?'You are':`The ${p.name} are`;
  if(NET) addLog(`The ${FACTIONS[p.faction].name} are out of the game${by!=null?`: the ${FACTIONS[S.players[by].faction].name} took their home castle, and their land goes neutral`:': no land left'}.`);
  else addLog(by!=null?""")
rep("""      if(S.players.length>2){ addLog(`${p.name} capture ${prev===0?'your':`the ${S.players[prev].name}'`} home castle!`,p.id);""",
    """      if(S.players.length>2){ addLog(`${p.name} capture ${NET?`the ${FACTIONS[S.players[prev].faction].name}'`:prev===0?'your':`the ${S.players[prev].name}'`} home castle!`,p.id);""")

# ---- the header and the panel online ----
rep("""${c.ai?(NET?(NET.oppName?escH(NET.oppName)+"'s move":'Their move'):""","""${S.players[0].out&&!S.over?'You are out, watching · ':''}${c.ai?(NET?(c.cpu?c.name+' (computer) are playing':netNameOf(c.id)?escH(netNameOf(c.id))+"'s move":'Their move'):""")
rep("""(NET?`<p class="hint"><b style="color:${inkOf(p)}">${NET.oppName?escH(NET.oppName):'Your opponent'}</b> (the ${p.name}) is taking their turn. Their moves show up here as they make them.</p>`""",
    """(NET?(p.cpu?`<p class="hint">The <b style="color:${inkOf(p)}">${p.name}</b> (computer) are taking their turn. Their moves show up here as they make them.</p>`:`<p class="hint"><b style="color:${inkOf(p)}">${netNameOf(p.id)?escH(netNameOf(p.id)):'Your opponent'}</b> (the ${p.name}) is taking their turn. Their moves show up here as they make them.</p>`)""")

# ---- Play online: 2 or 3 players ----
rep("""  for(const f of ['host','guest']){""","""  for(const f of ['host','guest','guest2']){""")
rep("""      NETX.games={...(NETX.g_host||{}),...(NETX.g_guest||{})};""","""      NETX.games={...(NETX.g_host||{}),...(NETX.g_guest||{}),...(NETX.g_guest2||{})};""")
rep("""function gameLine(g){
  const seat=seatOf(g)??0, mine=g.cur===seat;""","""function gameLine(g){
  if(g.np===3) return gameLine3(g);
  const seat=seatOf(g)??0, mine=g.cur===seat;""")
rep("""function renderOnline(){""","""function gameLine3(g){
  const seat=seatOf(g)??[0,1,2].find(i=>seatIds(g)[i]===NETX.uid)??0, mine=g.cur===seat, F=g.factions||[], K=g.kinds||[];
  const myF=F[seat], others=[0,1,2].filter(i=>i!==seat).map(i=>`the ${FACTIONS[F[i]]?FACTIONS[F[i]].name:'?'}${K[i]==='cpu'?' (computer)':''}`).join(' and ');
  const wait=openSeats(g).length;
  const st=g.status==='waiting'?`Waiting for ${wait} more player${wait>1?'s':''}`:g.status==='over'?(g.winner===seat?'You won':'You lost'):mine?'Your turn':'Their turn';
  return `<li class="ol-game${g.status==='playing'&&mine?' due':''}"><span class="ol-code">${escH(g.code)}</span>
    <span class="ol-gtxt"><b><span class="px px-c-${myF}" aria-hidden="true"></span> You play the ${FACTIONS[myF]?FACTIONS[myF].name:'?'}</b><small>3 players: vs ${others} · ${g.status==='playing'?'Turn '+(g.turn||1)+' · ':''}<span class="ol-st">${st}</span></small></span>
    <span class="ol-gbtns"><button data-ol="open" data-code="${escH(g.code)}" class="${g.status==='playing'&&mine?'primary':''}">${g.status==='waiting'&&seat===0?'Show code':'Open'}</button>${g.status!=='playing'?`<button class="ghost" data-ol="del" data-code="${escH(g.code)}" aria-label="Remove game ${escH(g.code)}">Remove</button>`:''}</span></li>`;
}
// 3 players: the other two factions (pick 2) and who plays each seat
function seatPicker(pick){
  const o=threeOpps(pick,NETX.opps);
  return `<div class="opick" role="group" aria-label="Opponents"><span class="cp-l">Other sides (pick 2)</span>${FACTION_ORDER.filter(f=>f!==pick).map(f=>`<button class="op-b" data-ol="opp3" data-fid="${f}" aria-pressed="${o.includes(f)}" style="--pc:${FACTIONS[f].ink}"><span class="px px-c-${f}" aria-hidden="true"></span>${FACTIONS[f].name}</button>`).join('')}</div>`
    +o.map((f,i)=>`<div class="opick ol-seat" role="group" aria-label="Who plays the ${FACTIONS[f].name}"><span class="cp-l"><span class="px px-c-${f}" aria-hidden="true"></span> ${FACTIONS[f].name}</span>${[['friend','A friend'],['cpu','The computer']].map(([k,l])=>`<button class="op-b" data-ol="kind" data-i="${i}" data-k="${k}" aria-pressed="${NETX.kinds[i]===k}" style="--pc:var(--bone)">${l}</button>`).join('')}</div>`).join('');
}
function renderOnline(){""")
rep("""    B.innerHTML=head+msg+`<div class="ol-wait"><p class="sub">Your game code</p><p class="ol-bigcode" aria-label="Game code ${code.split('').join(' ')}">${code}</p>
      <p>Send your friend the link to this game and this code. They tap <b>Play online</b>, enter the code, and the game starts. You move first.</p>""",
"""    const d3=NET.doc&&NET.doc.np===3?NET.doc:null, left=d3?openSeats(d3).length:1;
    B.innerHTML=head+msg+`<div class="ol-wait"><p class="sub">Your game code</p><p class="ol-bigcode" aria-label="Game code ${code.split('').join(' ')}">${code}</p>
      ${d3&&NET.seat!==0?`<p>You're in. Waiting for ${left} more player${left>1?'s':''} to join; the game starts once everyone's in.</p>`:d3?`<p>Send your friend${left>1?'s':''} the link to this game and this code. They tap <b>Play online</b>, enter the code, and the game starts once everyone's in (${left} still to join). You move first.</p>`
        :`<p>Send your friend the link to this game and this code. They tap <b>Play online</b>, enter the code, and the game starts. You move first.</p>`}""")
rep("""      ${oppPicker(pick,NETX.opp,'ol')}""","""      <div class="opick" role="group" aria-label="Players"><span class="cp-l">Players</span>${[2,3].map(n=>`<button class="op-b" data-ol="np" data-n="${n}" aria-pressed="${n===(NETX.np===3?3:2)}" style="--pc:var(--bone)">${n}</button>`).join('')}</div>
      ${NETX.np===3?seatPicker(pick):oppPicker(pick,NETX.opp,'ol')}""")
rep("""    const keep=S;
    newGame(NETX.pick,{online:true,opp:NETX.opp});
    S.first=0; S.pendingBegin=true;
    S.log=[]; addLog(`A new age begins: the ${FACTIONS[S.players[0].faction].name} against the ${FACTIONS[S.players[1].faction].name}. Win by taking the enemy home castle, holding ${CASTLES_TO_WIN} castles, or wiping them off the map.`);
    if(SECOND_PLAYER_GOLD) addLog(`The ${FACTIONS[S.players[1].faction].name} start with ${SECOND_PLAYER_GOLD} extra gold to offset moving second.`);
    const canon=toCanon(S,0); S=keep;
    const now=Date.now();
    await ref.set({code,host:NETX.uid,hostDev:DEVICE,guest:null,guestDev:null,hostFaction:NETX.pick,guestFaction:canon.players[1].faction,status:'waiting',rev:1,state:JSON.stringify(canon),cur:0,turn:1,winner:null,created:now,updated:now});
    NETX.view='wait'; netOpen(code,0);""","""    const keep=S, np=NETX.np===3?3:2, kinds=['me',...NETX.kinds];
    if(np===3) newGame(NETX.pick,{online:true,np:3,opps:threeOpps(NETX.pick,NETX.opps)});
    else newGame(NETX.pick,{online:true,opp:NETX.opp});
    S.first=0; S.pendingBegin=true;
    S.log=[];
    if(np===3){
      S.players.forEach((q,i)=>{ if(i>0&&kinds[i]==='cpu'){ q.cpu=true; q.diff=prefLevel; } });
      const nm=i=>`the ${FACTIONS[S.players[i].faction].name}${kinds[i]==='cpu'?' (computer)':''}`;
      addLog(`A new age begins: the ${FACTIONS[S.players[0].faction].name}, ${nm(1)} and ${nm(2)}. Take a side's home castle, or wipe them off the map, and they're out. The last side standing wins.`);
      for(let i=1;i<3;i++){ const q=S.players[i], my=q.faction==='mythical'; addLog(`The ${FACTIONS[q.faction].name} start with ${catchUp(i,my?MYTH.secondMagic:SECOND_PLAYER_GOLD,3)} extra ${my?'magic':'gold'} to offset moving ${i===1?'second':'third'}.`); }
    } else {
      addLog(`A new age begins: the ${FACTIONS[S.players[0].faction].name} against the ${FACTIONS[S.players[1].faction].name}. Win by taking the enemy home castle, holding ${CASTLES_TO_WIN} castles, or wiping them off the map.`);
      if(SECOND_PLAYER_GOLD) addLog(`The ${FACTIONS[S.players[1].faction].name} start with ${SECOND_PLAYER_GOLD} extra gold to offset moving second.`);
    }
    const canon=toCanon(S,0); S=keep; useBoard(S.players.length);
    const now=Date.now(), friends=np===3?kinds.filter(k=>k==='friend').length:1;
    const doc={code,host:NETX.uid,hostDev:DEVICE,guest:null,guestDev:null,hostFaction:NETX.pick,guestFaction:canon.players[1].faction,status:friends?'waiting':'playing',rev:1,state:JSON.stringify(canon),cur:0,turn:1,winner:null,created:now,updated:now};
    if(np===3) Object.assign(doc,{np:3,guest2:null,guest2Dev:null,factions:canon.players.map(q=>q.faction),kinds});
    await ref.set(doc);
    NETX.view=friends?'wait':'menu'; netOpen(code,0);""")
rep("""      let d=snap.data();
      const sameAcct=d.host===NETX.uid&&!d.guest&&d.hostDev!==DEVICE;""","""      let d=snap.data();
      if(d.np===3){ await netJoin3(ref,d,code); NETX.busy=false; renderOnline(); return; }
      const sameAcct=d.host===NETX.uid&&!d.guest&&d.hostDev!==DEVICE;""")
rep("""async function netDelete(code){""","""// joining a 3-player game: back to your seat if you have one here, or the first open friend seat
async function netJoin3(ref,d,code){
  const s=seatOf(d);
  if(s!=null){ NETX.view=(d.status==='waiting'&&s===0)?'wait':'menu'; netOpen(code,s); return; }
  if(!openSeats(d).length){ if(seatIds(d).includes(NETX.uid)) askSeat(d); else NETX.msg=`Game ${code} already has all its players.`; return; }
  const lease=await ref.acquire({holder:NETX.uid,ttlMs:5000});
  if(!lease.acquired){ NETX.msg='Someone else is joining that game right now. Try again in a few seconds.'; return; }
  d=(await ref.get()).data(); const open=openSeats(d);
  if(!open.length){ NETX.msg=`Game ${code} already has all its players.`; return; }
  const i=open[0], k=i===1?'guest':'guest2', up={[k]:NETX.uid,[k+'Dev']:DEVICE,updated:Date.now()};
  if(open.length===1){ up.status='playing'; up.rev=(d.rev||1)+1; }   // the last seat filled: the game starts on everyone's screen
  await ref.update(up); NETX.code=''; netOpen(code,i);
}
async function netDelete(code){""")
rep("""  else if(k==='opp'){ NETX.opp=b.dataset.fid; renderOnline(); }""","""  else if(k==='opp'){ NETX.opp=b.dataset.fid; renderOnline(); }
  else if(k==='np'){ NETX.np=+b.dataset.n===3?3:2; try{ localStorage.setItem('cc-np-ol',String(NETX.np)); }catch(_){} renderOnline(); }
  else if(k==='opp3'){ const f=b.dataset.fid, c3=threeOpps(NETX.pick,NETX.opps); NETX.opps=c3.includes(f)?c3:[c3[1],f]; renderOnline(); }
  else if(k==='kind'){ NETX.kinds[+b.dataset.i]=b.dataset.k==='cpu'?'cpu':'friend'; renderOnline(); }""")

# a friend who joined a 3-player game that's still filling up: no second "waiting" line, and no button that deletes everyone's game
rep("""      <p class="hint">Waiting for them to join… You can leave this screen. The game will be under <b>Your games</b>.</p>
      <div class="btns"><button data-ol="menu">Back to Play online</button><button data-ol="del" data-code="${code}">Cancel this game</button></div></div>`;""",
"""      <p class="hint">${d3&&NET.seat!==0?'You can leave this screen; the game is under <b>Your games</b>.':'Waiting for them to join… You can leave this screen. The game will be under <b>Your games</b>.'}</p>
      <div class="btns"><button data-ol="menu">Back to Play online</button>${NET.seat===0?`<button data-ol="del" data-code="${code}">Cancel this game</button>`:''}</div></div>`;""")
rep("""<p class="hint">Choose your side, and which side your friend plays.</p>""","""<p class="hint">${NETX.np===3?'Choose your side, the other two sides, and who plays each.':'Choose your side, and which side your friend plays.'}</p>""")
open(p,'w',encoding='utf8').write(s); print('patch4 ok')

# Three-player mode, step 3: the computer plays a 3-way game (Ethan, 2026-11-09).
# Everywhere the computer looked at "the enemy" (their land, their home castle, their threat, their score) it now looks at
# every rival still in the game. A rival's home castle is worth 2500 to take with 3 sides (it knocks them out) and 1e4 with 2
# (it wins). In its scoring, what a rival has counts 0.6x per rival when there are two of them, so it doesn't spend
# everything hurting one side while the third grows. With 2 players everything works out exactly as before.
import sys
p=sys.argv[1]; s=open(p,encoding='utf8').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:100]); s=s.replace(a,b)

rep("""function enemyNear(i,pid,radius){""","""// the sides still in the game other than pid, their home castles, and whether a hex is theirs
const foesOf=pid=>S.players.filter(q=>q.id!==pid&&!q.out).map(q=>q.id);
const foeHomes=pid=>foesOf(pid).map(e=>S.homes[e]);
const foeTiles=pid=>S.tiles.filter(t=>t.owner>=0&&t.owner!==pid).map(t=>t.id);
function enemyNear(i,pid,radius){""")
# the Mythical computer
rep("""  const p=S.players[pid], ids=[], own=S.tiles.filter(t=>t.owner===pid), eid=1-pid;
  const dE=bfs(S.tiles.filter(t=>t.owner===eid).map(t=>t.id)), dist=t=>fin(dE[t.id]);""",
"""  const p=S.players[pid], ids=[], own=S.tiles.filter(t=>t.owner===pid);
  const dE=bfs(foeTiles(pid)), dist=t=>fin(dE[t.id]);""")
# building plans
rep("""  const eid=1-pid, own=S.tiles.filter(t=>t.owner===pid&&t.terrain==='plain');""","""  const own=S.tiles.filter(t=>t.owner===pid&&t.terrain==='plain');""")
rep("""    const dEHome=bfs([S.homes[eid]]);
    const c=own.filter(t=>!t.wh&&bCount(t)<bMax()""","""    const dEHome=bfs(foeHomes(pid));
    const c=own.filter(t=>!t.wh&&bCount(t)<bMax()""")
rep("""    const dEnemy=bfs(S.tiles.filter(t=>t.owner===eid).map(t=>t.id));""","""    const dEnemy=bfs(foeTiles(pid));""")
rep("""    const dEHome=bfs([S.homes[eid]]);
    const c=own.filter(t=>!t.castle&&bCount(t)<bMax())""","""    const dEHome=bfs(foeHomes(pid));
    const c=own.filter(t=>!t.castle&&bCount(t)<bMax())""")
rep("""  opts=opts||{}; const p=S.players[pid], eid=1-pid, lvl=opts.lvl||0, gold=p.gold-(opts.keep||0);""",
    """  opts=opts||{}; const p=S.players[pid], lvl=opts.lvl||0, gold=p.gold-(opts.keep||0);""")
rep("""  const dEn=bfs(S.tiles.filter(t=>t.owner===eid).map(t=>t.id)), dE=t=>fin(dEn[t.id]);""","""  const dEn=bfs(foeTiles(pid)), dE=t=>fin(dEn[t.id]);""")
# recruiting where the rivals are
rep("""  const p=S.players[pid], eid=1-pid, own=S.tiles.filter(t=>t.owner===pid), sites=own.filter(t=>canRecruit(t)||canTrain(t));""",
    """  const p=S.players[pid], own=S.tiles.filter(t=>t.owner===pid), sites=own.filter(t=>canRecruit(t)||canTrain(t));""")
rep("""  const home=S.tiles[S.homes[pid]], dEHome=bfs([S.homes[eid]]);""","""  const home=S.tiles[S.homes[pid]], dEHome=bfs(foeHomes(pid));""")
# a wall on the home castle's side facing the nearest rival home
rep("""    const h=S.tiles[S.homes[pid]], dEH=bfs([S.homes[1-pid]]);""","""    const h=S.tiles[S.homes[pid]], dEH=bfs(foeHomes(pid));""")
# scoring a move
rep("""  const eid=1-pid, prog=D(s.id)-D(b.id), sel=pickUnits(s,n,claim&&n===1), st=armyGold(sel)/3, adv=prog>0?prog*0.4*st:0;
  let castleV=b.castle?(S.homes[eid]===b.id?1e4:45):0;                             // their home castle wins the game outright
  if(castleV<1e4&&b.castle&&b.owner===eid&&S.siege&&S.siege.pid===eid) castleV=3000;          // breaks their hold: must try
  else if(b.castle&&castleCount(pid)+1>=CASTLES_TO_WIN) castleV+=150;             // gets us to the winning count""",
"""  const foe=b.owner>=0&&b.owner!==pid, prog=D(s.id)-D(b.id), sel=pickUnits(s,n,claim&&n===1), st=armyGold(sel)/3, adv=prog>0?prog*0.4*st:0;
  const theirHome=b.castle&&foe&&S.homes[b.owner]===b.id;
  let castleV=b.castle?(theirHome?(foesOf(pid).length>1?2500:1e4):45):0;            // a rival's home castle: wins the game (2 sides) or knocks them out (3)
  if(castleV<1e4&&b.castle&&foe&&S.siege&&S.siege.pid===b.owner) castleV=3000;          // breaks their hold: must try
  else if(b.castle&&S.players.length===2&&castleCount(pid)+1>=CASTLES_TO_WIN) castleV+=150;             // gets us to the winning count""")
rep("""  if(b.troops===0&&!W&&!homeGuards(b)) return 4+castleV+coinV+(b.owner===eid?3:0)+adv-(n>1&&prog<=0?2:0);""",
    """  if(b.troops===0&&!W&&!homeGuards(b)) return 4+castleV+coinV+(foe?3:0)+adv-(n>1&&prog<=0?2:0);""")
# how good the board looks
rep("""  const tr=[0,0],tl=[0,0],ca=[0,0],xv=[0,0];""","""  const np=S.players.length, tr=Array(np).fill(0),tl=Array(np).fill(0),ca=Array(np).fill(0),xv=Array(np).fill(0), foes=foesOf(pid), fw=foes.length>1?0.6:1;""")
rep("""  const W=aiProf(pid).ev||{}; for(const i of [0,1]){const s=i===pid?1:-1; V+=s*((W.tr||3)*tr[i]+1.5*tl[i]+(W.ca||40)*ca[i]+(ca[i]>=CASTLES_TO_WIN?250:0)+""",
    """  const W=aiProf(pid).ev||{}; for(const i of [pid,...foes]){const s=i===pid?1:-fw; V+=s*((W.tr||3)*tr[i]+1.5*tl[i]+(W.ca||40)*ca[i]+(np===2&&ca[i]>=CASTLES_TO_WIN?250:0)+""")
rep("""  V-=(W.ex||1)*exposure(pid); V+=(W.ex2||0.3)*exposure(1-pid);""","""  V-=(W.ex||1)*exposure(pid); for(const e of foes) V+=(W.ex2||0.3)*exposure(e)/foes.length;""")
open(p,'w',encoding='utf8').write(s); print('patch3 ok')

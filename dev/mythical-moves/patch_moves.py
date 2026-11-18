"""index.html: Mythical movement (Ethan, 2026-11-17): "the mage can only move one hex per action", "only mages can capture
castles and the areas that minions move to are not captured hexes. Everything but minions can capture hexes but only mages
can capture castles."
- Mages: 1 hex per move (also no 2-hex moves through your own land, and 1 hex in a Fortify regroup).
- Minions: still 2 hexes, but only onto your own land; a move into new land or an attack needs a unit that isn't a Minion,
  and a castle needs a Mage (except an enemy Floating Castle, which only flyers can attack). Minions can go along."""
import sys
P = sys.argv[1]; s = open(P).read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90]); s = s.replace(a, b)
rep("const fastUnit=k=>k==='minion'||isMage(k);         // Mages and Minions move 2 hexes anywhere",
    """const fastUnit=k=>k==='minion';                     // Minions move 2 hexes (onto your own land); Mages 1 (Ethan, 2026-11-17)
// what a Mythical move into hex b needs: a Mage for a castle, any unit but a Minion for other land; nothing on your own land
// (an enemy Floating Castle only takes flyers, so no Mage is asked for there)
const mythNeed=(pid,b)=>!isMyth(pid)||b.owner===pid?null:b.castle?(b.owner>=0&&isFloating(b)?null:'mage'):'land';
const mythHas=(need,army)=>!need||Object.keys(army||{}).some(k=>(army[k]|0)>0&&(need==='mage'?isMage(k):k!=='minion'));""")
rep("""  const air=B.owner>=0&&B.owner!==pid&&isFloating(B), far=isMyth(pid)&&!moveTargetsCore(from,lvl||0,false).includes(to);
  if(air&&far) return ()=>false;
  if(air) return k=>!!UNIT_STATS[k].air;
  if(far) return fastUnit;
  return null;""", """  const air=B.owner>=0&&B.owner!==pid&&isFloating(B), far=isMyth(pid)&&!regrouping()&&!moveTargetsCore(from,lvl||0,false).includes(to);
  if(air&&far) return ()=>false;
  const noMage=isMyth(pid)&&man(from,to)>1;   // Mages go 1 hex a move
  if(air) return noMage?(k=>!!UNIT_STATS[k].air&&!isMage(k)):(k=>!!UNIT_STATS[k].air);
  if(far) return fastUnit;
  if(noMage) return k=>!isMage(k);
  return null;""")
rep("""'<br>Only Mages and Minions can go this far in one move.'; }""", """(isMyth(S.tiles[from].owner)&&!moveTargetsCore(from,curLvl(),false).includes(to)?'<br>Only Minions can go this far in one move, and only onto your own land.':'<br>Mages move 1 hex at a time, so they stay behind.'); }""")
# targets: Minions' long moves only onto your own land; new land needs a non-Minion, a castle a Mage
rep("""  return [...new Set(moveTargetsCore(from,lvl,far).concat(ext))].filter(i=>!co||(S.tiles[i].owner>=0&&S.tiles[i].owner!==pid)).filter(i=>{ const f=moveFilter(from,i,lvl); return !f||Object.keys(t.ready||{}).some(k=>t.ready[k]>0&&f(k)); });""",
    """  const near=far?new Set(moveTargetsCore(from,lvl,false)):null;
  return [...new Set(moveTargetsCore(from,lvl,far).concat(ext))].filter(i=>!co||(S.tiles[i].owner>=0&&S.tiles[i].owner!==pid)).filter(i=>!near||near.has(i)||S.tiles[i].owner===pid).filter(i=>{ const f=moveFilter(from,i,lvl), r={}; for(const k in (t.ready||{})) if(t.ready[k]>0&&(!f||f(k))) r[k]=t.ready[k]; return cnt(r)>0&&mythHas(mythNeed(pid,S.tiles[i]),r); });""")
# the move itself: a group that lacks what it needs takes one along (the computer picks strongest-first), or doesn't go
rep("""  mageTrim(A,B,sel);
  if(!cnt(sel)) return {from,to,n:0,sent:{},kind:'none',att:A.owner};""", """  { const need=mythNeed(A.owner,B);   // Mythical: a castle needs a Mage, new land a unit that isn't a Minion
    if(need&&!mythHas(need,sel)){ const fl=moveFilter(from,to,lvl||0), k=byStrength(A.ready||{}).find(x=>(A.ready[x]|0)>(sel[x]|0)&&(!fl||fl(x))&&(need==='mage'?isMage(x):x!=='minion'));
      if(k) sel[k]=(sel[k]|0)+1; else return {from,to,n:0,sent:{},kind:'none',att:A.owner}; } }
  mageTrim(A,B,sel);
  if(!cnt(sel)||!mythHas(mythNeed(A.owner,B),sel)) return {from,to,n:0,sent:{},kind:'none',att:A.owner};""")
# the unit picker: say what's needed and keep the button off until it's there
rep("""  const upd=()=>{ const n=cnt(pick); $('#mvsel').disabled=!n; $('#mvsel').textContent=`${verb} ${n||''} picked`.replace('  ',' '); };""",
    """  const mneed=mythNeed(s.owner,b);
  if(mneed) $('.mvsheet p').insertAdjacentHTML('beforeend',mneed==='mage'?'<br><b>Only Mages can take a castle:</b> send at least one Mage.':'<br><b>Minions can\\'t take land:</b> send at least one unit that isn\\'t a Minion.');
  const upd=()=>{ const n=cnt(pick), ok=mythHas(mneed,pick); $('#mvsel').disabled=!n||!ok; $('#mvsel').textContent=`${verb} ${n||''} picked`.replace('  ',' '); };""")
# texts
rep("if(a==='move') return `Make up to ${movesLimit(pid)} moves. Mages and Minions go up to 2 hexes anywhere; other units 1 hex into new land or an attack, or 2 through your own land. Only flyers can attack a Floating Castle`;",
    "if(a==='move') return `Make up to ${movesLimit(pid)} moves. Mages go 1 hex. Minions go up to 2 hexes but only onto your own land: they can't take land, so new land needs another unit with them, and only Mages take castles. Other units go 1 hex into new land or an attack, or 2 through your own land. Only flyers can attack a Floating Castle`;")
rep("<li>Mages and Minions move 2 hexes anywhere, and a Move action has 3 moves.</li></ul>",
    "<li>A Move action has 3 moves. Mages move 1 hex; Minions move 2 but only onto your own land.</li><li>Only Mages capture castles. Minions can't take land on their own; every other unit can.</li></ul>")
rep("minion:'Cheap and many. The only Mythical unit that captures castles. Mages turn Minions into bigger units',",
    "minion:'Cheap and many. Moves 2 hexes but only onto your own land: it can\\'t take land or castles on its own. Mages turn Minions into bigger units',")
open(P, 'w').write(s); print('patched')

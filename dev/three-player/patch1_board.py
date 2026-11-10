# Three-player mode, step 1: the board size becomes a setting of each game (Ethan, 2026-11-09).
#   2 players: the 8 x 8 board with 3 hexes cut at each corner (52 hexes), unchanged.
#   3 players: an 11 x 11 grid cut down to a hexagon of radius 5, less its six corner hexes and the two edge hexes beside
#   each of the three corners between the home castles: 79 hexes, about 1.5x as many. The cut turns with the board, so
#   every home castle has the same shape around it; the homes are 8 hexes apart and 4 from the centre.
#   Terrain on the 3-player board: 10 mountains, 4 water and 26 bonus coins (twice the 2-player board's 5, 2 and about 13),
#   6 neutral castles, 15 forests and 15 ferns. Castles, coins, mountains and water are placed so all three seats get the same.
import sys,json,os
p=sys.argv[1]; s=open(p,encoding='utf8').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:100]); s=s.replace(a,b)
B3=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'board3.json')))
N3=B3['N']; void3=[divmod(i,N3) for i in B3['void']]
HOMES3=[78,16,86]   # you lower left, then the right-hand home, then the upper left
assert sorted(HOMES3)==sorted(B3['homes'])

rep("""const N=8, C=32;                 // 8 x 8 = 64 hexes
const HR=18, HH=HR*Math.sqrt(3), HM=2;        // hex radius (centre to corner), hex height, board margin
const GRID_W=2*HM+HR*(1.5*(N-1)+2), GRID_H=2*HM+HH*(N+.5);
// The board is drawn turned a quarter (flipped across its diagonal), so it is wider than tall and the hexes stand points-up.
// Your corner stays lower left and the opponent's upper right.
const BOARD_W=GRID_H, BOARD_H=GRID_W;
const toBoard=([x,y])=>[GRID_H-y, GRID_W-x];
// the part of the board that is drawn: the hexes plus a hair of margin for their outlines
const VB_M=HM-1.4, VB_W=BOARD_W-2*VB_M, VB_H=BOARD_H-2*VB_M, MAP_SHARE=.66;""",
"""const C=32;
const HR=18, HH=HR*Math.sqrt(3), HM=2;        // hex radius (centre to corner), hex height, board margin
// ---- the boards: each game uses one (useBoard sets the values below) ----
// 2 players: 8 x 8, with 3 hexes left out at each corner (52 to play on); the cut is the same at opposite corners so neither side gains.
// 3 players: 11 x 11 cut to a hexagon of radius 5, less its 6 corner hexes and the 2 edge hexes beside each of the 3 corners
// between the home castles (79 to play on, about 1.5x as many). The cut turns with the board, so every home castle has the
// same shape around it; the homes are 8 hexes apart. Twice the 2-player board's mountains, water and bonus coins.
const BOARDS={
  2:{n:8, voids:[[0,0],[0,1],[1,0], [0,7],[0,6],[1,7], [7,0],[7,1],[6,0], [7,7],[7,6],[6,7]], homes:[[6,2],[1,5]],
     mountains:5, waters:2, castles:3, forests:10, ferns:10, coins:0},     // coins 0: a third of the open hexes
  3:{n:"""+str(N3)+""", voids:"""+json.dumps([list(x) for x in void3]).replace(' ','')+""", homes:"""+json.dumps([list(divmod(h,N3)) for h in HOMES3]).replace(' ','')+""",
     center:[5,5], mountains:10, waters:4, castles:6, forests:15, ferns:15, coins:26},
};
let N, GRID_W, GRID_H, BOARD_W, BOARD_H, VB_X, VB_Y, VB_W, VB_H, VOID, HOMES, MOUNTAINS, WATERS, NEUTRAL_CASTLES, FORESTS, FERNS, COINS, BOARD_NP=0;
const VB_M=HM-1.4, MAP_SHARE=.66;
// The board is drawn turned a quarter (flipped across its diagonal), so it is wider than tall and the hexes stand points-up.
// Your corner stays lower left; on the 2-player board the opponent's is upper right.
const toBoard=([x,y])=>[GRID_H-y, GRID_W-x];
function useBoard(np){
  np=np===3?3:2; if(BOARD_NP===np) return;
  const b=BOARDS[np]; BOARD_NP=np; N=b.n;
  GRID_W=2*HM+HR*(1.5*(N-1)+2); GRID_H=2*HM+HH*(N+.5);
  BOARD_W=GRID_H; BOARD_H=GRID_W;
  VOID=new Set(b.voids.map(([r,c])=>r*N+c)); HOMES=b.homes.map(([r,c])=>r*N+c);
  MOUNTAINS=b.mountains; WATERS=b.waters; NEUTRAL_CASTLES=b.castles; FORESTS=b.forests; FERNS=b.ferns; COINS=b.coins;
  // the part of the board that is drawn: the hexes plus a hair of margin for their outlines
  if(np===2){ VB_X=VB_M; VB_Y=VB_M; VB_W=BOARD_W-2*VB_M; VB_H=BOARD_H-2*VB_M; }
  else {   // the 3-player hexagon leaves the grid's corners empty: frame just the hexes
    let x0=1e9,x1=-1e9,y0=1e9,y1=-1e9;
    for(let i=0;i<N*N;i++){ if(VOID.has(i)) continue; const r=Math.floor(i/N), c=i%N, gx=HM+HR+c*1.5*HR, gy=HM+HH/2+r*HH+(c&1)*HH/2, [x,y]=toBoard([gx,gy]);
      x0=Math.min(x0,x-HH/2); x1=Math.max(x1,x+HH/2); y0=Math.min(y0,y-HR); y1=Math.max(y1,y+HR); }
    const m=HM-VB_M; VB_X=x0-m; VB_Y=y0-m; VB_W=x1-x0+2*m; VB_H=y1-y0+2*m;
  }
  try{ _mapReady=false; }catch(e){}   // the board's outline is drawn again for the new size
  try{ if(typeof fitStage==='function'&&document.getElementById('stage')) fitStage(); }catch(e){}
}
useBoard(2);""")
rep("""// 12 edge hexes are left out (3 at each corner), leaving 52 to play on; the cut is the same at opposite corners so neither side gains
const VOID=new Set([[0,0],[0,1],[1,0], [0,7],[0,6],[1,7], [7,0],[7,1],[6,0], [7,7],[7,6],[6,7]].map(([r,c])=>r*N+c));
const MOUNTAINS=5, WATERS=2, NEUTRAL_CASTLES=3, FORESTS=10, FERNS=10;
""","")
rep("""const HOMES=[6*N+2, 1*N+5];                    // You: lower left, Opponent: upper right; each one ring in from the edge, 6 hexes apart
""","")
# the zoomed view keeps to the drawn part of the board
rep("""  if(id==null) return [VB_M,VB_M,VB_W,VB_H];""","""  if(id==null) return [VB_X,VB_Y,VB_W,VB_H];""")
rep("""  let x0=Math.min(Math.max(cx-w/2,VB_M),VB_M+VB_W-w), y0=Math.min(Math.max(cy-h*.56,VB_M),VB_M+VB_H-h);""",
    """  let x0=Math.min(Math.max(cx-w/2,VB_X),VB_X+VB_W-w), y0=Math.min(Math.max(cy-h*.56,VB_Y),VB_Y+VB_H-h);""")

# ---- map generation: any number of home castles ----
rep("""function genMap(){
  for(let tries=0;tries<2000;tries++){""","""// the 3-player board turned a third of the way round its centre: the hex that stands where i would (-1 off the grid)
function rot3(i){ const b=BOARDS[3], c0=cube(b.center[0]*N+b.center[1]), p=cube(i);
  const X=c0[0]+(p[2]-c0[2]), Z=c0[2]+(p[1]-c0[1]), c=X, r=Z+(c-(c&1))/2;
  return (r<0||r>=N||c<0||c>=N)?-1:r*N+c; }
// The 3-player board: castles, mountains and water come in matching sets of three (a hex, and the same hex turned a third
// and two thirds of the way round), so every home castle has the same ones around it. A peak stands in the very centre,
// and the 4th water goes where it favours no one (as near as possible equally far from all three homes).
// Bonus coins are placed at random, as far from each home in total and with as many closest to each.
function genMap3(){
  const C0=BOARDS[3].center[0]*N+BOARDS[3].center[1], cells=[];
  for(let i=0;i<N*N;i++) if(!VOID.has(i)) cells.push(i);
  const nearHome=i=>Math.min(...HOMES.map(h=>man(i,h)));
  const orbits=(k,avoid,ok)=>{ const out=[];
    for(let g=0;g<300&&out.length<3*k;g++){ const i=cells[Math.floor(Math.random()*cells.length)], o=[i,rot3(i),rot3(rot3(i))];
      if(new Set(o).size<3||o.some(x=>x<0||VOID.has(x)||avoid.has(x)||out.includes(x))) continue;
      if(!o.every(x=>ok(x,out.concat(o.filter(y=>y!==x))))) continue;
      out.push(...o); }
    return out.length>=3*k?out:null; };
  const spread=i=>{ const ds=HOMES.map(h=>man(i,h)); return Math.max(...ds)-Math.min(...ds); };
  for(let tries=0;tries<4000;tries++){
    const tiles=Array.from({length:N*N},(_,i)=>({id:i,terrain:VOID.has(i)?'void':'plain',owner:-1,troops:0,fresh:0,army:{},ready:{},castle:false,market:0,fort:0,barracks:0,braced:-1,walls:[0,0,0,0,0,0],treb:0,trebDue:0,bk:0}));
    HOMES.forEach((h,p)=>{const t=tiles[h];t.castle=true;t.owner=p;});
    const taken=new Set([...HOMES,C0]);
    const cs=orbits(Math.round(NEUTRAL_CASTLES/3),taken,(x,others)=>nearHome(x)>=3&&others.every(c=>man(c,x)>=3)); if(!cs) continue;
    cs.forEach(i=>{ tiles[i].castle=true; taken.add(i); });
    const mt=orbits(Math.floor((MOUNTAINS-1)/3),taken,x=>nearHome(x)>=2); if(!mt) continue;
    mt.push(C0); mt.forEach(i=>{ tiles[i].terrain='mountain'; taken.add(i); });
    const wa=orbits(Math.floor(WATERS/3),taken,x=>nearHome(x)>=2); if(!wa) continue;
    wa.forEach(i=>taken.add(i));
    while(wa.length<WATERS){ const cand=shuffle(cells.filter(i=>!taken.has(i)&&nearHome(i)>=2)).sort((a,b)=>spread(a)-spread(b)); if(!cand.length) break; wa.push(cand[0]); taken.add(cand[0]); }
    if(wa.length<WATERS) continue;
    wa.forEach(i=>{ tiles[i].terrain='water'; });
    const d=bfs([HOMES[0]],tiles);
    if(tiles.some(t=>t.terrain==='plain'&&d[t.id]===Infinity)) continue;
    if(!placeCoins(tiles)) continue;
    placeForests(tiles); placeFerns(tiles);
    return tiles;
  }
  throw new Error('map generation failed');
}
function genMap(){
  if(HOMES.length>2) return genMap3();
  for(let tries=0;tries<2000;tries++){""")
rep("""      const d0=man(i,HOMES[0]), d1=man(i,HOMES[1]);
      if(d0<3||d1<3||Math.abs(d0-d1)>3) continue;""","""      const ds=HOMES.map(h=>man(i,h)), dmin=Math.min(...ds);
      if(dmin<3||Math.max(...ds)-dmin>3) continue;""")
rep("""    const bal=castles.reduce((s,c)=>s+man(c,HOMES[0])-man(c,HOMES[1]),0);
    if(Math.abs(bal)>2) continue;""","""    // every home castle about as far from the neutral ones as the others
    const sums=HOMES.map(h=>castles.reduce((s,c)=>s+man(c,h),0));
    if(Math.max(...sums)-Math.min(...sums)>2) continue;
""")
rep("""    place('mountain',MOUNTAINS); place('water',WATERS);""","""    place('mountain',MOUNTAINS); place('water',WATERS);
""")
rep("""  const n=Math.round(pool.length*COIN_SHARE);
  for(let k=0;k<400;k++){
    const pick=shuffle(pool).slice(0,n);
    let bal=0,near0=0,near1=0;
    pick.forEach(t=>{const d0=man(t.id,HOMES[0]),d1=man(t.id,HOMES[1]); bal+=d0-d1; if(d0<d1)near0++; else if(d1<d0)near1++;});
    if(Math.abs(bal)<=1&&near0===near1){ pick.forEach(t=>t.bounty=true); return true; }
  }
  return false;""","""  const n=COINS||Math.round(pool.length*COIN_SHARE);
  // as far from every home castle in total, and as many closest to each one
  for(let k=0;k<400;k++){
    const pick=shuffle(pool).slice(0,n), sums=HOMES.map(()=>0), near=HOMES.map(()=>0);
    pick.forEach(t=>{ const ds=HOMES.map(h=>man(t.id,h)), m=Math.min(...ds); ds.forEach((d,i)=>sums[i]+=d); if(ds.filter(x=>x===m).length===1) near[ds.indexOf(m)]++; });
    if(Math.max(...sums)-Math.min(...sums)<=(HOMES.length>2?2:1)&&Math.max(...near)===Math.min(...near)){ pick.forEach(t=>t.bounty=true); return true; }
  }
  return false;""")

# ---- saved games remember their board ----
rep("""    if(!s||!s.tiles||s.tiles.length!==N*N||!s.players||s.players.length!==2) return false;""",
    """    if(!s||!s.tiles||!s.players||(s.players.length!==2&&s.players.length!==3)) return false;
    const was=BOARD_NP; useBoard(s.players.length);
    if(s.tiles.length!==N*N){ useBoard(was); return false; }""")
open(p,'w',encoding='utf8').write(s); print('patch1 ok')

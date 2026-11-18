"""index.html: Ethan's hand-made maps (made in the Map Maker) as a choice on the new-game screen. Random stays the default.
Usage: patch_maps.py index.html maps.json   (re-runnable: the map list is swapped in place)"""
import sys, json
P, MJ = sys.argv[1], sys.argv[2]
s = open(P).read()
maps = json.load(open(MJ))
data = json.dumps([{k: m[k] for k in ('id', 'name', 'players', 'rows', 'coins', 'mats')} for m in maps], separators=(',', ':'))
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90]); s = s.replace(a, b)
if '/*CUSTOM_MAPS*/' in s:
    a = s.index('/*CUSTOM_MAPS*/const CUSTOM_MAPS='); b = s.index(';/*END_MAPS*/', a)
    s = s[:a] + '/*CUSTOM_MAPS*/const CUSTOM_MAPS=' + data + s[b:]
    open(P, 'w').write(s); print('maps swapped'); sys.exit()
# the maps and building a board from one
rep("useBoard(2);\n// where buildings stand", """useBoard(2);
// Hand-made maps (Ethan, 2026-11-17, made in the Map Maker): rows are the tile grid, x off the board, g grass, f forest,
// m mountain, w water, c neutral castle, 1-3 home castles (1 is you); coins and mats are [row, col]
/*CUSTOM_MAPS*/const CUSTOM_MAPS=""" + data + """;/*END_MAPS*/
const mapById=id=>CUSTOM_MAPS.find(m=>m.id===id)||null;
function mapTiles(m){
  const n=m.rows.length, homes=[];
  const tiles=Array.from({length:n*n},(_,i)=>({id:i,terrain:'plain',owner:-1,troops:0,fresh:0,army:{},ready:{},castle:false,market:0,fort:0,barracks:0,braced:-1,walls:[0,0,0,0,0,0],treb:0,trebDue:0,bk:0}));
  m.rows.forEach((row,r)=>[...row].forEach((ch,c)=>{ const t=tiles[r*n+c];
    if(ch==='x') t.terrain='void'; else if(ch==='m') t.terrain='mountain'; else if(ch==='w') t.terrain='water';
    else if(ch==='f') t.forest=true; else if(ch==='c') t.castle=true;
    else if('123'.includes(ch)){ t.castle=true; t.owner=+ch-1; homes[+ch-1]=t.id; } }));
  (m.coins||[]).forEach(([r,c])=>{ const t=tiles[r*n+c]; if(t&&t.terrain==='plain'&&!t.castle&&!t.forest) t.bounty=true; });
  (m.mats||[]).forEach(([r,c])=>{ const t=tiles[r*n+c]; if(t&&t.terrain==='plain'&&!t.castle&&!t.forest&&!t.bounty) t.crate=true; });
  return {tiles,homes};
}
// frame just the hexes on the board (the 3-player hexagon, or a hand-made map's own shape)
function frameHexes(){
  let x0=1e9,x1=-1e9,y0=1e9,y1=-1e9;
  for(let i=0;i<N*N;i++){ if(VOID.has(i)) continue; const r=Math.floor(i/N), c=i%N, gx=HM+HR+c*1.5*HR, gy=HM+HH/2+r*HH+(c&1)*HH/2, [x,y]=toBoard([gx,gy]);
    x0=Math.min(x0,x-HH/2); x1=Math.max(x1,x+HH/2); y0=Math.min(y0,y-HR); y1=Math.max(y1,y+HR); }
  const m=HM-VB_M; VB_X=x0-m; VB_Y=y0-m; VB_W=x1-x0+2*m; VB_H=y1-y0+2*m;
}
// the board's shape follows the game: a hand-made map's own, or the standard board for its player count
let _shapeKey='';
function syncShape(force){
  const key=S&&S.map?'map:'+S.map:'std';
  if(!force&&key===_shapeKey) return;
  _shapeKey=key;
  if(S&&S.map){ VOID=new Set(S.tiles.filter(t=>t.terrain==='void').map(t=>t.id)); HOMES=S.homes.slice(); frameHexes(); }
  else if(S){ BOARD_NP=0; useBoard(S.players.length); }
  try{ _mapReady=false; }catch(e){}
  try{ if(typeof fitStage==='function'&&document.getElementById('stage')) fitStage(); }catch(e){}
}
// where buildings stand""")
# newGame: a picked map instead of a random one
rep("""  const np=opts&&opts.np===3?3:2; useBoard(np);
  const facs=""", """  const np=opts&&opts.np===3?3:2; BOARD_NP=0; useBoard(np); _shapeKey='';
  const cmap=opts&&opts.map?mapById(opts.map):null, built=cmap&&cmap.players===np?mapTiles(cmap):null;
  if(built) HOMES=built.homes.slice();
  const facs=""")
rep("    tiles:genMap()};\n  { const mine=myColorFor", "    tiles:built?built.tiles:genMap()};\n  if(built){ S.map=cmap.id; S.mapName=cmap.name; }\n  syncShape(true);\n  { const mine=myColorFor")
rep("function renderMap(){\n  if(!_mapReady) initMap();", "function renderMap(){\n  syncShape();\n  if(!_mapReady) initMap();")
# load: games saved on a hand-made map keep its shape
rep("    S=s;\n", "    S=s; _shapeKey=''; syncShape(true);\n", 1) if s.count("    S=s;\n") == 1 else None
# the new-game screen: pick a map
rep("let fsPick=DEFAULT_FACTION, fsOpp=null, fsOpps=[], fsNP=2;", "let fsPick=DEFAULT_FACTION, fsOpp=null, fsOpps=[], fsNP=2, fsMap='';\ntry{ fsMap=localStorage.getItem('cc-map')||''; }catch(e){}")
rep("function oppPicker3(fid,want){", """function mapPicker(np){   // Random, or one of the hand-made maps for this many players
  const list=CUSTOM_MAPS.filter(m=>m.players===np); if(!list.length) return '';
  const sel=list.some(m=>m.id===fsMap)?fsMap:'';
  return `<div class="opick" role="group" aria-label="Map"><span class="cp-l">Map</span><button class="op-b" data-map="" aria-pressed="${!sel}" style="--pc:var(--bone)">Random</button>${list.map(m=>`<button class="op-b" data-map="${m.id}" aria-pressed="${m.id===sel}" style="--pc:var(--bone)">${escH(m.name)}</button>`).join('')}</div>`;
}
function oppPicker3(fid,want){""")
rep("<div id=\"fsPlayers\"></div><div id=\"fsOpp\"></div>", "<div id=\"fsPlayers\"></div><div id=\"fsMap\"></div><div id=\"fsOpp\"></div>")
rep("  $('#fsPlayers').innerHTML=playersPicker(fsNP);\n", "  $('#fsPlayers').innerHTML=playersPicker(fsNP);\n  $('#fsMap').innerHTML=mapPicker(fsNP);\n")
a = "  const fnp=e.target.closest('button[data-np]');"
rep(a, "  const fmp=e.target.closest('button[data-map]'); if(fmp){ fsMap=fmp.dataset.map; try{ localStorage.setItem('cc-map',fsMap); }catch(_){} renderFactionScreen(); return; }\n" + a)
rep("newGame(fsPick,{np:fsNP,opp:fsOpp,opps:fsOpps});", "newGame(fsPick,{np:fsNP,opp:fsOpp,opps:fsOpps,map:(mapById(fsMap)||{}).players===fsNP?fsMap:''});")
open(P, 'w').write(s); print('patched')

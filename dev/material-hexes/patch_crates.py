"""index.html: material hexes (Ethan, 2026-11-17: "add material icons to 6 hexes just like the coins on the map").
6 on the 2-player board, 9 on the 3-player board; the first side to take one gets MAT_BONUS materials (the Mythical, who
have no materials, get nothing, like coins); placed like the coins (fair distance to every home), never on a coin, castle
or forest. Tile flag: t.crate."""
import sys
P = sys.argv[1]; s = open(P).read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90]); s = s.replace(a, b)
rep("forests:10, ferns:0, coins:0},", "forests:10, ferns:0, coins:0, crates:6},")
rep("forests:15, ferns:0, coins:26},", "forests:15, ferns:0, coins:26, crates:9},")
rep("VOID, HOMES, MOUNTAINS, WATERS, NEUTRAL_CASTLES, FORESTS, FERNS, COINS,", "VOID, HOMES, MOUNTAINS, WATERS, NEUTRAL_CASTLES, FORESTS, FERNS, COINS, CRATES,")
rep("FERNS=b.ferns; COINS=b.coins;", "FERNS=b.ferns; COINS=b.coins; CRATES=b.crates||0;")
rep("const COIN_SHARE=1/3, COIN_GOLD=8;", "const COIN_SHARE=1/3, COIN_GOLD=8, MAT_BONUS=4;   // MAT_BONUS: materials in a material hex (worth a coin at 2 gold each)")
rep("    if(!placeCoins(tiles)) continue;\n    placeForests(tiles); placeFerns(tiles);", "    if(!placeCoins(tiles)) continue;\n    if(!placeCrates(tiles)) continue;\n    placeForests(tiles); placeFerns(tiles);", 2)
rep("function placeForests(tiles){\n  const pool=tiles.filter(t=>t.terrain==='plain'&&!t.castle&&!t.bounty&&", "function placeForests(tiles){\n  const pool=tiles.filter(t=>t.terrain==='plain'&&!t.castle&&!t.bounty&&!t.crate&&")
rep("function placeCoins(tiles){", """function placeCrates(tiles){   // material hexes: open land, not a coin; as fair to every home as the coins
  const pool=tiles.filter(t=>t.terrain==='plain'&&!t.castle&&!t.bounty&&!t.forest&&!t.market&&!t.fort&&!t.barracks);
  for(let k=0;k<600;k++){
    const pick=shuffle(pool).slice(0,CRATES), sums=HOMES.map(()=>0), near=HOMES.map(()=>0);
    pick.forEach(t=>{ const ds=HOMES.map(h=>man(t.id,h)), m=Math.min(...ds); ds.forEach((d,i)=>sums[i]+=d); if(ds.filter(x=>x===m).length===1) near[ds.indexOf(m)]++; });
    if(Math.max(...sums)-Math.min(...sums)<=(HOMES.length>2?2:1)&&Math.max(...near)===Math.min(...near)){ pick.forEach(t=>t.crate=true); return true; }
  }
  return false;
}
function placeCoins(tiles){""")
rep("t.castle=true; t.owner=-1; t.bounty=false;", "t.castle=true; t.owner=-1; t.bounty=false; t.crate=false;")
a = "  if(B.bounty){ B.bounty=false;"
rep(a, "  if(B.crate){ B.crate=false; if(!isMyth(A.owner)){ p.mat=matOf(p.id)+MAT_BONUS; res.crate=MAT_BONUS; addLog(`${p.name} take a materials cache: +${MAT_BONUS} materials.`,p.id); } }   // material hex\n" + a)
rep("+(b.bounty?` Its bonus coin pays you ${COIN_GOLD} gold.`:'');", "+(b.bounty?` Its bonus coin pays you ${COIN_GOLD} gold.`:'')+(b.crate&&!isMyth(S.current)?` Its materials cache gives you ${MAT_BONUS} materials.`:'');")
rep("const coinV=b.bounty?COIN_GOLD*0.9:0,", "const coinV=(b.bounty?COIN_GOLD*0.9:0)+(b.crate&&!isMyth(pid)?MAT_BONUS*1.8:0),")
rep("    if(t.bounty) tops+=`<use href=\"#ic-coin\" x=\"${(cx-4).toFixed(2)}\" y=\"${(cy+5.5).toFixed(2)}\"/>`;",
    "    if(t.bounty) tops+=`<use href=\"#ic-coin\" x=\"${(cx-4).toFixed(2)}\" y=\"${(cy+5.5).toFixed(2)}\"/>`;\n    if(t.crate) tops+=`<use href=\"#ic-mat\" x=\"${(cx-4).toFixed(2)}\" y=\"${(cy+5.5).toFixed(2)}\"/>`;   // material hex")
rep("  if(t.bounty) bl.push(`<span class=\"px px-coin\" aria-hidden=\"true\"></span> Bonus coin: +${COIN_GOLD} gold to whoever takes this hex first`);",
    "  if(t.bounty) bl.push(`<span class=\"px px-coin\" aria-hidden=\"true\"></span> Bonus coin: +${COIN_GOLD} gold to whoever takes this hex first`);\n  if(t.crate) bl.push(`${MAT_IC} Materials: +${MAT_BONUS} materials to whoever takes this hex first (not the Mythical)`);")
rep("so retaking the hex later pays nothing.</li>", "so retaking the hex later pays nothing. ${S.players.length>2?'Nine':'Six'} other hexes hold ${MAT_IC} materials instead: the first side to take one gets ${MAT_BONUS} materials (the Mythical, who don't use materials, get nothing).</li>")
rep("    if(!s.tiles.some(t=>t.fern)) placeFerns(s.tiles);", "    if(!s.crates){ if(!s.tiles.some(t=>t.crate)) placeCrates(s.tiles); s.crates=1; }   // a game saved before material hexes") if "    if(!s.tiles.some(t=>t.fern)) placeFerns(s.tiles);" in s else None
rep("  S={turn:1,current:0,over:null,log:[],homes:HOMES.slice(),", "  S={turn:1,current:0,over:null,log:[],crates:1,homes:HOMES.slice(),")
rep("    s.tiles.forEach(t=>{ delete t.fern; });", "    if(!s.crates){ if(!s.tiles.some(t=>t.crate)) placeCrates(s.tiles); s.crates=1; }   // a game saved before material hexes\n    s.tiles.forEach(t=>{ delete t.fern; });")
open(P, 'w').write(s); print('patched')

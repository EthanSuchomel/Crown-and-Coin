import sys
P='/tmp/claude-0/-home-claude/fb256341-5d08-5e47-8b49-8c9035f9f7b9/scratchpad/cc/'
s=open(P+'base.html',encoding='utf-8').read()
def rep(old,new,count=1):
    global s
    n=s.count(old)
    if n!=count:
        print('COUNT',n,'for',old[:120]); sys.exit(1)
    s=s.replace(old,new)

# ---------- materials icon ----------
rep("// the Mammal buildings are painted pictures, not pixel art",
r'''// Materials: Claude's stand-in icon, drawn in code (a stone block and two planks)
ART.icons.mat='data:image/svg+xml,'+encodeURIComponent(`<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><g stroke='#060907' stroke-width='1.6' stroke-linejoin='round'><path d='M15 10l3.5-4.5h12L27 10z' fill='#c9cdd1'/><path d='M27 10l3.5-4.5v10L27 20z' fill='#6c737a'/><rect x='15' y='10' width='12' height='10' fill='#9ba2a8'/><path d='M2.5 19.5h21l2 2.5-2 2.5h-21z' fill='#c28a48'/><path d='M4.5 24.5h21l2 2.5-2 2.5h-21z' fill='#a06a33'/></g><path d='M5 21.2h16M7 26.2h16' stroke='#e2b06e' stroke-width='1' opacity='.8'/></svg>`);
// the Mammal buildings are painted pictures, not pixel art''')
rep(".px-coin{image-rendering:auto}   /* the coin is smooth art too */",
    ".px-coin,.px-mat{image-rendering:auto}   /* the coin and materials are smooth art too */")
rep("const SMOOTH_IC=['move','harvest','recruit','build','fortify','advance','coin','magic','dome'];",
    "const SMOOTH_IC=['move','harvest','recruit','build','fortify','advance','coin','magic','dome','mat'];")

# ---------- prices: markets in gold, everything else in materials ----------
rep("const MATE_MAX=3, WH_OFF=5, WH_COST=8, IN_NUMBERS=10, FREE_WALLS=2;",
    "const MATE_MAX=3, WH_OFF=5, WH_COST=4, IN_NUMBERS=10, FREE_WALLS=2;   // WH_COST is in materials")
rep("""// Building prices by the Build action's upgrade level (0 = not upgraded)
const COSTS={market:[6,4,4,4], fort:[10,10,8,7], barracks:[10,10,10,8], wh:[WH_COST,WH_COST,WH_COST,WH_COST]};
const costOf=(k,lvl)=>COSTS[k][lvl||0];""",
r"""// Building prices by the Build action's upgrade level (0 = not upgraded). Markets cost gold; forts, barracks and
// Watering Holes cost materials (Ethan, 2026-11-10: about half their old gold price, at 2 gold a material).
const COSTS={market:[6,4,4,4], fort:[5,5,4,3], barracks:[5,5,5,4], wh:[WH_COST,WH_COST,WH_COST,WH_COST]};
const costOf=(k,lvl)=>COSTS[k][lvl||0];
const inMat=k=>k!=='market';                       // which buildings are paid for in materials
// ---- Materials (Ethan, 2026-11-10): markets sell them; buildings other than markets, walls, barracks upgrades and
// trebuchets are paid for with them. Each market sells up to 3 a turn and the home castle counts as one market, 2 gold each,
// any time on your turn. Units, markets, Alamosaurus guards and the Volcano stay gold. The Mythical keep magic for everything. ----
const MAT_PRICE=2, MAT_PER_MARKET=3;
const MAT_IC='<span class="px px-mat" aria-hidden="true"></span>';
const matTxt=n=>`${n} material${n===1?'':'s'}`;
const priceTxt=(k,n)=>inMat(k)?matTxt(n):`${n} gold`;
const priceIc=(k,n)=>inMat(k)?`${n} ${MAT_IC}`:`${n} gold`;      // for the round buttons
const usesMat=pid=>!!(S&&S.players&&S.players[pid])&&S.players[pid].faction!=='mythical';
const matOf=pid=>(S&&S.players&&S.players[pid]&&S.players[pid].mat)|0;
const marketsOf=pid=>S.tiles.reduce((n,t)=>n+(t.owner===pid?(t.market|0):0),0);
const homeMarket=pid=>{ const h=S.tiles[S.homes[pid]]; return !!h&&h.owner===pid; };
// how many materials a side's markets sell it each turn: 3 for every market, and 3 more while it holds its home castle
const matCap=pid=>usesMat(pid)?MAT_PER_MARKET*(marketsOf(pid)+(homeMarket(pid)?1:0)):0;
const matLeft=pid=>Math.max(0,matCap(pid)-((S.players[pid].tr)|0));
function buyMat(pid,n){
  const p=S.players[pid]; n=Math.min(n|0,matLeft(pid),Math.floor(p.gold/MAT_PRICE)); if(n<1) return 0;
  p.gold-=n*MAT_PRICE; p.mat=matOf(pid)+n; p.tr=(p.tr|0)+n;
  addLog(`${p.name} buy ${matTxt(n)} at the market for ${n*MAT_PRICE} gold.`,pid);
  return n;
}
const spendMat=(pid,n)=>{ S.players[pid].mat=Math.max(0,matOf(pid)-n); };
// pay for a building: markets in gold, the rest in materials
const canPayB=(pid,k,n)=>inMat(k)?matOf(pid)>=n:S.players[pid].gold>=n;
const payB=(pid,k,n)=>{ if(inMat(k)) spendMat(pid,n); else S.players[pid].gold-=n; };
// materials a side could have now: what it holds plus what its markets can still sell it, keeping `keep` gold back
const matReach=(pid,keep)=>matOf(pid)+Math.min(matLeft(pid),Math.max(0,Math.floor((S.players[pid].gold-(keep||0))/MAT_PRICE)));
// the computer buys the materials it's short of (all or nothing), keeping `keep` gold back
function aiMat(pid,need,keep){ const short=need-matOf(pid); if(short<=0) return true; if(matReach(pid,keep)<need) return false; buyMat(pid,short); return matOf(pid)>=need; }
// the gold a purchase of `mats` materials would still take, after what's already in store
const goldFor=(pid,mats)=>Math.max(0,mats-matOf(pid))*MAT_PRICE;
const canB=(pid,k,n,keep)=>inMat(k)?matReach(pid,keep)>=n:S.players[pid].gold-(keep||0)>=n;   // the computer: affordable, counting what it can buy""")
rep("const TREB_COST=15, TREB_DICE=5, TREB_HIT=4;","const TREB_COST=8, TREB_DICE=5, TREB_HIT=4;   // TREB_COST is in materials")
rep("// castles hold up to 2 trebuchets (no fort needed): 20 gold for the first, 30 for the second, 3 turns to build\nconst CASTLE_TREB=[20,30], CASTLE_TREB_TURNS=3;",
    "// castles hold up to 2 trebuchets (no fort needed): 10 materials for the first, 15 for the second, 3 turns to build\nconst CASTLE_TREB=[10,15], CASTLE_TREB_TURNS=3;")
rep("const WALL_HP=3, WALL_COSTS=[6,6,4,4];          // a wall counts as 3 defenders; its price by the Advancements level",
    "const WALL_HP=3, WALL_COSTS=[3,3,2,2];          // a wall counts as 3 defenders; its price in materials by the Advancements level")
rep("const BARRACKS_UP=[6,8,10], CHEAP_TROOP=2;","const BARRACKS_UP=[3,4,5], CHEAP_TROOP=2;   // barracks upgrades, in materials")

# ---------- action descriptions ----------
rep("""  if(a==='build') return (isDino(pid)?'Build as many Markets and Barracks as you can afford':'Build as many Markets, Forts and Barracks as you can afford')+(lvl?` (Market ${costOf('market',lvl)}${isDino(pid)?'':`, Fort ${costOf('fort',lvl)}`}, Barracks ${costOf('barracks',lvl)} gold)`:'');""",
r"""  if(a==='build') return `Build as many as you can afford: Markets (${costOf('market',lvl)} gold)${isDino(pid)?'':`, Forts (${matTxt(costOf('fort',lvl))})`} and Barracks (${matTxt(costOf('barracks',lvl))}). Buy materials at your markets`;""")
rep("""  if(a==='advance'&&isDino(pid)) return `Spend gold on as many as you can afford: upgrade a barracks (${BARRACKS_UP.join(', ')} gold for levels 1 to 3${lvl>=1?', your first level 1 free':''}), hire Alamosaurus guards for a barracks (${GUARD_COST} gold each, up to ${GUARD_MAX} per barracks), wake or stoke the volcano at your home castle (${VOLC.map(v=>v.cost).join(', ')} gold for levels 1 to 3), or build walls on a hex's sides (${wallCost(lvl)} gold each)`;""",
r"""  if(a==='advance'&&isDino(pid)) return `Do as many as you can afford: upgrade a barracks (${BARRACKS_UP.join(', ')} materials for levels 1 to 3${lvl>=1?', your first level 1 free':''}), hire Alamosaurus guards for a barracks (${GUARD_COST} gold each, up to ${GUARD_MAX} per barracks), wake or stoke the volcano at your home castle (${VOLC.map(v=>v.cost).join(', ')} gold for levels 1 to 3), or build walls on a hex's sides (${matTxt(wallCost(lvl))} each)`;""")
rep("""  if(a==='advance') return `Spend gold on as many as you can afford: upgrade a barracks (${BARRACKS_UP.join(', ')} gold for levels 1 to 3${lvl>=1?', your first level 1 free':''}), start a trebuchet on a hex with a fort (${TREB_COST} gold, ready at the end of your ${lvl>=3?'turn':'next turn'}) or on a castle (up to 2: ${CASTLE_TREB.join(' then ')} gold, ${CASTLE_TREB_TURNS-(lvl>=3?1:0)} turns to build), or build walls on a hex's sides (${wallCost(lvl)} gold each)`;""",
r"""  if(a==='advance') return `Do as many as you can afford, all paid in materials: upgrade a barracks (${BARRACKS_UP.join(', ')} for levels 1 to 3${lvl>=1?', your first level 1 free':''}), start a trebuchet on a hex with a fort (${TREB_COST}, ready at the end of your ${lvl>=3?'turn':'next turn'}) or on a castle (up to 2: ${CASTLE_TREB.join(' then ')}, ${CASTLE_TREB_TURNS-(lvl>=3?1:0)} turns to build), or build walls on a hex's sides (${wallCost(lvl)} each)`;""")
rep("""  if(a==='fortify') return (lvl>=3?'First, every castle and fort you hold gains 1 troop. Then e':'E')+`very hex with your troops gets +${m.fortifyBonus} defense`+(lvl>=1?' (+2 at forts and castles)':'')+' until your next turn'+(lvl>=2?'. Troops in forts and castles also defend with advantage':'');""",
r"""  if(a==='fortify'){ const n=fxPicksAt(pid,lvl);
    return `A wild card. First regroup: move your units any distance between your own hexes, as often as you like (no attacks or claiming). Then ${n>=3?'do all three of':n===2?'pick two of':'pick one of'} Build, Advancements and Recruit, played like the basic action`; }""")

# ---------- upgrade texts ----------
rep("""  build:  {next:['Markets cost 4 gold','Forts cost 8 gold','Forts 7 and Barracks 8 gold'],
           now:['Market 4','Market 4, Fort 8','Market 4, Fort 7, Barracks 8']},""",
r"""  build:  {next:['Markets cost 4 gold','Forts cost 4 materials','Forts 3 and Barracks 4 materials'],
           now:['Market 4','Market 4, Fort 4','Market 4, Fort 3, Barracks 4']},""")
rep("""  fortify:{next:['Forts and castles get +2 defense instead of +1','Troops in forts and castles defend with advantage: 1 extra die, keep the best','+1 troop at every castle and fort you hold'],
           now:['+2 at forts and castles','+2 and advantage at forts and castles','+2, advantage, +1 troop at forts and castles']},""",
r"""  fortify:{next:['Pick two of Build, Advancements and Recruit','Pick two of Build, Advancements and Recruit','Do all three: Build, Advancements and Recruit'],
           now:['pick 2','pick 2','all 3']},""")
rep("""  advance:{next:['Your first barracks upgrade to level 1 in this action is free','Walls cost 4 gold','Trebuchets you start finish at the end of this turn'],""",
r"""  advance:{next:['Your first barracks upgrade to level 1 in this action is free','Walls cost 2 materials','Trebuchets you start finish at the end of this turn'],""")
rep("""  build:  {name:'Watering Hole', next:`Watering Hole: you can build a Watering Hole (${WH_COST} gold), where""",
    """  build:  {name:'Watering Hole', next:`Watering Hole: you can build a Watering Hole (${matTxt(WH_COST)}), where""")
rep("""           desc:`Watering Hole: you can also build a Watering Hole (${WH_COST} gold, one per hex, castles too).""",
    """           desc:`Watering Hole: you can also build a Watering Hole (${matTxt(WH_COST)}, one per hex, castles too).""")
rep("""  market:{icon:'<span class="px px-market" aria-hidden="true"></span>',name:'Market',desc:'+2 gold every turn'},""",
    """  market:{icon:'<span class="px px-market" aria-hidden="true"></span>',name:'Market',desc:'+2 gold every turn, and sells you up to 3 materials a turn'},""")
rep("""  return k==='market'?`+${m.marketGold} gold every turn`:""",
    """  return k==='market'?`+${m.marketGold} gold every turn, and sells you up to ${MAT_PER_MARKET} materials a turn (${MAT_PRICE} gold each)`:""")

# ---------- the new decks (Ethan, 2026-11-10: each faction leans on two actions) ----------
rep("""      {id:'stamp', name:'Stampede',       actions:['move','build','fortify']},
      {id:'pack',  name:'Pack Call',      actions:['harvest','move','advance']},
      {id:'siege', name:'Siege of Teeth', actions:['fortify','harvest','move']},
      {id:'hunt',  name:'The Hunt',       actions:['harvest','build','recruit']},
      {id:'nest',  name:'Nesting Season', actions:['build','advance','recruit']},""",
"""      // themed on Fortify and Harvest (Ethan, 2026-11-10): each is on 4 of the 5 cards
      {id:'stamp', name:'Stampede',       actions:['move','build','fortify']},
      {id:'pack',  name:'Pack Call',      actions:['harvest','recruit','fortify']},
      {id:'siege', name:'Siege of Teeth', actions:['fortify','harvest','move']},
      {id:'hunt',  name:'The Hunt',       actions:['harvest','recruit','advance']},
      {id:'nest',  name:'Nesting Season', actions:['harvest','build','fortify']},""")
rep("""      {id:'mobil', name:'Mobilize',       actions:['recruit','advance','fortify']},
      {id:'deploy',name:'Deploy',         actions:['harvest','recruit','move']},
      {id:'onsl',  name:'Onslaught',      actions:['harvest','advance','recruit']},
      {id:'cons',  name:'Construct',      actions:['move','build','advance']},
      {id:'sprot', name:'Siege Protocol', actions:['build','harvest','fortify']},""",
"""      // themed on Move and Advancements (Ethan, 2026-11-10): each is on 4 of the 5 cards
      {id:'mobil', name:'Mobilize',       actions:['recruit','advance','move']},
      {id:'deploy',name:'Deploy',         actions:['harvest','recruit','move']},
      {id:'onsl',  name:'Onslaught',      actions:['harvest','advance','move']},
      {id:'cons',  name:'Construct',      actions:['move','build','advance']},
      {id:'sprot', name:'Siege Protocol', actions:['build','advance','fortify']},""")
rep("""      {id:'roam',  name:'The Long Roam',    actions:['move','build','recruit']},
      {id:'forage',name:'Forage',           actions:['harvest','build','advance']},
      {id:'den',   name:'Den Season',       actions:['harvest','recruit','fortify']},
      {id:'wild',  name:'Call of the Wild', actions:['recruit','harvest','advance']},
      {id:'tusks', name:'Tusks and Thorns', actions:['advance','fortify','move']},""",
"""      // themed on Harvest and Recruit (Ethan, 2026-11-10): each is on 4 of the 5 cards
      {id:'roam',  name:'The Long Roam',    actions:['move','build','recruit']},
      {id:'forage',name:'Forage',           actions:['harvest','build','recruit']},
      {id:'den',   name:'Den Season',       actions:['harvest','recruit','fortify']},
      {id:'wild',  name:'Call of the Wild', actions:['recruit','harvest','advance']},
      {id:'tusks', name:'Tusks and Thorns', actions:['harvest','advance','move']},""")
rep("""      {id:'march', name:'March of Minions', actions:['move','build','recruit']},
      {id:'gather',name:'Gathering',        actions:['harvest','recruit','move']},
      {id:'grove', name:'The Grove',        actions:['harvest','advance','fortify']},
      {id:'arcan', name:'Arcanum',          actions:['build','advance','recruit']},""",
"""      // themed on Advancements and Fortify (Ethan, 2026-11-10): each is on 3 of the 4 cards with actions
      {id:'march', name:'March of Minions', actions:['move','recruit','fortify']},
      {id:'gather',name:'Gathering',        actions:['harvest','recruit','advance']},
      {id:'grove', name:'The Grove',        actions:['fortify','advance','move']},
      {id:'arcan', name:'Arcanum',          actions:['build','advance','fortify']},""")

open(P+'stage1.html','w',encoding='utf-8').write(s)
print('ok')

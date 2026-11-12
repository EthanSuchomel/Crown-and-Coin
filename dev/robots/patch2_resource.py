# Robot rewrite, step 2 (Ethan, 2026-11-11): resource hexes. A Robot market can grow one of two ways:
# into a factory (barracks, then fortress, from the home castle) for defense, or, on its own hex, into a resource hex
# of up to 4 markets (same price as a market each). Never both.
import sys
p=sys.argv[1]; s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:120]); s=s.replace(a,b)

rep("""const bMax=()=>(S&&S.play&&isRobo(S.current))?1:""","""const bMax=()=>(S&&S.play&&isRobo(S.current))?ROBO_MARKETS:""")
rep("""const roboNext=t=>(t.market&&!t.castle)?(!t.barracks?'barracks':!t.fort?'fort':null):null;   // what the home castle can add to it next""",
"""const ROBO_MARKETS=4;   // a resource hex holds up to 4 markets
const roboNext=t=>(t.market&&!t.castle)?(!t.barracks?((t.market|0)===1?'barracks':null):!t.fort?'fort':null):null;   // what the home castle can add to it next (a resource hex takes none)
const roboCanMarket=t=>!t.barracks&&!t.fort&&!t.wh&&(t.market|0)<ROBO_MARKETS;   // an empty hex, or a market on the resource path""")
rep("""  if(isRobo(0)&&k!=='market') return;""","""  if(isRobo(0)&&(k!=='market'||!roboCanMarket(t))) return;""")
# the zoomed view's Market button
rep("""    const price=costOf(kind,lvl,t), castleNo=t.castle&&kind!=='market'&&kind!=='wh', has=kind==='wh'&&!!t.wh, can=!full&&!castleNo&&!has&&canPayB(0,kind,price);""",
"""    if(isRobo(0)&&kind==='market'&&!isHomeCastle(t)&&bCount(t)){   // a Robot market: add another (a resource hex), or it's a factory
      const price=costOf('market',lvl,t), ok=roboCanMarket(t), can=ok&&canPayB(0,'market',price), m=t.market|0;
      const note=ok?`${price} gold`:t.barracks?'Factory':'Full';
      html+=`<button class="bub${can?'':' off'}" data-bk="market" ${pos} ${can?'':'disabled'} aria-label="${ok?`Add market ${m+1} of ${ROBO_MARKETS} (a resource hex: no barracks or fortress here): ${price} gold`:t.barracks?'This hex is a factory, so it takes no more markets':`This resource hex already has ${ROBO_MARKETS} markets`}">${bldImg('market_robots')}<b>${ok?'Market '+(m+1):'Market'}</b><small>${note}</small></button>`;
      continue;
    }
    const price=costOf(kind,lvl,t), castleNo=t.castle&&kind!=='market'&&kind!=='wh', has=kind==='wh'&&!!t.wh, can=!full&&!castleNo&&!has&&canPayB(0,kind,price);""")
# on the board: a resource hex shows its markets like a little village; a factory keeps its one big picture
rep("""owned&&!t.castle&&S.players[t.owner].faction==='robots'&&roboLv(t)""",
    """owned&&!t.castle&&S.players[t.owner].faction==='robots'&&roboLv(t)&&(t.market|0)<2""")
# the side panel on a Robot hex
rep("""      h+=matRow()+`<p class="hint">${bCount(sel)?`This hex already has a factory${roboNext(sel)?`. Upgrade it from your home castle with a ${roboNext(sel)==='fort'?'fortress':'barracks'}`:', fully upgraded'}.`:""",
"""      h+=matRow()+`<p class="hint">${(sel.market|0)>=2?`A resource hex: ${sel.market} of ${ROBO_MARKETS} markets${roboCanMarket(sel)?'. Tap <b>Market</b> to add another':''}. It can't take a barracks or fortress.`
        :sel.barracks?`A factory${roboNext(sel)?`. Add its fortress from your home castle`:', fully upgraded'}. It can't take more markets.`
        :bCount(sel)?`Choose what this market becomes: tap <b>Market</b> to add a second one and make it a <b>resource hex</b> (up to ${ROBO_MARKETS} markets), or give it a <b>barracks</b> from your home castle to make it a defensive <b>factory</b>. Not both.`:""")
rep("""const roboKeyHtml=lvl=>[['market',`${BUILD_INFO.market.desc}. Every Robot building starts as one, one per hex`],""",
"""const roboKeyHtml=lvl=>[['market',`${BUILD_INFO.market.desc}. Every Robot building starts as one. Add more markets on its hex (up to ${ROBO_MARKETS}, ${costOf('market',lvl||0)} gold each) to make a resource hex, or upgrade it into a factory`],""")
rep("""const roboSpecialsHtml=()=>`Robots build one <b>factory</b> per hex. It starts as a market (gold). Then, during Build, tap your home castle and pick <b>Barracks</b> or <b>Fortress</b> (materials) and tap a factory to upgrade it: first a barracks, then a fortress. Each factory is upgraded on its own, and only while you hold your home castle.""",
"""const roboSpecialsHtml=()=>`Every Robot building starts as a market (gold), one per hex, and then takes one of two paths. A <b>resource hex</b>: build more markets on that hex, up to ${ROBO_MARKETS}. Or a defensive <b>factory</b>: during Build, tap your home castle, pick <b>Barracks</b> or <b>Fortress</b> (materials) and tap the market to upgrade it, first a barracks, then a fortress. Never both. Each is upgraded on its own, and factory upgrades only while you hold your home castle.""")
rep("""if(a==='build'&&isRobo(pid)) return `Build factories (${costOf('market',lvl)} gold, one per hex; each starts as a market) and upgrade them from your home castle: a Barracks, then a Fortress (${matTxt(costOf('barracks',lvl))} each). Buy materials at your markets`;""",
"""if(a==='build'&&isRobo(pid)) return `Build markets (${costOf('market',lvl)} gold). Stack up to ${ROBO_MARKETS} on a hex for a resource hex, or turn one into a factory from your home castle: a Barracks, then a Fortress (${matTxt(costOf('barracks',lvl))} each). Buy materials at your markets`;""")
# the reminder before ending Build
rep("""    const can=mine.some(t=>t.terrain==='plain'&&bCount(t)<bMax()&&(t.castle||isRobo(0)?['market']:BUILD_KINDS)""",
    """    const can=mine.some(t=>t.terrain==='plain'&&bCount(t)<bMax()&&(!isRobo(0)||roboCanMarket(t))&&(t.castle||isRobo(0)?['market']:BUILD_KINDS)""")
# captures: markets alone stay a resource hex (up to 4); anything military becomes a factory
rep("""  if(isRobo(p.id)&&!B.castle&&bCount(B)){ const bk=!!(B.barracks||B.fort), ft=!!(B.fort&&B.barracks);
    B.market=1;""","""  if(isRobo(p.id)&&!B.castle&&bCount(B)){ const bk=!!(B.barracks||B.fort), ft=!!(B.fort&&B.barracks);
    B.market=bk?1:Math.min(ROBO_MARKETS,Math.max(1,B.market|0));""")
# the computer: markets only where the resource path allows, on the safest such hex
rep("""    if(isRobo(pid)&&plan.k!=='market'){""","""    if(isRobo(pid)&&plan.k==='market'&&!roboCanMarket(S.tiles[plan.id])){
      const dE=bfs(foeTiles(pid)), c=S.tiles.filter(t=>t.owner===pid&&t.terrain==='plain'&&roboCanMarket(t)).sort((a,b)=>fin(dE[b.id])-fin(dE[a.id]))[0];
      if(!c) break; plan={k:'market',id:c.id};
    }
    if(isRobo(pid)&&plan.k!=='market'){""")
open(p,'w').write(s); print('robots patch2 ok')
s=open(p).read()
# a resource hex: its markets in a neat group, a little bigger than the usual village buildings
rep("""owned&&!t.castle&&S.players[t.owner].faction==='robots'&&roboLv(t)&&(t.market|0)<2){""",
"""owned&&!t.castle&&S.players[t.owner].faction==='robots'&&(t.market|0)>=2&&!t.barracks){
      const n=Math.min(t.market|0,ROBO_MARKETS), z=n>2?11.5:13, at=[null,null,[[-6.4,1],[6.4,1]],[[0,-5.6],[-6.6,5],[6.6,5]],[[-6,-5],[6,-5],[-6,6],[6,6]]][n];
      at.forEach(([ox,oy])=>{ const x=cx+ox-z/2, y=cy+oy-z/2; castles+=`<use href="#b-market_robots" transform="translate(${x.toFixed(2)} ${y.toFixed(2)}) scale(${(z/16).toFixed(4)})"/>`; });
    }
    else if(owned&&!t.castle&&S.players[t.owner].faction==='robots'&&roboLv(t)){""")
open(p,'w').write(s); print('robots patch2b ok')

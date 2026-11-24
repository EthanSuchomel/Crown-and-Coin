"""Ethan, 2026-11-24: "for the robots fix how you add a barracks and fortress to a market to being purchasable at the
market instead of the home castle". During Advancements, tap the market (or factory) itself: its button ring has
Barracks (a market with one market) or Fortress (a factory with a barracks), same prices in materials. The home castle
no longer has those buttons, and the home castle doesn't have to be held.
Usage: python3 patch.py index.html"""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, a[:120]); s = s.replace(a, b)
rep("if(!isRobo(pid)||t.owner!==pid||!k||!homeMarket(pid)) return false;", "if(!isRobo(pid)||t.owner!==pid||!k) return false;   // bought at the market itself (2026-11-24): the home castle needn't be held")
# the Advancements ring: the market's own factory upgrade instead of the home castle's two
rep("""    if(isRobo(0)&&isHomeCastle(t)&&t.owner===0){
      const rb=k=>{""", """    if(isRobo(0)&&!isHomeCastle(t)&&t.owner===0&&(roboNext(t)||t.barracks)){   // Robots: the market's own factory upgrade (2026-11-24)
      const k=roboNext(t), c=k?roboUpCost(0,k,t):0;
      opts.splice(t.barracks?1:0,t.barracks?0:1,k?{k:'rnext', img:ART.bld[k+'_robots'], sm:true, name:ROBO_NAME[k], can:matOf(0)>=c, note:`${c} ${MAT_IC}`,
        label:`Add a ${ROBO_NAME[k]} to this ${k==='fort'?'factory':'market'} for ${matTxt(c)}${k==='barracks'?': it becomes a factory':''}`}
        :{k:'rnext', img:ART.bld['fort_robots'], sm:true, name:'Fortress', can:false, note:'Built', label:'This factory already has its fortress'});
    }
    if(isRobo(0)&&isHomeCastle(t)&&t.owner===0){
      const rb=k=>{""")
rep("      opts.splice(0,1,rb('barracks'),rb('fort'));\n", "")
rep("  else if(kind==='rup_barracks'||kind==='rup_fort'){", "  else if(kind==='rnext'){ const t=S.tiles[ui.sel]; if(isRobo(0)&&roboNext(t)) doRoboUp(0,ui.sel); }\n  else if(kind==='rup_barracks'||kind==='rup_fort'){")
# the computer
rep("  if(isRobo(pid)&&homeMarket(pid)){   // the Robots' factory upgrades at the home castle, then Overclock", "  if(isRobo(pid)){   // the Robots' factory upgrades (bought at the market itself since 2026-11-24), then Overclock")
# texts
rep("add a Barracks or Fortress to one of your markets at your home castle (${COSTS.barracks[0]} each), ", "add a Barracks or Fortress to one of your markets: tap the market (${COSTS.barracks[0]} each), ")
rep("Barracks and Fortress upgrades for your markets are made here during Advancements.", "Barracks and Fortress upgrades are bought at each market during Advancements.")
rep(":sel.barracks?`A factory${roboNext(sel)?`. Add its fortress from your home castle during Advancements`:', fully upgraded'}.", ":sel.barracks?`A factory${roboNext(sel)?`. Add its fortress here during Advancements`:', fully upgraded'}.")
rep("or give it a <b>barracks</b> from your home castle during Advancements to make it", "or give it a <b>barracks</b> here during Advancements to make it")
rep("during Advancements, turn one into a factory at your home castle: a Barracks, then a Fortress", "during Advancements, tap a market to turn it into a factory: a Barracks, then a Fortress")
open(p, 'w', encoding='utf-8').write(s); print('ok')

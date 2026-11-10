# Dinosaur board rework, step 4: the Alamosaurus Guard (Ethan, 2026-11-09).
# Bought for a barracks with Advancements: 25 gold each, up to 2 per barracks. They're Alamosaurus units on the hex
# (t.army.alamo) that are never "ready", so they never move or attack; they fight whenever the hex is attacked,
# hold it on their own, and a dead (or fled) guard is gone until it's bought again.
import sys,re
p=sys.argv[1]; s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:100]); s=s.replace(a,b)
rep("const BARRACKS_UP=[6,8,10], CHEAP_TROOP=2;",
    "const BARRACKS_UP=[6,8,10], CHEAP_TROOP=2;\nconst GUARD_COST=25, GUARD_MAX=2;            // the Dinosaurs' Alamosaurus Guard: gold each, and how many per barracks\nconst guardsAt=t=>(t.army&&t.army.alamo)||0;")
# guards are never ready to move
rep("  S.tiles.forEach(t=>{if(t.owner===p.id){t.ready=Object.assign({},t.army||{}); syncT(t);",
    "  S.tiles.forEach(t=>{if(t.owner===p.id){t.ready=Object.assign({},t.army||{}); delete t.ready.alamo; syncT(t);")
# a guard that leaves the field (the Flee order) is lost: it never leaves its barracks
rep("    const fled=clip(defEsc,gone), dead=minus(gone,fled);",
    "    const fled=clip(defEsc,gone); delete fled.alamo; const dead=minus(gone,fled);   // an Alamosaurus guard never leaves its barracks: if it runs, it's lost")
# buying one
rep("const freeWallsLeft=pid=>",
"""function doBuyGuard(pid,i){
  const t=S.tiles[i], p=S.players[pid];
  if(t.owner!==pid||!isDino(pid)||!t.barracks||guardsAt(t)>=GUARD_MAX*t.barracks||p.gold<GUARD_COST) return false;
  p.gold-=GUARD_COST; addUnits(t,'alamo',1,false);
  addLog(`${p.name} station an Alamosaurus to guard a barracks (${guardsAt(t)} there now).`,pid);
  return true;
}
const freeWallsLeft=pid=>""")
rep("  else if(kind==='treb') doStartTreb(0,ui.sel,lvl);",
    "  else if(kind==='treb') doStartTreb(0,ui.sel,lvl);\n  else if(kind==='guard') doBuyGuard(0,ui.sel);\n  else if(kind==='volc') doVolcano(0);")
# the Advancements buttons: for the Dinosaurs the trebuchet button becomes the Alamosaurus (on a barracks) or the Volcano (home castle)
rep("""      {k:'walls', img:ART.icons.wall, name:'Walls',""",
"""      ...[],
      {k:'walls', img:ART.icons.wall, name:'Walls',""")
rep("""    [[150,1],[90,0],[30,5]].forEach(([deg,vi],i)=>{ const o=opts[i];""",
"""    if(isDino(0)){ const g=guardsAt(t), gm=GUARD_MAX*(t.barracks|0), home=isHomeCastle(t)&&t.owner===0, vl=volcLv(0);
      opts[1]=home?{k:'volc', img:ART.castle_dinos.uri, sm:true, name:vl<3?`Volcano ${vl+1}`:'Volcano',
          can:vl<3&&me.gold>=VOLC[vl].cost, note:vl>=3?'Max level':`${VOLC[vl].cost} gold`,
          label:vl>=3?'Volcano: already level 3':`Volcano level ${vl+1} for ${VOLC[vl].cost} gold: ${volcSay(vl+1)}`}
        :{k:'guard', img:UNIT_ART.alamo, sm:true, name:'Alamosaurus',
          can:!!t.barracks&&g<gm&&me.gold>=GUARD_COST, note:!t.barracks?'Needs barracks':g>=gm?`${g} guarding`:`${GUARD_COST} gold`,
          label:!t.barracks?'Alamosaurus Guard: needs a barracks on this hex':g>=gm?`This barracks already has ${g} Alamosaurus guarding it`:`Station an Alamosaurus to guard this barracks for ${GUARD_COST} gold (${g} of ${gm} there now)`}; }
    [[150,1],[90,0],[30,5]].forEach(([deg,vi],i)=>{ const o=opts[i];""")
rep(".bub img.sm,.px-wh{image-rendering:auto}",".bub img.sm,.px-wh{image-rendering:auto}\n.bub.adv img{object-fit:contain}")
# the computer: guards on its barracks nearest the enemy, once it can spare the gold
rep("""function aiAdvance(pid,lvl){
  const p=S.players[pid], ids=[];""",
"""function aiAdvance(pid,lvl){
  const p=S.players[pid], ids=[];
  if(isDino(pid)){
    // the volcano first (it hits every few turns from home), then Alamosaurus on the barracks the enemy is closest to
    const vl=volcLv(pid), sp=aiSmart(pid)?6:15;
    if(vl<3&&S.tiles[S.homes[pid]].owner===pid&&p.gold>=VOLC[vl].cost+sp&&doVolcano(pid)) ids.push(S.homes[pid]);
    const bks=S.tiles.filter(t=>t.owner===pid&&t.barracks&&guardsAt(t)<GUARD_MAX*t.barracks).map(t=>({t,thr:enemyNear(t.id,pid,2)})).filter(x=>x.thr>0).sort((a,b)=>b.thr-a.thr);
    for(const {t} of bks) while(guardsAt(t)<GUARD_MAX*t.barracks&&p.gold>=GUARD_COST+sp&&doBuyGuard(pid,t.id)) ids.push(t.id);
  }""")
open(p,'w').write(s); print('patch4 ok')

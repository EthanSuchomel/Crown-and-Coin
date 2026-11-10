# Dinosaur board rework, step 5: the volcano strike (Ethan, 2026-11-09). The Dinosaurs' trebuchets are replaced by
# their home castle's volcano, bought and upgraded with Advancements at the home castle:
#   level 1: 40 gold, reaches 5 hexes, erupts every 3 turns, 5 dice
#   level 2: 60 gold, reaches 7 hexes, every 2 turns, 6 dice
#   level 3: 100 gold, reaches the whole map, every turn, 8 dice
# One volley a turn, at the start of the Dinosaurs' turn, at an enemy hex with units that they pick. Each die of 4+ is a
# hit of 10 damage, front of the line first (like a trebuchet, but walls don't stop it). It's lost if the home castle falls.
import sys,re
p=sys.argv[1]; s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:100]); s=s.replace(a,b)
rep("const GUARD_COST=25, GUARD_MAX=2;",
"""const GUARD_COST=25, GUARD_MAX=2;
const VOLC=[{cost:40,reach:5,every:3,dice:5},{cost:60,reach:7,every:2,dice:6},{cost:100,reach:99,every:1,dice:8}];   // the Dinosaurs' volcano, levels 1 to 3
const volcLv=pid=>(S&&S.players[pid]&&S.players[pid].volc&&S.players[pid].volc.lv)||0;
const volcSay=l=>{ const v=VOLC[l-1]; return `reaches ${v.reach>=99?'the whole map':v.reach+' hexes'}, erupts ${v.every===1?'every turn':'every '+v.every+' turns'}, ${v.dice} dice`; };""")
# the volley: trebuchets and the volcano share it
rep("function trebTargets(i){",
"""// ---------- The Dinosaurs' volcano ----------
const isVolcHex=i=>{ const t=S.tiles[i]; return t.owner>=0&&isDino(t.owner)&&S.homes[t.owner]===i&&volcLv(t.owner)>0; };
function volcTargets(i){ const pid=S.tiles[i].owner, v=VOLC[volcLv(pid)-1]; if(!v) return [];
  return S.tiles.filter(b=>b.owner>=0&&b.owner!==pid&&b.troops>0&&man(i,b.id)<=v.reach).map(b=>b.id); }
const shotTargets=i=>isVolcHex(i)?volcTargets(i):trebTargets(i);
const shotFire=(i,j)=>isVolcHex(i)?fireVolcano(i,j):fireTreb(i,j);
// the home castle's volcano, if it's due this turn and has something to hit
function volcReady(pid){ const p=S.players[pid], h=S.homes[pid]; if(!volcLv(pid)) return null;
  if(S.tiles[h].owner!==pid){ p.volc=null; addLog(`${p.name} lost their home castle, and its volcano with it.`,pid); return null; }
  if(p.volc.cd>0) p.volc.cd--;
  return p.volc.cd<=0&&volcTargets(h).length?h:null; }
function fireVolcano(i,j){
  const b=S.tiles[j], pid=S.tiles[i].owner, p=S.players[pid], v=VOLC[volcLv(pid)-1];
  const dice=roll(v.dice), hits=dice.filter(x=>x>=TREB_HIT).length;
  const sd={}; for(const k in b.army) sd[k]={n:b.army[k],w:0};
  let dmg=hits*TREB_DMG; const dd={};
  Object.keys(sd).sort((x,y)=>UNIT_STATS[x].rank-UNIT_STATS[y].rank).forEach(k=>{ const h=sd[k].n*UNIT_STATS[k].hp, d=Math.min(h,dmg); if(d>0){dd[k]=d; dmg-=d;} });
  apply(sd,dd);
  const lost={}; let kl=0; for(const k in sd){ const d=b.army[k]-sd[k].n; if(d>0){ lost[k]=d; kl+=d; } }
  loseUnits(b,lost);
  p.volc.cd=v.every;
  addLog(`${pid===0?'Your':`The ${p.name}'`} volcano erupts: ${hits?`${kl} unit${kl===1?'':'s'} killed`:'every lava bomb misses'}.`,pid);
  return {from:i,to:j,dice,hits,wl:0,kl,lost,pid,volc:true};
}
function aiVolcTarget(pid){ const h=S.homes[pid]; let best=null,bv=-Infinity;
  for(const j of volcTargets(h)){ const b=S.tiles[j]; const v=Math.min(tp(b),8)*(b.castle?1.5:1)+(S.homes.includes(j)?3:0)-0.05*man(h,j); if(v>bv){bv=v;best=j;} }
  return best; }
function doVolcano(pid){
  const p=S.players[pid], lv=volcLv(pid), h=S.homes[pid];
  if(!isDino(pid)||lv>=3||S.tiles[h].owner!==pid||p.gold<VOLC[lv].cost) return false;
  p.gold-=VOLC[lv].cost; const cd=p.volc?Math.min(p.volc.cd,VOLC[lv].every):0; p.volc={lv:lv+1,cd};
  addLog(`${p.name} ${lv?'stoke':'awaken'} the volcano at ${pid===0?'your':'their'} home castle: level ${lv+1}, ${volcSay(lv+1)}.`,pid);
  return true;
}
function trebTargets(i){""")
rep("""    if(p.ai){ const shots=[]; for(const h of trebs){ const j=aiTrebTarget(h); if(j!=null) shots.push(fireTreb(h,j)); } ui.aiShots=shots; }
    else { S.volley={queue:trebs,shots:[]}; runVolley(); }
  }""","""    if(p.ai){ const shots=[]; for(const h of trebs){ const j=aiTrebTarget(h); if(j!=null) shots.push(fireTreb(h,j)); } ui.aiShots=shots; }
    else { S.volley={queue:trebs,shots:[]}; runVolley(); }
  }
  // the Dinosaurs' volcano erupts when it's due
  const vh=isDino(p.id)?volcReady(p.id):null;
  if(vh!=null){
    if(p.ai){ const j=aiVolcTarget(p.id); if(j!=null) (ui.aiShots=ui.aiShots||[]).push(fireVolcano(vh,j)); }
    else { S.volley=S.volley||{queue:[],shots:[]}; S.volley.queue.unshift(vh); runVolley(); }
  }""")
rep("    const h=v.queue[0], tg=(S.tiles[h].owner===0&&(S.tiles[h].treb===2||S.tiles[h].treb2===2))?trebTargets(h):[];",
    "    const h=v.queue[0], tg=S.tiles[h].owner!==0?[]:isVolcHex(h)?volcTargets(h):(S.tiles[h].treb===2||S.tiles[h].treb2===2)?trebTargets(h):[];")
rep("    if(tg.length===1) v.shots.push(fireTreb(h,tg[0]));","    if(tg.length===1) v.shots.push(shotFire(h,tg[0]));")
rep("  const v=S.volley; if(!v||v.queue[0]!==h||!trebTargets(h).includes(j)) return;\n  v.queue.shift(); v.shots.push(fireTreb(h,j)); runVolley(); render();",
    "  const v=S.volley; if(!v||v.queue[0]!==h||!shotTargets(h).includes(j)) return;\n  v.queue.shift(); v.shots.push(shotFire(h,j)); runVolley(); render();")
rep("  if(S.volley&&S.volley.queue.length&&trebTargets(S.volley.queue[0]).includes(i)){","  if(S.volley&&S.volley.queue.length&&shotTargets(S.volley.queue[0]).includes(i)){")
rep("shooter=S.volley.queue[0]; trebTargets(shooter).forEach(j=>tg.add(j)); }","shooter=S.volley.queue[0]; shotTargets(shooter).forEach(j=>tg.add(j)); }")
# the panel
rep("""    const body=(h0!=null?`<p class="hint" style="margin-bottom:.4em">Your trebuchet (gold ring) can hit ${trebTargets(h0).length} enemy hexes next to it. Tap a red-ringed hex to fire.</p>`:'')+v.shots.map(shotHtml).join('');
    P.innerHTML=`<div class="bigcard volley"><div class="bc-main"><div class="bc-head"><span class="bc-name"><span class="px px-${trebIc(0)}" aria-hidden="true"></span> Trebuchets</span>""",
"""    const vol=h0!=null?isVolcHex(h0):v.shots.some(x=>x.volc), vr=VOLC[volcLv(0)-1];
    const body=(h0!=null?(vol?`<p class="hint" style="margin-bottom:.4em">Your volcano (gold ring) is erupting: ${vr?vr.dice:0} lava bombs can hit any of ${volcTargets(h0).length} enemy hexes ${vr&&vr.reach>=99?'anywhere on the map':`within ${vr&&vr.reach} hexes`}. Tap a red-ringed hex to aim it.</p>`
        :`<p class="hint" style="margin-bottom:.4em">Your trebuchet (gold ring) can hit ${trebTargets(h0).length} enemy hexes next to it. Tap a red-ringed hex to fire.</p>`):'')+v.shots.map(shotHtml).join('');
    P.innerHTML=`<div class="bigcard volley"><div class="bc-main"><div class="bc-head"><span class="bc-name">${vol?`<img src="${ART.castle_dinos.uri}" alt="" style="height:1.3em;vertical-align:-.25em"> Volcano`:`<span class="px px-${trebIc(0)}" aria-hidden="true"></span> Trebuchets`}</span>""")
rep("""  return `<div class="battle"><div class="dice"><span class="px px-${trebIc(x.pid)}" aria-hidden="true"></span> ${dice}</div><div>${what}</div></div>`;""",
"""  return `<div class="battle"><div class="dice">${x.volc?`<img src="${ART.castle_dinos.uri}" alt="Volcano" style="height:1.4em">`:`<span class="px px-${trebIc(x.pid)}" aria-hidden="true"></span>`} ${dice}</div><div>${what}</div></div>`;""")
rep("""${p.name}' trebuchet${ui.shotsShown.length>1?'s fire':' fires'}</b>""",
    """${p.name}' ${ui.shotsShown.some(x=>x.volc)?(ui.shotsShown.length>1?'volcano and trebuchets fire':'volcano erupts'):`trebuchet${ui.shotsShown.length>1?'s fire':' fires'}`}</b>""")
# the hex details: the volcano's level and when it erupts next
rep("  if(t.treb===1) bl.push(",
    "  if(t.castle&&t.owner>=0&&isDino(t.owner)&&S.homes[t.owner]===t.id&&volcLv(t.owner)){ const pv=S.players[t.owner].volc; bl.push(`<img src=\"${ART.castle_dinos.uri}\" alt=\"\" style=\"height:1.2em;vertical-align:-.25em\"> Volcano level ${pv.lv}: ${volcSay(pv.lv)}. ${pv.cd>1?`Erupts in ${pv.cd} turns`:'Erupts at the start of '+(t.owner===0?'your':'their')+' next turn'}`); }\n  if(t.treb===1) bl.push(")
# the lava bombs: a few glowing rocks arc from the volcano to the target, then splash (skipped with reduced motion)
rep("})();\n</script>","""})();
(()=>{
const REDUCE=matchMedia('(prefers-reduced-motion: reduce)').matches;
const q=[]; let busy=false;
const orig=fireVolcano;
fireVolcano=function(i,j){ const r=orig(i,j); if(!REDUCE){ q.push(r); if(!busy) setTimeout(next,60); } return r; };
function next(){
  const r=q.shift(); if(!r){ busy=false; return; } busy=true;
  const map=$('#map'), wrap=map&&map.parentElement; if(!wrap){ busy=false; return; }
  const ns='http://www.w3.org/2000/svg', svg=document.createElementNS(ns,'svg');
  svg.setAttribute('class','lavafx'); svg.setAttribute('aria-hidden','true'); svg.setAttribute('viewBox',map.getAttribute('viewBox')); svg.setAttribute('preserveAspectRatio','xMidYMid meet');
  svg.style.cssText='position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:4';
  wrap.appendChild(svg);
  const [fx,fy]=hexCenter(r.from), [tx,ty]=hexCenter(r.to), n=r.dice.length, bombs=[];
  for(let k=0;k<n;k++){
    const hit=r.dice[k]>=TREB_HIT, ox=(Math.random()-.5)*(hit?7:16), oy=(Math.random()-.5)*(hit?5:12);
    const g=document.createElementNS(ns,'g'), c=document.createElementNS(ns,'circle'), core=document.createElementNS(ns,'circle');
    c.setAttribute('r','2'); c.setAttribute('fill','#e8541a'); c.setAttribute('stroke','#060907'); c.setAttribute('stroke-width','.7');
    core.setAttribute('r','.9'); core.setAttribute('fill','#ffd54a'); g.appendChild(c); g.appendChild(core); svg.appendChild(g);
    bombs.push({g,hit,t0:k*110,x1:tx+ox,y1:ty+oy,done:false});
  }
  const DUR=900, H=Math.max(28,Math.hypot(tx-fx,ty-fy)*.45), start=performance.now();
  // the crater flares first
  const flare=document.createElementNS(ns,'circle'); flare.setAttribute('cx',fx); flare.setAttribute('cy',fy-HR*.55); flare.setAttribute('fill','#ffb02e'); svg.appendChild(flare);
  function splash(x,y,hit){ const s=document.createElementNS(ns,'circle'); s.setAttribute('cx',x); s.setAttribute('cy',y); s.setAttribute('fill',hit?'#ff7a1a':'#7a6a5a'); svg.appendChild(s);
    const t0=performance.now(); (function f(now){ const u=Math.min(1,(now-t0)/380); s.setAttribute('r',(1.5+u*(hit?6:3.5)).toFixed(2)); s.setAttribute('opacity',(1-u).toFixed(2)); if(u<1) requestAnimationFrame(f); else s.remove(); })(t0); }
  (function frame(now){
    const el=now-start; let live=false;
    const fu=Math.min(1,el/300); flare.setAttribute('r',(2+fu*5).toFixed(2)); flare.setAttribute('opacity',(0.8*(1-fu)).toFixed(2));
    for(const b of bombs){ const u=(el-b.t0)/DUR;
      if(u<0){ live=true; b.g.setAttribute('opacity','0'); continue; }
      if(u>=1){ if(!b.done){ b.done=true; b.g.remove(); splash(b.x1,b.y1,b.hit); } continue; }
      live=true; const x=fx+(b.x1-fx)*u, y=(fy-HR*.55)+(b.y1-(fy-HR*.55))*u-H*4*u*(1-u);
      b.g.setAttribute('opacity','1'); b.g.setAttribute('transform',`translate(${x.toFixed(2)} ${y.toFixed(2)})`); }
    if(live||el<DUR+bombs.length*110+400) requestAnimationFrame(frame); else { svg.remove(); setTimeout(next,120); }
  })(start);
}
})();
</script>""")
open(p,'w').write(s); print('patch5 ok')

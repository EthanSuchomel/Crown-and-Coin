"""Adds the Mythical faction to Megaraptor Arena (arena.html).
Usage: python3 patch_myth.py IN OUT   -- also writes edits.json (old/new pairs) for publishing."""
import sys, json
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
S = json.load(open('/home/claude/work/spr/sprites.json'))
if len(sys.argv)>3 and sys.argv[3]=='url':
    for k in S:
        for side in ('blue','red'): S[k][side]='myth/%s_%s.png'%(k,side)
edits = []

def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, (n, old[:80])
    s = s.replace(old, new)
    edits.append({'old_text': old, 'new_text': new})

# ---- CSS: dragon fire and chain lightning ----
rep(".arc{position:absolute;height:2px;",
""".flame{position:absolute;transform-origin:0 50%;pointer-events:none;z-index:4997}
.flame b{position:absolute;inset:0;transform-origin:0 50%;clip-path:polygon(0 42%,100% 0,100% 100%,0 58%);
  background:radial-gradient(ellipse 60% 55% at 8% 50%,rgba(255,252,215,1),rgba(255,214,90,.95) 35%,rgba(255,140,30,.9) 65%,rgba(220,60,20,.8) 85%,rgba(140,25,10,0) 100%),linear-gradient(90deg,rgba(255,200,70,.9),rgba(255,120,30,.85) 55%,rgba(200,40,15,.5) 85%,rgba(120,20,10,0));
  filter:blur(1.2px);animation:flame .9s ease-out forwards}
@keyframes flame{0%{transform:scaleX(.15);opacity:0}15%{transform:scaleX(1);opacity:1}70%{opacity:.95}100%{transform:scaleX(1.05);opacity:0}}
.zap{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:4999;overflow:visible;animation:zapFade .45s linear forwards}
.zap .glow{fill:none;stroke-width:7px;stroke-linejoin:round;opacity:.75}
.zap.blue .glow{stroke:#5f9bff}.zap.red .glow{stroke:#ff5a48}
.zap .core{fill:none;stroke:#fff;stroke-width:2px;stroke-linejoin:round}
@keyframes zapFade{0%,55%{opacity:1}20%{opacity:.55}35%{opacity:1}100%{opacity:0}}
@media (prefers-reduced-motion: reduce){.flame b{animation-duration:.01s}.zap{animation-duration:.2s}}
.arc{position:absolute;height:2px;""")

# ---- the pictures (OpenArt art, cut out by Claude; purple trim swapped for each side's color) ----
def flyimg(k): return '{"blue": {"up": "%s", "down": "%s"}, "red": {"up": "%s", "down": "%s"}}' % (S[k]['blue'], S[k]['blue'], S[k]['red'], S[k]['red'])
def img(k): return '{"blue": "%s", "red": "%s"}' % (S[k]['blue'], S[k]['red'])
rep("const TYPES={",
"// Mythical (OpenArt art, cut out by Claude): the purple trim is blue on Blue's side and red on Red's\n"
"Object.assign(IMG,{\n  minion:%s,\n  mage:%s,\n  minotaur:%s,\n  griffin:%s,\n  dragon:%s\n});\nconst TYPES={" % (img('minion'), img('mage'), img('minotaur'), flyimg('griffin'), flyimg('dragon')))

# ---- the units ----
r = {k: S[k]['ratio'] for k in S}
rep("shoves them back\n};\nconst ORDER=['galli','dilo','ptero','mega','bow','quetz','alamo','robot','rarch','rdrone','rknight','rlong','rjet','rtank','ape','porc','bat','rhino','kanga','gbat','eleph'];",
"shoves them back\n"
"  // ---- Mythical (Ethan's stats). Speed: 100%% = 5.4 ----\n"
"  minion:{label:'Minion',faction:'Mythical',cost:1,hp:5,dmg:2,rate:1.0,range:3.5,speed:3.78,w:1.5,ratio:%s,aimFrac:0.45,ranged:false,hitKey:'melee',armor:{},\n"
"        flying:false,antiAir:false,rank:0,basic:true,lungeDur:.3,strikeAt:.13,lungeFwd:0.008,bob:0.6,bobRate:2.2},   // penguin chick: waddles\n"
"  mage:{label:'Mage',faction:'Mythical',cost:15,hp:15,dmg:5,rate:10,range:24,speed:3.51,w:2.8,ratio:%s,aimFrac:0.5,ranged:true,hitKey:'magic',armor:{},\n"
"        flying:false,antiAir:true,rank:2,lightning:{n:20,jump:9},lungeDur:.6,strikeAt:.3,noRecoil:true,bob:0.2,bobRate:1.2,staff:[0.17,0.06]},   // chain lightning: 5 to up to 20 enemies, every 10s\n"
"  minotaur:{label:'Minotaur',faction:'Mythical',heavy:true,cost:25,hp:35,dmg:15,rate:1.0,range:4.3,speed:6.21,w:6.0,ratio:%s,aimFrac:0.45,ranged:false,hitKey:'melee',armor:{},\n"
"        flying:false,antiAir:false,rank:0,multi:5,lungeDur:.5,strikeAt:.25,lungeFwd:0.012,bob:0.3,bobRate:1.1},   // hammer: 15 to up to 5 ground units at once\n"
"  griffin:{label:'Griffin',faction:'Mythical',cost:40,hp:45,dmg:25,rate:1.0,range:4,speed:7.02,walkSpeed:5.4,w:8.5,ratio:%s,aimFrac:0.45,ranged:false,hitKey:'air',armor:{},\n"
"        flying:true,antiAir:true,rank:1,lungeDur:.6,strikeAt:.3,flap:.6},   // flies at 130%%, on the ground at 100%%\n"
"  dragon:{label:'Dragon',faction:'Mythical',cost:85,hp:150,dmg:30,rate:1.0,range:5,speed:6.48,walkSpeed:4.86,w:15,ratio:%s,aimFrac:0.45,ranged:false,hitKey:'air',armor:{},\n"
"        flying:true,antiAir:true,rank:1,breath:{dmg:15,n:15,rate:8,reach:16,first:2},mouth:[0.95,0.2],lungeDur:.7,strikeAt:.35,flap:.8}   // bite 30 every 1s; fire breath 15 to up to 15 every 8s\n"
"};\n"
"const ORDER=['galli','dilo','ptero','mega','bow','quetz','alamo','robot','rarch','rdrone','rknight','rlong','rjet','rtank','ape','porc','bat','rhino','kanga','gbat','eleph','minion','mage','minotaur','griffin','dragon'];"
% (r['minion'], r['mage'], r['minotaur'], r['griffin'], r['dragon']))
rep("const FACTIONS=['Dinosaurs','Robots','Mammals'];", "const FACTIONS=['Dinosaurs','Robots','Mammals','Mythical'];")
rep("Mammals:{ape:14,porc:6,bat:10,rhino:3,kanga:3,gbat:2,eleph:1}};",
    "Mammals:{ape:14,porc:6,bat:10,rhino:3,kanga:3,gbat:2,eleph:1},Mythical:{minion:25,mage:4,minotaur:3,griffin:1,dragon:1}};")

rep("bobRate:0.6}   // Mammals' special unit: tusk sweep", "bobRate:0.6},   // Mammals' special unit: tusk sweep")

# ---- Griffin and Dragon: walking speed while down on the ground fighting a ground unit ----
rep("const spd=T.speed*(f.boost>0",
    "const spd=((T.walkSpeed&&f.baseAlt<(ALT+LOW_ALT)/2)?T.walkSpeed:T.speed)*(f.boost>0")

# ---- Dragon fire breath, checked every frame alongside its bite ----
old = "    const t=f.target;\n    if(!t&&!hold){"
rep(old, "    if(T.breath) breathStep(f);\n" + old)

# ---- Mage: its attack is chain lightning instead of an arrow ----
rep("  f.missVolley=!!f.missNext; f.missNext=false;   // War Trumpet: this whole volley misses\n",
    "  f.missVolley=!!f.missNext; f.missNext=false;   // War Trumpet: this whole volley misses\n"
    "  if(f.T.lightning){ castLightning(f,t); return; }\n")

rep("function shootFrom(f,ox,oy,t,mult,kind,stun){",
r"""// ---- Mythical ----
// Mage, chain lightning: a bolt from its staff to its target, then on to the nearest enemy within 9 of the last one hit,
// and so on, up to 20 enemies (ground or air); each takes 5. Units hidden in the forest or inside the fortress are out of its sight.
function castLightning(f,t){
  const Lg=f.T.lightning, chain=[t], done=new Set([t.id]); let cur=t;
  while(chain.length<Lg.n){ let nx=null,bd=Lg.jump;
    for(const o of F){ if(o.dead||o.pass||o.ballista||o.team===f.team||done.has(o.id)||!canHit(f,o)) continue;
      const d=dist(o,cur); if(d<bd){bd=d;nx=o;} }
    if(!nx) break; done.add(nx.id); chain.push(nx); cur=nx; }
  const st=f.T.staff, p0={x:f.x+f.face*(st[0]-0.5)*f.T.w,y:f.y-f.alt-f.h*(1-st[1])};
  zap(f,[p0,...chain.map(aimPt)]);
  if(f.missVolley){ floatText(t,'Miss','blk'); return; }   // War Trumpet: the spell fizzles
  for(const o of chain) if(!o.dead) hit(o,f);
}
function zap(f,pts){   // a jagged bolt through the points, drawn in field units (the arena is 100 x 60)
  let d='';
  for(let i=0;i<pts.length;i++){ const p=pts[i];
    if(i===0){ d+='M'+p.x.toFixed(2)+' '+p.y.toFixed(2); continue; }
    const q=pts[i-1], dx=p.x-q.x, dy=p.y-q.y, L=Math.hypot(dx,dy)||1, n=Math.max(2,Math.round(L/2.2));
    for(let k=1;k<n;k++){ const u=k/n, j=vrnd(-0.9,0.9); d+=' L'+(q.x+dx*u-dy/L*j).toFixed(2)+' '+(q.y+dy*u+dx/L*j).toFixed(2); }
    d+=' L'+p.x.toFixed(2)+' '+p.y.toFixed(2); }
  const ns='http://www.w3.org/2000/svg', svg=document.createElementNS(ns,'svg');
  svg.setAttribute('class','zap '+SIDE[f.team]); svg.setAttribute('viewBox','0 0 '+AW+' '+AH); svg.setAttribute('preserveAspectRatio','none');
  for(const c of ['glow','core']){ const pl=document.createElementNS(ns,'path'); pl.setAttribute('d',d); pl.setAttribute('class',c); pl.setAttribute('vector-effect','non-scaling-stroke'); svg.appendChild(pl); }
  svg.addEventListener('animationend',()=>svg.remove()); arena.appendChild(svg);
}
// Dragon, fire breath: every 8 seconds, when an enemy it is going for is within reach (about a sixth of the field) and in front of it,
// it breathes a cone of fire at it. Up to 15 enemies in the cone (ground or air, nearest first) take 15 each. Its bite carries on as normal.
function breathStep(f){
  const B=f.T.breath;
  if(f.fireAt==null) f.fireAt=clock+B.first+R();
  if(clock<f.fireAt||held(f)) return;
  const t=f.target; if(!t||t.dead||t.ballista) return;
  const ox=f.x+f.face*f.T.w*0.35, oy=f.y;   // the flame starts at its head
  const ax=t.x-ox, ay=t.y-oy, L=Math.hypot(ax,ay);
  if(L>B.reach||ax*f.face<Math.max(0.5,L*0.6)) return;   // out of reach, or not in front of it (within about 50 degrees of straight ahead)
  const ux=ax/(L||1), uy=ay/(L||1);
  const inCone=o=>{ const dx=o.x-ox, dy=o.y-oy, along=dx*ux+dy*uy; return along>=-1&&along<=B.reach&&Math.abs(dy*ux-dx*uy)<=1.6+Math.max(0,along)*0.4; };
  const burn=F.filter(o=>!o.dead&&!o.pass&&!o.ballista&&o.team!==f.team&&canHit(f,o)&&inCone(o)).sort((a,b)=>dist(a,f)-dist(b,f)).slice(0,B.n);
  f.fireAt=clock+B.rate;
  // draw it: from its mouth along the cone, as long as reach (or to just past the farthest unit burned)
  const M=f.T.mouth, mx=f.x+f.face*(M[0]-0.5)*f.T.w, my=f.y-f.alt-f.h*(1-M[1]);
  const far=burn.reduce((m,o)=>Math.max(m,dist(o,{x:ox,y:oy})),L)+2, len=Math.min(B.reach+2,far);
  const ex=ox+ux*len, ey=oy+uy*len-(t.T.flying?t.alt:0)-1, ang=Math.atan2(ey-my,ex-mx), dl=Math.hypot(ex-mx,ey-my);
  const aw=arena.clientWidth||1000, fl=document.createElement('div'); fl.className='flame';
  fl.style.left=mx+'%'; fl.style.top=(my/AH*100)+'%'; fl.style.width=dl+'%';
  const hpx=2*(1.6+len*0.4)*aw/AW; fl.style.height=hpx.toFixed(1)+'px'; fl.style.marginTop=(-hpx/2).toFixed(1)+'px';
  fl.style.transform='rotate('+(ang*180/Math.PI).toFixed(1)+'deg)';
  const b=document.createElement('b'); fl.appendChild(b); b.addEventListener('animationend',()=>fl.remove()); arena.appendChild(fl);
  if(f.missNext){ f.missNext=false; floatText(t,'Miss','blk'); return; }   // War Trumpet: this breath does no harm
  for(const o of burn) hit(o,f,B.dmg/f.T.dmg);
}
function shootFrom(f,ox,oy,t,mult,kind,stun){""")

# ---- words: the intro, the stats table and the notes ----
rep("Each side picks one faction above its army: Dinosaurs, Robots or Mammals (",
    "Each side picks one faction above its army: Dinosaurs, Robots, Mammals or Mythical (")
rep("Dinosaurs and Mammals get the bone-and-tusk ones,", "Dinosaurs, Mammals and Mythical get the bone-and-tusk ones,")
rep("<td>Its tusks</td><td>No</td></tr>",
"""<td>Its tusks</td><td>No</td></tr>
        <tr class="grp"><th colspan="8">Mythical</th></tr>
        <tr><td>Minion</td><td>1 gold</td><td>5</td><td>2</td><td>1.0s</td><td>70%</td><td>Melee</td><td>No</td></tr>
        <tr><td>Mage</td><td>15 gold</td><td>15</td><td>Chain lightning: 5 to up to 20 enemies at once</td><td>10s</td><td>65%</td><td>A quarter of the field; the bolt jumps to the next enemy within about a tenth of the field</td><td>Yes, never misses</td></tr>
        <tr><td>Minotaur</td><td>25 gold</td><td>35</td><td>15 to up to 5 ground units at once</td><td>1.0s</td><td>115%</td><td>Melee (hammer)</td><td>No</td></tr>
        <tr><td>Griffin</td><td>40 gold</td><td>45</td><td>25</td><td>1.0s</td><td>130% flying, 100% on the ground</td><td>Melee, flying</td><td>Yes</td></tr>
        <tr><td>Dragon</td><td>85 gold</td><td>150</td><td>Bite 30. Fire breath: 15 to up to 15 enemies at once</td><td>Bite 1.0s, fire breath 8s</td><td>120% flying, 90% on the ground</td><td>Melee, flying; fire breath reaches about a sixth of the field</td><td>Yes</td></tr>""")
rep("the other units fill whatever room is left.</p>",
    "the other units fill whatever room is left. Mythical: Minions are the cheap basic unit. The Minotaur's hammer hits up to 5 ground units at once, like the Palaeoloxodon's sweep. The Griffin and the Dragon fly like the Quetzalcoatlus, at their flying speed while cruising and at their ground speed while they're down fighting a ground unit; only units that hit flyers can reach them. The Mage's chain lightning leaps from its target to the nearest enemy, then the next, up to 20 enemies, ground or air, 5 damage each; arrows that miss flyers don't apply, and it can't see units hidden in the forest. The Dragon bites every second, and every 8 seconds, when the enemy it is after is in front of it and within about a sixth of the field, it breathes a cone of fire that burns up to 15 enemies in it (nearest first, ground or air) for 15 each. A War Trumpet makes the Mage's next spell fizzle and the Dragon's next bite or breath miss. Mythical sides use the bone-and-tusk walls, fortress and castle for now.</p>")

open(dst, 'w').write(s)
json.dump(edits, open('/home/claude/work/edits.json', 'w'))
print('ok', len(edits), 'edits; size', len(s))

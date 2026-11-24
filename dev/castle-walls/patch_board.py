"""Ethan, 2026-11-24: castle walls and battles.
- A castle's battle is fought on the Castle map (its walls, no ballistas) only when the castle has a wall on the side
  being attacked; with no wall there the battle is on the Open field (Ethan is designing a new arena for it), and the
  board's odds follow the same map.
- Walls on the map: stone walls with battlements and round corner towers along each walled side, drawn round the
  castle (or any hex); damaged walls show gaps. The Mammals' palisades the same in timber.
Usage: python3 patch_board.py index.html"""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, a[:120]); s = s.replace(a, b)
rep("const arenaMap=t=>t.castle?'castle':", "const arenaMap=(t,w)=>t.castle?((w==null||w>0)?'castle':'open'):   // a castle with no wall on the attacked side: the Open field (2026-11-24)\n  ")
rep("map:arenaMap(B),defStart,attLost", "map:arenaMap(B,W),defStart,attLost")
rep("const b=fightBattle(sel,defStart,{wall:W,bonus:defBonus(B),advD:defAdv(B),map:arenaMap(B),...ao});", "const b=fightBattle(sel,defStart,{wall:W,bonus:defBonus(B),advD:defAdv(B),map:arenaMap(B,W),...ao});")
rep("const o={wall:W,bonus:defBonus(b),advD,map:arenaMap(b),...ao}", "const o={wall:W,bonus:defBonus(b),advD,map:arenaMap(b,W),...ao}")
rep("const p=winEst(sel,defArmy(b),{wall:W,bonus:defBonus(b),advD:defAdv(b),map:arenaMap(b),", "const p=winEst(sel,defArmy(b),{wall:W,bonus:defBonus(b),advD:defAdv(b),map:arenaMap(b,W),")
rep("o={wall,bonus:defBonus(e),advD:defAdv(e),map:arenaMap(e),", "o={wall,bonus:defBonus(e),advD:defAdv(e),map:arenaMap(e,wall),")
rep("pr=Math.max(pr,winEst(b.army,defArmy(t),{wall:wl,bonus:defBonus(t),advD:defAdv(t),map:arenaMap(t)}))", "pr=Math.max(pr,winEst(b.army,defArmy(t),{wall:wl,bonus:defBonus(t),advD:defAdv(t),map:arenaMap(t,wl)}))")
rep("pr=winEst(a,defArmy(t),{wall:w,bonus:defBonus(t),advD:defAdv(t),map:arenaMap(t)});", "pr=winEst(a,defArmy(t),{wall:w,bonus:defBonus(t),advD:defAdv(t),map:arenaMap(t,w)});")
rep("att:A.owner,def:B.owner,map:arenaMap(B),seed:", "att:A.owner,def:B.owner,map:arenaMap(B,wallOn(to,from)),seed:")
# walls drawn as stone walls with battlements and corner towers
a = s.index("function wallSvg(cx,cy,k,hp,preview,wood){")
b = s.index("// ---------- building on the map ----------")
s = s[:a] + r'''function wallSvg(cx,cy,k,hp,preview,wood){
  const r=HR-2.3, [x1,y1]=hexV(cx,cy,r,k), [x2,y2]=hexV(cx,cy,r,k+1);
  const P=f=>[(x1+(x2-x1)*f).toFixed(2),(y1+(y2-y1)*f).toFixed(2)];
  const ln=(f0,f1,st)=>{const[a,b]=P(f0),[c,d]=P(f1); return `<line x1="${a}" y1="${b}" x2="${c}" y2="${d}" ${st}/>`;};
  if(preview) return ln(.06,.94,'stroke="#060907" stroke-width="3.6" stroke-dasharray="2 1.3" opacity=".8"')+ln(.06,.94,'stroke="#efc15a" stroke-width="2.2" stroke-dasharray="2 1.3"');
  // stone walls (Ethan, 2026-11-24: walls that fit round the castle): a thick wall with a walkway and battlements on
  // the outer edge, a round tower at each end. Each side ends at a hex corner, so walled sides meet in one tower.
  const L=Math.hypot(x2-x1,y2-y1), ux=(x2-x1)/L, uy=(y2-y1)/L, nx=-uy, ny=ux;   // along the side, and outwards
  const out=((x1+x2)/2-cx)*nx+((y1+y2)/2-cy)*ny>0?1:-1;   // which way is outside
  const C=wood?{dk:'#2a1608',body:'#8a5a30',top:'#b07a45',crest:'#d39a5a',twr:'#7a4c26',cap:'#5e3b20'}
             :{dk:'#1a1712',body:'#8f887a',top:'#b9b2a0',crest:'#dcd5c4',twr:'#a39b8a',cap:'#6f685b'};
  const seg=(f0,f1)=>{ const[a,b]=P(f0),[c,d]=P(f1), o=out*0.95, mx=nx*o, my=ny*o;
    const q=(x,y,dx,dy)=>`${(+x+dx).toFixed(2)},${(+y+dy).toFixed(2)}`;
    let g=`<line x1="${a}" y1="${b}" x2="${c}" y2="${d}" stroke="${C.dk}" stroke-width="4.4" stroke-linecap="butt"/>`
      +`<line x1="${a}" y1="${b}" x2="${c}" y2="${d}" stroke="${C.body}" stroke-width="3.2"/>`
      +`<line x1="${(+a-mx*0.5).toFixed(2)}" y1="${(+b-my*0.5).toFixed(2)}" x2="${(+c-mx*0.5).toFixed(2)}" y2="${(+d-my*0.5).toFixed(2)}" stroke="${C.top}" stroke-width="1.3"/>`;
    // battlements on the outer edge: little blocks with gaps
    const n=Math.max(2,Math.round(L*(f1-f0)/1.6));
    for(let i=0;i<n;i++){ const f=f0+(f1-f0)*(i+0.5)/n, [px,py]=P(f), w=0.55;
      g+=`<polygon points="${q(px,py,-ux*w+mx*0.2,-uy*w+my*0.2)} ${q(px,py,ux*w+mx*0.2,uy*w+my*0.2)} ${q(px,py,ux*w+mx*1.15,uy*w+my*1.15)} ${q(px,py,-ux*w+mx*1.15,-uy*w+my*1.15)}" fill="${wood?C.crest:C.crest}" stroke="${C.dk}" stroke-width=".35"/>`; }
    return g; };
  const tower=f=>{ const[px,py]=P(f); return `<circle cx="${px}" cy="${py}" r="2.35" fill="${C.twr}" stroke="${C.dk}" stroke-width=".7"/><circle cx="${px}" cy="${py}" r="1.35" fill="${C.cap}" stroke="${C.dk}" stroke-width=".35"/>`
    +(wood?'':`<circle cx="${px}" cy="${py}" r="2.35" fill="none" stroke="${C.crest}" stroke-width=".55" stroke-dasharray=".7 .55"/>`); };
  let g='';
  if(hp>=3) g+=seg(.04,.96);   // a whole wall
  else for(const q of WALL_SHOW[hp]||[]){ const [f0,f1]=WALL_PARTS[q]; g+=seg(Math.max(.04,f0),Math.min(.96,f1)); }   // a damaged one: pieces
  if(hp>=3) g+=tower(0)+tower(1);
  else if(hp>0){ const parts=(WALL_SHOW[hp]||[]).map(q=>WALL_PARTS[q]); if(parts.some(x=>x[0]<=.07)) g+=tower(0); if(parts.some(x=>x[1]>=.93)) g+=tower(1); }
  return g;
}
''' + s[b:]
open(p, 'w', encoding='utf-8').write(s); print('ok')

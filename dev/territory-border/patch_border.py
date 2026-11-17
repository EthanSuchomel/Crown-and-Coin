"""Territory borders (Ethan, 2026-11-17: "make the color border for the player tiles thinner and fix how it wraps around
the edge"). Each player's border is now one continuous line per territory outline, along the real hex edges (joined at
the corners, no notches where it turns), clipped to the territory so only its inner half shows, about half as thick as
before, with a thin dark line on the edge itself.   python3 patch_border.py index.html"""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(o, n):
    global s
    assert s.count(o) == 1, (o[:70], s.count(o)); s = s.replace(o, n)
rep('''      // territory edge: a band along every edge that borders someone else's land, with a dark outer line
      nbrDirs(i).forEach((j,k)=>{
        if(j>=0&&S.tiles[j].owner===t.owner) return;
        const[a1,b1]=hexV(cx,cy,HR-1.7,k),[a2,b2]=hexV(cx,cy,HR-1.7,k+1),[o1,p1]=hexV(cx,cy,HR-.35,k),[o2,p2]=hexV(cx,cy,HR-.35,k+1);
        own+=`<line class="ico" x1="${a1.toFixed(2)}" y1="${b1.toFixed(2)}" x2="${a2.toFixed(2)}" y2="${b2.toFixed(2)}" stroke="${col}" stroke-width="2.6" stroke-linecap="round"/><line class="ico" x1="${o1.toFixed(2)}" y1="${p1.toFixed(2)}" x2="${o2.toFixed(2)}" y2="${p2.toFixed(2)}" stroke="#060907" stroke-width=".8" opacity=".7"/>`;
      });
''', '''      // territory edge: every edge that borders someone else's land (drawn after the loop as one joined outline per player)
      const B=bord[t.owner]||(bord[t.owner]={edges:[],hexes:''});
      B.hexes+=`<polygon points="${hexPts(cx,cy,HR)}"/>`;
      nbrDirs(i).forEach((j,k)=>{ if(j>=0&&S.tiles[j].owner===t.owner) return; B.edges.push([hexV(cx,cy,HR,k),hexV(cx,cy,HR,k+1)]); });
''')
rep("  let h='', marks='', castles='', tops='', walls='', trees='', grs='', terr='', own='';",
    "  let h='', marks='', castles='', tops='', walls='', trees='', grs='', terr='', own='', bord={};")
rep("  $('#cells').innerHTML=h;", "  own+=borderSvg(bord);\n  $('#cells').innerHTML=h;")
rep("const hexV=(cx,cy,rad,k)=>{const a=Math.PI/3*k;return [cx-rad*Math.sin(a),cy-rad*Math.cos(a)];};",
    """const hexV=(cx,cy,rad,k)=>{const a=Math.PI/3*k;return [cx-rad*Math.sin(a),cy-rad*Math.cos(a)];};
// a player's border: the edges chained into closed outlines, drawn as one path (round joins), clipped to their own hexes so
// only the inner half shows (a thin band, 1.3 wide), with a thin dark line on the edge itself (Ethan, 2026-11-17)
function borderSvg(bord){
  let out='';
  for(const o in bord){
    const B=bord[o], key=([x,y])=>Math.round(x*20)+','+Math.round(y*20), next=new Map(), used=new Set();
    B.edges.forEach((e,n)=>{ const k=key(e[0]); if(!next.has(k)) next.set(k,[]); next.get(k).push(n); });
    let d='';
    B.edges.forEach((e0,n0)=>{
      if(used.has(n0)) return;
      used.add(n0); let pts=[e0[0],e0[1]], cur=e0[1];
      for(let g=0;g<400;g++){ const c=(next.get(key(cur))||[]).find(n=>!used.has(n)); if(c==null) break; used.add(c); cur=B.edges[c][1]; pts.push(cur); }
      d+='M'+pts.map(([x,y])=>x.toFixed(2)+' '+y.toFixed(2)).join('L')+(key(cur)===key(pts[0])?'Z':'');
    });
    const col=S.players[o].color;
    out+=`<clipPath id="bc-${o}">${B.hexes}</clipPath><path d="${d}" fill="none" stroke="${col}" stroke-width="2.6" stroke-linejoin="round" clip-path="url(#bc-${o})"/>`
        +`<path d="${d}" fill="none" stroke="#060907" stroke-width=".6" stroke-linejoin="round" opacity=".75"/>`;
  }
  return out;
}""")
open(p, 'w', encoding='utf-8').write(s); print('patched')

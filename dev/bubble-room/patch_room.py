"""Ethan, 2026-11-23: "When it appears and the castle or barracks is up against something it just squishes it. Can you
instead make it flexible so the purchase buttons go around the hexagon in the open spaces instead of squishing?"

The round buttons round a hex (Build, Recruit, Advancements, the unit menus, the Mythical's) are now laid out after
they're all known: if every button fits where it usually goes (on screen, clear of the cards column and the numbers box,
not touching another button), nothing changes. Otherwise they're spread round the hex into the open space, in the same
order, on a ring at the hex's edge; if that ring has too little open space, a wider ring, and only then smaller buttons.
Usage: python3 patch_room.py index.html"""
import sys
P = sys.argv[1]; s = open(P).read()
def rep(a, b, n=1):
    global s; c = s.count(a); assert c == n, (c, a[:100]); s = s.replace(a, b)

a = s.index("function placeBubbles(show){")
b = s.index("function renderMap(){", a)
body = s[a:b]
def brep(x, y, n=1):
    global body; c = body.count(x); assert c == n, (c, x[:100]); body = body.replace(x, y)

# the corner post and the ring post only note where their button wants to go; finish() places them all at once
brep("""  const post=(vi,deg)=>{
    const [hx,hy]=P(...hexV(cx,cy,HR,vi)), a=deg*Math.PI/180, ux=Math.cos(a), uy=-Math.sin(a);
    const bx=hx+ux*(stem+R), by=hy+uy*(stem+R), nx=-uy*R*.2, ny=ux*R*.2;
    for(const sg of [-1,1]){ const x1=(hx+sg*nx).toFixed(1), y1=(hy+sg*ny).toFixed(1), x2=(hx+ux*(stem+4)+sg*nx).toFixed(1), y2=(hy+uy*(stem+4)+sg*ny).toFixed(1);
      lines+=`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#060907" stroke-width="4.5" stroke-linecap="round"/><line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#ece4cf" stroke-width="2"/>`; }
    return `style="left:${bx.toFixed(1)}px;top:${by.toFixed(1)}px;width:${(2*R).toFixed(1)}px;height:${(2*R).toFixed(1)}px"`;
  };""", """  const slots=[];   // every button's wished-for spot; finish() lays them out (into open space if they don't fit)
  const post=(vi,deg)=>{ slots.push({vi,deg,r:R}); return `__SLOT${slots.length-1}__`; };""")
brep("""  const rpost=deg=>{ const a=deg*Math.PI/180, ux=Math.cos(a), uy=-Math.sin(a), nx=-uy*rr*.2, ny=ux*rr*.2, r0=hr*.86;
    for(const sg of [-1,1]){ const x1=(hcx+ux*r0+sg*nx).toFixed(1), y1=(hcy+uy*r0+sg*ny).toFixed(1), x2=(hcx+ux*(ring-rr+4)+sg*nx).toFixed(1), y2=(hcy+uy*(ring-rr+4)+sg*ny).toFixed(1);
      lines+=`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#060907" stroke-width="4.5" stroke-linecap="round"/><line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#ece4cf" stroke-width="2"/>`; }
    return `style="left:${(hcx+ux*ring).toFixed(1)}px;top:${(hcy+uy*ring).toFixed(1)}px;width:${(2*rr).toFixed(1)}px;height:${(2*rr).toFixed(1)}px;font-size:calc(.78em * ${rfs})"`; };""",
     """  const rpost=(deg,r1)=>{ slots.push({vi:null,deg,r:r1||rr}); return `__SLOT${slots.length-1}__`; };
  const finish=html=>{ ov.hidden=false; ov.innerHTML=bubLayout(ov,slots,html,{P,cx,cy,hcx,hcy,hr,stem,R}); requestAnimationFrame(()=>{ void ov.offsetWidth; ov.classList.add('show'); }); };""")
brep("""  if(isMyth(0)){ const m=mythBubbles(P,cx,cy,k,R,stem); ov.hidden=false; ov.innerHTML=`<svg aria-hidden="true">${m.lines}</svg>${m.html}`; requestAnimationFrame(()=>{ void ov.offsetWidth; ov.classList.add('show'); }); return; }""",
     """  if(isMyth(0)){ finish(mythBubbles(P,cx,cy,k,R,stem,rpost).html); return; }""")
for x in ["""    ov.hidden=false; ov.innerHTML=`<svg aria-hidden="true">${lines}</svg>${html}`;
    requestAnimationFrame(()=>{ void ov.offsetWidth; ov.classList.add('show'); });
    return;"""]:
    brep(x, """    finish(html);
    return;""", 3)
# the Build buttons draw their own post; they go through post() too now
brep("""  for(const [kind,deg,vi] of spots){
    const [hx,hy]=P(...hexV(cx,cy,HR,vi)), a=deg*Math.PI/180, ux=Math.cos(a), uy=-Math.sin(a);
    const bx=hx+ux*(stem+R), by=hy+uy*(stem+R), nx=-uy*R*.2, ny=ux*R*.2;
    for(const sg of [-1,1]){ const x1=(hx+sg*nx).toFixed(1), y1=(hy+sg*ny).toFixed(1), x2=(hx+ux*(stem+4)+sg*nx).toFixed(1), y2=(hy+uy*(stem+4)+sg*ny).toFixed(1);
      lines+=`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#060907" stroke-width="4.5" stroke-linecap="round"/><line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#ece4cf" stroke-width="2"/>`; }
    const pos=`style="left:${bx.toFixed(1)}px;top:${by.toFixed(1)}px;width:${(2*R).toFixed(1)}px;height:${(2*R).toFixed(1)}px"`;""",
     """  for(const [kind,deg,vi] of spots){
    const pos=post(vi,deg);""")
brep("""  ov.hidden=false;
  ov.innerHTML=`<svg aria-hidden="true">${lines}</svg>${html}`;
  requestAnimationFrame(()=>{ void ov.offsetWidth; ov.classList.add('show'); });
}""", """  finish(html);
}""")
s = s[:a] + body + s[b:]

# the Mythical's ring of buttons goes through the same slots
rep("""function mythBubbles(P,cx,cy,k,R,stem){
  const items=mythBubbleItems(S.tiles[_zoomHex]); let lines='', html='';
  const [hcx,hcy]=P(cx,cy), hr=HR*k, r=items.length>3?Math.min(R,(hr*.95+stem)/1.75):R, ring=hr*.95+stem+r, fsz=(r/R).toFixed(3);
  const rpost=deg=>{ const a=deg*Math.PI/180, ux=Math.cos(a), uy=-Math.sin(a), nx=-uy*r*.2, ny=ux*r*.2, r0=hr*.86;
    for(const sg of [-1,1]){ const x1=(hcx+ux*r0+sg*nx).toFixed(1), y1=(hcy+uy*r0+sg*ny).toFixed(1), x2=(hcx+ux*(ring-r+4)+sg*nx).toFixed(1), y2=(hcy+uy*(ring-r+4)+sg*ny).toFixed(1);
      lines+=`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#060907" stroke-width="4.5" stroke-linecap="round"/><line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#ece4cf" stroke-width="2"/>`; }
    return `style="left:${(hcx+ux*ring).toFixed(1)}px;top:${(hcy+uy*ring).toFixed(1)}px;width:${(2*r).toFixed(1)}px;height:${(2*r).toFixed(1)}px;font-size:calc(.78em * ${fsz})"`; };""",
    """function mythBubbles(P,cx,cy,k,R,stem,slot){
  const items=mythBubbleItems(S.tiles[_zoomHex]); let lines='', html='';
  const hr=HR*k, r=items.length>3?Math.min(R,(hr*.95+stem)/1.75):R, rpost=deg=>slot(deg,r);""")

# the layout
anchor = "function placeBubbles(show){"
s = s.replace(anchor, r"""// Lays out the round buttons round a hex (Ethan, 2026-11-23: "make it flexible so the purchase buttons go around the hexagon in
// the open spaces instead of squishing"). Each slot wants a spot: off a hex corner (vi, deg) or on the ring round the hex (deg).
// If every wished-for spot is on the map's open part of the screen (not off screen, not under the cards or the numbers box)
// and no two buttons touch, they stay there. Otherwise they keep their order round the hex and spread into the open arcs of a
// ring at the hex's edge; a wider ring if the open arc is too short, then smaller buttons. Returns the posts and the buttons.
function bubLayout(ov,slots,html,g){
  const {P,cx,cy,hcx,hcy,hr,stem,R}=g, n=slots.length;
  if(!n) return html;
  const ob=ov.getBoundingClientRect(), M=4, blocks=[];
  const add=el=>{ if(!el||el.hidden) return; const b=el.getBoundingClientRect(); if(b.width>2&&b.height>2&&getComputedStyle(el).visibility!=='hidden'&&+getComputedStyle(el).opacity>.05) blocks.push([b.left-ob.left-M,b.top-ob.top-M,b.right-ob.left+M,b.bottom-ob.top+M]); };
  add(document.querySelector('#app .side')); add(document.getElementById('stats'));
  const W=ov.clientWidth, H=ov.clientHeight;
  const fits=(x,y,r)=>x-r>=M&&y-r>=M&&x+r<=W-M&&y+r<=H-M&&!blocks.some(([l,t,rt,bt])=>{ const qx=Math.max(l,Math.min(x,rt)), qy=Math.max(t,Math.min(y,bt)); return (qx-x)**2+(qy-y)**2<r*r; });
  const apart=ps=>ps.every((p,i)=>ps.every((q,j)=>j<=i||Math.hypot(p.x-q.x,p.y-q.y)>=p.r+q.r+2));
  // where each button usually goes. Buttons on the ring keep their full size: when the hex is small on screen the ring
  // widens so they don't overlap (they used to shrink to fit round it, which squashed them)
  const rd=slots.filter(sl=>sl.vi==null).map(sl=>sl.deg);
  let dmin=360; rd.forEach((a,i)=>rd.forEach((b,j)=>{ if(j>i) dmin=Math.min(dmin,Math.abs(((a-b+540)%360)-180)); }));
  const ringR=Math.max(hr*.95+stem+R, rd.length>1?(R+3)/Math.sin(Math.max(1,dmin)/2*Math.PI/180):0);
  let ps=slots.map(sl=>{ const a=sl.deg*Math.PI/180, ux=Math.cos(a), uy=-Math.sin(a);
    if(sl.vi!=null){ const [hx,hy]=P(...hexV(cx,cy,HR,sl.vi)); return {x:hx+ux*(stem+sl.r), y:hy+uy*(stem+sl.r), r:sl.r, ux, uy, fx:hx, fy:hy, ring:false}; }
    return {x:hcx+ux*ringR, y:hcy+uy*ringR, r:R, ux, uy, ring:true}; });
  if(!(ps.every(p=>fits(p.x,p.y,p.r))&&apart(ps))){
    // into the open space: the buttons in their usual order round the hex, on one ring
    const norm=d=>((d%360)+360)%360, want=slots.map(sl=>norm(sl.deg));
    const tryRing=(r,extra)=>{
      const ring=hr*.95+stem+r+extra, step=2, ok=[];
      for(let d=0;d<360;d+=step){ const a=d*Math.PI/180; ok.push(fits(hcx+Math.cos(a)*ring,hcy-Math.sin(a)*ring,r)); }
      if(!ok.some(Boolean)) return null;
      const gap=2*Math.asin(Math.min(1,(r+2)/ring))*180/Math.PI;   // degrees between two button centres
      if(n*gap>360) return null;
      // the open arcs (runs of open degrees round the circle)
      const N=ok.length, arcs=[]; let st=ok.indexOf(false);
      if(st<0) arcs.push([0,360]); else for(let i=1;i<=N;i++){ const j=(st+i)%N; if(ok[j]&&!ok[(j-1+N)%N]) arcs.push([j*step,0]); if(ok[j]&&!ok[(j+1)%N]) arcs[arcs.length-1][1]=j*step; }
      const len=a=>a[1]>=a[0]?a[1]-a[0]:a[1]+360-a[0];
      // the arc nearest where the buttons usually are that holds them all
      const mean=Math.atan2(want.reduce((t,d)=>t+Math.sin(d*Math.PI/180),0),want.reduce((t,d)=>t+Math.cos(d*Math.PI/180),0))*180/Math.PI;
      const need=(n-1)*gap, dist=(a,b)=>Math.abs(((a-b+540)%360)-180);
      const fit=arcs.filter(a=>arcs.length===1&&a[1]-a[0]>=360||len(a)>=need).sort((p,q)=>dist(norm(p[0]+len(p)/2),mean)-dist(norm(q[0]+len(q)/2),mean))[0];
      if(!fit){   // no one open arc holds them all: spread them over several, in order, each a button apart
        if(st<0) return null;
        const at=[]; let last=-1e9;
        for(let i=1;i<=N;i++){ const d=(st+i)*step; if(ok[(st+i)%N]&&d-last>=gap&&(at.length===0||d-at[0]<=360-gap)){ at.push(d); last=d; } }
        if(at.length<n) return null;
        // the n of them closest together round the usual direction
        let bi=0, bv=1e9; for(let i=0;i+n<=at.length;i++){ const mid=norm((at[i]+at[i+n-1])/2), v=dist(mid,mean)+(at[i+n-1]-at[i])*.2; if(v<bv){ bv=v; bi=i; } }
        const use=at.slice(bi,bi+n), base2=norm(use[0]), order2=slots.map((sl,i)=>i).sort((i,j)=>norm(want[i]-base2)-norm(want[j]-base2)), out2=new Array(n);
        order2.forEach((si,k)=>{ const a=use[k]*Math.PI/180, ux=Math.cos(a), uy=-Math.sin(a); out2[si]={x:hcx+ux*ring, y:hcy+uy*ring, r, ux, uy, ring:true}; });
        return out2;
      }
      const full=fit[1]-fit[0]>=360, L=full?360:len(fit);
      // even steps, a little wider than touching when there's room; then the start angle and the turn of the (circular)
      // order that keep the buttons closest to their usual spots, every one on open ground
      const sp=full?Math.min(360/n,gap*1.25):Math.max(gap,Math.min(gap*1.3,n>1?L/(n-1):gap));
      const ord=slots.map((sl,i)=>i).sort((i,j)=>want[i]-want[j]), open=d=>ok[Math.round(norm(d)/step)%N];
      let best=null, bc=1e9;
      for(let c0=0;c0<360;c0+=2) for(let rot=0;rot<n;rot++){
        let cost=0, good=true;
        for(let k=0;k<n&&good;k++){ const d=c0+k*sp; if(!open(d)) good=false; else cost+=dist(norm(d),want[ord[(k+rot)%n]]); }
        if(good&&cost<bc){ bc=cost; best=[c0,rot]; } }
      if(!best) return null;
      const out=new Array(n);
      for(let k=0;k<n;k++){ const si=ord[(k+best[1])%n], a=(best[0]+k*sp)*Math.PI/180, ux=Math.cos(a), uy=-Math.sin(a);
        out[si]={x:hcx+ux*ring, y:hcy+uy*ring, r, ux, uy, ring:true}; }
      return out;
    };
    const big=R, rr=Math.min(big,(hr*.95+stem)/1.75);
    let got=null;   // full-size buttons on a ring that widens; smaller buttons only if nothing else fits
    for(const [r,extra] of [[big,0],[big,big*.6],[big,big*1.2],[big,big*1.8],[big,big*2.6],[big*.85,big*1.8],[rr,rr*1.8],[rr*.8,rr*2.4]]){ got=tryRing(r,extra); if(got&&got.every(p=>fits(p.x,p.y,p.r))&&apart(got)) break; got=null; }
    if(got) ps=got;
  }
  let lines='';
  ps.forEach(p=>{ const nx=-p.uy*p.r*.2, ny=p.ux*p.r*.2;
    const [x0,y0]=p.ring?[hcx+p.ux*hr*.86,hcy+p.uy*hr*.86]:[p.fx,p.fy], len=Math.hypot(p.x-x0,p.y-y0)-p.r+4;
    for(const sg of [-1,1]){ const x1=(x0+sg*nx).toFixed(1), y1=(y0+sg*ny).toFixed(1), x2=(x0+p.ux*len+sg*nx).toFixed(1), y2=(y0+p.uy*len+sg*ny).toFixed(1);
      lines+=`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#060907" stroke-width="4.5" stroke-linecap="round"/><line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#ece4cf" stroke-width="2"/>`; } });
  html=html.replace(/__SLOT(\d+)__/g,(m,i)=>{ const p=ps[+i], f=(slots[+i].vi==null||p.r<R-.01)?`;font-size:calc(.78em * ${(p.r/R).toFixed(3)})`:'';
    return `style="left:${p.x.toFixed(1)}px;top:${p.y.toFixed(1)}px;width:${(2*p.r).toFixed(1)}px;height:${(2*p.r).toFixed(1)}px${f}"`; });
  return `<svg aria-hidden="true">${lines}</svg>${html}`;
}
""" + anchor, 1)
open(P, 'w').write(s); print('ok')

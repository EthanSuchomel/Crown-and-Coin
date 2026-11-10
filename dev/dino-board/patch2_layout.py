# Dinosaur board rework, step 2: room for 6 barracks units (barracks menu and home-castle ring).
import sys,re
p=sys.argv[1]; s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:100]); s=s.replace(a,b)
# a ring of buttons all round the hex (used when there are more than fit on the corners)
rep("""  if(isMyth(0)){ const m=mythBubbles(P,cx,cy,k,R,stem);""",
"""  // a ring of smaller buttons all round the hex, for when more than fit on the corners
  const [hcx,hcy]=P(cx,cy), hr=HR*k, rr=Math.min(R,(hr*.95+stem)/1.75), ring=hr*.95+stem+rr, rfs=(rr/R).toFixed(3);
  const rpost=deg=>{ const a=deg*Math.PI/180, ux=Math.cos(a), uy=-Math.sin(a), nx=-uy*rr*.2, ny=ux*rr*.2, r0=hr*.86;
    for(const sg of [-1,1]){ const x1=(hcx+ux*r0+sg*nx).toFixed(1), y1=(hcy+uy*r0+sg*ny).toFixed(1), x2=(hcx+ux*(ring-rr+4)+sg*nx).toFixed(1), y2=(hcy+uy*(ring-rr+4)+sg*ny).toFixed(1);
      lines+=`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#060907" stroke-width="4.5" stroke-linecap="round"/><line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#ece4cf" stroke-width="2"/>`; }
    return `style="left:${(hcx+ux*ring).toFixed(1)}px;top:${(hcy+uy*ring).toFixed(1)}px;width:${(2*rr).toFixed(1)}px;height:${(2*rr).toFixed(1)}px;font-size:calc(.78em * ${rfs})"`; };
  if(isMyth(0)){ const m=mythBubbles(P,cx,cy,k,R,stem);""")
# the barracks menu: 6 units (Dinosaurs) go round the hex with Back at the bottom
rep("""    const list=UNITS[me.faction][menu], at=list.length===4?[[1,150],[5,30],[2,210],[4,330]]:[[1,150],[0,90],[5,30]];
    list.forEach(([k,nm,full],i)=>{ const pos=post(...at[i]),""",
"""    const list=UNITS[me.faction][menu], at=list.length===4?[[1,150],[5,30],[2,210],[4,330]]:[[1,150],[0,90],[5,30]];
    const big=list.length>4, ringAt=[167.1,115.7,64.3,12.9,321.4,218.6];   // 6 units and Back, evenly round the hex (Back at the bottom)
    list.forEach(([k,nm,full],i)=>{ const pos=big?rpost(ringAt[i]):post(...at[i]),""")
rep("""    html+=`<button class="bub back" data-tb="back" ${post(3,270)}""","""    html+=`<button class="bub back" data-tb="back" ${big?rpost(270):post(3,270)}""")
# the home-castle ring: drop its own copy of the ring maths; with no fort units, the barracks units fill the ring
rep("""      const [hcx,hcy]=P(cx,cy), hr=HR*k, r=Math.min(R,(hr*.95+stem)/1.75), ring=hr*.95+stem+r, fsz=(r/R).toFixed(3);
      const rpost=deg=>{ const a=deg*Math.PI/180, ux=Math.cos(a), uy=-Math.sin(a), nx=-uy*r*.2, ny=ux*r*.2, r0=hr*.86;
        for(const sg of [-1,1]){ const x1=(hcx+ux*r0+sg*nx).toFixed(1), y1=(hcy+uy*r0+sg*ny).toFixed(1), x2=(hcx+ux*(ring-r+4)+sg*nx).toFixed(1), y2=(hcy+uy*(ring-r+4)+sg*ny).toFixed(1);
          lines+=`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#060907" stroke-width="4.5" stroke-linecap="round"/><line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#ece4cf" stroke-width="2"/>`; }
        return `style="left:${(hcx+ux*ring).toFixed(1)}px;top:${(hcy+uy*ring).toFixed(1)}px;width:${(2*r).toFixed(1)}px;height:${(2*r).toFixed(1)}px;font-size:calc(.78em * ${fsz})"`; };
""","")
rep("""        .concat(UNITS[F].barracks.map(x=>x[0]).filter(x=>x!==bk).map((x,i)=>[x,'barracks',[150,195,240][i]]))""",
"""        .concat(UNITS[F].barracks.map(x=>x[0]).filter(x=>x!==bk).map((x,i,a)=>[x,'barracks',(UNITS[F].fort.length?[150,195,240]:[150,210,270,330,30])[i]]))""")
open(p,'w').write(s); print('patch2 ok')

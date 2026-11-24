"""Ethan, 2026-11-24: "make some walls that we can place around the game tiles with OpenArt, on theme with the new
neutral castle; these walls are used for every faction's walls". The OpenArt sheet he picked (Game buildings) is cut
into three pieces (art/wall_d0.png: a run going down to the right, wall_d1.png: a run going up to the right,
wall_tw.png: a round tower with the keep's blue roof). Each walled hex side is one run, sheared so its base lies on the
side while its verticals stay upright; the two upright sides of a hex are drawn as two runs meeting at a tower just
outside the side (a little bastion), since the art has no wall running straight up and down. Towers stand at the
corners. A damaged wall keeps only its pieces. Walls on the back half of a hex are drawn behind its castle, the rest in
front.
Usage: python3 patch_wallart.py index.html"""
import sys, os, json, base64, io
from PIL import Image
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
here = os.path.dirname(os.path.abspath(__file__))
J = json.load(open(os.path.join(here, 'art', 'walls.json')))
for k in J:
    im = Image.open(os.path.join(here, 'art', 'wall_%s.png' % k)); b = io.BytesIO(); im.save(b, 'WEBP', lossless=True)
    J[k]['uri'] = 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, a[:120]); s = s.replace(a, b)
rep("// ---------- building on the map ----------", r'''// The castle's stone walls from OpenArt (Ethan, 2026-11-24): every faction's walls. d0 runs down to the right, d1 up
// to the right (s and e: the ends of the wall's centre line on the ground, in picture pixels), tw is a tower (f: its foot).
const WALL_ART=%s, WALL_VS=0.8, WALL_BASTION=1.8;
// one run of wall whose ground line goes from a to b (board units, a left of b), optionally only the part t0..t1 of it
function wallRun(a,b,t0,t1){
  const down=b[1]>a[1], P=down?WALL_ART.d0:WALL_ART.d1, dPx=P.e[0]-P.s[0], dPy=P.e[1]-P.s[1];
  const sc=(b[0]-a[0])/dPx, D=sc*WALL_VS, B=((b[1]-a[1])-D*dPy)/dPx, E=a[0]-sc*P.s[0], F=a[1]-B*P.s[0]-D*P.s[1];
  let clip='';
  if(t0>0.001||t1<0.999){ const L=(t)=>[a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t], p0=L(t0), p1=L(t1), id='wc'+(++_wcN);
    clip=` clip-path="url(#${id})"`;
    return `<clipPath id="${id}"><polygon points="${p0[0].toFixed(2)},${(p0[1]+4).toFixed(2)} ${p1[0].toFixed(2)},${(p1[1]+4).toFixed(2)} ${p1[0].toFixed(2)},${(p1[1]-16).toFixed(2)} ${p0[0].toFixed(2)},${(p0[1]-16).toFixed(2)}"/></clipPath>`
      +`<g${clip}><use href="#wl-${down?'d0':'d1'}" transform="matrix(${sc.toFixed(5)} ${B.toFixed(5)} 0 ${D.toFixed(5)} ${E.toFixed(3)} ${F.toFixed(3)})"/></g>`; }   // (the clip on a group, so it's in board units)
  return `<use href="#wl-${down?'d0':'d1'}" transform="matrix(${sc.toFixed(5)} ${B.toFixed(5)} 0 ${D.toFixed(5)} ${E.toFixed(3)} ${F.toFixed(3)})"/>`;
}
let _wcN=0;
const wallScale=()=>(HR-2.3)*Math.sqrt(3)/2/(WALL_ART.d0.e[0]-WALL_ART.d0.s[0]);
function wallTower(x,y){ const sc=wallScale(), D=sc*WALL_VS, T=WALL_ART.tw;
  return `<use href="#wl-tw" transform="matrix(${sc.toFixed(5)} 0 0 ${D.toFixed(5)} ${(x-T.f[0]*sc).toFixed(3)} ${(y-T.f[1]*D).toFixed(3)})"/>`; }
// side k of the hex at cx,cy with hp: [behind the castle, in front of it]
function wallArt(cx,cy,k,hp){
  const r=HR-2.3, A=hexV(cx,cy,r,k), Bc=hexV(cx,cy,r,k+1);
  const parts=hp>=3?[[0,1]]:hp===2?[[0,.38],[.62,1]]:[[.36,.64]];
  // the side as one or two straight runs (an upright side: two runs meeting at a little bastion outside it)
  let legs;
  if(Math.abs(A[0]-Bc[0])<0.01){ const out=A[0]<cx?-1:1, M=[A[0]+out*WALL_BASTION,(A[1]+Bc[1])/2]; legs=[[A,M,0,.5],[M,Bc,.5,1]]; }
  else legs=[[A,Bc,0,1]];
  let back='', front='', tb='', tf='';
  for(const [p,q,u0,u1] of legs){ const L=p[0]<=q[0]?[p,q,false]:[q,p,true];
    for(const [t0,t1] of parts){ const a0=Math.max(t0,u0), a1=Math.min(t1,u1); if(a1-a0<0.02) continue;
      let l0=(a0-u0)/(u1-u0), l1=(a1-u0)/(u1-u0); if(L[2]){ const x=l0; l0=1-l1; l1=1-x; }
      const g=wallRun(L[0],L[1],l0,l1); if((L[0][1]+L[1][1])/2<cy) back+=g; else front+=g; } }
  const tw=(x,y)=>{ const g=wallTower(x,y); if(y<cy) tb+=g; else tf+=g; };
  if(hp>=2){ tw(A[0],A[1]); tw(Bc[0],Bc[1]); }
  return [back+tb, front+tf];
}
// ---------- building on the map ----------''' % json.dumps(J))
rep("  d+=img('wa',ART.water_img,+HH.toFixed(2),2*HR,0);", "  d+=img('wa',ART.water_img,+HH.toFixed(2),2*HR,0);\n  for(const k of ['d0','d1','tw']) d+=img('wl-'+k,WALL_ART[k].uri,WALL_ART[k].w,WALL_ART[k].h,0);   // the stone walls (2026-11-24)")
rep("    if(t.walls) t.walls.forEach((hp,k)=>{ if(hp>0) walls+=wallSvg(cx,cy,k,hp,false,false); });   // every faction's walls are the castle's stone walls (Ethan, 2026-11-24)",
    "    let wfront='';   // every faction's walls are the castle's stone walls (Ethan, 2026-11-24): behind the castle, or in front of it\n    if(t.walls) [0,5,1,4,2,3].forEach(k=>{ const hp=t.walls[k]; if(hp>0){ const [wb,wf]=wallArt(cx,cy,k,hp); walls+=wb; wfront+=wf; } });")
rep("    if(swords) castles+=`<image href=\"${ART.swords}\"", "    castles+=wfront;\n    if(swords) castles+=`<image href=\"${ART.swords}\"")
open(p, 'w', encoding='utf-8').write(s); print('ok')

"""Ethan, 2026-11-24: the OpenArt wall piece that runs straight up and down (art/wall_v.png, his pick from Game
buildings) for the two upright sides of each hex, in place of the stand-in drawn wall. It's scaled so its near end sits
on the lower corner and its far end on the upper corner; damaged walls show only their pieces.
Usage: python3 patch_wallv.py index.html"""
import sys, os, json, base64, io
from PIL import Image
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
here = os.path.dirname(os.path.abspath(__file__))
V = json.load(open(os.path.join(here, 'art', 'walls.json')))['v']
im = Image.open(os.path.join(here, 'art', 'wall_v.png')); b = io.BytesIO(); im.save(b, 'WEBP', lossless=True)
V['uri'] = 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, a[:120]); s = s.replace(a, b)
rep("let _wcN=0;", """let _wcN=0;
WALL_ART.v=%s;   // the wall running straight up and down (Ethan's pick, 2026-11-24): t and b, its far and near ends on the ground
const WALL_VW=0.95;   // its width, against its length
// an upright side from a (top) to b (bottom), optionally only the part t0..t1 of it (from the top)
function wallUp(a,b,t0,t1){ const V=WALL_ART.v, sy=(b[1]-a[1])/(V.b-V.t), sx=sy*WALL_VW, E=a[0]-V.cx*sx, F=a[1]-V.t*sy;
  const u=`<use href="#wl-v" transform="matrix(${sx.toFixed(5)} 0 0 ${sy.toFixed(5)} ${E.toFixed(3)} ${F.toFixed(3)})"/>`;
  if(t0<=0.001&&t1>=0.999) return u;
  const y0=a[1]+(b[1]-a[1])*t0-(t0<=0.001?6:0), y1=a[1]+(b[1]-a[1])*t1+(t1>=0.999?6:0), id='wc'+(++_wcN);
  return `<clipPath id="${id}"><rect x="${(a[0]-8).toFixed(2)}" y="${y0.toFixed(2)}" width="16" height="${(y1-y0).toFixed(2)}"/></clipPath><g clip-path="url(#${id})">${u}</g>`; }""" % json.dumps(V))
rep("for(const k of ['d0','d1','tw']) d+=img('wl-'+k,", "for(const k of ['d0','d1','tw','v']) d+=img('wl-'+k,")
rep("""  if(Math.abs(A[0]-Bc[0])<0.01){   // an upright side: the stone wall drawn in its colours (no OpenArt piece for it yet)
    back+=wallSvg(cx,cy,k,hp,false,false,true); }""", """  if(Math.abs(A[0]-Bc[0])<0.01){   // an upright side: the wall running straight up and down
    const top=A[1]<Bc[1], T=top?A:Bc, Bt=top?Bc:A;
    for(const [t0,t1] of parts){ const l0=top?t0:1-t1, l1=top?t1:1-t0; back+=wallUp(T,Bt,l0,l1); } }""")
open(p, 'w', encoding='utf-8').write(s); print('ok')

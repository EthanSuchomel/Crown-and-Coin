"""Ethan, 2026-11-24: "all the walls look like stickers instead of connecting together to create a solid wall". Each
wall picture has its own end faces and outlines, so every side looked like a separate block. Now every run is cut
flush at the hex corners (its end faces trimmed off, a hair of overlap so neighbours meet without a gap), and the
up-and-down wall is cut flush at its far corner too; the corner tower sits over each join.
Usage: python3 patch_flush.py index.html   (after patch_wallfix.py)"""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, a[:120]); s = s.replace(a, b)
rep("""  if(t0>0.001||t1<0.999){ const L=(t)=>[a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t], p0=L(t0), p1=L(t1), id='wc'+(++_wcN);""",
    """  { const L=(t)=>[a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t], ex=0.2/Math.hypot(b[0]-a[0],b[1]-a[1]),   // always cut flush at the corners (2026-11-24)
      p0=L(t0<=0.001?-ex:t0), p1=L(t1>=0.999?1+ex:t1), id='wc'+(++_wcN);""")
rep("""      +`<g${clip}><use href="#wl-${down?'d0':'d1'}" transform="matrix(${sc.toFixed(5)} ${B.toFixed(5)} 0 ${D.toFixed(5)} ${E.toFixed(3)} ${F.toFixed(3)})"/></g>`; }   // (the clip on a group, so it's in board units)
  return `<use href="#wl-${down?'d0':'d1'}" transform="matrix(${sc.toFixed(5)} ${B.toFixed(5)} 0 ${D.toFixed(5)} ${E.toFixed(3)} ${F.toFixed(3)})"/>`;
}""", """      +`<g${clip}><use href="#wl-${down?'d0':'d1'}" transform="matrix(${sc.toFixed(5)} ${B.toFixed(5)} 0 ${D.toFixed(5)} ${E.toFixed(3)} ${F.toFixed(3)})"/></g>`; }   // (the clip on a group, so it's in board units)
}""")
rep("""  if(t0<=0.001&&t1>=0.999) return u;
  const y0=a[1]+(b[1]-a[1])*t0-(t0<=0.001?6:0),""", """  // cut flush at the far corner (2026-11-24); the near end stays (under its tower)\n  const y0=a[1]+(b[1]-a[1])*t0-(t0<=0.001?0.2:0),""")
open(p, 'w', encoding='utf-8').write(s); print('ok')

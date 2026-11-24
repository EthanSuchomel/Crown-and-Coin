"""Ethan, 2026-11-24: "if there aren't any walls attaching to the (corner) tower it doesn't appear". A corner tower is
drawn only where a piece of wall that's actually drawn reaches that corner. Also fixed: a damaged wall's pieces were
clipped away entirely (the clip was in the picture's own units), which left towers standing alone; and the two upright
sides of a hex came out as slivers (the art has no straight up-and-down wall), so they're drawn as the stone wall in
the same colours (no round towers of their own) until an OpenArt piece for them is in.
Usage: python3 patch_lonetower.py index.html"""
import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, a[:120]); s = s.replace(a, b)
rep("function wallSvg(cx,cy,k,hp,preview,wood){", "function wallSvg(cx,cy,k,hp,preview,wood,noTowers){")
rep("  if(hp>=3) g+=tower(0)+tower(1);", "  if(noTowers) return g;\n  if(hp>=3) g+=tower(0)+tower(1);")
a = s.index("  // the side as one or two straight runs (an upright side: two runs meeting at a little bastion outside it)")
b = s.index("  return [back+tb, front+tf];\n}")
s = s[:a] + """  let back='', front='', tb='', tf='';
  if(Math.abs(A[0]-Bc[0])<0.01){   // an upright side: the stone wall drawn in its colours (no OpenArt piece for it yet)
    back+=wallSvg(cx,cy,k,hp,false,false,true); }
  else for(const [t0,t1] of parts){ const L=A[0]<=Bc[0]?[A,Bc,false]:[Bc,A,true];
    let l0=t0, l1=t1; if(L[2]){ l0=1-t1; l1=1-t0; }
    const g=wallRun(L[0],L[1],l0,l1); if((A[1]+Bc[1])/2<cy) back+=g; else front+=g; }
  // a corner tower only where a piece of wall reaches the corner (Ethan, 2026-11-24: no lone towers)
  const tw=(x,y)=>{ const g=wallTower(x,y); if(y<cy) tb+=g; else tf+=g; };
  if(parts.some(q=>q[0]<=0.01)) tw(A[0],A[1]);
  if(parts.some(q=>q[1]>=0.99)) tw(Bc[0],Bc[1]);
""" + s[b:]
open(p, 'w', encoding='utf-8').write(s); print('ok')

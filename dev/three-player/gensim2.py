import json,random
import board3 as B
from board3 import man,N,cube,from_cube
b=json.load(open('board3.json')); VOID=set(b['void']); HOMES=[78,16,86]; C=b['center']
cx,cy,cz=cube(C)
def rot(i):
    x,y,z=cube(i); x,y,z=x-cx,y-cy,z-cz; return from_cube(z+cx,x+cy,y+cz)
assert all(rot(h) in HOMES for h in HOMES)
assert all((rot(i) in VOID)==(i in VOID) for i in range(N*N) if rot(i) is not None)
cells=[i for i in range(N*N) if i not in VOID]
def castles_sym():
    cs=[]
    for g in range(200):
        i=random.choice(cells); orb={i,rot(i),rot(rot(i))}
        if len(orb)<3 or any(o in HOMES for o in orb): continue
        if any(min(man(o,h) for h in HOMES)<3 for o in orb): continue
        if any(man(o,c)<3 for o in orb for c in cs): continue
        if any(man(a,c)<3 for a in orb for c in orb if a!=c): continue
        cs+=list(orb)
        if len(cs)>=6: return cs
    return None
ok=0; fails={'castle':0,'blk':0,'coins':0,'conn':0}
import collections
def bfs(src,blocked):
    d={src:0};q=[src]
    while q:
        u=q.pop(0)
        for v in cells:
            pass
    return d
def nbrs(i):
    r,c=divmod(i,N); odd=c&1
    d=[[1,1],[1,0],[1,-1],[0,-1],[-1,0],[0,1]] if odd else [[0,1],[1,0],[0,-1],[-1,-1],[-1,0],[-1,1]]
    out=[]
    for dr,dc in d:
        rr,cc=r+dr,c+dc
        if 0<=rr<N and 0<=cc<N and rr*N+cc not in VOID: out.append(rr*N+cc)
    return out
T=3000
for t in range(T):
    cs=castles_sym()
    if not cs: fails['castle']+=1; continue
    free=[i for i in cells if i not in HOMES and i not in cs]
    blocked=set(random.sample(free,14)); mtn=list(blocked)[:10]
    blk=[sum(4-man(x,h) for x in blocked if man(x,h)<=3) for h in HOMES]
    if max(blk)-min(blk)>2 or any(man(x,h)<=1 for x in blocked for h in HOMES): fails['blk']+=1; continue
    # connectivity
    seen={HOMES[0]};q=[HOMES[0]]
    while q:
        u=q.pop()
        for v in nbrs(u):
            if v not in seen and v not in blocked: seen.add(v); q.append(v)
    if any(i not in seen for i in cells if i not in blocked): fails['conn']+=1; continue
    pool=[i for i in cells if i not in blocked and i not in HOMES and i not in cs]
    good=False
    for k in range(400):
        pick=random.sample(pool,26); sums=[0,0,0]; near=[0,0,0]
        for x in pick:
            ds=[man(x,h) for h in HOMES]; m=min(ds)
            for j in range(3): sums[j]+=ds[j]
            if ds.count(m)==1: near[ds.index(m)]+=1
        if max(sums)-min(sums)<=2 and max(near)==min(near): good=True; break
    if not good: fails['coins']+=1; continue
    ok+=1
print('ok',ok,'of',T,fails)

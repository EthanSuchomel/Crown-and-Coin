import json,random
from board3 import man,N,cube,from_cube
b=json.load(open('board3.json')); VOID=set(b['void']); HOMES=[78,16,86]; C=b['center']
cx,cy,cz=cube(C)
def rot(i):
    x,y,z=cube(i); x,y,z=x-cx,y-cy,z-cz; return from_cube(z+cx,x+cy,y+cz)
cells=[i for i in range(N*N) if i not in VOID]
def nbrs(i):
    r,c=divmod(i,N); odd=c&1
    d=[[1,1],[1,0],[1,-1],[0,-1],[-1,0],[0,1]] if odd else [[0,1],[1,0],[0,-1],[-1,-1],[-1,0],[-1,1]]
    return [ (r+dr)*N+c+dc for dr,dc in d if 0<=r+dr<N and 0<=c+dc<N and (r+dr)*N+c+dc not in VOID]
def orbits(k,avoid,ok):
    out=[]
    for g in range(300):
        i=random.choice(cells); orb=[i,rot(i),rot(rot(i))]
        if len(set(orb))<3 or any(o in avoid or o in out for o in orb) or not all(ok(o,out) for o in orb): continue
        out+=orb
        if len(out)>=3*k: return out
    return None
fails={'castle':0,'mtn':0,'water':0,'conn':0,'coins':0}; ok=0; T=3000
for t in range(T):
    cs=orbits(2,set(HOMES)|{C},lambda o,out:min(man(o,h) for h in HOMES)>=3 and all(man(o,c)>=3 for c in out))
    if not cs or any(man(a,b)<3 for a in cs for b in cs if a!=b): fails['castle']+=1; continue
    taken=set(HOMES)|set(cs)
    mt=orbits(3,taken|{C},lambda o,out:min(man(o,h) for h in HOMES)>=2)
    if not mt: fails['mtn']+=1; continue
    mt=mt+[C]; taken|=set(mt)
    wa=orbits(1,taken,lambda o,out:min(man(o,h) for h in HOMES)>=2)
    if not wa: fails['water']+=1; continue
    # the 4th water: the free hex whose distances to the three homes are closest to equal (ties: random)
    cand=[i for i in cells if i not in taken and i not in wa and min(man(i,h) for h in HOMES)>=2]
    random.shuffle(cand); cand.sort(key=lambda i:max(man(i,h) for h in HOMES)-min(man(i,h) for h in HOMES))
    wa.append(cand[0]); blocked=set(mt)|set(wa)
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

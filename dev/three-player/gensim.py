import json,random
from board3 import man,N
b=json.load(open('board3.json')); VOID=set(b['void']); HOMES=[78,16,86]
cells=[i for i in range(N*N) if i not in VOID]
stats={'castles_fill':0,'sums':0,'near':0,'closest':0,'ok':0}
def castles_try():
    castles=[];g=0
    while len(castles)<6 and g<800:
        g+=1; i=random.choice(range(N*N))
        if i in VOID or i in HOMES or i in castles: continue
        ds=[man(i,h) for h in HOMES]
        if min(ds)<3 or max(ds)-min(ds)>3: continue
        if any(man(c,i)<3 for c in castles): continue
        castles.append(i)
    return castles
for t in range(20000):
    c=castles_try()
    if len(c)<6: stats['castles_fill']+=1; continue
    sums=[sum(man(x,h) for x in c) for h in HOMES]
    if max(sums)-min(sums)>2: stats['sums']+=1; continue
    near=[min(man(x,h) for x in c) for h in HOMES]
    if max(near)-min(near)>0: stats['near']+=1; continue
    cl=[0,0,0]
    for x in c:
        ds=[man(x,h) for h in HOMES]; m=min(ds)
        if ds.count(m)==1: cl[ds.index(m)]+=1
    if max(cl)-min(cl)>0: stats['closest']+=1; continue
    stats['ok']+=1
print(stats)

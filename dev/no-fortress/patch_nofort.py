"""Ethan, 2026-11-24: "can you get rid of the fortress map please?" ... "and the 'walls' map". The arena's map picker has no Fortress button, a
battle on a hex with a fort is fought on that hex's own ground (mountain, forest, ferns or open), and a battle that still
asks for the fortress (an old save, or an older copy of the game online) is fought in the open. The fortress code stays
in the arena but nothing reaches it. The same goes for the Walls map (only the map picker offered it). The board's fort keeps its +1 on the defenders' best die.
Usage: python3 patch_nofort.py index.html"""
import json, sys, os
p=sys.argv[1]; R=os.path.dirname(os.path.abspath(p))+'/'
ix=open(p,encoding='utf8').read()
k='window.ARENA_HTML="'; i=ix.find(k)+len(k); j=i
while True:
    j=ix.find('"',j); bs=0; q=j-1
    while ix[q]=='\\': bs+=1; q-=1
    if bs%2==0: break
    j+=1
ar=json.loads('"'+ix[i:j]+'"')
def rep(t,a,b,n=1):
    assert t.count(a)==n,(t.count(a),a[:90]); return t.replace(a,b)
ar=rep(ar,'<button type="button" data-map="fortress" aria-pressed="false">Fortress</button>','')
a=ar.find('On the <b>Fortress</b> map'); b=ar.find('On the <b>Castle</b> map',a); assert 0<a<b; ar=ar[:a]+ar[b:]
ar=rep(ar,'<button type="button" data-map="walls" aria-pressed="false">Walls</button>','')
ar=rep(ar,'aria-label="Which side holds the walls, fortress, mountain or forest"','aria-label="Which side holds the castle, mountain or forest"')
a=ar.find('Pick the <b>Open field</b> or the <b>Walls</b> map'); b=ar.find('On the <b>Castle</b> map',a); assert 0<a<b
ar=ar[:a]+"Pick the map by the speed buttons. Under the maps, <b>Held by</b> picks which side holds the castle, the mountainside or the forest: Blue (as described here) or Red, in which case it all stands on the right, and everything said here about Blue's side applies to Red's. "+ar[b:]
ar=rep(ar,"all with the same bonus as the walls;","all with the high-ground bonus (+50% range, +1 damage, 10% of hits on them miss);")
ar=rep(ar,"Blue holds a bone-and-tusk castle: two hexagonal archers' nests joined by a thick wall,","Blue holds a stone castle (the same for every faction): two round archers' nests joined by a long wall,")
ar=rep(ar,"MAP=m.map||'open';","MAP=(m.map&&m.map!=='fortress'&&m.map!=='walls')?m.map:'open';   // no Fortress or Walls map any more (Ethan, 2026-11-24)\n ")
ix=ix[:i]+json.dumps(ar,ensure_ascii=False)[1:-1].replace('</script','<\\/script')+ix[j:]
ix=rep(ix,"const arenaMap=(t,w)=>t.castle?'castle':t.fort?'fortress':t.terrain","const arenaMap=(t,w)=>t.castle?'castle':t.terrain")
ix=rep(ix,"The hex decides the field: castle, fortress (a hex with a fort),","The hex decides the field: castle,")
open(R+'arena.html','w',encoding='utf8').write(ar); open(p,'w',encoding='utf8').write(ix); print('no fortress ok')

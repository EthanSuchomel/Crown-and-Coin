"""Ethan, 2026-11-24: "remove the ballistas on the castles". The arena's Castle map has no ballistas on its archers'
nests any more (and its notes stop mentioning them). Takes the arena embedded in index.html, writes arena.html, and
re-embeds it.
Usage: python3 patch_arena.py index.html"""
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
def rep(a,b,n=1):
    global ar
    assert ar.count(a)==n,(ar.count(a),a[:90]); ar=ar.replace(a,b)
if "makeBallistas();\n  BW=D.levels" in ar: rep("  img('bwallart',A.up); img('bwallart',A.lo);\n  makeBallistas();", "  img('bwallart',A.up); img('bwallart',A.lo);\n  BAL=[];   // no ballistas on the castle (Ethan, 2026-11-24)")
rep(" A ballista stands on top of each nest (50 health, a shot every 3.5 seconds for 15 damage: bolts from the dinosaurs', lasers from the Robots'); it turns to aim at anything in front of the castle, ground or air, and only shooters and flyers can reach it.", "")
open(R+'arena.html','w',encoding='utf8').write(ar)
enc=lambda t: json.dumps(t,ensure_ascii=False)[1:-1].replace('</script','<\\/script')
ix=ix[:i]+enc(ar)+ix[j:]
open(p,'w',encoding='utf8').write(ix); print('arena ok')

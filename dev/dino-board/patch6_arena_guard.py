# Dinosaur board rework, step 6: the Alamosaurus guard in the arena (Ethan, 2026-11-09).
# It now comes only from the board, as a barracks guard that fights when its hex is attacked:
# 120 health, 15 damage every 2 seconds to up to 4 enemies; no riders, no saddle, no charge, no stomp.
# Its body picture is repainted without the tower, riders and saddle cloth (alamo_repaint.py), the same for both teams.
# It is hidden from the standalone arena's army controls. Re-embeds the arena in index.html.
import json, base64, sys
R='/home/claude/crown-and-coin/'
ar=open(R+'arena.html').read(); ix=open(R+'index.html').read()
k='window.ARENA_HTML="'; i=ix.find(k)+len(k); j=i
while True:
    j=ix.find('"',j); bs=0; q=j-1
    while ix[q]=='\\': bs+=1; q-=1
    if bs%2==0: break
    j+=1
assert json.loads('"'+ix[i:j]+'"')==ar, 'embedded arena differs from arena.html'
def rep(a,b,n=1):
    global ar
    assert ar.count(a)==n,(ar.count(a),a[:90]); ar=ar.replace(a,b)
uri='data:image/png;base64,'+base64.b64encode(open(R+'dev/dino-board/alamo_plain.png','rb').read()).decode()
s0=ar.index("  alamo:{blue:'data:image/png;base64,"); e0=ar.index("\n",s0)
assert "red:'data:image/png;base64," in ar[s0:e0]
ar=ar[:s0]+f"  alamo:{{blue:'{uri}',red:'{uri}'}},"+ar[e0:]
rep("""  alamo:{label:'Alamosaurus',heavy:true,stunImmune:true,cost:30,hp:108,dmg:15,rate:2.25,range:2.5,footX:8.8,footY:2.0,speed:3.861,w:21,ratio:0.7621,aimFrac:0.27,ranged:false,hitKey:'melee',armor:{},reduce:{archer:3,longbow:3,rider:3},
        flying:false,antiAir:false,rank:0,preferGround:true,riderType:'dilo',riders:[{fx:0.517,fy:0.335},{fx:0.74,fy:0.303}],
        lungeDur:.6,strikeAt:.3,bob:0.4,bobRate:0.5,legs:true,multi:5,superStomp:{stun:2},charge:{mult:1.5,dist:21,max:4}},""",
"""  alamo:{label:'Alamosaurus',heavy:true,cost:25,hp:120,dmg:15,rate:2.0,range:2.5,footX:8.8,footY:2.0,speed:3.861,w:21,ratio:0.7621,aimFrac:0.27,ranged:false,hitKey:'melee',armor:{},
        flying:false,antiAir:false,rank:0,preferGround:true,hidden:true,guard:true,   // a barracks guard from the board: only defends, never in the army controls
        lungeDur:.6,strikeAt:.3,bob:0.4,bobRate:0.5,legs:true,multi:4},   // each stomp hits up to 4 enemies""")
rep("const ORDER=['galli','dilo','ptero','mega','bow','quetz',","const ORDER=['galli','dilo','ptero','mega','bow','quetz','alamo',")
open(R+'arena.html','w').write(ar)
enc=lambda t: json.dumps(t,ensure_ascii=False)[1:-1].replace('</script','<\\/script')
ix=ix[:i]+enc(ar)+ix[j:]
open(R+'index.html','w').write(ix); print('patch6 ok')

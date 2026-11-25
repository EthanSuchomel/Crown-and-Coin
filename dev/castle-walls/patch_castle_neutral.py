"""Ethan, 2026-11-24: "update the castle map to not be based on the faction but just a simple neutral castle map" /
"just draw the entire wall in the castle arena instead of doing it in parts". The Castle map is now one neutral stone
picture (Ethan's OpenArt pick, its two angled walls lengthened to reach the field's edge) for every faction, with the
walkways, stairs, nests and blocking rebuilt for the new walls.
Usage: python3 patch_castle_neutral.py index.html"""
import json, sys, os, base64
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
src='data:image/webp;base64,'+base64.b64encode(open(os.path.dirname(os.path.abspath(__file__))+'/art/castle_neutral.webp','rb').read()).decode()
s=11.9/672   # arena units per pixel of the full-size picture (2296 px wide)
a=ar.find('const CASTLE_ART={'); b=ar.find("// the angled walls' footprints")
assert 0<a<b
ar=ar[:a]+("// One neutral stone castle for every faction (Ethan's OpenArt picture: two round archers' nests joined by a long centre\n"
 "// wall, the top wall with stairs on its inner face, the bottom wall plain; both angled walls lengthened to the field's edge)\n"
 "const CASTLE_ART_N={left:%.3f,top:%.3f,w:%.3f,src:'%s'};\n" % (9.6385-760*s, 1.2792-320*s, 2296*s, src))+ar[b:]
rep("two hexagonal archers' nests joined by a thick wall, with an angled wall running from each nest back to the\n// top and bottom edges. The pictures were made in OpenArt from his bone-and-tusk gatehouse. There is no gate",
    "two round archers' nests joined by a long wall, with an angled wall running from each nest back to the\n// top and bottom edges. One neutral stone picture for every faction. There is no gate")
old=ar[ar.find('const CASTLE_DEF='):ar.find('\n',ar.find('slots:[4,7.6,11.2,14.8,18.4,22]}]};'))]
new='''const CASTLE_DEF={inX:27.1,gateX:32.8,gy:30,half:2.6,hp:150,hpAt:{x:34.2,y:25},
  rects:[{x0:24.2,x1:35.6,y0:13.8,y1:21.6},{x0:27.1,x1:32.8,y0:21.6,y1:27.4},{x0:27.1,x1:32.8,y0:32.6,y1:41.3},{x0:24.2,x1:35.6,y0:41.3,y1:49.7}],   // upper nest, centre wall either side of the gate, lower nest
  // the shooters stand along the centre wall and the two angled walls' walkways (walk: where their feet go along the wall; xa..xb: the part of it on the field)
  levels:[{mid:true,xa:28.7,xb:31.3,ya:17.5,yb:39.5,foot:{x:25.5,y:30},top:{x:30,y:30},band:[],   // the centre wall's walkway and the nest tops, filled first; reached from inside the castle, behind the gate
           slots:[[30,18],[30,39],[30,21.5],[30,35.5],[30,25],[30,32.5],[30,28.8]]},
          {xa:12,xb:23.2,walk:x=>-0.85+0.465*x,foot:{x:22.6,y:19.2},top:{x:15.6,y:6.4},band:castleBand(x=>-3.4+0.468*x,x=>7.2+0.465*x,true),   // up the stairs on the top wall's inner face
           slots:[16.4,18.6,20.8,23]},
          {xa:2,xb:22.8,walk:x=>50.24-0.367*x,foot:{x:20.5,y:39.3},top:{x:19.5,y:43.1},band:castleBand(x=>47.4-0.367*x,x=>58.4-0.36*x,false),   // the bottom wall has no stairs: a ladder behind it
           slots:[4,7.6,11.2,14.8,18.4,22]}]};'''
rep(old,new)
rep("const A=ROBO()?CASTLE_ART_R:MAMMO()?CASTLE_ART_M[HOLD===1?'red':'blue']:redOf(CASTLE_ART,'castle'), D=CASTLE_DEF,", "const A=CASTLE_ART_N, D=CASTLE_DEF,")
rep("  img('bwallart',A.up); img('bwallart',A.lo);\n  BAL=[];", "  BAL=[];")
rep("  FORT.el=img('fort',A.mid);", "  FORT.el=img('fort',A);   // the whole castle is one picture")
rep(" makeRedArt('castle',CASTLE_ART);", "")
open(R+'arena.html','w',encoding='utf8').write(ar)
enc=lambda t: json.dumps(t,ensure_ascii=False)[1:-1].replace('</script','<\\/script')
ix=ix[:i]+enc(ar)+ix[j:]
open(p,'w',encoding='utf8').write(ix); print('castle neutral ok', len(ar))

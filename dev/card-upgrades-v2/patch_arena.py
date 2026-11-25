"""Volley (the new cards, card 3 Move level 3): in a battle sent from Crown & Coin, the attackers' shooters fire once,
at random enemies on the field, the moment the battle starts. Usage: python3 patch_arena.py index.html"""
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
    c=ar.count(a); assert c==n,(c,a[:100]); ar=ar.replace(a,b)
rep("let SNEAK=null, SNEAK_HIT=false, MOD_PLUS=[0,0], MOD_MULT=[1,1], MOD_HP=[1,1];",
    "let SNEAK=null, SNEAK_HIT=false, MOD_PLUS=[0,0], MOD_MULT=[1,1], MOD_HP=[1,1];\n// Volley (Crown & Coin's card upgrade): VOLLEY is the attacking team; its shooters fire once as the battle starts\nlet VOLLEY=null, VOLLEY_DONE=false;\nfunction doVolley(){ VOLLEY_DONE=true; let n=0;\n  for(const f of F.slice()){ if(f.team!==VOLLEY||f.dead||!(f.T.ranged||f.T.rocket)) continue;\n    const fs=F.filter(t=>t.team!==VOLLEY&&!t.dead&&(!t.T.flying||f.T.antiAir)); if(!fs.length) break;\n    const t=fs[Math.floor(R()*fs.length)]; hit(t,f,1,true); n++; }\n  return n; }")
rep("SNEAK=(md.sneak===0||md.sneak===1)?md.sneak:null; SNEAK_HIT=false;","SNEAK=(md.sneak===0||md.sneak===1)?md.sneak:null; SNEAK_HIT=false; VOLLEY=(md.volley===0||md.volley===1)?md.volley:null; VOLLEY_DONE=false;")
rep("function update(dt){\n  clock+=dt;\n","function update(dt){\n  clock+=dt;\n  if(VOLLEY!=null&&!VOLLEY_DONE) doVolley();   // Volley: the attackers' shooters fire once as it starts\n")
open(R+'arena.html','w',encoding='utf8').write(ar)
ix=ix[:i]+json.dumps(ar,ensure_ascii=False)[1:-1].replace('</script','<\\/script')+ix[j:]
open(p,'w',encoding='utf8').write(ix); print('arena ok')

# Dinosaur board rework, step 6b: the Alamosaurus legs without the saddle's armour (Ethan, 2026-11-09).
# The hip plate (ro) is now empty and the blue cloth and steel bits on the upper legs are repainted with skin
# (alamo_legs_clean.py). Re-embeds the arena in index.html.
import json, base64, re
R='/home/claude/crown-and-coin/'
ar=open(R+'arena.html').read(); ix=open(R+'index.html').read()
k='window.ARENA_HTML="'; i=ix.find(k)+len(k); j=i
while True:
    j=ix.find('"',j); bs=0; q=j-1
    while ix[q]=='\\': bs+=1; q-=1
    if bs%2==0: break
    j+=1
assert json.loads('"'+ix[i:j]+'"')==ar, 'embedded arena differs from arena.html'
s0=ar.index('  alamoLegs:{'); e0=ar.index('\n',s0); line=ar[s0:e0]
for key in ['nu','nl','fu','fl','rnu','rnl','rfu','rfl','ro']:
    uri='data:image/png;base64,'+base64.b64encode(open(R+f'dev/dino-board/alamo_legs/leg_{key}.png','rb').read()).decode()
    line,n=re.subn(rf"(?<=[{{,]){key}:'data:image/png;base64,[A-Za-z0-9+/=]+'",f"{key}:'{uri}'",line); assert n==1,key
ar=ar[:s0]+line+ar[e0:]
open(R+'arena.html','w').write(ar)
enc=lambda t: json.dumps(t,ensure_ascii=False)[1:-1].replace('</script','<\\/script')
open(R+'index.html','w').write(ix[:i]+enc(ar)+ix[j:]); print('patch6b ok')

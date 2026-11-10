# Three-player mode, step 5: the battle screen names each side by its real color (Ethan, 2026-11-10).
# The line under the battlefield always said "Blue ... · Red ...", even when the sides were, say, Blue and Green.
# It now uses the names the game hands the arena (NAMES, which stay Blue/Red in the standalone arena).
# Takes the arena embedded in index.html, fixes it, writes arena.html, and re-embeds it (safe to re-run from the original).
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
rep("""setAttribute('aria-label','Blue health '+Math.ceil(hp[0])+' of '+Math.ceil(HP0[0])+', Red health '+""",
    """setAttribute('aria-label',NAMES[0]+' health '+Math.ceil(hp[0])+' of '+Math.ceil(HP0[0])+', '+NAMES[1]+' health '+""")
rep("""statusEl.innerHTML='<span class="b">Blue '+tot[0]+""","""statusEl.innerHTML='<span class="b">'+NAMES[0]+' '+tot[0]+""")
rep("""&middot; <span class="r">Red '+tot[1]+""","""&middot; <span class="r">'+NAMES[1]+' '+tot[1]+""")
open(R+'arena.html','w',encoding='utf8').write(ar)
enc=lambda t: json.dumps(t,ensure_ascii=False)[1:-1].replace('</script','<\\/script')
ix=ix[:i]+enc(ar)+ix[j:]
open(p,'w',encoding='utf8').write(ix); print('patch5 ok')

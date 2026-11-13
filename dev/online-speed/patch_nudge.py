"""Online moves show up faster (Ethan, 2026-11-13: 'the online game is taking so long to show moves').
The board travels in the db document games/<code>; the other device hears it through onSnapshot, which falls back to
a refresh about every 30 s when the platform's live stream isn't available. Now, after a move is saved, the sender
also pings the game's room ('nudge', declared for Contributors), and the other device reads the document at once.
Backup: while it isn't your turn, the game reads the document every 6 s (and whenever the page comes back to the
front). Usage: python3 patch_nudge.py index.html"""
import sys
P = sys.argv[1]; s = open(P).read()
def rep(a, b):
    global s; assert s.count(a) == 1, a[:90]; s = s.replace(a, b)
rep("""    net.rev=body.rev; net.lastJson=js; net.lastCur=cur0; net.err='';""",
    """    net.rev=body.rev; net.lastJson=js; net.lastCur=cur0; net.err='';
    if(NF.room) NF.room.emit('nudge',{rev:body.rev}).catch(()=>{});   // tell the other device to read it now""")
rep("""    NF.unsubs.push(room.on('bend',m=>{""",
    """    NF.unsubs.push(room.on('nudge',m=>{ if(!m.sameTab&&m.data&&NET&&NET.code===code&&+m.data.rev>NET.rev) netFetch(); },()=>{}));
    NF.unsubs.push(room.on('bend',m=>{""")
rep("""function netClose(){""", """// read the game's document now (after a nudge, on a timer while waiting, or when the page comes back)
async function netFetch(){
  const net=NET; if(!net||net.fetching) return; net.fetching=true;
  try{ const snap=await net.ref.get(); if(NET===net&&snap&&snap.exists) netApply(snap.data()); }catch(e){}
  net.fetching=false;
}
setInterval(()=>{ if(NET&&NET.entered&&S&&!S.over&&S.current!==0&&!S.fight&&document.visibilityState==='visible') netFetch(); },6000);
document.addEventListener('visibilitychange',()=>{ if(document.visibilityState==='visible'&&NET&&NET.entered) netFetch(); });
function netClose(){""")
open(P, 'w').write(s); print('ok')

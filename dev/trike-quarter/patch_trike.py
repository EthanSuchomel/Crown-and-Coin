"""Ethan, 2026-11-24: "change the triceratops from taking 0 damage from projectiles to 1/4 damage from projectiles".
Shots and spells now do a quarter of their damage to a Triceratops (they did none). Shots from up on walls and towers
still do half, and the Laser Tank's beam still does full. With every hit doing damage, the Robot Longbow no longer
gives up on a Triceratops. The board's battle model and unit notes follow.
Usage: python3 patch_trike.py index.html"""
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
ar=rep(ar,"""  else if(t.T.noProj&&!(att.T&&att.T.beam)&&(proj||(att.T&&(att.T.ranged||att.T.rocket)))){ floatText(t,'Block','blk'); if(att.T&&att.T.retargetNoDmg){ att.noDmg=(att.noDmgT===t.id?att.noDmg:0)+1; att.noDmgT=t.id; if(att.noDmg>=2*((att.T.gun&&att.T.gun.muzzles.length)||1)){ att.ignoreT=t.id; att.target=null; att.noDmg=0; } } return; }   // Triceratops: shots and spells can't hurt it, except the Laser Tank's beam (a Robot Longbow gives up on it after 2 shots)""",
"""  else if(t.T.noProj&&!(att.T&&att.T.beam)&&(proj||(att.T&&(att.T.ranged||att.T.rocket)))) mult=(mult||1)*0.25;   // Triceratops: other shots and spells do a quarter (Ethan, 2026-11-24); the Laser Tank's beam does full""")
ar=rep(ar,"45 (shots and spells hit it but do no damage, except shots from walls and towers, which do half, and the Laser Tank's beam)",
          "45 (shots and spells do a quarter of their damage, shots from walls and towers half, and the Laser Tank's beam full)")
ar=rep(ar,"Nothing that's shot or cast can hurt it (Dilophosaurus spit, quills, arrows, lasers, rockets and the Mage's lightning), except shots from up on walls and towers, ballista bolts included, which do half damage, and the Laser Tank's beam: shooters still aim at it and keep shooting it, but their hits do no damage.",
          "Anything shot or cast at it (Dilophosaurus spit, quills, arrows, lasers, rockets and the Mage's lightning) does only a quarter of its damage, except shots from up on walls and towers, which do half, and the Laser Tank's beam, which does full damage.")
ar=rep(ar,"even if blocked; after 2 shots at a target they don't hurt (a Triceratops), it switches to another target","even if blocked")
ar=rep(ar,"  let dmg=Math.round((att.T.dmg+","  let dmg=(t.T.noProj?(v=>Math.round(v*4)/4):Math.round)((att.T.dmg+")   # a Triceratops can take a quarter of a point (half a point from an Archer's laser)
ix=ix[:i]+json.dumps(ar,ensure_ascii=False)[1:-1].replace('</script','<\\/script')+ix[j:]
ix=rep(ix,"""    if(T.noProj&&(w.rng||w.hk==='gunship'||w.hk==='magic')&&w.hk!=='beam') return 0;   // Triceratops""",
          """    if(T.noProj&&(w.rng||w.hk==='gunship'||w.hk==='magic')&&w.hk!=='beam') d*=0.25;   // Triceratops: shots and spells do a quarter""")
ix=rep(ix,"noProj:true},   // shots and spells do nothing to it (the Laser Tank's beam does)","noProj:true},   // shots and spells do a quarter of their damage (the Laser Tank's beam does full)")
ix=rep(ix,"""bow:"Shots and spells do nothing to it (except the Laser Tank's beam).""","""bow:"Shots and spells do only a quarter of their damage to it (the Laser Tank's beam does full).""")
open(R+'arena.html','w',encoding='utf8').write(ar); open(p,'w',encoding='utf8').write(ix); print('trike ok')

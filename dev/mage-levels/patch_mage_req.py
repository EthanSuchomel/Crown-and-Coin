# Ethan, 2026-11-11: raising the Mages also needs Life Trees and captured castles (held when you upgrade; losing a castle later
# doesn't take the level away). Level 1: 1 tree. Level 2: 3 trees and 1 captured castle. Level 3: 5 trees and 2 captured castles.
import sys
for fn in sys.argv[1:]:
    s = open(fn, encoding='utf-8').read()
    def rep(a, b, need=1):
        global s
        c = s.count(a)
        if c != need: print(fn, 'COUNT', c, a[:100]); sys.exit(1)
        s = s.replace(a, b)
    rep("const magePrice=pid=>", """// Ethan, 2026-11-11: each Mage level also needs Life Trees and captured castles when you raise it (a castle lost later doesn't take the level away)
const MAGE_REQ=[{trees:1,castles:0},{trees:3,castles:1},{trees:5,castles:2}];
const treesOf=pid=>S.tiles.filter(t=>t.owner===pid&&t.tree>0).length;
const capCastlesOf=pid=>S.tiles.filter(t=>t.castle&&t.owner===pid&&t.id!==S.homes[pid]).length;
const mageReqOk=(pid,l)=>l<3&&treesOf(pid)>=MAGE_REQ[l].trees&&capCastlesOf(pid)>=MAGE_REQ[l].castles;
const mageReqTxt=l=>{ const r=MAGE_REQ[l]; return `${r.trees} Life Tree${r.trees>1?'s':''}`+(r.castles?` and ${r.castles} captured castle${r.castles>1?'s':''}`:''); };
const mageReqAll=()=>MAGE_REQ.map((r,l)=>`level ${l+1}: ${mageReqTxt(l)}`).join('; ');
const magePrice=pid=>""")
    rep("""  if(l>=3||!mythHome(pid)||p.gold<MYTH.mageUp[l]) return false;
  p.gold-=MYTH.mageUp[l]; p.mlv=l+1;""", """  if(l>=3||!mythHome(pid)||p.gold<MYTH.mageUp[l]||!mageReqOk(pid,l)) return false;
  p.gold-=MYTH.mageUp[l]; p.mlv=l+1;""")
    rep("""    it('upm',0,UNIT_ART.mage0,ml>=3?'Mages 3':`Mages ${ml+1}`,ml>=3?'Max level':!home?'No castle':`${MYTH.mageUp[ml]} magic`,ml<3&&home&&me.gold>=MYTH.mageUp[ml],
      {label:ml>=3?'Mages are at the top level':`Raise new Mages to level ${ml+1} for ${MYTH.mageUp[ml]} magic: ${MAGE_LV_NOTE[ml]}`});""",
        """    const rq=ml<3&&mageReqOk(0,ml), rqn=ml<3?MAGE_REQ[ml]:null;
    const rqShort=rqn?(treesOf(0)<rqn.trees?`${treesOf(0)}/${rqn.trees} trees`:`${capCastlesOf(0)}/${rqn.castles} castles`):'';
    it('upm',0,UNIT_ART.mage0,ml>=3?'Mages 3':`Mages ${ml+1}`,ml>=3?'Max level':!home?'No castle':!rq?rqShort:`${MYTH.mageUp[ml]} magic`,ml<3&&home&&rq&&me.gold>=MYTH.mageUp[ml],
      {label:ml>=3?'Mages are at the top level':!rq?`Mages level ${ml+1} needs ${mageReqTxt(ml)} (you have ${treesOf(0)} tree${treesOf(0)===1?'':'s'} and ${capCastlesOf(0)} captured castle${capCastlesOf(0)===1?'':'s'})`:`Raise new Mages to level ${ml+1} for ${MYTH.mageUp[ml]} magic: ${MAGE_LV_NOTE[ml]}`});""")
    rep("""Upgrade your Mages (${MYTH.mageUp.join(', ')} magic for levels 1 to 3) or the Floating Castle""",
        """Upgrade your Mages (${MYTH.mageUp.join(', ')} magic for levels 1 to 3; ${mageReqAll()}) or the Floating Castle""")
    rep("""Tap any of your hexes to upgrade your Mages (${MYTH.mageUp.join(', ')} magic) or the Floating Castle""",
        """Tap any of your hexes to upgrade your Mages (${MYTH.mageUp.join(', ')} magic; ${mageReqAll()}) or the Floating Castle""")
    rep("""<li>Levels (${MYTH.mageUp.join(', ')} magic, at the castle): 1 Griffins, 2 Dragons, 3 every unit 1 magic cheaper and 3 Mages a hex. Each level also lengthens the Mage's lightning; a Mage keeps the level it was made at.</li>""",
        """<li>Levels (${MYTH.mageUp.join(', ')} magic, at the castle): 1 Griffins, 2 Dragons, 3 every unit 1 magic cheaper and 3 Mages a hex. Each level also lengthens the Mage's lightning; a Mage keeps the level it was made at.</li>
      <li>Each level also needs Life Trees and captured castles when you raise it (${mageReqAll()}). Losing a castle later doesn't take the level away.</li>""")
    # the computer keeps magic back for a Mage level only when it qualifies
    rep("""clvOf(pid)<3?MYTH.castleUp[clvOf(pid)]:MYTH.mageUp[Math.min(2,mlvOf(pid))]):0;""",
        """clvOf(pid)<3?MYTH.castleUp[clvOf(pid)]:(mageReqOk(pid,mlvOf(pid))?MYTH.mageUp[Math.min(2,mlvOf(pid))]:0)):0;""")
    open(fn, 'w', encoding='utf-8').write(s)
    print(fn, 'ok')

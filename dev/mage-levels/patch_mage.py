# Ethan, 2026-11-11: Mage lightning reach 30 / 45 / 60 / 90 and damage 2 / 3 / 4 / 5 for levels 0-3 (were 30/60/90/120 and 5/6/7/7).
import sys
for fn in sys.argv[1:]:
    s = open(fn, encoding='utf-8').read()
    n0 = len(s)
    def rep(a, b, need):
        global s
        c = s.count(a)
        if c != need: print(fn, 'COUNT', c, a[:90]); sys.exit(1)
        s = s.replace(a, b)
    rep("[['mage0',30,5,.2],['mage1',60,6,.3],['mage2',90,7,.4],['mage3',120,7,.5]]",
        "[['mage0',30,2,.2],['mage1',45,3,.3],['mage2',60,4,.4],['mage3',90,5,.5]]", 1)
    if 'mage0:   {name' in s:   # the board (index.html / the claude.ai page): its battle maths use the same damage
        rep("mage0:   {name:'Mage',hp:15,dmg:5,", "mage0:   {name:'Mage',hp:15,dmg:2,", 1)
        rep("mage1:   {name:'Mage (level 1)',hp:15,dmg:6,", "mage1:   {name:'Mage (level 1)',hp:15,dmg:3,", 1)
        rep("mage2:   {name:'Mage (level 2)',hp:15,dmg:7,", "mage2:   {name:'Mage (level 2)',hp:15,dmg:4,", 1)
        rep("mage3:   {name:'Mage (level 3)',hp:15,dmg:7,", "mage3:   {name:'Mage (level 3)',hp:15,dmg:5,", 1)
        rep("'units 1 magic cheaper, longer lightning, 3 Mages a hex'", "'units 1 magic cheaper, longer lightning, +1 damage, 3 Mages a hex'", 1)
    open(fn, 'w', encoding='utf-8').write(s)
    print(fn, 'ok', n0, len(s))

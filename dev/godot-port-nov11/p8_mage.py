# Ethan, 2026-11-11: Mage reach 30 / 45 / 60 / 90 and damage 2 / 3 / 4 / 5 for levels 0-3 (Arena and board numbers).
import sys, re
W = sys.argv[1]
def patch(f, pairs):
    s = open(W + f, encoding='utf-8').read()
    for old, new in pairs:
        if s.count(old) != 1: print('COUNT', s.count(old), f, old[:100]); sys.exit(1)
        s = s.replace(old, new)
    open(W + f, 'w', encoding='utf-8').write(s)
A = []
for k, (r0, d0), (r1, d1) in [('mage0', ('30.0', 5), ('30.0', 2)), ('mage1', ('60.0', 6), ('45.0', 3)), ('mage2', ('90.0', 7), ('60.0', 4)), ('mage3', ('120.0', 7), ('90.0', 5))]:
    A.append(('"%s": {"label": "Mage", "faction": "Mythical", "cost": 15, "maxN": 3, "hidden": true, "hp": 15, "dmg": %d, "rate": 3, "range": %s,' % (k, d0, r0),
              '"%s": {"label": "Mage", "faction": "Mythical", "cost": 15, "maxN": 3, "hidden": true, "hp": 15, "dmg": %d, "rate": 3, "range": %s,' % (k, d1, r1)))
patch('/scripts/arena/arena_battle.gd', A)
s = open(W + '/data/units.json', encoding='utf-8').read()
for k, d0, d1 in [('mage0', 5, 2), ('mage1', 6, 3), ('mage2', 7, 4), ('mage3', 7, 5)]:
    pat = re.compile(r'("%s": \{\n\t\t"[^\n]*\n\t\t"[^\n]*\n\t\t"dmg": )%d,' % (k, d0))
    s, n = pat.subn(lambda m: m.group(1) + '%d,' % d1, s)
    if n != 1: print('units.json', k, n); sys.exit(1)
open(W + '/data/units.json', 'w', encoding='utf-8').write(s)
patch('/data/rules.json', [('"units 1 magic cheaper, longer lightning, 3 Mages a hex"', '"units 1 magic cheaper, longer lightning, +1 damage, 3 Mages a hex"')])
patch('/scripts/ui/main.gd', [("Each level also lengthens the Mage's lightning;", "Each level also lengthens the Mage's lightning and adds 1 damage;")])
patch('/scripts/rules/test_rules.gd', [('	check("arena: Rhino damage 12", int(ArenaBattle.TYPES.rhino.dmg) == 12)',
 '''	check("arena: Rhino damage 12", int(ArenaBattle.TYPES.rhino.dmg) == 12)
	check("arena: Mage levels reach 30/45/60/90, damage 2/3/4/5", ["mage0", "mage1", "mage2", "mage3"].map(func(k): return "%d/%d" % [int(ArenaBattle.TYPES[k].range), int(ArenaBattle.TYPES[k].dmg)]) == ["30/2", "45/3", "60/4", "90/5"])''')])
print('mage ok')

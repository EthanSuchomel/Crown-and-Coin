import re
U='/mnt/user-data/uploads/CrownAndCoin-Godot/'; O='/mnt/user-data/outputs/godot/minion/'
def ed(src, pairs, out):
    s=open(src).read()
    for a,b,n in pairs:
        assert s.count(a)==n,(src,s.count(a),a[:80]); s=s.replace(a,b)
    open(O+out,'w').write(s); return s
ed(U+'data/units.json',[('''		"name": "Minion",
		"hp": 5,
		"dmg": 2,''','''		"name": "Minion",
		"hp": 5,
		"dmg": 0.5,''',1)],'units.json')
ed(U+'data/rules.json',[('''		"minions": [
			5,
			7,
			9,
			11
		],''','''		"minions": [
			1,
			3,
			5,
			8
		],''',1)],'rules.json')
ed(U+'scripts/arena/arena_battle.gd',[('"minion": {"label": "Minion", "faction": "Mythical", "cost": 1, "hp": 5, "dmg": 2, "rate": 2.0, "range": 3.5, "speed": 3.78,','"minion": {"label": "Minion", "faction": "Mythical", "cost": 1, "hp": 5, "dmg": 0.5, "rate": 2.0, "range": 3.5, "speed": 3.24,',1)],'arena_battle.gd')
s=open(U+'scripts/ui/main.gd').read()
pairs=[
 ('grid.add_child(_label(str(int(U.dmg)) if not U.has("beam") else "beam %d" % int(U.dmg), 14, LICHEN))','grid.add_child(_label(_num(U.dmg) if not U.has("beam") else "beam %s" % _num(U.dmg), 14, LICHEN))',1),
 ('("%d damage" % int(U.dmg)) if not U.has("beam")','("%s damage" % _num(U.dmg)) if not U.has("beam")',2),
 ('	var atk: String = str(int(U.dmg))','	var atk: String = _num(U.dmg)',1),
 ('atk = "%d ×%d" % [int(U.dmg), int(U.beam.n)]','atk = "%s ×%d" % [_num(U.dmg), int(U.beam.n)]',1),
 ('atk = "%d ×%d" % [int(U.dmg), int(U.shots)]','atk = "%s ×%d" % [_num(U.dmg), int(U.shots)]',1),
 ('atk = "%d / %d air" % [int(U.dmg), int(U.airDmg)]','atk = "%s / %d air" % [_num(U.dmg), int(U.airDmg)]',1),
 ('raise that to %s magic and +2 Minions each. Only flyers can attack it.','raise that to %s magic and %s Minions. Only flyers can attack it.',1),
]
for a,b,n in pairs:
    assert s.count(a)==n,(s.count(a),a[:80]); s=s.replace(a,b)
open(O+'main.gd','w').write(s)
print('ok')

"""Godot, Ethan 2026-11-24: no Fortress map (a hex with a fort is fought on its own ground; Godot never had the Walls map),
and the Triceratops takes a quarter of the damage from shots and spells (was none; shots from walls still half, the Laser
Tank's beam full). Usage: python3 p21_nofort_trike.py GODOT_FOLDER"""
import sys
R=sys.argv[1].rstrip('/')+'/'
def edit(f, pairs):
    t=open(R+f,encoding='utf8').read()
    for a,b in pairs:
        assert t.count(a)==1,(f,t.count(a),a[:80]); t=t.replace(a,b)
    open(R+f,'w',encoding='utf8').write(t)
edit('scripts/rules/game_state.gd',[('''	if int(t.fort) > 0:
		return "fortress"
	if t.terrain == "mountain":''','''	if t.terrain == "mountain":   # no Fortress map (Ethan, 2026-11-24): a hex with a fort is fought on its own ground''')])
edit('scripts/ui/main.gd',[('var built: Array = ["open", "ferns", "trees", "mountain", "castle", "fortress"]','var built: Array = ["open", "ferns", "trees", "mountain", "castle"]')])
edit('scripts/arena/arena_preview.gd',[('@export_enum("open", "ferns", "trees", "mountain", "castle", "fortress") var map: String = "fortress"','@export_enum("open", "ferns", "trees", "mountain", "castle") var map: String = "castle"')])
edit('scripts/arena/arena_battle.gd',[
('''		# Triceratops: shots and spells can't hurt it, except the Laser Tank's beam (a Robot Longbow gives up on it after 2 shots)
		if att.T.get("retargetNoDmg", false):
			att.no_dmg = (att.no_dmg if att.no_dmg_t == t.id else 0) + 1
			att.no_dmg_t = t.id
			var per: int = (att.T.gun as Array).size() if att.T.has("gun") else 1
			if att.no_dmg >= 2 * per:
				att.ignore_t = t.id
				att.target = null
				att.no_dmg = 0
		return false''','''		mult *= 0.25   # Triceratops: other shots and spells do a quarter (Ethan, 2026-11-24); the Laser Tank's beam does full'''),
('''	var dmg: int = roundi(dmg_f * mult * float(mod_mult[att.team]))
	var reduce: Dictionary = t.T.get("reduce", {})
	if reduce.has(k):
		dmg = maxi(1, dmg - int(reduce[k]))''','''	var raw: float = dmg_f * mult * float(mod_mult[att.team])
	var dmg: float = (roundf(raw * 4.0) / 4.0) if t.T.get("noProj", false) else float(roundi(raw))   # a Triceratops can take a quarter of a point
	var reduce: Dictionary = t.T.get("reduce", {})
	if reduce.has(k):
		dmg = maxf(1.0, dmg - float(reduce[k]))'''),
])
edit('scripts/rules/combat.gd',[('''		return 0.0   # Triceratops: shots and spells do nothing to it (the Laser Tank's beam does)''','''		d *= 0.25   # Triceratops: shots and spells do a quarter (the Laser Tank's beam does full)''')])
edit('scripts/rules/test_rules.gd',[('''	# the Triceratops: shots do nothing to it
	var arrows: Dictionary = CombatRules.fight({"rarch": 10}, {"bow": 1}, {"avg": true})
	check("Robot Archers can't hurt a Triceratops", CombatRules.count(arrows.def_lost) == 0)''','''	# the Triceratops: shots do only a quarter of their damage to it
	var arrows: Dictionary = CombatRules.fight({"rarch": 10}, {"bow": 1}, {"avg": true})
	check("Robot Archers only chip at a Triceratops", CombatRules.count(arrows.def_lost) <= 1)''')])
edit('data/units.json',[('''"note": "Shots and spells do nothing to it (except the Laser Tank's beam).''','''"note": "Shots and spells do only a quarter of their damage to it (the Laser Tank's beam does full).''')])
print('ok')

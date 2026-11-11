# Godot port, step 3: Armor in board and Arena battles; Fortify no longer adds defense.
import sys
W = sys.argv[1] + '/scripts/'
def patch(f, pairs):
    s = open(W + f, encoding='utf-8').read()
    for old, new in pairs:
        n = s.count(old)
        if n != 1: print('COUNT', n, f, old[:120]); sys.exit(1)
        s = s.replace(old, new)
    open(W + f, 'w', encoding='utf-8').write(s)
patch('rules/game_state.gd', [
 ('''func braced(t: Dictionary) -> bool:
	return int(t.owner) >= 0 and int(t.braced) == int(t.owner)''',
  '''## Fortify gave +1 defense until 2026-11-10; it's a wild card now, so nothing is braced any more.
func braced(t: Dictionary) -> bool:
	return false'''),
])
patch('rules/combat.gd', [
 ('''				"wall": 0.0, "arm": arm[0], "plus": 0.0, "shield_foe": shield[0],''',
  '''				"wall": 0.0, "arm": arm[0], "plus": float(o.get("d_plus", 0)), "shield_foe": shield[0],'''),
 ('''		# Offline: the defenders hold fire until the attackers' first hit lands.''',
  '''		# Armor (the Dinosaurs' The Hunt): 10% more health, as less damage taken
		var arm_hp: float = float(o.get("arm_hp", 1.1))
		if bool(o.get("d_arm", false)):
			for k in hits_on_d.dmg:
				hits_on_d.dmg[k] = float(hits_on_d.dmg[k]) / arm_hp
		if bool(o.get("a_arm", false)):
			for k in hits_on_a.dmg:
				hits_on_a.dmg[k] = float(hits_on_a.dmg[k]) / arm_hp
		# Offline: the defenders hold fire until the attackers' first hit lands.'''),
])
patch('arena/arena_battle.gd', [
 ('''var mod_mult: Array = [1.0, 1.0]
var _sneak_t''', '''var mod_mult: Array = [1.0, 1.0]
var mod_hp: Array = [1.0, 1.0]   # Armor (the Dinosaurs' The Hunt): +10% health for that team
var _sneak_t'''),
 ('''	mod_plus = [0, 0]; mod_mult = [1.0, 1.0]
	for t in 2:
		mod_plus[t] = int(mods.get("plus", [0, 0])[t])
		mod_mult[t] = float(mods.get("mult", [1.0, 1.0])[t])''', '''	mod_plus = [0, 0]; mod_mult = [1.0, 1.0]; mod_hp = [1.0, 1.0]
	for t in 2:
		mod_plus[t] = int(mods.get("plus", [0, 0])[t])
		mod_mult[t] = float(mods.get("mult", [1.0, 1.0])[t])
		mod_hp[t] = float(mods.get("hp", [1.0, 1.0])[t])'''),
 ('''	return snappedf(float(TYPES[key].hp) * (FORT_HP if fort_buff(team) else 1.0), 0.01)''',
  '''	return snappedf(float(TYPES[key].hp) * (FORT_HP if fort_buff(team) else 1.0) * float(mod_hp[team]), 0.01)'''),
])
print('battle ok')

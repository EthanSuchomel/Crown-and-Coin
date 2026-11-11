extends Node
## Not shipped: the Mythical's default army with its 2 Mages at level 0, 1, 2 or 3 (and level 3 with a third Mage),
## against each faction's default army on all 6 maps. Both sides are the computer (Medium).
const AB = preload("res://scripts/arena/arena_battle.gd")
const MAPS := ["open", "ferns", "trees", "mountain", "castle", "fortress"]
func _alive(b, t: int) -> bool:
	for f in b.F:
		if f.team == t and not f.dead:
			return true
	return not b.RES[t].is_empty()
func _ready() -> void:
	var seeds: int = int(OS.get_environment("SEEDS")) if OS.get_environment("SEEDS") != "" else 4
	var variants: Array = [["level 0", {"mage0": 2}], ["level 1", {"mage1": 2}], ["level 2", {"mage2": 2}], ["level 3", {"mage3": 2}], ["level 3, 3 Mages", {"mage3": 3}]]
	var only: String = OS.get_environment("ONLY")
	var t0 := Time.get_ticks_msec()
	for v in variants:
		if only != "" and not String(v[0]) == only:
			continue
		var myth: Dictionary = {"minion": 25, "minotaur": 3, "griffin": 1, "dragon": 1}
		for k in v[1]:
			myth[k] = v[1][k]
		var tot := [0, 0, 0]
		var per := {}
		var bymap := {}
		for opp in ["Dinosaurs", "Robots", "Mammals"]:
			per[opp] = [0, 0, 0]
			for m in MAPS:
				if not bymap.has(m):
					bymap[m] = [0, 0, 0]
				for side in 2:   # which team the Mythical are (on a held map: 0 = they hold it, 1 = the other side holds it)
					for s in seeds:
						var b = AB.new()
						var counts: Array = [{}, {}]
						var mt: int = side
						counts[mt] = myth.duplicate()
						counts[1 - mt] = AB.DEFAULT_ARMY[opp].duplicate()
						var hold: int = mt if side == 0 else 1 - mt
						b.setup(counts, 1000 + s * 7 + side * 131 + MAPS.find(m) * 17, [0, 1], m, hold)
						var steps := 0
						while not b.over and steps < 30 * 300:
							b.update(AB.STEP)
							steps += 1
						var r: int = 2
						if not b.stalemate:
							var ma: bool = _alive(b, mt) and b.retreat != mt
							var oa: bool = _alive(b, 1 - mt) and b.retreat != 1 - mt
							r = 0 if (ma and not oa) else (1 if (oa and not ma) else 2)
						tot[r] += 1
						per[opp][r] += 1
						bymap[m][r] += 1
						b.free() if b is Object and not b is RefCounted else null
		var n: int = tot[0] + tot[1] + tot[2]
		var pct := func(a): return "%d%%" % roundi(100.0 * a[0] / maxf(1.0, a[0] + a[1] + a[2]))
		print("RESULT %s: Mythical win %s of %d (wins %d, losses %d, stalemates %d) | vs Dinosaurs %s, Robots %s, Mammals %s | maps %s  [%d s]" % [v[0], pct.call(tot), n, tot[0], tot[1], tot[2], pct.call(per.Dinosaurs), pct.call(per.Robots), pct.call(per.Mammals), ", ".join(PackedStringArray(MAPS.map(func(m): return "%s %s" % [m, pct.call(bymap[m])]))), (Time.get_ticks_msec() - t0) / 1000])
	get_tree().quit()

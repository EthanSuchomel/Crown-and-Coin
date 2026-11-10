extends Node
const ArenaBattle = preload("res://scripts/arena/arena_battle.gd")
## Not shipped: Rhinos and a Palaeoloxodon walk; their walk frames step with the ground covered.
func _ready() -> void:
	var b = ArenaBattle.new()
	b.setup([{"rhino": 3, "eleph": 1}, {"robot": 2, "rarch": 6}], 4242, [0, 1])
	var v = load("res://scripts/arena/arena_view.gd").new()
	v.battle = b
	var seen := {"rhino": {}, "eleph": {}}
	for s in 240:
		b.update(ArenaBattle.STEP)
		for f in b.F:
			if seen.has(f.key) and f.walking and not f.dead:
				seen[f.key][v._frame(f)] = true
	for k in seen:
		var odo: float = 0.0
		for f in b.F:
			if f.key == k:
				odo = maxf(odo, f.odo)
		print(k, " walk frames used: ", seen[k].keys(), "  ground covered ", snappedf(odo, 0.1))
	v.free()
	get_tree().quit()

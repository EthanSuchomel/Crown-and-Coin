extends Node
## Not shipped: 3-player computer games (Medium), each faction trio, to 80 rounds.
const AIPlayer = preload("res://scripts/rules/ai_player.gd")
func _ready() -> void:
	var facs := ["dinos", "robots", "mammals", "mythical"]
	var t0 := Time.get_ticks_msec()
	var wins := {}
	for f in facs:
		wins[f] = 0
	var lens: Array = []
	var unfinished: int = 0
	var knock := 0
	for rep in 2:
		for skip in facs:
			var trio: Array = facs.filter(func(f): return f != skip)
			if rep == 1:
				trio.reverse()
			var g := GameState.new()
			g.new_game(trio[0], [], "", 3, [trio[1], trio[2]])
			g.players[0].ai = true
			g.begin_turn()
			for i in 240:
				if g.over >= 0:
					break
				AIPlayer.take_turn(g)
			var outs: Array = []
			for q in g.players:
				if g.is_out(int(q.id)):
					outs.append("%s r%d %s" % [q.faction, int(q.out_round), String(q.out_why)])
			knock += outs.size()
			if g.over >= 0:
				wins[g.players[g.over].faction] += 1
				lens.append(g.turn)
			else:
				unfinished += 1
			print("game %s: rounds %d, winner %s, out: %s" % [str(trio), g.turn, (g.players[g.over].faction if g.over >= 0 else "none"), str(outs)])
	print("wins ", wins, " finished in ", lens, " unfinished ", unfinished, " knock-outs ", knock, "  [", (Time.get_ticks_msec() - t0) / 1000, " s]")
	get_tree().quit()

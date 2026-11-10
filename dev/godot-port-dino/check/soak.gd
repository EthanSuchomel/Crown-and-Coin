extends Node
## Not shipped: two computer players, Dinosaurs vs each opponent, many games; reports volcano and guard use.
const AIPlayer = preload("res://scripts/rules/ai_player.gd")
func _ready() -> void:
	for opp in ["robots", "mammals", "mythical"]:
		var volc_lv := 0
		var guards := 0
		var erupt := 0
		var forts := 0
		var trebs := 0
		var wins := [0, 0, 0]
		for game_n in 6:
			var g := GameState.new()
			g.new_game("dinos", [], opp)
			g.players[0].ai = true
			g.begin_turn()
			for i in 60:
				if g.over >= 0:
					break
				AIPlayer.take_turn(g)
			for t in g.tiles:
				if int(t.owner) == 0:
					guards += g.guards_at(t)
					forts += int(t.fort)
					trebs += int(t.treb) + int(t.treb2)
			volc_lv += g.volc_lv(0)
			for l in g.log_lines:
				if "volcano erupts" in l:
					erupt += 1
			wins[g.over + 1 if g.over >= 0 else 0] += 1
		print("vs %s: volcano levels %d, guards standing %d, eruptions in the last 80 log lines %d, Dinosaur forts %d, trebuchets %d, results [none, dinos, %s] %s" % [opp, volc_lv, guards, erupt, forts, trebs, opp, str(wins)])
	get_tree().quit()

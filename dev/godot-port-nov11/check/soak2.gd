extends Node
## Not shipped: computer vs computer, every pairing; win rates, materials bought, buildings, Fortify picks, Armor.
const AIPlayer = preload("res://scripts/rules/ai_player.gd")
func _ready() -> void:
	var facs := ["dinos", "robots", "mammals", "mythical"]
	var wins := {}
	var games := {}
	for f in facs:
		wins[f] = 0
		games[f] = 0
	var stats := {"bought": 0, "bk": 0, "forts": 0, "walls": 0, "fx": 0, "armor": 0, "trees": 0, "turns": 0, "neg": 0}
	var t0 := Time.get_ticks_msec()
	for a in facs:
		for b in facs:
			if a == b:
				continue
			for n in 3:
				var g := GameState.new()
				g.new_game(a, [], b)
				g.players[0].ai = true
				g.begin_turn()
				for i in 60:
					if g.over >= 0:
						break
					AIPlayer.take_turn(g)
					for p in g.players:
						if int(p.gold) < 0 or int(p.get("mat", 0)) < 0:
							stats.neg += 1
				stats.turns += g.turn
				for l in g.log_lines:
					if "at the market for" in l:
						stats.bought += 1
					if "fortify: a regroup" in l:
						stats.fx += 1
				for t in g.tiles:
					if int(t.owner) >= 0:
						stats.bk += int(t.barracks)
						stats.forts += int(t.fort)
						stats.trees += int(t.tree)
						for w in t.walls:
							stats.walls += 1 if int(w) > 0 else 0
				for p in g.players:
					if bool(p.get("armor", false)):
						stats.armor += 1
				games[a] += 1
				games[b] += 1
				if g.over >= 0:
					wins[g.players[g.over].faction] += 1
	for f in facs:
		print("%s: won %d of %d" % [f, wins[f], games[f]])
	print("stats (last 80 log lines per game for bought/fx): ", stats, " in ", (Time.get_ticks_msec() - t0) / 1000, " s")
	get_tree().quit()

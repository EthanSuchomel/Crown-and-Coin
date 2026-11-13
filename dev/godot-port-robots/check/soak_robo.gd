extends Node
## Not shipped: computer vs computer, the Robots against each faction from both seats (Medium); win rates, and what the
## Robot computer built and used: factories, resource hexes, Overclock, laser strikes, Sorties. Also checks the Robots
## never break the one-building-per-hex rule and nobody's gold or materials go negative.
const AIPlayer = preload("res://scripts/rules/ai_player.gd")
func _ready() -> void:
	var per: int = int(OS.get_environment("GAMES")) if OS.get_environment("GAMES") != "" else 3
	var wins := {"robots": 0, "other": 0, "none": 0}
	var st := {"factories": 0, "fortresses": 0, "resource": 0, "hubs": 0, "overclock": 0, "laser": 0, "sortie": 0, "bad": 0, "neg": 0, "turns": 0, "games": 0}
	var t0 := Time.get_ticks_msec()
	for o in ["dinos", "mammals", "mythical"]:
		for seat in 2:
			for k in per:
				var g := GameState.new()
				if seat == 0:
					g.new_game("robots", [], o)
				else:
					g.new_game(o, [], "robots")
				g.players[0].ai = true
				g.begin_turn()
				var rb: int = 0 if seat == 0 else 1
				for i in 80:
					if g.over >= 0:
						break
					var before: int = g.log_n
					AIPlayer.take_turn(g)
					for q in mini(g.log_n - before, g.log_lines.size()):
						var l: String = g.log_lines[q]
						if "laser strike" in l:
							st.laser += 1
					for p in g.players:
						if int(p.gold) < 0 or int(p.get("mat", 0)) < 0:
							st.neg += 1
					for t in g.tiles:
						if int(t.owner) == rb and not t.castle and (int(t.barracks) > 1 or int(t.fort) > 1 or (int(t.barracks) > 0 and int(t.market) > 1) or (int(t.fort) > 0 and int(t.barracks) == 0) or int(t.market) > 4):
							st.bad += 1
				st.turns += g.turn
				st.games += 1
				for t in g.tiles:
					if int(t.owner) == rb and not t.castle:
						st.factories += 1 if int(t.barracks) > 0 else 0
						st.fortresses += 1 if int(t.fort) > 0 else 0
						st.resource += 1 if int(t.market) >= 2 else 0
						st.hubs += 1 if int(t.market) >= 4 else 0
				st.overclock += 1 if bool(g.players[rb].get("armor", false)) else 0
				if g.over < 0:
					wins.none += 1
				elif g.over == rb:
					wins.robots += 1
				else:
					wins.other += 1
			print("  vs %s done" % o)
	print("robots won %d, lost %d, unfinished %d of %d games" % [wins.robots, wins.other, wins.none, st.games])
	print("stats: ", st, " in ", (Time.get_ticks_msec() - t0) / 1000, " s")
	get_tree().quit()

extends Node
const AIPlayer = preload("res://scripts/rules/ai_player.gd")
func _ready() -> void:
	for np in [2, 3]:
		for rep in 2:
			var g := GameState.new()
			if np == 3:
				g.new_game("dinos", [], "", 3, ["robots", "mammals"])
			else:
				g.new_game(["dinos", "robots"][rep], [], ["mammals", "mammals"][rep])
			g.players[0].ai = true
			g.begin_turn()
			var snaps: Array = []
			for i in 80 * np:
				if g.over >= 0:
					break
				AIPlayer.take_turn(g)
				if i % (20 * np) == 0:
					var parts: Array = []
					for q in g.players:
						var hx: int = 0
						var un: int = 0
						for t in g.tiles:
							if int(t.owner) == int(q.id):
								hx += 1
								un += int(t.troops)
						parts.append("%s %dh %du %dc %dg" % [String(q.faction).substr(0, 3), hx, un, g.castle_count(int(q.id)), int(q.gold)])
					snaps.append("r%d: %s" % [g.turn, ", ".join(parts)])
			print("%dp game: rounds %d winner %s why %s" % [np, g.turn, str(g.over), g.over_why])
			for sn in snaps:
				print("    ", sn)
			var fights: int = 0
			for l in g.log_lines:
				if "win the fight" in l or "lose the fight" in l or "beaten back" in l:
					fights += 1
			print("    fights in the last 80 log lines: ", fights)
	get_tree().quit()

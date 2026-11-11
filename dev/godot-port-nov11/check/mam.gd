extends Node
const AIPlayer = preload("res://scripts/rules/ai_player.gd")
func _ready() -> void:
	for opp in ["dinos", "robots"]:
		var w := [0, 0, 0]
		var hexes := [0, 0]
		var gold := [0, 0]
		var units := [0, 0]
		for n in 12:
			var side: int = n % 2
			var g := GameState.new()
			if side == 0:
				g.new_game("mammals", [], opp)
			else:
				g.new_game(opp, [], "mammals")
			g.players[0].ai = true
			g.begin_turn()
			for i in 60:
				if g.over >= 0:
					break
				AIPlayer.take_turn(g)
				if i == 20:
					for t in g.tiles:
						if int(t.owner) >= 0:
							var m: int = 0 if g.players[int(t.owner)].faction == "mammals" else 1
							hexes[m] += 1
							units[m] += int(t.troops)
					for p in g.players:
						gold[0 if p.faction == "mammals" else 1] += int(p.gold)
			if g.over < 0:
				w[2] += 1
			else:
				w[0 if g.players[g.over].faction == "mammals" else 1] += 1
		print("mammals vs %s: [mammals, them, none] %s; at turn 20 (sum of 12): hexes %s units %s gold %s" % [opp, w, hexes, units, gold])
	get_tree().quit()

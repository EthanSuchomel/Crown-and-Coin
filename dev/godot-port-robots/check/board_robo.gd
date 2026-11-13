extends Node
## Not shipped: a board with every Robot building look (resource hexes of 2, 3, 4 markets; factory levels 1-3), and
## the Laser Strike in the attack dialog. Screenshots to SHOTS.
var OUT := ""
func _f(n: int = 3) -> void:
	for q in n:
		await get_tree().process_frame
func _shot(name: String) -> void:
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(OUT + name + ".png")
	print("shot ", name)
func _ready() -> void:
	OUT = OS.get_environment("SHOTS")
	var main = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	await _f()
	main.start_game("robots")
	await _f()
	var g = main.g
	var home: int = g.homes[0]
	var ring: Array = []
	for t in g.tiles:
		if t.terrain == "plain" and not t.castle and int(t.owner) < 0 and HexGrid.distance(int(t.id), home) <= 2:
			ring.append(int(t.id))
	var looks: Array = [{"market": 2}, {"market": 3}, {"market": 4}, {"market": 1}, {"market": 1, "barracks": 1, "bk": 2}, {"market": 1, "barracks": 1, "fort": 1, "bk": 3}]
	for k in mini(ring.size(), looks.size()):
		var t: Dictionary = g.tiles[ring[k]]
		t.owner = 0
		for key in looks[k]:
			t[key] = looks[k][key]
	print("placed ", mini(ring.size(), looks.size()), " looks")
	main.refresh()
	await _f()
	await _shot("b_looks")
	# Laser Strike dialog
	g.players[0].up = {"onsl": [0, 0, 3]}
	g.players[0].hand = ["onsl", "cons", "mobil"]
	g.players[0].favor = {}
	var m: int = ring[3]
	var foe: int = -1
	for j in HexGrid.neighbors(m):
		if g.tiles[j].terrain == "plain" and int(g.tiles[j].owner) < 0 and not g.tiles[j].castle:
			foe = j
			break
	g.tiles[foe].owner = 1
	g.add_units(foe, "galli", 12, false)
	g.add_units(m, "ltank", 2, true)
	g.add_units(m, "brawler", 4, true)
	main._start_card("onsl", -1)
	await _f()
	main._next_action(true)
	await _f()
	print("action ", g.cur_action(), " laser ok ", g.laser_ok(0, m, foe))
	main.sel = m
	main.refresh()
	main._open_move(m, foe)
	await _f()
	await _shot("b_laser_dialog")
	get_tree().quit()

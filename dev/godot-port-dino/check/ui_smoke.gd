extends Node
## Not shipped: drives the main screen through the Dinosaur rework's new UI paths and reports script errors.
func _f(n: int = 3) -> void:
	for q in n:
		await get_tree().process_frame

func _ready() -> void:
	var main = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	await _f()
	main.show_factions()
	await _f()
	main.start_game("dinos")
	await _f()
	var g = main.g
	g.players[0].gold = 500
	var home: int = g.homes[0]
	var n: int = -1
	for j in HexGrid.neighbors(home):
		if g.tiles[j].terrain == "plain" and not g.tiles[j].castle:
			n = j
			break
	g.tiles[n].owner = 0
	g.play = {"card": "nest", "step": 0, "moves": 0, "free_bk": false, "al_bought": 0, "al_free": 0}
	main.sel = n
	main.refresh()
	await _f()
	print("build bubbles: ", main.bubbles.get_child_count())
	g.build(n, "barracks")
	g.build(n, "market")
	g.play.step = 1
	main.sel = home
	main.refresh()
	await _f()
	print("advance bubbles at home: ", main.bubbles.get_child_count())
	g.do_volcano(0)
	main.sel = n
	main.refresh()
	await _f()
	g.buy_guard(n)
	main.refresh()
	await _f()
	print("leftover warning: ", main._leftover_warning())
	g.play.step = 2
	main.train_menu = "barracks"
	main.sel = n
	g.tiles[n].bk = 3
	main.refresh()
	await _f()
	print("barracks menu bubbles: ", main.bubbles.get_child_count())
	main.train_menu = ""
	main.sel = home
	main.refresh()
	await _f()
	print("home ring bubbles: ", main.bubbles.get_child_count())
	# the volcano's volley: an enemy hex in reach, then aim at it
	var far: int = -1
	for t in g.tiles:
		if t.terrain == "plain" and not t.castle and int(t.owner) < 0 and HexGrid.distance(home, int(t.id)) == 4:
			far = int(t.id)
			break
	g.tiles[far].owner = 1
	g.add_units(far, "brawler", 6, false)
	var far2: int = -1
	for t in g.tiles:
		if t.terrain == "plain" and not t.castle and int(t.owner) < 0 and HexGrid.distance(home, int(t.id)) == 3:
			far2 = int(t.id)
			break
	g.tiles[far2].owner = 1
	g.add_units(far2, "brawler", 4, false)
	g.players[0].volc = {"lv": 2, "cd": 0}
	g.play = {}
	g.volley.clear()
	g.volley.push_front(home)
	g.run_volley()
	main.sel = -1
	main.refresh()
	await _f()
	print("volley waiting: ", g.volley, " targets ", g.shot_targets(home))
	main._on_hex(far)
	await _f(10)
	print("after shot: volley ", g.volley, " lava playing ", main.board.lava_fx.size(), " brawlers left ", g.tiles[far].army)
	main.sel = home
	main._hex_info()
	main.sel = n
	main._hex_info()
	main._open_help()
	await _f()
	main._close_overlay()
	main.my_faction = "dinos"
	main.show_factions()
	await _f()
	print("UI smoke done")
	get_tree().quit()

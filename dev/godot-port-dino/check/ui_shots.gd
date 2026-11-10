extends Node
## Not shipped: screenshots of the Dinosaur rework's screens.
const OUT := "/tmp/claude-0/-home-claude/112a0b3f-dd28-5943-ad35-c12df06d67ec/scratchpad/godot/shots/"
func _f(n: int = 4) -> void:
	for q in n:
		await get_tree().process_frame
func _shot(name: String) -> void:
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(OUT + name + ".png")
	print("shot ", name)

func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(OUT)
	var main = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	await _f()
	main.my_faction = "dinos"
	main.show_factions()
	await _f(6)
	await _shot("1_factions")
	main.start_game("dinos")
	await _f()
	var g = main.g
	g.players[0].gold = 500
	var home: int = g.homes[0]
	var ns: Array = []
	for j in HexGrid.neighbors(home):
		if g.tiles[j].terrain == "plain" and not g.tiles[j].castle:
			ns.append(j)
	var n: int = ns[0]
	g.tiles[n].owner = 0
	g.tiles[n].barracks = 1
	g.tiles[n].market = 1
	g.tiles[n].bk = 3
	g.add_units(n, "alamo", 2, false)
	g.add_units(n, "galli", 3, true)
	if ns.size() > 1:
		g.tiles[ns[1]].owner = 0
		g.tiles[ns[1]].market = 2
	g.add_units(home, "mega", 2, true)
	g.play = {"card": "nest", "step": 1, "moves": 0, "free_bk": false, "al_bought": 0, "al_free": 0}
	main.sel = home
	main.refresh()
	await _f(6)
	await _shot("2_advance_home")
	main.sel = n
	main.refresh()
	await _f(6)
	await _shot("3_advance_barracks")
	g.play.step = 2
	main.train_menu = "barracks"
	main.sel = n
	main.refresh()
	await _f(6)
	await _shot("4_barracks_menu")
	main.train_menu = ""
	main.sel = home
	main.refresh()
	await _f(6)
	await _shot("5_home_ring")
	# a volcano eruption
	var far: int = -1
	for t in g.tiles:
		if t.terrain == "plain" and not t.castle and int(t.owner) < 0 and HexGrid.distance(home, int(t.id)) == 4:
			far = int(t.id)
			break
	g.tiles[far].owner = 1
	g.add_units(far, "brawler", 6, false)
	g.players[0].volc = {"lv": 2, "cd": 0}
	g.play = {}
	g.volley.clear()
	g.volley.push_front(home)
	main.sel = -1
	main.refresh()
	await _f(6)
	await _shot("6_volley")
	g.shoot_volley(home, far)
	main.refresh()
	await get_tree().create_timer(0.55).timeout
	await _shot("7_lava")
	await get_tree().create_timer(1.6).timeout
	main.sel = home
	main.refresh()
	await _f(6)
	await _shot("8_after")
	print("shots done")
	get_tree().quit()

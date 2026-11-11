extends Node
## Not shipped: drives the main screen through the new Fortify, materials and Dinosaur-card screens; takes screenshots.
var OUT := ""
func _f(n: int = 3) -> void:
	for q in n:
		await get_tree().process_frame
func _shot(name: String) -> void:
	if OUT == "":
		return
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(OUT + name + ".png")
	print("shot ", name)

func _open_neighbor(g, i: int) -> int:
	for j in HexGrid.neighbors(i):
		if g.tiles[j].terrain == "plain" and not g.tiles[j].castle and int(g.tiles[j].owner) < 0:
			return j
	return -1

func _ready() -> void:
	OUT = OS.get_environment("SHOTS")
	var main = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	await _f()
	for fac in ["dinos", "robots", "mammals", "mythical"]:
		main.my_faction = fac
		main.show_factions()
		await _f()
		if fac == "dinos":
			await _shot("factions_dinos")
	main.start_game("dinos")
	await _f()
	var g = main.g
	g.players[0].gold = 200
	g.players[0].up = {"stamp": [3, 3, 2], "pack": [1, 1, 3], "siege": [3, 1, 2], "hunt": [3, 3, 3], "nest": [3, 3, 3]}
	g.players[0].hand = ["stamp", "pack", "hunt"]
	main.refresh()
	await _f()
	await _shot("hand_dinos")
	var home: int = g.homes[0]
	var n: int = _open_neighbor(g, home)
	g.tiles[n].owner = 0
	g.tiles[n].barracks = 1
	var n2: int = _open_neighbor(g, n)
	g.tiles[n2].owner = 0
	g.tiles[n2].barracks = 1
	# the upgrade picker
	g.players[0].favor = {"stamp": 1}
	main._open_upgrade("stamp")
	await _f()
	await _shot("upgrade_stamp")
	main._close_overlay()
	# Stampede: Move, Build, Fortify
	main._start_card("stamp", 2)
	await _f()
	print("stamp: action ", g.cur_action(), " moves ", g.moves_left(), " lvl ", g.cur_lvl())
	main._next_action(true)
	await _f()
	print("stamp build: mat ", g.mat_of(0), " market price ", g.build_cost("market", g.tiles[n]), " notes ", main.notes.size())
	main.sel = n
	main.refresh()
	await _f()
	print("build bubbles: ", main.bubbles.get_child_count())
	await _shot("build_bubbles")
	main._open_trade()
	await _f()
	await _shot("trade")
	main._close_overlay()
	main._next_action(true)
	await _f()
	print("fortify: regrouping ", g.regrouping(), " fx ", g.play.fx, " notes ", main.notes)
	main.sel = home
	main.refresh()
	await _f()
	print("regroup targets from home: ", main.board.targets)
	await _shot("regroup")
	main._next_action()
	await _f()
	print("pick phase: ", g.cur_action(), " button warn: ", main._leftover_warning())
	await _shot("fortify_picks")
	g.fx_choose("advance")
	main.sel = n
	main.refresh()
	await _f()
	print("advance pick bubbles: ", main.bubbles.get_child_count(), " last step now ", g.last_step_now())
	await _shot("fortify_advance")
	main._next_action(true)
	await _f()
	print("after stamp: current ", g.current)
	# wait for the computer's turn
	var t0: int = Time.get_ticks_msec()
	while (main.busy or g.current != 0) and Time.get_ticks_msec() - t0 < 90000:
		await get_tree().create_timer(0.5).timeout
	print("computer turn done: current ", g.current, " busy ", main.busy, " ai mat ", g.mat_of(1))
	# Pack Call: Harvest, Recruit (Calling), Fortify (Join Up, On the Move, Rally)
	g.players[0].hand = ["pack", "hunt", "nest"]
	g.players[0].favor = {}
	g.tiles[n].owner = 0
	g.tiles[n2].owner = 0
	main._start_card("pack", -1)
	await _f()
	print("pack: action ", g.cur_action(), " dpick ", g.play.get("dpick", {}), " warn ", main._leftover_warning())
	await _shot("calling")
	main._on_hex(n2)
	await _f()
	print("after tap: dpick ", g.play.get("dpick", {}), " n2 army ", g.tiles[n2].army)
	main._next_action(true)
	await _f()
	main.sel = n
	main.refresh()
	await _f()
	await _shot("rally")
	main._do(func(): g.rally_to(n))
	print("rally: n army ", g.tiles[n].army)
	main._next_action()
	await _f()
	print("pack picks: ", g.fx_pick_list())
	main._do(func(): g.fx_choose("move"))
	await _f()
	print("move pick: ", g.cur_action(), " moves left ", g.moves_left())
	# an attack with Two Herds: Stampede level 3 Move
	var foe: int = _open_neighbor(g, n)
	if foe >= 0:
		g.tiles[foe].owner = 1
		g.add_units(foe, "brawler", 2, false)
	main._next_action(true)
	await _f()
	t0 = Time.get_ticks_msec()
	while (main.busy or g.current != 0) and Time.get_ticks_msec() - t0 < 90000:
		await get_tree().create_timer(0.5).timeout
	g.players[0].hand = ["stamp", "hunt", "nest"]
	g.players[0].favor = {}
	main._start_card("stamp", -1)
	await _f()
	if foe >= 0 and int(g.tiles[foe].owner) == 1:
		var att: int = -1
		for j in HexGrid.neighbors(foe):
			if int(g.tiles[j].owner) == 0 and int(g.tiles[j].fresh) > 0:
				att = j
				break
		print("two herds from ", att, ": ", g.two_herds_hex(att, foe) if att >= 0 else -2)
		if att >= 0:
			main._open_move(att, foe)
			await _f()
			await _shot("two_herds")
			main._close_overlay()
	# The Hunt: Advancements with Armor at home
	g.play = {"card": "hunt", "step": 2, "moves": 0, "free_bk": false}
	g.players[0].gold = 200
	main.sel = home
	main.refresh()
	await _f()
	print("hunt advance at home bubbles: ", main.bubbles.get_child_count(), " can armor ", g.can_armor(0))
	await _shot("armor")
	main._open_help()
	await _f()
	await _shot("help")
	main._close_overlay()
	# a Robot game: Fortify with 2 picks, the header button, a Build with materials
	main.start_game("robots")
	await _f()
	g = main.g
	g.players[0].up = {"sprot": [0, 0, 2]}
	g.players[0].hand = ["sprot", "cons", "mobil"]
	g.players[0].gold = 60
	main._start_card("sprot", -1)
	await _f()
	main.sel = g.homes[0]
	main.refresh()
	await _f()
	await _shot("robots_build")
	main._next_action(true)
	main._next_action(true)
	await _f()
	main._next_action()
	await _f()
	print("robots fortify picks: n ", g.play.fx.n, " warn ", main._leftover_warning())
	await _shot("robots_picks")
	g.fx_choose("recruit")
	main.sel = g.homes[0]
	main.refresh()
	await _f()
	main._next_action(true)
	await _f()
	print("robots after first pick: ", g.cur_action(), " done ", g.play.fx.done)
	main._next_action(true)
	await _f()
	print("robots turn ended: current ", g.current)
	t0 = Time.get_ticks_msec()
	while (main.busy or g.current != 0) and Time.get_ticks_msec() - t0 < 90000:
		await get_tree().create_timer(0.5).timeout
	# a Mythical Fortify: the picks are their own Build, Advancements and Recruit
	main.start_game("mythical")
	await _f()
	g = main.g
	g.players[0].hand = ["grove", "march", "arcan"]
	main._start_card("grove", -1)
	await _f()
	main._next_action()
	await _f()
	g.fx_choose("recruit")
	main.sel = g.homes[0]
	main.refresh()
	await _f()
	print("mythical fortify recruit bubbles: ", main.bubbles.get_child_count())
	await _shot("myth_pick")
	print("UI CHECK DONE")
	get_tree().quit()

extends Node
## Not shipped: drives the main screen through the new Robot screens (faction screen, punch cards, Build on a resource hex,
## the home castle's factory upgrades, trades, Laser Strike, Sortie, How to play, a computer Robot turn); screenshots
## when SHOTS is set (run under xvfb-run with --rendering-driver opengl3).
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

func _open_neighbor(g, i: int, not_: Array = []) -> int:
	for j in HexGrid.neighbors(i):
		if g.tiles[j].terrain == "plain" and not g.tiles[j].castle and int(g.tiles[j].owner) < 0 and not not_.has(j):
			return j
	return -1

func _ready() -> void:
	OUT = OS.get_environment("SHOTS")
	var main = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	await _f()
	main.my_faction = "robots"
	main.show_factions()
	await _f()
	await _shot("r_factions")
	main.start_game("robots")
	await _f()
	var g = main.g
	g.arena_fights = false   # battles settle on the board here, so the computer's turns don't wait on the Arena
	g.players[0].gold = 200
	g.players[0].mat = 40
	g.players[0].up = {"mobil": [3, 3, 3], "deploy": [3, 3, 3], "onsl": [3, 3, 3], "cons": [3, 3, 3], "sprot": [3, 3, 3]}
	g.players[0].hand = ["cons", "onsl", "mobil"]
	main.refresh()
	await _f()
	await _shot("r_hand")
	g.players[0].favor = {"deploy": 1}
	g.players[0].up.deploy = [1, 0, 2]
	main._open_upgrade("deploy")
	await _f()
	await _shot("r_upgrade")
	main._close_overlay()
	g.players[0].up.deploy = [3, 3, 3]
	var home: int = g.homes[0]
	var n: int = _open_neighbor(g, home)
	var m: int = _open_neighbor(g, home, [n])
	var q: int = _open_neighbor(g, home, [n, m])
	for i in [n, m, q]:
		g.tiles[i].owner = 0
	g.tiles[q].market = 1
	# Construction: Move -> Build -> Advancements
	main._start_card("cons", -1)
	await _f()
	print("cons: action ", g.cur_action(), " moves ", g.moves_limit(0))
	main._next_action(true)
	await _f()
	print("cons build: action ", g.cur_action(), " notes ", main.notes)
	main.sel = n
	main.refresh()
	await _f()
	print("build bubbles on an empty hex: ", main.bubbles.get_child_count())
	g.build(n, "market")
	g.build(n, "market")
	main.refresh()
	await _f()
	print("market price on the resource hex: ", g.build_cost("market", g.tiles[n]), " markets ", int(g.tiles[n].market))
	await _shot("r_build_resource")
	main.sel = q
	main.refresh()
	await _f()
	await _shot("r_build_market")
	print("leftover warning in Build: ", main._leftover_warning())
	main._next_action(true)
	await _f()
	print("cons advance: action ", g.cur_action(), " can Overclock ", g.can_armor(0))
	main.sel = home
	main.refresh()
	await _f()
	print("home castle bubbles: ", main.bubbles.get_child_count())
	await _shot("r_adv_home")
	print("leftover warning in Advancements: ", main._leftover_warning())
	# pick Barracks, then tap the ringed market
	main.robo_up = "barracks"
	main.sel = -1
	main.refresh()
	await _f()
	print("ringed for a barracks: ", main.board.targets, " (q=", q, ")")
	await _shot("r_adv_pick")
	main._on_hex(q)
	await _f()
	print("after the tap: q barracks ", int(g.tiles[q].barracks), " robo_up '", main.robo_up, "' undo ", main.undo_stack.size())
	main.robo_up = "fort"
	main.refresh()
	main._on_hex(q)
	await _f()
	print("then its fortress: q fort ", int(g.tiles[q].fort), " lv ", g.robo_lv(g.tiles[q]))
	main._undo()
	await _f()
	print("undo takes the fortress back: ", int(g.tiles[q].fort) == 0)
	main._on_hex(q)
	g.robo_up_targets(0, "fort")
	main.robo_up = "fort"
	main._on_hex(q)
	main.sel = q
	main.refresh()
	await _f()
	await _shot("r_factory")
	main._next_action(true)   # end of turn: the computer plays
	await _f()
	var t0: int = Time.get_ticks_msec()
	while (main.busy or g.current != 0) and Time.get_ticks_msec() - t0 < 300000:
		await get_tree().create_timer(0.5).timeout
	print("computer played; back to you: ", g.current == 0)
	# Mobilize: Advancements (Recompile) -> Recruit (Rebuild, Refit) -> Move
	g.players[0].hand = ["mobil", "onsl", "sprot"]
	g.players[0].gold = 200
	g.add_units(home, "brawler", 12, true)
	g.add_units(home, "rarch", 5, true)
	main._start_card("mobil", -1)
	await _f()
	main.sel = home
	main.refresh()
	await _f()
	print("mobil advance: trades at home ", g.trades_at(home))
	main._next_action(true)
	await _f()
	main.sel = home
	main.refresh()
	await _f()
	print("mobil recruit: trades at home ", g.trades_at(home))
	await _shot("r_trades")
	var kn: int = int(g.tiles[home].army.get("rknight", 0))
	main._do(func(): g.robo_trade(home, "rk"))
	print("Rebuild: knights ", kn, " -> ", int(g.tiles[home].army.get("rknight", 0)))
	main._next_action(true)
	main._next_action(true)
	await _f()
	var t1: int = Time.get_ticks_msec()
	while (main.busy or g.current != 0) and Time.get_ticks_msec() - t1 < 300000:
		await get_tree().create_timer(0.5).timeout
	# Onslaught: Harvest -> Advancements -> Move with a Laser Strike
	g.players[0].hand = ["onsl", "sprot", "cons"]
	var foe: int = _open_neighbor(g, m)
	if foe < 0:
		foe = _open_neighbor(g, n)
	g.tiles[foe].owner = 1
	g.add_units(foe, "galli", 30, false)
	g.add_units(m, "ltank", 2, true)
	g.add_units(m, "brawler", 4, true)
	main._start_card("onsl", -1)
	await _f()
	print("onsl: harvest notes ", main.notes, " action ", g.cur_action())
	main._next_action(true)   # Advancements -> Move
	await _f()
	print("onsl: action ", g.cur_action(), " laser ok ", g.laser_ok(0, m, foe))
	main.sel = m
	main.refresh()
	main._open_move(m, foe)
	await _f()
	await _shot("r_laser_dialog")
	main._close_overlay()
	var before: int = int(g.tiles[foe].troops)
	main._laser(m, foe)
	await _f()
	print("laser: ", before, " -> ", int(g.tiles[foe].troops), " notes ", main.notes)
	await _shot("r_laser_done")
	main._next_action(true)
	await _f()
	var t2: int = Time.get_ticks_msec()
	while (main.busy or g.current != 0) and Time.get_ticks_msec() - t2 < 300000:
		await get_tree().create_timer(0.5).timeout
	# Siege Protocol: Build -> Advancements -> Fortify with Dual Core, Sortie, Home Link
	print("your turn again: current ", g.current, " busy ", main.busy, " play ", g.play)
	g.players[0].hand = ["sprot", "cons", "mobil"]
	main._start_card("sprot", -1)
	await _f()
	print("sprot build notes: ", main.notes, " market price ", g.build_cost("market", g.tiles[m]))
	main._next_action(true)
	await _f()
	print("sprot advance: home brawlers ", int(g.tiles[home].army.get("brawler", 0)), " notes ", main.notes)
	main._next_action(true)
	await _f()
	print("sprot fortify: regrouping ", g.regrouping(), " n ", int(g.play.fx.n), " mvx ", g.play.fx.mvx, " notes ", main.notes)
	main._next_action(true)
	await _f()
	await _shot("r_fortify_picks")
	main._next_action(true)   # skip the picks: the Sortie
	await _f()
	print("sortie: action ", g.cur_action(), " last step ", g.last_step_now())
	await _shot("r_sortie")
	main._next_action(true)
	await _f()
	print("after the sortie: ", g.cur_action(), " ph ", g.play.get("fx", {}).get("ph", "-"), " last ", g.last_step_now())
	main._next_action(true)
	await _f()
	main._open_help()
	await _f()
	await _shot("r_help")
	main._close_overlay()
	print("UI check done")
	get_tree().quit()

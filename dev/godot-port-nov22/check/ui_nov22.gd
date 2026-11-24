extends Node
## Not shipped: screenshots of the Nov 22 screens (SHOTS=dir/ WHAT=title,setup,game ; xvfb-run, --rendering-driver opengl3).
var OUT := ""
func _f(n: int = 4) -> void:
	for q in n:
		await get_tree().process_frame
func _shot(name: String) -> void:
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(OUT + name + ".png")
	print("shot ", name)

func _ready() -> void:
	OUT = OS.get_environment("SHOTS")
	var what: String = OS.get_environment("WHAT")
	var main = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	await _f(6)
	if what.contains("title"):
		await _shot("title")
	if what.contains("setup"):
		main.show_factions()
		await _f(6)
		await _shot("setup_0")
		if main.has_method("_fsx_go"):
			main._fsx_go(1)
			await _f(6)
			await _shot("setup_1")
			main._fsx_go(2)
			await _f(6)
			await _shot("setup_2")
			main.pref_np = 3
			main._fsx_go(1)
			await _f(6)
			await _shot("setup_1_three")
			main.pref_np = 2
			main._fsx_info()
			await _f(6)
			await _shot("setup_info")
			main._close_overlay()
			main._fsx_level()
			await _f(6)
			await _shot("setup_level")
			main._close_overlay()
	if what.contains("game"):
		main.pref_np = 2
		main.pref_map = ""
		main.start_game("dinos")
		await _f(30)
		await _shot("game_mine")
		if main.has_method("_set_solo"):
			main.g.current = 1
			main.refresh()
			await _f(50)
			await _shot("game_solo")
			main.g.current = 0
			main.refresh()
			await _f(50)
			await _shot("game_back")
			main.board.zoom_at(main.board.size / 2.0, 2.0)
			await _f(10)
			await _shot("game_zoom")
			main.board.zoom_at(main.board.size / 2.0, 0.1)
			main._stats_hide(true)
			await _f(10)
			await _shot("game_stats_hidden")
			main._stats_hide(false)
		for mid in ["arena-2p"]:
			main.pref_map = mid
			main.start_game("robots")
			await _f(30)
			await _shot("game_" + mid)
		main.pref_map = ""
		main.pref_np = 3
		main.pref_opps = ["robots", "mammals"]
		main.start_game("mythical")
		await _f(30)
		await _shot("game_three")
	if what.contains("play"):
		main.pref_np = 2
		main.pref_map = ""
		main.pref_level = "expert"
		main.start_game("dinos")
		await _f(20)
		var cid: String = ""
		for c in main.g.players[0].hand:
			if Array(main.g.card_of(0, c).actions).has("recruit"):
				cid = c
		main._start_card(cid, -1)
		await _f(4)
		var n: int = 0
		while main.g.cur_action() != "recruit" and n < 3:
			main._next_action(true)
			n += 1
			await _f(2)
		main._on_hex(int(main.g.homes[0]))
		await _f(10)
		await _shot("play_recruit")
		print("hexinfo size ", main.hexinfo.size, " min ", main.hexinfo.get_combined_minimum_size(), " pos ", main.hexinfo.position)
		for c in main.hexinfo.get_child(0).get_children():
			print("  ", c.get_class(), " ", c.size, " min ", c.get_combined_minimum_size())
		main.board.zoom_at(main.board.center(int(main.g.homes[0])), 2.2)
		await _f(10)
		await _shot("play_recruit_zoom")
		main.board.zoom_at(Vector2.ZERO, 0.1)
		var t0: int = Time.get_ticks_msec()
		n = 0
		while main.g.current == 0 and n < 6:
			main._next_action(true)
			n += 1
			await _f(2)
		await _f(20)
		await _shot("play_ai_turn")
		while main.g.current != 0 and Time.get_ticks_msec() - t0 < 60000:
			await _f(5)
		print("computer turn (expert) took %.1f s" % ((Time.get_ticks_msec() - t0) / 1000.0))
		await _f(40)
		await _shot("play_back")
	get_tree().quit()

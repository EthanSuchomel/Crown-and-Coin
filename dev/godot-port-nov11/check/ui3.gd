extends Node
## Not shipped: drives the 3-player screens and takes screenshots.
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
func _ready() -> void:
	OUT = OS.get_environment("SHOTS")
	var main = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	await _f()
	main.my_faction = "dinos"
	main.pref_np = 3
	main.pref_opps = ["mythical", "robots"]
	main.show_factions()
	await _f()
	await _shot("f3_factions")
	main.start_game("dinos")
	await _f(5)
	var g = main.g
	print("3p game: players ", g.players.size(), " colors ", g.players.map(func(p): return p.col), " homes ", g.homes)
	await _shot("f3_board")
	# your turn: play a card and end it; then both computers play
	main._start_card(g.players[0].hand[0], -1)
	await _f()
	for k in 6:
		if g.current != 0 or g.over >= 0:
			break
		main._next_action(true)
		await _f()
	print("after your turn: current ", g.current, " busy ", main.busy)
	await get_tree().create_timer(3.0).timeout
	await _shot("f3_ai_turn")
	var t0: int = Time.get_ticks_msec()
	var seen: Array = []
	while (main.busy or g.current != 0) and Time.get_ticks_msec() - t0 < 200000:
		if not seen.has(g.current):
			seen.append(g.current)
		await get_tree().create_timer(0.5).timeout
	print("computers played: ", seen, " back to you: ", g.current == 0, " round ", g.turn)
	await _shot("f3_back")
	main._open_help()
	await _f()
	await _shot("f3_help")
	main._close_overlay()
	# a battle between you and the 3rd seat: the Arena gets the right sides and colours
	print("arena sides you vs seat 2: ", main._arena_factions(0, 2), " ", main._arena_cols(0, 2))
	# knocked out, then the end screen
	g.knock_out(1, 2, "home")
	main.refresh()
	await _f()
	await _shot("f3_knocked")
	g.knock_out(2, 0, "home")
	main.refresh()
	await _f()
	await _shot("f3_won")
	print("UI3 DONE over ", g.over, " ", g.over_why)
	get_tree().quit()

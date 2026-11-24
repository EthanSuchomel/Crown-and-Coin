extends Node
## Not shipped: two copies play online through the lobby (ROLE=host|guest, DIR, SHOTS) against check/mock.py.
var main
var DIR := ""
func _f(n: int = 4) -> void:
	for q in n:
		await get_tree().process_frame
func _shot(name: String) -> void:
	if OS.get_environment("SHOTS") == "":
		return
	await _f(4)
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(OS.get_environment("SHOTS") + name + ".png")
func _until(f: Callable, sec: float) -> bool:
	var t := 0.0
	while not f.call():
		await get_tree().create_timer(0.2).timeout
		t += 0.2
		if t > sec:
			return false
	return true
func _fail(m: String) -> void:
	print("FAIL ", m)
	get_tree().quit(1)
func _end_turn() -> void:
	for c in main.g.players[0].hand:
		if main.g.play_card(String(c)):
			break
	main.g.finish_turn()
	main.refresh()
func _L() -> Dictionary:
	return main.online.get("lobby", {})

func _ready() -> void:
	var role: String = OS.get_environment("ROLE")
	DIR = OS.get_environment("DIR")
	main = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	await _f(6)
	main.net.url = "http://127.0.0.1:8765"
	main.net.key = "testkey"
	main.net.my_id = role + "-id"
	main._net_timer.wait_time = 0.5
	if role == "host":
		main.my_faction = "mammals"
		main.pref_map = "the-great-divide-2p"
		main._online_setup()
		await _f(6)
		main._fsx_go(1)
		await _shot("h_setup_opp")
		await main._net_create()
		await _shot("h_lobby_empty")
		var fa := FileAccess.open(DIR + "/code.txt", FileAccess.WRITE)
		fa.store_string(main.online.code)
		fa.close()
		if not await _until(func(): return main.online.get("joined", false), 40): return _fail("host: no join")
		await _shot("h_lobby_joined")
		if not await _until(func(): return bool(_L().get("guest", {}).get("ready", false)), 40): return _fail("host: guest never ready")
		await _shot("h_lobby_ready")
		print("HOST sees guest ", _L().guest)
		await main._lobby_start()
		await _f(10)
		if main.g == null: return _fail("host: game didn't start")
		print("HOST game: ", main.g.players[0].faction, "/", main.g.players[0].col, " vs ", main.g.players[1].faction, "/", main.g.players[1].col)
		if not await _until(func(): return main.g.current == 0 and main.online.get("last_cur", 1) == 0, 30): return _fail("host: no turn")
		_end_turn()
		if not await _until(func(): return main.g.current == 0, 40): return _fail("host: turn not back")
		# the host wins
		main.g.over = 0
		main.g.over_why = "home"
		main.refresh()
		await _f(20)
		await _shot("h_over")
		await get_tree().create_timer(2.0).timeout
		await main._net_next()
		await _shot("h_lobby_r2")
		print("HOST round2 lobby ", _L())
		if not await _until(func(): return bool(_L().get("guest", {}).get("ready", false)) and String(_L().guest.f) == "robots", 40): return _fail("host: r2 not ready")
		await main._lobby_start()
		await _f(10)
		if main.g == null: return _fail("host: game 2 didn't start")
		print("HOST game2: ", main.g.players[0].faction, " vs ", main.g.players[1].faction, " map ", main.g.map_id)
	else:
		if not await _until(func(): return FileAccess.file_exists(DIR + "/code.txt"), 60): return _fail("guest: no code")
		await main._net_join(FileAccess.get_file_as_string(DIR + "/code.txt"))
		await _f(6)
		if not main.online.get("in_lobby", false): return _fail("guest: not in lobby")
		await _shot("g_lobby")
		print("GUEST default ", _L().guest)
		await main._lobby_pick_faction("dinos")
		await main._lobby_pick_color("yellow")
		await _shot("g_lobby_picked")
		await main._lobby_change(func(X): X.guest["ready"] = true)
		await _shot("g_lobby_ready")
		if not await _until(func(): return main.g != null, 40): return _fail("guest: game never started")
		print("GUEST game: ", main.g.players[0].faction, "/", main.g.players[0].col, " vs ", main.g.players[1].faction)
		if not await _until(func(): return main.g.current == 0, 40): return _fail("guest: no turn")
		_end_turn()
		if not await _until(func(): return main.g.over >= 0, 40): return _fail("guest: never saw the end")
		await _f(20)
		await _shot("g_over")
		await get_tree().create_timer(3.0).timeout
		await main._net_next()
		await _shot("g_lobby_r2")
		print("GUEST round2 lobby ", _L())
		await main._lobby_pick_faction("robots")
		await main._lobby_change(func(X): X.guest["ready"] = true)
		if not await _until(func(): return main.g != null, 40): return _fail("guest: game 2 never started")
		print("GUEST game2: ", main.g.players[0].faction, " vs ", main.g.players[1].faction)
	print("DONE ", role)
	get_tree().quit(0)

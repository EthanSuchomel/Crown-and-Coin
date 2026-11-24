extends Node
## Not shipped: two copies of the game play a few turns online against check/mock.py (ROLE=host|guest, DIR=shared folder).
var main
var DIR := ""
func _f(n: int = 4) -> void:
	for q in n:
		await get_tree().process_frame
func _shot(name: String) -> void:
	if OS.get_environment("SHOTS") == "":
		return
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
func _end_turn() -> void:
	var ok := false
	for c in main.g.players[0].hand:
		if main.g.play_card(String(c)):
			ok = true
			break
	if not ok or main.g.play.is_empty():
		print("TEST: no card could be played, play=", main.g.play, " volley=", main.g.volley)
	main.g.finish_turn()
	main.refresh()

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
	main.show_online()
	await _f(20)
	await _shot(role + "_online")
	if role == "host":
		main.my_faction = "dinos"
		main.pref_map = ""
		main._online_setup()
		await _f(10)
		main._fsx_go(2)
		await _f(10)
		await _shot("host_setup_2")
		await main._net_create()
		await _f(10)
		await _shot("host_wait")
		print("CODE ", main.online.code)
		var fa := FileAccess.open(DIR + "/code.txt", FileAccess.WRITE)
		fa.store_string(main.online.code)
		fa.close()
		if not await _until(func(): return main.g != null, 60):
			print("FAIL host: nobody joined"); get_tree().quit(1); return
		print("host opened: me=", main.g.players[0].faction, " vs ", main.g.players[1].faction, " current=", main.g.current)
		for turn in 3:
			if not await _until(func(): return main.g.current == 0 and main.online.get("last_cur", 1) == 0, 60):
				print("FAIL host: turn never came back"); get_tree().quit(1); return
			print("host turn ", main.g.turn, " rev ", main.online.rev, " t=", Time.get_ticks_msec())
			await _f(5)
			_end_turn()
			await _f(5)
		await _until(func(): return main.g.current == 0, 30)
		await _f(20)
		await _shot("host_game")
		var own := [0, 0]
		for t in main.g.tiles:
			if int(t.owner) >= 0:
				own[int(t.owner)] += 1
		print("HOST owners ", own, " turn ", main.g.turn, " rev ", main.online.rev)
		main._net_leave()
		await _f(30)
		await _shot("host_online_after")
	else:
		if not await _until(func(): return FileAccess.file_exists(DIR + "/code.txt"), 60):
			print("FAIL guest: no code"); get_tree().quit(1); return
		var code: String = FileAccess.get_file_as_string(DIR + "/code.txt")
		await main._net_join(code.to_lower())
		await _f(10)
		if main.g == null:
			print("FAIL guest: join didn't open"); get_tree().quit(1); return
		print("guest opened: me=", main.g.players[0].faction, " vs ", main.g.players[1].faction, " current=", main.g.current)
		await _shot("guest_their_turn")
		for turn in 3:
			if not await _until(func(): return main.g.current == 0, 60):
				print("FAIL guest: turn never came"); get_tree().quit(1); return
			print("guest turn ", main.g.turn, " rev ", main.online.rev, " t=", Time.get_ticks_msec())
			await _f(5)
			if turn == 0:
				await _shot("guest_my_turn")
			_end_turn()
			await _f(5)
		await get_tree().create_timer(2.0).timeout
		var own := [0, 0]
		for t in main.g.tiles:
			if int(t.owner) >= 0:
				own[int(t.owner)] += 1
		print("GUEST owners(swapped) ", [own[1], own[0]], " turn ", main.g.turn, " rev ", main.online.rev, " cur ", main.g.current, " pushing ", main._net_pushing)
	print("DONE ", role)
	get_tree().quit(0)

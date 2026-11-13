extends Node
## Not shipped: screenshots of the hand with trophies, a picked card, an action's info box and the attack window.
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
	var main = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	await _f()
	main.pref_np = 2
	main.start_game("dinos")
	await _f(6)
	var g = main.g
	for cid in g.players[0].hand:
		g.players[0].up[cid] = [1, 2, 0]
	main.refresh()
	await _f()
	await _shot("i_hand")
	var cid: String = String(g.players[0].hand[0])
	main.preview = cid
	main.refresh()
	await _f()
	await _shot("i_card")
	main._open_action_info(0, cid, 1)
	await _f()
	await _shot("i_info")
	main._close_overlay()
	# an attack window: an enemy army next to home
	var home: int = g.homes[0]
	var n: int = -1
	for j in HexGrid.neighbors(home):
		if g.tiles[j].terrain == "plain" and not g.tiles[j].castle:
			n = j
			break
	g.tiles[n].owner = 1
	g.tiles[n].troops = 3
	g.tiles[n].army = {"rarch": 3}
	main.preview = ""
	main.refresh()
	await _f()
	if main.has_method("_open_move"):
		main._open_move(home, n)
	await _f()
	await _shot("i_attack")
	get_tree().quit()

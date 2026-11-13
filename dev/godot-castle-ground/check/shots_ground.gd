extends Node
## Not shipped: 3-player boards with every faction's home castle, to see the castle hex grounds. Screenshots to SHOTS.
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
	var n := 0
	for setup in [["mammals", ["robots", "dinos"]], ["mythical", ["robots", "dinos"]]]:
		main.pref_np = 3
		main.pref_opps = setup[1]
		main.start_game(setup[0])
		await _f(6)
		print("homes ", main.g.homes, " factions ", main.g.players.map(func(p): return p.faction))
		await _shot("board_%d" % n)
		n += 1
	get_tree().quit()

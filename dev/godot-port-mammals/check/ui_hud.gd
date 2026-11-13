extends Node
## Not shipped: screenshots of the game screen with the corner box (SHOTS=dir/, xvfb-run, --rendering-driver opengl3).
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
	main.start_game("dinos")
	await _f(8)
	await _shot("hud_dinos")
	main.g.players[0].gold = 27
	main.g.players[0].mat = 1
	main.refresh()
	await _f()
	main._open_trade()
	await _f()
	await _shot("hud_trade")
	main._close_overlay()
	main.pref_np = 3
	main.pref_opps = ["robots", "dinos"]
	main.start_game("mythical")
	await _f(8)
	await _shot("hud_myth3")
	get_tree().quit()

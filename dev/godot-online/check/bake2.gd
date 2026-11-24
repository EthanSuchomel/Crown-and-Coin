extends Node
var main
func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	for i in 6: await get_tree().process_frame
	await get_tree().create_timer(float(OS.get_environment("WAIT"))).timeout
	main.pref_np = 2
	main.pref_map = "the-great-divide-2p"
	main.start_game("mammals")
	for k in 4:
		await get_tree().create_timer(2.0).timeout
		var tx = main.board._bake_tex
		if tx != null:
			tx.get_image().save_png(OS.get_environment("SHOTS") + "k%d.png" % k)
		main.board._bake_for = "x%d" % k
		main.board.queue_redraw()
	get_tree().quit()

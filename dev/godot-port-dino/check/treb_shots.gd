extends Node
## Not shipped: screenshots of the trebuchet firing animation (steel for the Robots, bone for the Mammals).
const OUT := "/tmp/claude-0/-home-claude/112a0b3f-dd28-5943-ad35-c12df06d67ec/scratchpad/godot/shots/"
func _f(n: int = 4) -> void:
	for q in n:
		await get_tree().process_frame
func _shot(name: String, crop: Rect2 = Rect2()) -> void:
	await RenderingServer.frame_post_draw
	var img: Image = get_viewport().get_texture().get_image()
	img.save_png(OUT + name + ".png")
	if crop.size.x > 0:
		var r := Rect2i(crop.grow(crop.size.x * 0.1)).intersection(Rect2i(Vector2i.ZERO, img.get_size()))
		var c: Image = img.get_region(r)
		c.resize(c.get_width() * 4, c.get_height() * 4, Image.INTERPOLATE_NEAREST)
		c.save_png(OUT + name + "_zoom.png")
	print("shot ", name)

func _run(main, fac: String, tag: String) -> void:
	main.start_game(fac)
	await _f()
	var g = main.g
	var home: int = g.homes[0]
	var n: int = -1
	for j in HexGrid.neighbors(home):
		if g.tiles[j].terrain == "plain" and not g.tiles[j].castle:
			n = j
			break
	g.tiles[n].owner = 0
	g.tiles[n].treb = 2
	g.add_units(n, "brawler" if fac != "robots" else "robot", 2, false)
	var far: int = -1
	for t in g.tiles:
		if t.terrain == "plain" and not t.castle and int(t.owner) < 0 and HexGrid.distance(n, int(t.id)) == 2:
			far = int(t.id)
			break
	g.tiles[far].owner = 1
	g.add_units(far, "brawler", 6, false)
	main.sel = -1
	main.refresh()
	await _f(6)
	await _shot(tag + "_0_before")
	g.fire_treb(n, far)
	main.refresh()
	var ta = main.board.treb_anim
	var t0: int = Time.get_ticks_msec()
	var marks: Array = [0.25, 0.55, 0.75, 0.95, 1.25, 1.75]
	var k: int = 0
	while k < marks.size():
		await get_tree().process_frame
		if ta.playing and ta._t >= float(marks[k]):
			await _shot("%s_%d_t%.2f" % [tag, k + 1, ta._t], ta._rect.get_global_rect())
			k += 1
		if Time.get_ticks_msec() - t0 > 8000:
			print("timed out; playing=", ta.playing)
			break
	while ta.playing and Time.get_ticks_msec() - t0 < 9000:
		await get_tree().process_frame
	await _f(4)
	await _shot(tag + "_9_after")
	print(tag, " done: from ", n, " to ", far, " anim_hex ", main.board.anim_hex, " queue ", ta.queue.size())

func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(OUT)
	var main = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	await _f()
	await _run(main, "robots", "treb_steel")
	await _run(main, "mammals", "treb_bone")
	get_tree().quit()

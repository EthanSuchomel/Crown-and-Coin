extends Node
## Edge-aware terrain (Ethan, 2026-11-17: "That looks amazing please implement that into the godot game"). Draws the
## board's ground once, on the GPU, into a picture the board view then shows every frame:
##   1. every hex's soft grass tile (as before)
##   2. forest canopy bridges between neighbouring forests (under the forest tiles)
##   3. each forest / mountain / lake tile, faded side by side by what is next to it (terrain_tile.gdshader)
##   4. water bridges between neighbouring lakes (over their beaches)
## Built again only when the board's terrain changes (a new map, a new castle). Matches dev/edge-aware/preview.py.

signal baked(tex: Texture2D, sig: String)

const PX := 7.0                       # picture pixels per board unit
const TILE_SHADER := preload("res://scripts/ui/terrain_tile.gdshader")
const BRIDGE_SHADER := preload("res://scripts/ui/terrain_bridge.gdshader")

var board                             # the BoardView


## Which kind of edge-aware terrain a hex is: 0 forest, 1 mountain, 2 water, -1 none (grass, castle, off the board).
func kind_of(t: Dictionary) -> int:
	if t.terrain == "mountain":
		return 1
	if t.terrain == "water":
		return 2
	if board._whole_tile(t) == "hex_forest":
		return 0
	return -1


func bake(tiles: Array, sig: String) -> void:
	var HR: float = board.HR
	var rect_units := Vector2(board._grid_h(), board._grid_w())
	var vp := SubViewport.new()
	vp.size = Vector2i(ceili(rect_units.x * PX), ceili(rect_units.y * PX))
	vp.transparent_bg = true
	vp.disable_3d = true
	vp.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_LINEAR
	vp.render_target_update_mode = SubViewport.UPDATE_ONCE
	add_child(vp)
	var noise: Texture2D = board.tex("edge_noise")
	var sk: float = (HR + 0.3) * 1.10
	var tile_size := Vector2(sk * sqrt(3.0), 2.0 * sk)
	var live: Array = tiles.filter(func(t): return t.terrain != "void")
	var kinds: Dictionary = {}
	for t in live:
		kinds[int(t.id)] = kind_of(t)
	# 1. grass
	var grass := Node2D.new()
	vp.add_child(grass)
	grass.draw.connect(func():
		for t in live:
			var c: Vector2 = board._grid_pos(int(t.id)) * PX
			grass.draw_colored_polygon(board._hex_points(c, (HR + 0.3) * PX), Color("2f7d22"))
		for t in live:
			var i: int = int(t.id)
			var c2: Vector2 = board._grid_pos(i) * PX
			var g: Texture2D = board.tex("hex_grass_%d_soft" % ((((i + 5) * 2654435761 & 0xFFFFFFFF) >> 7) % 3))
			if g != null:
				grass.draw_texture_rect(g, Rect2(c2 - tile_size * PX / 2.0, tile_size * PX), false))
	# 2. under the joins: each tile solid out to the edges it shares with its own terrain; then the forest canopy bridges
	for t in live:
		_add_tile(vp, t, kinds, tile_size, noise, true)
	_add_bridge(vp, tiles, kinds, 0, rect_units, noise)
	# 3. the terrain tiles, faded side by side
	for t in live:
		_add_tile(vp, t, kinds, tile_size, noise, false)
	# 4. lake bridges
	_add_bridge(vp, tiles, kinds, 2, rect_units, noise)
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var img: Image = vp.get_texture().get_image() if vp.get_texture() != null else null
	vp.queue_free()
	if img == null or img.is_empty():
		baked.emit(null, sig)
		return
	baked.emit(ImageTexture.create_from_image(img), sig)


func _add_tile(vp: SubViewport, t: Dictionary, kinds: Dictionary, tile_size: Vector2, noise: Texture2D, under: bool) -> void:
	var HR: float = board.HR
	if true:   # (one block: the tile for hex t)
		var i: int = int(t.id)
		var kd: int = kinds[i]
		if kd < 0 or (under and kd == 2):   # lakes have no solid layer: the water bridge joins them
			return
		var texr: Texture2D = board.tex(["hex_forest_soft", "hex_mountain_soft", "hex_water_soft"][kd])
		if texr == null:
			return
		var modes := PackedInt32Array()
		for j in HexGrid.neighbor_dirs(i):
			var nk: int = int(kinds.get(j, -1)) if j >= 0 else -1
			modes.append(1 if nk == kd else (2 if nk >= 0 else 0))
		var sp := Sprite2D.new()
		sp.texture = texr
		sp.centered = true
		sp.position = board._grid_pos(i) * PX
		sp.scale = tile_size * PX / Vector2(texr.get_size())
		var mat := ShaderMaterial.new()
		mat.shader = TILE_SHADER
		mat.set_shader_parameter("modes", modes)
		mat.set_shader_parameter("kind", kd)
		mat.set_shader_parameter("size_units", tile_size)
		mat.set_shader_parameter("hr", HR)
		mat.set_shader_parameter("noise_tex", noise)
		mat.set_shader_parameter("underlay", under)
		mat.set_shader_parameter("seed", Vector2(fmod(i * 0.137, 1.0), fmod(i * 0.291, 1.0)))
		sp.material = mat
		vp.add_child(sp)


## The joins for one terrain (0 forest, 2 water): a capsule centre to centre for every neighbouring pair, and a disc
## on every corner three of them share.
func _add_bridge(vp: SubViewport, tiles: Array, kinds: Dictionary, kd: int, rect_units: Vector2, noise: Texture2D) -> void:
	var HR: float = board.HR
	var segs: Array[Vector4] = []
	var corners := PackedVector2Array()
	for t in tiles:
		var i: int = int(t.id)
		if int(kinds.get(i, -1)) != kd:
			continue
		var a: Vector2 = board._grid_pos(i)
		var nb: Array[int] = HexGrid.neighbor_dirs(i)
		for k in 6:
			var j: int = nb[k]
			if j > i and int(kinds.get(j, -1)) == kd:
				var b: Vector2 = board._grid_pos(j)
				segs.append(Vector4(a.x, a.y, b.x, b.y))
			var j2: int = nb[(k + 1) % 6]
			if j >= 0 and j2 >= 0 and int(kinds.get(j, -1)) == kd and int(kinds.get(j2, -1)) == kd:
				corners.append(board._corner(a, HR, k + 1))
	if segs.is_empty():
		return
	var patch: Texture2D = board.tex("hex_forest_patch" if kd == 0 else "hex_water_patch")
	if patch == null:
		return
	segs = segs.slice(0, 160)
	var rect := ColorRect.new()
	rect.size = rect_units * PX
	var mat := ShaderMaterial.new()
	mat.shader = BRIDGE_SHADER
	mat.set_shader_parameter("segs", segs)
	mat.set_shader_parameter("nseg", segs.size())
	mat.set_shader_parameter("corners", corners.slice(0, 96))
	mat.set_shader_parameter("ncorn", mini(corners.size(), 96))
	mat.set_shader_parameter("wid", HR * (0.78 if kd == 0 else 0.46))
	mat.set_shader_parameter("hr", HR)
	mat.set_shader_parameter("rect_units", rect_units)
	mat.set_shader_parameter("patch_tex", patch)
	mat.set_shader_parameter("patch_units", float(patch.get_width()) * (HR + 0.3) * sqrt(3.0) * 1.10 / 222.0)
	mat.set_shader_parameter("noise_tex", noise)
	rect.material = mat
	vp.add_child(rect)

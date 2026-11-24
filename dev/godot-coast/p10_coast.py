"""Ethan, 2026-11-23: "give each map a water/beach border so that there is no more dark void around it? Also clean up
the borders of the maps and the borders of the neutral castles."
- terrain_bake.gd: the baked ground reaches COAST_MG board units past the grid on every side; a coast layer over the
  grass (terrain_coast.gdshader) draws sand round the land's outer rim, wet sand, surf, shallow water fading to the open
  sea. The shore follows a blurred distance-from-land map (made here on the CPU), so it's smooth and wavy instead of
  following the hexes' zigzag edges. Holes in a hand-made map are sea too.
- board_view.gd: an ocean (ocean.gdshader, slowly moving) fills the whole board behind the map, moving and zooming with
  it; the baked ground is drawn with its margin.
- Neutral castles: drawn from hex_castle_neutral_soft.png (the tile's hard hex edge and grass corners fade into the
  ground) with no green hexagon under it.
Usage: python3 p10_coast.py PROJ"""
import sys, shutil, os
sys.path.insert(0, __file__.rsplit('/', 2)[0] + '/godot-port-nov22')
from common import F
P = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
for rel in ['scripts/ui/terrain_coast.gdshader', 'scripts/ui/ocean.gdshader', 'art/terrain/hex_castle_neutral_soft.png']:
    shutil.copy(os.path.join(here, 'files', rel), os.path.join(P, rel))

f = F(P + '/scripts/ui/terrain_bake.gd')
f.rep('''const BRIDGE_SHADER := preload("res://scripts/ui/terrain_bridge.gdshader")''', '''const BRIDGE_SHADER := preload("res://scripts/ui/terrain_bridge.gdshader")
const COAST_SHADER := preload("res://scripts/ui/terrain_coast.gdshader")
const COAST_RES := 1.5                # board units per point of the distance-from-land map''')
f.rep('''    var rect_units := Vector2(board._grid_h(), board._grid_w())
    var vp := SubViewport.new()
    vp.size = Vector2i(ceili(rect_units.x * PX), ceili(rect_units.y * PX))''', '''    var rect_units := Vector2(board._grid_h(), board._grid_w())
    var MG: float = board.COAST_MG   # the coast and some sea round the grid (2026-11-23)
    var full := rect_units + Vector2(MG, MG) * 2.0
    var vp := SubViewport.new()
    vp.size = Vector2i(ceili(full.x * PX), ceili(full.y * PX))''')
f.rep('''    # 1. grass
    var grass := Node2D.new()
    vp.add_child(grass)''', '''    var root := Node2D.new()   # everything in grid coordinates, shifted by the margin
    root.position = Vector2(MG, MG) * PX
    vp.add_child(root)
    # 1. grass
    var grass := Node2D.new()
    root.add_child(grass)''')
f.rep('''    # 2. under the joins: each tile solid out to the edges it shares with its own terrain; then the forest canopy bridges
    for t in live:
        _add_tile(vp, t, kinds, tile_size, noise, true)
    _add_bridge(vp, tiles, kinds, 0, rect_units, noise)
    # 3. the terrain tiles, faded side by side
    for t in live:
        _add_tile(vp, t, kinds, tile_size, noise, false)
    # 4. lake bridges
    _add_bridge(vp, tiles, kinds, 2, rect_units, noise)''', '''    # 1b. the coast: sand over the land's outer rim, surf and shallow water out to the open sea
    _add_coast(root, live, MG, full, noise)
    # 2. under the joins: each tile solid out to the edges it shares with its own terrain; then the forest canopy bridges
    for t in live:
        _add_tile(root, t, kinds, tile_size, noise, true)
    _add_bridge(root, tiles, kinds, 0, rect_units, noise)
    # 3. the terrain tiles, faded side by side
    for t in live:
        _add_tile(root, t, kinds, tile_size, noise, false)
    # 4. lake bridges
    _add_bridge(root, tiles, kinds, 2, rect_units, noise)
    # 5. the coast again over the tiles, off the land only
    _add_coast(root, live, MG, full, noise, true)''')
f.rep('''func _add_tile(vp: SubViewport, t: Dictionary''', '''func _add_tile(vp: Node, t: Dictionary''')
f.rep('''func _add_bridge(vp: SubViewport, tiles: Array''', '''func _add_bridge(vp: Node, tiles: Array''')
s = f.s.rstrip('\n') + '\n'

f.s = s
f.s += '''

## The coast layer (2026-11-23). A map of how far every point is from the land's edge (negative on land), blurred,
## handed to terrain_coast.gdshader on one rectangle over the whole picture.
var _coast_tex: ImageTexture = null

func _add_coast(root: Node2D, live: Array, MG: float, full: Vector2, noise: Texture2D, top: bool = false) -> void:
	var HR: float = board.HR
	var w: int = ceili(full.x / COAST_RES) + 1
	var h: int = ceili(full.y / COAST_RES) + 1
	var LO: float = -20.0
	var HI: float = 40.0
	if top and _coast_tex != null:
		_coast_rect(root, MG, w, h, LO, HI, noise, true)
		return
	var land := PackedByteArray()
	land.resize(w * h)
	land.fill(0)
	var ap: float = (HR + 0.3) * 0.8660254   # a hex's apothem (pointy-top hexes)
	for t in live:
		var c: Vector2 = board._grid_pos(int(t.id)) + Vector2(MG, MG)
		for y in range(maxi(0, int((c.y - HR - 1.0) / COAST_RES)), mini(h, int((c.y + HR + 1.0) / COAST_RES) + 2)):
			for x in range(maxi(0, int((c.x - HR - 1.0) / COAST_RES)), mini(w, int((c.x + HR + 1.0) / COAST_RES) + 2)):
				var ax: float = absf(x * COAST_RES - c.x)
				var ay: float = absf(y * COAST_RES - c.y)
				if ax <= ap and ax * 0.5 + ay * 0.8660254 <= ap:
					land[y * w + x] = 1
	var d_sea: PackedFloat32Array = _chamfer(land, w, h, 1)    # at sea: how far to land
	var d_land: PackedFloat32Array = _chamfer(land, w, h, 0)   # on land: how far to the sea
	var sd := PackedFloat32Array()
	sd.resize(w * h)
	for i in w * h:
		sd[i] = (d_sea[i] - d_land[i]) * COAST_RES
	sd = _blur(_blur(sd, w, h), w, h)
	var bytes := PackedByteArray()
	bytes.resize(w * h)
	for i in w * h:
		bytes[i] = clampi(int(round((sd[i] - LO) / (HI - LO) * 255.0)), 0, 255)
	_coast_tex = ImageTexture.create_from_image(Image.create_from_data(w, h, false, Image.FORMAT_L8, bytes))
	_coast_rect(root, MG, w, h, LO, HI, noise, top)


func _coast_rect(root: Node2D, MG: float, w: int, h: int, LO: float, HI: float, noise: Texture2D, top: bool) -> void:
	var rect := ColorRect.new()
	rect.position = -Vector2(MG, MG) * PX
	rect.size = Vector2(w - 1, h - 1) * COAST_RES * PX
	var mat := ShaderMaterial.new()
	mat.shader = COAST_SHADER
	mat.set_shader_parameter("dist_tex", _coast_tex)
	mat.set_shader_parameter("top", top)
	mat.set_shader_parameter("full_units", Vector2(w - 1, h - 1) * COAST_RES)
	mat.set_shader_parameter("lo", LO)
	mat.set_shader_parameter("hi", HI)
	mat.set_shader_parameter("noise_tex", noise)
	rect.material = mat
	root.add_child(rect)


## Distance (in points) from every point to the nearest point whose mask is target (two-pass chamfer).
func _chamfer(mask: PackedByteArray, w: int, h: int, target: int) -> PackedFloat32Array:
	var d := PackedFloat32Array()
	d.resize(w * h)
	for i in w * h:
		d[i] = 0.0 if mask[i] == target else 1e6
	var D: float = 1.4142
	for y in h:
		for x in w:
			var i: int = y * w + x
			var v: float = d[i]
			if x > 0:
				v = minf(v, d[i - 1] + 1.0)
			if y > 0:
				v = minf(v, d[i - w] + 1.0)
				if x > 0:
					v = minf(v, d[i - w - 1] + D)
				if x < w - 1:
					v = minf(v, d[i - w + 1] + D)
			d[i] = v
	for y in range(h - 1, -1, -1):
		for x in range(w - 1, -1, -1):
			var i: int = y * w + x
			var v: float = d[i]
			if x < w - 1:
				v = minf(v, d[i + 1] + 1.0)
			if y < h - 1:
				v = minf(v, d[i + w] + 1.0)
				if x < w - 1:
					v = minf(v, d[i + w + 1] + D)
				if x > 0:
					v = minf(v, d[i + w - 1] + D)
			d[i] = v
	return d


## A 5x5 box blur (separable), so the shore rounds off the hexes' corners.
func _blur(a: PackedFloat32Array, w: int, h: int) -> PackedFloat32Array:
	var b := PackedFloat32Array()
	b.resize(w * h)
	for y in h:
		for x in w:
			var s: float = 0.0
			for k in range(-2, 3):
				s += a[y * w + clampi(x + k, 0, w - 1)]
			b[y * w + x] = s / 5.0
	var c := PackedFloat32Array()
	c.resize(w * h)
	for y in h:
		for x in w:
			var s2: float = 0.0
			for k in range(-2, 3):
				s2 += b[clampi(y + k, 0, h - 1) * w + x]
			c[y * w + x] = s2 / 5.0
	return c
'''
f.save()

b = F(P + '/scripts/ui/board_view.gd')
b.rep('''const HM := 2.0                  # board margin''', '''const HM := 2.0                  # board margin
const COAST_MG := 30.0           # the baked ground's coast and sea past the grid on every side (2026-11-23)''')
b.rep('''    resized.connect(queue_redraw)
    _baker = load("res://scripts/ui/terrain_bake.gd").new()''', '''    resized.connect(queue_redraw)
    # the open sea behind the map (2026-11-23: no more dark void round the board)
    _ocean = ColorRect.new()
    _ocean.set_anchors_preset(Control.PRESET_FULL_RECT)
    _ocean.mouse_filter = Control.MOUSE_FILTER_IGNORE
    _ocean.show_behind_parent = true
    var om := ShaderMaterial.new()
    om.shader = load("res://scripts/ui/ocean.gdshader")
    om.set_shader_parameter("noise_tex", tex("edge_noise"))
    _ocean.material = om
    add_child(_ocean)
    _baker = load("res://scripts/ui/terrain_bake.gd").new()''')
b.rep('''        if _bake_tex != null and sig == _bake_for:
            draw_texture_rect(_bake_tex, Rect2(_offset(), Vector2(_grid_h(), _grid_w()) * u), false)''', '''        if _bake_tex != null and sig == _bake_for:
            var mg := Vector2(COAST_MG, COAST_MG)
            draw_texture_rect(_bake_tex, Rect2(_offset() - mg * u, (Vector2(_grid_h(), _grid_w()) + mg * 2.0) * u), false)''')
b.rep('''var _baker = null''', '''var _baker = null
var _ocean: ColorRect = null''')
b.rep('''        elif whole != "":
            draw_colored_polygon(pts, Color("2f7d22"))
            _draw_rect_tex(tex(whole), tile_rect)''', '''        elif whole == "hex_castle_neutral" and soft_ok and tex("hex_castle_neutral_soft") != null:
            _draw_rect_tex(tex("hex_castle_neutral_soft"), tile_rect)   # its edge fades into the ground (2026-11-23)
        elif whole != "":
            draw_colored_polygon(pts, Color("2f7d22"))
            _draw_rect_tex(tex(whole), tile_rect)''')
b.rep('''    for k in ["grass_0", "grass_1", "grass_2", "mountain", "forest", "fern", "water"]:
        names["hex_%s_soft" % k]''', '''    for k in ["grass_0", "grass_1", "grass_2", "mountain", "forest", "fern", "water", "castle_neutral"]:
        names["hex_%s_soft" % k]''')
b.rep('''    treb_feet = {}
    var u: float = _scale()''', '''    treb_feet = {}
    var u: float = _scale()
    if _ocean != null and _ocean.material != null:
        _ocean.material.set_shader_parameter("rect_px", size)
        _ocean.material.set_shader_parameter("off", _offset())
        _ocean.material.set_shader_parameter("u", u)''')
b.save()
print('ok')

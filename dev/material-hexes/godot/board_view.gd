extends Control
## Draws the hex board and reports which hex was clicked. Sizes, positions and colours follow the
## browser version's renderMap: grass hexes, territory edges along the borders of each side's land,
## forest groves and fern patches whose tops spill over the hex above, castles, building "villages",
## the home crown, troop-count badges and the dashed rings that show where you can go.

signal hex_clicked(i: int)

const HR := 18.0                 # hex radius in board units (centre to corner)
const HM := 2.0                  # board margin
var N: int:
	get: return HexGrid.SIZE   # 8, or 11 on the 3-player board
const OUTLINE := Color("060907")
const BONE := Color("ece4cf")
const GOLD := Color("efc15a")
const RED := Color("ff6b5e")

# Building spots inside a hex (board units from the centre), as in the browser version.
const HEX_SLOTS := [Vector2(-7.4, 0.0), Vector2(-5.3, -8.5), Vector2(-5.3, 8.5), Vector2(0.0, 11.6)]
const CASTLE_SLOTS := [Vector2(-10.3, 7.4), Vector2(10.3, 7.4), Vector2(-12.4, 0.6), Vector2(12.4, 0.6)]
const BLD_SIZE := 9.6
const BLD_GROW := {"barracks_dinos": 1.5, "market_dinos": 1.18}   # the Dinosaurs' nesting ground is flat, so it's drawn bigger (standing on the same spot)
const MW := 26.0                 # mountain picture width
const HFIT := 16.4

var game = null                  # the GameState being shown
var selected: int = -1
var targets: Array = []          # hexes ringed as places you can go or act on
var red_targets: bool = false    # true while aiming a trebuchet
var shooter: int = -1
var flash: Array = []            # hexes the computer just changed
var flash_color: Color = GOLD
var wall_for: int = -1           # a hex whose wall sides are being chosen
var dim_except: int = -1         # darken the board except this hex
var blink: bool = true
var lava_fx: Array = []          # volcano eruptions playing: {from, to, bombs, t0}
var anim_hex: int = -1           # the hex whose flat trebuchet picture is hidden while its 3D model fires
var treb_feet: Dictionary = {}   # hex -> where its finished trebuchet picture stands (screen), for the 3D model
var treb_anim = null             # the trebuchet firing animation (treb_anim.gd)

var _tex: Dictionary = {}
var _hh: float = HR * sqrt(3.0)
var _t: float = 0.0


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP
	treb_anim = load("res://scripts/ui/treb_anim.gd").new()
	treb_anim.board = self
	add_child(treb_anim)
	texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
	var names: Dictionary = {
		"grass": "res://art/terrain/board_grass.jpeg",
		"water": "res://art/terrain/water_img.png",
		"mountain": "res://art/terrain/mountain_img.png",
		"castle_dinos": "res://art/terrain/castle_dinos.png",
		"castle_robots": "res://art/terrain/castle_robots.png",
		"castle_mammals": "res://art/terrain/castle_mammals.png",
		"castle_mythical": "res://art/terrain/castle_mythical.png",
		"tree": "res://art/buildings/tree.png",
		"wh": "res://art/buildings/wh.png",
		"castle_neutral": "res://art/terrain/castle_neutral.png",
		"coin": "res://art/ui/coin.png",
		"mat": "res://art/ui/mat.png",
		"crown": "res://art/ui/crown.png",
		"fortify": "res://art/ui/fortify.png",
		"treb": "res://art/buildings/treb.png",
		"treb_dinos": "res://art/buildings/treb_dinos.png",
		"treb_robots": "res://art/buildings/treb_robots.png",
	}
	for b in ["market", "fort", "barracks"]:
		for f in ["dinos", "robots", "mammals"]:
			names[b + "_" + f] = "res://art/buildings/%s_%s.png" % [b, f]
	for f in ["dinos", "robots", "mammals", "mythical", "neutral"]:
		names["gnd_" + f] = "res://art/terrain/gnd_%s.png" % f   # castle hex grounds (the ones that exist)
	for v in 3:
		names["hex_grass_%d" % v] = "res://art/terrain/hex_grass_%d.png" % v   # each hex's own grass tile (Ethan, 2026-11-16)
	names["hex_forest_top"] = "res://art/terrain/hex_forest_top.png"   # the forest's treetops that rise above its hex (2026-11-17)
	names["hex_mountain"] = "res://art/terrain/hex_mountain.png"   # the mountain hex: the whole hex is mountain
	for k in ["castle_neutral", "forest", "fern"]:
		names["hex_" + k] = "res://art/terrain/hex_%s.png" % k   # whole-hex tiles: neutral castles, forests, ferns (2026-11-16)
	for k in ["grass_0", "grass_1", "grass_2", "mountain", "forest", "fern", "water"]:
		names["hex_%s_soft" % k] = "res://art/terrain/hex_%s_soft.png" % k   # soft-edged versions that blend into neighbours (2026-11-17)
	for v in 6:
		names["forest_%d" % v] = "res://art/vegetation/forest_%d.png" % v
		names["fern_%d" % v] = "res://art/vegetation/fern_%d.png" % v
	for key in names:
		if ResourceLoader.exists(names[key]):
			_tex[key] = load(names[key])
	resized.connect(queue_redraw)


func _process(delta: float) -> void:
	if not lava_fx.is_empty():
		queue_redraw()
	# the dashed rings blink, like the browser version's
	if targets.is_empty() and flash.is_empty() and shooter < 0:
		return
	_t += delta
	var on: bool = fmod(_t, 1.1) < 0.55
	if on != blink:
		blink = on
		queue_redraw()


func tex(key: String) -> Texture2D:
	return _tex.get(key, null)


# ---------------------------------------------------------------------
# Geometry

func _grid_w() -> float:
	return 2.0 * HM + HR * (1.5 * (N - 1) + 2.0)


func _grid_h() -> float:
	return 2.0 * HM + _hh * (N + 0.5)


## The part of the board that is drawn, in board units: the whole grid on the 2-player board; on the 3-player hexagon
## just its hexes (its grid corners are empty).
var _frame_n: int = -1
var _frame: Rect2
func _frame_rect() -> Rect2:
	if _frame_n == N:
		return _frame
	_frame_n = N
	if N == 8:
		_frame = Rect2(0, 0, _grid_h(), _grid_w())
		return _frame
	var lo := Vector2(INF, INF)
	var hi := Vector2(-INF, -INF)
	for i in N * N:
		if HexGrid.is_void(i):
			continue
		var p := _grid_pos(i)
		lo = lo.min(p - Vector2(_hh / 2.0, HR))
		hi = hi.max(p + Vector2(_hh / 2.0, HR))
	_frame = Rect2(lo - Vector2(HM, HM), hi - lo + Vector2(2 * HM, 2 * HM))
	return _frame


## Hex i's centre in board units (the board is drawn turned a quarter, as in the browser).
func _grid_pos(i: int) -> Vector2:
	var r: int = i / N
	var c: int = i % N
	var gx: float = HM + HR + c * 1.5 * HR
	var gy: float = HM + _hh / 2.0 + r * _hh + (c & 1) * _hh / 2.0
	return Vector2(_grid_h() - gy, _grid_w() - gx)


func _scale() -> float:
	var f := _frame_rect()
	return minf(size.x / f.size.x, size.y / f.size.y)


func _offset() -> Vector2:
	var f := _frame_rect()
	return (size - f.size * _scale()) / 2.0 - f.position * _scale()


## Where hex i's centre is on screen.
func center(i: int) -> Vector2:
	return _offset() + _grid_pos(i) * _scale()


func radius() -> float:
	return HR * _scale()


## Corner k of a hex; edge k runs from corner k to corner k + 1 and faces neighbour slot k.
func _corner(c: Vector2, rad: float, k: int) -> Vector2:
	var a: float = PI / 3.0 * k
	return c + Vector2(-rad * sin(a), -rad * cos(a))


func _hex_points(c: Vector2, rad: float) -> PackedVector2Array:
	var pts := PackedVector2Array()
	for k in 6:
		pts.append(_corner(c, rad, k))
	return pts


func _closed(pts: PackedVector2Array) -> PackedVector2Array:
	var out := pts.duplicate()
	out.append(pts[0])
	return out


func hex_at(pos: Vector2) -> int:
	var best: int = -1
	var best_d: float = radius() * 0.95
	for i in N * N:
		if game != null and game.tiles[i].terrain == "void":
			continue
		var d: float = pos.distance_to(center(i))
		if d < best_d:
			best_d = d
			best = i
	return best


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		var i: int = hex_at(event.position)
		if i >= 0:
			hex_clicked.emit(i)
			accept_event()


# ---------------------------------------------------------------------
# Drawing (all sizes in board units, times u)

func _player_color(pid: int) -> Color:
	if game == null or pid < 0:
		return Color(0.8, 0.8, 0.8)
	return Color(String(game.players[pid].get("color", GameData.factions[game.players[pid].faction].color)))


func _draw() -> void:
	if game == null:
		return
	treb_feet = {}
	var u: float = _scale()
	var font: Font = get_theme_default_font()
	var grass: Texture2D = tex("grass")
	var live: Array = []
	for t in game.tiles:
		if t.terrain != "void":
			live.append(t)

	# 0. soft ground (Ethan, 2026-11-17: "flow together better"): every hex's grass, then the mountain, forest and fern tiles,
	# each fading out at its edge and drawn 10% bigger than the hex, so neighbours overlap and blend (like the browser)
	var soft_ok: bool = tex("hex_grass_0_soft") != null
	if soft_ok:
		var sk: float = (HR + 0.3) * 1.10
		for t in live:
			var c0: Vector2 = center(int(t.id))
			draw_colored_polygon(_hex_points(c0, (HR + 0.3) * u), Color("2f7d22"))
		for pass_n in 2:
			for t in live:
				var i0: int = int(t.id)
				var c0: Vector2 = center(i0)
				var rr := Rect2(c0 - Vector2(sk * sqrt(3.0) / 2.0, sk) * u, Vector2(sk * sqrt(3.0), 2.0 * sk) * u)
				if pass_n == 0:
					_draw_rect_tex(tex("hex_grass_%d_soft" % ((((i0 + 5) * 2654435761 & 0xFFFFFFFF) >> 7) % 3)), rr)
				else:
					var w0: String = _whole_tile(t)
					if t.terrain == "water":
						w0 = "hex_water"   # the beach lake (2026-11-17)
					if w0 in ["hex_mountain", "hex_forest", "hex_fern", "hex_water"] and tex(w0 + "_soft") != null:
						_draw_rect_tex(tex(w0 + "_soft"), rr)

	# 1. ground: grass, water, mountains, owner tint and territory edges
	for t in live:
		var i: int = int(t.id)
		var c: Vector2 = center(i)
		var pts: PackedVector2Array = _hex_points(c, (HR + 0.3) * u)
		var gr0: float = HR + 0.3
		var tile_rect := Rect2(c - Vector2(gr0 * sqrt(3.0) / 2.0, gr0) * u, Vector2(gr0 * sqrt(3.0), 2.0 * gr0) * u)
		# every hex sits on its own grass tile (one of three, by hex number, like the browser), and a mountain hex is all mountain
		var hex_grass: Texture2D = tex("hex_grass_%d" % ((((i + 5) * 2654435761 & 0xFFFFFFFF) >> 7) % 3))
		var whole: String = _whole_tile(t)
		if soft_ok and (whole == "" or whole in ["hex_mountain", "hex_forest", "hex_fern"]):
			pass   # already drawn soft above
		elif whole != "":
			draw_colored_polygon(pts, Color("2f7d22"))
			_draw_rect_tex(tex(whole), tile_rect)
		elif hex_grass != null:
			draw_colored_polygon(pts, Color("2f7d22"))
			_draw_rect_tex(hex_grass, tile_rect)
		elif grass != null:
			var uvs := PackedVector2Array()
			for p in pts:
				uvs.append((p - _offset()) / (u * 64.0))
			draw_polygon(pts, PackedColorArray([Color.WHITE]), uvs, grass)
		else:
			draw_colored_polygon(pts, Color("2a5529"))
		if t.terrain == "water" and not (soft_ok and tex("hex_water_soft") != null):
			_draw_rect_tex(tex("water"), Rect2(c - Vector2(_hh / 2.0, HR) * u, Vector2(_hh, 2.0 * HR) * u))
		elif t.terrain == "mountain" and tex("hex_mountain") == null:
			var mh: float = MW * 0.8127
			_draw_rect_tex(tex("mountain"), Rect2(c + Vector2(-MW / 2.0, 10.0 - mh) * u, Vector2(MW, mh) * u))
		# a castle's hex is drawn with that castle's own ground (the Mythical's: a black drop into nothing)
		var gnd: String = _castle_gnd(t)
		if gnd != "":
			var gr: float = HR + 0.3
			_draw_rect_tex(tex(gnd), Rect2(c - Vector2(gr * sqrt(3.0) / 2.0, gr) * u, Vector2(gr * sqrt(3.0), 2.0 * gr) * u))
		var owner: int = int(t.owner)
		if owner >= 0 and gnd == "" and whole != "hex_castle_neutral":   # no colour wash over a castle's own ground; the team border still shows the owner
			var col: Color = _player_color(owner)
			var tint: Color = col
			tint.a = 0.2
			draw_colored_polygon(_hex_points(c, HR * u), tint)
		# no seam between hexes (Ethan, 2026-11-17: "get rid of the hex borders and instead have them show up on the borders
		# of players' territory"): the only lines are the territory borders below

	for t in live:
		var owner2: int = int(t.owner)
		if owner2 < 0:
			continue
		var i2: int = int(t.id)
		var c2: Vector2 = center(i2)
		var col2: Color = _player_color(owner2)
		var dirs: Array[int] = HexGrid.neighbor_dirs(i2)
		# the border (Ethan, 2026-11-17: thinner, and wrapping cleanly round the territory's corners, like the browser):
		# (thinner again later that day: a 1.0-wide band) a 1.3-wide band just inside every edge that borders other land, the corners filled in so the band turns without
		# notches, and a thin dark line on the edge itself
		var bd: Array[bool] = []
		for k in 6:
			var j: int = dirs[k]
			bd.append(not (j >= 0 and int(game.tiles[j].owner) == owner2))
		var outer: Color = OUTLINE
		outer.a = 0.75
		for k in 6:
			var v: Vector2 = _corner(c2, HR * u, k)
			if bd[k]:
				draw_colored_polygon(PackedVector2Array([v, _corner(c2, HR * u, k + 1), _corner(c2, (HR - 1.0) * u, k + 1), _corner(c2, (HR - 1.0) * u, k)]), col2)
			if bd[k] or bd[(k + 5) % 6]:
				var da: Vector2 = (_corner(c2, HR * u, k + 1) - v).normalized() * 0.87 * u
				var db: Vector2 = (_corner(c2, HR * u, k + 5) - v).normalized() * 0.87 * u
				draw_colored_polygon(PackedVector2Array([v, v + da, _corner(c2, (HR - 1.0) * u, k), v + db]), col2)
		for k in 6:
			if bd[k]:
				draw_line(_corner(c2, HR * u, k), _corner(c2, HR * u, k + 1), outer, maxf(0.7, 0.4 * u))
				draw_circle(_corner(c2, HR * u, k), maxf(0.35, 0.2 * u), outer)

	# 2. vegetation, top rows first so lower groves overlap the ones behind them
	if soft_ok and tex("hex_forest_top") != null:
		var sk2: float = (HR + 0.3) * 1.10
		var tops: Array = live.filter(func(t): return t.forest)
		tops.sort_custom(func(a, b): return center(int(a.id)).y < center(int(b.id)).y)
		for t in tops:
			var c4: Vector2 = center(int(t.id))
			var tw: float = sk2 * sqrt(3.0)
			var th: float = 2.0 * sk2
			_draw_rect_tex(tex("hex_forest_top"), Rect2(c4 - Vector2(tw / 2.0, sk2 + th * 0.30) * u, Vector2(tw, th * 1.30) * u))
	var veg: Array = live.filter(func(t): return (t.forest or t.fern) and _whole_tile(t) == "")   # (none while the forest and fern tiles exist)
	veg.sort_custom(func(a, b): return center(int(a.id)).y < center(int(b.id)).y)
	for t in veg:
		var i3: int = int(t.id)
		var key: String = ("forest_%d" if t.forest else "fern_%d") % (i3 % 6)
		var c3: Vector2 = center(i3)
		_draw_rect_tex(tex(key), Rect2(c3 - Vector2(21.0, 24.0) * u, Vector2(42.0, 44.0) * u))

	# 3. walls, and magic domes (a dome guards every side)
	for t in live:
		if int(t.get("dome", 0)) > 0:
			_draw_dome(center(int(t.id)), int(t.dome), u)
		for k in 6:
			var hp: int = int(t.walls[k])
			if hp > 0:
				_draw_wall(int(t.id), k, hp, false)
	if wall_for >= 0:
		var dirs2: Array[int] = HexGrid.neighbor_dirs(wall_for)
		for k in 6:
			var j2: int = dirs2[k]
			if j2 >= 0 and game.wall_sides(wall_for).has(j2) and game.wall_on(wall_for, j2) < int(GameData.rules.walls.hp) and int(game.tiles[j2].owner) != 0:
				_draw_wall(wall_for, k, 3, true)

	# 4. castles, buildings, icons, coins and troop badges
	for t in live:
		_draw_hex_things(font, t, u)

	# 5. darken everything but one hex (while choosing what to build or train there)
	if dim_except >= 0:
		var shade: Color = OUTLINE
		shade.a = 0.42
		for t in live:
			if int(t.id) != dim_except:
				draw_colored_polygon(_hex_points(center(int(t.id)), (HR + 0.3) * u), shade)

	# 6. rings: where you can go, the selected hex, the trebuchet's targets, what the computer just did
	for i4 in targets:
		if blink:
			_dashed_hex(center(int(i4)), (HR - 3.0) * u, RED if red_targets else BONE, (2.0 if red_targets else 1.8) * u)
	if selected >= 0:
		draw_polyline(_closed(_hex_points(center(selected), (HR - 1.4) * u)), OUTLINE, 3.6 * u)
		draw_polyline(_closed(_hex_points(center(selected), (HR - 1.4) * u)), BONE, 2.0 * u)
	if shooter >= 0 and blink:
		draw_polyline(_closed(_hex_points(center(shooter), (HR - 1.4) * u)), GOLD, 2.6 * u)
	if blink:
		for i5 in flash:
			draw_polyline(_closed(_hex_points(center(int(i5)), (HR - 1.4) * u)), flash_color, 2.6 * u)

	# 7. lava bombs from a Dinosaur volcano (just for show: the shot is already worked out)
	if not lava_fx.is_empty():
		_draw_lava(u)


## A tile that fills the whole hex, in place of the grass and anything placed on it (browser: the mountain, the neutral
## castle, forest and fern hexes; Ethan, 2026-11-16). "" when the hex is grass (or the tile is missing).
func _whole_tile(t: Dictionary) -> String:
	var key: String = ""
	if t.terrain == "mountain":
		key = "hex_mountain"
	elif t.castle and not (game.homes.has(int(t.id)) and int(t.owner) >= 0):
		key = "hex_castle_neutral"
	elif t.forest:
		key = "hex_forest"
	elif t.fern:
		key = "hex_fern"
	return key if tex(key) != null else ""


## The ground tile for a castle's hex (browser castleGnd): it follows the castle picture drawn there, so a home castle
## shows its owner's faction ground and any other castle the neutral one (none yet: neutral castles keep the grass).
func _castle_gnd(t: Dictionary) -> String:
	if not t.castle:
		return ""
	var owner: int = int(t.owner)
	var key: String = "gnd_neutral"
	if game.homes.has(int(t.id)) and owner >= 0:
		key = "gnd_" + String(game.players[owner].faction)
	return key if _tex.has(key) else ""


func _draw_hex_things(font: Font, t: Dictionary, u: float) -> void:
	var i: int = int(t.id)
	var c: Vector2 = center(i)
	var owner: int = int(t.owner)
	var fac: String = game.players[owner].faction if owner >= 0 else ""
	if t.castle:
		var art: String = "castle_neutral"
		if game.homes.has(i) and owner >= 0:
			art = "castle_" + fac
		var ct: Texture2D = tex(art)
		if art == "castle_neutral" and _whole_tile(t) == "hex_castle_neutral":
			ct = null   # the neutral castle tile already fills the hex
		if ct != null:
			var ratio: float = ct.get_size().y / ct.get_size().x
			var w: float = 26.0 if art == "castle_mythical" else minf(_hh - 3.5, 2.0 * HFIT / (ratio + 1.0 / sqrt(3.0)))   # the Floating Castle is drawn big, filling its hex (Ethan, 2026-11-10)
			var h: float = w * ratio
			_draw_rect_tex(ct, Rect2(c - Vector2(w, h) * u / 2.0, Vector2(w, h) * u))
	# buildings: a little village down the hex's left side (on a castle, around its feet)
	var blds: Array = []
	for k in ["fort", "barracks", "market", "wh"]:
		for q in int(t.get(k, 0)):
			blds.append(k)
	var robo: bool = owner >= 0 and fac == "robots" and not t.castle and int(t.market) > 0
	if robo:
		blds = []   # the Robots: one factory picture, or the resource hex's markets (below)
	var village: bool = (not blds.is_empty() or robo) and not t.castle
	if robo and int(t.market) >= 2 and int(t.barracks) == 0:
		var nm: int = mini(int(t.market), 4)
		var zm: float = 11.5 if nm > 2 else 13.0
		var spots: Array = [[], [], [Vector2(-6.4, 1.0), Vector2(6.4, 1.0)], [Vector2(0.0, -5.6), Vector2(-6.6, 5.0), Vector2(6.6, 5.0)], [Vector2(-6.0, -5.0), Vector2(6.0, -5.0), Vector2(-6.0, 6.0), Vector2(6.0, 6.0)]]
		for o in spots[nm]:
			_draw_rect_tex(tex("market_robots"), Rect2(c + (o - Vector2(zm, zm) / 2.0) * u, Vector2(zm, zm) * u))
	elif robo:
		var lv: int = game.robo_lv(t)
		var zs: Array = [0.0, 17.0, 19.0, 21.0]
		var keys: Array = ["", "market_robots", "barracks_robots", "fort_robots"]
		var z0: float = float(zs[lv])
		var p0 := Vector2(-z0 / 2.0, -z0 / 2.0 + 1.2)
		_draw_rect_tex(tex(String(keys[lv])), Rect2(c + p0 * u, Vector2(z0, z0) * u))
		for q in int(t.bk):   # the barracks level
			var rp := Rect2(c + (p0 + Vector2(z0 - 0.6, z0 * 0.45 + q * 2.2)) * u, Vector2(1.7, 1.7) * u)
			draw_rect(rp, GOLD)
			draw_rect(rp, OUTLINE, false, maxf(1.0, 0.35 * u))
	if not blds.is_empty() and owner >= 0:
		var slots: Array = CASTLE_SLOTS if t.castle else HEX_SLOTS
		var sz: float = 6.8 if t.castle else BLD_SIZE
		var placed: Array = []
		for n in mini(blds.size(), slots.size()):
			placed.append([blds[n], slots[n]])
		placed.sort_custom(func(a, b): return a[1].y < b[1].y)
		var pips: bool = int(t.bk) > 0
		for pair in placed:
			var pos: Vector2 = c + (pair[1] - Vector2(sz, sz) / 2.0) * u
			var bk: String = "wh" if pair[0] == "wh" else pair[0] + "_" + fac
			var z: float = sz * float(BLD_GROW.get(bk, 1.0))
			_draw_rect_tex(tex(bk), Rect2(c + (pair[1] + Vector2(-z / 2.0, sz / 2.0 - z)) * u, Vector2(z, z) * u))
			if pair[0] == "barracks" and pips:
				pips = false
				for q in int(t.bk):
					var r := Rect2(pos + Vector2(sz + 0.2, 1.0 + q * 2.2) * u, Vector2(1.7, 1.7) * u)
					draw_rect(r, GOLD)
					draw_rect(r, OUTLINE, false, maxf(1.0, 0.35 * u))
	# little icons: trebuchets (no crown on home castles since 2026-11-10)
	var ics: Array = []
	for key in ["treb", "treb2"]:
		if int(t[key]) > 0:
			var tk: String = "treb_" + fac if (fac == "dinos" or fac == "robots") else "treb"
			ics.append([tk, 1.0 if int(t[key]) == 2 else 0.4, int(t[key]) == 2])
	if game.braced(t) and int(t.troops) > 0:
		ics.append(["fortify", 1.0])
	for n in ics.size():
		var isz: float = 7.0 if village else 8.0
		var x: float = (2.8 if village else -ics.size() * 4.0 + n * 8.0)
		var y: float = ((-12.2 if n == 0 else 5.6) if village else -11.5)
		var big: bool = String(ics[n][0]).begins_with("treb_")
		var sz2: float = (10.5 if village else 11.0) if big else isz
		var tx: float = x + isz / 2.0 - sz2 / 2.0
		var ty: float = y + isz - sz2
		if ics[n].size() > 2 and ics[n][2]:   # a finished trebuchet: its 3D model stands on this spot when it fires
			if not treb_feet.has(i):
				treb_feet[i] = c + Vector2(tx + sz2 / 2.0, ty + sz2) * u
			if i == anim_hex:
				continue
		_draw_rect_tex(tex(ics[n][0]), Rect2(c + Vector2(tx, ty) * u, Vector2(sz2, sz2) * u), Color(1, 1, 1, ics[n][1]))
	if int(t.get("tree", 0)) > 0 and owner >= 0:   # a Life Tree: big, centred on its hex
		var z: float = 25.0
		_draw_rect_tex(tex("tree"), Rect2(c - Vector2(z, z) * u / 2.0, Vector2(z, z) * u))
	if t.bounty:
		_draw_rect_tex(tex("coin"), Rect2(c + Vector2(-4.0, 5.5) * u, Vector2(8.0, 8.0) * u))
	if t.get("crate", false):   # a material hex
		_draw_rect_tex(tex("mat"), Rect2(c + Vector2(-4.0, 5.5) * u, Vector2(8.0, 8.0) * u))
	if int(t.troops) > 0 and owner >= 0:
		var label: String = str(int(t.troops))
		var hh: float = 8.0
		var w2: float = maxf(hh, 3.6 + label.length() * 4.3)
		var bx: float = 6.2 if village else 0.0
		var by: float = 10.0 if t.castle else 1.0
		var tired: bool = game.cur_action() == "move" and owner == game.current and int(t.fresh) == 0
		var alpha: float = 0.5 if tired else 1.0
		var r2 := Rect2(c + Vector2(bx - w2 / 2.0, by - hh / 2.0) * u, Vector2(w2, hh) * u)
		var fill: Color = _player_color(owner)
		fill.a = alpha
		draw_rect(r2.grow(0.5 * u), Color(OUTLINE, alpha))
		draw_rect(r2, fill)
		draw_rect(Rect2(r2.position + Vector2(0.8, 0.8) * u, Vector2(w2 - 1.6, 1.0) * u), Color(1, 1, 1, 0.35 * alpha))
		var fs: int = maxi(8, int(7.6 * u))
		var tw: float = font.get_string_size(label, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		var tpos: Vector2 = c + Vector2(bx, by + 2.75) * u - Vector2(tw / 2.0, 0)
		draw_string(font, tpos, label, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(1, 1, 1, alpha))


## A volcano eruption: the crater flares, then one glowing rock per die arcs onto the target (hits land close together,
## misses scatter) and splashes. As the browser's lava-bomb animation.
func lava(from: int, to: int, dice: Array) -> void:
	var bombs: Array = []
	for k in dice.size():
		var hit: bool = int(dice[k]) >= int(GameData.rules.trebuchet.hit_on)
		var spread: float = 7.0 if hit else 16.0
		bombs.append({"hit": hit, "delay": k * 0.11, "off": Vector2(randf_range(-0.5, 0.5) * spread, randf_range(-0.5, 0.5) * spread * 0.75)})
	lava_fx.append({"from": from, "to": to, "bombs": bombs, "t0": Time.get_ticks_msec() / 1000.0})
	queue_redraw()


func _draw_lava(u: float) -> void:
	var now: float = Time.get_ticks_msec() / 1000.0
	var dur: float = 0.9
	var keep: Array = []
	for fx in lava_fx:
		var el: float = now - float(fx.t0)
		var fpos: Vector2 = center(int(fx.from)) + Vector2(0.0, -HR * 0.55) * u
		var tc: Vector2 = center(int(fx.to))
		var hgt: float = maxf(28.0 * u, fpos.distance_to(tc) * 0.45)
		if el < 0.3:
			var fl: float = el / 0.3
			draw_circle(fpos, (2.0 + fl * 5.0) * u, Color(1.0, 0.69, 0.18, 0.8 * (1.0 - fl)))
		for bm in fx.bombs:
			var t: float = (el - float(bm.delay)) / dur
			if t < 0.0:
				continue
			var tp: Vector2 = tc + Vector2(bm.off) * u
			if t < 1.0:
				var p: Vector2 = fpos.lerp(tp, t) - Vector2(0.0, hgt * 4.0 * t * (1.0 - t))
				draw_circle(p, 3.3 * u, OUTLINE)
				draw_circle(p, 2.7 * u, Color("e8541a"))
				draw_circle(p, 1.2 * u, Color("ffd54a"))
			else:
				var s: float = (t - 1.0) * dur / 0.38
				if s < 1.0:
					var col: Color = Color("ff7a1a") if bool(bm.hit) else Color("7a6a5a")
					col.a = 1.0 - s
					draw_circle(tp, (1.5 + s * (6.0 if bool(bm.hit) else 3.5)) * u, col)
		if el < dur + fx.bombs.size() * 0.11 + 0.45:
			keep.append(fx)
	lava_fx = keep


func _draw_wall(i: int, k: int, hp: int, preview: bool) -> void:
	var u: float = _scale()
	var c: Vector2 = center(i)
	var a: Vector2 = _corner(c, (HR - 1.2) * u, k)
	var b: Vector2 = _corner(c, (HR - 1.2) * u, k + 1)
	var width: float = (1.6 + hp * 0.8) * u
	if preview:
		_dashed_line(a, b, GOLD if blink else Color(GOLD, 0.4), 2.2 * u)
		return
	draw_line(a, b, OUTLINE, width + 1.4 * u)
	draw_line(a, b, Color("b8b2a2"), width)
	# crenellations
	var n: int = 4
	for q in n:
		var p: Vector2 = a.lerp(b, (q + 0.5) / n)
		var d: Vector2 = (b - a).normalized() * 1.2 * u
		draw_line(p - d, p + d, Color("8c8676"), width * 0.45)


## A Mythical magic dome over a hex: a pale violet bubble, brighter the stronger it is.
func _draw_dome(c: Vector2, hp: int, u: float) -> void:
	var r: float = (HR - 2.4) * u
	draw_circle(c, r, Color(Color("b48cff"), 0.08 + 0.05 * hp))
	draw_arc(c, r, 0.0, TAU, 48, Color(Color("e2d0ff"), 0.9), (0.45 + 0.35 * hp) * u, true)
	draw_arc(c + Vector2(-3.0, -6.0) * u, 6.0 * u, deg_to_rad(200), deg_to_rad(285), 12, Color(1, 1, 1, 0.55), 1.0 * u, true)


func _dashed_hex(c: Vector2, rad: float, col: Color, width: float) -> void:
	for k in 6:
		_dashed_line(_corner(c, rad, k), _corner(c, rad, k + 1), col, width)


func _dashed_line(a: Vector2, b: Vector2, col: Color, width: float) -> void:
	var u: float = _scale()
	draw_dashed_line(a, b, col, width, 4.0 * u, false)


func _draw_rect_tex(t: Texture2D, r: Rect2, modulate_col: Color = Color.WHITE) -> void:
	if t != null:
		draw_texture_rect(t, r, false, modulate_col)

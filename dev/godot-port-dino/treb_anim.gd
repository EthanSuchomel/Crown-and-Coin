extends Control
## The trebuchet firing animation, ported from the browser version's (three.js) one. When a finished trebuchet fires,
## its 3D model (steel for the Robots, bone for everyone else) stands where its picture is on the map, swings its arm,
## and lobs the stone onto the hex it hit. Purely for show: the shot itself is already worked out by GameState.fire_treb.
## BoardView owns one of these; main.gd hands it each shot (GameState.treb_fx).

const MODEL_LEN := 18.0         # the model is about 8 units long; draw it this many board units long on the map
const U := 8.0 / MODEL_LEN      # 3D units per board unit
const OL := 0.16                # outline thickness
const OUTLINE := Color("060907")

var board = null                # the BoardView this plays over
var queue: Array = []           # shots waiting: {from, to, pid}
var playing: bool = false
var _wait: float = 0.0
var _vp: SubViewport = null
var _rect: TextureRect = null
var _world: Node3D = null
var _kit: Dictionary = {}
var _steel: bool = false
var _team: Color = Color.WHITE
var _mats: Dictionary = {}
# one shot's state
var _t: float = 0.0
var _released: bool = false
var _flight: float = -1.0
var _landed_at: float = -1.0
var _stop_at: float = -1.0
var _target: Vector3 = Vector3.ZERO
var _vel: Vector3 = Vector3.ZERO
var _dust: Array = []
const G := 34.0
const FLY := 0.62


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_preset(Control.PRESET_FULL_RECT)
	_vp = SubViewport.new()
	_vp.transparent_bg = true
	_vp.own_world_3d = true
	_vp.render_target_update_mode = SubViewport.UPDATE_DISABLED
	_vp.size = Vector2i(64, 64)
	add_child(_vp)
	_rect = TextureRect.new()
	_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_rect.stretch_mode = TextureRect.STRETCH_SCALE
	_rect.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST   # chunky pixels, like the browser version's canvas
	_rect.texture = _vp.get_texture()
	_rect.visible = false
	add_child(_rect)


## Queues a shot from hex i at hex j by player pid.
func shot(i: int, j: int, pid: int) -> void:
	queue.append({"from": i, "to": j, "pid": pid})
	if not playing and _wait <= 0.0:
		_wait = 0.08


func _process(delta: float) -> void:
	if not playing:
		if _wait > 0.0:
			_wait -= delta
			if _wait <= 0.0 and not queue.is_empty():
				_start(queue.pop_front())
		return
	_frame(minf(0.05, delta))


func _start(r: Dictionary) -> void:
	if board == null or board.game == null or board.size.x < 10.0 or int(r.pid) < 0 or int(r.pid) >= board.game.players.size():
		if not queue.is_empty():
			_wait = 0.12
		return
	var game = board.game
	var pid: int = int(r.pid)
	playing = true
	board.anim_hex = int(r.from)   # the flat trebuchet picture is hidden while its model plays
	board.queue_redraw()
	var u: float = board._scale()
	var foot: Vector2 = board.treb_feet.get(int(r.from), board.center(int(r.from)))
	var tc: Vector2 = board.center(int(r.to))
	var R: float = 2.7 * board.HR
	var px: float = 2.0 * R * u
	var half: float = R * U
	_rect.position = foot - Vector2(px, px) / 2.0
	_rect.size = Vector2(px, px)
	# drawn at 3/4 of the screen's pixels, like the browser version
	var ss: float = absf(get_global_transform_with_canvas().get_scale().x)
	var res: int = clampi(int(px * ss * 0.75), 64, 1024)
	_vp.size = Vector2i(res, res)
	_rect.visible = true
	_vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS

	_world = Node3D.new()
	_vp.add_child(_world)
	var cam := Camera3D.new()
	cam.projection = Camera3D.PROJECTION_ORTHOGONAL
	cam.size = 2.0 * half
	cam.near = 0.1
	cam.far = 300.0
	_world.add_child(cam)
	cam.look_at_from_position(Vector3(0.0, 80.0 * sqrt(0.5), 80.0 * sqrt(0.5)), Vector3.ZERO, Vector3.UP)   # the map's 45-degree view
	# light: a pale sky above and a dark green ground below (the browser's hemisphere light), plus a warm sun from the upper left
	var env := Environment.new()
	env.background_mode = Environment.BG_CLEAR_COLOR
	var sky_mat := ProceduralSkyMaterial.new()
	sky_mat.sky_top_color = Color("e2e8d8")
	sky_mat.sky_horizon_color = Color("e2e8d8")
	sky_mat.ground_horizon_color = Color("26331f")
	sky_mat.ground_bottom_color = Color("26331f")
	sky_mat.sun_angle_max = 0.0
	var sky := Sky.new()
	sky.sky_material = sky_mat
	env.sky = sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env.ambient_light_sky_contribution = 1.0
	env.ambient_light_energy = 1.15 / PI
	env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	var we := WorldEnvironment.new()
	we.environment = env
	_world.add_child(we)
	var sun := DirectionalLight3D.new()
	sun.light_color = Color("fff3dc")
	sun.light_energy = 2.1 / PI
	sun.sky_mode = DirectionalLight3D.SKY_MODE_LIGHT_ONLY
	sun.shadow_enabled = true
	sun.directional_shadow_mode = DirectionalLight3D.SHADOW_ORTHOGONAL
	sun.directional_shadow_max_distance = 80.0 + 4.0 * half
	_world.add_child(sun)
	sun.look_at_from_position(Vector3(-8.0, 16.0, 10.0), Vector3.ZERO, Vector3.UP)
	var gnd := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(half * 3.0, half * 3.0)
	gnd.mesh = pm
	var sm := StandardMaterial3D.new()
	sm.shadow_to_opacity = true
	sm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	sm.albedo_color = Color(0, 0, 0, 0.32)
	gnd.material_override = sm
	gnd.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_world.add_child(gnd)

	_steel = String(game.players[pid].faction) == "robots"
	_team = board._player_color(pid)
	_kit = _make_kit()
	# the target on the ground: screen-down is +z, foreshortened by the 45-degree tilt
	var wx: float = (tc.x - foot.x) / u * U
	var wz: float = (tc.y - foot.y) / u * U * sqrt(2.0)
	_kit.root.rotation = Vector3(0.0, atan2(wz, -wx), 0.0)   # the stone flies toward the counterweight side
	_world.add_child(_kit.root)
	_target = Vector3(wx, 0.35, wz)
	_t = 0.0
	_released = false
	_flight = -1.0
	_landed_at = -1.0
	_stop_at = -1.0
	_dust = []


func _frame(dt: float) -> void:
	_t += dt
	var t: float = _t
	# grow from the size of the map picture, then shrink back to it at the end
	var sc: float = (0.6 + 0.4 * _ease_out(t / 0.22)) if t < 0.22 else 1.0
	if _stop_at >= 0.0:
		sc = 1.0 - 0.4 * minf(1.0, (t - _stop_at) / 0.2)
	_kit.root.scale = Vector3.ONE * sc
	var ft: float = t - 0.28
	var theta: float = 0.0
	var rel: float = 0.0
	if ft >= 0.0 and ft < 0.8:
		var q: float = ft / 0.8
		var s: float = q * q * q
		theta = 2.3 * q * q
		rel = -theta * (1.0 - s) + 2.2 * s
	elif ft >= 0.8:
		var st: float = ft - 0.8
		theta = 2.3 + 0.14 * sin(st * 11.0) * exp(-st * 4.0)
		rel = -theta + 4.5 * exp(-st * 3.0) * cos(st * 4.5)
	_kit.arm.rotation = Vector3(0.0, 0.0, theta)
	_kit.cw.rotation = Vector3(0.0, 0.0, -theta)
	_kit.sling.rotation = Vector3(0.0, 0.0, rel)
	_kit.wheel.rotation = Vector3(0.0, 0.0, -theta * 1.5)
	var stone: Node3D = _kit.stone
	if not _released and ft >= 0.0 and theta + rel >= 2.36:
		_released = true
		var gt: Transform3D = stone.global_transform
		stone.get_parent().remove_child(stone)
		_world.add_child(stone)
		stone.global_transform = gt
		_vel = (_target - stone.position) / FLY
		_vel.y += 0.5 * G * FLY
		_flight = 0.0
	if _flight >= 0.0 and _landed_at < 0.0:
		_flight += dt
		_vel.y -= G * dt
		stone.position += _vel * dt
		stone.rotation.x += dt * 7.0
		stone.rotation.z += dt * 5.0
		if _flight >= FLY:
			stone.position = _target
			_landed_at = t
			stone.visible = false
			_burst()
	for d in _dust:
		d.v.y -= 16.0 * dt
		d.m.position += d.v * dt
		if d.m.position.y < 0.1:
			d.m.position.y = 0.1
			d.v *= 0.5
		var a: float = (t - _landed_at) / 0.75
		var col: Color = d.mat.albedo_color
		col.a = maxf(0.0, 1.0 - a)
		d.mat.albedo_color = col
		d.m.scale = Vector3.ONE * (1.0 + a * 0.8)
	if _stop_at < 0.0 and _landed_at >= 0.0 and t - _landed_at > 0.75 and ft > 1.5:
		_stop_at = t
	if (_stop_at >= 0.0 and t - _stop_at >= 0.2) or t > 5.0:
		_finish()


## A puff of dirt and stone chips where it lands.
func _burst() -> void:
	var cols: Array = [Color("b8a37a"), Color("8a7a5a"), Color("6d6a62"), Color("d8cfb4")]
	for n in 14:
		var s: float = 0.3 + randf() * 0.4
		var mat := StandardMaterial3D.new()
		mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		mat.albedo_color = cols[n % 4]
		var bm := BoxMesh.new()
		bm.size = Vector3(s, s, s)
		var m := MeshInstance3D.new()
		m.mesh = bm
		m.material_override = mat
		m.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		m.position = _target
		_world.add_child(m)
		var a: float = randf() * TAU
		var sp: float = 2.5 + randf() * 4.0
		_dust.append({"m": m, "mat": mat, "v": Vector3(cos(a) * sp, 3.0 + randf() * 6.0, sin(a) * sp)})


func _finish() -> void:
	playing = false
	_vp.render_target_update_mode = SubViewport.UPDATE_DISABLED
	_rect.visible = false
	if _world != null:
		_world.queue_free()
		_world = null
	_kit = {}
	_dust = []
	if board != null:
		board.anim_hex = -1
		board.queue_redraw()
	if not queue.is_empty():
		_wait = 0.12


func _ease_out(x: float) -> float:
	return 1.0 - pow(1.0 - clampf(x, 0.0, 1.0), 3.0)


# ---------------------------------------------------------------------
# The two models, built from boxes, beams, cones and cylinders as in the browser version

func _lam(c: Color) -> StandardMaterial3D:
	var key: String = "l" + c.to_html()
	if _mats.has(key):
		return _mats[key]
	var m := StandardMaterial3D.new()
	m.albedo_color = c
	m.roughness = 1.0
	m.metallic_specular = 0.0
	m.diffuse_mode = BaseMaterial3D.DIFFUSE_LAMBERT
	m.specular_mode = BaseMaterial3D.SPECULAR_DISABLED
	_mats[key] = m
	return m


func _flat(c: Color) -> StandardMaterial3D:
	var key: String = "f" + c.to_html()
	if _mats.has(key):
		return _mats[key]
	var m := StandardMaterial3D.new()
	m.albedo_color = c
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_mats[key] = m
	return m


func _out() -> StandardMaterial3D:
	if _mats.has("out"):
		return _mats["out"]
	var m := StandardMaterial3D.new()
	m.albedo_color = OUTLINE
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.cull_mode = BaseMaterial3D.CULL_FRONT   # only the back faces: a dark rim around the part
	_mats["out"] = m
	return m


func _mi(p: Node3D, mesh: Mesh, mat: Material, shadow: bool) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = mat
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON if shadow else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	p.add_child(mi)
	return mi


func _box_mesh(s: Vector3) -> BoxMesh:
	var b := BoxMesh.new()
	b.size = s
	return b


func _cyl(rt: float, rb: float, h: float, seg: int) -> Mesh:
	var c := CylinderMesh.new()
	c.top_radius = rt
	c.bottom_radius = rb
	c.height = h
	c.radial_segments = seg
	c.rings = 0
	return _faceted(c)


## The same mesh with one normal per triangle, so it shades in flat facets like the browser version's low-poly parts.
func _faceted(src: Mesh) -> ArrayMesh:
	var arr: Array = src.surface_get_arrays(0)
	var vs: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
	var ns: PackedVector3Array = arr[Mesh.ARRAY_NORMAL]
	var idx: PackedInt32Array = arr[Mesh.ARRAY_INDEX]
	if idx.is_empty():
		idx.resize(vs.size())
		for k in vs.size():
			idx[k] = k
	var ov := PackedVector3Array()
	var on := PackedVector3Array()
	for k in range(0, idx.size() - 2, 3):
		var a: Vector3 = vs[idx[k]]
		var b: Vector3 = vs[idx[k + 1]]
		var c: Vector3 = vs[idx[k + 2]]
		var n: Vector3 = (b - a).cross(c - a)
		if n.length_squared() < 1e-12:
			continue   # a sliver (the tip of a cone): nothing to draw
		n = n.normalized()
		if n.dot(ns[idx[k]] + ns[idx[k + 1]] + ns[idx[k + 2]]) < 0.0:
			n = -n
		for p in [a, b, c]:
			ov.append(p)
			on.append(n)
	var out: Array = []
	out.resize(Mesh.ARRAY_MAX)
	out[Mesh.ARRAY_VERTEX] = ov
	out[Mesh.ARRAY_NORMAL] = on
	var am := ArrayMesh.new()
	am.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, out)
	return am


## Three.js Euler angles (XYZ order) as a Godot basis.
func _euler(r: Vector3) -> Basis:
	return Basis(Vector3(1, 0, 0), r.x) * Basis(Vector3(0, 1, 0), r.y) * Basis(Vector3(0, 0, 1), r.z)


func _beam(p: Node3D, a: Vector3, b: Vector3, t: float, m: Material, bands: Array = []) -> Node3D:
	var d: Vector3 = b - a
	var length: float = d.length()
	var g := Node3D.new()
	g.position = (a + b) * 0.5
	g.quaternion = Quaternion(Vector3.UP, d.normalized())
	_mi(g, _box_mesh(Vector3(t, length, t)), m, true)
	_mi(g, _box_mesh(Vector3(t + OL, length + OL, t + OL)), _out(), false)
	for f in bands:
		var bs: Vector3 = Vector3(t * 0.32, minf(0.5, length * 0.14), t * 1.06) if _steel else Vector3(t * 1.12, t * 0.5, t * 1.12)
		var bm: MeshInstance3D = _mi(g, _box_mesh(bs), _team_mat(), false)
		bm.position.y = (float(f) - 0.5) * length
	p.add_child(g)
	return g


func _box(p: Node3D, s: Vector3, pos: Vector3, m: Material, rot: Vector3 = Vector3.ZERO, o: float = OL) -> Node3D:
	var g := Node3D.new()
	g.position = pos
	g.basis = _euler(rot)
	_mi(g, _box_mesh(s), m, true)
	if o > 0.0:
		_mi(g, _box_mesh(s + Vector3(o, o, o)), _out(), false)
	p.add_child(g)
	return g


func _spike(p: Node3D, pos: Vector3, dir: Vector3, r: float = 0.13, h: float = 0.45) -> Node3D:
	var g := Node3D.new()
	g.position = pos
	g.quaternion = Quaternion(Vector3.UP, dir.normalized())
	var c: MeshInstance3D = _mi(g, _cyl(0.0, r, h, 5), _kit_m.bone, true)
	c.position.y = h / 2.0
	var oc: MeshInstance3D = _mi(g, _cyl(0.0, r + 0.07, h + 0.14, 5), _out(), false)
	oc.position.y = h / 2.0 - 0.03
	p.add_child(g)
	return g


func _octo(p: Node3D, r: float, depth: float, pos: Vector3, m: Material) -> Node3D:
	var g := Node3D.new()
	g.position = pos
	var c: MeshInstance3D = _mi(g, _cyl(r, r, depth, 8), m, true)
	c.basis = _euler(Vector3(PI / 2.0, PI / 8.0, 0.0))
	var oc: MeshInstance3D = _mi(g, _cyl(r + 0.08, r + 0.08, depth + 0.12, 8), _out(), false)
	oc.basis = c.basis
	p.add_child(g)
	return g


func _glow(p: Node3D, s: Vector3, pos: Vector3, rot: Vector3 = Vector3.ZERO) -> void:
	var m: MeshInstance3D = _mi(p, _box_mesh(s), _team_mat(), false)
	m.position = pos
	m.basis = _euler(rot)


func _team_mat() -> Material:
	return _kit_m.team


var _kit_m: Dictionary = {}

func _make_kit() -> Dictionary:
	_mats = {}
	if _steel:
		_kit_m = {"main": _lam(Color("4b4f60")), "trim": _lam(Color("6b7086")), "dark": _lam(Color("2d303b")), "silver": _lam(Color("b9bdc8")),
			"rope": _lam(Color("26282f")), "stone": _lam(Color("9a9a94")), "rivet": _lam(Color("1c1e25")), "team": _flat(_team.lerp(Color.WHITE, 0.15))}
	else:
		_kit_m = {"main": _lam(Color("e8dcc0")), "trim": _lam(Color("e8dcc0")), "dark": _lam(Color("5e3b20")), "wood": _lam(Color("8a5a32")), "silver": _lam(Color("70757b")),
			"rope": _lam(Color("a77a45")), "stone": _lam(Color("8f8f8a")), "rivet": _lam(Color("3a2412")), "team": _lam(_team)}
		_kit_m["bone"] = _kit_m.main
	var M: Dictionary = _kit_m
	var steel: bool = _steel
	var root := Node3D.new()
	var treb := Node3D.new()
	root.add_child(treb)
	treb.position.x = -0.4
	var AX: float = 4.2
	# base
	for z in [-1.15, 1.15]:
		_beam(treb, Vector3(-3.7, 0.27, z), Vector3(3.7, 0.27, z), 0.44, M.main if steel else M.wood, [0.2, 0.5, 0.8] if steel else [])
		for x in [-3.7, 3.7]:
			_box(treb, Vector3(0.6, 0.45, 0.6), Vector3(x, 0.22, z), M.dark if steel else M.bone)
			if steel:
				_glow(treb, Vector3(0.22, 0.1, 0.66), Vector3(x, 0.24, z))
			else:
				_spike(treb, Vector3(x + signf(x) * 0.2, 0.35, z), Vector3(signf(x), 0.9, 0.0), 0.17, 0.7)
	for x in [-3.1, 0.0, 3.1]:
		_beam(treb, Vector3(x, 0.27, -1.42), Vector3(x, 0.27, 1.42), 0.36, M.dark, [0.5] if steel else [])
	# A-frames
	for z in [-1.05, 1.05]:
		var s: float = signf(z)
		_beam(treb, Vector3(-2.3, 0.47, z), Vector3(0.0, AX, z), 0.4, M.main, [0.25, 0.58])
		_beam(treb, Vector3(2.3, 0.47, z), Vector3(0.0, AX, z), 0.4, M.main, [0.25, 0.58])
		_beam(treb, Vector3(-1.35, 2.05, z), Vector3(1.35, 2.05, z), 0.3, M.trim if steel else M.wood)
		_box(treb, Vector3(0.6, 0.6, 0.54), Vector3(0.0, AX, z), M.trim)
		if steel:
			_box(treb, Vector3(0.3, 0.4, 0.3), Vector3(0.0, AX + 0.5, z), M.main)
			var g := Node3D.new()
			var A := Vector3(-1.9, 0.55, z + s * 0.32)
			var B := Vector3(-0.55, 2.85, z + s * 0.32)
			var d: Vector3 = B - A
			var length: float = d.length()
			g.position = A
			g.quaternion = Quaternion(Vector3.UP, d.normalized())
			var sl: MeshInstance3D = _mi(g, _cyl(0.14, 0.14, length * 0.55, 8), M.dark, true)
			sl.position.y = length * 0.275
			var so: MeshInstance3D = _mi(g, _cyl(0.21, 0.21, length * 0.55 + 0.1, 8), _out(), false)
			so.position.y = length * 0.275
			var rd: MeshInstance3D = _mi(g, _cyl(0.08, 0.08, length * 0.5, 8), M.silver, true)
			rd.position.y = length * 0.75
			var cc: MeshInstance3D = _mi(g, _cyl(0.16, 0.16, 0.12, 8), M.team, false)
			cc.position.y = length * 0.5
			treb.add_child(g)
		else:
			_spike(treb, Vector3(0.0, AX + 0.25, z), Vector3(0, 1, 0), 0.15, 0.6)
	var axle: MeshInstance3D = _mi(treb, _cyl(0.17, 0.17, 3.0, 8), M.silver, true)
	axle.basis = _euler(Vector3(PI / 2.0, 0.0, 0.0))
	axle.position.y = AX
	# winch wheel
	var wheel := Node3D.new()
	wheel.position = Vector3(0.5, 1.35, 1.64)
	treb.add_child(wheel)
	var tor := TorusMesh.new()
	tor.inner_radius = 0.82
	tor.outer_radius = 1.18
	tor.rings = 12
	tor.ring_segments = 4
	var ti: MeshInstance3D = _mi(wheel, _faceted(tor), M.main if steel else M.wood, true)
	ti.basis = _euler(Vector3(PI / 2.0, 0.0, 0.0))   # three.js tori lie in the XY plane
	var tor2 := TorusMesh.new()
	tor2.inner_radius = 0.74
	tor2.outer_radius = 1.26
	tor2.rings = 12
	tor2.ring_segments = 4
	var to2: MeshInstance3D = _mi(wheel, tor2, _out(), false)
	to2.basis = ti.basis
	for i in 4:
		var a: float = i * PI / 4.0
		_beam(wheel, Vector3(cos(a) * 0.92, sin(a) * 0.92, 0.0), Vector3(-cos(a) * 0.92, -sin(a) * 0.92, 0.0), 0.13, M.trim if steel else M.dark)
	for i in 6:
		var a2: float = i * PI / 3.0 + PI / 12.0
		if steel:
			_glow(wheel, Vector3(0.12, 0.26, 0.44), Vector3(cos(a2), sin(a2), 0.02), Vector3(0.0, 0.0, a2 + PI / 2.0))
		else:
			_spike(wheel, Vector3(cos(a2) * 1.1, sin(a2) * 1.1, 0.0), Vector3(cos(a2), sin(a2), 0.0), 0.08, 0.28)
	_box(wheel, Vector3(0.36, 0.36, 0.3), Vector3(0.0, 0.0, 0.05), M.dark if steel else M.silver)
	# arm
	var arm := Node3D.new()
	arm.position = Vector3(0.0, AX, 0.0)
	treb.add_child(arm)
	var SHORT: float = -2.1
	var LONG: float = 5.6
	_beam(arm, Vector3(SHORT - 0.35, 0.0, 0.0), Vector3(LONG, 0.0, 0.0), 0.44, M.main, [0.42, 0.58, 0.72, 0.86] if steel else [0.1, 0.38, 0.62, 0.86])
	if steel:
		_octo(arm, 0.48, 0.78, Vector3.ZERO, M.trim)
		for z2 in [-0.45, 0.45]:
			var e: MeshInstance3D = _mi(arm, _cyl(0.16, 0.16, 0.06, 8), M.team, false)
			e.basis = _euler(Vector3(PI / 2.0, 0.0, 0.0))
			e.position.z = z2
		_box(arm, Vector3(0.7, 0.62, 0.62), Vector3(SHORT - 0.5, 0.0, 0.0), M.dark)
	else:
		_box(arm, Vector3(0.6, 0.6, 0.62), Vector3.ZERO, M.bone)
		_box(arm, Vector3(0.5, 0.55, 0.55), Vector3(SHORT - 0.45, 0.0, 0.0), M.stone)
		_spike(arm, Vector3(0.0, 0.3, 0.0), Vector3(0, 1, 0), 0.17, 0.8)
		_spike(arm, Vector3(LONG + 0.1, 0.1, 0.0), Vector3(1, 0.7, 0), 0.12, 0.45)
	# counterweight
	var cw := Node3D.new()
	cw.position = Vector3(SHORT, 0.0, 0.0)
	arm.add_child(cw)
	_beam(cw, Vector3(0.0, 0.0, -0.42), Vector3(0.0, -0.95, -0.42), 0.15, M.silver)
	_beam(cw, Vector3(0.0, 0.0, 0.42), Vector3(0.0, -0.95, 0.42), 0.15, M.silver)
	if steel:
		_octo(cw, 1.0, 1.28, Vector3(0.0, -1.95, 0.0), M.main)
		_octo(cw, 0.62, 1.36, Vector3(0.08, -1.95, 0.0), M.trim)
		_box(cw, Vector3(0.4, 0.9, 1.0), Vector3(-0.9, -1.95, 0.0), M.dark)
		for y in [-1.7, -1.95, -2.2]:
			_glow(cw, Vector3(0.06, 0.1, 0.7), Vector3(-1.12, y, 0.0))
		for z3 in [-0.7, 0.7]:
			_glow(cw, Vector3(0.12, 0.45, 0.04), Vector3(0.15, -1.95, z3))
	else:
		_box(cw, Vector3(1.6, 1.7, 1.3), Vector3(0.0, -1.9, 0.0), M.wood)
		_box(cw, Vector3(0.55, 1.2, 1.1), Vector3(-0.85, -1.85, 0.0), M.stone)
		_box(cw, Vector3(1.7, 0.18, 1.38), Vector3(0.0, -1.15, 0.0), M.bone)
		_box(cw, Vector3(1.7, 0.18, 1.38), Vector3(0.0, -2.65, 0.0), M.bone)
		_box(cw, Vector3(0.9, 1.0, 0.1), Vector3(0.15, -1.9, 0.7), M.bone)
		_box(cw, Vector3(0.5, 0.55, 0.06), Vector3(0.15, -1.95, 0.78), M.team, Vector3.ZERO, 0.0)
		for xy in [[-1.1, -1.6], [-1.1, -2.2], [0.85, -1.5], [0.85, -2.3]]:
			_spike(cw, Vector3(xy[0], xy[1], 0.0), Vector3(signf(xy[0]), 0.0, 0.0), 0.1, 0.3)
	# sling and stone
	var sling := Node3D.new()
	sling.position = Vector3(LONG, 0.0, 0.0)
	arm.add_child(sling)
	_beam(sling, Vector3(0.0, 0.0, -0.13), Vector3(0.0, -2.4, -0.13), 0.06, M.rope)
	_beam(sling, Vector3(0.0, 0.0, 0.13), Vector3(0.0, -2.4, 0.13), 0.06, M.rope)
	var pouch := Node3D.new()
	pouch.position = Vector3(0.0, -2.78, 0.0)
	sling.add_child(pouch)
	if steel:
		for i in 5:
			var a3: float = -PI / 2.0 + (i - 2) * 0.55
			var x3: float = cos(a3) * 0.45
			var y3: float = sin(a3) * 0.45
			_box(pouch, Vector3(0.2, 0.42, 0.62), Vector3(x3, y3 + 0.1, 0.0), M.main, Vector3(0.0, 0.0, a3 + PI / 2.0))
			if i % 2 == 0:
				_glow(pouch, Vector3(0.06, 0.22, 0.66), Vector3(x3 * 1.08, y3 * 1.08 + 0.1, 0.0), Vector3(0.0, 0.0, a3 + PI / 2.0))
	else:
		_spike(pouch, Vector3(-0.35, -0.15, 0.0), Vector3(-0.6, 1, 0), 0.12, 0.5)
		_spike(pouch, Vector3(0.35, -0.15, 0.0), Vector3(0.6, 1, 0), 0.12, 0.5)
		_box(pouch, Vector3(0.85, 0.22, 0.6), Vector3(0.0, -0.32, 0.0), M.team)
	var stone := Node3D.new()
	pouch.add_child(stone)
	var sp := SphereMesh.new()
	sp.radius = 0.42
	sp.height = 0.84
	sp.radial_segments = 6
	sp.rings = 3
	_mi(stone, _faceted(sp), M.stone, true)
	var sp2 := SphereMesh.new()
	sp2.radius = 0.53
	sp2.height = 1.06
	sp2.radial_segments = 6
	sp2.rings = 3
	_mi(stone, sp2, _out(), false)
	return {"root": root, "arm": arm, "cw": cw, "sling": sling, "wheel": wheel, "stone": stone}

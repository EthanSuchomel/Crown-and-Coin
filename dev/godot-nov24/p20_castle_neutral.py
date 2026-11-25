"""Godot: the Castle map is one neutral stone picture for every faction (art/arena/castle_neutral_full.png), with the
walkways, stairs and blocking refitted to it, as in the browser arena (dev/castle-walls/patch_castle_neutral.py).
Usage: python3 p20_castle_neutral.py GODOT_FOLDER"""
import sys
R=sys.argv[1].rstrip('/')+'/'
def edit(f, pairs):
    t=open(R+f,encoding='utf8').read()
    for a,b in pairs:
        assert t.count(a)==1,(f,t.count(a),a[:80]); t=t.replace(a,b)
    open(R+f,'w',encoding='utf8').write(t)
s=11.9/672
edit('scripts/arena/arena_battle.gd',[
("# Ethan's sketch: two hexagonal archers' nests joined by a thick wall, with an angled wall running from each nest back to the\n# top and bottom edges.",
 "# Ethan's sketch: two round archers' nests joined by a long wall, with an angled wall running from each nest back to the\n# top and bottom edges. One neutral stone picture for every faction (Ethan, 2026-11-24)."),
('''const CASTLE_DEF := {"inX": 26.6, "gateX": 33.2, "gy": 30.0, "half": 2.6, "hpAt": Vector2(34.2, 25.0),
	"rects": [{"x0": 24.6, "x1": 35.4, "y0": 13.5, "y1": 21.3}, {"x0": 26.6, "x1": 33.2, "y0": 21.3, "y1": 27.4},
		{"x0": 26.6, "x1": 33.2, "y0": 32.6, "y1": 41.0}, {"x0": 24.6, "x1": 35.4, "y0": 41.0, "y1": 49.8}]}''',
'''const CASTLE_DEF := {"inX": 27.1, "gateX": 32.8, "gy": 30.0, "half": 2.6, "hpAt": Vector2(34.2, 25.0),
	"rects": [{"x0": 24.2, "x1": 35.6, "y0": 13.8, "y1": 21.6}, {"x0": 27.1, "x1": 32.8, "y0": 21.6, "y1": 27.4},
		{"x0": 27.1, "x1": 32.8, "y0": 32.6, "y1": 41.3}, {"x0": 24.2, "x1": 35.6, "y0": 41.3, "y1": 49.7}]}'''),
('''	"robot": {"mid": [23.901, 10.178, 12.194], "up": [-11.974, -13.479, 42.263], "lo": [-11.966, 35.56, 42.623]}}''',
'''	"robot": {"mid": [23.901, 10.178, 12.194], "up": [-11.974, -13.479, 42.263], "lo": [-11.966, 35.56, 42.623]}}
## the neutral castle: one picture of the whole castle (field units: left, top, width)
const CASTLE_N := [%.3f, %.3f, %.3f]''' % (9.6385-760*s, 1.2792-320*s, 2296*s)),
('''	for p in [[30.1, 22.6], [30.1, 37.6], [30.1, 25.1], [30.1, 35.1], [30.1, 27.6], [30.1, 32.6], [30.1, 30.1]]:
		mid_slots.append({"x": p[0], "y": p[1], "u": null})
	levels.append({"kind": "mid", "x0": 28.9, "x1": 31.3, "y0": 22.3, "y1": 38.0, "foot": Vector2(25, 30), "top": Vector2(30.1, 30),''',
'''	for p in [[30.0, 18.0], [30.0, 39.0], [30.0, 21.5], [30.0, 35.5], [30.0, 25.0], [30.0, 32.5], [30.0, 28.8]]:
		mid_slots.append({"x": p[0], "y": p[1], "u": null})
	levels.append({"kind": "mid", "x0": 28.7, "x1": 31.3, "y0": 17.5, "y1": 39.5, "foot": Vector2(25.5, 30), "top": Vector2(30.0, 30),'''),
('''		var xa: float = 13.5 if side == 0 else 2.0
		var xb: float = 22.4
		var wa: float = -6.3 if side == 0 else 58.9
		var wb: float = 0.72 if side == 0 else -0.73
		var sl: Array = []
		for x in ([15.5, 17.7, 19.9, 22.1] if side == 0 else [4.0, 7.6, 11.2, 14.8, 18.4, 22.0]):''',
'''		var xa: float = 12.0 if side == 0 else 2.0
		var xb: float = 23.2 if side == 0 else 22.8
		var wa: float = -0.85 if side == 0 else 50.24
		var wb: float = 0.465 if side == 0 else -0.367
		var sl: Array = []
		for x in ([16.4, 18.6, 20.8, 23.0] if side == 0 else [4.0, 7.6, 11.2, 14.8, 18.4, 22.0]):'''),
('''_castle_band(-10.1, 0.72, 1.2, 0.69, true) if side == 0 else _castle_band(55.1, -0.73, 66.0, -0.733, false)''',
 '''_castle_band(-3.4, 0.468, 7.2, 0.465, true) if side == 0 else _castle_band(47.4, -0.367, 58.4, -0.36, false)'''),
('''"foot": Vector2(9, 10.5) if side == 0 else Vector2(21, 39.5),
			"top": Vector2(15.5, 4.9) if side == 0 else Vector2(19.5, 44.7),''',
 '''"foot": Vector2(22.6, 19.2) if side == 0 else Vector2(20.5, 39.3),
			"top": Vector2(15.6, 6.4) if side == 0 else Vector2(19.5, 43.1),'''),
])
edit('scripts/arena/arena_view.gd',[
('''	var robo: bool = battle.robo_holder()
	var A: Dictionary = ArenaBattle.CASTLE_ART.robot if robo else ArenaBattle.CASTLE_ART.dino
	for part in ["up", "lo", "mid"]:
		var t: Texture2D = tex(("castle_r_" if robo else "castle_") + part)
		if battle.mammal_holder():   # the Mammals' log-palisade castle, fitted onto the Dinosaur pieces' spots
			t = tex("castle_m_%s_%s" % [part, SIDE[battle.HOLD]])
		if t == null:
			continue
		var o: Array = A[part]
		var w: float = float(o[2])
		var h: float = w * t.get_size().y / t.get_size().x
		draw_texture_rect(t, Rect2(origin + Vector2(float(o[0]), float(o[1])) * px, Vector2(w, h) * px), false)''',
'''	var t: Texture2D = tex("castle_neutral_full")   # one neutral stone castle for every faction (Ethan, 2026-11-24)
	if t != null:
		var o: Array = ArenaBattle.CASTLE_N
		var w: float = float(o[2])
		var h: float = w * t.get_size().y / t.get_size().x
		draw_texture_rect(t, Rect2(origin + Vector2(float(o[0]), float(o[1])) * px, Vector2(w, h) * px), false)'''),
])
print('ok')

"""Godot port of the browser's castle hex grounds (repo 5946b18, 2026-11-12): the hex under each castle picture is drawn
with that castle's ground tile (art/terrain/gnd_<faction>.png, hex-shaped 222x256 from dev/castle-ground/tiles) in
place of the grass, and without the team colour wash. python3 p1_ground.py PROJECT_DIR"""
import sys
p = sys.argv[1] + '/scripts/ui/board_view.gd'
s = open(p, encoding='utf-8').read()


def rep(old, new):
    global s
    assert s.count(old) == 1, (old[:70], s.count(old))
    s = s.replace(old, new)


rep('''	for v in 6:
		names["forest_%d" % v] = "res://art/vegetation/forest_%d.png" % v''',
    '''	for f in ["dinos", "robots", "mammals", "mythical", "neutral"]:
		names["gnd_" + f] = "res://art/terrain/gnd_%s.png" % f   # castle hex grounds (the ones that exist)
	for v in 6:
		names["forest_%d" % v] = "res://art/vegetation/forest_%d.png" % v''')
rep('''		var owner: int = int(t.owner)
		if owner >= 0:
			var col: Color = _player_color(owner)
			var tint: Color = col
			tint.a = 0.2
			draw_colored_polygon(_hex_points(c, HR * u), tint)''',
    '''		# a castle's hex is drawn with that castle's own ground (the Mythical's: a black drop into nothing)
		var gnd: String = _castle_gnd(t)
		if gnd != "":
			var gr: float = HR + 0.3
			_draw_rect_tex(tex(gnd), Rect2(c - Vector2(gr * sqrt(3.0) / 2.0, gr) * u, Vector2(gr * sqrt(3.0), 2.0 * gr) * u))
		var owner: int = int(t.owner)
		if owner >= 0 and gnd == "":   # no colour wash over a castle's own ground; the team border still shows the owner
			var col: Color = _player_color(owner)
			var tint: Color = col
			tint.a = 0.2
			draw_colored_polygon(_hex_points(c, HR * u), tint)''')
rep('''func _draw_hex_things(font: Font, t: Dictionary, u: float) -> void:''',
    '''## The ground tile for a castle's hex (browser castleGnd): it follows the castle picture drawn there, so a home castle
## shows its owner's faction ground and any other castle the neutral one (none yet: neutral castles keep the grass).
func _castle_gnd(t: Dictionary) -> String:
	if not t.castle:
		return ""
	var owner: int = int(t.owner)
	var key: String = "gnd_neutral"
	if game.homes.has(int(t.id)) and owner >= 0:
		key = "gnd_" + String(game.players[owner].faction)
	return key if _tex.has(key) else ""


func _draw_hex_things(font: Font, t: Dictionary, u: float) -> void:''')
open(p, 'w', encoding='utf-8').write(s)
print('ok')

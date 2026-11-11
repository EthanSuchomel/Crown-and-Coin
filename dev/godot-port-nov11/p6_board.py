# Godot port, step 6: the board art (no home-castle crown, a bigger Floating Castle, the Life Tree centred).
import sys
F = sys.argv[1] + '/scripts/ui/board_view.gd'
s = open(F, encoding='utf-8').read()
def rep(old, new):
    global s
    if s.count(old) != 1: print('COUNT', s.count(old), old[:100]); sys.exit(1)
    s = s.replace(old, new)
rep('''			var w: float = minf(_hh - 3.5, 2.0 * HFIT / (ratio + 1.0 / sqrt(3.0)))''',
    '''			var w: float = 26.0 if art == "castle_mythical" else minf(_hh - 3.5, 2.0 * HFIT / (ratio + 1.0 / sqrt(3.0)))   # the Floating Castle is drawn big, filling its hex (Ethan, 2026-11-10)''')
rep('''	# little icons: home crown, trebuchets, fortified
	var ics: Array = []
	if game.homes.has(i) and t.castle and owner >= 0:
		ics.append(["crown", 1.0])''', '''	# little icons: trebuchets (no crown on home castles since 2026-11-10)
	var ics: Array = []''')
rep('''	if int(t.get("tree", 0)) > 0 and owner >= 0:   # a Life Tree: big, in the middle of its hex
		var z: float = 25.0
		_draw_rect_tex(tex("tree"), Rect2(c + Vector2(-z / 2.0 + 2.0, HR * 0.42 - z) * u, Vector2(z, z) * u))''',
    '''	if int(t.get("tree", 0)) > 0 and owner >= 0:   # a Life Tree: big, centred on its hex
		var z: float = 25.0
		_draw_rect_tex(tex("tree"), Rect2(c - Vector2(z, z) * u / 2.0, Vector2(z, z) * u))''')
open(F, 'w', encoding='utf-8').write(s); print('board ok')

"""Ethan, 2026-11-24: no weird wall overlaps (as the browser's patch_wallfix.py): the up-and-down wall re-cut straight
(no perspective taper) and a little narrower; round a hex the walls are drawn first (upright sides, then the slanted
ones) and the towers after them, for the back half and again for the front half.
Usage: python3 p17_wallfix.py PROJ   (after p16_wallv.py)"""
import sys, shutil, os, json
sys.path.insert(0, __file__.rsplit('/', 2)[0] + '/godot-port-nov22')
from common import F
P = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
shutil.copy(os.path.join(here, 'files/art/walls/wall_v.png'), P + '/art/walls/wall_v.png')
V = json.load(open(os.path.join(here, '..', 'castle-walls', 'art', 'walls.json')))['v']
b = F(P + '/scripts/ui/board_view.gd')
s = b.s
i = s.index('const WALL_V := '); j = s.index('\n', i)
s = s[:i] + 'const WALL_V := ' + json.dumps(V) + s[j:]
b.s = s
b.rep('''const WALL_VW := 0.95''', '''const WALL_VW := 1.15''')
b.rep('''func _draw_wall_art(i: int, k: int, hp: int, back: bool) -> void:''', '''## towers: 0 the walls only, 1 the towers only (walls first round the hex, then the towers over the joins)
func _draw_wall_art(i: int, k: int, hp: int, back: bool, towers: int = 0) -> void:''')
b.rep('''    var legs: Array = []
    if absf(A.x - B.x) < 0.01:   # an upright side: the wall running straight up and down (behind the castle)
        if back:''', '''    var legs: Array = []
    if towers == 1:
        pass
    elif absf(A.x - B.x) < 0.01:   # an upright side: the wall running straight up and down (behind the castle)
        if back:''')
b.rep('''    if hp >= 2:   # a corner tower only where a piece of wall reaches the corner (no lone towers)''', '''    if hp >= 2 and towers == 1:   # a corner tower only where a piece of wall reaches the corner (no lone towers)''')
b.rep('''        for k in 6:
            var hp: int = int(t.walls[[0, 5, 1, 4, 2, 3][k]])
            if hp > 0:
                _draw_wall_art(int(t.id), [0, 5, 1, 4, 2, 3][k], hp, true)   # the back half (2026-11-24); the front after the castle''', '''        for tw in [0, 1]:   # the back half (2026-11-24): walls (upright sides first), then towers; the front after the castle
            for k in [1, 4, 0, 5, 2, 3]:
                if int(t.walls[k]) > 0:
                    _draw_wall_art(int(t.id), k, int(t.walls[k]), true, tw)''')
b.rep('''    for k in [0, 5, 1, 4, 2, 3]:   # the front half of its walls, in front of the castle (2026-11-24)
        if int(t.walls[k]) > 0:
            _draw_wall_art(i, k, int(t.walls[k]), false)''', '''    for tw in [0, 1]:   # the front half of its walls, in front of the castle (2026-11-24): walls, then towers
        for k in [1, 4, 0, 5, 2, 3]:
            if int(t.walls[k]) > 0:
                _draw_wall_art(i, k, int(t.walls[k]), false, tw)''')
# cut flush at the corners (no end faces: the walls join into one, under the corner towers)
b.rep('''    if l0 <= 0.001 and l1 >= 0.999:
        draw_texture(t, Vector2.ZERO)
    else:   # a damaged wall: only the columns of its pieces (the shear keeps columns upright)
        var x0: float = float(P.s[0]) + l0 * dPx
        var x1: float = float(P.s[0]) + l1 * dPx''', '''    if true:   # always cut flush at the corners (2026-11-24), a damaged wall to its pieces (the shear keeps columns upright)
        var ex: float = 0.2 * _scale() / maxf(1.0, a.distance_to(b))
        var x0: float = float(P.s[0]) + (l0 if l0 > 0.001 else -ex) * dPx
        var x1: float = float(P.s[0]) + (l1 if l1 < 0.999 else 1.0 + ex) * dPx''')
b.rep('''    var y0: float = 0.0 if l0 <= 0.001 else vt + l0 * (vb - vt)''', '''    var y0: float = vt + l0 * (vb - vt)   # cut flush at the far corner (2026-11-24)''')
b.save()
print('ok')

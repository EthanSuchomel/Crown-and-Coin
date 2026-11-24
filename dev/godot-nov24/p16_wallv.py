"""Ethan, 2026-11-24: the upright sides of a hex get the OpenArt wall that runs straight up and down
(art/walls/wall_v.png), not two slanted runs; corner towers only where a wall reaches them (as the browser's
patch_wallv.py and patch_lonetower.py).
Usage: python3 p16_wallv.py PROJ   (after p15_wallart.py)"""
import sys, shutil, os, json
sys.path.insert(0, __file__.rsplit('/', 2)[0] + '/godot-port-nov22')
from common import F
P = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
shutil.copy(os.path.join(here, 'files/art/walls/wall_v.png'), P + '/art/walls/wall_v.png')
V = json.load(open(os.path.join(here, '..', 'castle-walls', 'art', 'walls.json')))['v']
b = F(P + '/scripts/ui/board_view.gd')
b.rep('''        "wall_tw": "res://art/walls/wall_tw.png",''', '''        "wall_tw": "res://art/walls/wall_tw.png",
        "wall_v": "res://art/walls/wall_v.png",''')
b.rep('''    var legs: Array = []
    if absf(A.x - B.x) < 0.01:   # an upright side: two runs meeting in a little bastion outside it
        var M := Vector2(A.x + (-1.0 if A.x < c.x else 1.0) * WALL_BASTION * u, (A.y + B.y) * 0.5)
        legs = [[A, M, 0.0, 0.5], [M, B, 0.5, 1.0]]
    else:
        legs = [[A, B, 0.0, 1.0]]''', '''    var legs: Array = []
    if absf(A.x - B.x) < 0.01:   # an upright side: the wall running straight up and down (behind the castle)
        if back:
            var top: bool = A.y < B.y
            for pr in parts:
                var l0u: float = float(pr[0]) if top else 1.0 - float(pr[1])
                var l1u: float = float(pr[1]) if top else 1.0 - float(pr[0])
                _wall_up(A if top else B, B if top else A, l0u, l1u)
    else:
        legs = [[A, B, 0.0, 1.0]]''')
b.rep('''    if hp >= 2:
        for e in [A, B]:
            if (e.y < c.y) == back:
                _wall_tower(e, r)''', '''    if hp >= 2:   # a corner tower only where a piece of wall reaches the corner (no lone towers)
        for e in [A, B]:
            if (e.y < c.y) == back:
                _wall_tower(e, r)


const WALL_V := %s
const WALL_VW := 0.95


## An upright side from a (top) to b (bottom); only the part l0..l1 of it (from the top) when damaged.
func _wall_up(a: Vector2, b: Vector2, l0: float, l1: float) -> void:
    var t: Texture2D = tex("wall_v")
    if t == null:
        return
    var vt: float = float(WALL_V.t)
    var vb: float = float(WALL_V.b)
    var sy: float = (b.y - a.y) / (vb - vt)
    var sx: float = sy * WALL_VW
    draw_set_transform_matrix(Transform2D(Vector2(sx, 0.0), Vector2(0.0, sy), Vector2(a.x - float(WALL_V.cx) * sx, a.y - vt * sy)))
    var y0: float = 0.0 if l0 <= 0.001 else vt + l0 * (vb - vt)
    var y1: float = t.get_size().y if l1 >= 0.999 else vt + l1 * (vb - vt)
    var w: float = t.get_size().x
    draw_texture_rect_region(t, Rect2(0.0, y0, w, y1 - y0), Rect2(0.0, y0, w, y1 - y0))
    draw_set_transform_matrix(Transform2D.IDENTITY)''' % json.dumps(V))
b.save()
print('ok')

"""Ethan, 2026-11-24: the OpenArt stone walls for every faction (same as the browser's dev/castle-walls/patch_wallart.py):
art/walls/wall_d0.png (a run down to the right), wall_d1.png (up to the right), wall_tw.png (a tower). Each walled side
is one run sheared onto the side (verticals stay upright); an upright side is two runs meeting in a little bastion just
outside it; towers at the corners; a damaged wall keeps only its pieces (cut by picture columns). Walls on the back half
of a hex are drawn before its castle, the rest after.
Usage: python3 p15_wallart.py PROJ"""
import sys, shutil, os, json
sys.path.insert(0, __file__.rsplit('/', 2)[0] + '/godot-port-nov22')
from common import F
P = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
os.makedirs(P + '/art/walls', exist_ok=True)
for k in ['d0', 'd1', 'tw']:
    shutil.copy(os.path.join(here, 'files/art/walls/wall_%s.png' % k), P + '/art/walls/wall_%s.png' % k)
J = json.load(open(os.path.join(here, '..', 'castle-walls', 'art', 'walls.json')))
b = F(P + '/scripts/ui/board_view.gd')
b.rep('''            var hp: int = int(t.walls[k])
            if hp > 0:
                _draw_wall(int(t.id), k, hp, false)''', '''            var hp: int = int(t.walls[[0, 5, 1, 4, 2, 3][k]])
            if hp > 0:
                _draw_wall_art(int(t.id), [0, 5, 1, 4, 2, 3][k], hp, true)   # the back half (2026-11-24); the front after the castle''')
b.rep('''    # buildings: a little village down the hex's left side (on a castle, around its feet)''', '''    for k in [0, 5, 1, 4, 2, 3]:   # the front half of its walls, in front of the castle (2026-11-24)
        if int(t.walls[k]) > 0:
            _draw_wall_art(i, k, int(t.walls[k]), false)
    # buildings: a little village down the hex's left side (on a castle, around its feet)''')
b.rep('''## A Mythical magic dome over a hex''', '''## The castle's stone walls from OpenArt (Ethan, 2026-11-24): every faction's walls. s and e: the ends of a run's centre
## line on the ground, in picture pixels; f: a tower's foot.
const WALL_PIX := %s
const WALL_VS := 0.8
const WALL_BASTION := 1.8


func _draw_wall_art(i: int, k: int, hp: int, back: bool) -> void:
    var u: float = _scale()
    var c: Vector2 = center(i)
    var r: float = (HR - 2.3) * u
    var A: Vector2 = _corner(c, r, k)
    var B: Vector2 = _corner(c, r, k + 1)
    var parts: Array = [[0.0, 1.0]] if hp >= 3 else ([[0.0, 0.38], [0.62, 1.0]] if hp == 2 else [[0.36, 0.64]])
    var legs: Array = []
    if absf(A.x - B.x) < 0.01:   # an upright side: two runs meeting in a little bastion outside it
        var M := Vector2(A.x + (-1.0 if A.x < c.x else 1.0) * WALL_BASTION * u, (A.y + B.y) * 0.5)
        legs = [[A, M, 0.0, 0.5], [M, B, 0.5, 1.0]]
    else:
        legs = [[A, B, 0.0, 1.0]]
    for lg in legs:
        var p: Vector2 = lg[0]
        var q: Vector2 = lg[1]
        var u0: float = lg[2]
        var u1: float = lg[3]
        var flip: bool = p.x > q.x
        var L0: Vector2 = q if flip else p
        var L1: Vector2 = p if flip else q
        for pr in parts:
            var a0: float = maxf(float(pr[0]), u0)
            var a1: float = minf(float(pr[1]), u1)
            if a1 - a0 < 0.02:
                continue
            var l0: float = (a0 - u0) / (u1 - u0)
            var l1: float = (a1 - u0) / (u1 - u0)
            if flip:
                var x0: float = l0
                l0 = 1.0 - l1
                l1 = 1.0 - x0
            if ((L0.y + L1.y) * 0.5 < c.y) == back:
                _wall_run(L0, L1, l0, l1, r)
    if hp >= 2:
        for e in [A, B]:
            if (e.y < c.y) == back:
                _wall_tower(e, r)


func _wall_run(a: Vector2, b: Vector2, l0: float, l1: float, r: float) -> void:
    var key: String = "d0" if b.y > a.y else "d1"
    var t: Texture2D = tex("wall_" + key)
    if t == null:
        return
    var P: Dictionary = WALL_PIX[key]
    var dPx: float = float(P.e[0]) - float(P.s[0])
    var dPy: float = float(P.e[1]) - float(P.s[1])
    var sc: float = (b.x - a.x) / dPx
    var D: float = sc * WALL_VS
    var sh: float = ((b.y - a.y) - D * dPy) / dPx
    var o := Vector2(a.x - sc * float(P.s[0]), a.y - sh * float(P.s[0]) - D * float(P.s[1]))
    draw_set_transform_matrix(Transform2D(Vector2(sc, sh), Vector2(0.0, D), o))
    if l0 <= 0.001 and l1 >= 0.999:
        draw_texture(t, Vector2.ZERO)
    else:   # a damaged wall: only the columns of its pieces (the shear keeps columns upright)
        var x0: float = float(P.s[0]) + l0 * dPx
        var x1: float = float(P.s[0]) + l1 * dPx
        var h: float = t.get_size().y
        draw_texture_rect_region(t, Rect2(x0, 0.0, x1 - x0, h), Rect2(x0, 0.0, x1 - x0, h))
    draw_set_transform_matrix(Transform2D.IDENTITY)


func _wall_tower(at: Vector2, r: float) -> void:
    var t: Texture2D = tex("wall_tw")
    if t == null:
        return
    var d0: Dictionary = WALL_PIX.d0
    var sc: float = r * 0.8660254 / (float(d0.e[0]) - float(d0.s[0]))
    var D: float = sc * WALL_VS
    var f: Array = WALL_PIX.tw.f
    draw_set_transform_matrix(Transform2D(Vector2(sc, 0.0), Vector2(0.0, D), Vector2(at.x - float(f[0]) * sc, at.y - float(f[1]) * D)))
    draw_texture(t, Vector2.ZERO)
    draw_set_transform_matrix(Transform2D.IDENTITY)


## A Mythical magic dome over a hex''' % json.dumps({k: {kk: vv for kk, vv in v.items() if kk not in ('uri',)} for k, v in J.items()}))
b.rep('''        "castle_keep": "res://art/terrain/castle_keep.png",''', '''        "castle_keep": "res://art/terrain/castle_keep.png",
        "wall_d0": "res://art/walls/wall_d0.png",
        "wall_d1": "res://art/walls/wall_d1.png",
        "wall_tw": "res://art/walls/wall_tw.png",''')
b.save()
print('ok')

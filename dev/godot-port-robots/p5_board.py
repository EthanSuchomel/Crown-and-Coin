# The Robot rework for the Godot version, step 5: the board (board_view.gd). A Robot factory is one big picture for its
# level (market, market + barracks, full fortress), centred in the hex, with gold pips for its barracks level; a resource
# hex shows its markets as a neat group of 2, 3 or 4. Sizes and spots as in the browser (patch1/patch2).
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import F
f = F(sys.argv[1] + '/scripts/ui/board_view.gd')
f.rep('''    var village: bool = not blds.is_empty() and not t.castle
    if not blds.is_empty() and owner >= 0:''', '''    var robo: bool = owner >= 0 and fac == "robots" and not t.castle and int(t.market) > 0
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
    if not blds.is_empty() and owner >= 0:''')
f.save(); print('p5 board ok')

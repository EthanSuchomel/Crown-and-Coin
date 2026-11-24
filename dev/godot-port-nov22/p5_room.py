"""Browser commit a75a599 (Ethan, 2026-11-23) in Godot:
- the round buttons round a hex keep their full size and, when they don't fit where they usually go (off the screen,
  under the cards or the numbers box, or on top of each other), spread round the hex into the open space in the same
  order, on a ring that widens if it has to (they used to be pushed against the edge on top of each other);
- no hints under the playing card (the notes, picks, buttons and warnings stay);
- on a computer-sized window (1150 px and wider) the cards column takes a quarter of the width instead of a third.
Usage: python3 p5_room.py PROJ"""
import sys, re
from common import F, T
P = sys.argv[1]
f = F(P + '/scripts/ui/main.gd')

# full-size buttons on the rings; no squeezing against the edges (the layout below moves them instead)
n0 = f.s.count('minf(R, (hr * 0.95 + stem) / 1.75)')
assert n0 == 3, n0
f.s = f.s.replace('minf(R, (hr * 0.95 + stem) / 1.75)', 'R')
f.s, k = re.subn(r'\.clamp\(_bub_lo\((\w+)\), _bub_hi\(\1\)\)', '', f.s)
assert k == 4, k

f.rep('''func _place_bubbles() -> void:
    if bubbles == null:
        return''', '''## The buttons round the selected hex, then laid out into open space if they don't fit (Ethan, 2026-11-23).
func _place_bubbles() -> void:
    _place_bubbles_raw()
    if bubbles != null and g != null and sel >= 0 and bubbles.size.x >= 10.0:
        _bub_relayout()


func _place_bubbles_raw() -> void:
    if bubbles == null:
        return''')

f.rep('''## Where the buttons round a hex may go: inside the map's part of the screen.''', '''## If every button round the hex is on screen, clear of the cards column, the numbers box and the floating buttons, and
## none touch, they stay. Otherwise they keep their order round the hex and go, evenly spaced, wherever the ring round the
## hex is open (the ring widens if it must; smaller spacing last), nearest their usual spots. The posts follow.
func _bub_relayout() -> void:
    var bs: Array = bubbles.get_children().filter(func(b): return b is Button and not b.is_queued_for_deletion())
    var n: int = bs.size()
    if n == 0:
        return
    var c: Vector2 = board.center(sel)
    var hr: float = board.radius()
    var stem: float = clampf(hr * 0.66, 26.0, 44.0) * 0.36
    var M: float = 4.0
    var area := Rect2(Vector2.ZERO, bubbles.size).grow(-M)
    var blocks: Array = []
    for nd in [side, stats_panel, float_btns]:
        if nd != null and is_instance_valid(nd) and nd.is_visible_in_tree() and nd.modulate.a > 0.05:
            blocks.append(Rect2(nd.global_position - bubbles.global_position, nd.size).grow(M))
    var fits := func(p: Vector2, r: float) -> bool:
        if p.x - r < area.position.x or p.y - r < area.position.y or p.x + r > area.end.x or p.y + r > area.end.y:
            return false
        for bl in blocks:
            var q: Vector2 = p.clamp(bl.position, bl.end)
            if q.distance_squared_to(p) < r * r:
                return false
        return true
    var ps: Array = []
    var rs: Array = []
    for b in bs:
        ps.append(b.position + b.size / 2.0)
        rs.append(b.size.x / 2.0)
    var ok_now: bool = true
    for i in n:
        if not fits.call(ps[i], rs[i]):
            ok_now = false
        for j in range(i + 1, n):
            if ps[i].distance_to(ps[j]) < rs[i] + rs[j] + 2.0:
                ok_now = false
    if ok_now:
        return
    var want: Array = []
    for i in n:
        var v: Vector2 = ps[i] - c
        want.append(fposmod(rad_to_deg(atan2(-v.y, v.x)), 360.0))
    var ord: Array = range(n)
    ord.sort_custom(func(x, y): return want[x] < want[y])
    var rmax: float = 0.0
    for r in rs:
        rmax = maxf(rmax, r)
    var dist := func(a: float, b: float) -> float: return absf(fposmod(a - b + 540.0, 360.0) - 180.0)
    for extra in [0.0, 0.6, 1.2, 1.8, 2.6, 3.4]:
        var ring: float = hr * 0.95 + stem + rmax + extra * rmax
        var gap: float = rad_to_deg(2.0 * asin(minf(1.0, (rmax + 2.0) / ring)))
        if gap * n > 360.0:
            continue
        var sp: float = minf(360.0 / n, gap * 1.25)
        var open := {}
        for d in range(0, 360, 2):
            var a: float = deg_to_rad(d)
            open[d] = fits.call(c + Vector2(cos(a), -sin(a)) * ring, rmax)
        var best: Array = []
        var bc: float = INF
        for c0 in range(0, 360, 2):
            for rot in n:
                var cost: float = 0.0
                var good: bool = true
                for k in n:
                    var dd: float = fposmod(c0 + k * sp, 360.0)
                    if not open.get(int(dd / 2.0) * 2, false):
                        good = false
                        break
                    cost += dist.call(dd, want[ord[(k + rot) % n]])
                if good and cost < bc:
                    bc = cost
                    best = [c0, rot]
        var spots: Array = []   # the spot for the k-th button in order, from the even spacing or the fallback below
        if not best.is_empty():
            for k in n:
                spots.append(float(best[0]) + k * sp)
        else:   # no evenly spaced run fits: spread them over the open stretches, each a button apart, in order
            var st: int = -1
            for d in range(0, 360, 2):
                if not open[d]:
                    st = d
                    break
            if st < 0:
                continue
            var at: Array = []
            var last: float = -1e9
            for i in range(1, 181):
                var dd2: float = float(st + i * 2)
                if open[int(fposmod(dd2, 360.0))] and dd2 - last >= gap and (at.is_empty() or dd2 - at[0] <= 360.0 - gap):
                    at.append(dd2)
                    last = dd2
            if at.size() < n:
                continue
            var bi: int = 0
            var bv: float = INF
            for i in range(0, at.size() - n + 1):
                for rot in n:
                    var cost2: float = 0.0
                    for k in n:
                        cost2 += dist.call(fposmod(at[i + k], 360.0), want[ord[(k + rot) % n]])
                    if cost2 < bv:
                        bv = cost2
                        bi = i
                        best = [0, rot]
            spots = at.slice(bi, bi + n)
        bubbles.posts = []
        for k in n:
            var si: int = ord[(k + int(best[1])) % n]
            var a2: float = deg_to_rad(float(spots[k]))
            var d2 := Vector2(cos(a2), -sin(a2))
            var p2: Vector2 = c + d2 * ring
            bs[si].position = p2 - bs[si].size / 2.0
            bubbles.posts.append([c + d2 * hr * 0.86, p2 - d2 * rs[si] * 0.9])
        bubbles.queue_redraw()
        return
    # nothing open enough: at least keep each one on the screen
    for i in n:
        var p3: Vector2 = Vector2(ps[i]).clamp(area.position + Vector2(rs[i], rs[i]), area.end - Vector2(rs[i], rs[i]))
        bs[i].position = p3 - bs[i].size / 2.0


## Where the buttons round a hex may go: inside the map's part of the screen.''')

# no hints under the playing card
f.rep('''func _hint(box: VBoxContainer, text: String) -> void:
    box.add_child(_label(text, 14, LICHEN))''', '''## The hints under the playing card are gone (Ethan, 2026-11-23: "get rid of the description under the card").
func _hint(box: VBoxContainer, text: String) -> void:
    pass''')

# a slimmer cards column on a computer-sized window
f.rep('''    var right := VBoxContainer.new()
    right.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    right.size_flags_stretch_ratio = 34.0
    right.custom_minimum_size.x = 330''', '''    var right := VBoxContainer.new()
    right.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    right.size_flags_stretch_ratio = 100.0 - _map_share()
    right.custom_minimum_size.x = _side_min()''')
f.rep('''    left.size_flags_stretch_ratio = 66.0''', '''    left.size_flags_stretch_ratio = _map_share()''')
f.rep('''func _on_resized() -> void:
    _layout_board.call_deferred()''', '''func _on_resized() -> void:
    if side != null and is_instance_valid(side):   # the cards column's share follows the window's width
        side.size_flags_stretch_ratio = 100.0 - _map_share()
        side.custom_minimum_size.x = _side_min()
        var left: Control = side.get_parent().get_child(0)
        left.size_flags_stretch_ratio = _map_share()
    _layout_board.call_deferred()


## The map's share of the width: 75 on a computer-sized window (Ethan, 2026-11-23: a slimmer cards column), else 66.
func _map_share() -> float:
    return 75.0 if size.x >= 1150.0 else 66.0


func _side_min() -> float:
    return 300.0 if size.x >= 1150.0 else 330.0''')
f.rep('''        var lw: float = avail - maxf(330.0, avail * 0.34)''', '''        var lw: float = avail - maxf(_side_min(), avail * (1.0 - _map_share() / 100.0))''')
f.save()
print('ok')

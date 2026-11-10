# Godot port, catching up with the browser (claude.ai) version, 2026-11-09:
#  - the 3D trebuchet firing animation (scripts/ui/treb_anim.gd, copied in separately)
#  - the Rhino's and Palaeoloxodon's walk frames follow the ground they cover (stride), so their feet don't slide
#  - two unit notes (Robot Archer, Robot Longbow) worded as in the browser version
import sys, json; sys.path.insert(0,sys.path[0])
from common import F
R=sys.argv[1].rstrip('/')
P=R+'/scripts/'

# ---- rules: each finished trebuchet's shot is handed to the board to animate
g=F(P+'rules/game_state.gd')
g.rep('''var volc_fx: Array = []            # volcano eruptions for the board to animate: {from, to, dice} (not saved)''',
'''var volc_fx: Array = []            # volcano eruptions for the board to animate: {from, to, dice} (not saved)
var treb_fx: Array = []            # trebuchet shots for the board to animate: {from, to, pid} (not saved)''')
g.rep('''    else:
        add_log("%s trebuchet misses." % players[pid].name)
    return {"from": i, "to": j, "dice": dice, "hits": hits, "wall_lost": wall_hits, "killed": killed_total, "lost": lost}''',
'''    else:
        add_log("%s trebuchet misses." % players[pid].name)
    if not quiet and treb_fx.size() < 24:
        treb_fx.append({"from": i, "to": j, "pid": pid})
    return {"from": i, "to": j, "dice": dice, "hits": hits, "wall_lost": wall_hits, "killed": killed_total, "lost": lost}''')
g.save()

# ---- board: hosts the animation, remembers where each finished trebuchet picture stands, hides it while its model plays
b=F(P+'ui/board_view.gd')
b.rep('''var lava_fx: Array = []          # volcano eruptions playing: {from, to, bombs, t0}''',
'''var lava_fx: Array = []          # volcano eruptions playing: {from, to, bombs, t0}
var anim_hex: int = -1           # the hex whose flat trebuchet picture is hidden while its 3D model fires
var treb_feet: Dictionary = {}   # hex -> where its finished trebuchet picture stands (screen), for the 3D model
var treb_anim = null             # the trebuchet firing animation (treb_anim.gd)''')
b.rep('''func _ready() -> void:
    mouse_filter = Control.MOUSE_FILTER_STOP
''','''func _ready() -> void:
    mouse_filter = Control.MOUSE_FILTER_STOP
    treb_anim = load("res://scripts/ui/treb_anim.gd").new()
    treb_anim.board = self
    add_child(treb_anim)
''')
b.rep('''func _draw() -> void:
    if game == null:
        return
    var u: float = _scale()
''','''func _draw() -> void:
    if game == null:
        return
    treb_feet = {}
    var u: float = _scale()
''')
b.rep('''            ics.append([tk, 1.0 if int(t[key]) == 2 else 0.4])''','''            ics.append([tk, 1.0 if int(t[key]) == 2 else 0.4, int(t[key]) == 2])''')
b.rep('''        var tx: float = x + isz / 2.0 - sz2 / 2.0
        var ty: float = y + isz - sz2
        _draw_rect_tex(tex(ics[n][0]), Rect2(c + Vector2(tx, ty) * u, Vector2(sz2, sz2) * u), Color(1, 1, 1, ics[n][1]))''',
'''        var tx: float = x + isz / 2.0 - sz2 / 2.0
        var ty: float = y + isz - sz2
        if ics[n].size() > 2 and ics[n][2]:   # a finished trebuchet: its 3D model stands on this spot when it fires
            if not treb_feet.has(i):
                treb_feet[i] = c + Vector2(tx + sz2 / 2.0, ty + sz2) * u
            if i == anim_hex:
                continue
        _draw_rect_tex(tex(ics[n][0]), Rect2(c + Vector2(tx, ty) * u, Vector2(sz2, sz2) * u), Color(1, 1, 1, ics[n][1]))''')
b.save()

# ---- main: hand the shots over when the screen refreshes, as with the volcano's lava
m=F(P+'ui/main.gd')
m.rep('''    while not g.volc_fx.is_empty():
        var fx: Dictionary = g.volc_fx.pop_front()
        board.lava(int(fx.from), int(fx.to), fx.dice)''','''    while not g.volc_fx.is_empty():
        var fx: Dictionary = g.volc_fx.pop_front()
        board.lava(int(fx.from), int(fx.to), fx.dice)
    while not g.treb_fx.is_empty():
        var tf: Dictionary = g.treb_fx.pop_front()
        board.treb_anim.shot(int(tf.from), int(tf.to), int(tf.pid))''')
m.save()

# ---- arena: stride-locked walk frames for the two big Mammals
a=F(P+'arena/arena_battle.gd')
a.rep('''"walkSheet": true, "sheet": 13, "runFrames": 12, "runCycle": 0.8, "rank": 0,''','''"walkSheet": true, "sheet": 13, "runFrames": 12, "runCycle": 0.8, "stride": 4.962, "rank": 0,''')
a.rep('''"walkSheet": true, "sheet": 25, "runFrames": 12, "runCycle": 0.7, "atkFrames": 13,''','''"walkSheet": true, "sheet": 25, "runFrames": 12, "runCycle": 0.7, "stride": 4.14, "atkFrames": 13,''')
a.rep('''    var phase: float = 0.0''','''    var phase: float = 0.0
    var odo: float = 0.0          # ground covered, for units whose walk frames follow their feet (T.stride)''')
a.rep('''            f.x += f.vx
            f.y += f.vy
            if f.T.has("prop"):''','''            f.x += f.vx
            f.y += f.vy
            if f.T.has("stride"):
                f.odo += Vector2(f.vx, f.vy).length()
            if f.T.has("prop"):''')
a.save()
v=F(P+'arena/arena_view.gd')
v.rep('''        if f.walking and not over and f.lunge < 0 and not (f.stun > 0):
            var fast: bool = T.has("sprintFrom") and (f.boost > 0 or f.fleeing)''','''        if f.walking and not over and f.lunge < 0 and not (f.stun > 0):
            if T.has("stride"):   # Rhino, Palaeoloxodon: one walk cycle per stride of ground covered, so the feet don't slide
                return 1 + int(floor(f.odo / float(T.stride) * RF)) % RF
            var fast: bool = T.has("sprintFrom") and (f.boost > 0 or f.fleeing)''')
v.save()

# ---- unit notes, as the browser version words them
u=F(R+'/data/units.json')
u.rep('''        "note": "Shooter. Hits flyers (misses 20%)"''','''        "note": "Shooter. Fires 2 lasers a shot. Hits flyers (misses 20%)"''')
u.rep('''Stun Shot: shots 1, 5, 9 stun the unit hit''','''Stun Shot: shots 1, 5, 9… stun the unit hit''')
u.save()
json.load(open(R+'/data/units.json'))
print('p15 match ok')

# ---- self-test: the shot reaches the board's animation queue; the stride numbers are the browser's
t=F(P+'rules/test_rules.gd')
t.rep('''    var shot: Dictionary = h.fire_treb(h.homes[0], m)
    check("trebuchet rolls 5 dice", shot.dice.size() == 5)''','''    var shot: Dictionary = h.fire_treb(h.homes[0], m)
    check("trebuchet rolls 5 dice", shot.dice.size() == 5)
    check("the shot is handed to the board's 3D trebuchet animation", h.treb_fx.size() == 1 and int(h.treb_fx[0].from) == h.homes[0] and int(h.treb_fx[0].to) == m)''')
t.rep('''    var AT: Dictionary = ArenaBattle.TYPES.alamo''','''    check("arena: the Rhino's and Palaeoloxodon's walk frames follow the ground they cover", is_equal_approx(float(ArenaBattle.TYPES.rhino.get("stride", 0)), 4.962) and is_equal_approx(float(ArenaBattle.TYPES.eleph.get("stride", 0)), 4.14))
    var AT: Dictionary = ArenaBattle.TYPES.alamo''')
t.save()
print('p15 tests ok')

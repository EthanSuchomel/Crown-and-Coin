"""Ethan, 2026-11-24 (the same changes as the browser's dev/robo-market-up, dev/turn-warn and dev/castle-walls):
- Robots: Barracks / Fortress bought at the market itself during Advancements (not from the home castle, which needn't
  be held).
- A castle battle is on the Castle map only when there's a wall on the attacked side; otherwise the Open field. No
  ballistas on the castle.
- Walls on the board: stone walls with battlements and round corner towers (timber for the Mammals).
- About to win: a banner at the start of every turn. Your faction: a briefing on your first turn.
Usage: python3 p13_fixes.py PROJ"""
import sys
sys.path.insert(0, __file__.rsplit('/', 2)[0] + '/godot-port-nov22')
from common import F
P = sys.argv[1]

g = F(P + '/scripts/rules/game_state.gd')
g.rep('''    if not is_robots(pid) or int(t.owner) != pid or nk == "" or (k != "" and k != nk) or not home_market(pid) or cur_action() != "advance":''',
      '''    if not is_robots(pid) or int(t.owner) != pid or nk == "" or (k != "" and k != nk) or cur_action() != "advance":   # at the market itself (2026-11-24)''')
g.rep('''## Which Arena map a fight on this hex uses.
func arena_map(t: Dictionary) -> String:
    if t.castle:
        return "castle"''', '''## Which Arena map a fight on this hex uses. w: the wall on the attacked side (-1: not known). A castle with no wall
## there is fought on the Open field (Ethan, 2026-11-24).
func arena_map(t: Dictionary, w: int = -1) -> String:
    if t.castle:
        return "castle" if w != 0 else "open"''')
g.rep('''    o.adv_d = def_adv(B)
    o.map = arena_map(B)
    return o''', '''    o.adv_d = def_adv(B)
    o.map = arena_map(B, int(o.wall))
    return o''')
g.rep('''            o = arena_o(pid, lvl, prev, arena_map(B))''', '''            o = arena_o(pid, lvl, prev, arena_map(B, W))''')
g.save()

a = F(P + '/scripts/rules/ai_player.gd')
a.rep('''        o = g.arena_o(pid, lvl, int(b.owner), g.arena_map(b))''', '''        o = g.arena_o(pid, lvl, int(b.owner), g.arena_map(b, W))''')
a.rep('''        o.map = g.arena_map(b)
    var p: float = win_est(sel, g.def_army(b), o)''', '''        o.map = g.arena_map(b, W)
    var p: float = win_est(sel, g.def_army(b), o)''')
a.rep('''            o = g.arena_o(pid, lvl, int(e.owner), g.arena_map(e))''', '''            o = g.arena_o(pid, lvl, int(e.owner), g.arena_map(e, g.wall_on(j, int(b.id))))''')
a.rep('''            o.map = g.arena_map(e)''', '''            o.map = g.arena_map(e, int(o.wall))''')
a.rep('''    if g.is_robots(pid) and g.home_market(pid):   # the Robots' factory upgrades, made at the home castle, then Overclock''',
      '''    if g.is_robots(pid):   # the Robots' factory upgrades (bought at the market itself since 2026-11-24), then Overclock''')
a.save()

ab = F(P + '/scripts/arena/arena_battle.gd')
ab.rep('''    _make_ballistas()
    _make_path(float(D.gateX) - 1.2, AW, float(D.gy))''', '''    bal = []   # no ballistas on the castle (Ethan, 2026-11-24)
    _make_path(float(D.gateX) - 1.2, AW, float(D.gy))''')
ab.save()

b = F(P + '/scripts/ui/board_view.gd')
b.rep('''    var width: float = (1.6 + hp * 0.8) * u
    if preview:
        _dashed_line(a, b, GOLD if blink else Color(GOLD, 0.4), 2.2 * u)
        return
    draw_line(a, b, OUTLINE, width + 1.4 * u)
    draw_line(a, b, Color("b8b2a2"), width)
    # crenellations
    var n: int = 4
    for q in n:
        var p: Vector2 = a.lerp(b, (q + 0.5) / n)
        var d: Vector2 = (b - a).normalized() * 1.2 * u
        draw_line(p - d, p + d, Color("8c8676"), width * 0.45)''', '''    if preview:
        _dashed_line(a, b, GOLD if blink else Color(GOLD, 0.4), 2.2 * u)
        return
    # stone walls (Ethan, 2026-11-24: walls that fit round the castle): a thick wall with battlements on the outer edge
    # and a round tower at each end, so walled sides meet in one tower. A damaged wall shows gaps. Timber for the Mammals.
    var t: Dictionary = game.tiles[i]
    var wood: bool = int(t.owner) >= 0 and String(game.players[int(t.owner)].faction) == "mammals"
    var dk: Color = Color("2a1608") if wood else Color("1a1712")
    var body: Color = Color("8a5a30") if wood else Color("8f887a")
    var top: Color = Color("b07a45") if wood else Color("b9b2a0")
    var crest: Color = Color("d39a5a") if wood else Color("dcd5c4")
    var twr: Color = Color("7a4c26") if wood else Color("a39b8a")
    var cap: Color = Color("5e3b20") if wood else Color("6f685b")
    var along: Vector2 = (b - a).normalized()
    var mid: Vector2 = (a + b) * 0.5
    var outv: Vector2 = (mid - c).normalized()
    var parts: Array = [[0.04, 0.96]] if hp >= 3 else ([[0.06, 0.34], [0.66, 0.94]] if hp == 2 else [[0.36, 0.64]])
    for pr in parts:
        var p0: Vector2 = a.lerp(b, float(pr[0]))
        var p1: Vector2 = a.lerp(b, float(pr[1]))
        draw_line(p0, p1, dk, 4.4 * u)
        draw_line(p0, p1, body, 3.2 * u)
        draw_line(p0 - outv * 0.5 * u, p1 - outv * 0.5 * u, top, 1.3 * u)
        var n: int = maxi(2, int(round(p0.distance_to(p1) / u / 1.6)))
        for q in n:
            var pc: Vector2 = p0.lerp(p1, (q + 0.5) / n)
            var w: Vector2 = along * 0.55 * u
            var pts := PackedVector2Array([pc - w + outv * 0.2 * u, pc + w + outv * 0.2 * u, pc + w + outv * 1.15 * u, pc - w + outv * 1.15 * u])
            draw_colored_polygon(pts, crest)
            draw_polyline(pts + PackedVector2Array([pts[0]]), dk, 0.35 * u)
    for e in [[0.0, hp >= 3 or hp == 2], [1.0, hp >= 3 or hp == 2]]:
        if not bool(e[1]):
            continue
        var tc: Vector2 = a.lerp(b, float(e[0]))
        draw_circle(tc, 2.35 * u + 0.7 * u * 0.5, dk)
        draw_circle(tc, 2.35 * u - 0.35 * u, twr)
        draw_circle(tc, 1.35 * u, cap)''')
b.rep('''    var a: Vector2 = _corner(c, (HR - 1.2) * u, k)
    var b: Vector2 = _corner(c, (HR - 1.2) * u, k + 1)''', '''    var a: Vector2 = _corner(c, (HR - 2.3) * u, k)
    var b: Vector2 = _corner(c, (HR - 2.3) * u, k + 1)''')
b.save()

m = F(P + '/scripts/ui/main.gd')
# the Robots: the market's own upgrade in the Advancements ring
m.rep('''        if g.is_robots(0) and g.is_home_castle(t):   # the Robots' home castle: add a barracks or fortress to a market; Overclock
            _robo_home_bubbles(post, R)
        else:''', '''        if g.is_robots(0) and not g.is_home_castle(t) and g.robo_next(t) != "":   # the Robots: this market's factory upgrade (2026-11-24)
            var rk: String = g.robo_next(t)
            var rc: int = g.robo_up_cost(0, rk, t)
            var can_r: bool = g.mat_of(0) >= rc
            var ri: int = sel
            _bubble(post.call(2, 210) if int(t.barracks) > 0 else post.call(1, 150), R, "res://art/buildings/%s_robots.png" % rk, "Fortress" if rk == "fort" else "Barracks", "%d|mat" % rc, can_r, false, can_r,
                func(): _do(func(): g.do_robo_up(0, ri, rk)))
        if g.is_robots(0) and g.is_home_castle(t):   # the Robots' home castle: Overclock
            _robo_home_bubbles(post, R)
        elif g.is_robots(0) and int(t.barracks) == 0 and g.robo_next(t) != "":
            pass   # a market: its Barracks button takes the barracks spot
        else:''')
m.rep('''func _robo_home_bubbles(post: Callable, R: float) -> void:
    for spec in [["barracks", 1, 150], ["fort", 2, 210]]:''', '''func _robo_home_bubbles(post: Callable, R: float) -> void:
    for spec in []:   # Barracks and Fortress are bought at each market since 2026-11-24''')
m.rep('''            if g.is_robots(0) and g.home_market(0):
                for k in ["barracks", "fort"]:
                    if not g.robo_up_targets(0, k).is_empty() and mats >= g.robo_up_best(0, k):
                        return "You have [b]%s[/b] and can still add a %s to one of your markets at your home castle." % [g.mat_txt(mats), "fortress" if k == "fort" else "barracks"]''',
      '''            if g.is_robots(0):
                for k in ["barracks", "fort"]:
                    if not g.robo_up_targets(0, k).is_empty() and mats >= g.robo_up_best(0, k):
                        return "You have [b]%s[/b] and can still add a %s to one of your markets (tap the market)." % [g.mat_txt(mats), "fortress" if k == "fort" else "barracks"]''')
# a castle battle: the Castle map only with a wall on the attacked side
m.rep('''    var B: Dictionary = g.tiles[int(fight.to)]
    var map: String = g.arena_map(B)''', '''    var B: Dictionary = g.tiles[int(fight.to)]
    var map: String = g.arena_map(B, g.wall_on(int(fight.to), int(fight.from)))''')
# the turn banner and the briefing
m.rep('''    _place_bubbles()
    _stats()
    _net_badge()''', '''    _place_bubbles()
    _stats()
    _net_badge()
    _turn_start_check()''')
m.rep('''## The one-time swap: first the hand card to put back, then the reserve card to take.''', '''# ---------------------------------------------------------------------
# The start of a turn (Ethan, 2026-11-24): your faction's briefing on your first turn, and a banner when a side is
# about to win
# ---------------------------------------------------------------------
var _turn_key: String = ""
var _warn_box: Control = null

const FAC_BRIEF := {
    "dinos": {"best": ["The biggest, toughest units: Triceratops, Stegosaurus and Megaraptors win straight-up fights", "The Volcano at your home castle rains lava on enemy armies", "Nesting grounds and Alamosaurus guards hold the land you take"],
        "lack": "No forts or trebuchets: you break castles with brute force.", "plan": "Build nesting grounds, grow a herd of big units, then smash through."},
    "robots": {"best": ["Economy: stack markets into resource hexes for more gold and materials", "Factories: turn a market into a barracks, then a fortress, right where you need it", "Lasers, Archers and Longbows hit hard from range, and trebuchets break walls"],
        "lack": "Each hex is one building: a resource hex or a factory, never both.", "plan": "Build markets early, make a few into factories near the front, then push with ranged units."},
    "mammals": {"best": ["Numbers and speed: cheap units that spread across the map fast", "Rhinos charge, Porcupines prick every attacker with their quills", "The Watering Hole and dens keep your army growing"],
        "lack": "Single units are weaker than the Dinosaurs' giants.", "plan": "Claim land quickly, build dens, and overwhelm your enemy with a big army."},
    "mythical": {"best": ["Magic: Mages, Life Trees and magic domes", "Minions become Minotaurs, Griffins and Dragons where a Mage stands", "Flyers: only flying units can attack your Floating Castle"],
        "lack": "No forts, markets, coins or trebuchets: everything runs on magic.", "plan": "Plant Life Trees, level up your Mages, then turn Minions into Dragons and Griffins."},
}


func _turn_start_check() -> void:
    if g == null or g.over >= 0:
        return
    var key: String = "%d:%d" % [g.turn, g.current]
    if key == _turn_key:
        return
    _turn_key = key
    if g.current == 0 and not bool(g.players[0].get("briefed", false)) and overlay == null:
        g.players[0]["briefed"] = true
        _show_briefing.call_deferred()
        return
    _show_win_warn()


func _show_briefing() -> void:
    var f: String = String(g.players[0].faction)
    if not FAC_BRIEF.has(f):
        return
    var b: Dictionary = FAC_BRIEF[f]
    var box := _open_overlay("You play the %s" % String(GameData.factions[f].name), 640.0)
    var row := HBoxContainer.new()
    row.add_theme_constant_override("separation", 16)
    box.add_child(row)
    var pic := _pic("res://art/terrain/castle_%s.png" % f, Vector2(130, 110))
    pic.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
    row.add_child(pic)
    var v := VBoxContainer.new()
    v.add_theme_constant_override("separation", 6)
    v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    row.add_child(v)
    var bb: String = "[color=#e9c66a][b]Best at[/b][/color]\\n"
    for x in b.best:
        bb += "•  %s\\n" % x
    bb += "\\n[color=#e9c66a][b]Watch out[/b][/color]\\n%s\\n\\n[color=#e9c66a][b]How to play them[/b][/color]\\n%s" % [b.lack, b.plan]
    var r := _rich(bb, 15)
    r.add_theme_color_override("default_color", PARCH)
    v.add_child(r)
    var go := _plate_button("Let's go", func(): _close_overlay(), "gold", false, 17, 20, 8)
    go.size_flags_horizontal = Control.SIZE_SHRINK_END
    box.add_child(go)


## Who is about to win: a side holding enough castles (the countdown is on), one castle short of that, or an enemy army
## next to a home castle.
func _win_warnings() -> Array:
    var out: Array = []
    var need: int = g.win_castles()
    var n3: bool = g.players.size() > 2
    if not g.siege.is_empty():
        var h: int = int(g.siege.pid)
        var L: int = int(g.siege.left)
        if h == 0:
            out.append({"mine": true, "t": "You're about to win!", "d": "You hold %d castles. Keep them through %d more %s turn%s." % [need, L, "rival" if n3 else "enemy", "" if L == 1 else "s"]})
        else:
            out.append({"mine": false, "t": "The %s are about to win!" % String(g.players[h].name), "d": "They hold %d castles.%s" % [need, "" if h == g.current else " %s %d turn%s to take one back." % ["Their rivals have" if n3 else "You have", L, "" if L == 1 else "s"]]})
    elif need > 0:
        for q in g.players:
            if not bool(q.get("out", false)) and g.win_count(int(q.id)) == need - 1:
                out.append({"mine": int(q.id) == 0, "t": "One castle from winning" if int(q.id) == 0 else "The %s are one castle from winning" % String(q.name), "d": "%s %d of %d castles." % ["You hold" if int(q.id) == 0 else "They hold", need - 1, need]})
    for q in g.players:
        if bool(q.get("out", false)):
            continue
        var hid: int = int(g.homes[int(q.id)])
        if hid < 0 or int(g.tiles[hid].owner) != int(q.id):
            continue
        for j in HexGrid.neighbors(hid):
            var e: Dictionary = g.tiles[j]
            if int(e.owner) >= 0 and int(e.owner) != int(q.id) and int(e.troops) > 0 and not bool(g.players[int(e.owner)].get("out", false)):
                var f: int = int(e.owner)
                if int(q.id) == 0:
                    out.append({"mine": false, "t": "Your home castle is under threat!", "d": "Troops from the %s are next to it. If they take it, %s." % [String(g.players[f].name), "you're out" if n3 else "they win"]})
                else:
                    out.append({"mine": true, "t": "The %s' home castle is in reach" % String(q.name), "d": "%s next to it. Take it to %s." % ["Your troops are" if f == 0 else "Troops from the %s are" % String(g.players[f].name), "knock them out" if n3 else "win"]})
                break
    return out


func _show_win_warn() -> void:
    if is_instance_valid(_warn_box):
        _warn_box.queue_free()
    var w: Array = _win_warnings()
    if w.is_empty():
        return
    var box := VBoxContainer.new()
    box.add_theme_constant_override("separation", 8)
    box.mouse_filter = Control.MOUSE_FILTER_STOP
    for x in w.slice(0, 3):
        var p := PanelContainer.new()
        var sb := StyleBoxFlat.new()
        sb.bg_color = Color(0.11, 0.075, 0.04, 0.95)
        sb.border_color = Color("c0392b") if not x.mine else Color("b8893a")
        sb.set_border_width_all(2)
        sb.set_corner_radius_all(6)
        sb.set_content_margin_all(10)
        sb.shadow_color = Color(0, 0, 0, 0.6)
        sb.shadow_size = 10
        p.add_theme_stylebox_override("panel", sb)
        p.custom_minimum_size.x = minf(560.0, get_viewport_rect().size.x - 40.0)
        var r := _rich("[center][font_size=19][color=%s][b]%s%s[/b][/color][/font_size]\\n%s[/center]" % ["#f3cf6b" if x.mine else "#ff8a70", "♛ " if x.mine else "⚠ ", x.t, x.d], 14)
        r.add_theme_color_override("default_color", Color("f0dcaa"))
        p.add_child(r)
        box.add_child(p)
    add_child(box)
    box.reset_size()
    var bw: float = board.size.x if board != null else get_viewport_rect().size.x
    box.position = Vector2((bw - box.size.x) * 0.5, 14.0)
    box.gui_input.connect(func(ev): if ev is InputEventMouseButton and ev.pressed: box.queue_free())
    _warn_box = box
    box.modulate.a = 0.0
    var tw := create_tween()
    tw.tween_property(box, "modulate:a", 1.0, 0.4)
    tw.tween_interval(5.5)
    tw.tween_property(box, "modulate:a", 0.0, 0.6)
    tw.tween_callback(func(): if is_instance_valid(box): box.queue_free())


## The one-time swap: first the hand card to put back, then the reserve card to take.''')
m.save()
print('ok')

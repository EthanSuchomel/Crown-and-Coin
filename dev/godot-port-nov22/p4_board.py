"""Browser commits 020caa9, c6bcdf1, af8e723, 3a7f62e, 3c61a0b, be7d358, 27c49e0 (Ethan, 2026-11-22) in Godot:
- the map is the background: a full-screen layer behind the cards column, so zooming fills the whole screen;
  zoom with the mouse wheel, a trackpad pinch or two fingers, drag to look round a zoomed map (a drag isn't a tap);
- no frame round the map, a plain black background;
- your numbers box never hides the map: it goes in the clearest corner, or room is made beside the board (right or
  below); a × hides it, leaving a small coin button that brings it back (remembered: settings player/stats_hidden);
- the cards column's header is just the buttons (Full, ?, Log, New);
- on the other side's turn the cards go away and the map grows (at most ~20%) in a smooth half-second slide; the
  buttons float top-right in a column;
- the random 2-player board is framed to its hexes; home castles get no grass patch under their own ground.
Usage: python3 p4_board.py PROJ"""
import sys, re
from common import F, T
P = sys.argv[1]

# ---------------------------------------------------------------- board_view.gd
f = F(P + '/scripts/ui/board_view.gd')
f.rep('''signal hex_clicked(i: int)''', '''signal hex_clicked(i: int)
signal view_changed   # the board moved or zoomed (the buttons round a hex follow it)''')
f.rep('''var _tex: Dictionary = {}''', '''# The view (Ethan, 2026-11-22): main.gd fits the board into the space beside the cards (base_s, base_o: board units to
# screen); on top of that the player's zoom zk (1..Z_MAX) and pan zpan. The board control fills the whole screen.
const Z_MAX := 4.0
var base_s: float = 0.0
var base_o: Vector2 = Vector2.ZERO
var zk: float = 1.0
var zpan: Vector2 = Vector2.ZERO
var _press_at: Vector2 = Vector2(-1, -1)
var _dragging: bool = false
var _pinched: bool = false
var _touches: Dictionary = {}
var _pinch_d: float = 0.0
var _pinch_c: Vector2 = Vector2.ZERO

var _tex: Dictionary = {}''', raw=True)
f.rep('''func _scale() -> float:
    var f := _frame_rect()
    return minf(size.x / f.size.x, size.y / f.size.y)


func _offset() -> Vector2:
    var f := _frame_rect()
    return (size - f.size * _scale()) / 2.0 - f.position * _scale()''', '''## [scale, offset] fitting the board's hexes into rect r (screen pixels), the scale capped at cap when cap > 0.
func fit_view(r: Rect2, cap: float = 0.0) -> Array:
    var f := _frame_rect()
    var s: float = maxf(0.01, minf(r.size.x / f.size.x, r.size.y / f.size.y))
    if cap > 0.0:
        s = minf(s, cap)
    return [s, r.position + (r.size - f.size * s) / 2.0 - f.position * s]


## The unzoomed view, from main.gd's layout.
func set_base(s: float, o: Vector2) -> void:
    base_s = s
    base_o = o
    _clamp_pan()
    queue_redraw()
    view_changed.emit()


func _base() -> Array:
    if base_s > 0.0:
        return [base_s, base_o]
    return fit_view(Rect2(Vector2.ZERO, size))


func _scale() -> float:
    return float(_base()[0]) * zk


func _offset() -> Vector2:
    return Vector2(_base()[1]) * zk + zpan


## Zoom by factor fz keeping screen point q still (wheel, pinch); back at 1 the board returns to its place.
func zoom_at(q: Vector2, fz: float) -> void:
    var k2: float = clampf(zk * fz, 1.0, Z_MAX)
    if is_equal_approx(k2, zk):
        return
    zpan = q - (q - zpan) * (k2 / zk)
    zk = k2
    _clamp_pan()
    queue_redraw()
    view_changed.emit()


## Keep the middle of the unzoomed board on the zoomed board, so it can't be dragged away.
func _clamp_pan() -> void:
    if zk <= 1.0001:
        zk = 1.0
        zpan = Vector2.ZERO
        return
    var b: Array = _base()
    var f := _frame_rect()
    var r0 := Rect2(Vector2(b[1]) + f.position * float(b[0]), f.size * float(b[0]))
    var c0: Vector2 = r0.get_center()
    zpan.x = clampf(zpan.x, c0.x - r0.end.x * zk, c0.x - r0.position.x * zk)
    zpan.y = clampf(zpan.y, c0.y - r0.end.y * zk, c0.y - r0.position.y * zk)


## Each hex's bounding box on screen for a view [s, o] (to find a corner clear of the map).
func hex_rects(s: float, o: Vector2) -> Array:
    var out: Array = []
    if game == null:
        return out
    for t in game.tiles:
        if t.terrain == "void":
            continue
        var c: Vector2 = o + _grid_pos(int(t.id)) * s
        out.append(Rect2(c - Vector2(_hh / 2.0, HR) * s, Vector2(_hh, 2.0 * HR) * s))
    return out''')
f.rep('''func _gui_input(event: InputEvent) -> void:
    if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
        var i: int = hex_at(event.position)
        if i >= 0:
            hex_clicked.emit(i)
            accept_event()''', '''## A tap picks a hex (on release, if it wasn't a drag or a pinch); the wheel and pinches zoom; a drag pans a zoomed map.
func _gui_input(event: InputEvent) -> void:
    if event is InputEventMouseButton:
        if event.pressed and (event.button_index == MOUSE_BUTTON_WHEEL_UP or event.button_index == MOUSE_BUTTON_WHEEL_DOWN):
            var fz: float = exp(0.18 * (event.factor if event.factor > 0.0 else 1.0))
            zoom_at(event.position, fz if event.button_index == MOUSE_BUTTON_WHEEL_UP else 1.0 / fz)
            accept_event()
        elif event.button_index == MOUSE_BUTTON_LEFT:
            if event.pressed:
                _press_at = event.position
                _dragging = false
                _pinched = _touches.size() >= 2
            else:
                if _press_at.x >= 0.0 and not _dragging and not _pinched:
                    var i: int = hex_at(event.position)
                    if i >= 0:
                        hex_clicked.emit(i)
                _press_at = Vector2(-1, -1)
                _dragging = false
            accept_event()
    elif event is InputEventMouseMotion:
        if _press_at.x >= 0.0 and (event.button_mask & MOUSE_BUTTON_MASK_LEFT) and _touches.size() < 2:
            if not _dragging and event.position.distance_to(_press_at) > 7.0:
                _dragging = true
            if _dragging and zk > 1.0:
                zpan += event.relative
                _clamp_pan()
                queue_redraw()
                view_changed.emit()
            accept_event()
    elif event is InputEventMagnifyGesture:
        zoom_at(event.position, event.factor)
        accept_event()
    elif event is InputEventPanGesture:   # two-finger scroll on a trackpad zooms, like the browser's wheel
        zoom_at(event.position, exp(-event.delta.y * 0.08))
        accept_event()
    elif event is InputEventScreenTouch:
        if event.pressed:
            _touches[event.index] = event.position
        else:
            _touches.erase(event.index)
        if _touches.size() == 2:
            var ps: Array = _touches.values()
            _pinch_d = Vector2(ps[0]).distance_to(ps[1])
            _pinch_c = (Vector2(ps[0]) + Vector2(ps[1])) / 2.0
            _pinched = true
    elif event is InputEventScreenDrag:
        _touches[event.index] = event.position
        if _touches.size() == 2:
            var ps2: Array = _touches.values()
            var d: float = Vector2(ps2[0]).distance_to(ps2[1])
            var c: Vector2 = (Vector2(ps2[0]) + Vector2(ps2[1])) / 2.0
            if _pinch_d > 1.0:
                zoom_at(c, d / _pinch_d)
                zpan += c - _pinch_c
                _clamp_pan()
                queue_redraw()
                view_changed.emit()
            _pinch_d = d
            _pinch_c = c
            _pinched = true''')
# the random 2-player board framed to its hexes, like the others
f.rep('''    _frame_n = HexGrid.shape_id
    if N == 8 and not HexGrid.custom:
        _frame = Rect2(0, 0, _grid_h(), _grid_w())
        return _frame
''', '''    _frame_n = HexGrid.shape_id
''')
f.rep('''## The part of the board that is drawn, in board units: the whole grid on the 2-player board; on the 3-player hexagon
## just its hexes (its grid corners are empty).''', '''## The part of the board that is drawn, in board units: just its hexes (on every board since 2026-11-22: the random
## 2-player board was framed to its whole grid before).''')
# no grass patch under a castle's own ground (it stuck out as a green fringe)
f.rep('''                if pass_n == 0:
                    _draw_rect_tex(tex("hex_grass_%d_soft" % ((((i0 + 5) * 2654435761 & 0xFFFFFFFF) >> 7) % 3)), rr)''', '''                if pass_n == 0:
                    if _castle_gnd(t) == "":   # not under a castle's own ground: it would show as a green fringe (2026-11-22)
                        _draw_rect_tex(tex("hex_grass_%d_soft" % ((((i0 + 5) * 2654435761 & 0xFFFFFFFF) >> 7) % 3)), rr)''')
f.rep('''        var k: String = "m" if t.terrain == "mountain" else ("w" if t.terrain == "water" else ("f" if _whole_tile(t) == "hex_forest" else "g"))''',
      '''        var k: String = "m" if t.terrain == "mountain" else ("w" if t.terrain == "water" else ("f" if _whole_tile(t) == "hex_forest" else ("c" if _castle_gnd(t) != "" else "g")))''')
f.save()

f = F(P + '/scripts/ui/terrain_bake.gd')
f.rep('''            var g: Texture2D = board.tex("hex_grass_%d_soft" % ((((i + 5) * 2654435761 & 0xFFFFFFFF) >> 7) % 3))
            if g != null:''', '''            var g: Texture2D = board.tex("hex_grass_%d_soft" % ((((i + 5) * 2654435761 & 0xFFFFFFFF) >> 7) % 3))
            if g != null and board._castle_gnd(t) == "":   # no grass patch under a castle's own ground (2026-11-22)''')
f.save()

# ---------------------------------------------------------------- main.gd
f = F(P + '/scripts/ui/main.gd')
f.rep('''var stats_row: VBoxContainer = null   # your numbers, in the board's bottom-left corner''', '''var stats_row: VBoxContainer = null   # your numbers, in the clearest corner beside the map
var stats_panel: PanelContainer = null
var stats_hidden: bool = false        # closed with its ×: just a coin button (remembered)
var float_btns: VBoxContainer = null  # Full, ?, Log, New stacked top-right while the other side plays
var solo_t: float = 0.0               # 0: the cards are out; 1: the other side's turn, the map grown (eased between)
var _solo_goal: int = -1
var _solo_tw: Tween = null
var bub_area: Rect2 = Rect2()          # where the buttons round a hex may go (the map's part of the screen)''', raw=True)
f.rep('''        pref_opps = Array(cfg.get_value("player", "opponents3", []))''', '''        pref_opps = Array(cfg.get_value("player", "opponents3", []))
        stats_hidden = bool(cfg.get_value("player", "stats_hidden", false))''')

# the game screen
a = f.s.index(T('    var margin := MarginContainer.new()\n'), f.s.index('func start_game('))
b = f.s.index(T('    side = right\n'), a) + len(T('    side = right\n'))
f.s = f.s[:a] + T('''    # the map is the background (Ethan, 2026-11-22): it fills the screen behind the cards, so zooming fills it all
    var black := ColorRect.new()
    black.color = Color.BLACK
    black.set_anchors_preset(Control.PRESET_FULL_RECT)
    black.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(black)
    board = BoardView.new()
    board.game = g
    board.set_anchors_preset(Control.PRESET_FULL_RECT)
    board.hex_clicked.connect(_on_hex)
    board.view_changed.connect(func(): _place_bubbles())
    add_child(board)
    bubbles = BubbleLayer.new()
    bubbles.set_anchors_preset(Control.PRESET_FULL_RECT)
    bubbles.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(bubbles)
    hexinfo = PanelContainer.new()
    hexinfo.position = Vector2(8, 8)
    hexinfo.custom_minimum_size = Vector2(230, 0)
    hexinfo.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(hexinfo)
    hexinfo.minimum_size_changed.connect(func(): hexinfo.reset_size.call_deferred())   # shrinks back to its lines
    # your numbers: placed by _layout_board in the corner clearest of the map
    stats_panel = PanelContainer.new()
    stats_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(stats_panel)
    stats_row = VBoxContainer.new()
    stats_row.add_theme_constant_override("separation", 0)
    stats_row.mouse_filter = Control.MOUSE_FILTER_IGNORE
    stats_panel.add_child(stats_row)
    stats_panel.minimum_size_changed.connect(func(): _layout_board.call_deferred())
    # right: the cards column, over the map
    var margin := MarginContainer.new()
    margin.set_anchors_preset(Control.PRESET_FULL_RECT)
    margin.mouse_filter = Control.MOUSE_FILTER_IGNORE
    for m in ["margin_left", "margin_right", "margin_top", "margin_bottom"]:
        margin.add_theme_constant_override(m, 10)
    add_child(margin)
    var row := HBoxContainer.new()
    row.add_theme_constant_override("separation", 12)
    row.mouse_filter = Control.MOUSE_FILTER_IGNORE
    margin.add_child(row)
    var left := Control.new()   # the map's share of the screen (the map itself is the layer behind)
    left.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    left.size_flags_stretch_ratio = 66.0
    left.mouse_filter = Control.MOUSE_FILTER_IGNORE
    row.add_child(left)
    var right := VBoxContainer.new()
    right.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    right.size_flags_stretch_ratio = 34.0
    right.custom_minimum_size.x = 330
    right.mouse_filter = Control.MOUSE_FILTER_IGNORE
    row.add_child(right)
    side = right
    # the other side's turn: the buttons float top-right, stacked
    float_btns = VBoxContainer.new()
    float_btns.add_theme_constant_override("separation", 6)
    float_btns.set_anchors_preset(Control.PRESET_TOP_RIGHT)
    float_btns.grow_horizontal = Control.GROW_DIRECTION_BEGIN
    float_btns.position = Vector2(-10, 10)
    float_btns.offset_left = -70
    float_btns.offset_right = -10
    float_btns.offset_top = 10
    float_btns.mouse_filter = Control.MOUSE_FILTER_IGNORE
    float_btns.visible = false
    add_child(float_btns)
    _solo_goal = -1
    solo_t = 0.0
    if not resized.is_connected(_on_resized):
        resized.connect(_on_resized)
''') + f.s[b:]

# refresh: the turn-change slide and the layout
f.rep('''    _place_bubbles()
    _stats()
    _hex_info()
    for c in side.get_children():
        c.queue_free()
    _side_head()
    var body := VBoxContainer.new()
    body.size_flags_vertical = Control.SIZE_EXPAND_FILL''', '''    _place_bubbles()
    _stats()
    _hex_info()
    for c in side.get_children():
        c.queue_free()
    _side_head()
    _set_solo()
    _layout_board.call_deferred()
    var body := VBoxContainer.new()
    body.size_flags_vertical = Control.SIZE_EXPAND_FILL
    body.mouse_filter = Control.MOUSE_FILTER_IGNORE''')

# the numbers box: a × to close it, a coin button to bring it back
a = f.s.index(T('func _stats() -> void:\n'))
b = f.s.index(T('func _stat_line(bb: String, size_px: int = 13) -> void:\n'))
old = f.s[a:b]
old = old.replace(T('''    for c in stats_row.get_children():
        c.queue_free()
'''), T('''    for c in stats_row.get_children():
        stats_row.remove_child(c)
        c.queue_free()
    stats_panel.add_theme_stylebox_override("panel", _stats_box())
    if stats_hidden:   # just a coin: tap it to show your numbers again
        var ob := TextureButton.new()
        ob.texture_normal = load("res://art/ui/magic.png" if g.is_myth(0) else "res://art/ui/coin.png")
        ob.ignore_texture_size = true
        ob.stretch_mode = TextureButton.STRETCH_KEEP_ASPECT_CENTERED
        ob.custom_minimum_size = Vector2(26, 26)
        ob.tooltip_text = "Show your numbers (coins, units, materials, castles)"
        ob.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
        ob.pressed.connect(func(): _stats_hide(false))
        stats_row.add_child(ob)
        return
'''))
old = old.replace(T('''    _stat_line("[color=#efc15a][b]+%d[/b][/color] %s / turn" % [int(g.income_of(0).total), word])
'''), T('''    _stat_line("[color=#efc15a][b]+%d[/b][/color] %s / turn" % [int(g.income_of(0).total), word])
    var first: Control = stats_row.get_child(stats_row.get_child_count() - 1)   # the first line gets the ×
    stats_row.remove_child(first)
    var top := HBoxContainer.new()
    top.mouse_filter = Control.MOUSE_FILTER_IGNORE
    top.add_child(first)
    var x := Button.new()
    x.text = "×"
    x.flat = true
    x.focus_mode = Control.FOCUS_NONE
    x.tooltip_text = "Hide your numbers"
    x.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
    x.add_theme_font_size_override("font_size", 16)
    x.add_theme_color_override("font_color", LICHEN)
    x.add_theme_color_override("font_hover_color", BONE)
    var xs := StyleBoxEmpty.new()
    xs.content_margin_left = 6
    xs.content_margin_right = 0
    for st in ["normal", "hover", "pressed", "focus"]:
        x.add_theme_stylebox_override(st, xs)
    x.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
    x.pressed.connect(func(): _stats_hide(true))
    top.add_child(x)
    stats_row.add_child(top)
'''))
f.s = f.s[:a] + old + T('''func _stats_hide(h: bool) -> void:
    stats_hidden = h
    _save_pref("stats_hidden", h)
    _stats()
    _layout_board.call_deferred()


func _stats_box() -> StyleBox:
    if stats_hidden:
        var sb := StyleBoxFlat.new()
        sb.bg_color = Color(0.118, 0.094, 0.067, 0.92)
        sb.border_color = EDGE
        sb.set_border_width_all(2)
        sb.set_corner_radius_all(18)
        sb.set_content_margin_all(4)
        sb.shadow_color = Color(0, 0, 0, 0.5)
        sb.shadow_size = 4
        return sb
    var p := _iron_panel(0)
    p.content_margin_left = 9
    p.content_margin_right = 6
    p.content_margin_top = 4
    p.content_margin_bottom = 6
    return p


''') + f.s[b:]

# the header: just the buttons
a = f.s.index(T('func _side_head() -> void:\n'))
b = f.s.index(T('func _small_button_box() -> StyleBox:\n'))
f.s = f.s[:a] + T('''## The cards column's header: just the buttons (Ethan, 2026-11-22); while the other side plays they float top-right.
func _side_head() -> void:
    var vb := VBoxContainer.new()
    vb.add_theme_constant_override("separation", 6)
    vb.mouse_filter = Control.MOUSE_FILTER_IGNORE
    side.add_child(vb)
    var top := HBoxContainer.new()
    top.alignment = BoxContainer.ALIGNMENT_END
    top.add_theme_constant_override("separation", 6)
    top.mouse_filter = Control.MOUSE_FILTER_IGNORE
    vb.add_child(top)
    for b in _head_buttons():
        top.add_child(b)
    if float_btns != null:
        for c in float_btns.get_children():
            float_btns.remove_child(c)
            c.queue_free()
        for b in _head_buttons():
            b.custom_minimum_size.x = 60
            float_btns.add_child(b)
    var to_win: int = g.win_castles()
    if not g.siege.is_empty():
        var mine: bool = int(g.siege.pid) == 0
        var txt: String = ("You hold %d " + ("" if g.home_counts() else "captured ") + "castles! Keep them for %d more enemy turns to win." if mine else ("The %s hold %%d " % String(g.players[int(g.siege.pid)].name)) + ("" if g.home_counts() else "captured ") + "castles! Take one back within %d turns.") % [to_win, int(g.siege.left)]
        var sb := _box(NIGHT, GOLD if mine else Color("e0574c"), 2, 6)
        var sp := PanelContainer.new()
        sp.add_theme_stylebox_override("panel", sb)
        sp.add_child(_label(txt, 13, GOLD if mine else RED))
        vb.add_child(sp)


func _head_buttons() -> Array:
    var out: Array = []
    for spec in [["Full", func(): _toggle_full()], ["?", func(): _open_help()], ["Log", func(): _open_log()], ["New", func(): show_title()]]:
        var b := _button(spec[0], spec[1])
        b.add_theme_font_size_override("font_size", 13)
        b.add_theme_stylebox_override("normal", _small_button_box())
        b.focus_mode = Control.FOCUS_NONE
        out.append(b)
    return out


# =====================================================================
# The map's place on the screen
# =====================================================================

func _on_resized() -> void:
    _layout_board.call_deferred()


## Not your turn: the cards go and the map grows, in a smooth half-second slide (Ethan, 2026-11-22: "a nice smooth
## transition instead of an aggressive switch"); your turn: back again.
func _set_solo() -> void:
    if g == null or side == null or float_btns == null:
        return
    var goal: int = 1 if (g.over < 0 and g.current != 0) else 0
    if goal == _solo_goal:
        return
    var first: bool = _solo_goal < 0
    _solo_goal = goal
    if _solo_tw != null and _solo_tw.is_valid():
        _solo_tw.kill()
    float_btns.visible = goal == 1
    if first:
        solo_t = float(goal)
        side.visible = goal == 0
        side.modulate.a = 1.0 - goal
        return
    side.visible = true
    _solo_tw = create_tween().set_parallel(true)
    _solo_tw.tween_method(_solo_step, solo_t, float(goal), 0.52).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN_OUT)
    _solo_tw.tween_property(side, "modulate:a", 1.0 - goal, 0.3 if goal == 1 else 0.45)
    if goal == 1:
        _solo_tw.chain().tween_callback(func(): side.visible = _solo_goal == 0)


func _solo_step(v: float) -> void:
    solo_t = v
    _layout_board()


## Fits the map into its part of the screen and puts your numbers in the corner clearest of it; between the two
## layouts (cards out, cards away) while the turn changes.
func _layout_board() -> void:
    if g == null or not is_instance_valid(board) or not board.is_inside_tree() or not is_instance_valid(stats_panel):
        return
    var L: Dictionary = _layout_for(false)
    if solo_t > 0.0:
        var L1: Dictionary = _layout_for(true, float(L.s) * 1.2)   # the map grows at most ~20%
        var e: float = solo_t
        L = {"s": lerpf(float(L.s), float(L1.s), e), "o": Vector2(L.o).lerp(L1.o, e), "sp": Vector2(L.sp).lerp(L1.sp, e), "area": L1.area if e >= 0.5 else L.area}
    stats_panel.size = stats_panel.get_combined_minimum_size()
    stats_panel.position = Vector2(L.sp).round()
    bub_area = L.area
    hexinfo.position = Rect2(L.area).position + Vector2(8, 8)
    board.set_base(float(L.s), L.o)


## One layout: the map's scale and offset, and where the numbers box goes. solo: the other side's turn.
func _layout_for(solo: bool, cap: float = 0.0) -> Dictionary:
    var vw: Vector2 = size
    var M: float = 10.0
    var area: Rect2
    var fit: Rect2
    if solo:
        area = Rect2(Vector2.ZERO, vw)
        fit = Rect2(M, M, vw.x - 2.0 * M - 70.0, vw.y - 2.0 * M)   # room on the right for the floating buttons
    else:
        var avail: float = vw.x - 2.0 * M - 12.0
        var lw: float = avail - maxf(330.0, avail * 0.34)
        area = Rect2(0, 0, M + lw, vw.y)
        fit = Rect2(M, M, lw, vw.y - 2.0 * M)
    var bs: Vector2 = stats_panel.get_combined_minimum_size()
    var inner: Rect2 = area.grow(-6.0)
    var spots: Array = [inner.end - bs, Vector2(inner.position.x, inner.end.y - bs.y)]
    if not solo:
        spots.append(Vector2(inner.end.x - bs.x, inner.position.y))
    spots.append(inner.position)
    var v: Array = board.fit_view(fit, cap)
    var m: Dictionary = _stats_spot(v, spots, bs)
    if float(m.frac) > 0.005 and not stats_hidden:   # every corner would hide hexes: make room beside the board, right or below
        var v1: Array = board.fit_view(Rect2(fit.position, fit.size - Vector2(bs.x + 6.0, 0)), cap)
        var m1: Dictionary = _stats_spot(v1, spots, bs)
        var v2: Array = board.fit_view(Rect2(fit.position, fit.size - Vector2(0, bs.y + 6.0)), cap)
        var m2: Dictionary = _stats_spot(v2, spots, bs)
        if float(m1.frac) < float(m2.frac) - 0.01 or (absf(float(m1.frac) - float(m2.frac)) <= 0.01 and float(v1[0]) > float(v2[0])):
            v = v1
            m = m1
        else:
            v = v2
            m = m2
    return {"s": float(v[0]), "o": Vector2(v[1]), "sp": Vector2(m.pos), "area": area}


## The corner where the box hides the least of the map (in order: bottom-right, bottom-left, top-right, top-left).
func _stats_spot(v: Array, spots: Array, bs: Vector2) -> Dictionary:
    var rects: Array = board.hex_rects(float(v[0]), Vector2(v[1]))
    var best: Vector2 = spots[0]
    var bv: float = INF
    for sp in spots:
        var box := Rect2(sp, bs)
        var cover: float = 0.0
        for r in rects:
            var hit: Rect2 = box.intersection(r)
            cover += hit.get_area()
        if cover < bv - bs.x * bs.y * 0.02:
            bv = cover
            best = sp
    return {"pos": best, "frac": bv / maxf(1.0, bs.x * bs.y)}


## Where the buttons round a hex may go: inside the map's part of the screen.
func _bub_lo(r: float) -> Vector2:
    return (bub_area.position if bub_area.size.x > 0.0 else Vector2.ZERO) + Vector2(r + 2, r + 2)


func _bub_hi(r: float) -> Vector2:
    var hi: Vector2 = bub_area.end if bub_area.size.x > 0.0 else bubbles.size
    return (hi - Vector2(r + 2, r + 2)).max(_bub_lo(r))


''') + f.s[b:]
n0 = f.s.count('bubbles.size - Vector2(')
f.s = re.sub(r'\.clamp\(Vector2\((\w+) \+ 2, \1 \+ 2\), bubbles\.size - Vector2\(\1 \+ 2, \1 \+ 2\)\)', r'.clamp(_bub_lo(\1), _bub_hi(\1))', f.s)
assert f.s.count('bubbles.size - Vector2(') == 0, n0
f.rep('''    vb.add_theme_constant_override("separation", 2)
    hexinfo.add_child(vb)''', '''    vb.add_theme_constant_override("separation", 2)
    hexinfo.add_child(vb)
    hexinfo.reset_size.call_deferred()   # as small as its lines (it's no longer inside the map's frame)''')
f.rep('Tap the materials line in the map\'s bottom-right corner, or Buy materials', 'Tap the materials line in your numbers box beside the map, or Buy materials', raw=True)
f.save()
print('ok')

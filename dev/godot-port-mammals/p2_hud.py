"""Ethan's board layout (2026-11-12 sketch, browser commit d76a45a) in the Godot version: no stat tiles above the map;
a small box in the board's bottom-left corner with +X coins / turn, X units, X coins, X materials (tap to buy) and
every side's castles; the cards column's header is just the turn line and Full / ? / Log / New.
Usage: python3 p2_hud.py PROJ"""
import sys
from common import F, T
P = sys.argv[1]
f = F(P + '/scripts/ui/main.gd')

f.rep('var stats_row: HBoxContainer = null', 'var stats_row: VBoxContainer = null   # your numbers, in the board\'s bottom-left corner', raw=True)

# the game screen: no stats row over the board; the box goes in the board's corner
f.rep('''    # left: stat tiles over the framed board
    var left := VBoxContainer.new()''', '''    # left: the framed board, your numbers in its bottom-left corner
    var left := VBoxContainer.new()''')
f.rep('''    stats_row = HBoxContainer.new()
    stats_row.add_theme_constant_override("separation", 8)
    left.add_child(stats_row)
''', '')
f.rep('''    stack.add_child(bubbles)
    board.resized.connect(func(): _place_bubbles())
''', '''    stack.add_child(bubbles)
    board.resized.connect(func(): _place_bubbles())
    var sp := PanelContainer.new()
    var sbox := _box(MOSS, EDGE, 2, 6)
    sbox.border_width_left = 0
    sbox.border_width_bottom = 0
    sbox.corner_radius_top_left = 0
    sbox.corner_radius_bottom_left = 0
    sbox.corner_radius_bottom_right = 0
    sbox.content_margin_top = 4
    sbox.content_margin_bottom = 5
    sp.add_theme_stylebox_override("panel", sbox)
    sp.mouse_filter = Control.MOUSE_FILTER_IGNORE   # taps go through to the board, except on the materials line
    sp.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
    sp.grow_vertical = Control.GROW_DIRECTION_BEGIN
    stack.add_child(sp)
    stats_row = VBoxContainer.new()
    stats_row.add_theme_constant_override("separation", 0)
    stats_row.mouse_filter = Control.MOUSE_FILTER_IGNORE
    sp.add_child(stats_row)
''')

# the corner box's lines
a = f.s.index('func _stats() -> void:')
b = f.s.index('func _side_head() -> void:')
f.s = f.s[:a] + T('''func _stats() -> void:
    for c in stats_row.get_children():
        c.queue_free()
    var myth: bool = g.is_myth(0)
    var word: String = "magic" if myth else "coins"
    var units: int = 0
    for t in g.tiles:
        if int(t.owner) == 0:
            units += int(t.troops)
    _stat_line("[color=#efc15a][b]+%d[/b][/color] %s / turn" % [int(g.income_of(0).total), word])
    _stat_line("[b]%d[/b] unit%s" % [units, "" if units == 1 else "s"])
    _stat_line("%s [color=#efc15a][b]%d[/b][/color] %s" % [_img("magic" if myth else "coin", 16), int(g.players[0].gold), word])
    if g.uses_mat(0):   # materials: tap to buy more at your markets
        var m: int = g.mat_of(0)
        var mb := Button.new()
        mb.flat = true
        mb.focus_mode = Control.FOCUS_NONE
        mb.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
        mb.tooltip_text = "Materials: tap to buy more at your markets"
        mb.pressed.connect(func(): _open_trade())
        var empty := StyleBoxEmpty.new()
        for st in ["normal", "hover", "pressed", "focus"]:
            mb.add_theme_stylebox_override(st, empty)
        var r := _rich("[img=16x16]res://art/ui/mat.png[/img] [b]%d[/b] material%s" % [m, "" if m == 1 else "s"], 13)
        r.autowrap_mode = TextServer.AUTOWRAP_OFF
        r.set_anchors_preset(Control.PRESET_FULL_RECT)
        mb.add_child(r)
        mb.custom_minimum_size = Vector2(118, 19)
        stats_row.add_child(mb)
    var parts: PackedStringArray = []
    for q in g.players:
        parts.append(("[s][color=%s]%d[/color][/s]" if g.is_out(int(q.id)) else "[color=%s]%d[/color]") % [_ink(int(q.id)), g.castle_count(int(q.id))])
    var of: String = "" if g.players.size() > 2 else " [color=#a5b49e][font_size=11]of %d[/font_size][/color]" % int(GameData.rules.castles.to_win)
    _stat_line("[img=20x15]res://art/terrain/castle_neutral.png[/img] [b]%s[/b]%s" % [" – ".join(parts), of], 14)


func _stat_line(bb: String, size_px: int = 13) -> void:
    var r := _rich(bb, size_px)
    r.autowrap_mode = TextServer.AUTOWRAP_OFF
    r.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
    r.custom_minimum_size.x = 118
    stats_row.add_child(r)


''') + f.s[b:]

# the cards header: the turn line and the four buttons
a = f.s.index(T('    var top := HBoxContainer.new()\n'), f.s.index('func _side_head() -> void:'))
b = f.s.index(T('    if not g.siege.is_empty():'), a)
f.s = f.s[:a] + T('''    var top := HBoxContainer.new()
    top.add_theme_constant_override("separation", 6)
    vb.add_child(top)
    var who: String = "[color=#8db0ff]your move[/color]" if (g.current == 0 and not busy) else "[color=%s]%s'[/color] move" % [_ink(g.current), g.players[g.current].name]
    if g.over >= 0:
        who = "game over"
    var turn := _rich("[color=#a5b49e]Turn %d · %s[/color]" % [g.turn, who], 14)
    turn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    turn.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    top.add_child(turn)
    var to_win: int = int(GameData.rules.castles.to_win)
    for spec in [["Full", func(): _toggle_full()], ["?", func(): _open_help()], ["Log", func(): _open_log()], ["New", func(): show_title()]]:
        var b := _button(spec[0], spec[1])
        b.add_theme_font_size_override("font_size", 13)
        b.add_theme_stylebox_override("normal", _small_button_box())
        top.add_child(b)
''') + f.s[b:]
f.rep('Tap the materials button at the top, or Buy materials', 'Tap the materials line in the map\'s bottom-left corner, or Buy materials', raw=True)
f.save()
print('ok')

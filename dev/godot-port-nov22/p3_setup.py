"""Browser commits 46dcab5, fa62fa2, e9b7297, c1b0c9a (Ethan, 2026-11-22) in Godot: the screen before a game in three
tabs, themed like the home screen (the battle painting blurred and darkened behind it, iron tabs and plates, a bronze-
trimmed panel, Cinzel headings, a gold Start plate):
  1 You: your faction (four tiles), your colour, and "About the ..." (a pop-up with the faction's cards, units, abilities);
  2 Opponent (Rivals with 3 players): 2 or 3 players, each rival's faction and colour, and the difficulty (a pop-up);
  3 Map & rules: Random or one of the hand-made maps (each drawn as a little picture), and how to win.
The rivals' colours are remembered (settings: player/opp_colors) and used when the game starts.
Usage: python3 p3_setup.py PROJ   (art/title_battle_dim.jpg goes to art/ui/: the painting blurred 2px, darkened, vignetted)"""
import sys
from common import F, T
P = sys.argv[1]
f = F(P + '/scripts/ui/main.gd')

f.rep('''var pref_opps: Array = []   # 3 players: the two rivals' factions''', '''var pref_opps: Array = []   # 3 players: the two rivals' factions
var pref_ocol: Array = ["", ""]   # the rivals' colours ("" = their faction's usual one), remembered (Ethan, 2026-11-22)
var fs_tab: int = 0               # the setup screen's open tab: 0 You, 1 Opponent, 2 Map & rules''', raw=True)
f.rep('''        pref_opps = Array(cfg.get_value("player", "opponents3", []))''', '''        pref_opps = Array(cfg.get_value("player", "opponents3", []))
        var oc: Array = Array(cfg.get_value("player", "opp_colors", ["", ""]))
        pref_ocol = [String(oc[0]) if oc.size() > 0 else "", String(oc[1]) if oc.size() > 1 else ""]''')

# the old one-page faction screen: keep its faction details for the "About" pop-up
a = f.s.index(T('func show_factions() -> void:\n'))
b = f.s.index(T('func _volc_say(v: Dictionary) -> String:\n'))
old = f.s[a:b]
c0 = old.index(T('    body.add_child(_label("Your cards", 16, BONE, true))\n'))
c1 = old.index(T('    var foot := HBoxContainer.new()\n'))
info = old[c0:c1].replace('my_faction', 'fid')
for x, y in [('_label("Your cards", 16, BONE, true)', '_fsx_h("Your cards")'),
             ('_rich("[b]Magic, not gold[/b]", 16)', '_fsx_h("Magic, not gold")'),
             ('_rich("[b]Gold and materials[/b]", 16)', '_fsx_h("Gold and materials")'),
             ('_label("Your units", 16, BONE, true)', '_fsx_h("Your units")'),
             ('_label("Volcano and guards", 16, BONE, true)', '_fsx_h("Volcano and guards")'),
             ('_label("Factories", 16, BONE, true)', '_fsx_h("Factories")'),
             ('_label("Watering Hole", 16, BONE, true)', '_fsx_h("Watering Hole")')]:
    assert info.count(x) == 1, x
    info = info.replace(x, y)
info = info.replace('grid.add_child(_label(h, 14, BONE, true))', 'grid.add_child(_label(h, 14, PARCH, true))')

new = T('''## The screen before a game, in three tabs (Ethan, 2026-11-22): You, Opponent, Map & rules.
func show_factions() -> void:
    _clear()
    _painting("res://art/ui/title_battle_dim.jpg")
    var sides: Dictionary = _fsx_sides()
    var vw: Vector2 = get_viewport_rect().size
    var margin := MarginContainer.new()
    margin.set_anchors_preset(Control.PRESET_FULL_RECT)
    for m in ["margin_left", "margin_right"]:
        margin.add_theme_constant_override(m, 16)
    for m in ["margin_top", "margin_bottom"]:
        margin.add_theme_constant_override(m, 14)
    add_child(margin)
    var center := HBoxContainer.new()
    center.alignment = BoxContainer.ALIGNMENT_CENTER
    margin.add_child(center)
    var fsx := VBoxContainer.new()
    fsx.custom_minimum_size.x = minf(880.0, vw.x - 32.0)
    fsx.add_theme_constant_override("separation", 12)
    center.add_child(fsx)
    # the tabs
    var tabs := HBoxContainer.new()
    tabs.add_theme_constant_override("separation", 10)
    fsx.add_child(tabs)
    var names: Array = [["You", "You"], ["Opponents" if pref_np == 3 else "Opponent", "Rivals"], ["Map & rules", "Map"]]
    for i in 3:
        var k: int = i
        var tb := _plate_button("", func(): _fsx_go(k), "tab", i == fs_tab, 17, 10, 8)
        tb.size_flags_horizontal = Control.SIZE_EXPAND_FILL
        tb.custom_minimum_size.y = 46
        var hb := HBoxContainer.new()
        hb.set_anchors_preset(Control.PRESET_FULL_RECT)
        hb.alignment = BoxContainer.ALIGNMENT_CENTER
        hb.add_theme_constant_override("separation", 8)
        tb.add_child(hb)
        var on: bool = i == fs_tab
        var num := Label.new()
        num.text = str(i + 1)
        num.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
        num.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
        num.custom_minimum_size = Vector2(24, 24)
        num.size_flags_vertical = Control.SIZE_SHRINK_CENTER
        num.add_theme_font_override("font", _font_bold)
        num.add_theme_font_size_override("font_size", 13)
        var ring := StyleBoxFlat.new()
        ring.draw_center = false
        ring.set_border_width_all(2)
        ring.set_corner_radius_all(12)
        ring.border_color = Color("e9c66a") if on else Color("9c8156")
        num.add_theme_stylebox_override("normal", ring)
        num.add_theme_color_override("font_color", Color("e9c66a") if on else Color("cdbb92"))
        hb.add_child(num)
        var tl := Label.new()
        tl.text = String(names[i][0] if vw.x >= 640 else names[i][1])
        tl.add_theme_font_override("font", _font_head)
        tl.add_theme_font_size_override("font_size", 17)
        tl.add_theme_color_override("font_color", Color("f6e7bf") if on else PARCH)
        tl.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.9))
        tl.add_theme_constant_override("shadow_offset_y", 1)
        tl.size_flags_vertical = Control.SIZE_SHRINK_CENTER
        hb.add_child(tl)
        _ignore_mouse(hb)
        tabs.add_child(tb)
    # the panel
    var panel := PanelContainer.new()
    panel.add_theme_stylebox_override("panel", _plate("panel", 18, 14))
    panel.size_flags_vertical = Control.SIZE_EXPAND_FILL
    fsx.add_child(panel)
    var scroll := ScrollContainer.new()
    scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
    panel.add_child(scroll)
    var body := VBoxContainer.new()
    body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    body.add_theme_constant_override("separation", 10)
    scroll.add_child(body)
    if fs_tab == 0:
        _fsx_you(body, sides)
    elif fs_tab == 1:
        _fsx_rivals(body, sides)
    else:
        _fsx_map(body, sides)
    # the foot: Back (or Title), who plays whom, Next, Start
    var foot := HBoxContainer.new()
    foot.add_theme_constant_override("separation", 10)
    fsx.add_child(foot)
    foot.add_child(_plate_button("Back" if fs_tab > 0 else "Title", func(): _fsx_back(), "iron", false, 15, 16, 8))
    var who: Array = []
    for i in sides.facs.size():
        who.append("[color=%s][b]%s[/b][/color]" % [String(COLORS[sides.cols[i]].ink), String(GameData.factions[sides.facs[i]].name)])
    var mp: Dictionary = GameData.map_by_id(pref_map) if pref_map != "" else {}
    var map_name: String = String(mp.name) if (not mp.is_empty() and int(mp.get("players", 0)) == pref_np) else "Random map"
    var sum := _rich("%s vs %s · %s · %s" % [who[0], " and ".join(PackedStringArray(who.slice(1))), String(GameState.AI_LEVEL_NAME[pref_level]), map_name], 14)
    sum.add_theme_color_override("default_color", Color("d9c79c"))
    sum.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    foot.add_child(sum)
    if fs_tab < 2:
        foot.add_child(_plate_button("Next", func(): _fsx_go(fs_tab + 1), "iron", false, 15, 16, 8))
    var go := _plate_button("Start", func():
        _close_overlay()
        start_game(my_faction), "gold", false, 19, 22, 8)
    go.custom_minimum_size.x = 112
    foot.add_child(go)


func _fsx_back() -> void:
    if fs_tab > 0:
        _fsx_go(fs_tab - 1)
    else:
        show_title()


## Rival k (0 or 1) plays faction fid; with 3 players the other rival takes the old pick if it had fid.
func _fsx_pick_rival(k: int, fid: String) -> void:
    if pref_np == 3:
        var o: Array = GameState.three_opps(my_faction, pref_opps)
        if o[1 - k] == fid:
            o[1 - k] = o[k]
        o[k] = fid
        pref_opps = o
        _save_pref("opponents3", pref_opps)
    else:
        pref_opp = fid
        _save_pref("opponent", fid)
    show_factions()


func _fsx_rival_color(k: int, c: String) -> void:
    while pref_ocol.size() < 2:
        pref_ocol.append("")
    pref_ocol[k] = c
    _save_pref("opp_colors", pref_ocol)
    show_factions()


func _fsx_go(tab: int) -> void:
    fs_tab = clampi(tab, 0, 2)
    show_factions()


## Every side's faction and colour as the game will start them: yours wins a clash; a rival's taken pick falls back.
func _fsx_sides() -> Dictionary:
    var facs: Array = [my_faction]
    if pref_np == 3:
        facs.append_array(GameState.three_opps(my_faction, pref_opps))
    else:
        facs.append(_opponent_for(my_faction))
    var cols: Array = [_my_color_for(my_faction)]
    for i in range(1, facs.size()):
        var w: String = String(pref_ocol[i - 1]) if i - 1 < pref_ocol.size() else ""
        cols.append(w if (COLORS.has(w) and not cols.has(w)) else _other_color(cols, String(facs[i])))
    return {"facs": facs, "cols": cols}


func _save_pref(key: String, v) -> void:
    var cfg := ConfigFile.new()
    cfg.load(SETTINGS)
    cfg.set_value("player", key, v)
    cfg.save(SETTINGS)


## A heading on the setup screen: carved serif in parchment, with a small note after it.
func _fsx_l(text: String, note: String = "") -> RichTextLabel:
    var r := _rich("[font_size=18]%s[/font_size]%s" % [text, ("   [font_size=13][color=#bfae88]%s[/color][/font_size]" % note) if note != "" else ""], 18)
    r.add_theme_font_override("normal_font", _font_head)
    r.add_theme_color_override("default_color", PARCH)
    r.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.8))
    r.add_theme_constant_override("shadow_offset_y", 1)
    return r


## A heading inside the faction pop-up.
func _fsx_h(text: String) -> Label:
    var l := _label(text, 18, PARCH, true)
    l.add_theme_font_override("font", _font_head)
    return l


## A faction tile: its castle, its name in its colour and (big tiles) its tagline. on: picked.
func _fac_tile(fid: String, on: bool, big: bool, f: Callable) -> Button:
    var F: Dictionary = GameData.factions[fid]
    var b := _plate_button("", f, "tile", on, 15, 6, 6)
    b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    b.custom_minimum_size = Vector2(0, 150 if big else 96)
    var vb := VBoxContainer.new()
    vb.set_anchors_preset(Control.PRESET_FULL_RECT)
    vb.alignment = BoxContainer.ALIGNMENT_CENTER
    vb.add_theme_constant_override("separation", 2)
    b.add_child(vb)
    var pic := _pic("res://art/terrain/castle_%s.png" % fid, Vector2(96, 66) if big else Vector2(68, 46))
    pic.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
    vb.add_child(pic)
    var nm := _label(String(F.name), 17 if big else 15, Color(String(F.ink)), true)
    nm.add_theme_font_override("font", _font_head)
    nm.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.9))
    nm.add_theme_constant_override("shadow_offset_y", 1)
    nm.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    vb.add_child(nm)
    if big:
        var tg := Label.new()
        tg.text = String(F.tagline)
        tg.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
        tg.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
        tg.add_theme_font_size_override("font_size", 12)
        tg.add_theme_color_override("font_color", Color("bfae88"))
        tg.custom_minimum_size.x = 120
        vb.add_child(tg)
    _ignore_mouse(vb)
    return b


## Five round colour swatches; taken ones (another side's) can't be picked.
func _swatches(sel: String, taken: Array, pick: Callable) -> HBoxContainer:
    var row := HBoxContainer.new()
    row.add_theme_constant_override("separation", 10)
    for c in COLOR_ORDER:
        var b := Button.new()
        b.custom_minimum_size = Vector2(34, 34)
        b.size_flags_vertical = Control.SIZE_SHRINK_CENTER
        b.tooltip_text = String(COLORS[c].name)
        b.focus_mode = Control.FOCUS_NONE
        b.disabled = taken.has(c)
        for st in ["normal", "hover", "pressed", "disabled"]:
            var sb := StyleBoxFlat.new()
            sb.bg_color = Color(String(COLORS[c].color)).lightened(0.12 if st == "hover" else 0.0)
            if st == "disabled":
                sb.bg_color = Color(sb.bg_color, 0.3)
            sb.set_corner_radius_all(17)
            sb.set_border_width_all(3 if c == sel else 2)
            sb.border_color = PARCH if c == sel else Color("6b4d1c")
            sb.expand_margin_left = 2 if c == sel else 0
            sb.expand_margin_right = 2 if c == sel else 0
            sb.expand_margin_top = 2 if c == sel else 0
            sb.expand_margin_bottom = 2 if c == sel else 0
            b.add_theme_stylebox_override(st, sb)
        b.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
        var cc: String = c
        b.pressed.connect(func(): pick.call(cc))
        row.add_child(b)
    var n := _label(String(COLORS[sel].name) if COLORS.has(sel) else "", 15, Color("f0dcaa"), true)
    n.add_theme_font_override("font", _font_head)
    n.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    row.add_child(n)
    return row


## A wide plate with a round gold mark and a line of text: "About the ...", "Difficulty: ...".
func _fsx_more(mark: String, bb: String, f: Callable) -> Button:
    var b := _plate_button("", f, "iron", false, 15, 12, 8)
    b.custom_minimum_size.y = 46
    var hb := HBoxContainer.new()
    hb.set_anchors_preset(Control.PRESET_FULL_RECT)
    hb.add_theme_constant_override("separation", 10)
    b.add_child(hb)
    var pad := Control.new()
    pad.custom_minimum_size.x = 4
    hb.add_child(pad)
    var ic := Label.new()
    ic.text = mark
    ic.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    ic.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    ic.custom_minimum_size = Vector2(24, 24)
    ic.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    ic.add_theme_font_override("font", _font_bold)
    ic.add_theme_font_size_override("font_size", 14)
    ic.add_theme_color_override("font_color", Color("2a1805"))
    var dot := StyleBoxFlat.new()
    dot.bg_color = Color("e8c060")
    dot.set_corner_radius_all(12)
    dot.border_color = IRON_RING
    dot.set_border_width_all(1)
    ic.add_theme_stylebox_override("normal", dot)
    hb.add_child(ic)
    var r := _rich(bb, 16)
    r.add_theme_font_override("bold_font", _font_head)
    r.add_theme_color_override("default_color", PARCH)
    r.autowrap_mode = TextServer.AUTOWRAP_OFF
    r.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    hb.add_child(r)
    _ignore_mouse(hb)
    return b


func _fsx_you(body: VBoxContainer, sides: Dictionary) -> void:
    body.add_child(_fsx_l("Your faction"))
    var facs := HBoxContainer.new()
    facs.add_theme_constant_override("separation", 10)
    body.add_child(facs)
    for fid in GameData.factions.order:
        var ff: String = fid
        facs.add_child(_fac_tile(fid, fid == my_faction, true, func():
            my_faction = ff
            show_factions()))
    body.add_child(_fsx_l("Your color"))
    body.add_child(_swatches(String(sides.cols[0]), [], func(c):
        _set_pref_color(c)
        show_factions()))
    var gap := Control.new()
    gap.custom_minimum_size.y = 4
    body.add_child(gap)
    body.add_child(_fsx_more("i", "About the [b]%s[/b]   [font_size=13][color=#bfae88]cards, units, abilities[/color][/font_size]" % String(GameData.factions[my_faction].name), func(): _fsx_info()))


func _fsx_rivals(body: VBoxContainer, sides: Dictionary) -> void:
    var np_row := HBoxContainer.new()
    np_row.add_theme_constant_override("separation", 8)
    body.add_child(np_row)
    var pl := _fsx_l("Players")
    pl.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
    pl.autowrap_mode = TextServer.AUTOWRAP_OFF
    pl.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    np_row.add_child(pl)
    for n in [2, 3]:
        var nn: int = n
        var nb := _plate_button(str(n), func():
            pref_np = nn
            _save_pref("players", nn)
            show_factions(), "tab", n == pref_np, 16, 14, 4)
        nb.custom_minimum_size = Vector2(44, 34)
        np_row.add_child(nb)
    var hint := _label("You and two rivals" if pref_np == 3 else "You and one opponent", 14, Color("bfae88"))
    hint.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    np_row.add_child(hint)
    var rivals: Array = sides.facs.slice(1)
    for k in rivals.size():
        var kk: int = k
        var box := PanelContainer.new()
        var sb := StyleBoxFlat.new()
        sb.bg_color = Color(0.047, 0.035, 0.024, 0.6)
        sb.border_color = Color("6b4d1c")
        sb.set_border_width_all(1)
        sb.set_corner_radius_all(4)
        sb.set_content_margin_all(12)
        box.add_theme_stylebox_override("panel", sb)
        body.add_child(box)
        var vb := VBoxContainer.new()
        vb.add_theme_constant_override("separation", 8)
        box.add_child(vb)
        vb.add_child(_fsx_l(("Rival %d" % (k + 1)) if pref_np == 3 else "Opponent", "played by the computer"))
        var row := HBoxContainer.new()
        row.add_theme_constant_override("separation", 10)
        vb.add_child(row)
        for fid in GameData.factions.order:
            if fid == my_faction:
                continue
            var ff: String = fid
            row.add_child(_fac_tile(fid, fid == rivals[k], false, func(): _fsx_pick_rival(kk, ff)))
        var others: Array = []
        for i in sides.cols.size():
            if i != k + 1:
                others.append(sides.cols[i])
        vb.add_child(_swatches(String(sides.cols[k + 1]), others, func(c): _fsx_rival_color(kk, c)))
    body.add_child(_fsx_more("!", "Difficulty: [b]%s[/b]   [font_size=13][color=#bfae88]%s[/color][/font_size]" % [String(GameState.AI_LEVEL_NAME[pref_level]), String(GameState.AI_LEVEL_NOTE[pref_level])], func(): _fsx_level()))


## A little picture of a hand-made map, drawn the way the board shows it (the browser's mapThumb).
class MapThumb extends Control:
    var rows: Array = []
    var coins: Array = []
    var cols: Array = []   # the sides' colours, for the home castles 1, 2, 3
    func _draw() -> void:
        var rt: float = sqrt(3.0)
        var fill: Dictionary = {"g": Color("3f7a3a"), "f": Color("1f4a26"), "m": Color("8f8a7e"), "w": Color("1f5a6e"), "c": Color("cfc8b4")}
        var hexes: Array = []
        var lo := Vector2(INF, INF)
        var hi := Vector2(-INF, -INF)
        for r in rows.size():
            var row: String = rows[r]
            for c in row.length():
                var ch: String = row[c]
                if ch == "x":
                    continue
                var gx: float = c * 1.5
                var gy: float = r * rt + (c & 1) * rt / 2.0
                var ctr := Vector2(-gy, -gx)
                var pts := PackedVector2Array()
                for k in 6:
                    var a: float = k * PI / 3.0
                    var v := Vector2(-(gy + sin(a) * 0.96), -(gx + cos(a) * 0.96))
                    pts.append(v)
                    lo = lo.min(v)
                    hi = hi.max(v)
                hexes.append([ch, ctr, pts])
        if hexes.is_empty():
            return
        lo -= Vector2(0.3, 0.3)
        hi += Vector2(0.3, 0.3)
        var s: float = minf(size.x / (hi.x - lo.x), size.y / (hi.y - lo.y))
        var off: Vector2 = (size - (hi - lo) * s) / 2.0 - lo * s
        for h in hexes:
            var ch: String = h[0]
            var home: String = ""
            if "123".contains(ch) and int(ch) - 1 < cols.size():
                home = String(cols[int(ch) - 1])
            var col: Color = fill.get(ch, fill.g)
            if home != "":
                col = Color(home)
            var pts := PackedVector2Array()
            for v in h[2]:
                pts.append(off + v * s)
            draw_colored_polygon(pts, col)
            if ch == "c" or home != "":
                var p: Vector2 = off + h[1] * s
                var q: float = 0.42 * s
                draw_rect(Rect2(p - Vector2(q, q), Vector2(2 * q, 2 * q)), Color(1, 1, 1, 0.9) if home != "" else Color(Color("5b5547"), 0.8))
        for rc in coins:
            var r2: int = int(rc[0])
            var c2: int = int(rc[1])
            if r2 >= rows.size() or c2 >= String(rows[r2]).length() or String(rows[r2])[c2] != "g":
                continue
            var p2: Vector2 = off + Vector2(-(r2 * rt + (c2 & 1) * rt / 2.0), -(c2 * 1.5)) * s
            draw_circle(p2, 0.3 * s, Color("efc15a"))


func _fsx_map(body: VBoxContainer, sides: Dictionary) -> void:
    body.add_child(_fsx_l("Map", "%d players" % pref_np))
    var list: Array = GameData.maps_for(pref_np)
    var sel: String = pref_map if list.any(func(m): return String(m.id) == pref_map) else ""
    var flow := HFlowContainer.new()
    flow.add_theme_constant_override("h_separation", 10)
    flow.add_theme_constant_override("v_separation", 10)
    body.add_child(flow)
    var hexcols: Array = []
    for c in sides.cols:
        hexcols.append(String(COLORS[c].color))
    for entry in [{"id": "", "name": "Random"}] + list:
        var mid: String = String(entry.id)
        var b := _plate_button("", func():
            pref_map = mid
            _save_pref("map", mid)
            show_factions(), "tile", mid == sel, 14, 6, 6)
        b.custom_minimum_size = Vector2(150, 150)
        var vb := VBoxContainer.new()
        vb.set_anchors_preset(Control.PRESET_FULL_RECT)
        vb.alignment = BoxContainer.ALIGNMENT_CENTER
        vb.add_theme_constant_override("separation", 2)
        b.add_child(vb)
        if mid == "":
            var q := _label("?", 46, Color("f0dcaa"), true)
            q.add_theme_font_override("font", _font_head)
            q.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
            q.custom_minimum_size.y = 84
            q.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
            vb.add_child(q)
        else:
            var th := MapThumb.new()
            th.rows = entry.rows
            th.coins = entry.get("coins", [])
            th.cols = hexcols
            th.custom_minimum_size = Vector2(130, 84)
            th.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
            vb.add_child(th)
        var nm := _label(String(entry.name), 15, Color("f0dcaa"), true)
        nm.add_theme_font_override("font", _font_head)
        nm.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
        nm.clip_text = true
        nm.custom_minimum_size.x = 136
        vb.add_child(nm)
        var need: int = _win_castles_for(pref_np, mid)
        var sm := _label("a new map each game" if mid == "" else (("%d castles to win" % need) if need > 0 else "last side standing"), 12, Color("bfae88"))
        sm.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
        vb.add_child(sm)
        _ignore_mouse(vb)
        flow.add_child(b)
    body.add_child(_fsx_l("How to win", String(GameData.map_by_id(sel).name) if sel != "" else "Random map"))
    var rules := PanelContainer.new()
    var sb := StyleBoxFlat.new()
    sb.bg_color = Color(0.047, 0.035, 0.024, 0.6)
    sb.border_color = Color("6b4d1c")
    sb.set_border_width_all(1)
    sb.set_corner_radius_all(4)
    sb.set_content_margin_all(12)
    rules.add_theme_stylebox_override("panel", sb)
    body.add_child(rules)
    var rr := _rich(_win_list_bb(pref_np, sel), 15)
    rr.add_theme_color_override("default_color", Color("cdbf9c"))
    rules.add_child(rr)


## Castles to hold to win on a map (as GameState.win_castles before a game exists): the map's own number, else 4 with
## 2 players and none with 3.
func _win_castles_for(np: int, map_id: String) -> int:
    var m: Dictionary = GameData.map_by_id(map_id) if map_id != "" else {}
    if not m.is_empty() and int(m.get("players", 0)) == np and m.has("castles"):
        return int(m.castles)
    return 0 if np > 2 else int(GameData.rules.castles.to_win)


## How to win, as the browser's winListHtml.
func _win_list_bb(np: int, map_id: String) -> String:
    var need: int = _win_castles_for(np, map_id)
    var hold: int = int(GameData.rules.castles.hold_turns)
    var m: Dictionary = GameData.map_by_id(map_id) if map_id != "" else {}
    var own_rule: bool = not m.is_empty() and int(m.get("players", 0)) == np and m.has("castles")
    var lines: Array = []
    if np == 3:
        lines.append("[color=#f0e2bd][b]Take a rival's home castle[/b][/color] and they're out; their land turns neutral.")
        lines.append("[color=#f0e2bd][b]Wipe a rival off the map[/b][/color] and they're out too.")
        if need > 0:
            lines.append("[color=#f0e2bd][b]Hold %d captured castles[/b][/color] (not counting your home) while each rival gets %d turns to take one back." % [need, hold])
        lines.append("[color=#f0e2bd][b]Be the last side standing.[/b][/color]")
    else:
        lines.append("[color=#f0e2bd][b]Take their home castle[/b][/color] and win on the spot.")
        lines.append("[color=#f0e2bd][b]Hold %d %s for %d of their turns." % [need, "captured castles[/b][/color] (not counting your home)" if own_rule else "castles[/b][/color]", hold])
        lines.append("[color=#f0e2bd][b]Wipe them off the map.[/b][/color]")
    return "\\n".join(PackedStringArray(lines.map(func(x): return "  •  " + x)))


## The faction pop-up: its cards, units and abilities (what the old faction screen showed beside the tiles).
func _fsx_info() -> void:
    var fid: String = my_faction
    var F: Dictionary = GameData.factions[fid]
    var vw: Vector2 = get_viewport_rect().size
    var box := _open_overlay("", minf(820.0, vw.x - 40.0))
    box.get_child(0).queue_free()   # the head below stands in for the title line
    var head := HBoxContainer.new()
    head.add_theme_constant_override("separation", 12)
    box.add_child(head)
    head.add_child(_pic("res://art/terrain/castle_%s.png" % fid, Vector2(84, 60)))
    var ht := VBoxContainer.new()
    ht.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    head.add_child(ht)
    var nm := _label(String(F.name), 28, Color(String(F.ink)), true)
    nm.add_theme_font_override("font", _font_head)
    nm.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.9))
    nm.add_theme_constant_override("shadow_offset_y", 1)
    ht.add_child(nm)
    ht.add_child(_label(String(F.tagline), 15, Color("cdbf9c")))
    var scroll := ScrollContainer.new()
    scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
    scroll.custom_minimum_size.y = maxf(240.0, vw.y - 230.0)
    box.add_child(scroll)
    var body := VBoxContainer.new()
    body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    body.add_theme_constant_override("separation", 6)
    scroll.add_child(body)
    _faction_info_body(body, fid)
    body.add_child(_fsx_h("How to win"))
    var w := _rich(_win_list_bb(pref_np, pref_map), 14)
    body.add_child(w)
    var foot := HBoxContainer.new()
    foot.alignment = BoxContainer.ALIGNMENT_END
    box.add_child(foot)
    var close := _plate_button("Close", func(): _close_overlay(), "iron", false, 15, 22, 7)
    close.custom_minimum_size.x = 128
    foot.add_child(close)


## The difficulty pop-up: four tiles, the picked one ringed in gold.
func _fsx_level() -> void:
    var box := _open_overlay("Difficulty", 460.0)
    box.add_child(_label("How well the computer plays.", 14, Color("cdbf9c")))
    for lv in GameState.AI_LEVELS:
        var ll: String = lv
        var b := _plate_button("", func():
            pref_level = ll
            _save_pref("level", ll)
            _close_overlay()
            show_factions(), "tile", lv == pref_level, 15, 12, 8)
        b.custom_minimum_size.y = 58
        var vb := VBoxContainer.new()
        vb.set_anchors_preset(Control.PRESET_FULL_RECT)
        vb.alignment = BoxContainer.ALIGNMENT_CENTER
        vb.add_theme_constant_override("separation", 0)
        b.add_child(vb)
        var nm := _label(String(GameState.AI_LEVEL_NAME[lv]), 18, Color("f6e7bf") if lv == pref_level else PARCH, true)
        nm.add_theme_font_override("font", _font_head)
        nm.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
        vb.add_child(nm)
        var note := _label(String(GameState.AI_LEVEL_NOTE[lv]), 13, Color("bfae88"))
        note.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
        note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
        vb.add_child(note)
        _ignore_mouse(vb)
        box.add_child(b)
    var foot := HBoxContainer.new()
    foot.alignment = BoxContainer.ALIGNMENT_END
    box.add_child(foot)
    var close := _plate_button("Close", func(): _close_overlay(), "iron", false, 15, 22, 7)
    close.custom_minimum_size.x = 128
    foot.add_child(close)


## A faction's cards, units and abilities (the "About" pop-up).
func _faction_info_body(body: VBoxContainer, fid: String) -> void:
    var f2: Dictionary = GameData.factions[fid]
''') + info + '\n\n'
f.s = f.s[:a] + new + f.s[b:]

# the colours the game starts with: the rivals' picks when they're free
f.rep('''func _apply_colors() -> void:
    var mine: String = _my_color_for(String(g.players[0].faction))
    var taken: Array = [mine]
    var pcs: Array = [[0, mine]]
    for k in range(1, g.players.size()):
        var c: String = _other_color(taken, String(g.players[k].faction))''', '''func _apply_colors() -> void:
    var mine: String = _my_color_for(String(g.players[0].faction))
    var taken: Array = [mine]
    var pcs: Array = [[0, mine]]
    for k in range(1, g.players.size()):
        var w: String = String(pref_ocol[k - 1]) if k - 1 < pref_ocol.size() else ""   # the rival's colour picked on the setup screen
        var c: String = w if (COLORS.has(w) and not taken.has(w)) else _other_color(taken, String(g.players[k].faction))''')
# a new game opens the setup screen on its first tab
f.rep('''func _toggle_full() -> void:''', '''func _open_setup() -> void:
    fs_tab = 0
    show_factions()


func _toggle_full() -> void:''')
f.rep('''var start := _plate_button("Start Game" if saved.is_empty() else "New Game", func(): show_factions(), "gold", false, 22, 26, 10)''',
      '''var start := _plate_button("Start Game" if saved.is_empty() else "New Game", func(): _open_setup(), "gold", false, 22, 26, 10)''')
f.save()
print('ok')

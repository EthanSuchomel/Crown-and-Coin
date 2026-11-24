"""Browser commits 17d073e, a497d4b, f26a527, e9b7297, 55d9f18 (Ethan, 2026-11-22) in Godot:
- the home screen: the four-faction battle painting (art/ui/title_battle.jpg) with a soft dark glow behind the title,
  carved-gold "Crown & Coin" lettering with a gold rule and diamond under it, a gold Start plate and iron plates;
- the whole game themed the same way: the green panels turn dark iron with bronze trim and parchment text, buttons are
  iron plates and the main ones a softer gold plate, headings and pop-up titles in the carved serif (Cinzel).
Cinzel: drop Cinzel's .ttf (e.g. "Cinzel[wght].ttf" from Google Fonts) into res://art/fonts/; until then the game uses
Trajan Pro, Palatino Linotype or Georgia, like the browser does offline.
Needs files/scripts/ui/plate_box.gd and gold_text.gdshader copied in, and art/title_battle.jpg as art/ui/title_battle.jpg.
Usage: python3 p2_theme.py PROJ"""
import sys
from common import F, T
P = sys.argv[1]
f = F(P + '/scripts/ui/main.gd')

# --- the palette: iron, bronze and parchment (the browser's tokens)
f.rep('''# The browser version's palette
const NIGHT := Color("0f1912")
const MOSS := Color("16241a")
const MOSS2 := Color("1d3022")
const EDGE := Color("2f4b35")
const OUTLINE := Color("060907")
const BONE := Color("ece4cf")
const LICHEN := Color("a5b49e")''', '''# The browser version's palette: dark iron, bronze trim and parchment (Ethan, 2026-11-22)
const NIGHT := Color("100d09")
const MOSS := Color("1e1811")
const MOSS2 := Color("2b2319")
const EDGE := Color("5e4622")
const OUTLINE := Color("060907")
const BONE := Color("ece0c0")
const LICHEN := Color("b9a984")
const BRONZE := Color("6e5226")
const PARCH := Color("e4d6b4")
const IRON_RING := Color("120c06")''', raw=True)
for a, b in [("a5b49e", "b9a984"), ('Color("243a29")', 'Color("3a3024")'), ('Color("142118")', 'Color("17120c")'),
             ('Color("2a4430")', 'Color("4a3e2e")'), ('Color("1a231c")', 'Color("17120c")'), ('Color("2f3a31")', 'Color("5e4622")'),
             ("#0f1912", "#100d09"), ('Color("ece4cf")', 'Color("ece0c0")')]:
    f.s = f.s.replace(a, b)
f.rep('overlay.color = Color(0.012, 0.024, 0.016, 0.72)', 'overlay.color = Color(0.024, 0.016, 0.008, 0.72)', raw=True)

# --- fonts: the carved serif for headings
f.rep('''var _font_body: Font
var _font_bold: Font''', '''var _font_body: Font
var _font_bold: Font
var _font_head: Font    # Cinzel 700: headings, card names, pop-up titles, the setup screen
var _font_title: Font   # Cinzel 900: the home screen's title''', raw=True)
f.rep('''    _font_body = _make_font(500)
    _font_bold = _make_font(700)''', '''    _font_body = _make_font(500)
    _font_bold = _make_font(700)
    _font_head = _make_serif(700)
    _font_title = _make_serif(900, false)''')
f.rep('''## Finds an Oswald .ttf anywhere inside the fonts folder (and its subfolders),
## preferring the variable font that holds every weight.
func _find_oswald(dir_path: String) -> String:''', '''## The carved serif (Cinzel), as the browser's --cz font: Cinzel from res://art/fonts/ if it's there, otherwise Trajan Pro,
## Palatino Linotype or Georgia from the computer. msdf: false for the title, whose gold gradient reads the glyphs' coverage.
func _make_serif(weight: int, msdf: bool = true) -> Font:
    var path: String = _find_font("res://art/fonts", "cinzel")
    if path != "":
        var fv := FontVariation.new()
        fv.base_font = load(path)
        if path.to_lower().contains("wght") or path.to_lower().contains("variable"):
            var ts: TextServer = TextServerManager.get_primary_interface()
            fv.variation_opentype = {ts.name_to_tag("wght"): weight}
        elif weight >= 800:
            fv.variation_embolden = 0.5
        return fv
    var sf := SystemFont.new()
    sf.font_names = PackedStringArray(["Cinzel", "Trajan Pro", "Palatino Linotype", "Palatino", "Book Antiqua", "Georgia", "Times New Roman", "serif"])
    sf.font_weight = weight
    sf.multichannel_signed_distance_field = msdf
    sf.generate_mipmaps = true
    if weight >= 800:
        sf.font_weight = 700
        sf.font_stretch = 100
    return sf


## A .ttf whose name starts with prefix anywhere inside the folder (variable font preferred).
func _find_font(dir_path: String, prefix: String) -> String:
    var d := DirAccess.open(dir_path)
    if d == null:
        return ""
    var found: String = ""
    for fl in d.get_files():
        var fname: String = fl.trim_suffix(".import").trim_suffix(".remap")
        var low: String = fname.to_lower()
        if low.begins_with(prefix) and (low.ends_with(".ttf") or low.ends_with(".otf")):
            var path: String = dir_path.path_join(fname)
            if low.contains("wght") or low.contains("variable"):
                return path
            if found == "" or low.contains("regular"):
                found = path
    for sub in d.get_directories():
        var inner: String = _find_font(dir_path.path_join(sub), prefix)
        if inner != "" and (found == "" or inner.to_lower().contains("wght")):
            found = inner
    return found


## Finds an Oswald .ttf anywhere inside the fonts folder (and its subfolders),
## preferring the variable font that holds every weight.
func _find_oswald(dir_path: String) -> String:''')

# --- plates: iron buttons, a softer gold for the main ones, iron cards and panels
a = f.s.index(T('func _button_box(fill: Color, bottom: Color) -> StyleBoxFlat:\n'))
b = f.s.index(T('func _make_theme() -> Theme:\n'))
f.s = f.s[:a] + T('''## The game's buttons: iron plates (browser: button{linear-gradient(#3a3125,#211a12)} with a bronze inner line).
func _button_box(fill: Color, bottom: Color) -> StyleBox:
    var cols: Array = [fill.lightened(0.08), fill.darkened(0.25)]
    if fill == MOSS2:
        cols = [Color("3a3125"), Color("211a12")]
    elif fill == Color("3a3024"):   # hover
        cols = [Color("4a3e2e"), Color("2a2117")]
    elif fill == Color("17120c"):   # pressed
        cols = [Color("211a12"), Color("2a2117")]
    elif fill.a < 1.0:              # disabled
        cols = [Color(Color("3a3125"), fill.a), Color(Color("211a12"), fill.a)]
    var p := PlateBox.make(cols, IRON_RING, 12, 7)
    p.trim_w = 2.0
    p.ring_w = 0.0
    p.inner = Color(EDGE, fill.a)
    p.top_hi = Color(1.0, 0.925, 0.745, 0.08 * fill.a)
    p.top_hi_w = 2.0
    p.bottom_lo = Color(0, 0, 0, 0.35 * fill.a)
    p.bottom_lo_w = 3.0
    if bottom == GOLD2:   # the gold plate (browser: button.primary)
        p.stops = PackedColorArray([Color(Color("f6e2a4"), fill.a), Color(Color("e2b75a"), fill.a), Color(Color("b98432"), fill.a)])
        if fill == Color("f6cd6c"):   # hover
            p.stops = PackedColorArray([Color("fbeab8"), Color("e9c26a"), Color("c48f3a")])
        elif fill == GOLD2:           # pressed
            p.stops = PackedColorArray([Color("e2b75a"), Color("c99a45"), Color("a87428")])
        p.at = PackedFloat32Array([0.0, 0.4, 1.0])
        p.trim = Color("4a300c")
        p.inner = Color(0, 0, 0, 0)
        p.top_hi = Color(1, 1, 1, 0.45 * fill.a)
        p.bottom_lo = Color(0.353, 0.216, 0.039, 0.5 * fill.a)
    return p


## A plate for the home and setup screens (Ethan, 2026-11-22):
## "iron" (parchment letters, bronze trim), "iron_hover", "gold" (Start), "gold_hover", "ghost" (Full screen),
## "tab", "tab_on", "tile", "tile_on", "panel" (the setup screen's body), "sheet" (its pop-ups).
func _plate(kind: String, mx: float = 14.0, my: float = 8.0) -> PlateBox:
    var p: PlateBox
    match kind:
        "iron":
            p = PlateBox.make([Color("3b3226"), Color("221b13"), Color("17120c")], BRONZE, mx, my, [0.0, 0.55, 1.0])
        "iron_hover":
            p = PlateBox.make([Color("4a3f2f"), Color("2a2118"), Color("1c160e")], Color("8a6a34"), mx, my, [0.0, 0.55, 1.0])
        "gold":
            p = PlateBox.make([Color("fff0bd"), Color("f4cf6b"), Color("dca43a"), Color("a9721f")], Color("5a3a0e"), mx, my, [0.0, 0.22, 0.55, 1.0])
            p.top_hi = Color(1, 1, 1, 0.55)
            p.top_hi_w = 2.0
            p.bottom_lo = Color(0.353, 0.216, 0.039, 0.55)
            p.bottom_lo_w = 3.0
            p.glow = Color(1.0, 0.706, 0.235, 0.22)
            p.glow_w = 3.0
        "gold_hover":
            p = PlateBox.make([Color("fff6d2"), Color("f8da80"), Color("e6b14a"), Color("b67d26")], Color("5a3a0e"), mx, my, [0.0, 0.22, 0.55, 1.0])
            p.top_hi = Color(1, 1, 1, 0.55)
            p.top_hi_w = 2.0
            p.bottom_lo = Color(0.353, 0.216, 0.039, 0.55)
            p.bottom_lo_w = 3.0
            p.glow = Color(1.0, 0.706, 0.235, 0.3)
            p.glow_w = 3.0
        "ghost":
            p = PlateBox.make([Color(0.071, 0.051, 0.031, 0.72), Color(0.071, 0.051, 0.031, 0.72)], Color(0.788, 0.584, 0.184, 0.7), mx, my)
            p.top_hi = Color(0, 0, 0, 0)
        "tab":
            p = PlateBox.make([Color("3b3226"), Color("1d1710")], BRONZE, mx, my)
        "tab_on":
            p = PlateBox.make([Color("5a4a33"), Color("2c2318")], Color("b8913f"), mx, my)
            p.top_hi = Color(1.0, 0.925, 0.745, 0.22)
            p.bottom_lo = Color(0.914, 0.725, 0.286, 0.55)
            p.bottom_lo_w = 3.0
        "tile":
            p = PlateBox.make([Color(0.204, 0.165, 0.118, 0.9), Color(0.094, 0.075, 0.051, 0.92)], Color("4f3b1c"), mx, my)
            p.top_hi = Color(1.0, 0.925, 0.745, 0.1)
        "tile_hover":
            p = PlateBox.make([Color(0.235, 0.188, 0.133, 0.92), Color(0.11, 0.086, 0.059, 0.94)], Color("8a6a34"), mx, my)
            p.top_hi = Color(1.0, 0.925, 0.745, 0.12)
        "tile_on":
            p = PlateBox.make([Color(0.251, 0.196, 0.118, 0.95), Color(0.118, 0.09, 0.055, 0.95)], Color("d9b25a"), mx, my)
            p.glow = Color(0.914, 0.725, 0.286, 0.75)
            p.glow_w = 3.0
            p.top_hi = Color(1.0, 0.925, 0.745, 0.12)
        "panel":
            p = PlateBox.make([Color(0.086, 0.067, 0.047, 0.78), Color(0.086, 0.067, 0.047, 0.78)], BRONZE, mx, my)
            p.inner = Color(0.914, 0.725, 0.286, 0.12)
            p.top_hi = Color(0, 0, 0, 0)
        "sheet":
            p = PlateBox.make([Color(0.133, 0.106, 0.075, 0.97), Color(0.071, 0.055, 0.039, 0.97)], BRONZE, mx, my)
            p.inner = Color(0.914, 0.725, 0.286, 0.12)
            p.top_hi = Color(0, 0, 0, 0)
        _:
            p = PlateBox.make([MOSS, MOSS], EDGE, mx, my)
    return p


## A button made of plates: kind "iron", "gold" or "ghost" (and "tab"/"tile" with on = picked).
func _plate_button(text: String, f: Callable, kind: String = "iron", on: bool = false, size_px: int = 16, mx: float = 14.0, my: float = 8.0) -> Button:
    var b := Button.new()
    b.text = text
    b.focus_mode = Control.FOCUS_NONE
    b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
    var normal: String = kind + ("_on" if on and (kind == "tab" or kind == "tile") else "")
    var hover: String = kind + "_hover" if kind in ["iron", "gold", "tile"] and not on else normal
    b.add_theme_stylebox_override("normal", _plate(normal, mx, my))
    b.add_theme_stylebox_override("hover", _plate(hover, mx, my))
    b.add_theme_stylebox_override("pressed", _plate(hover, mx, my))
    b.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
    var dis := _plate(normal, mx, my)
    b.add_theme_stylebox_override("disabled", dis)
    b.add_theme_font_override("font", _font_head)
    b.add_theme_font_size_override("font_size", size_px)
    var ink: Color = Color("2a1805") if kind == "gold" else (Color("f6e7bf") if on else PARCH)
    for c in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color", "font_hover_pressed_color"]:
        b.add_theme_color_override(c, ink)
    b.add_theme_color_override("font_disabled_color", Color(ink, 0.35))
    if kind != "gold":
        b.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.6))
        b.add_theme_constant_override("outline_size", 2)
    b.pressed.connect(f)
    return b


''') + f.s[b:]
f.rep('''    # buttons: moss with a near-black outline
    th.set_font("font", "Button", _font_bold)''', '''    # buttons: iron plates (Ethan, 2026-11-22)
    th.set_font("font", "Button", _font_bold)''')
f.rep('''    # the gold primary button
    th.set_type_variation("Primary", "Button")''', '''    # the gold primary button, in the carved serif
    th.set_type_variation("Primary", "Button")
    th.set_font("font", "Primary", _font_head)''')
f.rep('''    th.set_type_variation("CardButton", "Button")
    var card := _frame(MOSS2, 0)
    th.set_stylebox("normal", "CardButton", card)
    var card_hover := _frame(Color("3a3024"), 0)
    th.set_stylebox("hover", "CardButton", card_hover)
    th.set_stylebox("pressed", "CardButton", card_hover)
    var card_due := _box(MOSS2, GOLD, 2, 0)
    th.set_type_variation("CardDue", "Button")
    th.set_stylebox("normal", "CardDue", card_due)
    th.set_stylebox("hover", "CardDue", _box(Color("3a3024"), GOLD, 2, 0))
    th.set_stylebox("pressed", "CardDue", _box(Color("3a3024"), GOLD, 2, 0))
    # panels
    th.set_stylebox("panel", "PanelContainer", _frame(MOSS))
    th.set_stylebox("panel", "PopupPanel", _frame(MOSS))''', '''    th.set_type_variation("CardButton", "Button")
    var card := _iron_panel(0)
    th.set_stylebox("normal", "CardButton", card)
    var card_hover := PlateBox.make([Color(0.196, 0.157, 0.11, 0.96), Color(0.11, 0.086, 0.059, 0.96)], EDGE, 0, 0)
    card_hover.ring = OUTLINE
    th.set_stylebox("hover", "CardButton", card_hover)
    th.set_stylebox("pressed", "CardButton", card_hover)
    var card_due := _iron_panel(0)
    card_due.trim = GOLD
    th.set_type_variation("CardDue", "Button")
    th.set_stylebox("normal", "CardDue", card_due)
    var due_hover: PlateBox = card_hover.copy()
    due_hover.trim = GOLD
    th.set_stylebox("hover", "CardDue", due_hover)
    th.set_stylebox("pressed", "CardDue", due_hover)
    # panels: dark iron with bronze trim (browser: linear-gradient(rgba(38,30,21,.94),rgba(22,17,12,.95)))
    th.set_stylebox("panel", "PanelContainer", _iron_panel(8))
    th.set_stylebox("panel", "PopupPanel", _iron_panel(8))''')
f.rep('''# =====================================================================
# Screens
# =====================================================================
''', '''## An iron panel with bronze trim, as the browser's game panels.
func _iron_panel(margin: float = 8.0) -> PlateBox:
    var p := PlateBox.make([Color(0.149, 0.118, 0.082, 0.94), Color(0.086, 0.067, 0.047, 0.95)], EDGE, margin, margin)
    p.ring = OUTLINE
    p.top_hi = Color(1.0, 0.925, 0.745, 0.06)
    return p


# =====================================================================
# Screens
# =====================================================================
''')

# --- the home screen
a = f.s.index(T('func show_title() -> void:\n'))
b = f.s.index(T('func _toggle_full() -> void:\n'))
f.s = f.s[:a] + T('''## The battle painting filling the screen (cropped to cover it), as the browser's background-size:cover.
func _painting(path: String) -> void:
    var tr := TextureRect.new()
    if ResourceLoader.exists(path):
        tr.texture = load(path)
    tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
    tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
    tr.set_anchors_preset(Control.PRESET_FULL_RECT)
    tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(tr)


## The home screen (Ethan, 2026-11-22): the four-faction battle painting, a soft dark glow behind the title and buttons,
## carved-gold lettering with a gold rule under it, a gold Start plate and iron plates.
func show_title() -> void:
    _clear()
    g = null
    _painting("res://art/ui/title_battle.jpg")
    var shade := TextureRect.new()   # linear-gradient(rgba(9,16,11,.1),rgba(9,16,11,.25))
    var lg := Gradient.new()
    lg.set_color(0, Color(0.035, 0.063, 0.043, 0.1))
    lg.set_color(1, Color(0.035, 0.063, 0.043, 0.25))
    var lt := GradientTexture2D.new()
    lt.gradient = lg
    lt.fill_from = Vector2(0.5, 0.0)
    lt.fill_to = Vector2(0.5, 1.0)
    shade.texture = lt
    shade.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
    shade.stretch_mode = TextureRect.STRETCH_SCALE
    shade.set_anchors_preset(Control.PRESET_FULL_RECT)
    shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(shade)
    var glow := TextureRect.new()    # radial-gradient(ellipse 34% 46% at 50% 52%, .62 -> .38 at 55% -> 0)
    var rg := Gradient.new()
    rg.offsets = PackedFloat32Array([0.0, 0.55, 1.0])
    rg.colors = PackedColorArray([Color(0.035, 0.063, 0.043, 0.62), Color(0.035, 0.063, 0.043, 0.38), Color(0.035, 0.063, 0.043, 0.0)])
    var rt := GradientTexture2D.new()
    rt.gradient = rg
    rt.fill = GradientTexture2D.FILL_RADIAL
    rt.fill_from = Vector2(0.5, 0.5)
    rt.fill_to = Vector2(1.0, 0.5)
    glow.texture = rt
    glow.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
    glow.stretch_mode = TextureRect.STRETCH_SCALE
    glow.anchor_left = 0.16
    glow.anchor_right = 0.84
    glow.anchor_top = 0.06
    glow.anchor_bottom = 0.98
    glow.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(glow)
    var center := CenterContainer.new()
    center.set_anchors_preset(Control.PRESET_FULL_RECT)
    add_child(center)
    var box := VBoxContainer.new()
    box.add_theme_constant_override("separation", 14)
    box.alignment = BoxContainer.ALIGNMENT_CENTER
    center.add_child(box)
    var fs: int = int(clampf(get_viewport_rect().size.y * 0.115, 40.0, 84.0))
    box.add_child(_gold_title(fs))
    box.add_child(_gold_rule(minf(416.0, get_viewport_rect().size.x * 0.8)))
    var btns := VBoxContainer.new()
    btns.add_theme_constant_override("separation", 12)
    btns.alignment = BoxContainer.ALIGNMENT_CENTER
    box.add_child(btns)
    var saved: Dictionary = _read_save()
    var start := _plate_button("Start Game" if saved.is_empty() else "New Game", func(): show_factions(), "gold", false, 22, 26, 10)
    _studs(start, Color("5a3a0e"), Color("fff0bd"))
    start.custom_minimum_size = Vector2(212, 0)
    start.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
    btns.add_child(start)
    if not saved.is_empty():
        var cont := _plate_button("Continue game", func(): _continue_game(saved), "iron", false, 16, 26, 9)
        _studs(cont, Color("a88a55"), IRON_RING)
        cont.custom_minimum_size = Vector2(200, 0)
        cont.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
        btns.add_child(cont)
        var gs: Dictionary = saved.game
        var who: String = String(GameData.factions[String(gs.players[0].faction)].name)
        var sub := _label("%s · turn %d" % [who, int(gs.turn)], 14, BONE)
        sub.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.9))
        sub.add_theme_constant_override("shadow_offset_y", 1)
        sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
        btns.add_child(sub)
    var full := _plate_button("⛶ Full screen", func(): _toggle_full(), "ghost", false, 13, 18, 6)
    full.add_theme_color_override("font_color", Color("e8d3a0"))
    full.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
    btns.add_child(full)


## Diamond studs at both ends of a home-screen plate (the browser's ::before and ::after).
func _studs(b: Button, col: Color, ring: Color) -> void:
    for st in ["normal", "hover", "pressed"]:
        var p = b.get_theme_stylebox(st)
        if p is PlateBox:
            p.gem = col
            p.gem_ring = ring


## "Crown & Coin" in carved gold: a gold gradient through the letters, a dark outline and a drop shadow; the & in red-gold.
func _gold_title(fs: int) -> Control:
    var row := HBoxContainer.new()
    row.alignment = BoxContainer.ALIGNMENT_CENTER
    row.add_theme_constant_override("separation", 0)
    row.mouse_filter = Control.MOUSE_FILTER_IGNORE
    var sh: Shader = load("res://scripts/ui/gold_text.gdshader")
    for part in [["Crown ", 1.0, false], ["&", 0.82, true], [" Coin", 1.0, false]]:
        var l := Label.new()
        l.text = part[0]
        var size_px: int = int(fs * float(part[1]))
        l.add_theme_font_override("font", _font_title)
        l.add_theme_font_size_override("font_size", size_px)
        l.add_theme_color_override("font_color", Color.WHITE)
        l.add_theme_color_override("font_outline_color", Color("2a1a06"))
        l.add_theme_constant_override("outline_size", maxi(2, int(size_px * 0.05)))
        l.add_theme_color_override("font_shadow_color", Color(0.102, 0.063, 0.02, 0.95))
        l.add_theme_constant_override("shadow_offset_x", 0)
        l.add_theme_constant_override("shadow_offset_y", maxi(2, int(size_px * 0.05)))
        l.add_theme_constant_override("shadow_outline_size", maxi(3, int(size_px * 0.09)))
        l.size_flags_vertical = Control.SIZE_SHRINK_CENTER
        l.mouse_filter = Control.MOUSE_FILTER_IGNORE
        var m := ShaderMaterial.new()
        m.shader = sh
        if part[2]:   # the ampersand: red gold
            m.set_shader_parameter("c0", Color("ffd9c9"))
            m.set_shader_parameter("c1", Color("f27b52"))
            m.set_shader_parameter("c2", Color("d04a2a"))
            m.set_shader_parameter("c3", Color("b3271c"))
            m.set_shader_parameter("c4", Color("e55a33"))
        var fnt: Font = _font_title
        var asc: float = fnt.get_ascent(size_px)
        m.set_shader_parameter("y0", asc - size_px * 0.74)
        m.set_shader_parameter("y1", asc + size_px * 0.02)
        l.material = m
        row.add_child(l)
    return row


## A gold rule with a diamond, under the title.
class GoldRule extends Control:
    func _draw() -> void:
        var w: float = size.x
        var y: float = size.y / 2.0
        var d: float = 7.0
        var gap: float = 14.0
        var lc := Color(0, 0, 0, 0.0)
        var mid := Color("e9b949")
        var tip := Color("fff1b8")
        # left line: transparent -> gold -> pale at the diamond (and the mirror on the right)
        for side in [-1.0, 1.0]:
            var x_out: float = w / 2.0 + side * (w / 2.0)
            var x_in: float = w / 2.0 + side * gap
            var x_mid: float = lerpf(x_out, x_in, 0.4)
            for seg in [[x_out, x_mid, lc, mid], [x_mid, x_in, mid, tip]]:
                var a0: float = minf(seg[0], seg[1])
                var a1: float = maxf(seg[0], seg[1])
                var c0: Color = seg[2] if seg[0] < seg[1] else seg[3]
                var c1: Color = seg[3] if seg[0] < seg[1] else seg[2]
                draw_rect(Rect2(a0, y - 2.0, a1 - a0, 4.0), Color(0, 0, 0, 0.35 * maxf(c0.a, c1.a)))
                draw_polygon(PackedVector2Array([Vector2(a0, y - 1.0), Vector2(a1, y - 1.0), Vector2(a1, y + 1.0), Vector2(a0, y + 1.0)]), PackedColorArray([c0, c1, c1, c0]))
        var c := Vector2(w / 2.0, y)
        draw_colored_polygon(PackedVector2Array([c + Vector2(0, -d - 2), c + Vector2(d + 2, 0), c + Vector2(0, d + 2), c + Vector2(-d - 2, 0)]), Color("2a1a06"))
        draw_polygon(PackedVector2Array([c + Vector2(0, -d), c + Vector2(d, 0), c + Vector2(0, d), c + Vector2(-d, 0)]),
            PackedColorArray([Color("fff1b8"), Color("e0b048"), Color("c98f2a"), Color("f0d27a")]))


func _gold_rule(w: float) -> Control:
    var r := GoldRule.new()
    r.custom_minimum_size = Vector2(w, 20)
    r.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
    r.mouse_filter = Control.MOUSE_FILTER_IGNORE
    return r


''') + f.s[b:]

# --- pop-ups: the iron sheet, a Cinzel title in parchment
f.rep('''    var panel := PanelContainer.new()
    panel.custom_minimum_size = Vector2(width, 0)
    panel.add_theme_stylebox_override("panel", _frame(MOSS, 16))
    center.add_child(panel)
    var box := VBoxContainer.new()
    box.add_theme_constant_override("separation", 8)
    panel.add_child(box)
    var t := _label(title, 24, BONE, true)''', '''    var panel := PanelContainer.new()
    panel.custom_minimum_size = Vector2(width, 0)
    panel.add_theme_stylebox_override("panel", _plate("sheet", 16, 16))
    center.add_child(panel)
    var box := VBoxContainer.new()
    box.add_theme_constant_override("separation", 8)
    panel.add_child(box)
    var t := _label(title, 24, Color("f0e2bd"), true)
    t.add_theme_font_override("font", _font_head)''')
f.rep('''func _small_button_box() -> StyleBoxFlat:
    var sb := _button_box(MOSS2, OUTLINE)''', '''func _small_button_box() -> StyleBox:
    var sb: StyleBox = _button_box(MOSS2, OUTLINE)''')
f.save()
print('ok')

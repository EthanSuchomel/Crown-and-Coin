"""Ethan, 2026-11-12 (browser commit cdc3ff3) in the Godot version: no explanations next to a card's actions (tap the
action's icon for a box with the explanation and its upgrades), a trophy for each upgrade in place of the upgrade
names, and no win chance in the attack window. Usage: python3 p3_info.py PROJ  (and copy trophy.png to art/ui/)"""
import sys
from common import F, T
P = sys.argv[1]
f = F(P + '/scripts/ui/main.gd')

# hand cards: number, tappable icon, name and trophies
f.rep('''    for s in card.actions.size():
        var a: String = card.actions[s]
        var l: int = g.lvl_of(0, cid, s)
        var up: String = ""
        if l > 0:
            up = "  [color=#efc15a]%s[/color]" % _level_name(0, a, l, cid)
        vb.add_child(_rich("[bgcolor=#0f1912][color=#a5b49e] %d [/color][/bgcolor] %s %s%s" % [s + 1, _img(a, 28), ACTION_NAMES[a], up], 14))
    if g.upgrade_due(0, cid):
        vb.add_child(_label("▲ Playing it now upgrades an action", 12, GOLD))
    _ignore_mouse(hb)
''', '''    var icons: Array = []
    for s in card.actions.size():
        var a: String = card.actions[s]
        var l: int = g.lvl_of(0, cid, s)
        var ic: TextureButton = _act_icon(0, cid, s, 28)
        icons.append(ic)
        vb.add_child(_act_row(s, ic, ACTION_NAMES[a] + _trophies(l), 14))
    if g.upgrade_due(0, cid):
        vb.add_child(_label("▲ Playing it now upgrades an action", 12, GOLD))
    _ignore_mouse(hb)
    for ic in icons:   # the action icons still take taps: they open the action's explanation
        ic.mouse_filter = Control.MOUSE_FILTER_STOP
''')

# the card filling the column
f.rep('''        var desc: String = _action_desc(a, pid, raw, cid)
        var name_txt: String = "[s]%s[/s]" % ACTION_NAMES[a] if done else ACTION_NAMES[a]
        var lvl_txt: String = ("  [color=#efc15a]%s[/color]" % _level_name(pid, a, raw, cid)) if raw > 0 else ""
        var show_desc: bool = not done
        var txt: String = "[bgcolor=#0f1912][color=#a5b49e] %d [/color][/bgcolor] %s [b]%s[/b]%s" % [s + 1, _img(a, 30), name_txt, lvl_txt]
        if show_desc:
            txt += "\\n[color=#a5b49e][font_size=13]%s[/font_size][/color]" % desc
        var r := _rich(txt, 15)
        r.modulate = Color(1, 1, 1, 0.55) if done else Color.WHITE
        row_panel.add_child(r)
''', '''        # no explanation here (Ethan): tap the icon for it; a trophy for each upgrade
        var name_txt: String = "[s]%s[/s]" % ACTION_NAMES[a] if done else ACTION_NAMES[a]
        var r := _act_row(s, _act_icon(pid, cid, s, 30), "[b]%s[/b]%s" % [name_txt, _trophies(raw)], 15)
        r.modulate = Color(1, 1, 1, 0.55) if done else Color.WHITE
        row_panel.add_child(r)
''')
f.rep('''        var up_txt: String = "You'll carry out these 3 actions in order and can skip any of them. Playing it earns a favor. Every 2nd favor upgrades one of its actions."''',
      '''        var up_txt: String = "You'll carry out these 3 actions in order and can skip any of them. Playing it earns a favor. Every 2nd favor upgrades one of its actions. Tap an action's icon to read what it does."''')

# the helpers
f.rep('''## What an action does at its current level, as in the browser version's actionDesc.
''', '''## A trophy for each upgrade on an action (in place of the upgrade's name).
func _trophies(l: int) -> String:
    if l <= 0:
        return ""
    return " " + "[img=16x16]res://art/ui/trophy.png[/img]".repeat(l)


## An action's icon: tap it for a box explaining the action (with its upgrades).
func _act_icon(pid: int, cid: String, s: int, size_px: int) -> TextureButton:
    var a: String = String(g.card_of(pid, cid).actions[s])
    var ic := TextureButton.new()
    ic.texture_normal = load("res://art/ui/%s.png" % a)
    ic.ignore_texture_size = true
    ic.stretch_mode = TextureButton.STRETCH_KEEP_ASPECT_CENTERED
    ic.custom_minimum_size = Vector2(size_px, size_px)
    ic.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    ic.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
    ic.tooltip_text = "What does %s do?" % ACTION_NAMES[a]
    ic.pressed.connect(func(): _open_action_info(pid, cid, s))
    return ic


## One action row: its number, its (tappable) icon, then its name.
func _act_row(s: int, ic: TextureButton, bb: String, size_px: int) -> HBoxContainer:
    var row := HBoxContainer.new()
    row.add_theme_constant_override("separation", 5)
    var num := _rich("[bgcolor=#0f1912][color=#a5b49e] %d [/color][/bgcolor]" % (s + 1), size_px)
    num.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
    num.autowrap_mode = TextServer.AUTOWRAP_OFF
    num.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    row.add_child(num)
    row.add_child(ic)
    var r := _rich(bb, size_px)
    r.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    row.add_child(r)
    return row


func _open_action_info(pid: int, cid: String, s: int) -> void:
    var a: String = String(g.card_of(pid, cid).actions[s])
    var l: int = g.lvl_of(pid, cid, s)
    var box := _open_overlay(ACTION_NAMES[a], 520.0)
    var txt: String = "%s %s" % [_img(a, 40), _action_desc(a, pid, l, cid)]
    if l > 0:
        txt += "\\n\\n[color=#efc15a]%s[/color]%s" % [_level_name(pid, a, l, cid), _trophies(l)]
    box.add_child(_rich(txt, 15))
    var close := _button("Close", func(): _close_overlay(), true)
    box.add_child(close)


## What an action does at its current level, as in the browser version's actionDesc.
''')

# no win chance before a battle
a = f.s.index(T('    var odds := _rich("", 15)\n'))
b = f.s.index(T('    var rows := VBoxContainer.new()\n'), a)
f.s = f.s[:a] + T('    var update_odds := func(): pass   # no win chance shown before a battle (Ethan, 2026-11-12)\n') + f.s[b:]
f.rep('''    box.add_child(odds)
    update_odds.call()
''', '')
f.save()
print('ok')

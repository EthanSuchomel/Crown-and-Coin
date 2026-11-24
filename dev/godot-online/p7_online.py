"""Ethan, 2026-11-23: "can we add the online play to godot?" (Godot to Godot, through a free Supabase database).
- The home screen gets **Play online**: New game (the same three-tab setup, 2 players, the opponent played by a friend,
  ending in **Create game** and a 4-letter code), Join a game (type the code), and Your games (open or remove them).
- In an online game you are always player 0 on your own computer (the friend's computer sees the stored game turned
  round: online.gd swap_seats). The side whose turn it is stores the board after everything it does; the other side
  checks every 2.5 s and picks it up, so you see their moves as they make them. New becomes Leave.
- Battles are fought on the attacker's computer (the defender's army is led by the computer), and the result is stored.
- Needs scripts/ui/online.gd and data/online.json ({"url": "https://....supabase.co", "key": "..."}).
Usage: python3 p7_online.py PROJ"""
import sys
sys.path.insert(0, __file__.rsplit('/', 2)[0] + '/godot-port-nov22')
from common import F, T
P = sys.argv[1]
f = F(P + '/scripts/ui/main.gd')

f.rep('''var fs_tab: int = 0               # the setup screen's open tab: 0 You, 1 Opponent, 2 Map & rules''',
      '''var fs_tab: int = 0               # the setup screen's open tab: 0 You, 1 Opponent, 2 Map & rules
var net = null                    # the online database (online.gd)
var online: Dictionary = {}       # the online game being played or waited for: {code, seat, rev, json, last_cur, waiting}
var fs_online: bool = false       # the setup screen is making an online game
var _np_keep: int = 2             # the local game's Players while the setup screen makes an online game (always 2)
var _net_timer: Timer = null
var _net_pushing: bool = false
var _net_again: bool = false
var _net_fetching: bool = false
var _net_ticking: bool = false''', raw=True)

f.rep('''    show_title()


# =====================================================================
# Theme''', '''    net = load("res://scripts/ui/online.gd").new()
    add_child(net)
    _net_timer = Timer.new()
    _net_timer.wait_time = 2.5
    _net_timer.autostart = true
    _net_timer.timeout.connect(_net_tick)
    add_child(_net_timer)
    show_title()


# =====================================================================
# Theme''')

f.rep('''func _clear() -> void:
    for c in get_children():
        c.queue_free()''', '''func _clear() -> void:
    for c in get_children():
        if c == net or c == _net_timer:
            continue
        c.queue_free()''')

# the home screen: Play online
f.rep('''    var full := _plate_button("⛶ Full screen", func(): _toggle_full(), "ghost", false, 13, 18, 6)''',
      '''    var ol := _plate_button("Play online", func(): show_online(), "iron", false, 16, 26, 9)
    _studs(ol, Color("a88a55"), IRON_RING)
    ol.custom_minimum_size = Vector2(200, 0)
    ol.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
    btns.add_child(ol)
    var full := _plate_button("⛶ Full screen", func(): _toggle_full(), "ghost", false, 13, 18, 6)''')
f.rep('''func show_title() -> void:
    _clear()
    g = null''', '''func show_title() -> void:
    _clear()
    g = null
    online = {}
    if fs_online:
        fs_online = false
        pref_np = _np_keep''')

# the setup screen's online mode
f.rep('''    foot.add_child(_plate_button("Back" if fs_tab > 0 else "Title", func(): _fsx_back(), "iron", false, 15, 16, 8))''',
      '''    foot.add_child(_plate_button("Back" if fs_tab > 0 else ("Online" if fs_online else "Title"), func(): _fsx_back(), "iron", false, 15, 16, 8))''')
f.rep('''    var go := _plate_button("Start", func():
        _close_overlay()
        start_game(my_faction), "gold", false, 19, 22, 8)
    go.custom_minimum_size.x = 112''', '''    var go := _plate_button("Create game" if fs_online else "Start", func():
        _close_overlay()
        if fs_online:
            _net_create()
        else:
            start_game(my_faction), "gold", false, 19, 22, 8)
    go.custom_minimum_size.x = 112''')
f.rep('''func _fsx_back() -> void:
    if fs_tab > 0:
        _fsx_go(fs_tab - 1)
    else:
        show_title()''', '''func _fsx_back() -> void:
    if fs_tab > 0:
        _fsx_go(fs_tab - 1)
    elif fs_online:
        show_online()
    else:
        show_title()''')
f.rep('''    var sum := _rich("%s vs %s · %s · %s" % [who[0], " and ".join(PackedStringArray(who.slice(1))), String(GameState.AI_LEVEL_NAME[pref_level]), map_name], 14)''',
      '''    var sum := _rich(("[color=#e9c66a][b]Online[/b][/color] · %s vs %s (a friend) · %s" % [who[0], who[1], map_name]) if fs_online else ("%s vs %s · %s · %s" % [who[0], " and ".join(PackedStringArray(who.slice(1))), String(GameState.AI_LEVEL_NAME[pref_level]), map_name]), 14)''')
f.rep('''    for n in [2, 3]:
        var nn: int = n''', '''    for n in ([2] if fs_online else [2, 3]):   # online games are 2 players for now
        var nn: int = n''')
f.rep('''    var hint := _label("You and two rivals" if pref_np == 3 else "You and one opponent", 14, Color("bfae88"))''',
      '''    var hint := _label("You and two rivals" if pref_np == 3 else ("You and a friend, online" if fs_online else "You and one opponent"), 14, Color("bfae88"))''')
f.rep('''        vb.add_child(_fsx_l(("Rival %d" % (k + 1)) if pref_np == 3 else "Opponent", "played by the computer"))''',
      '''        vb.add_child(_fsx_l(("Rival %d" % (k + 1)) if pref_np == 3 else "Opponent", "played by a friend" if fs_online else "played by the computer"))''')
f.rep('''    body.add_child(_fsx_more("!", "Difficulty: [b]%s[/b]''', '''    if fs_online:
        body.add_child(_label("Your friend joins with the game's code once it's made.", 14, Color("bfae88")))
        return
    body.add_child(_fsx_more("!", "Difficulty: [b]%s[/b]''')

# a local game never sends; an online one sends instead of saving to the computer
f.rep('''func _save() -> void:
    if g == null or busy:
        return''', '''func _save() -> void:
    if g == null or busy:
        return
    if not online.is_empty():   # online: the board goes to the shared game instead of this computer's save
        _net_push_soon()
        return''')
f.rep('''func _run_ai() -> void:
    busy = true''', '''func _run_ai() -> void:
    if not online.is_empty():   # online: the other side is a person on their own computer; send them the board
        _net_push_soon()
        return
    busy = true''')
f.rep('''    for spec in [["Full", func(): _toggle_full()], ["?", func(): _open_help()], ["Log", func(): _open_log()], ["New", func(): show_title()]]:''',
      '''    for spec in [["Full", func(): _toggle_full()], ["?", func(): _open_help()], ["Log", func(): _open_log()], ["Leave" if not online.is_empty() else "New", func(): _net_leave() if not online.is_empty() else show_title()]]:''')

# the online screens and the syncing
f.rep('''# =====================================================================
# The map's place on the screen
# =====================================================================''', '''# =====================================================================
# Online play (Ethan, 2026-11-23)
# =====================================================================

## The Play online screen: New game, Join a game (a 4-letter code) and Your games.
func show_online(msg: String = "") -> void:
    _clear()
    g = null
    online = {}
    if fs_online:
        fs_online = false
        pref_np = _np_keep
    _painting("res://art/ui/title_battle_dim.jpg")
    var vw: Vector2 = get_viewport_rect().size
    var center := CenterContainer.new()
    center.set_anchors_preset(Control.PRESET_FULL_RECT)
    add_child(center)
    var panel := PanelContainer.new()
    panel.add_theme_stylebox_override("panel", _plate("panel", 20, 16))
    panel.custom_minimum_size.x = minf(820.0, vw.x - 40.0)
    center.add_child(panel)
    var box := VBoxContainer.new()
    box.add_theme_constant_override("separation", 12)
    panel.add_child(box)
    var head := HBoxContainer.new()
    box.add_child(head)
    var h := _label("Play online", 26, PARCH, true)
    h.add_theme_font_override("font", _font_head)
    h.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    head.add_child(h)
    head.add_child(_plate_button("Back", func(): show_title(), "iron", false, 15, 16, 7))
    if msg != "":
        box.add_child(_ol_note(msg))
    if net == null or not net.configured():
        box.add_child(_ol_note("Online play isn't set up on this copy of the game yet. It needs the online database's address and key in data/online.json."))
        return
    var cols := HBoxContainer.new()
    cols.add_theme_constant_override("separation", 12)
    box.add_child(cols)
    var nb := _ol_box()
    cols.add_child(nb)
    var nv: VBoxContainer = nb.get_child(0)
    nv.add_child(_fsx_l("New game"))
    nv.add_child(_label("Set it up like a game against the computer: your side and color, your friend's side, then the map. You get a code to send them.", 14, Color("cdbf9c")))
    var setup := _plate_button("Set up a new game", func(): _online_setup(), "gold", false, 17, 18, 8)
    nv.add_child(setup)
    var jb := _ol_box()
    cols.add_child(jb)
    var jv: VBoxContainer = jb.get_child(0)
    jv.add_child(_fsx_l("Join a game"))
    jv.add_child(_label("Enter the 4-letter code your friend sent you.", 14, Color("cdbf9c")))
    var row := HBoxContainer.new()
    row.add_theme_constant_override("separation", 8)
    jv.add_child(row)
    var le := LineEdit.new()
    le.max_length = 4
    le.placeholder_text = "ABCD"
    le.alignment = HORIZONTAL_ALIGNMENT_CENTER
    le.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    le.add_theme_font_override("font", _font_bold)
    le.add_theme_font_size_override("font_size", 24)
    le.add_theme_color_override("font_color", Color("f6e7bf"))
    var les := StyleBoxFlat.new()
    les.bg_color = Color(0.047, 0.035, 0.024, 0.85)
    les.border_color = BRONZE
    les.set_border_width_all(2)
    les.set_corner_radius_all(4)
    les.set_content_margin_all(6)
    le.add_theme_stylebox_override("normal", les)
    le.add_theme_stylebox_override("focus", les)
    le.text_changed.connect(func(tx):
        var up: String = tx.to_upper()
        if up != tx:
            var c: int = le.caret_column
            le.text = up
            le.caret_column = c)
    le.text_submitted.connect(func(tx): _net_join(tx))
    row.add_child(le)
    row.add_child(_plate_button("Join", func(): _net_join(le.text), "gold", false, 17, 18, 8))
    box.add_child(_fsx_l("Your games"))
    var list := VBoxContainer.new()
    list.add_theme_constant_override("separation", 6)
    box.add_child(list)
    list.add_child(_label("Looking…", 14, Color("bfae88")))
    _ol_fill(list)


func _ol_box() -> PanelContainer:
    var p := PanelContainer.new()
    var sb := StyleBoxFlat.new()
    sb.bg_color = Color(0.047, 0.035, 0.024, 0.6)
    sb.border_color = Color("6b4d1c")
    sb.set_border_width_all(1)
    sb.set_corner_radius_all(4)
    sb.set_content_margin_all(12)
    p.add_theme_stylebox_override("panel", sb)
    p.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    var v := VBoxContainer.new()
    v.add_theme_constant_override("separation", 8)
    p.add_child(v)
    return p


func _ol_note(text: String) -> Control:
    var p := _ol_box()
    p.get_child(0).add_child(_label(text, 14, PARCH))
    return p


## Your games, newest first, each with Open (and Remove once it's over or nobody joined).
func _ol_fill(list: VBoxContainer) -> void:
    var games: Array = await net.my_games()
    if not is_instance_valid(list):
        return
    for c in list.get_children():
        c.queue_free()
    if games.is_empty():
        list.add_child(_label("Games you create or join show up here, so you can come back to them.", 14, Color("bfae88")))
        return
    for gd in games:
        var seat: int = 0 if String(gd.host) == net.my_id else 1
        var mine: String = String(gd.host_faction if seat == 0 else gd.get("guest_faction", ""))
        var theirs: String = String(gd.get("guest_faction", "") if seat == 0 else gd.host_faction)
        var st: String = String(gd.status)
        var due: bool = st == "playing" and int(gd.get("cur", 0)) == seat
        var line: String = "Waiting for your friend to join" if st == "waiting" else (("You won" if int(gd.get("winner", -1)) == seat else "You lost") if st == "over" else ("Your turn" if due else "Their turn"))
        var row := HBoxContainer.new()
        row.add_theme_constant_override("separation", 10)
        list.add_child(row)
        var code := _label(String(gd.code), 18, Color("e9c66a"), true)
        code.custom_minimum_size.x = 64
        row.add_child(code)
        var tx := _rich("[b]You play the %s[/b]  [color=#bfae88]vs the %s · turn %d · %s[/color]" % [String(GameData.factions.get(mine, {}).get("name", mine)), String(GameData.factions.get(theirs, {}).get("name", theirs)), int(gd.get("turn", 1)), line], 14)
        tx.add_theme_color_override("default_color", Color("f0dcaa"))
        tx.size_flags_vertical = Control.SIZE_SHRINK_CENTER
        row.add_child(tx)
        var cc: String = String(gd.code)
        row.add_child(_plate_button("Show code" if st == "waiting" else "Open", func(): _net_open_code(cc), "gold" if due else "iron", false, 14, 12, 5))
        if st != "playing":
            row.add_child(_plate_button("Remove", func(): _net_remove(cc), "iron", false, 14, 12, 5))


func _online_setup() -> void:
    _np_keep = pref_np
    pref_np = 2
    fs_online = true
    fs_tab = 0
    show_factions()


## Makes the game (the maker plays first) and shows its code.
func _net_create() -> void:
    var gs := GameState.new()
    var mp: Dictionary = GameData.map_by_id(pref_map) if pref_map != "" else {}
    gs.new_game(my_faction, [], _opponent_for(my_faction), 2, pref_opps, pref_map if (not mp.is_empty() and int(mp.get("players", 0)) == 2) else "")
    gs.arena_fights = true
    for p in gs.players:   # both sides by their faction's name (the log reads the same on both computers), and both people
        p["name"] = String(GameData.factions[p.faction].name)
        p["ai"] = false
        p["gold_bonus"] = 0.0
    g = gs
    _apply_colors()
    g = null
    gs.log_lines = []
    gs.add_log("A new age begins online: the %s against the %s. Win by taking their home castle, holding %d castles, or wiping them off the map." % [String(gs.players[0].name), String(gs.players[1].name), gs.win_castles()])
    gs.begin_turn()
    var js: String = JSON.stringify(gs.snapshot())
    var now: int = int(Time.get_unix_time_from_system() * 1000.0)
    var fs_was: bool = fs_online
    fs_online = false
    pref_np = _np_keep
    for attempt in 8:
        var code: String = net.new_code()
        var r: Dictionary = await net.create({"code": code, "host": net.my_id, "host_faction": String(gs.players[0].faction), "guest_faction": String(gs.players[1].faction),
            "status": "waiting", "rev": 1, "state": js, "cur": 0, "turn": 1, "created": now, "updated": now})
        if r.ok:
            _online_wait(code)
            return
        if int(r.status) != 409:   # 409: that code is taken, try another
            show_online("The game couldn't be made (%s). Check the internet connection and try again." % ("error %d" % int(r.status) if int(r.status) > 0 else "no connection"))
            return
    show_online("The game couldn't be made. Try again.")


## Your code, big, while you wait for the friend to join (you can leave: the game stays under Your games).
func _online_wait(code: String) -> void:
    _clear()
    g = null
    online = {"code": code, "seat": 0, "waiting": true}
    _painting("res://art/ui/title_battle_dim.jpg")
    var center := CenterContainer.new()
    center.set_anchors_preset(Control.PRESET_FULL_RECT)
    add_child(center)
    var panel := PanelContainer.new()
    panel.add_theme_stylebox_override("panel", _plate("panel", 28, 22))
    panel.custom_minimum_size.x = minf(640.0, get_viewport_rect().size.x - 40.0)
    center.add_child(panel)
    var box := VBoxContainer.new()
    box.add_theme_constant_override("separation", 12)
    box.alignment = BoxContainer.ALIGNMENT_CENTER
    panel.add_child(box)
    var sub := _label("Your game code", 15, Color("bfae88"))
    sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    box.add_child(sub)
    var big := _gold_title(72)
    (big.get_child(0) as Label).text = code
    big.get_child(1).queue_free()
    big.get_child(2).queue_free()
    box.add_child(big)
    var tx := _label("Send your friend this code. They open the game, tap Play online, enter it, and the game starts. You move first.", 15, PARCH)
    tx.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    box.add_child(tx)
    var tx2 := _label("Waiting for them to join… You can leave this screen: the game will be under Your games.", 14, Color("bfae88"))
    tx2.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    box.add_child(tx2)
    var btns := HBoxContainer.new()
    btns.alignment = BoxContainer.ALIGNMENT_CENTER
    btns.add_theme_constant_override("separation", 10)
    box.add_child(btns)
    btns.add_child(_plate_button("Back to Play online", func(): show_online(), "iron", false, 15, 16, 7))
    btns.add_child(_plate_button("Cancel this game", func(): _net_remove(code), "iron", false, 15, 16, 7))


func _net_join(raw: String) -> void:
    var code: String = ""
    for ch in raw.to_upper():
        if ch >= "A" and ch <= "Z":
            code += ch
    if code.length() != 4:
        show_online("A game code is 4 letters.")
        return
    var d: Dictionary = await net.get_game(code)
    if d.is_empty():
        show_online("There's no game with the code %s. Check the letters with your friend." % code)
        return
    if String(d.host) == net.my_id:
        if String(d.status) == "waiting":
            _online_wait(code)
        else:
            _net_open(d, 0)
        return
    if d.get("guest") != null and String(d.guest) == net.my_id:
        _net_open(d, 1)
        return
    if d.get("guest") != null:
        show_online("Game %s already has two players." % code)
        return
    var j: Dictionary = await net.join(code, {"guest": net.my_id, "status": "playing", "rev": int(d.rev) + 1, "updated": int(Time.get_unix_time_from_system() * 1000.0)})
    if j.is_empty():
        show_online("Someone else just joined game %s." % code)
        return
    _net_open(j, 1)


func _net_open_code(code: String) -> void:
    var d: Dictionary = await net.get_game(code)
    if d.is_empty():
        show_online("That game isn't there any more.")
        return
    if String(d.status) == "waiting" and String(d.host) == net.my_id:
        _online_wait(code)
        return
    var seat: int = 0 if String(d.host) == net.my_id else (1 if (d.get("guest") != null and String(d.guest) == net.my_id) else -1)
    if seat < 0:
        show_online("You aren't a player in game %s." % code)
        return
    _net_open(d, seat)


## Opens the stored game on this computer: turned round for the friend, so you are player 0 here.
func _net_open(d: Dictionary, seat: int) -> void:
    var st = JSON.parse_string(String(d.get("state", "")))
    if not (st is Dictionary):
        show_online("That game's board couldn't be read.")
        return
    st = GameState.ints(st)
    if seat == 1:
        st = net.swap_seats(st)
    for p in st.players:
        p["ai"] = false
    online = {"code": String(d.code), "seat": seat, "rev": int(d.rev), "json": String(d.state), "last_cur": int(st.current)}
    my_faction = String(st.players[0].faction)
    start_game(my_faction, st)
    online.json = _net_json()   # what's on the screen now is what's stored: nothing to send yet


## The board changed on your turn (or you just ended it): send it, a moment later so a burst of changes goes as one.
func _net_push_soon() -> void:
    if g == null or online.is_empty() or online.get("waiting", false):
        return
    if g.current != 0 and int(online.get("last_cur", 0)) != 0:
        return   # their turn, and you didn't just hand it over: they are the one sending
    _net_push.call_deferred()


func _net_push() -> void:
    if g == null or online.is_empty() or busy:
        return
    if _net_pushing:
        _net_again = true
        return
    var st: Dictionary = _net_state()
    var js: String = JSON.stringify(st)
    if js == String(online.get("json", "")):
        return
    _net_pushing = true
    var rev: int = int(online.rev)
    var fields: Dictionary = {"state": js, "rev": rev + 1, "cur": int(st.current), "turn": int(st.turn), "updated": int(Time.get_unix_time_from_system() * 1000.0),
        "status": "over" if int(st.over) >= 0 else "playing", "winner": int(st.over) if int(st.over) >= 0 else null}
    var code: String = String(online.code)
    var r: Dictionary = await net.push(code, rev, fields)
    _net_pushing = false
    if online.is_empty() or String(online.get("code", "")) != code:
        return
    if r.is_empty():   # someone stored a newer board: take theirs
        await _net_fetch()
    else:
        online.rev = rev + 1
        online.json = js
        online.last_cur = g.current if g != null else 0
    if _net_again:
        _net_again = false
        _net_push()


## Every 2.5 s: while waiting for a friend to join, or while it's their turn, look for a newer board.
func _net_tick() -> void:
    if online.is_empty() or _net_fetching or _net_pushing or _net_ticking or net == null:
        return
    _net_ticking = true
    await _net_look()
    _net_ticking = false


func _net_look() -> void:
    var code: String = String(online.code)
    if online.get("waiting", false):
        var pk: Dictionary = await net.peek(code)
        if not online.is_empty() and online.get("waiting", false) and String(online.code) == code and String(pk.get("status", "")) == "playing":
            _net_open_code(code)
        return
    if g == null or busy or overlay != null:
        return
    if g.current == 0 and int(online.get("last_cur", 0)) == 0 and g.over < 0:
        return   # your turn: you are the one sending
    var p: Dictionary = await net.peek(code)
    if online.is_empty() or String(online.get("code", "")) != code or g == null:
        return
    if g.current == 0 and int(online.get("last_cur", 0)) == 0 and g.over < 0:
        return   # it became your turn while looking
    if not p.is_empty() and int(p.rev) > int(online.rev):
        await _net_fetch()


func _net_fetch() -> void:
    if online.is_empty() or _net_fetching:
        return
    _net_fetching = true
    var code: String = String(online.code)
    var d: Dictionary = await net.get_game(code)
    _net_fetching = false
    if d.is_empty() or online.is_empty() or String(online.get("code", "")) != code or g == null or busy:
        return
    if int(d.rev) <= int(online.rev):
        return   # nothing newer than what's on the screen
    var st = JSON.parse_string(String(d.get("state", "")))
    if not (st is Dictionary):
        return
    st = GameState.ints(st)
    if int(online.seat) == 1:
        st = net.swap_seats(st)
    for p in st.players:
        p["ai"] = false
    var was_mine: bool = g.current == 0
    g.restore(st)
    g.arena_fights = true
    online.rev = int(d.rev)
    online.json = _net_json()
    online.last_cur = g.current
    if g.current == 0 and not was_mine:   # your turn now
        sel = -1
        preview = ""
        notes = []
        undo_stack = []
    refresh()


## The board as it's stored (from the maker's side).
func _net_state() -> Dictionary:
    var st: Dictionary = g.snapshot()
    return net.swap_seats(st) if int(online.get("seat", 0)) == 1 else st


func _net_json() -> String:
    return JSON.stringify(_net_state()) if g != null else ""


## While it's the friend's turn: a plate at the top of the map saying so (their moves show up as they make them).
var _net_plate: PanelContainer = null

func _net_badge() -> void:
    var want: bool = not online.is_empty() and g != null and g.current != 0 and g.over < 0
    if not want:
        if is_instance_valid(_net_plate):
            _net_plate.visible = false
        return
    if not is_instance_valid(_net_plate):
        _net_plate = PanelContainer.new()
        _net_plate.add_theme_stylebox_override("panel", _plate("panel", 14, 6))
        _net_plate.mouse_filter = Control.MOUSE_FILTER_IGNORE
        var l := _label("", 16, PARCH, true)
        l.name = "L"
        _net_plate.add_child(l)
        add_child(_net_plate)
    _net_plate.visible = true
    (_net_plate.get_node("L") as Label).text = "The %s (your friend) are playing their turn…" % String(g.players[g.current].name)
    _net_plate.reset_size()
    _net_plate.position = Vector2((board.size.x - _net_plate.size.x) / 2.0 if board != null else 20.0, 10.0)


func _net_leave() -> void:
    online = {}
    show_online()


func _net_remove(code: String) -> void:
    await net.remove(code)
    show_online()


# =====================================================================
# The map's place on the screen
# =====================================================================''')
f.rep('''    _place_bubbles()
    _stats()''', '''    _place_bubbles()
    _stats()
    _net_badge()''')
f.save()
print('ok')

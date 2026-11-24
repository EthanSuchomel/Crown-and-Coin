"""Ethan, 2026-11-23: "create an intermediate page for after the finished game and before the next game. Player 2 and on
have to ready up before the next game starts, they can change their faction and see what map the next game is on. Also
give the online opponent the choice of faction and color and add a ready button."
The online game gets a lobby (the game's row has status "lobby" and state {"lobby": L}):
  L = {map, host: {f, c}, guest: {f, c, ready}, score: [host wins, guest wins], last: winner seat or -1, round}
- Making a game (the setup tabs: your side, colour and the map; the friend picks their own) opens the lobby with the code.
- Joining puts the friend in the lobby with a free faction and colour. There they pick their faction and colour (not the
  maker's), see the next map, and press Ready. The maker can change their own side, colour and the map (that un-readies
  the friend), and starts the game once the friend is ready.
- After a game, Next game (on the end panel) takes either player back to the lobby: the score goes up, the round
  number too, and the friend has to ready up again (they can change faction first).
- While playing, the lobby rides along in the stored board ({"lobby": L} next to the game), so the next round keeps it.
Usage: python3 p11_lobby.py PROJ   (after p7_online.py)"""
import sys, re
sys.path.insert(0, __file__.rsplit('/', 2)[0] + '/godot-port-nov22')
from common import F, T
P = sys.argv[1]
f = F(P + '/scripts/ui/main.gd')

# ---- the setup screen: the friend picks their own side
f.rep('''    var sum := _rich(("[color=#e9c66a][b]Online[/b][/color] · %s vs %s (a friend) · %s" % [who[0], who[1], map_name]) if fs_online''',
      '''    var sum := _rich(("[color=#e9c66a][b]Online[/b][/color] · %s vs a friend · %s" % [who[0], map_name]) if fs_online''')
f.rep('''    var rivals: Array = sides.facs.slice(1)
    for k in rivals.size():''', '''    var rivals: Array = sides.facs.slice(1)
    if fs_online:   # the friend picks their own faction and colour in the game's lobby (2026-11-23)
        body.add_child(_ol_note("Your friend picks their own faction and colour when they join, then readies up. You start the game from the lobby."))
        return
    for k in rivals.size():''')

# ---- making a game: straight to the lobby
s = f.s
a = s.index('## Makes the game (the maker plays first) and shows its code.\nfunc _net_create() -> void:')
b = s.index('## Your code, big, while you wait for the friend to join')
f.s = s[:a] + T('''## Makes the game in its lobby (2026-11-23): your side, colour and the map; the friend joins with the code.
func _net_create() -> void:
    var sides: Dictionary = _fsx_sides()
    var mp: Dictionary = GameData.map_by_id(pref_map) if pref_map != "" else {}
    var L: Dictionary = {"map": pref_map if (not mp.is_empty() and int(mp.get("players", 0)) == 2) else "",
        "host": {"f": my_faction, "c": String(sides.cols[0])}, "guest": {"f": "", "c": "", "ready": false},
        "score": [0, 0], "last": -1, "round": 1}
    var now: int = int(Time.get_unix_time_from_system() * 1000.0)
    fs_online = false
    pref_np = _np_keep
    for attempt in 8:
        var code: String = net.new_code()
        var r: Dictionary = await net.create({"code": code, "host": net.my_id, "host_faction": my_faction, "guest_faction": "",
            "status": "lobby", "rev": 1, "state": JSON.stringify({"lobby": L}), "cur": 0, "turn": 1, "created": now, "updated": now})
        if r.ok:
            online = {"code": code, "seat": 0, "rev": 1, "lobby": L, "joined": false, "in_lobby": true}
            show_lobby()
            return
        if int(r.status) != 409:   # 409: that code is taken, try another
            show_online("The game couldn't be made. The online database said: %s" % String(r.err))
            return
    show_online("The game couldn't be made. Try again.")


''') + s[b:]

# ---- joining: into the lobby
f.rep('''    if String(d.host) == net.my_id:
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
        return''', '''    if String(d.host) == net.my_id:
        if String(d.status) == "waiting":
            _online_wait(code)
        else:
            _net_open_any(d, 0)
        return
    if d.get("guest") != null and String(d.guest) == net.my_id:
        _net_open_any(d, 1)
        return
    if d.get("guest") != null:
        show_online("Game %s already has two players." % code)
        return
    if String(d.status) == "lobby":   # take the free seat with a free faction and colour; then pick and ready up
        var st0 = JSON.parse_string(String(d.get("state", "")))
        var L: Dictionary = (st0.get("lobby", {}) if st0 is Dictionary else {}).duplicate(true)
        if L.is_empty():
            show_online("That game's lobby couldn't be read.")
            return
        var hf: String = String(L.host.f)
        var gf: String = my_faction if (GameData.factions.has(my_faction) and my_faction != hf) else _opponent_for(hf)
        var gc: String = _my_color_for(gf)
        if gc == String(L.host.c):
            gc = _other_color([String(L.host.c)], gf)
        L["guest"] = {"f": gf, "c": gc, "ready": false}
        var jl: Dictionary = await net.join(code, {"guest": net.my_id, "guest_faction": gf, "state": JSON.stringify({"lobby": L}),
            "rev": int(d.rev) + 1, "updated": int(Time.get_unix_time_from_system() * 1000.0)})
        if jl.is_empty():
            show_online("Someone else just joined game %s." % code)
            return
        online = {"code": code, "seat": 1}
        _lobby_load(jl)
        show_lobby()
        return''')
f.rep('''    if String(d.status) == "waiting" and String(d.host) == net.my_id:
        _online_wait(code)
        return
    var seat: int = 0 if String(d.host) == net.my_id else (1 if (d.get("guest") != null and String(d.guest) == net.my_id) else -1)
    if seat < 0:
        show_online("You aren't a player in game %s." % code)
        return
    _net_open(d, seat)''', '''    if String(d.status) == "waiting" and String(d.host) == net.my_id:
        _online_wait(code)
        return
    var seat: int = 0 if String(d.host) == net.my_id else (1 if (d.get("guest") != null and String(d.guest) == net.my_id) else -1)
    if seat < 0:
        show_online("You aren't a player in game %s." % code)
        return
    _net_open_any(d, seat)


## A game in its lobby opens the lobby; a game being played (or just over) opens the board.
func _net_open_any(d: Dictionary, seat: int) -> void:
    if String(d.get("status", "")) == "lobby":
        online = {"code": String(d.code), "seat": seat}
        _lobby_load(d)
        show_lobby()
    else:
        _net_open(d, seat)''')

# the board carries its lobby
f.rep('''    if seat == 1:
        st = net.swap_seats(st)
    for p in st.players:
        p["ai"] = false
    online = {"code": String(d.code), "seat": seat, "rev": int(d.rev), "json": String(d.state), "last_cur": int(st.current)}''',
'''    if not st.has("players"):
        show_online("That game hasn't started yet.")
        return
    var lob: Dictionary = st.get("lobby", {})
    if seat == 1:
        st = net.swap_seats(st)
    for p in st.players:
        p["ai"] = false
    online = {"code": String(d.code), "seat": seat, "rev": int(d.rev), "json": String(d.state), "last_cur": int(st.current), "lobby": lob}''')
f.rep('''func _net_state() -> Dictionary:
    var st: Dictionary = g.snapshot()
    return net.swap_seats(st) if int(online.get("seat", 0)) == 1 else st''', '''func _net_state() -> Dictionary:
    var st: Dictionary = g.snapshot()
    if int(online.get("seat", 0)) == 1:
        st = net.swap_seats(st)
    if not Dictionary(online.get("lobby", {})).is_empty():
        st["lobby"] = online.lobby
    return st''')
# a board fetched after the other side went back to the lobby: nothing to load
f.rep('''    if int(d.rev) <= int(online.rev):
        return   # nothing newer than what's on the screen''', '''    if int(d.rev) <= int(online.rev):
        return   # nothing newer than what's on the screen
    if String(d.get("status", "")) == "lobby":   # the other side went on to the next game: Next game takes you there
        online.rev = int(d.rev)
        online["next_open"] = true
        return''')
# the poll: lobby
f.rep('''func _net_look() -> void:
    var code: String = String(online.code)''', '''func _net_look() -> void:
    var code: String = String(online.code)
    if online.get("in_lobby", false):
        await _lobby_look(code)
        return''')
# the end of a game: Next game
f.rep('''    var again := _button("Play again", func(): show_factions(), true)
    again.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
    vb.add_child(again)
    body.add_child(p)''', '''    if not online.is_empty():   # online: back to the lobby for the next game (2026-11-23)
        var nx := _plate_button("Next game", func(): _net_next(), "gold", false, 18, 22, 8)
        nx.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
        vb.add_child(nx)
        var sub := _label("Back to the lobby: the score, the next map, and a new pick of sides", 13, BONE)
        sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
        vb.add_child(sub)
        body.add_child(p)
        return
    var again := _button("Play again", func(): show_factions(), true)
    again.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
    vb.add_child(again)
    body.add_child(p)''')
# Your games: games in their lobby
f.rep('''        var line: String = "Waiting for your friend to join" if st == "waiting" else''',
      '''        var line: String = ("In the lobby" if gd.get("guest") != null else "Waiting for your friend to join") if st == "lobby" else "Waiting for your friend to join" if st == "waiting" else''')
f.rep('''        var tx := _rich("[b]You play the %s[/b]  [color=#bfae88]vs the %s · turn %d · %s[/color]" % [String(GameData.factions.get(mine, {}).get("name", mine)), String(GameData.factions.get(theirs, {}).get("name", theirs)), int(gd.get("turn", 1)), line], 14)''',
      '''        var tx := _rich(("[b]You play the %s[/b]  [color=#bfae88]%s[/color]" % [String(GameData.factions.get(mine, {}).get("name", mine)), line]) if st == "lobby" else ("[b]You play the %s[/b]  [color=#bfae88]vs the %s · turn %d · %s[/color]" % [String(GameData.factions.get(mine, {}).get("name", mine)), String(GameData.factions.get(theirs, {}).get("name", theirs)), int(gd.get("turn", 1)), line]), 14)''')
f.rep('''        row.add_child(_plate_button("Show code" if st == "waiting" else "Open", func(): _net_open_code(cc), "gold" if due else "iron", false, 14, 12, 5))''',
      '''        row.add_child(_plate_button("Show code" if st == "waiting" else "Open", func(): _net_open_code(cc), "gold" if (due or st == "lobby") else "iron", false, 14, 12, 5))''')

# ---- the lobby itself
f.rep('''## The board as it's stored (from the maker's side).''', '''# ---------------------------------------------------------------------
# The lobby (Ethan, 2026-11-23): before the first game and between games
# ---------------------------------------------------------------------

## Takes the lobby out of a stored row into online (rev, joined, the lobby).
func _lobby_load(d: Dictionary) -> void:
    var st = JSON.parse_string(String(d.get("state", "")))
    var L = st.get("lobby", {}) if st is Dictionary else {}
    online["lobby"] = GameState.ints(L) if L is Dictionary else {}
    online["rev"] = int(d.get("rev", 1))
    online["joined"] = d.get("guest") != null
    online["in_lobby"] = true
    online.erase("next_wait")


## The lobby page: the score, both sides' factions and colours, the next map, and Ready (the friend) or Start (the maker).
func show_lobby() -> void:
    _clear()
    g = null
    var L: Dictionary = online.get("lobby", {})
    if L.is_empty():
        show_online("That game's lobby couldn't be read.")
        return
    var me: int = int(online.seat)
    var mine: Dictionary = L.host if me == 0 else L.guest
    var theirs: Dictionary = L.guest if me == 0 else L.host
    var joined: bool = bool(online.get("joined", me == 1))
    _painting("res://art/ui/title_battle_dim.jpg")
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
    var col := VBoxContainer.new()
    col.custom_minimum_size.x = minf(940.0, vw.x - 32.0)
    col.add_theme_constant_override("separation", 10)
    center.add_child(col)
    # the head: the game, the round and the score
    var head := HBoxContainer.new()
    head.add_theme_constant_override("separation", 12)
    col.add_child(head)
    var h := _label("Game %s" % String(online.code), 26, PARCH, true)
    h.add_theme_font_override("font", _font_head)
    h.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.9))
    h.add_theme_constant_override("shadow_offset_y", 2)
    head.add_child(h)
    var rnd: int = int(L.get("round", 1))
    var sc: Array = L.get("score", [0, 0])
    var last: int = int(L.get("last", -1))
    var info: String = "Round %d" % rnd
    if rnd > 1:
        info = "Round %d  ·  [color=#e9c66a][b]You %d – %d Your friend[/b][/color]" % [rnd, int(sc[me]), int(sc[1 - me])]
        if last >= 0:
            info += "  ·  " + ("you won the last game" if last == me else "your friend won the last game")
    var ir := _rich(info, 15)
    ir.add_theme_color_override("default_color", Color("d9c79c"))
    ir.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    ir.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    ir.autowrap_mode = TextServer.AUTOWRAP_OFF
    head.add_child(ir)
    head.add_child(_plate_button("Leave", func(): show_online(), "iron", false, 15, 16, 7))
    # the panel
    var panel := PanelContainer.new()
    panel.add_theme_stylebox_override("panel", _plate("panel", 18, 14))
    panel.size_flags_vertical = Control.SIZE_EXPAND_FILL
    col.add_child(panel)
    var scroll := ScrollContainer.new()
    scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
    panel.add_child(scroll)
    var body := VBoxContainer.new()
    body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    body.add_theme_constant_override("separation", 10)
    scroll.add_child(body)
    if me == 0 and not joined:
        var cb := _ol_box()
        body.add_child(cb)
        var cv: VBoxContainer = cb.get_child(0)
        var crow := HBoxContainer.new()
        crow.add_theme_constant_override("separation", 16)
        cv.add_child(crow)
        var big := _gold_title(48)
        (big.get_child(0) as Label).text = String(online.code)
        big.get_child(1).queue_free()
        big.get_child(2).queue_free()
        crow.add_child(big)
        var ct := _label("Send your friend this code. They open the game, tap Play online and enter it, then pick their side and ready up here.", 15, PARCH)
        ct.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
        ct.size_flags_horizontal = Control.SIZE_EXPAND_FILL
        ct.size_flags_vertical = Control.SIZE_SHRINK_CENTER
        crow.add_child(ct)
    if online.get("next_wait", false):
        body.add_child(_ol_note("Getting the next game ready…"))
    # both sides
    var sides := HBoxContainer.new()
    sides.add_theme_constant_override("separation", 12)
    body.add_child(sides)
    var yb := _ol_box()
    sides.add_child(yb)
    yb.size_flags_stretch_ratio = 1.6
    var yv: VBoxContainer = yb.get_child(0)
    yv.add_child(_fsx_l("You", ("ready" if bool(mine.get("ready", false)) else "not ready yet") if me == 1 else "you start the game"))
    var facs := HBoxContainer.new()
    facs.add_theme_constant_override("separation", 8)
    yv.add_child(facs)
    for fid in GameData.factions.order:
        var ff: String = fid
        var tile := _fac_tile(fid, fid == String(mine.f), false, func(): _lobby_pick_faction(ff))
        if fid == String(theirs.get("f", "")):   # your friend's faction: taken
            tile.disabled = true
            tile.modulate = Color(1, 1, 1, 0.35)
            tile.tooltip_text = "Your friend plays this one"
        facs.add_child(tile)
    yv.add_child(_swatches(String(mine.c), [String(theirs.get("c", ""))] if String(theirs.get("c", "")) != "" else [], func(c): _lobby_pick_color(c)))
    var fb := _ol_box()
    sides.add_child(fb)
    var fv: VBoxContainer = fb.get_child(0)
    if me == 0 and not joined:
        fv.add_child(_fsx_l("Your friend", "not joined yet"))
        fv.add_child(_label("They'll pick their own faction and colour.", 14, Color("bfae88")))
    else:
        var rd: bool = bool(L.guest.get("ready", false))
        fv.add_child(_fsx_l("Your friend", ("ready" if rd else "not ready yet") if me == 0 else "starts the game"))
        var tf: String = String(theirs.get("f", ""))
        if GameData.factions.has(tf):
            var trow := HBoxContainer.new()
            trow.add_theme_constant_override("separation", 10)
            fv.add_child(trow)
            trow.add_child(_pic("res://art/terrain/castle_%s.png" % tf, Vector2(86, 60)))
            var tv := VBoxContainer.new()
            tv.size_flags_vertical = Control.SIZE_SHRINK_CENTER
            trow.add_child(tv)
            var nm := _label(String(GameData.factions[tf].name), 18, Color(String(GameData.factions[tf].ink)), true)
            nm.add_theme_font_override("font", _font_head)
            tv.add_child(nm)
            var tc: String = String(theirs.get("c", ""))
            if COLORS.has(tc):
                tv.add_child(_rich("[color=%s]●[/color] %s" % [String(COLORS[tc].color), String(COLORS[tc].name)], 15))
        if me == 0:
            var badge := _label("✔  Ready" if rd else "Waiting for them to ready up", 16, Color("8fe3a0") if rd else Color("e8c060"), true)
            fv.add_child(badge)
    # the next map
    var mid: String = String(L.get("map", ""))
    body.add_child(_fsx_l("Next map", "the maker picks" if me == 1 else "tap one to change"))
    var flow := HFlowContainer.new()
    flow.add_theme_constant_override("h_separation", 10)
    flow.add_theme_constant_override("v_separation", 10)
    body.add_child(flow)
    var hexcols: Array = []
    for s2 in [L.host, L.guest]:
        hexcols.append(String(COLORS[String(s2.c)].color) if COLORS.has(String(s2.get("c", ""))) else "#888888")
    var entries: Array = [{"id": "", "name": "Random"}] + GameData.maps_for(2)
    for entry in entries:
        var eid: String = String(entry.id)
        if me == 1 and eid != mid:
            continue   # the friend sees just the next map
        flow.add_child(_lobby_map_tile(entry, eid == mid, hexcols, func(): _lobby_pick_map(eid)))
    var rules := _ol_box()
    body.add_child(rules)
    var rr := _rich(_win_list_bb(2, mid), 14)
    rr.add_theme_color_override("default_color", Color("cdbf9c"))
    rules.get_child(0).add_child(rr)
    # the foot: Ready (the friend) or Start (the maker)
    var foot := HBoxContainer.new()
    foot.add_theme_constant_override("separation", 10)
    foot.alignment = BoxContainer.ALIGNMENT_END
    col.add_child(foot)
    var hint := _label("", 14, Color("d9c79c"))
    hint.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    hint.size_flags_vertical = Control.SIZE_SHRINK_CENTER
    foot.add_child(hint)
    if me == 0:
        var can: bool = joined and bool(L.guest.get("ready", false))
        hint.text = "Start when your friend is ready." if can else ("Waiting for your friend to join." if not joined else "Waiting for your friend to ready up.")
        var go := _plate_button("Start game", func(): _lobby_start(), "gold", false, 19, 24, 8)
        go.disabled = not can
        if not can:
            go.modulate = Color(1, 1, 1, 0.45)
        foot.add_child(go)
    else:
        var rd2: bool = bool(L.guest.get("ready", false))
        hint.text = "Your friend starts the game once you're ready." if rd2 else "Pick your faction and colour, then ready up."
        foot.add_child(_plate_button("Not ready" if rd2 else "Ready", func(): _lobby_change(func(X): X.guest["ready"] = not bool(X.guest.get("ready", false))), "iron" if rd2 else "gold", false, 19, 24, 8))


## A map tile in the lobby (as on the setup screen).
func _lobby_map_tile(entry: Dictionary, on: bool, hexcols: Array, f: Callable) -> Button:
    var mid: String = String(entry.id)
    var b := _plate_button("", f, "tile", on, 14, 6, 6)
    b.custom_minimum_size = Vector2(140, 140)
    var vb := VBoxContainer.new()
    vb.set_anchors_preset(Control.PRESET_FULL_RECT)
    vb.alignment = BoxContainer.ALIGNMENT_CENTER
    vb.add_theme_constant_override("separation", 2)
    b.add_child(vb)
    if mid == "":
        var q := _label("?", 42, Color("f0dcaa"), true)
        q.add_theme_font_override("font", _font_head)
        q.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
        q.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
        q.custom_minimum_size.y = 78
        vb.add_child(q)
    else:
        var th := MapThumb.new()
        th.rows = entry.rows
        th.coins = entry.get("coins", [])
        th.cols = hexcols
        th.custom_minimum_size = Vector2(122, 78)
        th.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
        vb.add_child(th)
    var nm := _label(String(entry.name), 15, Color("f0dcaa"), true)
    nm.add_theme_font_override("font", _font_head)
    nm.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    nm.clip_text = true
    nm.custom_minimum_size.x = 126
    vb.add_child(nm)
    var need: int = _win_castles_for(2, mid)
    var sm := _label("a new map each game" if mid == "" else (("%d castles to win" % need) if need > 0 else "last side standing"), 12, Color("bfae88"))
    sm.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    vb.add_child(sm)
    _ignore_mouse(vb)
    return b


func _lobby_pick_faction(fid: String) -> void:
    var me: int = int(online.seat)
    await _lobby_change(func(X):
        var other: Dictionary = X.guest if me == 0 else X.host
        if String(other.get("f", "")) == fid:
            return
        var mine: Dictionary = X.host if me == 0 else X.guest
        mine["f"] = fid
        X.guest["ready"] = false)


func _lobby_pick_color(c: String) -> void:
    var me: int = int(online.seat)
    await _lobby_change(func(X):
        var other: Dictionary = X.guest if me == 0 else X.host
        if String(other.get("c", "")) == c:
            return
        var mine: Dictionary = X.host if me == 0 else X.guest
        mine["c"] = c
        X.guest["ready"] = false)


func _lobby_pick_map(mid: String) -> void:
    if int(online.seat) != 0:
        return
    await _lobby_change(func(X):
        X["map"] = mid
        X.guest["ready"] = false)


## Changes the lobby (fn edits it) here at once, then stores it; if the other side stored a change first, takes
## theirs and makes the changes again on top. Changes made while one is being stored go out right after it.
var _lobby_fns: Array = []

func _lobby_change(fn: Callable) -> void:
    if online.is_empty() or not online.get("in_lobby", false):
        return
    fn.call(online.lobby)
    _lobby_fns.append(fn)
    show_lobby()
    if _net_pushing:
        return
    var code: String = String(online.code)
    _net_pushing = true
    var tries: int = 0
    while not _lobby_fns.is_empty() and tries < 8:
        tries += 1
        var sent: int = _lobby_fns.size()
        var rev: int = int(online.rev)
        var L: Dictionary = online.lobby
        var r: Dictionary = await net.push(code, rev, {"state": JSON.stringify({"lobby": L}), "rev": rev + 1,
            "host_faction": String(L.host.f), "guest_faction": String(L.guest.get("f", "")), "updated": int(Time.get_unix_time_from_system() * 1000.0)})
        if online.is_empty() or String(online.get("code", "")) != code:
            break
        if not r.is_empty():
            online.rev = rev + 1
            _lobby_fns = _lobby_fns.slice(sent)
            continue
        var d: Dictionary = await net.get_game(code)
        if d.is_empty() or online.is_empty() or String(online.get("code", "")) != code:
            break
        if String(d.status) != "lobby":
            _lobby_fns = []
            _net_pushing = false
            _net_open_any(d, int(online.seat))
            return
        _lobby_load(d)
        for f2 in _lobby_fns:
            f2.call(online.lobby)
    _lobby_fns = []
    _net_pushing = false
    if not online.is_empty() and online.get("in_lobby", false) and String(online.get("code", "")) == code:
        show_lobby()


## In the lobby, every 2.5 s: the friend joined or changed something, or the maker started the game.
func _lobby_look(code: String) -> void:
    var p: Dictionary = await net.peek(code)
    if p.is_empty() or online.is_empty() or String(online.get("code", "")) != code or not online.get("in_lobby", false):
        return
    if int(p.rev) <= int(online.rev) and not online.get("next_wait", false):
        return
    var d: Dictionary = await net.get_game(code)
    if d.is_empty() or online.is_empty() or String(online.get("code", "")) != code or not online.get("in_lobby", false) or _net_pushing:
        return
    if String(d.status) == "lobby":
        _lobby_load(d)
        show_lobby()
    elif String(d.status) == "playing":
        _net_open(d, int(online.seat))


## The maker starts the game with both sides' picks and the map.
func _lobby_start() -> void:
    if int(online.seat) != 0 or _net_pushing:
        return
    var L: Dictionary = online.lobby
    if not bool(L.guest.get("ready", false)):
        return
    var code: String = String(online.code)
    var gs := GameState.new()
    var mid: String = String(L.get("map", ""))
    var mp: Dictionary = GameData.map_by_id(mid) if mid != "" else {}
    gs.new_game(String(L.host.f), [], String(L.guest.f), 2, [], mid if (not mp.is_empty() and int(mp.get("players", 0)) == 2) else "")
    gs.arena_fights = true
    for k in 2:   # both people, by their faction's name, in their own colours
        var p: Dictionary = gs.players[k]
        var side: Dictionary = L.host if k == 0 else L.guest
        p["name"] = String(GameData.factions[p.faction].name)
        p["ai"] = false
        p["gold_bonus"] = 0.0
        var cc: String = String(side.c) if COLORS.has(String(side.c)) else _other_color([], String(p.faction))
        p["col"] = cc
        p["color"] = COLORS[cc].color
        p["ink"] = COLORS[cc].ink
    gs.log_lines = []
    gs.add_log("Game %d begins online: the %s against the %s. Win by taking their home castle, holding %d castles, or wiping them off the map." % [int(L.get("round", 1)), String(gs.players[0].name), String(gs.players[1].name), gs.win_castles()])
    gs.begin_turn()
    var st: Dictionary = gs.snapshot()
    st["lobby"] = L
    var js: String = JSON.stringify(st)
    var rev: int = int(online.rev)
    _net_pushing = true
    var r: Dictionary = await net.push(code, rev, {"state": js, "rev": rev + 1, "status": "playing", "cur": 0, "turn": 1, "winner": null,
        "host_faction": String(L.host.f), "guest_faction": String(L.guest.f), "updated": int(Time.get_unix_time_from_system() * 1000.0)})
    _net_pushing = false
    if r.is_empty():   # the lobby changed under us (the friend un-readied?): show it as it is now
        var d: Dictionary = await net.get_game(code)
        if not d.is_empty():
            _net_open_any(d, 0)
        return
    _net_open({"code": code, "rev": rev + 1, "state": js, "status": "playing"}, 0)


## Next game (the end of a game): back to the lobby. The first side to press it turns the finished game into the lobby
## (score and round up, the friend un-readied); the other finds it there.
func _net_next() -> void:
    if online.is_empty():
        show_online()
        return
    var code: String = String(online.code)
    var seat: int = int(online.seat)
    for attempt in 3:
        var d: Dictionary = await net.get_game(code)
        if d.is_empty():
            show_online("That game isn't there any more.")
            return
        if String(d.status) == "lobby":
            online = {"code": code, "seat": seat}
            _lobby_load(d)
            show_lobby()
            return
        var st = JSON.parse_string(String(d.get("state", "")))
        if not (st is Dictionary):
            show_online("That game couldn't be read.")
            return
        st = GameState.ints(st)
        var L: Dictionary = Dictionary(st.get("lobby", {})).duplicate(true)
        if L.is_empty():   # a game from before the lobby: make one from it
            var ps: Array = st.get("players", [])
            L = {"map": String(st.get("map_id", "")), "host": {"f": String(d.host_faction), "c": String(ps[0].get("col", "red")) if ps.size() > 0 else "red"},
                "guest": {"f": String(d.get("guest_faction", "")), "c": String(ps[1].get("col", "blue")) if ps.size() > 1 else "blue", "ready": false},
                "score": [0, 0], "last": -1, "round": 1}
        var w: int = int(d.winner) if d.get("winner") != null else int(st.get("over", -1))
        if w >= 0 and w < 2:
            L.score[w] = int(L.score[w]) + 1
        L["last"] = w
        L["round"] = int(L.get("round", 1)) + 1
        L.guest["ready"] = false
        var r: Dictionary = await net.push(code, int(d.rev), {"state": JSON.stringify({"lobby": L}), "rev": int(d.rev) + 1, "status": "lobby",
            "cur": 0, "turn": 1, "winner": null, "updated": int(Time.get_unix_time_from_system() * 1000.0)})
        if not r.is_empty():
            online = {"code": code, "seat": seat}
            _lobby_load(r)
            show_lobby()
            return
    show_online("The next game couldn't be set up. Open it from Your games.")


## The board as it's stored (from the maker's side).''')
f.save()
print('ok')

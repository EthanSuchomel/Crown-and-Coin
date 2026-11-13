# The Robot rework for the Godot version, step 4: the screens (main.gd), as in the browser's patch1-4:
# - Build: Robots get only the Market button; on a market of theirs it reads "Market 2..4" (a resource hex), or
#   "Factory"/"Full"; the side panel explains the two paths.
# - Advancements at the home castle: Barracks and Fortress buttons; pick one, then tap a ringed market (or factory) to
#   upgrade it; Done ends picking. Overclock sits there too (Construction, Advancements level 3).
# - Trades (Mobilize): Recompile in Advancements, Rebuild and Refit in Recruit, as buttons for the selected hex.
# - Move: the Laser Strike button in the attack dialog; Overclock in the attack notes.
# - Texts: card upgrades for the Robot cards (faction screen, How to play, card rows, upgrade picker), Factories,
#   Build/Advancements descriptions, Fortify notes, materials, hex details, the leftover warning; Sortie's heading.
# - Card art: the punch cards keep their wider shape.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import F
f = F(sys.argv[1] + '/scripts/ui/main.gd')

f.rep('''var wall_for: int = -1''', '''var wall_for: int = -1
var robo_up: String = ""   # the Robots' factory upgrade being placed during Advancements: "barracks" or "fort"''')
f.rep('''
    wall_for = -1
''', '''
    wall_for = -1
    robo_up = ""
''', 3)

# ---------- faction screen and How to play ----------
f.rep('''% ["Barracks, upgrades and walls" if my_faction == "dinos" else "Forts, barracks, upgrades, walls and trebuchets",''',
      '''% ["Barracks, upgrades and walls" if my_faction == "dinos" else ("Factory upgrades, barracks upgrades, walls and trebuchets" if my_faction == "robots" else "Forts, barracks, upgrades, walls and trebuchets"),''')
f.rep('''        if my_faction == "dinos":
            body.add_child(_rich(_dino_card_list(), 14))''', '''        if my_faction == "dinos" or my_faction == "robots":
            body.add_child(_rich(_card_list(my_faction), 14))''')
f.rep('''    if my_faction == "dinos":
        body.add_child(_label("Volcano and guards", 16, BONE, true))
        body.add_child(_rich(_dino_specials(), 14))''', '''    if my_faction == "dinos":
        body.add_child(_label("Volcano and guards", 16, BONE, true))
        body.add_child(_rich(_dino_specials(), 14))
    if my_faction == "robots":
        body.add_child(_label("Factories", 16, BONE, true))
        body.add_child(_rich(_robo_specials(), 14))''')
f.rep('''func _dino_card_list() -> String:
    var lines: Array = ["[b]Every Dinosaur card has its own upgrades for each of its actions[/b] (every 2nd play you pick which action goes up a level):"]
    for c in GameData.factions.dinos.cards:
        var parts: Array = []
        for a in c.actions:
            var d: Array = GameData.upgrades.dinos_cards.get(c.id, {}).get(a, [])''', '''func _dino_card_list() -> String:
    return _card_list("dinos")


## Every Dinosaur or Robot card's own upgrades, for How to play and the faction screen.
func _card_list(fid: String) -> String:
    var lines: Array = ["[b]Every %s card has its own upgrades for each of its actions[/b] (every 2nd play you pick which action goes up a level):" % ("Robot" if fid == "robots" else "Dinosaur")]
    for c in GameData.factions[fid].cards:
        var parts: Array = []
        for a in c.actions:
            var d: Array = GameData.upgrades.get(fid + "_cards", {}).get(c.id, {}).get(a, [])''')
f.rep('''func _dino_specials() -> String:''', '''## The Robots' factories and resource hexes, for How to play and the faction screen.
func _robo_specials() -> String:
    var c: Dictionary = GameData.rules.buildings.cost_by_level
    var n: int = int(GameData.rules.robots.markets_max)
    return ("Every Robot building starts as a [b]market[/b] (%d gold), one per hex, and then takes one of two paths. Never both.\\n"
        + "  •  [img=26]res://art/buildings/market_robots.png[/img] A [b]resource hex[/b]: build more markets on that hex, up to %d, %d gold each. Each market pays +2 gold a turn and sells you materials.\\n"
        + "  •  [img=26]res://art/buildings/barracks_robots.png[/img] [img=26]res://art/buildings/fort_robots.png[/img] A defensive [b]factory[/b]: during Advancements, tap your home castle, pick [b]Barracks[/b] or [b]Fortress[/b] (%d materials each) and tap the market to upgrade it: first a barracks (recruits there and trains barracks units), then a fortress (+1 on the defenders' best die, trains fortress units, can hold a trebuchet).\\n"
        + "Each is upgraded on its own, and factory upgrades only while you hold your home castle. Buildings you capture become one factory, or a resource hex if they were only markets.") % [int(c.market[0]), n, int(c.market[0]), int(c.barracks[0])]


func _dino_specials() -> String:''')
f.rep('''    if g != null and g.is_dinos(0):
        txt += "\\n\\n" + _dino_specials() + "\\n\\n" + _dino_card_list()''', '''    if g != null and g.is_dinos(0):
        txt += "\\n\\n" + _dino_specials() + "\\n\\n" + _dino_card_list()
    elif g != null and g.is_robots(0):
        txt += "\\n\\n" + _robo_specials() + "\\n\\n" + _card_list("robots")''')

# ---------- card pictures: the punch cards are wider than the head shots ----------
f.rep('''    var p := _pic(path, Vector2(h, h))
    p.size_flags_vertical = Control.SIZE_SHRINK_CENTER''', '''    var tx: Texture2D = load(path)
    var ar: float = clampf(tx.get_size().x / maxf(1.0, tx.get_size().y), 1.0, 1.45) if tx != null else 1.0   # the Robots' punch cards are wider
    var p := _pic(path, Vector2(h * ar, h))
    p.size_flags_vertical = Control.SIZE_SHRINK_CENTER''')

# ---------- action descriptions ----------
f.rep('''    var lvl: int = 0 if (raw == 1 or g.is_dinos(pid)) else raw   # the Dinosaurs' cards use their own upgrades''',
      '''    var lvl: int = 0 if (raw == 1 or g.card_ups(pid)) else raw   # the Dinosaurs' and Robots' cards use their own upgrades''')
f.rep('''            if g.is_dinos(pid):
                txt = "Build as many as you can afford: Markets (%d gold) and Barracks (%s). Buy materials at your markets"''',
'''            if g.is_robots(pid):
                txt = "Build markets (%d gold). Stack up to %d on a hex for a resource hex, or, during Advancements, turn one into a factory at your home castle: a Barracks, then a Fortress (%s each). Buy materials at your markets" % [int(c.market[lvl]), int(GameData.rules.robots.markets_max), g.mat_txt(int(c.barracks[0]))]
            elif g.is_dinos(pid):
                txt = "Build as many as you can afford: Markets (%d gold) and Barracks (%s). Buy materials at your markets"''')
f.rep('''paid in materials: upgrade a barracks (%d, %d, %d for levels 1 to 3%s), start a trebuchet on a hex with a fort (%d) or on a castle (up to 2: %d then %d), or build walls on a hex's sides (%d each)" % [int(up_costs[0]),''',
      '''paid in materials: %supgrade a barracks (%d, %d, %d for levels 1 to 3%s), start a trebuchet on a hex with a fort (%d) or on a castle (up to 2: %d then %d), or build walls on a hex's sides (%d each)" % [("add a Barracks or Fortress to one of your markets at your home castle (%d each), " % int(GameData.rules.buildings.cost_by_level.barracks[0])) if g.is_robots(pid) else "", int(up_costs[0]),''')
f.rep('''    if g.is_dinos(pid):
        if raw >= 1 and g.d_up(pid, cid, a):''', '''    if g.card_ups(pid):
        if raw >= 1 and g.d_up(pid, cid, a):''')

# ---------- Fortify: the Robots' pick notes, Sortie ----------
f.rep('''const FX_NOTES_DINO := {"build": "Markets and barracks", "advance": "Barracks, guards, volcano, walls"}''',
      '''const FX_NOTES_DINO := {"build": "Markets and barracks", "advance": "Barracks, guards, volcano, walls"}
const FX_NOTES_ROBO := {"build": "Markets", "advance": "Factory upgrades, barracks, trebuchets, walls"}''')
f.rep('''String((FX_NOTES_DINO if g.is_dinos(0) else {}).get(k, FX_NOTES[k]))''',
      '''String((FX_NOTES_DINO if g.is_dinos(0) else (FX_NOTES_ROBO if g.is_robots(0) else {})).get(k, FX_NOTES[k]))''')
f.rep('''    elif f.ph == "act":
        box.add_child(_rich("%s [b]Fortify%s: %s %s[/b]"''', '''    elif f.ph == "act" and String(f.cur) == "move" and bool(f.get("mvx", false)):
        box.add_child(_rich("%s [b]Sortie: %s Move[/b]  [color=#a5b49e]a real Move, to claim or attack[/color]" % [_img("fortify", 24), _img("move", 24)], 16))
    elif f.ph == "act":
        box.add_child(_rich("%s [b]Fortify%s: %s %s[/b]"''')

# ---------- materials ----------
f.rep('''if g.is_mammals(0) else "forts, barracks, barracks upgrades, walls and trebuchets")''',
      '''if g.is_mammals(0) else ("factory upgrades (a barracks, then a fortress), barracks upgrades, walls and trebuchets" if g.is_robots(0) else "forts, barracks, barracks upgrades, walls and trebuchets"))''')

# ---------- Build and Advancements controls in the card column ----------
f.rep('''func _build_controls(box: VBoxContainer) -> void:
    if not _sel_mine():''', '''## The Robots' Build: one factory per hex, or up to 4 markets on a resource hex.
func _robo_build_hint(box: VBoxContainer) -> void:
    var n: int = g.robo_markets()
    if not _sel_mine():
        _hint(box, "▸ Tap one of your hexes to build a market there. A hex holds one factory, or up to %d markets as a resource hex." % n)
        return
    var t: Dictionary = g.tiles[sel]
    if t.terrain != "plain":
        box.add_child(_label("You can't build here.", 13, RED))
    elif g.is_home_castle(t):
        _hint(box, "▸ Tap Market to build one at your home castle. Barracks and Fortress upgrades for your markets are made here during Advancements.")
    elif t.castle:
        _hint(box, "▸ Tap Market to build one here. Castles only take markets.")
    elif int(t.market) >= 2:
        _hint(box, "▸ A resource hex: %d of %d markets.%s It can't take a barracks or fortress." % [int(t.market), n, " Tap Market to add another." if g.robo_can_market(t) else ""])
    elif int(t.barracks) > 0:
        _hint(box, "▸ A factory%s. It can't take more markets." % (": add its fortress from your home castle during Advancements" if g.robo_next(t) == "fort" else ", fully upgraded"))
    elif g.building_count(t) > 0:
        _hint(box, "▸ Choose what this market becomes: tap Market to add a second one and make it a resource hex (up to %d markets), or give it a barracks from your home castle during Advancements to make it a defensive factory. Not both." % n)
    else:
        _hint(box, "▸ Tap Market to build a factory here. It starts as a market; then add more markets for a resource hex, or a barracks and then a fortress from your home castle during Advancements.")


## Mobilize's trades on the selected hex: Recompile (Advancements), Rebuild and Refit (Recruit).
func _robo_trades(box: VBoxContainer) -> void:
    if not g.is_robots(0) or not _sel_mine():
        return
    var T: Dictionary = GameData.rules.robots.trades
    for k in g.trades_at(sel):
        var x: Dictionary = T[k]
        var kk: String = k
        var s0: int = sel
        box.add_child(_build_button("res://art/units/%s.png" % String(x["to"]), "%s: %d %s → 1 %s" % [x["name"], int(x["n"]), _plural(String(x["from"])), GameData.units[String(x["to"])].name], "Trade them on this hex", func(): _do(func(): g.robo_trade(s0, kk)), true))


func _build_controls(box: VBoxContainer) -> void:
    if g.is_robots(0):
        _robo_build_hint(box)
        return
    if not _sel_mine():''')
f.rep('''func _advance_controls(box: VBoxContainer) -> void:
    if not _sel_mine():''', '''func _advance_controls(box: VBoxContainer) -> void:
    if g.is_robots(0) and robo_up != "":   # placing a factory upgrade
        var k: String = robo_up
        var n: int = g.robo_up_targets(0, k).size()
        box.add_child(_rich("[img=26]res://art/buildings/%s_robots.png[/img] [b]%s[/b]: %s each%s (you have %d)" % [k, "Fortress" if k == "fort" else "Barracks", g.mat_txt(g.robo_up_cost(0, k)), ", 1 less next to your home castle" if g.dk(0, "mobil", "advance") >= 1 else "", g.mat_of(0)], 15))
        _hint(box, "▸ Tap a ringed %s. %d can take one." % ["factory to add its fortress" if k == "fort" else "market to add a barracks and make it a factory", n])
        box.add_child(_button("Done", func():
            robo_up = ""
            refresh()))
        return
    if g.is_robots(0) and _sel_mine() and g.is_home_castle(g.tiles[sel]):
        _hint(box, "▸ Tap Barracks or Fortress around your home castle, then tap the market or factory to upgrade. Each market is upgraded on its own: first a barracks, then a fortress.%s" % (" Overclock is here too." if g.can_armor(0) else ""))
        _robo_trades(box)
        return
    if not _sel_mine():''')
f.rep('''else "▸ Tap one of your hexes to upgrade a barracks, start a trebuchet or build walls.")''',
      '''else ("▸ Tap your home castle to add a barracks or fortress to one of your markets, or tap one of your hexes to upgrade a barracks, start a trebuchet or build walls." if g.is_robots(0) else "▸ Tap one of your hexes to upgrade a barracks, start a trebuchet or build walls."))''')
f.rep('''"▸ Tap an option above the hex: upgrade the barracks, start a trebuchet, or build walls.")
    return
    var t: Dictionary = g.tiles[sel]
    var gold: int = int(g.players[0].gold)
    var fac: String = g.players[0].faction
    if int(t.barracks) > 0 and int(t.bk) < 3:''', '''"▸ Tap an option above the hex: upgrade the barracks, start a trebuchet, or build walls.")
    _robo_trades(box)
    return
    var t: Dictionary = g.tiles[sel]
    var gold: int = int(g.players[0].gold)
    var fac: String = g.players[0].faction
    if int(t.barracks) > 0 and int(t.bk) < 3:''')
f.rep('''        box.add_child(_label("You can't recruit here. Pick a castle or barracks.", 13, RED))
    return
    var t: Dictionary = g.tiles[sel]
    var basic: String = g.basic_of(0)''', '''        box.add_child(_label("You can't recruit here. Pick a castle or barracks.", 13, RED))
    _robo_trades(box)
    return
    var t: Dictionary = g.tiles[sel]
    var basic: String = g.basic_of(0)''')

# ---------- the leftover warning ----------
f.rep('''                if t.terrain == "plain" and g.building_count(t) < g.max_buildings():
                    for k in (["market"] if t.castle else''', '''                if t.terrain == "plain" and g.building_count(t) < g.max_buildings() and (not g.is_robots(0) or g.robo_can_market(t)):
                    for k in (["market"] if (t.castle or g.is_robots(0)) else''')
f.rep('''            var adv_txt: String = "upgrade a barracks, hire a guard, stoke the volcano or build walls" if g.is_dinos(0) else "upgrade a barracks, start a trebuchet or build walls"''',
      '''            var adv_txt: String = "upgrade a barracks, hire a guard, stoke the volcano or build walls" if g.is_dinos(0) else "upgrade a barracks, start a trebuchet or build walls"
            if g.is_robots(0) and g.home_market(0):
                for k in ["barracks", "fort"]:
                    if not g.robo_up_targets(0, k).is_empty() and mats >= g.robo_up_best(0, k):
                        return "You have [b]%s[/b] and can still add a %s to one of your markets at your home castle." % [g.mat_txt(mats), "fortress" if k == "fort" else "barracks"]''')

# ---------- buttons round the hex ----------
f.rep('''        for spot in [["barracks", 150, 1], ["fort", 90, 0], ["market", 30, 5]].filter(func(x): return not (x[0] == "fort" and g.is_dinos(0))):   # the Dinosaurs build no forts''',
      '''        for spot in [["barracks", 150, 1], ["fort", 90, 0], ["market", 30, 5]].filter(func(x): return not (x[0] == "fort" and g.is_dinos(0)) and (not g.is_robots(0) or x[0] == "market")):   # the Dinosaurs build no forts; the Robots build markets''')
f.rep('''            var note: String = "Full" if full else ("Not here" if castle_no else ("Free" if price == 0 else (("%d|mat" % price) if g.in_mat(kind) else "%d gold" % price)))
            var k2: String = kind
            _bubble(post.call(spot[2], spot[1]), R, "res://art/buildings/%s_%s.png" % [kind, fac], kind.capitalize(), note, can, false, can,''',
'''            var note: String = "Full" if full else ("Not here" if castle_no else ("Free" if price == 0 else (("%d|mat" % price) if g.in_mat(kind) else "%d gold" % price)))
            var title: String = kind.capitalize()
            if g.is_robots(0) and kind == "market" and not g.is_home_castle(t) and g.building_count(t) > 0:   # another market (a resource hex), or it's a factory
                var ok_m: bool = g.robo_can_market(t)
                can = ok_m and g.can_pay_b(0, "market", price)
                note = ("Free" if price == 0 else "%d gold" % price) if ok_m else ("Factory" if int(t.barracks) > 0 else "Full")
                title = ("Market %d" % (int(t.market) + 1)) if ok_m else "Market"
            var k2: String = kind
            _bubble(post.call(spot[2], spot[1]), R, "res://art/buildings/%s_%s.png" % [kind, fac], title, note, can, false, can,''')
f.rep('''        _bubble(post.call(1, 150), R, "res://art/buildings/barracks_%s.png" % fac, ("Level %d" % (lv + 1)) if (int(t.barracks) > 0 and lv < 3) else "Barracks", bk_note, can_bk, false, can_bk,
            func(): _do(func(): g.upgrade_barracks(sel)))
        if g.is_dinos(0):''', '''        if g.is_robots(0) and g.is_home_castle(t):   # the Robots' home castle: add a barracks or fortress to a market; Overclock
            _robo_home_bubbles(post, R)
        else:
            _bubble(post.call(1, 150), R, "res://art/buildings/barracks_%s.png" % fac, ("Level %d" % (lv + 1)) if (int(t.barracks) > 0 and lv < 3) else "Barracks", bk_note, can_bk, false, can_bk,
                func(): _do(func(): g.upgrade_barracks(sel)))
        if g.is_dinos(0):''')
f.rep('''func _place_bubbles() -> void:''', '''## The Robots' home castle in Advancements: Barracks and Fortress (pick one, then tap the market to upgrade), and Overclock.
func _robo_home_bubbles(post: Callable, R: float) -> void:
    for spec in [["barracks", 1, 150], ["fort", 2, 210]]:
        var k: String = spec[0]
        var tg: Array[int] = g.robo_up_targets(0, k)
        var c: int = g.robo_up_best(0, k)
        var can: bool = not tg.is_empty() and g.mat_of(0) >= c
        var note: String = ("%d|mat" % c) if not tg.is_empty() else ("No barracks" if k == "fort" else "No market")
        _bubble(post.call(spec[1], spec[2]), R, "res://art/buildings/%s_robots.png" % k, "Fortress" if k == "fort" else "Barracks", note, can, robo_up == k, can,
            func():
                robo_up = k
                sel = -1
                refresh())
    if g.can_armor(0):   # Overclock (Construction, Advancements level 3)
        var ac: int = int(g.armor_rules().cost)
        var can_a: bool = not g.armor_on(0) and int(g.players[0].gold) >= ac
        _bubble(post.call(4, 330), R, "res://art/terrain/castle_robots.png", "Overclock", "Running" if g.armor_on(0) else "%d gold" % ac, can_a, false, can_a,
            func(): _do(func(): g.do_armor(0)))


func _place_bubbles() -> void:''')

# ---------- the board: ringing the markets that can take the upgrade, and tapping them ----------
f.rep('''        elif wall_for >= 0 and g.cur_action() == "advance":
            for j in g.wall_sides(wall_for):''', '''        elif robo_up != "" and g.cur_action() == "advance":
            board.targets = g.robo_up_targets(0, robo_up)
        elif wall_for >= 0 and g.cur_action() == "advance":
            for j in g.wall_sides(wall_for):''')
f.rep('''    if g.cur_action() == "advance" and wall_for >= 0:
        if board.targets.has(i):''', '''    if g.cur_action() == "advance" and robo_up != "":   # the Robots: tap a ringed market or factory to upgrade it
        if board.targets.has(i):
            var k0: String = robo_up
            _do(func(): g.do_robo_up(0, i, k0))
            if not g.robo_up_targets(0, k0).any(func(j): return g.mat_of(0) >= g.robo_up_cost(0, k0, g.tiles[j])):
                robo_up = ""   # nothing more to upgrade, or out of materials
                refresh()
            return
        robo_up = ""
    if g.cur_action() == "advance" and wall_for >= 0:
        if board.targets.has(i):''')
f.rep('''    if g.cur_action() == "move":
        sel = -1
    wall_for = -1
    robo_up = ""''', '''    if g.cur_action() == "move":
        sel = -1
    wall_for = -1
    robo_up = ""''')

# ---------- the computer's laser strikes flash too; your notes keep them ----------
f.rep('''        if e.kind == "done":
            ai_flash.append_array(e.ids)''', '''        if e.kind == "done" or e.kind == "flash":
            ai_flash.append_array(e.ids)''')
f.rep('''notes.filter(func(n2): return (String(n2).contains("trebuchet") or''', '''notes.filter(func(n2): return (String(n2).contains("trebuchet") or String(n2).contains("laser strike") or''')
f.rep('''        elif "trebuchet" in line:
            icon = _img("advance", 22)''', '''        elif "trebuchet" in line:
            icon = _img("advance", 22)
        elif "laser strike" in line:
            icon = _img("move", 22)''')

# ---------- the attack dialog: Overclock, Laser Strike ----------
f.rep('''        if bool(ao.get("a_arm", false)):
            lines.append("Your units wear Armor: +%d damage, +10%% health" % int(g.armor_rules().dmg))
        if bool(ao.get("d_arm", false)):
            lines.append("Their units wear Armor: +%d damage, +10%% health" % int(g.armor_rules().dmg))''',
'''        if bool(ao.get("a_arm", false)):
            lines.append(("Your units are overclocked: +%d damage, +10%% health" if g.is_robots(0) else "Your units wear Armor: +%d damage, +10%% health") % int(g.armor_rules().dmg))
        if bool(ao.get("d_arm", false)):
            lines.append(("Their units are overclocked: +%d damage, +10%% health" if g.is_robots(int(b.owner)) else "Their units wear Armor: +%d damage, +10%% health") % int(g.armor_rules().dmg))
        if g.laser_ok(0, from, to):
            var nt: int = int(g.tiles[from].ready.get("ltank", 0))
            lines.append("[b]Laser Strike[/b]: your %d Laser Tank%s can fire from here instead, like a trebuchet%s, with no battle." % [nt, "s" if nt > 1 else "", " (twice)" if g.dk(0, "onsl", "move") >= 3 else ""])''')
f.rep('''    btns.add_child(_button("Cancel", func(): _close_overlay()))
    var all_b := _button("%s all" % verb, func():''', '''    btns.add_child(_button("Cancel", func(): _close_overlay()))
    if fight and g.laser_ok(0, from, to):   # Laser Strike (Onslaught)
        btns.add_child(_button("Laser strike", func():
            _close_overlay()
            _laser(from, to)))
    var all_b := _button("%s all" % verb, func():''')
f.rep('''func _go_move(from: int, to: int, units: Dictionary, join: bool = false) -> void:''', '''## Laser Strike: the tanks fire like a trebuchet. Dice are rolled, so it locks in (no undo).
func _laser(from: int, to: int) -> void:
    var r: Dictionary = g.do_laser(0, from, to)
    if r.is_empty():
        return
    undo_stack = []
    notes.append("%s Laser Strike: %d shot%s, %d hit%s, %d unit%s destroyed" % [_img("move", 22), int(r.shots), "" if int(r.shots) == 1 else "s", int(r.hits), "" if int(r.hits) == 1 else "s", int(r.killed), "" if int(r.killed) == 1 else "s"])
    sel = -1
    refresh()


func _go_move(from: int, to: int, units: Dictionary, join: bool = false) -> void:''')

# ---------- hex details ----------
f.rep('''    var bits: Array = []
    for b in ["market", "fort", "barracks"]:
        if int(t[b]) > 0:
            bits.append("%d %s" % [int(t[b]), b])''', '''    var bits: Array = []
    var robo_hex: bool = owner >= 0 and g.is_robots(owner) and not t.castle and int(t.market) > 0
    if robo_hex:
        var fl: Array = ["", "factory: a market", "factory: market and barracks", "factory: market, barracks and fortress"]
        bits.append(("resource hex, %d of %d markets" % [int(t.market), g.robo_markets()]) if int(t.market) >= 2 else String(fl[g.robo_lv(t)]))
    for b in ["market", "fort", "barracks"]:
        if int(t[b]) > 0 and not robo_hex:
            bits.append("%d %s" % [int(t[b]), b])''')
f.save(); print('p4 ui ok')

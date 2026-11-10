# Godot port of the browser's Dinosaur rework (2026-11-09), screens: the map buttons (no fort, the volcano and guards,
# 6 barracks units round the hex), the volley panel, hex details, notes, help, the faction screen, and the board's
# bigger nesting ground and lava-bomb animation.
import sys; sys.path.insert(0,sys.path[0])
from common import F
P=sys.argv[1].rstrip('/')+'/scripts/'
gs=F(P+'rules/game_state.gd')
# a running count of log lines (the log keeps only the last 80, so its size stops telling how many were added)
gs.rep('''var log_lines: Array[String] = []''','''var log_lines: Array[String] = []
var log_n: int = 0                 # log lines written this session (the log itself keeps only the last 80)''')
gs.rep('''    log_lines.push_front(text)
    if log_lines.size() > 80:''','''    log_lines.push_front(text)
    log_n += 1
    if log_lines.size() > 80:''')
gs.save()

m=F(P+'ui/main.gd')
m.s=m.s.replace('g.log_lines.size()\n','g.log_n\n').replace('game.log_lines.size()\n','game.log_n\n')
m.rep('''    var added: int = g.log_lines.size() - before''','''    var added: int = mini(g.log_n - before, g.log_lines.size())''')
m.rep('''var bubbles = null                # the buttons round the selected hex''','''var bubbles = null                # the buttons round the selected hex
var ai_notes: Array = []          # what the computer's volcano did at the start of its turn, shown when yours begins''')
# build: no fort for the Dinosaurs
m.rep('''        for spot in [["barracks", 150, 1], ["fort", 90, 0], ["market", 30, 5]]:''',
      '''        for spot in [["barracks", 150, 1], ["fort", 90, 0], ["market", 30, 5]].filter(func(x): return not (x[0] == "fort" and g.is_dinos(0))):   # the Dinosaurs build no forts''')
# advance: the volcano (home castle) or an Alamosaurus guard (barracks) in place of the trebuchet
m.rep('''        var can_tr: bool = g.can_treb_at(t) and gold >= g.treb_price(t)
        var tr_note: String = ("%d gold" % g.treb_price(t)) if g.can_treb_at(t) else ("Max 2" if t.castle else ("Building" if int(t.treb) == 1 else ("Built" if int(t.treb) > 0 else "Needs fort")))
        _bubble(post.call(0, 90), R, "res://art/buildings/treb_%s.png" % fac, "Trebuchet 2" if (t.castle and g.treb_count(t) == 1) else "Trebuchet", tr_note, can_tr, false, can_tr,
            func(): _do(func(): g.start_trebuchet(sel)))''','''        if g.is_dinos(0):
            # the Dinosaurs: the volcano at the home castle, an Alamosaurus guard on a barracks
            if g.is_home_castle(t):
                var vl: int = g.volc_lv(0)
                var vc: int = int(g.volc_levels()[mini(2, vl)].cost)
                var can_v: bool = vl < 3 and gold >= vc
                _bubble(post.call(0, 90), R, "res://art/terrain/castle_dinos.png", ("Volcano %d" % (vl + 1)) if vl < 3 else "Volcano", "Max level" if vl >= 3 else "%d gold" % vc, can_v, false, can_v,
                    func(): _do(func(): g.do_volcano(0)))
            else:
                var gn: int = g.guards_at(t)
                var gm: int = g.guard_max(t)
                var can_g: bool = int(t.barracks) > 0 and gn < gm and gold >= g.guard_cost()
                var g_note: String = "Needs barracks" if int(t.barracks) == 0 else (("%d guarding" % gn) if gn >= gm else "%d gold" % g.guard_cost())
                _bubble(post.call(0, 90), R, "res://art/units/alamo.png", "Alamosaurus", g_note, can_g, false, can_g,
                    func(): _do(func(): g.buy_guard(sel)))
        else:
            var can_tr: bool = g.can_treb_at(t) and gold >= g.treb_price(t)
            var tr_note: String = ("%d gold" % g.treb_price(t)) if g.can_treb_at(t) else ("Max 2" if t.castle else ("Building" if int(t.treb) == 1 else ("Built" if int(t.treb) > 0 else "Needs fort")))
            _bubble(post.call(0, 90), R, "res://art/buildings/treb_%s.png" % fac, "Trebuchet 2" if (t.castle and g.treb_count(t) == 1) else "Trebuchet", tr_note, can_tr, false, can_tr,
                func(): _do(func(): g.start_trebuchet(sel)))''')
# recruit: a barracks with 6 units puts them evenly round the hex, Back at the bottom
m.rep('''            var at: Array = [[1, 150], [5, 30], [2, 210], [4, 330]] if list.size() == 4 else [[1, 150], [0, 90], [5, 30], [2, 210], [4, 330]]
            for n in mini(list.size(), at.size()):''','''            var at: Array = [[1, 150], [5, 30], [2, 210], [4, 330]] if list.size() == 4 else [[1, 150], [0, 90], [5, 30], [2, 210], [4, 330]]
            var big: bool = list.size() > 5   # 6 units (the Dinosaurs) go evenly round the hex, with Back at the bottom
            var rr: float = minf(R, (hr * 0.95 + stem) / 1.75) if big else R
            var rring: float = hr * 0.95 + stem + rr
            var rpost := func(deg) -> Vector2:
                var d := Vector2(cos(deg_to_rad(deg)), -sin(deg_to_rad(deg)))
                var p0: Vector2 = (c + d * rring).clamp(Vector2(rr + 2, rr + 2), bubbles.size - Vector2(rr + 2, rr + 2))
                bubbles.posts.append([c + d * hr * 0.86, p0 - d * rr * 0.9])
                return p0
            var ring_at: Array = [167.1, 115.7, 64.3, 12.9, 321.4, 218.6]
            for n in (mini(list.size(), ring_at.size()) if big else mini(list.size(), at.size())):''')
m.rep('''                _bubble(post.call(at[n][0], at[n][1]), R, "res://art/units/%s.png" % k, _short(k), note2, ok, picked, true,''',
      '''                _bubble(rpost.call(float(ring_at[n])) if big else post.call(at[n][0], at[n][1]), rr, "res://art/units/%s.png" % k, _short(k), note2, ok, picked, true,''')
m.rep('''            _bubble(post.call(3, 270), R * 0.8, "", "Back", "", true, false, true, func():''',
      '''            _bubble(rpost.call(270.0) if big else post.call(3, 270), rr * 0.8, "", "Back", "", true, false, true, func():''')
# the home-castle ring: with no fort units, the barracks units fill the ring
m.rep('''            for n in bl.size():
                items.append([bl[n], "barracks", float(UNIT_RING_BARRACKS[mini(n, 2)])])
            var fl: Array = g.faction_of(0).training.fort''','''            var fl: Array = g.faction_of(0).training.fort
            for n in bl.size():
                items.append([bl[n], "barracks", float(UNIT_RING_BARRACKS[mini(n, 2)]) if not fl.is_empty() else float(UNIT_RING_ALL[mini(n, 4)])])''')
m.rep('''const UNIT_RING_FORT := [30, 345, 300]''','''const UNIT_RING_FORT := [30, 345, 300]
const UNIT_RING_ALL := [150, 210, 270, 330, 30]   # no fort units (the Dinosaurs): the barracks units go all the way round''')
# the volley: trebuchets or the volcano
m.rep('''            board.targets = g.treb_targets(g.volley[0])''','''            board.targets = g.shot_targets(g.volley[0])''')
m.rep('''        if g.treb_targets(g.volley[0]).has(i):
            var before: int = g.log_n
            g.shoot_volley(g.volley[0], i)
            undo_stack = []   # the trebuchet rolls dice: its shot locks in''','''        if g.shot_targets(g.volley[0]).has(i):
            var before: int = g.log_n
            g.shoot_volley(g.volley[0], i)
            undo_stack = []   # the trebuchet (or volcano) rolls dice: its shot locks in''')
m.rep('''    elif not g.volley.is_empty():
        _note_box(body, "%s Your trebuchet is ready. Tap a hex ringed in red next to it to fire." % _img("advance", 22), GOLD)''','''    elif not g.volley.is_empty():
        if g.is_volc_hex(g.volley[0]):
            var vv: Dictionary = g.volc_levels()[g.volc_lv(0) - 1]
            _note_box(body, "[img=30]res://art/terrain/castle_dinos.png[/img] Your volcano is erupting: %d lava bombs for one enemy hex %s. Tap a hex ringed in red to aim it." % [int(vv.dice), "anywhere on the map" if int(vv.reach) >= 99 else "within %d hexes" % int(vv.reach)], GOLD)
        else:
            _note_box(body, "%s Your trebuchet is ready. Tap a hex ringed in red next to it to fire." % _img("advance", 22), GOLD)''')
# the board plays each eruption
m.rep('''    _save()
    _update_board()
    _place_bubbles()''','''    _save()
    _update_board()
    while not g.volc_fx.is_empty():
        var fx: Dictionary = g.volc_fx.pop_front()
        board.lava(int(fx.from), int(fx.to), fx.dice)
    _place_bubbles()''')
m.rep('''        elif "trebuchet" in line:
            icon = _img("advance", 22)''','''        elif "volcano" in line:
            icon = "[img=26]res://art/terrain/castle_dinos.png[/img]"
        elif "trebuchet" in line:
            icon = _img("advance", 22)''')
m.rep('''    if g.over < 0 and g.current == 1:
        notes = []
        _save()''','''    if g.over < 0 and g.current == 1:
        notes = []
        ai_notes = []
        for k in range(mini(g.log_n - before, g.log_lines.size()) - 1, -1, -1):   # the computer's volcano, at the start of its turn
            if "volcano" in g.log_lines[k]:
                ai_notes.append("[img=26]res://art/terrain/castle_dinos.png[/img] " + g.log_lines[k])
        _save()''')
m.rep('''        notes = notes.filter(func(n2): return String(n2).contains("trebuchet") and not String(n2).contains(String(game.players[1].name)))''',
      '''        notes = ai_notes + notes.filter(func(n2): return (String(n2).contains("trebuchet") or String(n2).contains("volcano")) and not String(n2).contains(String(game.players[1].name)))
        ai_notes = []''')
# action texts
m.rep('''                txt = "First, free %s: %d at each castle and %d at each barracks. Then recruit %s (%d gold each) at your castles and barracks, or train other units at barracks and forts" % [bname, fc, fb, bname, cost]
            else:
                txt = "Recruit %s (%d gold each) at your castles and barracks, or train other units at barracks and forts" % [bname, cost]''',
'''                txt = "First, free %s: %d at each castle and %d at each barracks. Then recruit %s (%d gold each) at your castles and barracks, or train other units at barracks%s" % [bname, fc, fb, bname, cost, "" if g.is_dinos(pid) else " and forts"]
            else:
                txt = "Recruit %s (%d gold each) at your castles and barracks, or train other units at barracks%s" % [bname, cost, "" if g.is_dinos(pid) else " and forts"]''')
m.rep('''            txt = "Build as many Markets, Forts and Barracks as you can afford"
            if lvl > 0:
                var c: Dictionary = GameData.rules.buildings.cost_by_level
                txt += " (Market %d, Fort %d, Barracks %d gold)" % [int(c.market[lvl]), int(c.fort[lvl]), int(c.barracks[lvl])]''',
'''            txt = "Build as many Markets and Barracks as you can afford" if g.is_dinos(pid) else "Build as many Markets, Forts and Barracks as you can afford"
            if lvl > 0:
                var c: Dictionary = GameData.rules.buildings.cost_by_level
                if g.is_dinos(pid):
                    txt += " (Market %d, Barracks %d gold)" % [int(c.market[lvl]), int(c.barracks[lvl])]
                else:
                    txt += " (Market %d, Fort %d, Barracks %d gold)" % [int(c.market[lvl]), int(c.fort[lvl]), int(c.barracks[lvl])]''')
m.rep('''            var tr: Dictionary = GameData.rules.trebuchet
            txt = "Spend gold on as many as you can afford: upgrade a barracks''','''            var tr: Dictionary = GameData.rules.trebuchet
            if g.is_dinos(pid):
                var D: Dictionary = GameData.rules.dinos
                txt = "Spend gold on as many as you can afford: upgrade a barracks (%d, %d, %d gold for levels 1 to 3%s), hire Alamosaurus guards for a barracks (%d gold each, up to %d per barracks), wake or stoke the volcano at your home castle (%d, %d, %d gold for levels 1 to 3), or build walls on a hex's sides (%d gold each)" % [int(up_costs[0]), int(up_costs[1]), int(up_costs[2]), ", your first level 1 free" if lvl >= 1 else "", int(D.guard_cost), int(D.guard_max), int(D.volcano[0].cost), int(D.volcano[1].cost), int(D.volcano[2].cost), int(GameData.rules.walls.cost_by_level[lvl])]
            else:
                txt = "Spend gold on as many as you can afford: upgrade a barracks''')
m.rep('''        _hint(box, "▸ Tap one of your hexes to upgrade a barracks, start a trebuchet or build walls.")''',
      '''        _hint(box, "▸ Tap one of your hexes to upgrade a barracks or hire its Alamosaurus guards, tap your home castle to wake or stoke its volcano, or build walls." if g.is_dinos(0) else "▸ Tap one of your hexes to upgrade a barracks, start a trebuchet or build walls.")''')
m.rep('''        _hint(box, "▸ Tap an option above the hex: upgrade the barracks, start a trebuchet, or build walls.")''',
      '''        _hint(box, "▸ Tap an option above the hex: upgrade the barracks, hire an Alamosaurus guard (the volcano, at your home castle), or build walls." if g.is_dinos(0) else "▸ Tap an option above the hex: upgrade the barracks, start a trebuchet, or build walls.")''')
m.rep('''Markets earn +2 gold a turn; forts and barracks unlock units.%s" % (" Castles can only take markets." if g.tiles[sel].castle else ""))''','''Markets earn +2 gold a turn; %s unlock units.%s" % ["barracks" if g.is_dinos(0) else "forts and barracks", " Castles can only take markets." if g.tiles[sel].castle else ""])''')
# the warning when you end an action with gold left
m.rep('''                    for k in (["market"] if t.castle else ["market", "fort", "barracks"]):''',
      '''                    for k in (["market"] if t.castle else (["market", "barracks"] if g.is_dinos(0) else ["market", "fort", "barracks"])):''')
m.rep('''        "advance":
            for t in mine:
                if t.terrain == "water":
                    continue''','''        "advance":
            var adv_txt: String = "upgrade a barracks, hire a guard, stoke the volcano or build walls" if g.is_dinos(0) else "upgrade a barracks, start a trebuchet or build walls"
            for t in mine:
                if t.terrain == "water":
                    continue
                if g.is_dinos(0) and int(t.barracks) > 0 and g.guards_at(t) < g.guard_max(t) and gold >= g.guard_cost():
                    return "You have [b]%d gold[/b] and can still %s." % [gold, adv_txt]
                if g.is_dinos(0) and g.is_home_castle(t) and g.volc_lv(0) < 3 and gold >= int(g.volc_levels()[g.volc_lv(0)].cost):
                    return "You have [b]%d gold[/b] and can still %s." % [gold, adv_txt]''')
n=m.s.count('return "You have [b]%d gold[/b] and can still upgrade a barracks, start a trebuchet or build walls." % gold'); assert n==3,n
m.s=m.s.replace('return "You have [b]%d gold[/b] and can still upgrade a barracks, start a trebuchet or build walls." % gold','return "You have [b]%d gold[/b] and can still %s." % [gold, adv_txt]')
# hex details
m.rep('''    if int(t.treb) > 0:
        bits.append("trebuchet %s" % ("ready" if int(t.treb) == 2 else "being built"))''','''    if int(t.treb) > 0:
        bits.append("trebuchet %s" % ("ready" if int(t.treb) == 2 else "being built"))
    if int(t.barracks) > 0 and owner >= 0 and g.is_dinos(owner):
        bits.append("%d of %d Alamosaurus guards" % [g.guards_at(t), g.guard_max(t)])
    if g.is_volc_hex(sel):
        var pv: Dictionary = g.players[owner].volc
        bits.append("volcano level %d: %s; %s" % [int(pv.lv), g.volc_say(int(pv.lv)), ("erupts in %d turns" % int(pv.cd)) if int(pv.cd) > 1 else "erupts at the start of %s next turn" % ("your" if owner == 0 else "their")])''')
# help and the faction screen
m.rep('''    txt += "%s Bonus coins pay %d gold to whoever takes the hex first. Every 2nd time you play a card, you upgrade one of its actions." % [_img("coin", 20), int(GameData.rules.coin.gold)]''',
'''    txt += "%s Bonus coins pay %d gold to whoever takes the hex first. Every 2nd time you play a card, you upgrade one of its actions." % [_img("coin", 20), int(GameData.rules.coin.gold)]
    if g != null and g.is_dinos(0):
        txt += "\\n\\n" + _dino_specials()''')
m.rep('''    for menu in ["barracks", "fort"]:
        for k in f2.training[menu]:
            if not units.has(k):
                units.append(k)''','''    for menu in ["barracks", "fort"]:
        for k in f2.training[menu]:
            if not units.has(k):
                units.append(k)
    if my_faction == "dinos":
        units.append("alamo")   # the barracks guard''')
m.rep('''    var foot := HBoxContainer.new()
    foot.add_theme_constant_override("separation", 8)
    vb.add_child(foot)
    foot.add_child(_button("Back", func(): show_title()))''','''    if my_faction == "dinos":
        body.add_child(_label("Volcano and guards", 16, BONE, true))
        body.add_child(_rich(_dino_specials(), 14))
    var foot := HBoxContainer.new()
    foot.add_theme_constant_override("separation", 8)
    vb.add_child(foot)
    foot.add_child(_button("Back", func(): show_title()))''')
m.rep('''## Who the computer plays: your pick on the faction screen, or the usual opponent.''','''func _volc_say(v: Dictionary) -> String:
    return "reaches %s, erupts %s, %d dice" % ["the whole map" if int(v.reach) >= 99 else "%d hexes" % int(v.reach), "every turn" if int(v.every) == 1 else "every %d turns" % int(v.every), int(v.dice)]


## The Dinosaurs' volcano and Alamosaurus guards, for How to play and the faction screen.
func _dino_specials() -> String:
    var D: Dictionary = GameData.rules.dinos
    var tr: Dictionary = GameData.rules.trebuchet
    var lv: Array = []
    for i in D.volcano.size():
        lv.append("level %d (%d gold) %s" % [i + 1, int(D.volcano[i].cost), _volc_say(D.volcano[i])])
    return ("[img=30]res://art/terrain/castle_dinos.png[/img] [b]Volcano[/b]: the Dinosaurs build no forts and no trebuchets. Instead, Advancements at your home castle wake its volcano and stoke it higher: %s. When it's due it erupts at the start of your turn, once, at an enemy hex with units in reach (you pick): every %d or higher does %d damage to the front of their line, and walls don't stop it. If your home castle falls, the volcano is lost.\\n"
        + "[img=30]res://art/units/alamo.png[/img] [b]Alamosaurus guards[/b]: Advancements at a barracks hire them, %d gold each, up to %d per barracks. A guard never moves or attacks; it joins the fight whenever that hex is attacked, and can hold it on its own. Each stomp hits up to 4 enemies. A guard that dies is gone until you hire another.") % ["; ".join(PackedStringArray(lv)), int(tr.hit_on), int(tr.damage_per_hit), int(D.guard_cost), int(D.guard_max)]


## Who the computer plays: your pick on the faction screen, or the usual opponent.''')
m.rep('''const SHORT_NAMES := {"eleph": "Palaeolox.", "kanga": "Procoptodon", "porc": "Porcupine", "dilo": "Dilo Archer", "quetz": "Quetzal",''',
      '''const SHORT_NAMES := {"eleph": "Palaeolox.", "kanga": "Procoptodon", "porc": "Porcupine", "galli": "Pachy", "dilo": "Dilophosaurus", "quetz": "Stegosaurus",''')
m.save()

b=F(P+'ui/board_view.gd')
b.rep('''const BLD_SIZE := 9.6''','''const BLD_SIZE := 9.6
const BLD_GROW := {"barracks_dinos": 1.5, "market_dinos": 1.18}   # the Dinosaurs' nesting ground is flat, so it's drawn bigger (standing on the same spot)''')
b.rep('''var blink: bool = true''','''var blink: bool = true
var lava_fx: Array = []          # volcano eruptions playing: {from, to, bombs, t0}''')
b.rep('''func _process(delta: float) -> void:
    # the dashed rings blink, like the browser version's
    if targets.is_empty() and flash.is_empty() and shooter < 0:''','''func _process(delta: float) -> void:
    if not lava_fx.is_empty():
        queue_redraw()
    # the dashed rings blink, like the browser version's
    if targets.is_empty() and flash.is_empty() and shooter < 0:''')
b.rep('''        for pair in placed:
            var pos: Vector2 = c + (pair[1] - Vector2(sz, sz) / 2.0) * u
            _draw_rect_tex(tex("wh" if pair[0] == "wh" else pair[0] + "_" + fac), Rect2(pos, Vector2(sz, sz) * u))''','''        for pair in placed:
            var pos: Vector2 = c + (pair[1] - Vector2(sz, sz) / 2.0) * u
            var bk: String = "wh" if pair[0] == "wh" else pair[0] + "_" + fac
            var z: float = sz * float(BLD_GROW.get(bk, 1.0))
            _draw_rect_tex(tex(bk), Rect2(c + (pair[1] + Vector2(-z / 2.0, sz / 2.0 - z)) * u, Vector2(z, z) * u))''')
b.rep('''    if blink:
        for i5 in flash:
            draw_polyline(_closed(_hex_points(center(int(i5)), (HR - 1.4) * u)), flash_color, 2.6 * u)
''','''    if blink:
        for i5 in flash:
            draw_polyline(_closed(_hex_points(center(int(i5)), (HR - 1.4) * u)), flash_color, 2.6 * u)

    # 7. lava bombs from a Dinosaur volcano (just for show: the shot is already worked out)
    if not lava_fx.is_empty():
        _draw_lava(u)
''')
b.rep('''func _draw_wall(i: int, k: int, hp: int, preview: bool) -> void:''','''## A volcano eruption: the crater flares, then one glowing rock per die arcs onto the target (hits land close together,
## misses scatter) and splashes. As the browser's lava-bomb animation.
func lava(from: int, to: int, dice: Array) -> void:
    var bombs: Array = []
    for k in dice.size():
        var hit: bool = int(dice[k]) >= int(GameData.rules.trebuchet.hit_on)
        var spread: float = 7.0 if hit else 16.0
        bombs.append({"hit": hit, "delay": k * 0.11, "off": Vector2(randf_range(-0.5, 0.5) * spread, randf_range(-0.5, 0.5) * spread * 0.75)})
    lava_fx.append({"from": from, "to": to, "bombs": bombs, "t0": Time.get_ticks_msec() / 1000.0})
    queue_redraw()


func _draw_lava(u: float) -> void:
    var now: float = Time.get_ticks_msec() / 1000.0
    var dur: float = 0.9
    var keep: Array = []
    for fx in lava_fx:
        var el: float = now - float(fx.t0)
        var fpos: Vector2 = center(int(fx.from)) + Vector2(0.0, -HR * 0.55) * u
        var tc: Vector2 = center(int(fx.to))
        var hgt: float = maxf(28.0 * u, fpos.distance_to(tc) * 0.45)
        if el < 0.3:
            var fl: float = el / 0.3
            draw_circle(fpos, (2.0 + fl * 5.0) * u, Color(1.0, 0.69, 0.18, 0.8 * (1.0 - fl)))
        for bm in fx.bombs:
            var t: float = (el - float(bm.delay)) / dur
            if t < 0.0:
                continue
            var tp: Vector2 = tc + Vector2(bm.off) * u
            if t < 1.0:
                var p: Vector2 = fpos.lerp(tp, t) - Vector2(0.0, hgt * 4.0 * t * (1.0 - t))
                draw_circle(p, 3.3 * u, OUTLINE)
                draw_circle(p, 2.7 * u, Color("e8541a"))
                draw_circle(p, 1.2 * u, Color("ffd54a"))
            else:
                var s: float = (t - 1.0) * dur / 0.38
                if s < 1.0:
                    var col: Color = Color("ff7a1a") if bool(bm.hit) else Color("7a6a5a")
                    col.a = 1.0 - s
                    draw_circle(tp, (1.5 + s * (6.0 if bool(bm.hit) else 3.5)) * u, col)
        if el < dur + fx.bombs.size() * 0.11 + 0.45:
            keep.append(fx)
    lava_fx = keep


func _draw_wall(i: int, k: int, hp: int, preview: bool) -> void:''')
b.save()
print('p12 ui ok')

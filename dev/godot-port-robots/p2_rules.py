# The Robot rework (browser 2026-11-11/12) for the Godot version, step 2: the rules (game_state.gd).
# Ported from the browser's dev/robots/patch1_factory.py, patch2_resource.py and patch3_cards.py:
# - one Robot building per hex: a market that becomes either a resource hex (up to 4 markets) or a factory (a barracks,
#   then a fortress, added from the home castle during Advancements, paid in materials);
# - every Robot card has its own upgrades (dk, as for the Dinosaurs); the old Update, Offline, Efficiency, Factory,
#   Assembly Line and Industrialization are gone (Offline and Assembly Line are Mobilize upgrades now);
# - Harvest (castle gold, Full Yield, Market Hubs, Hub Stores), prices (free markets, Fourth Free, Cheap Markets,
#   Fresh Ground, Border Market, flyers, Quick Barracks/Fortress, Home Grid), moves (Extra Thread, Climb, Offline,
#   Air Lanes, Ridge Hop, Overflight, Brawler Dash, Fresh Units, Scavenger), Laser Strike, trades, Muster, Factory/
#   Barracks/Fortress Run, Overclock, Dual Core, Sortie, Home Link, and captured buildings becoming one factory.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import F
f = F(sys.argv[1] + '/scripts/rules/game_state.gd')

# ---------- tiles remember when they made units and who captured them ----------
f.rep('''    var defaults: Dictionary = {"troops": 0, "fresh": 0, "braced": -1, "bl": 0, "wh": 0,
        "treb": 0, "treb_due": 0, "treb2": 0, "treb2_due": 0, "tree": 0, "root": 0, "dome": 0}''',
'''    var defaults: Dictionary = {"troops": 0, "fresh": 0, "braced": -1, "bl": 0, "wh": 0,
        "treb": 0, "treb_due": 0, "treb2": 0, "treb2_due": 0, "tree": 0, "root": 0, "dome": 0,
        "new_t": -1, "cap_t": -1, "cap_by": -1}   # Robots: the round units were made here; when and by whom it was captured''')
f.rep('''        for t in d.tiles:
            if not t.has("wh"):
                t["wh"] = 0''', '''        for t in d.tiles:
            if not t.has("wh"):
                t["wh"] = 0
            for key in ["new_t", "cap_t", "cap_by"]:
                if not t.has(key):
                    t[key] = -1''')

# ---------- levels: the Robots' cards use their own upgrades ----------
f.rep('''    return (1 if dk(pid, "stamp", "move") >= 1 else 0) + int(mods_of(pid).movesPerAction)''',
      '''    return (1 if dk(pid, "stamp", "move") >= 1 else 0) + (1 if dk(pid, "mobil", "move") >= 1 else 0) + int(mods_of(pid).movesPerAction)''')
f.rep('''    if is_dinos(current):
        return 1 if dk(current, "siege", "move") >= 1 else 0
    var raw: int = raw_lvl()''', '''    if is_dinos(current):
        return 1 if dk(current, "siege", "move") >= 1 else 0
    if is_robots(current):
        return 1 if dk(current, "mobil", "move") >= 2 else 0   # Climb (Mobilize)
    var raw: int = raw_lvl()''')
f.rep('''    if play.is_empty() or is_dinos(current):
        return false
    return raw_lvl() >= 1''', '''    if play.is_empty() or card_ups(current):
        return false
    return raw_lvl() >= 1''')
f.rep('''func dk(pid: int, cid: String, a: String) -> int:
    if play.is_empty() or current != pid or not is_dinos(pid) or String(play.card) != cid or card_action() != a:''',
'''## Factions whose cards have their own upgrades: the Dinosaurs, and the Robots since 2026-11-11.
func card_ups(pid: int) -> bool:
    return is_dinos(pid) or is_robots(pid)


## The level a card's action has reached, played now or not (Mobilize's Cheap Markets stays on once reached).
func card_lv(pid: int, cid: String, a: String) -> int:
    var c: Dictionary = card_of(pid, cid)
    if c.is_empty():
        return 0
    var i: int = c.actions.find(a)
    return 0 if i < 0 else lvl_of(pid, cid, i)


func dk(pid: int, cid: String, a: String) -> int:
    if play.is_empty() or current != pid or not card_ups(pid) or String(play.card) != cid or card_action() != a:''')
f.rep('''    return GameData.upgrades.get("dinos_cards", {}).get(cid, {}).get(a, [])''',
      '''    var d: Dictionary = GameData.upgrades.get("dinos_cards", {})
    if not d.has(cid):
        d = GameData.upgrades.get("robots_cards", {})
    return d.get(cid, {}).get(a, [])''')
f.rep('''## Does this Dinosaur card's action have its own upgrades?
func d_up(pid: int, cid: String, a: String) -> bool:
    return is_dinos(pid) and not dcard(cid, a).is_empty()''', '''## Does this card's action have its own upgrades? (the Dinosaurs' and the Robots' cards)
func d_up(pid: int, cid: String, a: String) -> bool:
    return card_ups(pid) and not dcard(cid, a).is_empty()''')

# ---------- Armor (The Hunt) and Overclock (Construction): the same thing ----------
f.rep('''    if not is_dinos(pid) or armor_on(pid) or int(h.owner) != pid or dk(pid, "hunt", "advance") < 3 or int(p.gold) < cost:
        return false
    p.gold = int(p.gold) - cost
    p.armor = true
    add_log("%s forge Armor: all their units get +%d damage and +10%% health." % [p.name, int(armor_rules().dmg)])''',
'''    if armor_on(pid) or int(h.owner) != pid or not (dk(pid, "hunt", "advance") >= 3 or dk(pid, "cons", "advance") >= 3) or int(p.gold) < cost:
        return false   # Armor (The Hunt) or Overclock (Construction)
    p.gold = int(p.gold) - cost
    p.armor = true
    add_log("%s %s: all their units get +%d damage and +10%% health." % [p.name, "run Overclock" if is_robots(pid) else "forge Armor", int(armor_rules().dmg)])''')
f.rep('''    return is_dinos(pid) and dk(pid, "hunt", "advance") >= 3 and int(tiles[homes[pid]].owner) == pid''',
      '''    return ((is_dinos(pid) and dk(pid, "hunt", "advance") >= 3) or (is_robots(pid) and dk(pid, "cons", "advance") >= 3)) and int(tiles[homes[pid]].owner) == pid''')
f.rep('''func bk_up_cost(pid: int, lv: int) -> int:
    return int(GameData.rules.buildings.barracks_upgrade_cost[lv]) - (1 if dk(pid, "hunt", "advance") >= 1 else 0)   # Quick Nests''',
'''func bk_up_cost(pid: int, lv: int, t: Dictionary = {}) -> int:
    var c: int = int(GameData.rules.buildings.barracks_upgrade_cost[lv]) - (1 if dk(pid, "hunt", "advance") >= 1 else 0)   # Quick Nests
    if dk(pid, "cons", "advance") >= 1:
        c -= 1   # Quick Barracks (Construction)
    if not t.is_empty() and dk(pid, "mobil", "advance") >= 1 and HexGrid.neighbors(homes[pid]).has(int(t.id)):
        c -= 1   # Home Grid (Mobilize)
    return maxi(0, c)''')

# ---------- the Robots: factories, resource hexes and their card upgrades ----------
f.rep('''# =====================================================================
# Materials (Ethan, 2026-11-10)''', '''# =====================================================================
# The Robots (Ethan, 2026-11-11/12). One building per hex. It starts as a market and then takes one of two paths:
# a resource hex (more markets on that hex, up to 4), or a factory (from the home castle during Advancements: a barracks,
# then a fortress, paid in materials). Never both. Each Robot card has its own upgrades (upgrades.json robots_cards).
# Ported from the browser's dev/robots/patch1_factory.py, patch2_resource.py and patch3_cards.py.
# =====================================================================

func robo_markets() -> int:
    return int(GameData.rules.robots.markets_max)


## A Robot hex's factory level: 1 a market, 2 with a barracks, 3 with its fortress (0: nothing built).
func robo_lv(t: Dictionary) -> int:
    if int(t.market) <= 0:
        return 0
    if int(t.barracks) <= 0:
        return 1
    return 3 if int(t.fort) > 0 else 2


## What the home castle can add to this hex next: "barracks" (on a single market), then "fort"; "" when nothing
## (a resource hex, a castle, a full factory).
func robo_next(t: Dictionary) -> String:
    if int(t.market) <= 0 or t.castle:
        return ""
    if int(t.barracks) <= 0:
        return "barracks" if int(t.market) == 1 else ""
    return "fort" if int(t.fort) <= 0 else ""


## Can this hex take another Robot market? (an empty hex, or a market on the resource path)
func robo_can_market(t: Dictionary) -> bool:
    return int(t.barracks) <= 0 and int(t.fort) <= 0 and int(t.get("wh", 0)) <= 0 and int(t.market) < robo_markets()


func robo_up_targets(pid: int, k: String) -> Array[int]:
    var out: Array[int] = []
    for t in tiles:
        if int(t.owner) == pid and robo_next(t) == k:
            out.append(int(t.id))
    return out


## A factory upgrade's price in materials: Quick Barracks, Quick Fortress, and Home Grid next to the home castle.
func robo_up_cost(pid: int, k: String, t: Dictionary = {}) -> int:
    var c: int = int(GameData.rules.buildings.cost_by_level[k][0])
    if k == "barracks" and dk(pid, "cons", "advance") >= 1:
        c -= 1
    if k == "fort" and dk(pid, "cons", "advance") >= 2:
        c -= 1
    if not t.is_empty() and dk(pid, "mobil", "advance") >= 1 and HexGrid.neighbors(homes[pid]).has(int(t.id)):
        c -= 1
    return maxi(0, c)


## The cheapest that upgrade comes to now (for the buttons); its base price when nothing can take it.
func robo_up_best(pid: int, k: String) -> int:
    var tg: Array[int] = robo_up_targets(pid, k)
    if tg.is_empty():
        return robo_up_cost(pid, k)
    var best: int = 999
    for i in tg:
        best = mini(best, robo_up_cost(pid, k, tiles[i]))
    return best


## Adds a barracks (or then the fortress) to one of pid's markets, paid in materials: during Advancements, while the
## Robots hold their home castle.
func do_robo_up(pid: int, i: int, k: String = "") -> bool:
    var t: Dictionary = tiles[i]
    var nk: String = robo_next(t)
    if not is_robots(pid) or int(t.owner) != pid or nk == "" or (k != "" and k != nk) or not home_market(pid) or cur_action() != "advance":
        return false
    var c: int = robo_up_cost(pid, nk, t)
    if mat_of(pid) < c:
        return false
    spend_mat(pid, c)
    t[nk] = 1
    _note_unlock(pid, nk, t)
    add_log("%s upgrade a factory with a %s." % [players[pid].name, "fortress" if nk == "fort" else "barracks"])
    if nk == "barracks":
        robo_muster(pid, t)
    return true


## Muster (Onslaught, Advancements): every barracks upgrade also makes units on that hex.
func robo_muster(pid: int, t: Dictionary) -> void:
    var l: int = dk(pid, "onsl", "advance")
    if l < 1 or not is_robots(pid):
        return
    var got: Dictionary = {"rknight": 1, "rlong": 1} if l >= 3 else ({"brawler": 2, "rarch": 1} if l >= 2 else {"brawler": 2})
    _add_army(int(t.id), got, true)
    t.new_t = turn
    add_log("%s muster %s at the new barracks." % [players[pid].name, _army_words(got)])


func _army_words(a: Dictionary) -> String:
    var parts: Array = []
    for k in a:
        parts.append("%d %s" % [int(a[k]), String(GameData.units[k].name)])
    return ", ".join(PackedStringArray(parts))


## The Robots' market prices in a Build: Free Market(s) (Siege Protocol), Fourth Free, Cheap Markets (Mobilize, for good
## once reached), Fresh Ground (Construction) and Border Market (Siege Protocol).
func robo_cost(pid: int, k: String, c: int, t: Dictionary) -> int:
    if k != "market":
        return c
    var sb: int = dk(pid, "sprot", "build")
    if sb >= 2 and int(play.get("free_used", 0)) < (2 if sb >= 3 else 1):
        return 0
    if dk(pid, "cons", "build") >= 2 and not t.is_empty() and int(t.market) == 3:
        return 0
    if card_lv(pid, "mobil", "advance") >= 3:
        c -= 3
    if not t.is_empty() and int(t.market) == 0 and int(t.get("cap_by", -1)) == pid:
        if dk(pid, "cons", "build") >= 1 and int(t.get("cap_t", -1)) == turn:
            c -= 1
        if sb >= 1 and HexGrid.neighbors(homes[pid]).has(int(t.id)):
            c -= 2
    return maxi(0, c)


func _robo_built(pid: int, k: String, price: int) -> void:
    if k != "market" or play.is_empty():
        return
    var sb: int = dk(pid, "sprot", "build")
    if price == 0 and sb >= 2 and int(play.get("free_used", 0)) < (2 if sb >= 3 else 1):
        play.free_used = int(play.get("free_used", 0)) + 1
    if dk(pid, "cons", "build") >= 3:   # Scrap
        play.mk_b = int(play.get("mk_b", 0)) + 1
        if int(play.mk_b) % 2 == 0:
            players[pid].mat = mat_of(pid) + 1
            add_log("%s salvage 1 material from their new markets (Scrap)." % players[pid].name)


## A Robot Harvest's card upgrades: castle gold (Deploy), Full Yield, Market Hubs and Hub Stores (Onslaught).
func robo_harvest(pid: int) -> Dictionary:
    var cs: int = 0
    var hubs: int = 0
    for t in tiles:
        if int(t.owner) == pid:
            if t.castle:
                cs += 1
            if int(t.market) >= robo_markets():
                hubs += 1
    var hexes: int = int(income_of(pid).hexes)
    var g: int = 0
    var m: int = 0
    var why: Array = []
    var de: int = dk(pid, "deploy", "harvest")
    var on: int = dk(pid, "onsl", "harvest")
    if de >= 1:
        var per: Array = [0, 2, 5, 12]
        var names: Array = ["", "Castle Tax", "Castle Tolls", "Castle Vaults"]
        var x: int = int(per[de]) * cs
        g += x
        if x > 0:
            why.append("%s +%d" % [names[de], x])
    if on >= 1:
        var y: int = hexes - hexes / 2
        g += y
        if y > 0:
            why.append("Full Yield +%d" % y)
    if on >= 2 and hubs > 0:
        g += 5 * hubs
        why.append("Market Hubs +%d" % (5 * hubs))
    if on >= 3 and hubs > 0:
        m += 2 * hubs
        why.append("Hub Stores +%s" % mat_txt(2 * hubs))
    return {"g": g, "m": m, "why": why}


## A Robot action's card upgrades that happen when it starts: Factory, Barracks and Fortress Run (Siege Protocol's
## Advancements), and the notes for the free markets and Scrap. Returns notes for the card column.
func robo_action_start(pid: int) -> Array:
    var out: Array = []
    var a: String = card_action()
    var p: Dictionary = players[pid]
    if a == "advance":
        var l: int = dk(pid, "sprot", "advance")
        if l >= 1:   # (the log lines become the notes under your card, so the runs only log)
            if int(tiles[homes[pid]].owner) == pid:
                add_units(homes[pid], "brawler", int(GameData.rules.robots.factory_units), true)
                tiles[homes[pid]].new_t = turn
                add_log("%s run the factory: +%d Brawlers at %s home castle (Factory Run)." % [p.name, int(GameData.rules.robots.factory_units), "your" if pid == 0 else "their"])
            else:
                out.append("Factory Run: no Brawlers, because you don't hold your home castle")
        if l >= 2:
            var n: int = 0
            for t in tiles:
                if int(t.owner) == pid and int(t.barracks) > 0:
                    add_units(int(t.id), "brawler", 3, true)
                    t.new_t = turn
                    n += 1
            if n > 0:
                add_log("%s get 3 free Brawlers at each of %d barracks (Barracks Run)." % [p.name, n])
        if l >= 3:
            var nf: int = 0
            for t in tiles:
                if int(t.owner) == pid and int(t.fort) > 0:
                    add_units(int(t.id), "rknight", 2, true)
                    t.new_t = turn
                    nf += 1
            if nf > 0:
                add_log("%s get 2 free Robot Knights at each of %d fortress%s (Fortress Run)." % [p.name, nf, "es" if nf > 1 else ""])
    if a == "build":
        var sb: int = dk(pid, "sprot", "build")
        if sb >= 2:
            out.append("Two Free Markets: your first 2 markets in this action cost nothing" if sb >= 3 else "Free Market: your first market in this action costs nothing")
        if dk(pid, "cons", "build") >= 3:
            out.append("Scrap: +1 material for every 2 markets you build")
    return out


## Laser Strike (Onslaught, Move level 2): the ready Laser Tanks on a hex fire at an enemy hex next door like a trebuchet,
## with no battle (twice with Double Strike). It uses a move, and the tanks.
func laser_ok(pid: int, from: int, to: int) -> bool:
    if play.is_empty() or not is_robots(pid) or cur_action() != "move" or dk(pid, "onsl", "move") < 2:
        return false
    var s: Dictionary = tiles[from]
    var b: Dictionary = tiles[to]
    return int(s.owner) == pid and int(s.ready.get("ltank", 0)) > 0 and int(b.owner) >= 0 and int(b.owner) != pid and int(b.troops) > 0 and HexGrid.neighbors(from).has(to) and moves_left() > 0


func do_laser(pid: int, from: int, to: int) -> Dictionary:
    if not laser_ok(pid, from, to):
        return {}
    var s: Dictionary = tiles[from]
    var n: int = int(s.ready.ltank)
    s.ready.erase("ltank")
    sync_tile(s)
    play.moves = int(play.moves) + 1
    var shots: int = 0
    var kl: int = 0
    var hits: int = 0
    for q in (2 if dk(pid, "onsl", "move") >= 3 else 1):
        if int(tiles[to].troops) > 0:
            var r: Dictionary = fire_treb(from, to, "laser strike")
            shots += 1
            kl += int(r.killed)
            hits += int(r.hits)
    return {"n": n, "shots": shots, "killed": kl, "hits": hits}


## Robot trades (Mobilize): Recompile in Advancements (5 Brawlers for a Knight), Rebuild and Refit in Recruit.
func trades_at(i: int) -> Array:
    var out: Array = []
    if i < 0 or play.is_empty() or fx_on() or not is_robots(current):
        return out
    var t: Dictionary = tiles[i]
    if int(t.owner) != current:
        return out
    var T: Dictionary = GameData.rules.robots.trades
    for k in T:
        var x: Dictionary = T[k]
        if cur_action() == String(x["a"]) and dk(current, "mobil", String(x["a"])) >= int(x["l"]) and int(t.army.get(String(x["from"]), 0)) >= int(x["n"]):
            out.append(String(k))
    return out


func robo_trade(i: int, k: String) -> bool:
    if not trades_at(i).has(k):
        return false
    var x: Dictionary = GameData.rules.robots.trades[k]
    var t: Dictionary = tiles[i]
    var fk: String = String(x["from"])
    var n: int = int(x["n"])
    var rdy: bool = int(t.ready.get(fk, 0)) >= n
    take_units(i, {fk: n})
    add_units(i, String(x["to"]), 1, rdy)
    add_log("%s trade %d %s for a %s (%s)." % [players[current].name, n, GameData.units[fk].name, GameData.units[String(x["to"])].name, x["name"]])
    return true


## The Robots' card moves: extra hexes a move can reach, each only for the units that can make it.
## [{hexes: {hex: true}, ok: Callable(unit) -> bool, every: true when every unit can, why: the note}]
func robo_move_extra(from: int, lvl: int) -> Array:
    var out: Array = []
    var t: Dictionary = tiles[from]
    var pid: int = int(t.owner)
    if pid < 0 or not is_robots(pid) or play.is_empty() or current != pid or regrouping():
        return out
    var dep: int = dk(pid, "deploy", "move")
    var con: int = dk(pid, "cons", "move")
    var ons: int = dk(pid, "onsl", "move")
    var flyer := func(k): return bool(GameData.units[k].get("air", false))
    if dep >= 1 or con >= 3:   # Air Lanes (Deploy 1, Construction 3)
        var st: Dictionary = {}
        for x in tiles:
            if int(x.owner) == pid and int(x.id) != from and can_enter(int(x.id), 1):
                st[int(x.id)] = true
        if not st.is_empty():
            out.append({"hexes": st, "ok": flyer, "every": false, "why": "Only flyers can go this far (Air Lanes)."})
    if dep >= 2:   # Ridge Hop
        var st2: Dictionary = {}
        for a in HexGrid.neighbors(from):
            if tiles[a].terrain == "mountain":
                for b in HexGrid.neighbors(a):
                    if b != from and can_enter(b, lvl):
                        st2[b] = true
        if not st2.is_empty():
            out.append({"hexes": st2, "ok": flyer, "every": false, "why": "Only flyers can hop the mountain (Ridge Hop)."})
    if dep >= 3:   # Overflight
        var st3: Dictionary = {}
        for a in HexGrid.neighbors(from):
            var A: Dictionary = tiles[a]
            if int(A.owner) >= 0 and int(A.owner) != pid and int(A.troops) > 0:
                for b in HexGrid.neighbors(a):
                    if b != from and can_enter(b, lvl):
                        st3[b] = true
        if not st3.is_empty():
            out.append({"hexes": st3, "ok": flyer, "every": false, "why": "Only flyers can fly over the enemy army (Overflight)."})
    if con >= 2:   # Brawler Dash: 2 hexes, both empty
        var st4: Dictionary = {}
        for a in HexGrid.neighbors(from):
            if not can_enter(a, lvl) or int(tiles[a].troops) > 0 or not _pass_through(from, a, lvl, pid):
                continue
            for b in HexGrid.neighbors(a):
                if b != from and can_enter(b, lvl) and int(tiles[b].troops) == 0 and home_guards(tiles[b]).is_empty():
                    st4[b] = true
        if not st4.is_empty():
            out.append({"hexes": st4, "ok": func(k): return k == "brawler", "every": false, "why": "Only Brawlers can dash this far (Brawler Dash)."})
    if ons >= 1 and int(t.get("new_t", -1)) == turn:   # Fresh Units: a hex where you made units this turn
        var st5: Dictionary = {}
        for a in HexGrid.neighbors(from):
            if can_enter(a, lvl) and _pass_through(from, a, lvl, pid):
                for b in HexGrid.neighbors(a):
                    if b != from and can_enter(b, lvl):
                        st5[b] = true
        if not st5.is_empty():
            out.append({"hexes": st5, "ok": func(_k): return true, "every": true, "why": "Units made this turn go 2 hexes (Fresh Units)."})
    return out


func _robo_move_filter(from: int, to: int, lvl: int) -> Callable:
    if _move_targets_core(from, lvl, false).has(to):
        return Callable()
    var xs: Array = robo_move_extra(from, lvl).filter(func(x): return x["hexes"].has(to))
    if xs.is_empty() or xs.any(func(x): return bool(x["every"])):
        return Callable()
    return func(k): return xs.any(func(x): return bool(x["ok"].call(k)))


# =====================================================================
# Materials (Ethan, 2026-11-10)''')

# the Dinosaur hooks also run the Robots'
f.rep('''    var out: Array = []
    if not is_dinos(pid) or play.is_empty():
        return out
    var a: String = card_action()
    var p: Dictionary = players[pid]
    if a == "build":''', '''    var out: Array = []
    if is_robots(pid) and not play.is_empty():
        return robo_action_start(pid)
    if not is_dinos(pid) or play.is_empty():
        return out
    var a: String = card_action()
    var p: Dictionary = players[pid]
    if a == "build":''')
f.rep('''func _dino_built(pid: int, k: String, price: int) -> void:
    if not is_dinos(pid) or price > 0 or play.is_empty():''', '''func _dino_built(pid: int, k: String, price: int) -> void:
    if is_robots(pid):
        _robo_built(pid, k, price)
        return
    if not is_dinos(pid) or price > 0 or play.is_empty():''')

# ---------- Fortify: no more Update; Dual Core, Sortie and Home Link ----------
f.rep('''    if is_robots(pid) and raw >= 1:
        p.upd_next = true
        add_log("%s run an Update: +1 attack and +1 damage on their next turn." % p.name)
        out.append("Update: +1 attack and +1 damage on %s next turn" % ("your" if pid == 0 else "their"))''',
'''    if is_robots(pid) and raw >= 2:   # Siege Protocol, the Robots' only Fortify card
        out.append("Sortie: after your picks, a real Move that can attack or claim")
    if is_robots(pid) and raw >= 3:
        out.append("Home Link: units at your home castle can regroup to any of your hexes")''')
f.rep('''func fx_picks_at(pid: int, raw: int) -> int:
    var eff: int = 0 if (is_dinos(pid) or raw == 1) else raw''', '''func fx_picks_at(pid: int, raw: int) -> int:
    if is_robots(pid):
        return 2 if raw >= 1 else 1   # Dual Core (Siege Protocol)
    var eff: int = 0 if (is_dinos(pid) or raw == 1) else raw''')
f.rep('''        "far": 1 if l >= 1 else 0, "mv": l >= 2, "rally": 1 if l >= 3 else 0}''',
      '''        "far": 1 if l >= 1 else 0, "mv": l >= 2, "rally": 1 if l >= 3 else 0, "mvx": dk(pid, "sprot", "fortify") >= 2}   # mvx: Sortie''')
f.rep('''        if f.done.size() < int(f.n) and fx_pick_list().any(func(k): return not f.done.has(k)):
            f.ph = "pick"
            return true
    play.fx = {}
    return false''', '''        if f.done.size() < int(f.n) and fx_pick_list().any(func(k): return not f.done.has(k)):
            f.ph = "pick"
            return true
    if bool(f.get("mvx", false)) and not f.done.has("move"):   # Sortie (Siege Protocol): a real Move after the picks
        f.ph = "act"
        f.cur = "move"
        play.moves = 0
        return true
    play.fx = {}
    return false''')
f.rep('''        if f.ph == "regroup" or (f.ph == "act" and f.done.size() + 1 < int(f.n)):
            return false''', '''        var sortie: bool = bool(f.get("mvx", false)) and String(f.cur) != "move" and not f.done.has("move")
        if f.ph == "regroup" or (f.ph == "act" and (f.done.size() + 1 < int(f.n) or sortie)) or (f.ph == "pick" and sortie):
            return false''')
f.rep('''    if regrouping() and pid == current:
        return regroup_targets(from, fx_reach())
    var any_run''', '''    if regrouping() and pid == current:
        return regroup_targets(from, 99 if (dk(pid, "sprot", "fortify") >= 3 and from == homes[pid]) else fx_reach())   # Home Link (Siege Protocol)
    var any_run''')

# ---------- turn flow: the old Robot Factory is gone (Factory Run comes from robo_action_start) ----------
f.rep('''    if a == "advance" and named_on():
        if is_robots(current):
            _factory(current)
        elif is_dinos(current):''', '''    if a == "advance" and named_on():
        if is_dinos(current):''')
f.rep('''        var dh: Dictionary = dino_harvest(current) if is_dinos(current) else {"g": 0, "m": 0, "why": []}''',
      '''        var dh: Dictionary = dino_harvest(current) if is_dinos(current) else (robo_harvest(current) if is_robots(current) else {"g": 0, "m": 0, "why": []})''')

# ---------- Recruit: flyer prices (Deploy), Assembly Line (Mobilize), hexes that made units this turn ----------
f.rep('''    if int(t.get("wh", 0)) > 0 and is_mammals(pid) and GameData.rules.mammals.wh_units.has(unit):''',
      '''    if is_robots(pid) and bool(GameData.units[unit].get("air", false)):
        cost -= dk(pid, "deploy", "recruit")   # Drone Line, Air Wing, Sky Fleet (Deploy)
    if int(t.get("wh", 0)) > 0 and is_mammals(pid) and GameData.rules.mammals.wh_units.has(unit):''')
f.rep('''    p.gold = int(p.gold) - cost
    add_units(i, unit, n, true)
    var free: int = 0
    if is_robots(current) and named_on():''', '''    p.gold = int(p.gold) - cost
    add_units(i, unit, n, true)
    t.new_t = turn
    var free: int = 0
    if dk(current, "mobil", "recruit") >= 1:   # Assembly Line (Mobilize)''')
f.rep('''    p.gold = int(p.gold) - cost
    add_units(i, unit, n, true)
    add_log("%s train %d %s." % [p.name, n, GameData.units[unit].name])''', '''    p.gold = int(p.gold) - cost
    add_units(i, unit, n, true)
    t.new_t = turn
    add_log("%s train %d %s." % [p.name, n, GameData.units[unit].name])''')

# ---------- Build: Robot markets only ----------
f.rep('''    if cur_action() == "build" and is_robots(current) and named_on():
        return int(GameData.rules.robots.efficiency_max_buildings)''', '''    if not play.is_empty() and is_robots(current):
        return robo_markets()   # Robots: one factory per hex, or up to 4 markets on a resource hex''')
f.rep('''    if not play.is_empty() and is_dinos(current) and cur_action() == "build":
        return dino_cost(current, kind, c, t)
    return c''', '''    if not play.is_empty() and is_dinos(current) and cur_action() == "build":
        return dino_cost(current, kind, c, t)
    if not play.is_empty() and is_robots(current) and cur_action() == "build":
        return robo_cost(current, kind, c, t)
    return c''')
f.rep('''    if kind == "fort" and is_dinos(current):
        return false   # the Dinosaurs build no forts
    pay_b(current, kind, price)''', '''    if kind == "fort" and is_dinos(current):
        return false   # the Dinosaurs build no forts
    if is_robots(current) and (kind != "market" or not robo_can_market(t)):
        return false   # Robots: markets only; barracks and fortresses are factory upgrades from the home castle
    pay_b(current, kind, price)''')
f.rep('''    var price: int = 0 if free else bk_up_cost(current, lv)
    if mat_of(current) < price:
        return false''', '''    var price: int = 0 if free else bk_up_cost(current, lv, t)
    if mat_of(current) < price:
        return false''')
f.rep('''    add_log("%s upgrade a barracks to level %d%s." % [p.name, int(t.bk), " for free" if free else ""])
    return true''', '''    add_log("%s upgrade a barracks to level %d%s." % [p.name, int(t.bk), " for free" if free else ""])
    robo_muster(current, t)   # Muster (Onslaught)
    return true''')

# ---------- Move: the Robots' extra moves, Offline, Scavenger, captures ----------
f.rep('''    var out: Array[int] = []
    var co: bool = charge_only(pid)
    for i in _move_targets_core(from, lvl, far):''', '''    var out: Array[int] = []
    var co: bool = charge_only(pid)
    var cand: Array[int] = _move_targets_core(from, lvl, far)
    if pid >= 0 and is_robots(pid):   # the Robots' card moves: flyers, Brawlers and new units
        for x in robo_move_extra(from, lvl):
            for i in x["hexes"]:
                if not cand.has(int(i)):
                    cand.append(int(i))
    for i in cand:''')
f.rep('''    var pid: int = int(A.owner)
    var air: bool = int(B.owner) >= 0 and int(B.owner) != pid and is_floating(B)''', '''    var pid: int = int(A.owner)
    if pid >= 0 and is_robots(pid):
        var rf: Callable = _robo_move_filter(from, to, lvl)
        if rf.is_valid():
            return rf
    var air: bool = int(B.owner) >= 0 and int(B.owner) != pid and is_floating(B)''')
f.rep('''func move_filter_note(from: int, to: int) -> String:
    var B: Dictionary = tiles[to]''', '''func move_filter_note(from: int, to: int) -> String:
    var B: Dictionary = tiles[to]
    if is_robots(int(tiles[from].owner)) and not _move_targets_core(from, cur_lvl(), false).has(to):
        for x in robo_move_extra(from, cur_lvl()):
            if x["hexes"].has(to):
                return String(x["why"])''')
f.rep('''    var offline: bool = is_robots(pid) and raw >= 1 and not herd''',
      '''    var offline: bool = dk(pid, "mobil", "move") >= 3 and not herd   # Offline (Mobilize, Move level 3)''')
f.rep('''    # The hex changes hands.
    B.owner = pid''', '''    # The hex changes hands.
    if prev >= 0:   # captured from an enemy (Fresh Ground, Border Market)
        B.cap_t = turn
        B.cap_by = pid
    B.owner = pid''')
f.rep('''    if is_dinos(pid) and (int(B.treb) > 0 or int(B.treb2) > 0):''', '''    if is_robots(pid) and not B.castle and building_count(B) > 0:   # the Robots: what stood there becomes one factory, or a resource hex
        var bkx: bool = int(B.barracks) > 0 or int(B.fort) > 0
        var ftx: bool = int(B.fort) > 0 and int(B.barracks) > 0
        B.market = 1 if bkx else clampi(int(B.market), 1, robo_markets())
        B.barracks = 1 if bkx else 0
        B.fort = 1 if ftx else 0
        B.wh = 0
        if not bkx:
            B.bk = 0
        add_log("%s turn the captured buildings into a factory." % p.name)
    if is_dinos(pid) and (int(B.treb) > 0 or int(B.treb2) > 0):''')
f.rep('''            var coin: int = int(GameData.rules.coin.gold)
            p.gold = int(p.gold) + coin
            res.coin = coin
            add_log("%s take a bonus coin: +%d gold." % [p.name, coin])''', '''            var coin: int = int(GameData.rules.robots.scavenger_gold) if dk(pid, "cons", "move") >= 1 else int(GameData.rules.coin.gold)   # Scavenger
            p.gold = int(p.gold) + coin
            res.coin = coin
            add_log("%s take a bonus coin: +%d gold%s." % [p.name, coin, " (Scavenger)" if coin > int(GameData.rules.coin.gold) else ""])''')

# ---------- trebuchets: a laser strike fires the same way, without the trebuchet animation ----------
f.rep('''func fire_treb(i: int, j: int) -> Dictionary:''', '''func fire_treb(i: int, j: int, nm: String = "") -> Dictionary:''')
f.rep('''    if hits > 0:
        add_log("%s trebuchet hits: %d units killed%s." % [players[pid].name, killed_total, (", a wall loses %d" % wall_hits) if wall_hits > 0 else ""])
    else:
        add_log("%s trebuchet misses." % players[pid].name)
    if not quiet and treb_fx.size() < 24:''', '''    var what: String = nm if nm != "" else "trebuchet"
    if hits > 0:
        add_log("%s %s hits: %d units killed%s." % [players[pid].name, what, killed_total, (", a wall loses %d" % wall_hits) if wall_hits > 0 else ""])
    else:
        add_log("%s %s misses." % [players[pid].name, what])
    if not quiet and treb_fx.size() < 24 and nm == "":''')
f.save(); print('p2 rules ok')

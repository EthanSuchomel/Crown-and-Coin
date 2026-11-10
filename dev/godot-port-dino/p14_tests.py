# Godot port of the browser's Dinosaur rework (2026-11-09), self-test: the new numbers, and checks for the
# Dinosaurs' missing forts and trebuchets, Alamosaurus guards, the volcano and the Triceratops.
import sys; sys.path.insert(0,sys.path[0])
from common import F
P=sys.argv[1].rstrip('/')+'/scripts/'
t=F(P+'rules/test_rules.gd')
t.rep('''"_test_moves", "_test_sync"]:''','''"_test_moves", "_test_dinos", "_test_sync"]:''')
t.rep('''    check("Megaraptor costs 7", GameData.units.mega.cost == 7)
    check("Megaraptor has 20 health", GameData.units.mega.hp == 20)''','''    check("Megaraptor costs 12", int(GameData.units.mega.cost) == 12)
    check("Megaraptor has 35 health", int(GameData.units.mega.hp) == 35)''')
t.rep('''    check("home castle starts with 2 Gallimimus",''','''    check("home castle starts with 2 Pachycephalosaurus",''')
t.rep('''    check("recruit 3 Gallimimus at home", h.recruit(h.homes[0], 3))
    check("home now has 5 Gallimimus", int(h.tiles[h.homes[0]].army.galli) == 5)
    check("recruiting cost 6 gold", int(h.players[0].gold) == 44, str(h.players[0].gold))''','''    check("recruit 3 Pachycephalosaurus at home", h.recruit(h.homes[0], 3))
    check("home now has 5 Pachycephalosaurus", int(h.tiles[h.homes[0]].army.galli) == 5)
    check("recruiting cost 9 gold", int(h.players[0].gold) == 41, str(h.players[0].gold))''')
t.rep('''    check("10 Megaraptors beat 1 Gallimimus", bool(big.won))''','''    check("10 Megaraptors beat 1 Pachycephalosaurus", bool(big.won))''')
t.rep('''    check("1 Gallimimus loses to 10 Megaraptors", not bool(small.won))''','''    check("1 Pachycephalosaurus loses to 10 Megaraptors", not bool(small.won))''')
t.rep('''    check("3 Gallimimus break an empty wall",''','''    check("3 Pachycephalosaurus break an empty wall",''')
t.rep('''    check("arena: retired Alamosaurus and Procoptodon are left out", not c.has("alamo") and not c.has("kanga"))''',
      '''    check("arena: the Alamosaurus guard goes in; the retired Procoptodon is left out", c.has("alamo") and not c.has("kanga"))
    var AT: Dictionary = ArenaBattle.TYPES.alamo
    check("arena: Alamosaurus guard stats", int(AT.hp) == 120 and int(AT.dmg) == 15 and float(AT.rate) == 2.0 and int(AT.multi) == 4 and not AT.has("riders") and not AT.has("charge") and not AT.has("superStomp"))''')
t.rep('''func _test_ai() -> void:''','''func _test_dinos() -> void:
    # The Dinosaur rework (Ethan, 2026-11-09): no forts or trebuchets, Alamosaurus guards, the volcano.
    var g := GameState.new()
    g.new_game("dinos")
    g.begin_turn()
    g.players[0].gold = 500
    var home: int = g.homes[0]
    var n: int = _first_open_neighbor(g, home)
    g.tiles[n].owner = 0
    g.play = {"card": "nest", "step": 0, "moves": 0, "free_bk": false, "al_bought": 0, "al_free": 0}
    check("Dinosaurs can't build a fort", not g.build(n, "fort"))
    check("Dinosaurs can build a barracks", g.build(n, "barracks"))
    check("Dinosaur barracks trains 6 units, no fort units", g.faction_of(0).training.barracks.size() == 6 and g.faction_of(0).training.fort.is_empty())
    check("barracks levels: Megaraptor 1, Pterodactyl 2, Triceratops and Stegosaurus 3",
        g.barracks_needed("mega") == 1 and g.barracks_needed("ptero") == 2 and g.barracks_needed("bow") == 3 and g.barracks_needed("quetz") == 3)
    g.play.step = 1   # Advancements
    check("no trebuchets for the Dinosaurs", not g.can_treb_at(g.tiles[home]) and not g.start_trebuchet(home))
    var gold0: int = int(g.players[0].gold)
    check("hire an Alamosaurus guard", g.buy_guard(n))
    check("a guard costs 25 gold", gold0 - int(g.players[0].gold) == 25)
    check("hire a second guard", g.buy_guard(n))
    check("only 2 guards per barracks", not g.buy_guard(n))
    check("the guards are on the hex", g.guards_at(g.tiles[n]) == 2)
    check("guards can't move", int(g.tiles[n].ready.get("alamo", 0)) == 0 and int(g.tiles[n].fresh) == 0)
    check("no guard without a barracks", not g.buy_guard(home))
    check("wake the volcano for 40 gold", g.do_volcano(0) and g.volc_lv(0) == 1 and gold0 - int(g.players[0].gold) == 90)
    check("stoke it: level 2 for 60, level 3 for 100", g.do_volcano(0) and g.do_volcano(0) and g.volc_lv(0) == 3 and gold0 - int(g.players[0].gold) == 250)
    check("no volcano level 4", not g.do_volcano(0))
    g.begin_turn()
    check("guards still can't move next turn", int(g.tiles[n].ready.get("alamo", 0)) == 0)
    var holds: float = CombatRules.win_odds({"brawler": 6}, g.def_army(g.tiles[n]), {}, 200)
    check("2 guards hold their barracks against 6 Brawlers", holds < 0.3, str(holds))
    # the volcano's reach and timing
    var v := GameState.new()
    v.new_game("dinos")
    v.players[0].volc = {"lv": 1, "cd": 0}
    var near: int = -1
    var far: int = -1
    for tt in v.tiles:
        if tt.terrain != "plain" or tt.castle or int(tt.owner) >= 0:
            continue
        var d: int = HexGrid.distance(v.homes[0], int(tt.id))
        if d == 3 and near < 0:
            near = int(tt.id)
        if d >= 6 and far < 0:
            far = int(tt.id)
    check("test board has a hex 3 away and one 6+ away", near >= 0 and far >= 0)
    if near < 0 or far < 0:
        return
    v.tiles[near].owner = 1
    v.add_units(near, "brawler", 8, false)
    v.tiles[far].owner = 1
    v.add_units(far, "brawler", 8, false)
    check("a level 1 volcano reaches 5 hexes", v.volc_targets(v.homes[0]).has(near) and not v.volc_targets(v.homes[0]).has(far))
    v.players[0].volc.lv = 3
    check("a level 3 volcano reaches the whole map", v.volc_targets(v.homes[0]).has(far))
    var shot: Dictionary = v.fire_volcano(v.homes[0], far)
    check("level 3 erupts with 8 dice", shot.dice.size() == 8 and bool(shot.volc))
    check("then it waits a turn", int(v.players[0].volc.cd) == 1)
    v.players[0].volc = {"lv": 1, "cd": 3}
    var waits: Array = []
    for q in 3:
        waits.append(v.volc_ready(0))
    check("level 1 erupts every 3 turns", int(waits[0]) < 0 and int(waits[1]) < 0 and int(waits[2]) == v.homes[0], str(waits))
    # the Triceratops: shots do nothing to it
    var arrows: Dictionary = CombatRules.fight({"rarch": 10}, {"bow": 1}, {"avg": true})
    check("Robot Archers can't hurt a Triceratops", CombatRules.count(arrows.def_lost) == 0)


func _test_ai() -> void:''')
# the Rhino test measured against 8 of the old 8-health Gallimimus; the same strength now is 4 Pachycephalosaurus
t.rep('''    var plain: float = CombatRules.win_odds({"ape": 6}, {"galli": 8}, {}, 200)
    var rh: float = CombatRules.win_odds({"ape": 4, "rhino": 1}, {"galli": 8}, {}, 200)''','''    var plain: float = CombatRules.win_odds({"ape": 6}, {"galli": 4}, {}, 200)   # (4 Pachycephalosaurus: about the old 8 Gallimimus)
    var rh: float = CombatRules.win_odds({"ape": 4, "rhino": 1}, {"galli": 4}, {}, 200)''')
t.save()
print('p14 tests ok')

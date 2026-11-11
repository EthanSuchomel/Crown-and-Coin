# Godot port, step 5: the self-test follows the new decks and checks materials, Fortify and the Dinosaur cards.
import sys
F = sys.argv[1] + '/scripts/rules/test_rules.gd'
s = open(F, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        print('COUNT', n, 'for', old[:160]); sys.exit(1)
    s = s.replace(old, new)

rep('''"_test_moves", "_test_dinos", "_test_sync"]:''', '''"_test_moves", "_test_dinos", "_test_sync", "_test_fortify_materials", "_test_dino_cards"]:''')
# The Hunt is now Harvest, Recruit, Advancements; Stampede has the Build
rep('''	h.play = {"card": "hunt", "step": 2, "moves": 0, "free_bk": false, "al_bought": 0, "al_free": 0}
	check("recruit 3 Pachycephalosaurus at home", h.recruit(h.homes[0], 3))
	check("home now has 5 Pachycephalosaurus", int(h.tiles[h.homes[0]].army.galli) == 5)
	check("recruiting cost 9 gold", int(h.players[0].gold) == 41, str(h.players[0].gold))
	h.play.step = 1''', '''	h.play = {"card": "hunt", "step": 1, "moves": 0, "free_bk": false, "al_bought": 0, "al_free": 0}
	check("recruit 3 Pachycephalosaurus at home", h.recruit(h.homes[0], 3))
	check("home now has 5 Pachycephalosaurus", int(h.tiles[h.homes[0]].army.galli) == 5)
	check("recruiting cost 9 gold", int(h.players[0].gold) == 41, str(h.players[0].gold))
	h.play = {"card": "stamp", "step": 1, "moves": 0, "free_bk": false, "al_bought": 0, "al_free": 0}''')
# Nesting Season is now Harvest, Build, Fortify; The Hunt has the Advancements. Barracks cost materials.
rep('''	g.play = {"card": "nest", "step": 0, "moves": 0, "free_bk": false, "al_bought": 0, "al_free": 0}
	check("Dinosaurs can't build a fort", not g.build(n, "fort"))''', '''	g.play = {"card": "nest", "step": 1, "moves": 0, "free_bk": false, "al_bought": 0, "al_free": 0}
	g.players[0].mat = 5
	check("Dinosaurs can't build a fort", not g.build(n, "fort"))''')
rep('''	g.play.step = 1   # Advancements''', '''	g.play = {"card": "hunt", "step": 2, "moves": 0, "free_bk": false, "al_bought": 0, "al_free": 0}   # Advancements''')

s = s.rstrip('\n') + '''


func _test_fortify_materials() -> void:
	# materials: the home castle sells 3 a turn, 2 gold each; a barracks costs 5 of them
	var g := GameState.new()
	g.new_game("robots")
	g.begin_turn()
	g.players[0].gold = 30
	check("materials: the home castle sells 3 a turn", g.mat_cap(0) == 3 and g.mat_left(0) == 3)
	check("materials: buying 3 costs 6 gold", g.buy_mat(0, 5) == 3 and int(g.players[0].gold) == 24 and g.mat_of(0) == 3)
	check("materials: no more this turn", g.buy_mat(0, 1) == 0)
	var home: int = g.homes[0]
	var n: int = _first_open_neighbor(g, home)
	g.tiles[n].owner = 0
	g.play = {"card": "cons", "step": 1, "moves": 0, "free_bk": false, "al_bought": 0, "al_free": 0}   # Construct: Build
	check("materials: a barracks needs 5", not g.build(n, "barracks"))
	g.players[0].mat = 5
	var gold0: int = int(g.players[0].gold)
	check("materials: a barracks for 5 materials, no gold", g.build(n, "barracks") and g.mat_of(0) == 0 and int(g.players[0].gold) == gold0)
	check("materials: a market costs 6 gold", g.build(n, "market") and int(g.players[0].gold) == gold0 - 6)
	g.tiles[n].market = 1
	check("materials: a market sells 3 more", g.mat_cap(0) == 6 + 3 * (g.markets_of(0) - 1))
	g.begin_turn()
	check("materials: the count resets each turn", int(g.players[0].tr) == 0)
	# Fortify: the regroup (2 hexes, units stay ready), then a pick
	var f := GameState.new()
	f.new_game("robots")
	f.begin_turn()
	f.players[0].hand = ["sprot", "cons", "mobil"]
	f.players[0].gold = 40
	var h0: int = f.homes[0]
	var a: int = _first_open_neighbor(f, h0)
	f.tiles[a].owner = 0
	var b: int = -1
	for j in HexGrid.neighbors(a):
		if j != h0 and f.tiles[j].terrain == "plain" and not f.tiles[j].castle and int(f.tiles[j].owner) < 0 and not HexGrid.neighbors(h0).has(j):
			b = j
			break
	if b >= 0:
		f.tiles[b].owner = 0
	f.players[0].favor = {}
	check("fortify: play Siege Protocol", f.play_card("sprot"))
	f.next_step()   # Advancements
	f.next_step()   # Fortify
	check("fortify: starts with a regroup", f.card_action() == "fortify" and f.regrouping() and f.cur_action() == "move")
	check("fortify: regroup reaches 2 hexes through your land", b < 0 or (f.move_targets(h0, 0).has(b) and f.move_targets(h0, 0).has(a)))
	var before: int = int(f.tiles[h0].fresh)
	var r: Dictionary = f.move(h0, a, {"brawler": 2})
	check("fortify: a regroup move", r.get("kind", "") == "move" and int(f.tiles[a].troops) == 2)
	check("fortify: units that regroup stay ready", int(f.tiles[a].fresh) == 2 and int(f.tiles[h0].fresh) == before - 2)
	check("fortify: no attacks in a regroup", f.move_targets(a, 0).all(func(i): return int(f.tiles[i].owner) == 0))
	check("fortify: the button doesn't end the turn yet", not f.last_step_now())
	f.next_step()
	check("fortify: then a pick", f.cur_action() == "fortify" and String(f.play.fx.ph) == "pick" and int(f.play.fx.n) == 1)
	check("fortify: pick Recruit", f.fx_choose("recruit") and f.cur_action() == "recruit")
	check("fortify: only one pick at level 0", not f.fx_choose("build"))
	check("fortify: the recruit plays", f.recruit(h0, 2))
	check("fortify: last pick ends the turn", f.last_step_now())
	check("fortify: no defense bonus any more", f.def_bonus(f.tiles[a]) == 0)
	check("fortify: 2 picks at level 2, 3 at level 3", f.fx_picks_at(0, 2) == 2 and f.fx_picks_at(0, 3) == 3 and f.fx_picks_at(0, 1) == 1)
	# the computer plays a Fortify card all the way through
	var c := GameState.new()
	c.new_game("mammals", [], "dinos")
	c.begin_turn()
	c.players[0].ai = true
	var ev: Array = AIPlayer.run_card(c, 0, "den")
	var acts: Array = ev.filter(func(e): return e.kind == "step").map(func(e): return String(e.action))
	check("fortify: the computer regroups and picks", acts.size() == 4 and acts[2] == "fortify" and ["build", "advance", "recruit"].has(acts[3]) and c.play.get("fx", {}).is_empty(), str(acts))
	# the Mythical: a Mage that moved can still plant
	var m := GameState.new()
	m.new_game("mythical")
	m.begin_turn()
	var mh: int = m.homes[0]
	var mn: int = _first_open_neighbor(m, mh)
	m.tiles[mn].owner = 0
	m.add_units(mn, "mage0", 1, false)
	m.play = {"card": "arcan", "step": 0, "moves": 0}
	check("mythical: a Mage that moved can plant a Life Tree", m.myth_plant(0, mn) and int(m.tiles[mn].tree) == 1)


func _test_dino_cards() -> void:
	var g := GameState.new()
	g.new_game("dinos")
	g.begin_turn()
	var home: int = g.homes[0]
	var n: int = _first_open_neighbor(g, home)
	g.tiles[n].owner = 0
	g.tiles[n].barracks = 1
	# The Hunt, Harvest 1: Hunting Grounds, 1 gold per hex instead of 1 per 2
	g.players[0].up = {"hunt": [1, 3, 3], "stamp": [0, 3, 0], "pack": [3, 1, 3], "siege": [0, 3, 0], "nest": [2, 0, 0]}
	g.play = {"card": "hunt", "step": 0, "moves": 0, "free_bk": false, "al_bought": 0, "al_free": 0}
	var hx: int = int(g.income_of(0).hexes)
	var g0: int = int(g.players[0].gold)
	g._resolve_instant("harvest")
	check("dino cards: Hunting Grounds pays a gold per hex", int(g.players[0].gold) - g0 == 2 + hx / 2 + (hx - hx / 2), str(int(g.players[0].gold) - g0))
	check("dino cards: the usual upgrade levels don't apply", g.cur_lvl() == 0 and not g.named_on())
	# Siege of Teeth Harvest 3: materials
	g.play = {"card": "siege", "step": 1, "moves": 0}
	var m0: int = g.mat_of(0)
	g._resolve_instant("harvest")
	check("dino cards: Big Quarry and Castle Stores give materials", g.mat_of(0) - m0 == int(g.income_of(0).hexes) / 2 + 1)
	# Nesting Season Harvest 2: Stockpile, +5 materials
	g.play = {"card": "nest", "step": 0, "moves": 0}
	m0 = g.mat_of(0)
	g._resolve_instant("harvest")
	check("dino cards: Stockpile +5 materials", g.mat_of(0) - m0 == 5)
	# Stampede Build 3: Free Market, Supplies, Cheap Nests
	g.play = {"card": "stamp", "step": 1, "moves": 0}
	g.players[0].mat = 0
	g.dino_action_start(0)
	check("dino cards: Supplies +2 materials", g.mat_of(0) == 2)
	check("dino cards: the first market is free", g.build_cost("market", g.tiles[n]) == 0 and g.build(n, "market") and g.build_cost("market", g.tiles[n]) == 5)
	check("dino cards: Cheap Nests, a barracks for 4 materials", g.build_cost("barracks") == 4)
	# The Hunt Recruit 3 and Advancements 3
	g.play = {"card": "hunt", "step": 1, "moves": 0}
	check("dino cards: Home Hunters and Nest Hunters", g.unit_cost_at(home, 0, "mega") == 11 and g.unit_cost_at(n, 0, "mega") == 11)
	g.play = {"card": "hunt", "step": 2, "moves": 0, "free_bk": false}
	g.players[0].gold = 100
	check("dino cards: Quick Nests and Cheap Guards", g.bk_up_cost(0, 0) == 2 and g.guard_cost() == 22)
	check("dino cards: forge Armor for 40 gold", g.do_armor(0) and int(g.players[0].gold) == 60 and g.armor_on(0))
	var o: Dictionary = g.atk_opts(0, 0, 0, 1)
	check("dino cards: Armor in board battles", int(o.a_plus) == 2 and bool(o.a_arm))
	var am: Dictionary = g.arena_mods({"att": 0, "def": 1, "mods": g.fight_mods(0, 0, 1)})
	var t0: int = g.arena_team(0)
	check("dino cards: Armor in the Arena, +2 damage and +10% health", int(am.plus[t0]) == 2 and is_equal_approx(float(am.hp[t0]), 1.1))
	# Pack Call: Fortify 3 (Join Up, On the Move, Rally) and Recruit 1 (Calling)
	g.play = {"card": "pack", "step": 2, "moves": 0}
	g.fx_begin(0)
	check("dino cards: Pack Call's Fortify sets Join Up, Move and Rally", int(g.play.fx.far) == 1 and bool(g.play.fx.mv) and int(g.play.fx.rally) == 1 and g.fx_pick_list().has("move"))
	g.add_units(n, "galli", 3, true)
	var all0: int = g.unit_total(0)
	check("dino cards: Rally brings every ready unit to one hex", g.rally_to(n) > 0 and int(g.tiles[home].fresh) == 0 and g.unit_total(0) == all0)
	g.play = {"card": "pack", "step": 1, "moves": 0}
	var u0: int = int(g.tiles[n].troops)
	g.dino_action_start(0)
	check("dino cards: Calling puts 3 Pachycephalosaurus on the only nesting ground", int(g.tiles[n].troops) == u0 + 3)
	# Stampede Fortify 2 (Hatchlings, Raptor Brood)
	g.players[0].up.stamp = [0, 0, 2]
	g.play = {"card": "stamp", "step": 2, "moves": 0}
	var mg: int = int(g.tiles[n].army.get("mega", 0))
	g.fx_begin(0)
	check("dino cards: Raptor Brood hatches a Megaraptor at each nesting ground", int(g.tiles[n].army.get("mega", 0)) == mg + 1)
	check("dino cards: one Fortify pick", int(g.play.fx.n) == 1)
	# Stampede Move 1: Charge (3 moves, the last an attack)
	g.players[0].up.stamp = [1, 0, 0]
	g.play = {"card": "stamp", "step": 0, "moves": 0}
	check("dino cards: Charge gives a third move", g.moves_left() == 3)
	g.play.moves = 2
	check("dino cards: the extra move must be an attack", g.charge_only(0))
	# Stampede Move 3: Two Herds
	var h := GameState.new()
	h.new_game("dinos")
	h.begin_turn()
	h.players[0].up = {"stamp": [3, 0, 0]}
	h.play = {"card": "stamp", "step": 0, "moves": 0}
	var H: int = h.homes[0]
	var a2: int = -1
	var f2: int = -1
	for x in HexGrid.neighbors(H):
		if h.tiles[x].terrain != "plain" or h.tiles[x].castle:
			continue
		for y in HexGrid.neighbors(x):
			if y != H and HexGrid.neighbors(H).has(y) and h.tiles[y].terrain == "plain" and not h.tiles[y].castle:
				a2 = x
				f2 = y
				break
		if a2 >= 0:
			break
	if a2 >= 0:
		h.tiles[a2].owner = 0
		h.add_units(a2, "mega", 2, true)
		h.tiles[f2].owner = 1
		h.add_units(f2, "brawler", 1, false)
		check("dino cards: Two Herds finds the hex next door", h.two_herds_hex(H, f2) == a2)
		var res2: Dictionary = h.move(H, f2, {"galli": 2}, true)
		check("dino cards: Two Herds sends both herds", int(res2.get("sent", {}).get("mega", 0)) == 2 and int(h.tiles[a2].army.get("mega", 0)) == 0, str(res2.get("sent", {})))
'''
open(F, 'w', encoding='utf-8').write(s)
print('test ok')

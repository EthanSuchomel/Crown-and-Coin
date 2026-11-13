# The Robot rework for the Godot version, step 6: the self-test (test_rules.gd).
# Two older checks built a barracks and counted Fortify picks with the Robots; those now use the Mammals (and a Robot
# check for Dual Core). New: _test_robots, the factories, resource hexes and every kind of Robot card upgrade.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import F
f = F(sys.argv[1] + '/scripts/rules/test_rules.gd')
f.rep('''"_test_dino_cards", "_test_three"]:''', '''"_test_dino_cards", "_test_three", "_test_robots"]:''')
f.rep('''    var g := GameState.new()
    g.new_game("robots")
    g.begin_turn()
    g.players[0].gold = 30
    check("materials: the home castle sells 3 a turn"''', '''    var g := GameState.new()
    g.new_game("mammals")   # (the Robots build no barracks since 2026-11-11)
    g.begin_turn()
    g.players[0].gold = 30
    check("materials: the home castle sells 3 a turn"''')
f.rep('''    g.play = {"card": "cons", "step": 1, "moves": 0, "free_bk": false, "al_bought": 0, "al_free": 0}   # Construct: Build''',
      '''    g.play = {"card": "roam", "step": 1, "moves": 0, "free_bk": false, "al_bought": 0, "al_free": 0}   # The Long Roam: Build''')
f.rep('''    check("fortify: 2 picks at level 2, 3 at level 3", f.fx_picks_at(0, 2) == 2 and f.fx_picks_at(0, 3) == 3 and f.fx_picks_at(0, 1) == 1)''',
'''    var fm := GameState.new()
    fm.new_game("mammals")
    check("fortify: 2 picks at level 2, 3 at level 3", fm.fx_picks_at(0, 2) == 2 and fm.fx_picks_at(0, 3) == 3 and fm.fx_picks_at(0, 1) == 1)
    check("fortify: the Robots pick 2 with Dual Core, 1 without", f.fx_picks_at(0, 1) == 2 and f.fx_picks_at(0, 3) == 2 and f.fx_picks_at(0, 0) == 1)''')
f.s = f.s.rstrip('\n') + '\n' + '''

## The Robot rework (browser 2026-11-11/12): factories, resource hexes and each Robot card's own upgrades.
func _test_robots() -> void:
	var g := GameState.new()
	g.new_game("robots")
	g.begin_turn()
	var home: int = g.homes[0]
	var n: int = _first_open_neighbor(g, home)
	g.tiles[n].owner = 0
	check("robots: Mobilize is Advancements, Recruit, Move; Construct is Construction", g.card_of(0, "mobil").actions == ["advance", "recruit", "move"] and String(g.card_of(0, "cons").name) == "Construction")
	check("robots: each card has its own upgrades", g.d_up(0, "sprot", "fortify") and g.dcard("onsl", "move").size() == 3 and g.card_ups(0))
	# Build: markets only; one factory per hex, or up to 4 markets (a resource hex)
	g.players[0].gold = 100
	g.players[0].mat = 30
	g.play = {"card": "cons", "step": 1, "moves": 0, "free_bk": false, "al_bought": 0, "al_free": 0}
	check("robots: the usual upgrade levels don't apply", g.cur_lvl() == 0 and not g.named_on())
	check("robots: no barracks or forts in Build", not g.build(n, "barracks") and not g.build(n, "fort"))
	check("robots: a market starts a factory", g.build(n, "market") and g.robo_next(g.tiles[n]) == "barracks")
	check("robots: more markets make a resource hex, up to 4", g.build(n, "market") and g.build(n, "market") and g.build(n, "market") and not g.build(n, "market") and int(g.tiles[n].market) == 4)
	check("robots: a resource hex takes no barracks", g.robo_next(g.tiles[n]) == "" and not g.robo_can_market(g.tiles[n]))
	# Advancements: the home castle adds a barracks, then the fortress, to a single market
	var m: int = -1
	for j in HexGrid.neighbors(home):
		if j != n and g.tiles[j].terrain == "plain" and not g.tiles[j].castle and int(g.tiles[j].owner) < 0:
			m = j
			break
	g.tiles[m].owner = 0
	g.tiles[m].market = 1
	g.play = {"card": "cons", "step": 1, "moves": 0}
	check("robots: factory upgrades aren't made in Build", not g.do_robo_up(0, m, "barracks"))
	g.play = {"card": "cons", "step": 2, "moves": 0, "free_bk": false}
	var mat0: int = g.mat_of(0)
	var tb: Array = g.robo_up_targets(0, "barracks")
	check("robots: a barracks on a market, 5 materials", tb.size() == 1 and int(tb[0]) == m and g.do_robo_up(0, m, "barracks") and g.mat_of(0) == mat0 - 5 and int(g.tiles[m].barracks) == 1)
	var tf: Array = g.robo_up_targets(0, "fort")
	check("robots: then its fortress", tf.size() == 1 and int(tf[0]) == m and g.do_robo_up(0, m, "fort") and int(g.tiles[m].fort) == 1 and g.robo_lv(g.tiles[m]) == 3)
	check("robots: a factory takes no more markets", not g.robo_can_market(g.tiles[m]))
	# prices: Quick Barracks, Quick Fortress, Home Grid; Overclock
	g.players[0].up = {"cons": [1, 2, 3], "mobil": [1, 0, 0], "sprot": [3, 3, 3], "onsl": [3, 2, 3], "deploy": [3, 3, 3]}
	check("robots: Quick Barracks and Quick Fortress", g.robo_up_cost(0, "barracks") == 4 and g.robo_up_cost(0, "fort") == 4 and g.bk_up_cost(0, 0) == 2)
	g.play = {"card": "mobil", "step": 0, "moves": 0, "free_bk": false}
	check("robots: Home Grid, 1 material less next to the home castle", g.robo_up_cost(0, "barracks", g.tiles[m]) == 4 and g.robo_up_cost(0, "barracks") == 5 and g.bk_up_cost(0, 0, g.tiles[m]) == 2)
	g.play = {"card": "cons", "step": 2, "moves": 0, "free_bk": false}
	g.players[0].gold = 100
	check("robots: Overclock for 40 gold", g.can_armor(0) and g.do_armor(0) and g.armor_on(0) and int(g.players[0].gold) == 60)
	# Muster (Onslaught, Advancements 2): a barracks upgrade makes 2 Brawlers and a Robot Archer
	g.play = {"card": "onsl", "step": 1, "moves": 0, "free_bk": false}
	g.players[0].mat = 30
	var u0: int = int(g.tiles[m].troops)
	check("robots: Muster Archers", g.upgrade_barracks(m) and int(g.tiles[m].troops) == u0 + 3 and int(g.tiles[m].army.get("rarch", 0)) == 1)
	# Siege Protocol's Advancements 3: Factory, Barracks and Fortress Run
	g.play = {"card": "sprot", "step": 1, "moves": 0, "free_bk": false}
	var h0: int = int(g.tiles[home].army.get("brawler", 0))
	var b0: int = int(g.tiles[m].army.get("brawler", 0))
	var k0: int = int(g.tiles[m].army.get("rknight", 0))
	g.dino_action_start(0)
	check("robots: Factory, Barracks and Fortress Run", int(g.tiles[home].army.get("brawler", 0)) == h0 + 5 and int(g.tiles[m].army.get("brawler", 0)) == b0 + 3 and int(g.tiles[m].army.get("rknight", 0)) == k0 + 2)
	# Build prices: Two Free Markets, Cheap Markets, Fourth Free, Fresh Ground
	var free: Array = []
	for t in g.tiles:
		if t.terrain == "plain" and not t.castle and int(t.owner) < 0 and free.size() < 4:
			free.append(int(t.id))
	for i in free:
		g.tiles[i].owner = 0
	g.players[0].gold = 100
	g.play = {"card": "sprot", "step": 0, "moves": 0}
	check("robots: Two Free Markets", g.build_cost("market", g.tiles[free[0]]) == 0 and g.build(free[0], "market") and g.build(free[1], "market") and g.build_cost("market", g.tiles[free[2]]) == 6 and int(g.players[0].gold) == 100)
	g.players[0].up.mobil = [3, 0, 0]
	g.players[0].up.cons = [2, 3, 3]   # Construction: Move 2 (Scavenger, Brawler Dash), Build 3 (to Scrap), Advancements 3
	g.play = {"card": "cons", "step": 1, "moves": 0}
	g.tiles[free[2]].market = 3
	check("robots: Cheap Markets (for good) and Fourth Free", g.build_cost("market", g.tiles[free[3]]) == 3 and g.build_cost("market", g.tiles[free[2]]) == 0)
	g.tiles[free[3]].cap_by = 0
	g.tiles[free[3]].cap_t = g.turn
	check("robots: Fresh Ground, 1 less on a hex captured this turn", g.build_cost("market", g.tiles[free[3]]) == 2)
	var mk0: int = g.mat_of(0)
	g.build(free[2], "market")
	g.build(free[3], "market")
	check("robots: Scrap, +1 material for every 2 markets", g.mat_of(0) == mk0 + 1)
	# Harvest: Castle Vaults (Deploy 3); Full Yield, Market Hubs and Hub Stores (Onslaught 3)
	g.play = {"card": "deploy", "step": 0, "moves": 0}
	check("robots: Castle Vaults, +12 a castle", int(g.robo_harvest(0).g) == 12 * g.castle_count(0))
	g.play = {"card": "onsl", "step": 0, "moves": 0}
	var rh: Dictionary = g.robo_harvest(0)
	var hx: int = int(g.income_of(0).hexes)
	var hubs: int = g.tiles.filter(func(t): return int(t.owner) == 0 and int(t.market) >= 4).size()
	check("robots: Full Yield, Market Hubs and Hub Stores", int(rh.g) == (hx - hx / 2) + 5 * hubs and int(rh.m) == 2 * hubs and hubs >= 1)
	# Recruit: Sky Fleet (Deploy 3)
	g.play = {"card": "deploy", "step": 1, "moves": 0}
	check("robots: Sky Fleet, flyers 3 gold less (at least 1)", g.unit_cost_at(home, 0, "gunship") == int(GameData.units.gunship.cost) - 3 and g.unit_cost_at(home, 0, "drone") == 1)
	# Move: Air Lanes (Deploy 1), only flyers
	g.play = {"card": "deploy", "step": 2, "moves": 0}
	g.add_units(home, "drone", 2, true)
	var far: int = free[1]
	check("robots: Air Lanes reach any of your hexes", g.move_targets(home, g.cur_lvl()).has(far) and not g._move_targets_core(home, 0, false).has(far))
	var r: Dictionary = g.move(home, far, {"drone": 2, "brawler": 2})
	check("robots: only flyers make that move", r.get("kind", "") == "move" and int(g.tiles[far].army.get("drone", 0)) == 2 and int(g.tiles[far].army.get("brawler", 0)) == 0)
	# Mobilize's Move 3: Extra Thread, Climb, Offline
	g.players[0].up.mobil = [3, 3, 3]
	g.play = {"card": "mobil", "step": 2, "moves": 0}
	check("robots: Extra Thread, Climb and Offline", g.moves_limit(0) == 3 and g.cur_lvl() == 1 and bool(g.atk_opts(0, g.cur_lvl(), 0, 1).surprise) and bool(g.fight_mods(0, 1, 1).sneak))
	# Brawler Dash (Construction 2) and Fresh Units (Onslaught 1)
	g.play = {"card": "cons", "step": 0, "moves": 0}
	var dash: Array = g.robo_move_extra(home, 0)
	check("robots: Brawler Dash is for Brawlers", dash.any(func(x): return bool(x["ok"].call("brawler")) and not bool(x["ok"].call("rarch"))))
	g.play = {"card": "onsl", "step": 2, "moves": 0}
	check("robots: Fresh Units, a hex that made units this turn", g.robo_move_extra(m, 0).any(func(x): return bool(x["every"])))
	# Laser Strike and Double Strike (Onslaught 3)
	var foe: int = -1
	for j in HexGrid.neighbors(m):
		if g.tiles[j].terrain == "plain" and int(g.tiles[j].owner) < 0 and not g.tiles[j].castle:
			foe = j
			break
	g.tiles[foe].owner = 1
	g.add_units(foe, "galli", 40, false)
	g.add_units(m, "ltank", 1, true)
	check("robots: Laser Strike can fire at the army next door", g.laser_ok(0, m, foe))
	var lr: Dictionary = g.do_laser(0, m, foe)
	check("robots: Double Strike fires twice and uses a move and the tanks", int(lr.shots) == 2 and int(g.play.moves) == 1 and int(g.tiles[m].ready.get("ltank", 0)) == 0)
	# captures: whatever stood there becomes one factory
	var tc: Dictionary = g.tiles[foe]
	tc.army = {}
	tc.ready = {}
	g.sync_tile(tc)
	tc.market = 2
	tc.barracks = 1
	tc.bk = 1
	g.execute_move(m, foe, {"brawler": 1}, 0)
	check("robots: captured buildings become one factory", int(tc.owner) == 0 and int(tc.market) == 1 and int(tc.barracks) == 1 and int(tc.fort) == 0 and int(tc.cap_by) == 0)
	# Scavenger (Construction, Move 1): a bonus coin pays 12
	g.play = {"card": "cons", "step": 0, "moves": 0}
	var cb: int = -1
	for j in HexGrid.neighbors(home):
		if g.tiles[j].terrain == "plain" and int(g.tiles[j].owner) < 0 and not g.tiles[j].castle:
			cb = j
	if cb >= 0:
		g.tiles[cb].bounty = true
		var gb: int = int(g.players[0].gold)
		g.execute_move(home, cb, {"brawler": 1}, 0)
		check("robots: Scavenger, a bonus coin pays 12", int(g.players[0].gold) == gb + 12)
	# Mobilize: Assembly Line, Rebuild, Refit, Recompile
	g.play = {"card": "mobil", "step": 1, "moves": 0, "free_bk": false, "al_bought": 0, "al_free": 0}
	g.players[0].gold = 100
	var al0: int = int(g.tiles[home].army.get("brawler", 0))
	check("robots: Assembly Line, a 3rd Brawler free", g.recruit(home, 4) and int(g.tiles[home].army.get("brawler", 0)) == al0 + 6)
	g.add_units(home, "brawler", 10, true)
	g.add_units(home, "rarch", 5, true)
	var ta: Array = g.trades_at(home)
	check("robots: Rebuild and Refit in Recruit", ta.has("rk") and ta.has("rl") and not ta.has("ak"))
	var kn0: int = int(g.tiles[home].army.get("rknight", 0))
	var bw0: int = int(g.tiles[home].army.get("brawler", 0))
	check("robots: Rebuild trades 8 Brawlers for a Knight", g.robo_trade(home, "rk") and int(g.tiles[home].army.get("rknight", 0)) == kn0 + 1 and int(g.tiles[home].army.get("brawler", 0)) == bw0 - 8)
	g.play = {"card": "mobil", "step": 0, "moves": 0, "free_bk": false}
	check("robots: Recompile in Advancements", g.trades_at(home).has("ak") and not g.trades_at(home).has("rk"))
	# Siege Protocol's Fortify 3: Dual Core, Sortie and Home Link
	var p2: int = -1
	var p3: int = -1
	for a in HexGrid.neighbors(n):
		if a == home or HexGrid.neighbors(home).has(a) or g.tiles[a].terrain != "plain" or g.tiles[a].castle:
			continue
		for b in HexGrid.neighbors(a):
			if b != n and HexGrid.distance(b, home) == 3 and g.tiles[b].terrain == "plain" and not g.tiles[b].castle:
				p2 = a
				p3 = b
				break
		if p3 >= 0:
			break
	g.play = {"card": "sprot", "step": 2, "moves": 0}
	g.fx_begin(0)
	check("robots: Dual Core gives 2 picks, Sortie a Move after them", int(g.play.fx.n) == 2 and bool(g.play.fx.mvx))
	if p3 >= 0:
		g.tiles[p2].owner = 0
		g.tiles[p3].owner = 0
		check("robots: Home Link, the home castle regroups past 2 hexes", g.move_targets(home, 0).has(p3) and not g.regroup_targets(home, g.regroup_reach()).has(p3))
	g.fx_next()   # the regroup is over: the picks
	check("robots: the turn doesn't end before the Sortie", not g.last_step_now())
	g.fx_next()   # skip the picks: the Sortie
	check("robots: Sortie is a real Move", g.cur_action() == "move" and not g.regrouping() and g.moves_limit(0) >= 2)
	check("robots: after the Sortie, the picks are still there, then it ends", g.fx_next() and String(g.play.fx.ph) == "pick" and not g.fx_next())
	# the computer plays a whole Robot game for a while without stopping
	var c := GameState.new()
	c.new_game("dinos", [], "robots")
	c.players[0].ai = true
	c.begin_turn()
	for k in 40:
		if c.over >= 0:
			break
		AIPlayer.take_turn(c)
	var rb: Array = c.tiles.filter(func(t): return int(t.owner) == 1)
	var fac_n: int = rb.filter(func(t): return int(t.barracks) > 0).size()
	var too_many: bool = rb.any(func(t): return not t.castle and (int(t.barracks) > 1 or int(t.fort) > 1 or (int(t.barracks) > 0 and int(t.market) > 1) or int(t.market) > 4))
	check("robots: the computer keeps to one factory or a resource hex per hex", not too_many, "factories %d" % fac_n)
'''
f.save(); print('p6 test ok')

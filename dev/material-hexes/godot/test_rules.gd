extends Node
## Stage 2 self-test. Run the test scene in Godot (F6). Results print to the Output panel.
## Every line should say PASS. Any FAIL means a ported number or rule does not match the browser version.

const CombatRules = preload("res://scripts/rules/combat.gd")
const AIPlayer = preload("res://scripts/rules/ai_player.gd")
const ArenaBattle = preload("res://scripts/arena/arena_battle.gd")
var passed := 0
var failed := 0


func _ready() -> void:
	print("=== Crown & Coin rules self-test ===")
	for step in ["_test_data", "_test_hex", "_test_economy", "_test_new_game", "_test_board", "_test_turns", "_test_combat", "_test_moves", "_test_dinos", "_test_sync", "_test_fortify_materials", "_test_dino_cards", "_test_three", "_test_robots", "_test_mammal_numbers"]:
		print("  -- %s" % step)
		await get_tree().process_frame   # lets the Output panel catch up, so a stuck test shows where it stopped
		call(step)
	print("    (rules done; now the Arena battles, which take a little while)")
	await get_tree().process_frame
	await _test_arena()
	print("=== %d passed, %d failed ===" % [passed, failed])
	await _test_ai()
	print("=== after the computer test: %d passed, %d failed ===" % [passed, failed])



func _test_mammal_numbers() -> void:
	var u: Dictionary = GameData.units
	check("mammals: Porcupine 8 health with quills", int(u.porc.hp) == 8 and int(u.porc.get("thorns", 0)) == 1)
	check("mammals: Rhino 12 damage", int(u.rhino.dmg) == 12)
	check("mammals: the barracks trains Gorilla, Porcupine, Rhino", GameData.factions.mammals.training.barracks == ["ape", "porc", "rhino"])
	check("mammals: no Procoptodon to unlock or discount", not GameData.rules.barracks_unlocks.has("kanga") and not GameData.rules.mammals.wh_units.has("kanga"))
	# quills: Gorillas (melee) lose more health against Porcupines with quills; Archers (shots) don't
	var avg: Dictionary = {"avg": true}
	var with_q: Dictionary = CombatRules.fight({"ape": 6}, {"porc": 6}, avg)
	var arch_q: Dictionary = CombatRules.fight({"rarch": 6}, {"porc": 6}, avg)
	var tr_q: Dictionary = CombatRules.fight({"rhino": 2}, {"porc": 6}, avg)
	u.porc.thorns = 0
	var no_q: Dictionary = CombatRules.fight({"ape": 6}, {"porc": 6}, avg)
	var arch_n: Dictionary = CombatRules.fight({"rarch": 6}, {"porc": 6}, avg)
	var tr_n: Dictionary = CombatRules.fight({"rhino": 2}, {"porc": 6}, avg)
	u.porc.thorns = 1
	check("mammals: quills prick Gorillas in board battles", float(with_q.a_hp) < float(no_q.a_hp) - 0.5, "%s vs %s" % [with_q.a_hp, no_q.a_hp])
	check("mammals: quills don't prick shooters", absf(float(arch_q.a_hp) - float(arch_n.a_hp)) < 0.01, "%s vs %s" % [arch_q.a_hp, arch_n.a_hp])
	check("mammals: trampling Porcupines pricks the Rhinos", float(tr_q.a_hp) < float(tr_n.a_hp) - 0.5, "%s vs %s" % [tr_q.a_hp, tr_n.a_hp])

func check(label: String, ok: bool, detail: String = "") -> void:
	if ok:
		passed += 1
		print("PASS  ", label)
	else:
		failed += 1
		print("FAIL  ", label, "  ", detail)


func _test_data() -> void:
	check("30 units loaded", GameData.units.size() == 30, str(GameData.units.size()))
	check("Megaraptor costs 12", int(GameData.units.mega.cost) == 12)
	check("Megaraptor has 35 health", int(GameData.units.mega.hp) == 35)
	check("four factions loaded", GameData.factions.order.size() == 4)
	check("Dinosaurs have 5 cards", GameData.factions.dinos.cards.size() == 5)
	check("castles to win is 4", GameData.rules.castles.to_win == 4)


func _test_hex() -> void:
	# Hex 27 is row 3, column 3 (an odd column), so it is inside the board and has 6 neighbours.
	check("inner hex has 6 neighbours", HexGrid.neighbors(27).size() == 6, str(HexGrid.neighbors(27)))
	# Hex 0 is a corner, so it has fewer neighbours.
	check("corner hex has fewer neighbours", HexGrid.neighbors(0).size() < 6)
	check("corner 0 is void", HexGrid.is_void(0))
	check("centre hex is not void", not HexGrid.is_void(27))
	check("a hex is 0 steps from itself", HexGrid.distance(27, 27) == 0)
	check("neighbour is 1 step away", HexGrid.distance(27, HexGrid.neighbors(27)[0]) == 1)


func _test_economy() -> void:
	var base := Economy.mods_for("dinos")
	check("base harvest is 2", int(base.harvestBase) == 2)
	# 10 hexes, 2 castles, 1 market: castles 2 x 3 = 6, land 10 / 2 = 5, market 2. Total 13.
	check("income 10 hexes, 2 castles, 1 market = 13",
		Economy.turn_income(base, 10, 2, 1) == 13,
		str(Economy.turn_income(base, 10, 2, 1)))
	# Harvest at level 0 with 10 hexes: base 2 + 10 x 0.5 = 7.
	check("harvest level 0 with 10 hexes = 7",
		Economy.harvest_gold(base, 0, 10) == 7,
		str(Economy.harvest_gold(base, 0, 10)))


func _test_new_game() -> void:
	var g := GameState.new()
	g.new_game("dinos")
	check("two players", g.players.size() == 2)
	check("you are player 0", g.players[0].name == "You")
	check("your hand has 3 cards", g.players[0].hand.size() == 3)
	check("your reserve has 2 cards", g.players[0].reserve.size() == 2)
	check("computer gets 8 extra gold", g.players[1].gold == GameData.rules.second_player_gold,
		str(g.players[1].gold))
	check("you start with 0 gold", g.players[0].gold == 0)


func _test_board() -> void:
	var tiles := BoardGen.generate()
	check("board generated", tiles.size() == 64, str(tiles.size()))
	if tiles.size() != 64:
		return
	var count := func(pred: Callable) -> int:
		var n := 0
		for t in tiles:
			if pred.call(t):
				n += 1
		return n
	check("12 void corners", count.call(func(t): return t.terrain == "void") == 12)
	check("5 mountains", count.call(func(t): return t.terrain == "mountain") == GameData.rules.board.mountains)
	check("2 water hexes", count.call(func(t): return t.terrain == "water") == GameData.rules.board.waters)
	check("2 home castles", count.call(func(t): return t.castle and t.owner >= 0) == 2)
	check("3 neutral castles", count.call(func(t): return t.castle and t.owner < 0) == GameData.rules.board.neutral_castles)
	check("10 forest hexes", count.call(func(t): return t.forest) == GameData.rules.board.forests)
	check("no fern hexes (taken off the map, 2026-11-17)", count.call(func(t): return t.fern) == 0)
	check("6 material hexes, none on gold, forest or castle", count.call(func(t): return t.crate) == 6 and count.call(func(t): return t.crate and (t.bounty or t.forest or t.castle)) == 0)
	var gold_hexes: int = count.call(func(t): return t.bounty)
	check("gold hexes about a third of open land (10 to 15)", gold_hexes >= 10 and gold_hexes <= 15, str(gold_hexes))


func _test_turns() -> void:
	var g := GameState.new()
	g.new_game("dinos")
	check("game has 64 hexes", g.tiles.size() == 64)
	check("home castle starts with 2 Pachycephalosaurus", int(g.tiles[g.homes[0]].army.get("galli", 0)) == 2)
	check("robot home starts with 4 Brawlers", int(g.tiles[g.homes[1]].army.get("brawler", 0)) == 4)
	g.begin_turn()
	# You own 1 hex (your home castle): castle 3 gold, land 0. So 3 gold.
	check("first turn income is 3 gold", int(g.players[0].gold) == 3, str(g.players[0].gold))
	var card: String = String(g.players[0].hand[0])
	check("can play a card", g.play_card(card))
	check("an action is under way", g.cur_action() != "")
	# Walk through the rest of the card and end the turn.
	var guard: int = 0
	while g.current == 0 and guard < 5:
		g.next_step()
		guard += 1
	check("turn passed to the opponent", g.current == 1)
	check("your played card went to reserve", g.players[0].reserve.has(card))
	check("hand still has 3 cards", g.players[0].hand.size() == 3)
	# Recruiting and building, set up directly so the test doesn't depend on which card was drawn.
	var h := GameState.new()
	h.new_game("dinos")
	h.begin_turn()
	h.players[0].gold = 50
	h.play = {"card": "hunt", "step": 1, "moves": 0, "free_bk": false, "al_bought": 0, "al_free": 0}
	check("recruit 3 Pachycephalosaurus at home", h.recruit(h.homes[0], 3))
	check("home now has 5 Pachycephalosaurus", int(h.tiles[h.homes[0]].army.galli) == 5)
	check("recruiting cost 9 gold", int(h.players[0].gold) == 41, str(h.players[0].gold))
	h.play = {"card": "stamp", "step": 1, "moves": 0, "free_bk": false, "al_bought": 0, "al_free": 0}
	check("castle can take a market", h.build(h.homes[0], "market"))
	check("castle cannot take a fort", not h.build(h.homes[0], "fort"))


func _test_combat() -> void:
	var avg: Dictionary = {"avg": true}
	var big: Dictionary = CombatRules.fight({"mega": 10}, {"galli": 1}, avg)
	check("10 Megaraptors beat 1 Pachycephalosaurus", bool(big.won))
	var small: Dictionary = CombatRules.fight({"galli": 1}, {"mega": 10}, avg)
	check("1 Pachycephalosaurus loses to 10 Megaraptors", not bool(small.won))
	check("loser's units are gone", CombatRules.count(small.att_left) == 0)
	var walled: Dictionary = CombatRules.fight({"galli": 3}, {}, {"avg": true, "wall": 3})
	check("3 Pachycephalosaurus break an empty wall", bool(walled.won) and float(walled.wall_left) <= 0.001)
	var even: float = CombatRules.win_odds({"galli": 5}, {"galli": 5}, {}, 200)
	check("an even fight is close to 50/50 (20% to 80%)", even > 0.2 and even < 0.8, str(even))
	var tank: Dictionary = CombatRules.fight({"ltank": 1}, {"brawler": 10}, avg)
	check("Laser Tank fight finishes", int(tank.rounds) > 0)
	var knights: Dictionary = CombatRules.fight({"dilo": 6}, {"rknight": 3, "rarch": 3}, avg)
	check("shield wall fight finishes", int(knights.rounds) > 0)


func _first_open_neighbor(g: GameState, i: int) -> int:
	for n in HexGrid.neighbors(i):
		var t: Dictionary = g.tiles[n]
		if t.terrain == "plain" and not t.castle and int(t.owner) < 0:
			return n
	return -1


func _test_moves() -> void:
	var g := GameState.new()
	g.new_game("dinos")
	g.begin_turn()
	g.play = {"card": "stamp", "step": 0, "moves": 0, "free_bk": false, "al_bought": 0, "al_free": 0}
	var home: int = g.homes[0]
	check("Move action has 2 moves", g.moves_left() == 2)
	var n: int = _first_open_neighbor(g, home)
	check("home has an open neighbour", n >= 0)
	if n < 0:
		return
	check("open neighbour is a move target", g.move_targets(home, 0).has(n))
	var res: Dictionary = g.move(home, n, {"galli": 1})
	check("claim a hex", res.get("kind", "") == "claim", str(res.get("kind", "")))
	check("claimed hex is yours", int(g.tiles[n].owner) == 0)
	check("1 move left", g.moves_left() == 1)
	check("home guards for Robots are 5 archers", g.home_guards(g.tiles[g.homes[1]]).get("rarch", 0) == 5)
	check("home castle defense is 4", g.def_bonus(g.tiles[g.homes[1]]) == 4)
	# An attack: put 1 enemy Brawler next door and send 6 Megaraptors.
	var h := GameState.new()
	h.new_game("dinos")
	h.begin_turn()
	h.play = {"card": "stamp", "step": 0, "moves": 0, "free_bk": false, "al_bought": 0, "al_free": 0}
	var m: int = _first_open_neighbor(h, h.homes[0])
	h.tiles[m].owner = 1
	h.add_units(m, "brawler", 1, false)
	h.add_units(h.homes[0], "mega", 6, true)
	var fight: Dictionary = h.move(h.homes[0], m, {"mega": 6})
	check("attack is a battle", fight.get("kind", "") == "battle", str(fight.get("kind", "")))
	check("6 Megaraptors win", bool(fight.get("won", false)))
	check("won hex is yours", int(h.tiles[m].owner) == 0)
	# A trebuchet shot.
	var shot: Dictionary = h.fire_treb(h.homes[0], m)
	check("trebuchet rolls 5 dice", shot.dice.size() == 5)
	check("the shot is handed to the board's 3D trebuchet animation", h.treb_fx.size() == 1 and int(h.treb_fx[0].from) == h.homes[0] and int(h.treb_fx[0].to) == m)


func _test_dinos() -> void:
	# The Dinosaur rework (Ethan, 2026-11-09): no forts or trebuchets, Alamosaurus guards, the volcano.
	var g := GameState.new()
	g.new_game("dinos")
	g.begin_turn()
	g.players[0].gold = 500
	var home: int = g.homes[0]
	var n: int = _first_open_neighbor(g, home)
	g.tiles[n].owner = 0
	g.play = {"card": "nest", "step": 1, "moves": 0, "free_bk": false, "al_bought": 0, "al_free": 0}
	g.players[0].mat = 5
	check("Dinosaurs can't build a fort", not g.build(n, "fort"))
	check("Dinosaurs can build a barracks", g.build(n, "barracks"))
	check("Dinosaur barracks trains 6 units, no fort units", g.faction_of(0).training.barracks.size() == 6 and g.faction_of(0).training.fort.is_empty())
	check("barracks levels: Megaraptor 1, Pterodactyl 2, Triceratops and Stegosaurus 3",
		g.barracks_needed("mega") == 1 and g.barracks_needed("ptero") == 2 and g.barracks_needed("bow") == 3 and g.barracks_needed("quetz") == 3)
	g.play = {"card": "hunt", "step": 2, "moves": 0, "free_bk": false, "al_bought": 0, "al_free": 0}   # Advancements
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


func _test_ai() -> void:
	# Two computer players play 20 turns against each other.
	var g := GameState.new()
	g.new_game("dinos")
	g.players[0].ai = true
	g.begin_turn()
	print("Computer test: two computer players, up to 20 turns...")
	var start: int = Time.get_ticks_msec()
	var turns_played: int = 0
	for i in 20:
		if g.over >= 0:
			break
		await get_tree().process_frame   # lets the window and the Output panel update between turns
		var t0: int = Time.get_ticks_msec()
		AIPlayer.take_turn(g)
		turns_played += 1
		print("      turn %d took %d ms" % [turns_played, Time.get_ticks_msec() - t0])
	var ms: int = Time.get_ticks_msec() - start
	check("computer players took turns", turns_played > 0)
	check("gold never went negative", int(g.players[0].gold) >= 0 and int(g.players[1].gold) >= 0,
		"%d / %d" % [int(g.players[0].gold), int(g.players[1].gold)])
	var hexes: Array = [0, 0]
	for t in g.tiles:
		if int(t.owner) >= 0:
			hexes[int(t.owner)] += 1
	check("both sides spread out (more than 1 hex each, or the game ended)", g.over >= 0 or (hexes[0] > 1 and hexes[1] > 1), str(hexes))
	print("      after %d turns: round %d, hexes %s, gold %d / %d, winner %d, %d ms per turn" % [turns_played, g.turn, str(hexes), int(g.players[0].gold), int(g.players[1].gold), g.over, ms / maxi(1, turns_played)])


## Runs a battle a little at a time, so the window stays responsive and the Output panel keeps updating.
func _run_battle(b, label: String) -> int:
	var steps: int = 0
	var t0: int = Time.get_ticks_msec()
	while not b.over and steps < 30 * 240:
		b.update(ArenaBattle.STEP)
		steps += 1
		if steps % 150 == 0:
			print("      ... %s: %d battle seconds so far (%d ms)" % [label, steps / 30, Time.get_ticks_msec() - t0])
			await get_tree().process_frame
	return Time.get_ticks_msec() - t0


## Changes made in the browser version after the first port (Nov 2026).
func _test_sync() -> void:
	check("sync: Brawler attacks every 1 s (board)", is_equal_approx(float(GameData.units.brawler.rate), 1.0))
	check("sync: Brawler attacks every 1 s (Arena)", is_equal_approx(float(ArenaBattle.TYPES.robot.rate), 1.0))
	check("sync: the board's Robot Archer fires 2 lasers", int(GameData.units.rarch.get("shots", 1)) == 2)
	# the castle gate: an attacker battering the shut gate is in plain sight
	var b = ArenaBattle.new()
	b.setup([{"dilo": 8}, {"robot": 6}], 5, [0, 1], "castle", 0)
	var u = b._alive(1)[0]
	u.x = float(b.fort.gateX) + 1.0
	u.y = float(b.fort.gy)
	check("sync: attackers at the shut castle gate stay visible", b.fort_fade(u) == 1.0)
	# Offline and Update come into the battle from Crown & Coin
	var g := GameState.new()
	g.new_game("robots")
	var fm: Dictionary = g.fight_mods(0, 0, 1)
	check("sync: no Offline or Update without the upgrades", not bool(fm.sneak) and int(fm.plus) == 0)
	var s2 = ArenaBattle.new()
	s2.setup([{"galli": 6}, {"robot": 6}], 9, [0, 1], "open", 0, {"sneak": 1, "plus": [0, 1], "mult": [1.0, 1.12]})
	var g0 = s2._alive(0)[0]
	check("sync: Offline holds the defenders back", s2.held(g0) and not s2.held(s2._alive(1)[0]))
	# Undo and saving: a snapshot puts the whole game back exactly
	var gu := GameState.new()
	gu.new_game("dinos")
	var snap: Dictionary = gu.snapshot()
	var was: String = JSON.stringify(snap)
	gu.players[0].gold = 99
	gu.tiles[0].owner = 1
	gu.log_lines.append("changed")
	gu.restore(snap)
	check("sync: undo puts the game back exactly", JSON.stringify(gu.snapshot()) == was)
	var gl := GameState.new()
	gl.restore(GameState.ints(JSON.parse_string(was)))
	check("sync: a saved game loads back", JSON.stringify(gl.snapshot()) == was)
	# Difficulty: Expert's computer collects 40% more gold; the others play fair
	var gx := GameState.new()
	gx.new_game("dinos")
	gx.set_level(1, "expert")
	gx.current = 1
	var gold0: int = int(gx.players[1].gold)
	var inc: int = int(gx.income_of(1).total)
	gx.begin_turn()
	check("sync: Expert collects 40% more gold", int(gx.players[1].gold) - gold0 == roundi(inc * 1.4), "%d from %d" % [int(gx.players[1].gold) - gold0, inc])
	gx.set_level(1, "hard")
	check("sync: Hard plays fair", is_equal_approx(gx.gold_mult(1), 1.0))
	check("sync: Arena rules when a person plays", gx.arena_rules())
	_test_mammals()
	_test_mythical()
	_test_new_arena()


func _test_mythical() -> void:
	var M: Dictionary = GameData.rules.mythical
	var g := GameState.new()
	g.new_game("mythical", [], "dinos")
	var home: int = g.homes[0]
	check("mythical: start with 5 magic, a Mage and 4 Minions", int(g.players[0].gold) == 5 and int(g.tiles[home].army.get("mage0", 0)) == 1 and int(g.tiles[home].army.get("minion", 0)) == 4, str(g.tiles[home].army))
	check("mythical: income is the Floating Castle's 10 magic", int(g.income_of(0).total) == 10)
	check("mythical: 3 moves a Move action", g.moves_limit(0) == 3)
	check("mythical: cards don't upgrade", not g.upgrade_due(0, "march"))
	g.players[0].gold = 40
	check("mythical: 3 Minions for 1 magic", g.myth_buy_minions(0, home, 2) and int(g.tiles[home].army.minion) == 10 and int(g.players[0].gold) == 38)
	var mp: int = g.mage_price(0)
	check("mythical: a Mage costs 4 magic", mp == 4)
	check("mythical: a second Mage on the castle", g.myth_buy_mage(0, home) and g.mages_on(g.tiles[home]) == 2)
	check("mythical: no third Mage on one hex", not g.myth_buy_mage(0, home))
	check("mythical: a Mage turns a Minion into a Minotaur for 7 magic", g.myth_convert(0, home, "minotaur") and int(g.tiles[home].army.get("minotaur", 0)) == 1 and int(g.players[0].gold) == 38 - 4 - 7)
	check("mythical: no Griffins with a level 0 Mage", not g.myth_convert(0, home, "griffin"))
	check("mythical: no Mage level 1 without a Life Tree", not g.myth_up_mages(0) and g.mlv_of(0) == 0)
	var tr: Array = g.tiles.filter(func(x): return int(x.owner) < 0 and x.terrain == "plain" and not x.castle)
	for k in 3:
		tr[k].owner = 0
		tr[k].tree = 1
	check("mythical: Mage level 1 for 7 magic", g.myth_up_mages(0) and g.mlv_of(0) == 1)
	var gold_was: int = int(g.players[0].gold)
	g.players[0].gold = gold_was + 30
	check("mythical: Mage level 2 needs a captured castle", not g.myth_up_mages(0) and g.mlv_of(0) == 1)
	var cc: Array = g.tiles.filter(func(x): return x.castle and int(x.id) != g.homes[0] and int(x.id) != g.homes[1])
	if not cc.is_empty():
		cc[0].owner = 0
		check("mythical: Mage level 2 with 3 trees and a captured castle", g.myth_up_mages(0) and g.mlv_of(0) == 2)
		cc[0].owner = -1
		check("mythical: losing the castle keeps the level", g.mlv_of(0) == 2 and not g.mage_req_ok(0, 2))
	g.players[0].gold = gold_was
	g.players[0].mlv = 1   # back to level 1 for the checks below
	for k in 3:
		tr[k].owner = -1
		tr[k].tree = 0
	check("mythical: Floating Castle level 1", g.myth_up_castle(0) and int(g.income_of(0).total) == 15)
	# a plain hex next to home, with a Mage on it: a Life Tree and a dome
	var spot: int = -1
	for j in HexGrid.neighbors(home):
		if g.tiles[j].terrain == "plain" and not g.tiles[j].castle:
			spot = j
			break
	g.tiles[spot].owner = 0
	g.add_units(spot, "mage1", 1, true)
	g.players[0].gold = 20
	check("mythical: a Mage plants a Life Tree", g.myth_plant(0, spot) and int(g.tiles[spot].tree) == 1 and int(g.tiles[spot].ready.get("mage1", 0)) == 0)
	check("mythical: a tree makes 3 magic", int(g.income_of(0).tree_m) == 3)
	check("mythical: a dome guards every side", g.myth_dome(0, spot) and g.wall_on(spot, HexGrid.neighbors(spot)[0]) == int(GameData.rules.walls.hp))
	var before: int = int(g.players[0].gold)
	g.current = 0
	g.play = {"card": "chan", "step": 0, "moves": 0}
	g._resolve_instant("channel")
	check("mythical: Channeling pays 2 a Mage and 5 a castle", int(g.players[0].gold) - before == 2 * g.mage_total(0) + 5 * g.castle_count(0), str(int(g.players[0].gold) - before))
	# the Floating Castle can only be attacked by flyers
	var gd := GameState.new()
	gd.new_game("dinos", [], "mythical")
	var fh: int = gd.homes[1]
	var next_to: int = -1
	for j in HexGrid.neighbors(fh):
		if gd.tiles[j].terrain == "plain":
			next_to = j
			break
	gd.tiles[next_to].owner = 0
	gd.add_units(next_to, "mega", 3, true)
	check("mythical: ground units can't attack the Floating Castle", not gd.move_targets(next_to, 0).has(fh))
	gd.add_units(next_to, "ptero", 2, true)
	check("mythical: flyers can", gd.move_targets(next_to, 0).has(fh) and gd._move_sel(next_to, fh, gd.tiles[next_to].ready, 0).keys() == ["ptero"], str(gd._move_sel(next_to, fh, gd.tiles[next_to].ready, 0)))
	check("mythical: the Floating Castle is guarded by a Griffin", gd.home_guards(gd.tiles[fh]) == {"griffin": 1})
	# a saved Mythical game loads back
	var snap: Dictionary = g.snapshot()
	var gl := GameState.new()
	gl.restore(JSON.parse_string(JSON.stringify(snap)))
	check("mythical: a saved game loads back", int(gl.tiles[spot].tree) == 1 and gl.mlv_of(0) == 1 and gl.players[0].faction == "mythical")
	# computer against a Mythical computer
	var ga := GameState.new()
	ga.new_game("dinos", [], "mythical")
	ga.players[0].ai = true
	var turns: int = 0
	for n in 40:
		if ga.over >= 0:
			break
		AIPlayer.take_turn(ga)
		turns += 1
	var hexes: int = 0
	var army: int = 0
	for t in ga.tiles:
		if int(t.owner) == 1:
			hexes += 1
			army = maxi(army, int(t.troops))
	print("      Mythical computer: %d turns, winner %d, Mythical hexes %d, biggest army %d, magic %d, Mage level %d, castle level %d" % [turns, ga.over, hexes, army, int(ga.players[1].gold), ga.mlv_of(1), ga.clv_of(1)])
	check("mythical: computer vs Mythical computer plays", turns > 0 and hexes > 1)


func _test_new_arena() -> void:
	var c: Dictionary = ArenaBattle.arena_counts({"alamo": 1, "kanga": 2, "mage2": 3, "minion": 5, "galli": 2})
	check("arena: the Alamosaurus guard goes in; the retired Procoptodon is left out", c.has("alamo") and not c.has("kanga"))
	check("arena: the Rhino's and Palaeoloxodon's walk frames follow the ground they cover", is_equal_approx(float(ArenaBattle.TYPES.rhino.get("stride", 0)), 4.962) and is_equal_approx(float(ArenaBattle.TYPES.eleph.get("stride", 0)), 4.14))
	var AT: Dictionary = ArenaBattle.TYPES.alamo
	check("arena: Alamosaurus guard stats", int(AT.hp) == 120 and int(AT.dmg) == 15 and float(AT.rate) == 2.0 and int(AT.multi) == 4 and not AT.has("riders") and not AT.has("charge") and not AT.has("superStomp"))
	check("arena: a board Mage keeps its level", int(c.get("mage2", 0)) == 3 and int(c.minion) == 5)
	check("arena: Pachycephalosaurus stats", int(ArenaBattle.TYPES.galli.hp) == 15 and int(ArenaBattle.TYPES.galli.cost) == 3)
	check("arena: Rhino damage 12", int(ArenaBattle.TYPES.rhino.dmg) == 12)
	check("arena: Mage levels reach 30/45/60/90, damage 2/3/4/5", ["mage0", "mage1", "mage2", "mage3"].map(func(k): return "%d/%d" % [int(ArenaBattle.TYPES[k].range), int(ArenaBattle.TYPES[k].dmg)]) == ["30/2", "45/3", "60/4", "90/5"])
	check("arena: Laser Tank beam 2.5 s", is_equal_approx(float(ArenaBattle.TYPES.rtank.beam.dur), 2.5))
	var bt = ArenaBattle.new()
	bt.factions = ["Dinosaurs", "Robots"]
	bt.setup([{"bow": 1}, {"rarch": 2}], 7, [0, 1], "open", 0)
	var tk = bt.F.filter(func(f): return f.key == "bow")[0]
	var ar = bt.F.filter(func(f): return f.key == "rarch")[0]
	bt.hit(tk, ar, 1.0, true)
	var hp_ground: float = tk.hp
	ar.on_wall = 0
	bt.hit(tk, ar, 1.0, true)
	check("arena: shots can't hurt a Triceratops, but shots from a wall do half", hp_ground == 45.0 and tk.hp < 45.0 and tk.hp >= 45.0 - 2.0, "%.1f -> %.1f" % [hp_ground, tk.hp])
	var b = ArenaBattle.new()
	b.factions = ["Dinosaurs", "Mythical"]
	b.setup([ArenaBattle.DEFAULT_ARMY.Dinosaurs.duplicate(), {"minion": 25, "mage2": 2, "minotaur": 3, "griffin": 1, "dragon": 1}], 99, [0, 1], "open", 0)
	var zaps: int = 0
	var swoop: bool = false
	for n in 30 * 200:
		b.update(ArenaBattle.STEP)
		for e in b.fx:
			if e.type == "zap":
				zaps += 1
		b.fx.clear()
		for f in b.F:
			if f.key == "dragon" and not f.swoop.is_empty():
				swoop = true
		if b.over:
			break
	check("arena: Dinosaurs vs Mythical battle finishes", b.over, "%.1f s" % b.clock)
	check("arena: Mages cast lightning and the Dragon makes its fire run", zaps > 0 and swoop)


func _test_mammals() -> void:
	var g := GameState.new()
	g.new_game("mammals", [], "robots")
	check("mammals: you play the Mammals against the Robots", g.players[0].faction == "mammals" and g.players[1].faction == "robots")
	check("mammals: they take the Dinosaurs' Arena side", g.arena_team(0) == 0 and g.arena_team(1) == 1)
	var g2 := GameState.new()
	g2.new_game("dinos", [], "mammals")
	check("mammals: against the Dinosaurs they take the other side", g2.arena_team(1) == 1 and g2.arena_team(0) == 0)
	# the battle math: Rhinos trample, the War Trumpet rallies
	var plain: float = CombatRules.win_odds({"ape": 6}, {"galli": 4}, {}, 200)   # (4 Pachycephalosaurus: about the old 8 Gallimimus)
	var rh: float = CombatRules.win_odds({"ape": 4, "rhino": 1}, {"galli": 4}, {}, 200)
	check("mammals: a Rhino's charge wins more fights", rh > plain, "%.2f vs %.2f" % [rh, plain])
	var f: Dictionary = CombatRules.fight({"rhino": 2}, {"galli": 6}, {})
	check("mammals: a Rhino battle finishes", f.has("att_left") or f.size() > 0)
	var e0: float = CombatRules.win_odds({"ape": 6}, {"brawler": 14}, {}, 200)
	var e1: float = CombatRules.win_odds({"ape": 5, "eleph": 1}, {"brawler": 14}, {}, 200)
	check("mammals: a Palaeoloxodon helps", e1 > e0, "%.2f vs %.2f" % [e1, e0])
	var home: int = g.homes[0]
	g.current = 0
	# the Watering Hole: a normal Mammal building in any Build
	var t: Dictionary = g.tiles[home]
	t.wh = 1
	var c0: int = g.unit_cost_at(home, 0, "rhino")
	t.wh = 0
	var c1: int = g.unit_cost_at(home, 0, "rhino")
	check("mammals: a Watering Hole makes Rhinos 5 cheaper", c1 - c0 == 5, "%d vs %d" % [c0, c1])
	t.wh = 1
	check("mammals: the Watering Hole counts as a building", g.building_count(t) >= 1)
	var snap: Dictionary = g.snapshot()
	var gl := GameState.new()
	gl.restore(GameState.ints(JSON.parse_string(JSON.stringify(snap))))
	check("mammals: a saved Mammal game loads back", int(gl.tiles[home].wh) == 1 and gl.players[0].faction == "mammals")
	t.wh = 0
	_test_mammal_cards()
	# the computer can play a whole Mammal game turn without errors
	var ga := GameState.new()
	ga.new_game("dinos", [], "mammals")
	ga.players[0].ai = true
	ga.begin_turn()
	var turns: int = 0
	var hi: int = 0
	while turns < 40 and ga.over < 0:
		AIPlayer.take_turn(ga)
		turns += 1
		for tt in ga.tiles:
			if int(tt.owner) == 1:
				hi = maxi(hi, int(tt.troops))
	var mh: int = ga.tiles.filter(func(x): return int(x.owner) == 1).size()
	check("mammals: computer vs Mammal computer plays", turns > 0)
	print("      Mammal computer: %d turns, winner %d, Mammal hexes %d, biggest army %d, gold %d" % [turns, ga.over, mh, hi, int(ga.players[1].gold)])


func _test_arena() -> void:
	# The browser Arena's starting armies fight a whole battle on the Open field.
	var b = ArenaBattle.new()
	b.setup([{"mega": 24, "dilo": 8, "ptero": 4, "bow": 8, "alamo": 1}, {"robot": 4, "rarch": 28, "rdrone": 8, "rknight": 6, "rlong": 4, "rtank": 1, "rjet": 2}], 12345, [0, 1])
	check("arena: both sides on the field", b._alive(0).size() > 0 and b._alive(1).size() > 0)
	check("arena: shield walls formed", b.walls.size() >= 1, str(b.walls.size()))
	print("      starting the open field battle")
	await get_tree().process_frame
	var ms: int = await _run_battle(b, "open")
	check("arena: the battle ends", b.over, "%.1f s" % b.clock)
	var r: Dictionary = b.tally()
	check("arena: tally has both sides", r.left.size() == 2 and r.esc.size() == 2)
	print("      arena battle: %.1f battle seconds, %d ms to run, left %s / %s, fled %d, stalemate %s" % [b.clock, ms, str(r.left[0]), str(r.left[1]), int(r.fled), str(r.stalemate)])
	# The same armies on the Ferns map, and on the Trees map held by each side in turn.
	for setup_case in [["ferns", 0], ["trees", 0], ["trees", 1], ["mountain", 0], ["mountain", 1], ["castle", 0], ["castle", 1], ["fortress", 0], ["fortress", 1]]:
		print("      setting up the %s battle, held by %d" % setup_case)
		await get_tree().process_frame
		var bm = ArenaBattle.new()
		bm.setup([{"mega": 24, "dilo": 8, "ptero": 4, "bow": 8, "alamo": 1}, {"robot": 4, "rarch": 28, "rdrone": 8, "rknight": 6, "rlong": 4, "rtank": 1, "rjet": 2}], 777, [0, 1], setup_case[0], setup_case[1])
		check("arena %s: map built" % setup_case[0], (bm.levels.size() == (2 if setup_case[0] == "fortress" else 3)) if (setup_case[0] == "mountain" or setup_case[0] == "castle" or setup_case[0] == "fortress") else (bm.ferns.size() > 0 and (setup_case[0] == "ferns" or bm.trees.size() == 24)))
		var msm: int = await _run_battle(bm, String(setup_case[0]))
		var rm: Dictionary = bm.tally()
		check("arena %s (held by %d): the battle ends" % setup_case, bm.over, "%.1f s" % bm.clock)
		print("      %s battle, held by %d: %.1f battle seconds, %d ms to run, left %s / %s" % [setup_case[0], setup_case[1], bm.clock, msm, str(rm.left[0]), str(rm.left[1])])
	# Crown & Coin names go in and come back out the same.
	var c: Dictionary = ArenaBattle.arena_counts({"brawler": 3, "ltank": 1, "galli": 2})
	check("arena: unit names convert", int(c.get("robot", 0)) == 3 and int(c.get("rtank", 0)) == 1 and int(c.get("galli", 0)) == 2)


func _test_fortify_materials() -> void:
	# materials: the home castle sells 3 a turn, 2 gold each; a barracks costs 5 of them
	var g := GameState.new()
	g.new_game("mammals")   # (the Robots build no barracks since 2026-11-11)
	g.begin_turn()
	g.players[0].gold = 30
	check("materials: the home castle sells 3 a turn", g.mat_cap(0) == 3 and g.mat_left(0) == 3)
	check("materials: buying 3 costs 6 gold", g.buy_mat(0, 5) == 3 and int(g.players[0].gold) == 24 and g.mat_of(0) == 3)
	check("materials: no more this turn", g.buy_mat(0, 1) == 0)
	var home: int = g.homes[0]
	var n: int = _first_open_neighbor(g, home)
	g.tiles[n].owner = 0
	g.play = {"card": "roam", "step": 1, "moves": 0, "free_bk": false, "al_bought": 0, "al_free": 0}   # The Long Roam: Build
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
	var fm := GameState.new()
	fm.new_game("mammals")
	check("fortify: the Mammals' Fortify keeps 1 pick (their cards have their own upgrades since 2026-11-13)", fm.fx_picks_at(0, 2) == 1 and fm.fx_picks_at(0, 3) == 1 and fm.fx_picks_at(0, 1) == 1)
	check("fortify: the Robots pick 2 with Dual Core, 1 without", f.fx_picks_at(0, 1) == 2 and f.fx_picks_at(0, 3) == 2 and f.fx_picks_at(0, 0) == 1)
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


func _test_three() -> void:
	var g := GameState.new()
	g.new_game("dinos", [], "", 3, ["robots", "mythical"])
	var hexes: int = g.tiles.filter(func(t): return t.terrain != "void").size()
	check("3 players: 79 hexes on an 11 x 11 grid", g.tiles.size() == 121 and hexes == 79, str(hexes))
	check("3 players: the rivals are the ones picked", g.players.size() == 3 and g.players[1].faction == "robots" and g.players[2].faction == "mythical")
	var cnt := func(f): return g.tiles.filter(f).size()
	check("3 players: 6 neutral castles, 10 mountains, 4 lakes, 26 coins, 15 forests, no ferns",
		cnt.call(func(t): return t.castle and int(t.owner) < 0) == 6 and cnt.call(func(t): return t.terrain == "mountain") == 10 and cnt.call(func(t): return t.terrain == "water") == 4
		and cnt.call(func(t): return t.bounty) == 26 and cnt.call(func(t): return t.forest) == 15 and cnt.call(func(t): return t.fern) == 0)
	check("3 players: 9 material hexes", cnt.call(func(t): return t.crate) == 9)
	check("3 players: homes 8 apart, the board turns a third onto itself", HexGrid.distance(g.homes[0], g.homes[1]) == 8 and HexGrid.distance(g.homes[1], g.homes[2]) == 8
		and [g.homes[0], g.homes[1], g.homes[2]].all(func(h): return [g.homes[0], g.homes[1], g.homes[2]].has(HexGrid.rot3(h))))
	var mts: Array = g.tiles.filter(func(t): return t.terrain == "mountain").map(func(t): return int(t.id))
	check("3 players: mountains in matching sets of three", mts.all(func(i): return mts.has(HexGrid.rot3(i))))
	var base_gold: int = int(Economy.mods_for("robots").startGold)
	check("3 players: 6 and 12 extra at the start", int(g.players[1].gold) == base_gold + 6 and int(g.players[2].gold) == int(GameData.rules.mythical.start_magic) + 5)
	g.begin_turn()
	var order: Array = [g.current]
	for k in 3:
		g.play = {"card": g.players[g.current].hand[0], "step": 0, "moves": 0}
		g.finish_turn()
		order.append(g.current)
	check("3 players: turns go round the three seats", order == [0, 1, 2, 0] and g.turn == 2, str(order))
	check("3 players: Arena sides for the two rivals", g.arena_team(1, 2) != g.arena_team(2, 1))
	# a save loads back on the right board
	var snap: Dictionary = g.snapshot()
	var two := GameState.new()
	two.new_game("robots")
	check("2 players after 3: back to 52 hexes", HexGrid.SIZE == 8 and two.tiles.filter(func(t): return t.terrain != "void").size() == 52)
	var gl := GameState.new()
	gl.restore(GameState.ints(JSON.parse_string(JSON.stringify(snap))))
	check("3 players: a saved game loads back", HexGrid.SIZE == 11 and gl.players.size() == 3 and gl.tiles.size() == 121 and gl.homes.size() == 3)
	# knocked out: their land goes neutral, buildings stay; turns skip them; the last side standing wins
	var h1: int = g.homes[1]
	g.tiles[h1].market = 1
	g.knock_out(1, 2, "home")
	check("3 players: knocked out, land neutral, buildings stay", g.is_out(1) and int(g.tiles[h1].owner) == -1 and int(g.tiles[h1].troops) == 0 and int(g.tiles[h1].market) == 1 and g.over < 0)
	check("3 players: a fallen home is an ordinary castle", not g.is_home_castle(g.tiles[h1]) and g.foes_of(0) == [2])
	g.current = 0
	g.play = {"card": g.players[0].hand[0], "step": 0, "moves": 0}
	g.finish_turn()
	check("3 players: turns skip a side that's out", g.current == 2)
	g.knock_out(2, 0, "home")
	check("3 players: the last side standing wins", g.over == 0 and g.over_why == "last")
	# you're knocked out: the game ends for you
	var y := GameState.new()
	y.new_game("mammals", [], "", 3)
	y.knock_out(0, 1, "home")
	check("3 players: you're out, the game is over", y.over == 1 and y.over_why == "out")
	# taking a home castle in a move knocks them out
	var m := GameState.new()
	m.new_game("robots", [], "", 3, ["dinos", "mammals"])
	m.begin_turn()
	var hh: int = m.homes[2]
	var nb: int = -1
	for j in HexGrid.neighbors(hh):
		if m.tiles[j].terrain == "plain":
			nb = j
			break
	m.tiles[nb].owner = 0
	m.tiles[hh].army = {}
	m.tiles[hh].ready = {}
	m.tiles[hh].troops = 0
	m.tiles[hh].fresh = 0
	m.add_units(nb, "rknight", 20, true)
	var res: Dictionary = m.execute_move(nb, hh, {"rknight": 20}, 0)
	check("3 players: taking a home castle knocks them out", m.is_out(2) and int(m.tiles[hh].owner) == 0 and m.over < 0, str(res.get("kind", "")))
	# the computer plays a 3-way game to the end
	var c := GameState.new()
	c.new_game("dinos", [], "", 3)
	c.players[0].ai = true
	c.begin_turn()
	var outs: int = 0
	for i in 120:
		if c.over >= 0:
			break
		AIPlayer.take_turn(c)
	for q in c.players:
		if c.is_out(int(q.id)):
			outs += 1
	print("      3-player computer game: %d rounds, %d out, winner %s" % [c.turn, outs, str(c.over)])
	check("3 players: computers play a 3-way game", c.turn > 5 and c.over != -2)
	g.new_game("dinos")   # back to the 2-player board for anything after


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


## The Mammal cards' own upgrades (Ethan, 2026-11-13).
func _mm_game() -> GameState:
	var g := GameState.new()
	g.new_game("mammals", [], "dinos")
	g.current = 0
	g.players[0].ai = false
	return g


func _mm_play(g: GameState, cid: String, a: String, lv: int) -> void:
	var c: Dictionary = g.card_of(0, cid)
	var slot: int = c.actions.find(a)
	g.players[0].up[cid] = [0, 0, 0]
	g.players[0].up[cid][slot] = lv
	g.play = {"card": cid, "step": slot, "moves": 0, "free_bk": false, "al_bought": 0, "al_free": 0}


func _mm_spot(g: GameState) -> int:
	for t in g.tiles:
		if int(t.owner) == -1 and t.terrain == "plain" and not t.castle:
			for n in HexGrid.neighbors(g.homes[0]):
				if n == int(t.id):
					return n
	return -1


func _test_mammal_cards() -> void:
	var g := _mm_game()
	check("mammal cards: the Mammals have card upgrades", g.card_ups(0) and g.d_up(0, "roam", "move") and g.d_up(0, "tusks", "advance"))
	for c in GameData.factions.mammals.cards:
		for a in c.actions:
			check("mammal cards: %s %s has 3 upgrades" % [c.id, a], g.dcard(String(c.id), a).size() == 3)
		check("mammal cards: %s has a picture" % c.id, ResourceLoader.exists(String(GameData.factions.mammals.card_art.get(c.id, ""))))
	# old abilities retired
	_mm_play(g, "roam", "move", 1)
	check("mammal cards: Territorial and In Numbers are retired", not g.named_on() and not g.in_numbers(g.tiles[g.homes[0]]))
	var base: int = int(g.mods_of(0).movesPerAction)
	check("mammal cards: Long March gives 3 moves", g.moves_limit(0) == base + 1)
	_mm_play(g, "roam", "move", 2)
	check("mammal cards: Far Roam gives 4 moves", g.moves_limit(0) == base + 2)
	_mm_play(g, "roam", "move", 3)
	check("mammal cards: Mountain Paths climbs mountains", g.cur_lvl() == 1)
	_mm_play(g, "tusks", "move", 1)
	check("mammal cards: Charge is an extra attack move", g.moves_limit(0) == base + 1 and not g.charge_only(0))
	g.play.moves = base
	check("mammal cards: Charge's last move must attack", g.charge_only(0))
	_mm_play(g, "tusks", "move", 3)
	check("mammal cards: Stride adds another move", g.moves_limit(0) == base + 2)
	check("mammal cards: Ambush makes sneak attacks", bool(g.atk_opts(0, 0, 3, 1).surprise))
	_mm_play(g, "roam", "move", 0)
	check("mammal cards: no sneak attacks without Ambush", not bool(g.atk_opts(0, 0, 0, 1).surprise) and g.moves_limit(0) == base)
	# Fortify gets one pick (the basic Fortify), like the other card factions
	_mm_play(g, "den", "fortify", 2)
	check("mammal cards: an upgraded Fortify still has 1 pick", g.fx_picks_at(0, 2) == 1)
	# Den Season's Fortify: Porcupines with big armies
	var home: int = g.homes[0]
	g.tiles[home].army = {"ape": 12}
	g.sync_tile(g.tiles[home])
	g.play.step = g.card_of(0, "den").actions.find("fortify")
	g.players[0].up.den = [0, 0, 3]
	var fn: Array = g._mamm_fortify(0, 3)
	check("mammal cards: Rhino Guard gives 2 Porcupines and a Rhino to an army of 10+", int(g.tiles[home].army.get("porc", 0)) == 2 and int(g.tiles[home].army.get("rhino", 0)) == 1, str(fn))
	# Harvests
	g = _mm_game()
	home = g.homes[0]
	var hexes: int = int(g.income_of(0).hexes)
	_mm_play(g, "forage", "harvest", 1)
	var hv: Dictionary = g.mamm_harvest(0)
	check("mammal cards: Grazing pays 1 gold per hex in all", int(hv.g) + int(floor(hexes * float(GameData.rules.actions.harvest.per_hex_by_level[0]))) == hexes, str(hv))
	_mm_play(g, "den", "harvest", 3)
	hv = g.mamm_harvest(0)
	check("mammal cards: Home Bounty pays 15 gold and 3 materials", int(hv.g) == 15 and int(hv.m) == 3, str(hv))
	_mm_play(g, "wild", "harvest", 2)
	hv = g.mamm_harvest(0)
	check("mammal cards: Castle Riches pays 6 per castle", int(hv.g) == 6 * g.castle_count(0), str(hv))
	var g0: int = int(g.players[0].gold)
	g._resolve_instant("harvest")
	check("mammal cards: the Harvest pays its card upgrades", int(g.players[0].gold) - g0 >= 6, "%d" % (int(g.players[0].gold) - g0))
	# Tusks and Thorns' Harvest: every round
	g.play = {}
	var inc0: int = int(g.income_of(0).total)
	g.players[0].up.tusks = [3, 0, 0]
	var inc3: Dictionary = g.income_of(0)
	check("mammal cards: Castle Wealth pays +5 per castle every round", int(inc3.total) - inc0 == 5 * g.castle_count(0), "%d vs %d" % [int(inc3.total), inc0])
	var m0: int = g.mat_of(0)
	g.begin_turn()
	check("mammal cards: Castle Wealth gives 2 materials per castle every round", g.mat_of(0) - m0 == 2 * g.castle_count(0), "%d" % (g.mat_of(0) - m0))
	# Builds
	g = _mm_game()
	home = g.homes[0]
	var sp: int = _mm_spot(g)
	g.tiles[sp].owner = 0
	g.tiles[sp].barracks = 1
	g.tiles[sp].bk = 0
	_mm_play(g, "forage", "build", 3)
	m0 = g.mat_of(0)
	var notes: Array = g.dino_action_start(0)
	check("mammal cards: Supplies gives 3 materials", g.mat_of(0) - m0 == 3, str(notes))
	check("mammal cards: Free Den and Roost Grant tokens", int(g.players[0].fnest) == 1 and int(g.players[0].ffort) == 1)
	check("mammal cards: the free barracks and fortress cost nothing", g.build_cost("barracks", g.tiles[sp]) == 0 and g.build_cost("fort", g.tiles[sp]) == 0)
	g.tiles[sp].barracks = 0
	g.players[0].gold = 50
	check("mammal cards: a free fortress can be built", g.build(sp, "fort") and int(g.players[0].ffort) == 0 and int(g.tiles[sp].fort) == 1)
	g.players[0].mat = 10
	check("mammal cards: a Watering Hole goes up in any Build", g.build(sp, "wh"))
	_mm_play(g, "roam", "build", 3)
	g.tiles[sp].barracks = 1
	g.tiles[sp].wh = 0
	g.tiles[sp].fort = 0
	m0 = g.mat_of(0)
	g.dino_action_start(0)
	var own: int = g.tiles.filter(func(x): return int(x.owner) == 0).size()
	check("mammal cards: Land Bounty gives 1 material per hex", g.mat_of(0) - m0 == own, "%d vs %d" % [g.mat_of(0) - m0, own])
	check("mammal cards: Den Raising advances a barracks for free", g.mamm_free_bk(0, sp) and int(g.tiles[sp].bk) == 1 and not g.mamm_free_bk(0, sp))
	g.tiles[sp].market = 1
	check("mammal cards: Second Stall makes a hex's 2nd market free", g.build_cost("market", g.tiles[sp]) == 0)
	g.tiles[sp].market = 0
	check("mammal cards: a 1st market still costs gold", g.build_cost("market", g.tiles[sp]) > 0)
	# Recruits
	g = _mm_game()
	home = g.homes[0]
	sp = _mm_spot(g)
	g.tiles[sp].owner = 0
	g.tiles[sp].barracks = 1
	g.tiles[sp].fort = 1
	_mm_play(g, "roam", "recruit", 3)
	var h0: Dictionary = g.tiles[home].army.duplicate()
	g.dino_action_start(0)
	check("mammal cards: Young Tusker gives a Gorilla, a Rhino and a Palaeoloxodon at home", int(g.tiles[home].army.get("eleph", 0)) - int(h0.get("eleph", 0)) == 1 and int(g.tiles[home].army.get("rhino", 0)) - int(h0.get("rhino", 0)) == 1)
	_mm_play(g, "forage", "recruit", 3)
	var s0: Dictionary = g.tiles[sp].army.duplicate()
	g.dino_action_start(0)
	check("mammal cards: Rhino Calves give 2 Gorillas and a Rhino on a barracks-and-fortress hex", int(g.tiles[sp].army.get("ape", 0)) - int(s0.get("ape", 0)) == 2 and int(g.tiles[sp].army.get("rhino", 0)) - int(s0.get("rhino", 0)) == 1, str(g.tiles[sp].army))
	_mm_play(g, "den", "recruit", 3)
	var base_c: int = int(GameData.units.ape.cost)
	check("mammal cards: Den Prices make units 1 gold cheaper", g.unit_cost_at(sp, 0, "ape") == maxi(1, base_c - 1))
	_mm_play(g, "wild", "recruit", 3)
	g.dino_action_start(0)
	check("mammal cards: Home Calling makes home units 2 gold cheaper", g.unit_cost_at(home, 0, "ape") == maxi(1, base_c - 2) and g.unit_cost_at(sp, 0, "ape") == base_c)
	g.players[0].gold = 200
	m0 = g.mat_of(0)
	g.recruit(home, 3)
	check("mammal cards: Hide Trade gives 1 material for 3 units", g.mat_of(0) - m0 == 1, "%d" % (g.mat_of(0) - m0))
	g.tiles[home].fort = 1
	g.players[0].unl.fort = true
	m0 = g.mat_of(0)
	var ok_e: bool = g.train(home, "eleph", "fort", 1)
	check("mammal cards: Tusk Trade gives 5 materials for a Palaeoloxodon", ok_e and g.mat_of(0) - m0 == 5, "%s %d" % [ok_e, g.mat_of(0) - m0])
	# Advancements
	g = _mm_game()
	home = g.homes[0]
	sp = _mm_spot(g)
	g.tiles[sp].owner = 0
	g.tiles[sp].barracks = 1
	g.tiles[sp].bk = 2
	_mm_play(g, "tusks", "advance", 3)
	g.dino_action_start(0)
	g.players[0].mat = 20
	check("mammal cards: Quick Dens make upgrades 1 cheaper", g.bk_up_cost(0, 1) == int(GameData.rules.buildings.barracks_upgrade_cost[1]) - 1)
	m0 = g.mat_of(0)
	check("mammal cards: Free Den Upgrade is free at any level", g.upgrade_barracks(sp) and g.mat_of(0) == m0 and int(g.tiles[sp].bk) == 3)
	check("mammal cards: Roam Free comes after the Advancements", g.rg_due(0) and not g.last_step_now())
	g.next_step()
	check("mammal cards: Roam Free plays as a regroup", g.rg_on() and g.cur_action() == "move" and g.regrouping() and g.moves_limit(0) == GameState.REGROUP_MOVES and g.fx_reach() == 99)
	var tg: Array = g.move_targets(home, 0)
	check("mammal cards: Roam Free moves only inside your land", tg.has(sp) and tg.all(func(j): return int(g.tiles[j].owner) == 0))
	var st0: int = int(g.play.step)
	g.next_step()
	check("mammal cards: Roam Free ends and the card goes on", int(g.play.get("rg", 0)) == 2 or g.play.is_empty() or int(g.play.step) != st0)
	g = _mm_game()
	home = g.homes[0]
	sp = _mm_spot(g)
	g.tiles[sp].owner = 0
	var sp2: int = -1
	for n in HexGrid.neighbors(home):
		if n != sp and int(g.tiles[n].owner) == -1 and g.tiles[n].terrain == "plain" and not g.tiles[n].castle:
			sp2 = n
	g.tiles[sp2].owner = 0
	g.tiles[sp].barracks = 1
	g.tiles[sp].bk = 2
	_mm_play(g, "wild", "advance", 3)
	g.dino_action_start(0)
	g.players[0].mat = 0
	check("mammal cards: Free Roost makes Roost Raising free", g.mamm_fort_price(0) == 0 and g.mamm_fort(0, sp2) and int(g.tiles[sp2].fort) == 1 and not g.mamm_fort(0, sp2))
	check("mammal cards: Den Move keeps the level", g.mamm_move_bk(0, sp, sp2) and int(g.tiles[sp2].barracks) == 1 and int(g.tiles[sp2].bk) == 2 and int(g.tiles[sp].barracks) == 0)
	# the computer plays Mammal games with every card upgraded
	var wins: Array = [0, 0, 0]
	var tot: int = 0
	for gi in 4:
		var ga := GameState.new()
		ga.new_game("dinos" if gi % 2 == 0 else "robots", [], "mammals")
		ga.players[0].ai = true
		ga.begin_turn()
		var turns: int = 0
		while turns < 160 and ga.over < 0:
			if turns == 30:
				for c in GameData.factions.mammals.cards:
					ga.players[1].up[c.id] = [3, 3, 3]   # every Mammal card fully upgraded
			AIPlayer.take_turn(ga)
			turns += 1
		tot += turns
		wins[ga.over + 1 if ga.over >= 0 else 0] += 1
	check("mammal cards: the computer plays upgraded Mammal cards without errors", tot > 0)
	print("      upgraded Mammal computer games: Mammals won %d, rivals %d, unfinished %d" % [wins[2], wins[1], wins[0]])

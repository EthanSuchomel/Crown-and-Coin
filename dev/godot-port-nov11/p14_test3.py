# Godot port, step 14: self-test checks for three-player mode.
import sys
W = sys.argv[1]
F = W + '/scripts/rules/test_rules.gd'
s = open(F, encoding='utf-8').read()
a = '"_test_fortify_materials", "_test_dino_cards"]:'
assert s.count(a) == 1
s = s.replace(a, '"_test_fortify_materials", "_test_dino_cards", "_test_three"]:')
s = s.rstrip('\n') + '''


func _test_three() -> void:
	var g := GameState.new()
	g.new_game("dinos", [], "", 3, ["robots", "mythical"])
	var hexes: int = g.tiles.filter(func(t): return t.terrain != "void").size()
	check("3 players: 79 hexes on an 11 x 11 grid", g.tiles.size() == 121 and hexes == 79, str(hexes))
	check("3 players: the rivals are the ones picked", g.players.size() == 3 and g.players[1].faction == "robots" and g.players[2].faction == "mythical")
	var cnt := func(f): return g.tiles.filter(f).size()
	check("3 players: 6 neutral castles, 10 mountains, 4 lakes, 26 coins, 15 forests, 15 ferns",
		cnt.call(func(t): return t.castle and int(t.owner) < 0) == 6 and cnt.call(func(t): return t.terrain == "mountain") == 10 and cnt.call(func(t): return t.terrain == "water") == 4
		and cnt.call(func(t): return t.bounty) == 26 and cnt.call(func(t): return t.forest) == 15 and cnt.call(func(t): return t.fern) == 15)
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
'''
open(F, 'w', encoding='utf-8').write(s)
print('test3 ok')

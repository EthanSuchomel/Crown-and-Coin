# Godot port, step 10: three-player mode (browser commit b3b855e, Ethan 2026-11-09/10), offline part.
# The 79-hex board and its fair map maker, turn order that skips sides who are out, knock-outs (land goes neutral),
# catch-up gold for the 2nd and 3rd seats, the last side standing wins, the computer weighs every rival,
# computer-vs-computer battles settled on the board.
import sys, json
W = sys.argv[1]
def patch(f, pairs):
    s = open(W + f, encoding='utf-8').read()
    for old, new in pairs:
        if s.count(old) != 1: print('COUNT', s.count(old), f, old[:140]); sys.exit(1)
        s = s.replace(old, new)
    open(W + f, 'w', encoding='utf-8').write(s)

# ---------------- data: the 3-player board ----------------
B3 = json.load(open('/home/claude/crown-and-coin/dev/three-player/board3.json'))
N3 = B3['N']
r = json.load(open(W + '/data/rules.json', encoding='utf-8'))
r['board3'] = {
    '_note': "Three-player board (Ethan, 2026-11-09): an 11 x 11 grid cut to a hexagon of radius 5, less its 6 corners and the 2 edge hexes beside each corner between the homes: 79 hexes. Twice the 2-player board's mountains, water and coins. Terrain comes in 120-degree sets so every home has the same around it.",
    'size': N3, 'voids': [list(divmod(i, N3)) for i in B3['void']],
    'homes': [list(divmod(h, N3)) for h in [78, 16, 86]], 'center': [5, 5],
    'mountains': 10, 'waters': 4, 'neutral_castles': 6, 'forests': 15, 'ferns': 15, 'coins': 26}
r['three_players'] = {'_note': 'Catch-up for later seats: 3/4 of the 2-player second-seat gold (or magic) per seat behind (6 and 12 gold). The last side standing wins; no castle-count win and no siege.', 'catch_up': 0.75}
open(W + '/data/rules.json', 'w', encoding='utf-8').write(json.dumps(r, indent='\t', ensure_ascii=False) + '\n')

# ---------------- HexGrid: the board size is a setting of each game ----------------
patch('/scripts/rules/hex_grid.gd', [
 ('''## Hex math for the 8 x 8 board. Hexes are numbered 0..63 as row * 8 + column,
## matching the browser version. Ported from its rc, cube, man and nbrDirs helpers.

const SIZE := 8
''', '''## Hex math for the board. Hexes are numbered row * SIZE + column, matching the browser version.
## Ported from its rc, cube, man and nbrDirs helpers. 2 players: 8 x 8 (52 hexes). 3 players: 11 x 11 (79 hexes);
## use_board() switches (the browser's useBoard).

static var SIZE: int = 8
static var players_n: int = 0
static var _void: Dictionary = {}


## Sets the board for a 2- or 3-player game.
static func use_board(np: int) -> void:
	np = 3 if np == 3 else 2
	if players_n == np:
		return
	players_n = np
	var b: Dictionary = board_rules(np)
	SIZE = int(b.size)
	_void = {}
	for v in (b.voids if b.has("voids") else b.void_corners):
		_void[int(v[0]) * SIZE + int(v[1])] = true


## The board's settings: rules.json "board" (2 players) or "board3".
static func board_rules(np: int) -> Dictionary:
	return GameData.rules.board3 if np == 3 else GameData.rules.board


static func cell_count() -> int:
	if players_n == 0:
		use_board(2)
	return SIZE * SIZE
'''),
 ('''static func is_void(i: int) -> bool:
	var v := rc(i)
	for corner in GameData.rules.board.void_corners:
		if corner[0] == v.x and corner[1] == v.y:
			return true
	return false''', '''static func is_void(i: int) -> bool:
	if players_n == 0:
		use_board(2)
	return _void.has(i)


## The 3-player board turned a third of the way round its centre: the hex that stands where i would (-1 off the grid).
static func rot3(i: int) -> int:
	var b: Dictionary = board_rules(3)
	var c0 := cube(int(b.center[0]) * SIZE + int(b.center[1]))
	var p := cube(i)
	var X: int = c0.x + (p.z - c0.z)
	var Z: int = c0.z + (p.y - c0.y)
	var c: int = X
	var r: int = Z + (c - (c & 1)) / 2
	return -1 if (r < 0 or r >= SIZE or c < 0 or c >= SIZE) else r * SIZE + c'''),
])

# ---------------- BoardGen: any number of homes, and the symmetric 3-player maker ----------------
patch('/scripts/rules/board_gen.gd', [
 ('''const SIZE := 8


## Returns the 64 hexes, or an empty array if no fair board was found.
static func generate() -> Array:
	var rules: Dictionary = GameData.rules.board
	var homes: Array[int] = [HexGrid.index_of(6, 2), HexGrid.index_of(1, 5)]
	for attempt in range(2000):''', '''## The home castles for a 2- or 3-player board.
static func homes_for(np: int) -> Array[int]:
	HexGrid.use_board(np)
	var out: Array[int] = []
	for h in HexGrid.board_rules(np).homes if np == 3 else [GameData.rules.board.homes.you, GameData.rules.board.homes.opponent]:
		out.append(HexGrid.index_of(int(h[0]), int(h[1])))
	return out


## Returns the board's hexes, or an empty array if no fair board was found.
static func generate(np: int = 2) -> Array:
	HexGrid.use_board(np)
	if np == 3:
		return _generate3()
	var SIZE: int = HexGrid.SIZE
	var rules: Dictionary = GameData.rules.board
	var homes: Array[int] = homes_for(2)
	for attempt in range(2000):'''),
 ('''	push_error("Map generation failed after 2000 tries")
	return []''', '''	push_error("Map generation failed after 2000 tries")
	return []


## The 3-player board (the browser's genMap3): castles, mountains and water come in matching sets of three (a hex and
## the same hex turned a third and two thirds of the way round), so every home has the same around it. A peak stands in
## the very centre and the 4th water goes where it favours no one. Bonus coins at random, balanced between the homes.
static func _generate3() -> Array:
	var b: Dictionary = HexGrid.board_rules(3)
	var SIZE: int = HexGrid.SIZE
	var homes: Array[int] = homes_for(3)
	var c0: int = int(b.center[0]) * SIZE + int(b.center[1])
	var cells: Array[int] = []
	for i in SIZE * SIZE:
		if not HexGrid.is_void(i):
			cells.append(i)
	var near_home := func(i: int) -> int:
		var m: int = 999
		for h in homes:
			m = mini(m, HexGrid.distance(i, h))
		return m
	var spread := func(i: int) -> int:
		var lo: int = 999
		var hi: int = -1
		for h in homes:
			var d: int = HexGrid.distance(i, h)
			lo = mini(lo, d)
			hi = maxi(hi, d)
		return hi - lo
	for attempt in range(4000):
		var tiles := _blank_tiles()
		for p in 3:
			tiles[homes[p]].castle = true
			tiles[homes[p]].owner = p
		var taken: Dictionary = {c0: true}
		for h in homes:
			taken[h] = true
		var cs: Array = _orbits(cells, int(b.neutral_castles) / 3, taken, func(x, others): return near_home.call(x) >= 3 and others.all(func(c): return HexGrid.distance(c, x) >= 3))
		if cs.is_empty():
			continue
		for i in cs:
			tiles[i].castle = true
			taken[i] = true
		var mt: Array = _orbits(cells, (int(b.mountains) - 1) / 3, taken, func(x, _o): return near_home.call(x) >= 2)
		if mt.is_empty():
			continue
		mt.append(c0)
		for i in mt:
			tiles[i].terrain = "mountain"
			taken[i] = true
		var wa: Array = _orbits(cells, int(b.waters) / 3, taken, func(x, _o): return near_home.call(x) >= 2)
		if wa.is_empty():
			continue
		for i in wa:
			taken[i] = true
		while wa.size() < int(b.waters):
			var cand: Array = cells.filter(func(i): return not taken.has(i) and near_home.call(i) >= 2)
			if cand.is_empty():
				break
			cand.shuffle()
			cand.sort_custom(func(x, y): return spread.call(x) < spread.call(y))
			wa.append(cand[0])
			taken[cand[0]] = true
		if wa.size() < int(b.waters):
			continue
		for i in wa:
			tiles[i].terrain = "water"
		var reach := _bfs(homes[0], tiles)
		var connected := true
		for t in tiles:
			if t.terrain == "plain" and reach[t.id] == INF:
				connected = false
				break
		if not connected:
			continue
		if not _place_gold(tiles, homes, int(b.coins)):
			continue
		_place_forests(tiles, int(b.forests))
		_place_ferns(tiles, int(b.ferns))
		return tiles
	push_error("3-player map generation failed")
	return []


## k sets of three hexes, each a hex and the same hex turned a third and two thirds round. Empty if they don't fit.
static func _orbits(cells: Array[int], k: int, avoid: Dictionary, ok: Callable) -> Array:
	var out: Array = []
	for g in 300:
		if out.size() >= 3 * k:
			break
		var i: int = cells[randi() % cells.size()]
		var o: Array = [i, HexGrid.rot3(i), HexGrid.rot3(HexGrid.rot3(i))]
		if o[0] == o[1] or o[1] == o[2] or o[0] == o[2]:
			continue
		if o.any(func(x): return x < 0 or HexGrid.is_void(x) or avoid.has(x) or out.has(x)):
			continue
		var good: bool = true
		for x in o:
			var others: Array = out.duplicate()
			for y in o:
				if y != x:
					others.append(y)
			if not ok.call(x, others):
				good = false
				break
		if good:
			out.append_array(o)
	return out if out.size() >= 3 * k else []'''),
 ('''static func _blank_tiles() -> Array:
	var tiles: Array = []
	for i in SIZE * SIZE:''', '''static func _blank_tiles() -> Array:
	var tiles: Array = []
	for i in HexGrid.SIZE * HexGrid.SIZE:'''),
 ('''		var t: Dictionary = tiles[randi() % (SIZE * SIZE)]''', '''		var t: Dictionary = tiles[randi() % (HexGrid.SIZE * HexGrid.SIZE)]'''),
 ('''## Marks a balanced set of plain hexes as one-time gold hexes (a third of the open land).
static func _place_gold(tiles: Array, homes: Array[int]) -> bool:
	var pool: Array = tiles.filter(func(t): return t.terrain == "plain" and not t.castle)
	var share_parts: PackedStringArray = str(GameData.rules.coin.share).split("/")
	var share := float(share_parts[0]) / float(share_parts[1])
	var n := roundi(pool.size() * share)
	for attempt in range(400):
		var pick: Array = pool.duplicate()
		pick.shuffle()
		pick = pick.slice(0, n)
		var bal := 0
		var near0 := 0
		var near1 := 0
		for t in pick:
			var d0 := HexGrid.distance(t.id, homes[0])
			var d1 := HexGrid.distance(t.id, homes[1])
			bal += d0 - d1
			if d0 < d1:
				near0 += 1
			elif d1 < d0:
				near1 += 1
		if absi(bal) <= 1 and near0 == near1:''', '''## Marks a balanced set of plain hexes as one-time gold hexes (a third of the open land, or "count" of them):
## as far from every home castle in total, and as many closest to each one.
static func _place_gold(tiles: Array, homes: Array[int], count: int = 0) -> bool:
	var pool: Array = tiles.filter(func(t): return t.terrain == "plain" and not t.castle)
	var share_parts: PackedStringArray = str(GameData.rules.coin.share).split("/")
	var share := float(share_parts[0]) / float(share_parts[1])
	var n := count if count > 0 else roundi(pool.size() * share)
	for attempt in range(400):
		var pick: Array = pool.duplicate()
		pick.shuffle()
		pick = pick.slice(0, n)
		var sums: Array = []
		var near: Array = []
		for h in homes:
			sums.append(0)
			near.append(0)
		for t in pick:
			var ds: Array = []
			for h in homes:
				ds.append(HexGrid.distance(t.id, h))
			var m: int = ds.min()
			for k in ds.size():
				sums[k] += ds[k]
			if ds.count(m) == 1:
				near[ds.find(m)] += 1
		if sums.max() - sums.min() <= (2 if homes.size() > 2 else 1) and near.max() == near.min():'''),
 ('''	var dist: Array = []
	dist.resize(SIZE * SIZE)''', '''	var dist: Array = []
	dist.resize(HexGrid.SIZE * HexGrid.SIZE)'''),
])

# ---------------- GameState ----------------
G = '/scripts/rules/game_state.gd'
patch(G, [
 ('''func new_game(your_faction: String = "dinos", board: Array = [], opponent: String = "") -> void:
	var other: String = opponent if (opponent != "" and opponent != your_faction and GameData.factions.has(opponent)) else ("robots" if your_faction == "dinos" else "dinos")
	var faction_ids: Array[String] = [your_faction, other]
	tiles = board if not board.is_empty() else BoardGen.generate()
	for t in tiles:
		_init_tile(t)
	homes = [HexGrid.index_of(6, 2), HexGrid.index_of(1, 5)]''', '''## np: 2 or 3 players. opps: the two rivals' factions for 3 players (filled up from the faction list).
func new_game(your_faction: String = "dinos", board: Array = [], opponent: String = "", np: int = 2, opps: Array = []) -> void:
	np = 3 if np == 3 else 2
	var other: String = opponent if (opponent != "" and opponent != your_faction and GameData.factions.has(opponent)) else ("robots" if your_faction == "dinos" else "dinos")
	var faction_ids: Array = [your_faction, other] if np == 2 else [your_faction] + three_opps(your_faction, opps)
	HexGrid.use_board(np)
	tiles = board if not board.is_empty() else BoardGen.generate(np)
	for t in tiles:
		_init_tile(t)
	homes = BoardGen.homes_for(np)'''),
 ('''	for i in 2:
		var fid: String = faction_ids[i]
		var faction: Dictionary = GameData.factions[fid]
		var deck: Array = []
		for card in faction.cards:
			deck.append(card.id)
		deck.shuffle()
		var m: Dictionary = Economy.mods_for(fid)
		var second_gold: int = int(GameData.rules.second_player_gold) if i == 1 else 0''', '''	for i in np:
		var fid: String = faction_ids[i]
		var faction: Dictionary = GameData.factions[fid]
		var deck: Array = []
		for card in faction.cards:
			deck.append(card.id)
		deck.shuffle()
		var m: Dictionary = Economy.mods_for(fid)
		var second_gold: int = catch_up(i, int(GameData.rules.second_player_gold), np)'''),
 ('''			"armor": false,   # Dinosaurs (The Hunt): Armor forged
		})
	for i in 2:
		if is_myth(i):
			_myth_setup(i)   # 1 Mage, 4 Minions and 5 magic
		else:
			add_basic(homes[i], i, int(mods_of(i).startTroops), true)
	add_log("A new age begins. Win by taking the enemy home castle, holding %d castles, or wiping them off the map." % int(GameData.rules.castles.to_win))''',
  '''			"armor": false,   # Dinosaurs (The Hunt): Armor forged
			"out": false,     # 3 players: knocked out
		})
	for i in np:
		if is_myth(i):
			_myth_setup(i)   # 1 Mage, 4 Minions and 5 magic
		else:
			add_basic(homes[i], i, int(mods_of(i).startTroops), true)
	if np == 3:
		add_log("A new age begins: you, the %s and the %s. Take a side's home castle, or wipe them off the map, and they're out. The last side standing wins." % [players[1].name, players[2].name])
	else:
		add_log("A new age begins. Win by taking the enemy home castle, holding %d castles, or wiping them off the map." % int(GameData.rules.castles.to_win))


## Extra gold (or magic) for a seat that moves later: 2 players, the 2nd seat gets it all; 3 players, 3/4 of it per seat behind.
static func catch_up(i: int, base: int, np: int) -> int:
	if np > 2:
		return roundi(base * float(GameData.rules.three_players.catch_up) * i)
	return base if i == 1 else 0


## 3 players: the two rivals' factions (the ones picked, filled up from the faction list).
static func three_opps(fid: String, want: Array) -> Array:
	var o: Array = []
	for f in want:
		if GameData.factions.has(f) and f != fid and not o.has(f) and o.size() < 2:
			o.append(f)
	for f in GameData.factions.order:
		if o.size() >= 2:
			break
		if f != fid and not o.has(f):
			o.append(f)
	return o


## The sides still in the game other than pid.
func foes_of(pid: int) -> Array:
	var out: Array = []
	for q in players:
		if int(q.id) != pid and not bool(q.get("out", false)):
			out.append(int(q.id))
	return out


func foe_homes(pid: int) -> Array:
	return foes_of(pid).map(func(e): return homes[e])


func foe_tiles(pid: int) -> Array:
	var out: Array = []
	for t in tiles:
		if int(t.owner) >= 0 and int(t.owner) != pid:
			out.append(int(t.id))
	return out


func is_out(pid: int) -> bool:
	return bool(players[pid].get("out", false))


## 3 players: a side whose home castle falls (or that has no land left) is out. Its land goes neutral: its units, walls,
## trebuchets, Life Trees and domes are gone; the buildings stay for whoever walks in. The last side standing wins.
func knock_out(pid: int, by: int, why: String) -> void:
	var p: Dictionary = players[pid]
	if bool(p.get("out", false)):
		return
	p.out = true
	p.out_by = by
	p.out_why = why
	p.out_round = turn
	p.volc = {}
	for t in tiles:
		if int(t.braced) == pid:
			t.braced = -1
		if int(t.owner) != pid:
			continue
		t.owner = -1
		t.army = {}
		t.ready = {}
		t.troops = 0
		t.fresh = 0
		t.walls = [0, 0, 0, 0, 0, 0]
		t.braced = -1
		t.treb = 0
		t.treb_due = 0
		t.treb2 = 0
		t.treb2_due = 0
		t.tree = 0
		t.root = 0
		t.dome = 0
	var who: String = "You are" if pid == 0 else "The %s are" % p.name
	if by >= 0:
		add_log("%s out of the game: %s took %s home castle, and %s land goes neutral." % [who, "you" if by == 0 else "the " + String(players[by].name), "your" if pid == 0 else "their", "your" if pid == 0 else "their"])
	else:
		add_log("%s out of the game: no land left." % who)
	var left: Array = players.filter(func(q): return not bool(q.get("out", false)))
	if left.size() == 1:
		_end_game(int(left[0].id), "last")
	elif pid == 0 and not bool(p.ai):
		# you're out: the game is over for you. "over" names the side that put you out (or the biggest one left).
		var w: int = by
		if w < 0:
			var best: int = -1
			for q in left:
				var n: int = tiles.filter(func(t): return int(t.owner) == int(q.id)).size()
				if n > best:
					best = n
					w = int(q.id)
		_end_game(w, "out")'''),
 ('''	current = 1 - current
	if current == first:
		turn += 1''', '''	# the next side still in the game; a new round starts each time play passes the first seat
	var n: int = players.size()
	var c: int = done
	var round_done: bool = false
	for k in n:
		c = (c + 1) % n
		if c == first:
			round_done = true
		if not bool(players[c].get("out", false)):
			break
	current = c
	if round_done:
		turn += 1'''),
 ('''	if over >= 0:
		return
	for pid in [0, 1]:
		var has_land: bool = false''', '''	if over >= 0:
		return
	if players.size() > 2:   # 3 players: no castle-count win; a side with no land left is out
		for q in players:
			if bool(q.get("out", false)) or over >= 0:
				continue
			if not tiles.any(func(t): return int(t.owner) == int(q.id)):
				knock_out(int(q.id), -1, "wipe")
		return
	for pid in [0, 1]:
		var has_land: bool = false'''),
 ('''	var pool: Array = open.filter(func(t): return absi(HexGrid.distance(t.id, homes[0]) - HexGrid.distance(t.id, homes[1])) <= 1)''',
  '''	var hs: Array = []
	for k in players.size():
		if not is_out(k):
			hs.append(homes[k])
	var pool: Array = open.filter(func(t):
		var ds: Array = hs.map(func(h): return HexGrid.distance(t.id, h))
		return ds.max() - ds.min() <= 1)'''),
 ('''		elif to == homes[prev]:
			add_log("%s capture the enemy home castle!" % p.name)
			_end_game(pid, "home")
			return res''', '''		elif to == homes[prev]:
			if players.size() > 2:   # 3 players: it knocks them out
				add_log("%s capture %s home castle!" % [p.name, "your" if prev == 0 else "the %s'" % players[prev].name])
				res.knockout = prev
				knock_out(prev, pid, "home")
				if over >= 0:
					return res
			else:
				add_log("%s capture the enemy home castle!" % p.name)
				_end_game(pid, "home")
				return res'''),
 ('''func castle_def(t: Dictionary) -> int:
	if homes.has(int(t.id)):''', '''func castle_def(t: Dictionary) -> int:
	if is_home_castle(t):'''),
 ('''(1.5 if b.castle else 1.0) - 0.7 * wall_on(j, i) + (2.0 if homes.has(j) else 0.0)''', '''(1.5 if b.castle else 1.0) - 0.7 * wall_on(j, i) + (2.0 if is_home_castle(b) else 0.0)'''),
 ('''(1.5 if b.castle else 1.0) + (3.0 if homes.has(j) else 0.0) - 0.05 * HexGrid.distance(h, j)''', '''(1.5 if b.castle else 1.0) + (3.0 if is_home_castle(b) else 0.0) - 0.05 * HexGrid.distance(h, j)'''),
 ('''func arena_team(pid: int) -> int:
	var T: Dictionary = GameData.factions.arena_team
	var f: String = String(players[pid].faction)
	if T.has(f):
		return int(T[f])
	var other: String = String(players[1 - pid].faction)
	return 1 - int(T[other]) if T.has(other) else (0 if pid == 0 else 1)''', '''## A side's Arena team (Blue 0, Red 1) against "other" (with 2 players, the other player).
func arena_team(pid: int, other: int = -1) -> int:
	if other < 0:
		other = 1 - pid if players.size() == 2 else (1 if pid == 0 else 0)
	var T: Dictionary = GameData.factions.arena_team
	var f: String = String(players[pid].faction)
	var o: String = String(players[other].faction)
	if f == o:
		return 0 if pid < other else 1
	if T.has(f):
		return int(T[f])
	return 1 - int(T[o]) if T.has(o) else (0 if pid < other else 1)'''),
 ('''	var m: Dictionary = fight.get("mods", {})
	var t: int = arena_team(int(fight.att))''', '''	var m: Dictionary = fight.get("mods", {})
	var t: int = arena_team(int(fight.att), int(fight.def))'''),
 ('''	armies[arena_team(int(fight.att))] = fight.sel
	armies[arena_team(int(fight.def))] = def_army(tiles[int(fight.to)])''', '''	var ta: int = arena_team(int(fight.att), int(fight.def))
	armies[ta] = fight.sel
	armies[1 - ta] = def_army(tiles[int(fight.to)])'''),
 ('''		var tA: int = arena_team(pid)
		var tD: int = 1 - tA''', '''		var tA: int = arena_team(pid, prev)
		var tD: int = 1 - tA'''),
 # only battles with a person in them go to the Arena
 ('''	if arena_fights and is_fight(from, to):''', '''	if arena_fights and is_fight(from, to) and needs_arena(current, int(tiles[to].owner)):'''),
 ('''func arena_rules() -> bool:''', '''## A battle goes to the Arena when a person fights in it; computer-vs-computer battles are settled on the board.
func needs_arena(att: int, def: int) -> bool:
	if def < 0 or def >= players.size():
		return true
	return not (bool(players[att].ai) and bool(players[def].ai))


func arena_rules() -> bool:'''),
 # saves remember their board
 ('''	for p in players:
		for key in ["mat", "tr", "fnest"]:''', '''	HexGrid.use_board(players.size())
	for p in players:
		if not p.has("out"):
			p["out"] = false
		for key in ["mat", "tr", "fnest"]:'''),
])
# the board size before the tiles are read back (restore: tiles come first in SAVED)
s = open(W + G, encoding='utf-8').read()
a = '''func restore(d: Dictionary) -> void:
	if d.has("tiles"):'''
assert s.count(a) == 1
s = s.replace(a, '''func restore(d: Dictionary) -> void:
	if d.has("players"):
		HexGrid.use_board(d.players.size())
	if d.has("tiles"):''')
open(W + G, 'w', encoding='utf-8').write(s)

patch(G, [('''	p.gold = int(myth().start_magic) + (int(myth().second_magic) if i == 1 else 0)''', '''	p.gold = int(myth().start_magic) + catch_up(i, int(myth().second_magic), players.size())''')])
print('three ok')

class_name BoardGen
extends RefCounted
## Builds a random board: homes, neutral castles, mountains, water, the one-time gold hexes,
## forests and ferns. Ported from the browser version's genMap, placeCoins, placeForests,
## placeFerns and bfs. Each hex is a Dictionary; see new_tile() for its fields.

## The home castles for a 2- or 3-player board.
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
	for attempt in range(2000):
		var tiles := _blank_tiles()
		for p in 2:
			tiles[homes[p]].castle = true
			tiles[homes[p]].owner = p
		var castles: Array[int] = []
		var tries := 0
		while castles.size() < int(rules.neutral_castles) and tries < 800:
			tries += 1
			var i := randi() % (SIZE * SIZE)
			if tiles[i].castle or tiles[i].terrain != "plain":
				continue
			var d0 := HexGrid.distance(i, homes[0])
			var d1 := HexGrid.distance(i, homes[1])
			if d0 < 3 or d1 < 3 or absi(d0 - d1) > 3:
				continue
			var too_close := false
			for c in castles:
				if HexGrid.distance(c, i) < 3:
					too_close = true
					break
			if too_close:
				continue
			castles.append(i)
			tiles[i].castle = true
		if castles.size() < int(rules.neutral_castles):
			continue
		var bal := 0
		for c in castles:
			bal += HexGrid.distance(c, homes[0]) - HexGrid.distance(c, homes[1])
		if absi(bal) > 2:
			continue
		_place(tiles, "mountain", int(rules.mountains))
		_place(tiles, "water", int(rules.waters))
		if not _place_gold(tiles, homes):
			continue
		if not place_crates(tiles, homes, int(rules.get("crates", 0))):
			continue
		_place_forests(tiles, int(rules.forests))
		_place_ferns(tiles, int(rules.ferns))
		var reach := _bfs(homes[0], tiles)
		var connected := true
		for t in tiles:
			if t.terrain == "plain" and reach[t.id] == INF:
				connected = false
				break
		if connected:
			return tiles
	push_error("Map generation failed after 2000 tries")
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
		if not place_crates(tiles, homes, int(b.get("crates", 0))):
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
	return out if out.size() >= 3 * k else []


static func new_tile(i: int) -> Dictionary:
	return {
		"id": i,
		"terrain": "void" if HexGrid.is_void(i) else "plain",
		"owner": -1,
		"castle": false,
		"market": 0,
		"fort": 0,
		"barracks": 0,
		"bk": 0,
		"bounty": false,
		"crate": false,   # a material hex (2026-11-17)
		"forest": false,
		"fern": false,
		"walls": [0, 0, 0, 0, 0, 0],
	}


static func _blank_tiles() -> Array:
	var tiles: Array = []
	for i in HexGrid.SIZE * HexGrid.SIZE:
		tiles.append(new_tile(i))
	return tiles


## Turns random plain hexes into the given terrain, avoiding castles.
static func _place(tiles: Array, kind: String, count: int) -> void:
	var placed := 0
	var tries := 0
	while placed < count and tries < 2000:
		tries += 1
		var t: Dictionary = tiles[randi() % (HexGrid.SIZE * HexGrid.SIZE)]
		if t.castle or t.terrain != "plain":
			continue
		t.terrain = kind
		placed += 1


## Marks a balanced set of plain hexes as one-time gold hexes (a third of the open land, or "count" of them):
## as far from every home castle in total, and as many closest to each one.
## Material hexes (Ethan, 2026-11-17): "count" open hexes that aren't gold hexes, as fair to every home castle as the gold.
static func place_crates(tiles: Array, homes: Array, count: int) -> bool:
	if count <= 0:
		return true
	var pool: Array = tiles.filter(func(t): return t.terrain == "plain" and not t.castle and not t.bounty and not t.forest and int(t.market) == 0 and int(t.fort) == 0 and int(t.barracks) == 0)
	for attempt in range(600):
		var pick: Array = pool.duplicate()
		pick.shuffle()
		pick = pick.slice(0, count)
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
		if sums.max() - sums.min() <= (2 if homes.size() > 2 else 1) and near.max() == near.min():
			for t in pick:
				t.crate = true
			return true
	return false


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
		if sums.max() - sums.min() <= (2 if homes.size() > 2 else 1) and near.max() == near.min():
			for t in pick:
				t.bounty = true
			return true
	return false


static func _place_forests(tiles: Array, count: int) -> void:
	var pool: Array = tiles.filter(func(t): return t.terrain == "plain" and not t.castle and not t.bounty and not t.get("crate", false) and t.market == 0 and t.fort == 0 and t.barracks == 0)
	pool.shuffle()
	for t in pool.slice(0, count):
		t.forest = true


static func _place_ferns(tiles: Array, count: int) -> void:
	var pool: Array = tiles.filter(func(t): return t.terrain == "plain" and not t.castle and not t.bounty and not t.forest and t.market == 0 and t.fort == 0 and t.barracks == 0)
	pool.shuffle()
	for t in pool.slice(0, count):
		t.fern = true


## Distance from a starting hex over plain land only. Hexes not reached are INF.
static func _bfs(start: int, tiles: Array) -> Array:
	var dist: Array = []
	dist.resize(HexGrid.SIZE * HexGrid.SIZE)
	dist.fill(INF)
	dist[start] = 0
	var queue: Array[int] = [start]
	while not queue.is_empty():
		var c: int = queue.pop_front()
		for n in HexGrid.neighbors(c):
			if tiles[n].terrain == "plain" and dist[n] == INF:
				dist[n] = dist[c] + 1
				queue.append(n)
	return dist

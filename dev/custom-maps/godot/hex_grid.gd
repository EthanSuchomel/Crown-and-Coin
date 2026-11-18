class_name HexGrid
extends RefCounted
## Hex math for the board. Hexes are numbered row * SIZE + column, matching the browser version.
## Ported from its rc, cube, man and nbrDirs helpers. 2 players: 8 x 8 (52 hexes). 3 players: 11 x 11 (79 hexes);
## use_board() switches (the browser's useBoard).

static var SIZE: int = 8
static var players_n: int = 0
static var _void: Dictionary = {}
static var custom: bool = false   # a hand-made map's shape is in use
static var shape_id: int = 0      # changes whenever the board's shape does (the board view frames it again)


## Sets the board for a 2- or 3-player game.
static func use_board(np: int) -> void:
	np = 3 if np == 3 else 2
	if players_n == np and not custom:
		return
	players_n = np
	custom = false
	shape_id += 1
	var b: Dictionary = board_rules(np)
	SIZE = int(b.size)
	_void = {}
	for v in (b.voids if b.has("voids") else b.void_corners):
		_void[int(v[0]) * SIZE + int(v[1])] = true


## A hand-made map's shape: its size and the hexes that are off the board.
static func use_shape(np: int, size: int, voids: Array) -> void:
	players_n = 3 if np == 3 else 2
	SIZE = size
	_void = {}
	for i in voids:
		_void[int(i)] = true
	custom = true
	shape_id += 1


## The board's settings: rules.json "board" (2 players) or "board3".
static func board_rules(np: int) -> Dictionary:
	return GameData.rules.board3 if np == 3 else GameData.rules.board


static func cell_count() -> int:
	if players_n == 0:
		use_board(2)
	return SIZE * SIZE


static func index_of(row: int, col: int) -> int:
	return row * SIZE + col


static func rc(i: int) -> Vector2i:
	return Vector2i(i / SIZE, i % SIZE)


static func is_void(i: int) -> bool:
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
	return -1 if (r < 0 or r >= SIZE or c < 0 or c >= SIZE) else r * SIZE + c


## All six neighbour slots in edge order: lower-right, below, lower-left, upper-left,
## above, upper-right. Off-board slots are -1, so a slot's position is its edge number (used by walls).
static func neighbor_dirs(i: int) -> Array[int]:
	var v := rc(i)
	var dirs: Array
	if (v.y & 1) == 1:
		dirs = [[1, 1], [1, 0], [1, -1], [0, -1], [-1, 0], [0, 1]]
	else:
		dirs = [[0, 1], [1, 0], [0, -1], [-1, -1], [-1, 0], [-1, 1]]
	var out: Array[int] = []
	for d in dirs:
		var r: int = v.x + d[0]
		var c: int = v.y + d[1]
		out.append(index_of(r, c) if r >= 0 and r < SIZE and c >= 0 and c < SIZE else -1)
	return out


## The six neighbours of a hex, in edge order: lower-right, below, lower-left,
## upper-left, above, upper-right. Off-board neighbours are left out.
static func neighbors(i: int) -> Array[int]:
	var v := rc(i)
	var odd := v.y & 1
	var dirs: Array
	if odd == 1:
		dirs = [[1, 1], [1, 0], [1, -1], [0, -1], [-1, 0], [0, 1]]
	else:
		dirs = [[0, 1], [1, 0], [0, -1], [-1, -1], [-1, 0], [-1, 1]]
	var out: Array[int] = []
	for d in dirs:
		var r: int = v.x + d[0]
		var c: int = v.y + d[1]
		if r >= 0 and r < SIZE and c >= 0 and c < SIZE:
			out.append(index_of(r, c))
	return out


## Cube coordinates (x, y, z) with x + y + z = 0.
static func cube(i: int) -> Vector3i:
	var v := rc(i)
	var x := v.y
	var z := v.x - (v.y - (v.y & 1)) / 2
	var y := -x - z
	return Vector3i(x, y, z)


## Number of steps between two hexes.
static func distance(a: int, b: int) -> int:
	var p := cube(a)
	var q := cube(b)
	return maxi(absi(p.x - q.x), maxi(absi(p.y - q.y), absi(p.z - q.z)))

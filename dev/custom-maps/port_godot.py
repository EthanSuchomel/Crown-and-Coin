import json
M='/mnt/user-data/outputs/godot/m/'; U='/mnt/user-data/uploads/CrownAndCoin-Godot/'; O='/mnt/user-data/outputs/godot/maps/'
def ed(src, pairs, out):
    s=open(src).read()
    for a,b,n in pairs:
        assert s.count(a)==n,(src,s.count(a),a[:80]); s=s.replace(a,b)
    open(O+out,'w').write(s)
maps=json.load(open('/home/claude/crown-and-coin/dev/custom-maps/maps.json'))
json.dump({"_note":"Ethan's hand-made maps (Map Maker, 2026-11-17). rows: x off the board, g grass, f forest, m mountain, w water, c neutral castle, 1-3 home castles (1 is you); coins and mats are [row, col].","maps":maps}, open(O+'maps.json','w'), indent=1)
ed(U+'scripts/rules/game_data.gd',[
 ('var rules: Dictionary = {}\n','var rules: Dictionary = {}\nvar maps: Array = []   # hand-made maps (data/maps.json)\n',1),
 ('\trules = _load_json("res://data/rules.json")\n','\trules = _load_json("res://data/rules.json")\n\tif FileAccess.file_exists("res://data/maps.json"):\n\t\tmaps = _load_json("res://data/maps.json").get("maps", [])\n',1),
 ('\nfunc _load_json(','''
## A hand-made map by its id, or an empty Dictionary.
func map_by_id(id: String) -> Dictionary:
	for m in maps:
		if String(m.id) == id:
			return m
	return {}


## The hand-made maps for this many players.
func maps_for(np: int) -> Array:
	return maps.filter(func(m): return int(m.players) == np)


func _load_json(''',1)],'game_data.gd')
ed(U+'scripts/rules/hex_grid.gd',[
 ('static var _void: Dictionary = {}\n','static var _void: Dictionary = {}\nstatic var custom: bool = false   # a hand-made map\'s shape is in use\nstatic var shape_id: int = 0      # changes whenever the board\'s shape does (the board view frames it again)\n',1),
 ('\tif players_n == np:\n\t\treturn\n\tplayers_n = np\n','\tif players_n == np and not custom:\n\t\treturn\n\tplayers_n = np\n\tcustom = false\n\tshape_id += 1\n',1),
 ('\n## The board\'s settings:','''
## A hand-made map's shape: its size and the hexes that are off the board.
static func use_shape(np: int, size: int, voids: Array) -> void:
	players_n = 3 if np == 3 else 2
	SIZE = size
	_void = {}
	for i in voids:
		_void[int(i)] = true
	custom = true
	shape_id += 1


## The board's settings:''',1)],'hex_grid.gd')
ed(M+'board_gen.gd',[
 ('static func new_tile(i: int) -> Dictionary:','''## A hand-made map (Ethan, 2026-11-17): sets the board's shape, then returns {tiles, homes}.
static func from_map(m: Dictionary) -> Dictionary:
	var rows: Array = m.rows
	var n: int = rows.size()
	var voids: Array = []
	for r in n:
		for c in n:
			if String(rows[r])[c] == "x":
				voids.append(r * n + c)
	HexGrid.use_shape(int(m.players), n, voids)
	var tiles := _blank_tiles()
	var homes: Array[int] = []
	homes.resize(int(m.players))
	for r in n:
		for c in n:
			var ch: String = String(rows[r])[c]
			var t: Dictionary = tiles[r * n + c]
			match ch:
				"m": t.terrain = "mountain"
				"w": t.terrain = "water"
				"f": t.forest = true
				"c": t.castle = true
				"1", "2", "3":
					t.castle = true
					t.owner = int(ch) - 1
					homes[int(ch) - 1] = r * n + c
	for rcv in m.get("coins", []):
		var t2: Dictionary = tiles[int(rcv[0]) * n + int(rcv[1])]
		if t2.terrain == "plain" and not t2.castle and not t2.forest:
			t2.bounty = true
	for rcv in m.get("mats", []):
		var t3: Dictionary = tiles[int(rcv[0]) * n + int(rcv[1])]
		if t3.terrain == "plain" and not t3.castle and not t3.forest and not t3.bounty:
			t3.crate = true
	return {"tiles": tiles, "homes": homes}


static func new_tile(i: int) -> Dictionary:''',1)],'board_gen.gd')
ed(M+'game_state.gd',[
 ('func new_game(your_faction: String = "dinos", board: Array = [], opponent: String = "", np: int = 2, opps: Array = []) -> void:\n\tnp = 3 if np == 3 else 2\n',
  'func new_game(your_faction: String = "dinos", board: Array = [], opponent: String = "", np: int = 2, opps: Array = [], map: String = "") -> void:\n\tnp = 3 if np == 3 else 2\n\tvar cmap: Dictionary = GameData.map_by_id(map) if map != "" else {}\n\tif not cmap.is_empty() and int(cmap.players) != np:\n\t\tcmap = {}\n\tmap_id = String(cmap.get("id", ""))\n',1),
 ('\tHexGrid.use_board(np)\n\ttiles = board if not board.is_empty() else BoardGen.generate(np)\n\tfor t in tiles:\n\t\t_init_tile(t)\n\thomes = BoardGen.homes_for(np)\n',
  '\tHexGrid.use_board(np)\n\tvar built: Dictionary = BoardGen.from_map(cmap) if not cmap.is_empty() else {}\n\ttiles = built.tiles if not built.is_empty() else (board if not board.is_empty() else BoardGen.generate(np))\n\tfor t in tiles:\n\t\t_init_tile(t)\n\thomes = built.homes if not built.is_empty() else BoardGen.homes_for(np)\n',1),
 ('const SAVED := ["players", "tiles", "homes",','const SAVED := ["map_id", "players", "tiles", "homes",',1),
 ('\tHexGrid.use_board(players.size())\n\tfor p in players:','''	HexGrid.use_board(players.size())
	if map_id != "":   # a game on a hand-made map keeps its shape
		var voids: Array = []
		for t in tiles:
			if t.terrain == "void":
				voids.append(int(t.id))
		HexGrid.use_shape(players.size(), int(round(sqrt(tiles.size()))), voids)
	for p in players:''',1),
 ('\tc.homes = homes.duplicate()\n','\tc.homes = homes.duplicate()\n\tc.map_id = map_id\n',1),
 ('var homes: Array[int] = []\n','var homes: Array[int] = []\nvar map_id: String = ""   # a hand-made map\'s id ("" for a random map)\n',1)],'game_state.gd')
ed(M+'board_view.gd',[
 ('\tif _frame_n == N:\n\t\treturn _frame\n\t_frame_n = N\n\tif N == 8:','\tif _frame_n == HexGrid.shape_id:\n\t\treturn _frame\n\t_frame_n = HexGrid.shape_id\n\tif N == 8 and not HexGrid.custom:',1)],'board_view.gd')
ed(M+'main.gd',[
 ('var pref_np: int = 2        # 2 or 3 players (remembered)\n','var pref_np: int = 2        # 2 or 3 players (remembered)\nvar pref_map: String = ""   # a hand-made map\'s id, "" for a random map (remembered)\n',1),
 ('\t\tpref_np = 3 if int(cfg.get_value("player", "players", 2)) == 3 else 2\n','\t\tpref_np = 3 if int(cfg.get_value("player", "players", 2)) == 3 else 2\n\t\tpref_map = String(cfg.get_value("player", "map", ""))\n',1),
 ('\tht.move_child(np_row, vs.get_index())   # Players above who you face\n','''	ht.move_child(np_row, vs.get_index())   # Players above who you face
	var maps_here: Array = GameData.maps_for(pref_np)
	if not maps_here.is_empty():   # Random, or one of Ethan's hand-made maps (2026-11-17)
		var map_row := HFlowContainer.new()
		map_row.add_theme_constant_override("h_separation", 6)
		map_row.add_theme_constant_override("v_separation", 6)
		ht.add_child(map_row)
		ht.move_child(map_row, vs.get_index())
		map_row.add_child(_label("Map", 15, LICHEN, true))
		var sel: String = pref_map if maps_here.any(func(m): return String(m.id) == pref_map) else ""
		for entry in [{"id": "", "name": "Random"}] + maps_here:
			var mid: String = String(entry.id)
			var mb := _button(String(entry.name), func():
				pref_map = mid
				var cfg := ConfigFile.new()
				cfg.load(SETTINGS)
				cfg.set_value("player", "map", mid)
				cfg.save(SETTINGS)
				show_factions(), mid == sel)
			mb.add_theme_font_size_override("font_size", 14)
			map_row.add_child(mb)
''',1),
 ('\t\tg.new_game(fid, [], _opponent_for(fid), pref_np, pref_opps)\n','\t\tg.new_game(fid, [], _opponent_for(fid), pref_np, pref_opps, pref_map)\n',1)],'main.gd')
print('ok')

import json
S='/mnt/user-data/outputs/godot/maps/'; A='/mnt/user-data/outputs/godot/m/ai_player.gd'; O='/mnt/user-data/outputs/godot/wins/'
import os; os.makedirs(O, exist_ok=True)
def ed(src, pairs, out):
    s=open(src).read()
    for a,b,n in pairs:
        assert s.count(a)==n,(src,s.count(a),a[:80]); s=s.replace(a,b)
    open(O+out,'w').write(s)
maps=json.load(open('/home/claude/crown-and-coin/dev/custom-maps/maps.json'))
json.dump({"_note":"Ethan's hand-made maps (Map Maker, 2026-11-17). rows: x off the board, g grass, f forest, m mountain, w water, c neutral castle, 1-4 home castles (1 is you); coins and mats are [row, col]. castles: castles to hold to win (0 = no castle win; absent = the usual: 4 with 2 players, none with 3). events: a castle at [row, col] in a round. 4-player maps wait for a 4-player mode.","maps":maps}, open(O+'maps.json','w'), indent=1)
ed(S+'game_state.gd',[
 ('func _end_game(winner: int, why: String) -> void:','''## Castles to hold to win: the map's own number, or the usual (rules.json, 2 players; none with 3). 0 = no castle win.
func win_castles() -> int:
	var m: Dictionary = GameData.map_by_id(map_id) if map_id != "" else {}
	if not m.is_empty() and m.has("castles"):
		return int(m.castles)
	return 0 if players.size() > 2 else int(GameData.rules.castles.to_win)


## A hand-made map's events at the start of a round (e.g. Control: a castle on the centre hex in round 20).
func _map_events() -> void:
	var m: Dictionary = GameData.map_by_id(map_id) if map_id != "" else {}
	for e in m.get("events", []):
		if int(e.get("round", -1)) != turn or not e.has("castle"):
			continue
		var i: int = int(e.castle[0]) * HexGrid.SIZE + int(e.castle[1])
		if i < 0 or i >= tiles.size():
			continue
		var t: Dictionary = tiles[i]
		if t.castle or t.terrain == "void":
			continue
		t.terrain = "plain"
		t.forest = false
		t.castle = true
		if int(t.owner) < 0:
			t.bounty = false
			t.crate = false
		add_log("Round %d: a new castle rises at the centre of the map." % turn)


func _end_game(winner: int, why: String) -> void:''',1),
 ('''	if players.size() > 2:   # 3 players: no castle-count win; a side with no land left is out
		for q in players:
			if bool(q.get("out", false)) or over >= 0:
				continue
			if not tiles.any(func(t): return int(t.owner) == int(q.id)):
				knock_out(int(q.id), -1, "wipe")
		return
	for pid in [0, 1]:''','''	var to_win: int = win_castles()
	if players.size() > 2:   # 3 players: a side with no land left is out (a castle win only on maps that have one)
		for q in players:
			if bool(q.get("out", false)) or over >= 0:
				continue
			if not tiles.any(func(t): return int(t.owner) == int(q.id)):
				knock_out(int(q.id), -1, "wipe")
		if over >= 0 or to_win <= 0:
			return
	else:
	  for pid in [0, 1]:''',1),
 ('''	var to_win: int = int(GameData.rules.castles.to_win)
	var holder: int = -1
	for pid in [0, 1]:
		if castle_count(pid) >= to_win:
			holder = pid''','''	var holder: int = -1
	for q2 in players:
		if not bool(q2.get("out", false)) and castle_count(int(q2.id)) >= to_win:
			holder = int(q2.id)
			break''',1),
 ('''	if holder >= 0 and siege.is_empty():
		siege = {"pid": holder, "left": int(GameData.rules.castles.hold_turns)}
		add_log("%s hold %d castles! %s have %d turns to take one back." % [players[holder].name, to_win, players[1 - holder].name, int(GameData.rules.castles.hold_turns)])''','''	if holder >= 0 and siege.is_empty():
		var rivals: int = players.filter(func(q3): return int(q3.id) != holder and not bool(q3.get("out", false))).size()
		siege = {"pid": holder, "left": int(GameData.rules.castles.hold_turns) * rivals}   # every rival gets its turns to take one back
		add_log("%s hold %d castles! %s %d turns%s to take one back." % [players[holder].name, to_win, ("%s have" % players[1 - holder].name) if players.size() == 2 else "Their rivals have", int(GameData.rules.castles.hold_turns), "" if rivals < 2 else " each"])''',1),
 ('add_log("%s held %d castles and win!" % [players[int(siege.pid)].name, int(GameData.rules.castles.to_win)])','add_log("%s held %d castles and win!" % [players[int(siege.pid)].name, win_castles()])',1),
 ('holding %d castles, or wiping them off the map." % int(GameData.rules.castles.to_win))','holding %d castles, or wiping them off the map." % win_castles())',1),
 ('''		if turn == int(GameData.rules.castles.new_neutral_after_round) + 1 and extra_castle < 0:
			_spawn_castle()
''','''		if turn == int(GameData.rules.castles.new_neutral_after_round) + 1 and extra_castle < 0:
			_spawn_castle()
		_map_events()
''',1)],'game_state.gd')
ed(A,[
 ('''	var to_win: int = int(GameData.rules.castles.to_win)
	if castle_v < 10000.0''','''	var to_win: int = g.win_castles()
	if castle_v < 10000.0''',1),
 ('elif b.castle and g.players.size() == 2 and g.castle_count(pid) + 1 >= to_win:','elif b.castle and to_win > 0 and g.castle_count(pid) + 1 >= to_win:',1),
 ('''	var to_win: int = int(GameData.rules.castles.to_win)
	var V: float = 0.0''','''	var to_win: int = g.win_castles()
	var V: float = 0.0''',1),
 ('(250.0 if np == 2 and ca[i] >= to_win else 0.0)','(250.0 if to_win > 0 and ca[i] >= to_win else 0.0)',1)],'ai_player.gd')
ed(S+'main.gd',[
 ('var of: String = "" if g.players.size() > 2 else " [color=#a5b49e][font_size=11]of %d[/font_size][/color]" % int(GameData.rules.castles.to_win)','var of: String = "" if g.win_castles() <= 0 else " [color=#a5b49e][font_size=11]of %d[/font_size][/color]" % g.win_castles()',1),
 ('''	var to_win: int = int(GameData.rules.castles.to_win)
	for spec in [["Full"''','''	var to_win: int = g.win_castles()
	for spec in [["Full"''',1),
 ('("You hold %d castles! Keep them for %d more enemy turns to win." if mine else "The enemy holds %d castles! Take one back within %d turns.")','("You hold %d castles! Keep them for %d more enemy turns to win." if mine else ("The %s hold %%d castles! Take one back within %%d turns." % String(g.players[int(g.siege.pid)].name)))',1),
 ('"hold": "by holding %d castles" % int(GameData.rules.castles.to_win)','"hold": "by holding %d castles" % g.win_castles()',1),
 ('''		txt = "You're the last side standing. " + " ".join(parts)''','''		txt = ("You held %d castles and no rival took one back." % g.win_castles()) if g.over_why == "hold" else ("You're the last side standing. " + " ".join(parts))''',1),
 ('''		txt += " in round %d." % int(me.get("out_round", g.turn))''','''		txt += " in round %d." % int(me.get("out_round", g.turn))
		if g.over_why == "hold" and not g.is_out(0):
			txt = "The %s held %d castles and no one took one back in time." % [g.players[g.over].name, g.win_castles()]''',1)],'main.gd')
print('ok')

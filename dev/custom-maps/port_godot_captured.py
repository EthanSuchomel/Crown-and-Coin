O='/mnt/user-data/outputs/godot/cap/'
def ed(src, pairs, out):
    s=open(src).read()
    for a,b,n in pairs:
        assert s.count(a)==n,(src,s.count(a),a[:80]); s=s.replace(a,b)
    open(O+out,'w').write(s)
ed('/mnt/user-data/outputs/godot/myth/game_state.gd',[
 ('## A hand-made map\'s events at the start of a round','''## Does the home castle count toward the castle win? Not on a hand-made map with its own number (Ethan, 2026-11-17:
## "it needs to be x amount of captured castles to win"); random maps keep the usual count, home included.
func home_counts() -> bool:
	var m: Dictionary = GameData.map_by_id(map_id) if map_id != "" else {}
	return m.is_empty() or not m.has("castles")


## Castles toward the win: every castle the side holds, less its own home castle where that doesn't count.
func win_count(pid: int) -> int:
	var n: int = castle_count(pid)
	if not home_counts() and pid < homes.size() and int(tiles[homes[pid]].owner) == pid:
		n -= 1
	return n


## A hand-made map's events at the start of a round''',1),
 ('if not bool(q2.get("out", false)) and castle_count(int(q2.id)) >= to_win:','if not bool(q2.get("out", false)) and win_count(int(q2.id)) >= to_win:',1),
 ('add_log("%s hold %d castles! %s %d turns%s to take one back." % [players[holder].name, to_win,','add_log("%s hold %d %scastles! %s %d turns%s to take one back." % [players[holder].name, to_win, "" if home_counts() else "captured ",',1)],'game_state.gd')
ed('/mnt/user-data/outputs/godot/wins/ai_player.gd',[
 ('elif b.castle and to_win > 0 and g.castle_count(pid) + 1 >= to_win:','elif b.castle and to_win > 0 and g.win_count(pid) + 1 >= to_win:',1),
 ('(250.0 if to_win > 0 and ca[i] >= to_win else 0.0)','(250.0 if to_win > 0 and ca[i] - (0 if g.home_counts() or int(g.tiles[g.homes[i]].owner) != i else 1) >= to_win else 0.0)',1)],'ai_player.gd')
ed('/mnt/user-data/outputs/godot/minion/main.gd',[
 ('_ink(int(q.id)), g.castle_count(int(q.id))])','_ink(int(q.id)), g.win_count(int(q.id)) if (g.win_castles() > 0 and not g.home_counts()) else g.castle_count(int(q.id))])',1),
 ('("You hold %d castles! Keep them for %d more enemy turns to win." if mine else ("The %s hold %%d castles! Take one back within %%d turns." % String(g.players[int(g.siege.pid)].name)))','("You hold %d " + ("" if g.home_counts() else "captured ") + "castles! Keep them for %d more enemy turns to win." if mine else ("The %s hold %%d " % String(g.players[int(g.siege.pid)].name)) + ("" if g.home_counts() else "captured ") + "castles! Take one back within %d turns.")',1),
 ('"[b]On this map you can also win by holding %d castles:[/b]','"[b]On this map you can also win by holding %d captured castles[/b] (your home doesn\'t count):',1),
 ('2. Hold %d castles for %d enemy turns.','2. Hold %d " + ("castles" if g == null or g.home_counts() else "captured castles (not counting your home)") + " for %d enemy turns.',1)],'main.gd')
print('ok')

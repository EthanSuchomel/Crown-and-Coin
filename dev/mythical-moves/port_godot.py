import os
W='/mnt/user-data/outputs/godot/wins/'; O='/mnt/user-data/outputs/godot/myth/'; os.makedirs(O, exist_ok=True)
def ed(src, pairs, out):
    s=open(src).read()
    for a,b,n in pairs:
        assert s.count(a)==n,(src,s.count(a),a[:80]); s=s.replace(a,b)
    open(O+out,'w').write(s)
MOVE_TXT='Make up to %d moves. Mages go 1 hex. Minions go up to 2 hexes but only onto your own land: they can\'t take land, so new land needs another unit with them, and only Mages take castles. Other units go 1 hex into new land or an attack, or 2 through your own land. Only flyers can attack a Floating Castle'
ed(W+'game_state.gd',[
 ('''## Mages and Minions move 2 hexes anywhere.
func fast_unit(k: String) -> bool:
	return k == "minion" or is_mage(k)''','''## Minions move 2 hexes (onto your own land only); Mages 1 (Ethan, 2026-11-17).
func fast_unit(k: String) -> bool:
	return k == "minion"


## What a Mythical move into hex b needs (Ethan, 2026-11-17): "mage" for a castle (not an enemy Floating Castle, which only
## flyers can attack), "land" (any unit but a Minion) for other land, "" on your own land or for the other factions.
func myth_need(pid: int, b: Dictionary) -> String:
	if not is_myth(pid) or int(b.owner) == pid:
		return ""
	if b.castle:
		return "" if (int(b.owner) >= 0 and is_floating(b)) else "mage"
	return "land"


func myth_has(need: String, army: Dictionary) -> bool:
	if need == "":
		return true
	for k in army:
		if int(army[k]) > 0 and (is_mage(k) if need == "mage" else k != "minion"):
			return true
	return false''',1),
 ('''	if air and far:
		return func(_k): return false
	if air:
		return func(k): return bool(GameData.units[k].get("air", false))
	if far:
		return func(k): return fast_unit(k)
	return Callable()''','''	if air and far:
		return func(_k): return false
	var no_mage: bool = is_myth(pid) and HexGrid.distance(from, to) > 1   # Mages go 1 hex a move
	if air:
		if no_mage:
			return func(k): return bool(GameData.units[k].get("air", false)) and not is_mage(k)
		return func(k): return bool(GameData.units[k].get("air", false))
	if far:
		return func(k): return fast_unit(k)
	if no_mage:
		return func(k): return not is_mage(k)
	return Callable()''',1),
 ('''		return "The Floating Castle can only be attacked by flyers."
	return "Only Mages and Minions can go this far in one move."''','''		return "The Floating Castle can only be attacked by flyers."
	if is_myth(int(tiles[from].owner)) and not _move_targets_core(from, cur_lvl(), false).has(to):
		return "Only Minions can go this far in one move, and only onto your own land."
	return "Mages move 1 hex at a time, so they stay behind."''',1),
 ('''	var cand: Array[int] = _move_targets_core(from, lvl, far)
''','''	var cand: Array[int] = _move_targets_core(from, lvl, far)
	var near: Array[int] = []
	if far:
		near = _move_targets_core(from, lvl, false)
''',1),
 ('''		if co and not (int(tiles[i].owner) >= 0 and int(tiles[i].owner) != pid):
			continue   # Charge: the extra move is an attack
		var f: Callable = move_filter(from, i, lvl)
		if not f.is_valid():
			out.append(i)
			continue
		for k in t.ready:
			if int(t.ready[k]) > 0 and f.call(k):
				out.append(i)
				break''','''		if co and not (int(tiles[i].owner) >= 0 and int(tiles[i].owner) != pid):
			continue   # Charge: the extra move is an attack
		if far and not near.has(i) and int(tiles[i].owner) != pid:
			continue   # Minions' long moves: only onto your own land
		var f: Callable = move_filter(from, i, lvl)
		var can: Dictionary = {}
		for k in t.ready:
			if int(t.ready[k]) > 0 and (not f.is_valid() or f.call(k)):
				can[k] = int(t.ready[k])
		if not can.is_empty() and myth_has(myth_need(pid, tiles[i]), can):   # Mythical: a castle needs a Mage, new land a non-Minion
			out.append(i)''',1),
 ('''	var A: Dictionary = tiles[from]
	var B: Dictionary = tiles[to]
	if is_myth(int(A.owner)):
		var room: int''','''	var A: Dictionary = tiles[from]
	var B: Dictionary = tiles[to]
	var need: String = myth_need(int(A.owner), B)
	if need != "" and not myth_has(need, out):   # a Mythical group that lacks what it needs takes one along
		for k in _by_strength(A.ready):
			if int(A.ready[k]) > int(out.get(k, 0)) and (not f.is_valid() or f.call(k)) and (is_mage(k) if need == "mage" else k != "minion"):
				out[k] = int(out.get(k, 0)) + 1
				break
	if is_myth(int(A.owner)):
		var room: int''',1),
 ('''	sel = _move_sel(from, to, sel, lvl)
	if CombatRules.count(sel) == 0:''','''	sel = _move_sel(from, to, sel, lvl)
	if CombatRules.count(sel) == 0 or not myth_has(myth_need(pid, B), sel):''',1)],'game_state.gd')
ed(W+'main.gd',[
 ('"Mages and Minions move 2 hexes anywhere, and a Move action has 3 moves."]:','"A Move action has 3 moves. Mages move 1 hex; Minions move 2 but only onto your own land.",\n\t\t\t\t"Only Mages capture castles. Minions can\'t take land on their own; every other unit can."]:',1),
 ('return "Make up to %d moves. Mages and Minions go up to 2 hexes anywhere; other units 1 hex into new land or an attack, or 2 through your own land. Only flyers can attack a Floating Castle" % g.moves_limit(pid)','return "'+MOVE_TXT+'" % g.moves_limit(pid)',1),
 ('Mages and Minions go up to 2 hexes anywhere; other units 1 into new land or an attack, or 2 through your own land. Only flyers can attack a Floating Castle. Each send uses one move.")','Mages go 1 hex; Minions up to 2 but only onto your own land (they can\'t take land), and only Mages take castles. Other units go 1 into new land or an attack, or 2 through your own land. Only flyers can attack a Floating Castle. Each send uses one move.")',1),
 ('''	if mf.is_valid():
		text += "\\n" + g.move_filter_note(from, to)
''','''	if mf.is_valid():
		text += "\\n" + g.move_filter_note(from, to)
	var mneed: String = g.myth_need(int(g.tiles[from].owner), b)
	if mneed != "":
		text += "\\n[b]Only Mages can take a castle:[/b] if you don't pick a Mage, one goes with them." if mneed == "mage" else "\\n[b]Minions can't take land:[/b] if you only pick Minions, one other unit goes with them."
''',1)],'main.gd')
print('ok')

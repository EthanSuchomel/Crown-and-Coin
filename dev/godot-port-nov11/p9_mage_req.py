# Ethan, 2026-11-11: raising the Mages also needs Life Trees and captured castles (checked when you raise the level;
# losing a castle later keeps it). Level 1: 1 tree. Level 2: 3 trees and 1 captured castle. Level 3: 5 trees and 2 captured castles.
import sys, json
W = sys.argv[1]
def patch(f, pairs):
    s = open(W + f, encoding='utf-8').read()
    for old, new in pairs:
        if s.count(old) != 1: print('COUNT', s.count(old), f, old[:100]); sys.exit(1)
        s = s.replace(old, new)
    open(W + f, 'w', encoding='utf-8').write(s)
r = json.load(open(W + '/data/rules.json', encoding='utf-8'))
r['mythical']['mage_req'] = [{'trees': 1, 'castles': 0}, {'trees': 3, 'castles': 1}, {'trees': 5, 'castles': 2}]
r['mythical']['_mage_req_note'] = "Ethan, 2026-11-11: each Mage level also needs Life Trees and captured castles (castles you hold other than your home) when you raise it; a castle lost later doesn't take the level away."
open(W + '/data/rules.json', 'w', encoding='utf-8').write(json.dumps(r, indent='\t', ensure_ascii=False) + '\n')
patch('/scripts/rules/game_state.gd', [('''func myth_up_mages(pid: int) -> bool:
	var p: Dictionary = players[pid]
	var l: int = mlv_of(pid)
	if l >= 3 or myth_home(pid).is_empty() or int(p.gold) < int(myth().mage_up[l]):
		return false''', '''func trees_of(pid: int) -> int:
	var n: int = 0
	for t in tiles:
		if int(t.owner) == pid and int(t.get("tree", 0)) > 0:
			n += 1
	return n


## Castles held other than your own home castle.
func cap_castles_of(pid: int) -> int:
	var n: int = 0
	for t in tiles:
		if t.castle and int(t.owner) == pid and int(t.id) != homes[pid]:
			n += 1
	return n


## Mage level l+1 also needs Life Trees and captured castles (Ethan, 2026-11-11).
func mage_req_ok(pid: int, l: int) -> bool:
	if l >= 3:
		return false
	var q: Dictionary = myth().mage_req[l]
	return trees_of(pid) >= int(q.trees) and cap_castles_of(pid) >= int(q.castles)


func mage_req_txt(l: int) -> String:
	var q: Dictionary = myth().mage_req[l]
	var t: String = "%d Life Tree%s" % [int(q.trees), "s" if int(q.trees) > 1 else ""]
	if int(q.castles) > 0:
		t += " and %d captured castle%s" % [int(q.castles), "s" if int(q.castles) > 1 else ""]
	return t


func mage_req_all() -> String:
	var parts: PackedStringArray = []
	for l in 3:
		parts.append("level %d: %s" % [l + 1, mage_req_txt(l)])
	return "; ".join(parts)


func myth_up_mages(pid: int) -> bool:
	var p: Dictionary = players[pid]
	var l: int = mlv_of(pid)
	if l >= 3 or myth_home(pid).is_empty() or int(p.gold) < int(myth().mage_up[l]) or not mage_req_ok(pid, l):
		return false''')])
patch('/scripts/rules/ai_player.gd', [('''int(M.castle_up[g.clv_of(pid)]) if g.clv_of(pid) < 3 else int(M.mage_up[mini(2, g.mlv_of(pid))]))''',
 '''int(M.castle_up[g.clv_of(pid)]) if g.clv_of(pid) < 3 else (int(M.mage_up[mini(2, g.mlv_of(pid))]) if g.mage_req_ok(pid, g.mlv_of(pid)) else 0))''')])
patch('/scripts/ui/main.gd', [
 ('''			return "Upgrade your Mages (%s magic for levels 1 to 3) or the Floating Castle (%s magic), or raise a magic dome where a Mage stands (%d magic, then %d a turn)" % [joined.call(M.mage_up), joined.call(M.castle_up),''',
  '''			return "Upgrade your Mages (%s magic for levels 1 to 3; %s) or the Floating Castle (%s magic), or raise a magic dome where a Mage stands (%d magic, then %d a turn)" % [joined.call(M.mage_up), g.mage_req_all(), joined.call(M.castle_up),'''),
 ('''		_hint(box, "▸ Tap any of your hexes to upgrade your Mages (%s magic) or the Floating Castle (%s magic), or to raise a magic dome where a Mage stands: %d magic, then %d every turn (if you can't pay, it fades). A dome guards every side like a full wall." % [", ".join(PackedStringArray(M.mage_up.map(func(v): return str(int(v))))), ''',
  '''		_hint(box, "▸ Tap any of your hexes to upgrade your Mages (%s magic; %s) or the Floating Castle (%s magic), or to raise a magic dome where a Mage stands: %d magic, then %d every turn (if you can't pay, it fades). A dome guards every side like a full wall." % [", ".join(PackedStringArray(M.mage_up.map(func(v): return str(int(v))))), g.mage_req_all(), '''),
 ('''		if (g.mlv_of(0) < 3 and magic >= int(M.mage_up[g.mlv_of(0)])) or''', '''		if (g.mlv_of(0) < 3 and magic >= int(M.mage_up[g.mlv_of(0)]) and g.mage_req_ok(0, g.mlv_of(0))) or'''),
 ('''		items.append(["res://art/units/mage0.png", "Mages 3" if ml2 >= 3 else "Mages %d" % (ml2 + 1), "Max level" if ml2 >= 3 else ("No castle" if not home else "%d magic" % int(M.mage_up[ml2])), ml2 < 3 and home and magic >= int(M.mage_up[mini(2, ml2)]), func(): _do(func(): g.myth_up_mages(0))])''',
  '''		var rq: bool = g.mage_req_ok(0, ml2)
		var rq_note: String = ""
		if ml2 < 3:
			var q: Dictionary = M.mage_req[ml2]
			rq_note = ("%d/%d trees" % [g.trees_of(0), int(q.trees)]) if g.trees_of(0) < int(q.trees) else ("%d/%d castles" % [g.cap_castles_of(0), int(q.castles)])
		items.append(["res://art/units/mage0.png", "Mages 3" if ml2 >= 3 else "Mages %d" % (ml2 + 1), "Max level" if ml2 >= 3 else ("No castle" if not home else (rq_note if not rq else "%d magic" % int(M.mage_up[ml2]))), ml2 < 3 and home and rq and magic >= int(M.mage_up[mini(2, ml2)]), func(): _do(func(): g.myth_up_mages(0))])'''),
 ('''Each level also lengthens the Mage's lightning and adds 1 damage; a Mage keeps the level it was made at." %''',
  '''Each level also lengthens the Mage's lightning and adds 1 damage; a Mage keeps the level it was made at. Each level also needs Life Trees and captured castles when you raise it (level 1: 1 tree; level 2: 3 trees and 1 captured castle; level 3: 5 trees and 2 captured castles); losing a castle later keeps the level." %'''),
])
patch('/scripts/rules/test_rules.gd', [('''	check("mythical: Mage level 1 for 7 magic", g.myth_up_mages(0) and g.mlv_of(0) == 1)''',
 '''	check("mythical: no Mage level 1 without a Life Tree", not g.myth_up_mages(0) and g.mlv_of(0) == 0)
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
		tr[k].tree = 0''')])
print('mage req ok')

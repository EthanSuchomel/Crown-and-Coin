# Godot port, step 11: the computer plays a 3-way game (browser patch3_ai.py). Everywhere it looked at "the enemy" it
# now looks at every rival still in the game. A rival's home castle is worth 2500 with 3 sides (it knocks them out) and
# 1e4 with 2 (it wins). In its scoring each rival counts 0.6x when there are two. With 2 players nothing changes.
import sys
W = sys.argv[1]
F = W + '/scripts/rules/ai_player.gd'
s = open(F, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    if s.count(a) != n: print('COUNT', s.count(a), a[:140]); sys.exit(1)
    s = s.replace(a, b)

rep('''static func build_plan(g, pid: int, treb: bool, lvl: int) -> Dictionary:
	var eid: int = 1 - pid
''', '''static func build_plan(g, pid: int, treb: bool, lvl: int) -> Dictionary:
''')
rep('''		var enemy: Array = []
		for t in g.tiles:
			if int(t.owner) == eid:
				enemy.append(int(t.id))
		var d_enemy: Array = bfs(g, enemy)''', '''		var d_enemy: Array = bfs(g, g.foe_tiles(pid))''')
rep('''		var d_home: Array = bfs(g, [g.homes[eid]])''', '''		var d_home: Array = bfs(g, g.foe_homes(pid))''', 2)
rep('''	var p: Dictionary = g.players[pid]
	var eid: int = 1 - pid
	var gold: int = int(p.gold) - keep''', '''	var p: Dictionary = g.players[pid]
	var gold: int = int(p.gold) - keep''')
rep('''	var enemy: Array = []
	for t in g.tiles:
		if int(t.owner) == eid:
			enemy.append(int(t.id))
	var d_en: Array = bfs(g, enemy)''', '''	var d_en: Array = bfs(g, g.foe_tiles(pid))''')
rep('''	var p: Dictionary = g.players[pid]
	var eid: int = 1 - pid
	var sites: Array''', '''	var p: Dictionary = g.players[pid]
	var sites: Array''')
rep('''			var d_eh: Array = bfs(g, [g.homes[1 - pid]])''', '''			var d_eh: Array = bfs(g, g.foe_homes(pid))''')
rep('''	var eid: int = 1 - pid
	var prog: float = float(D[int(s.id)]) - float(D[int(b.id)])''', '''	var foe: bool = int(b.owner) >= 0 and int(b.owner) != pid
	var prog: float = float(D[int(s.id)]) - float(D[int(b.id)])''')
rep('''		castle_v = 10000.0 if g.homes[eid] == int(b.id) else 45.0   # their home castle wins the game outright
	var to_win: int = int(GameData.rules.castles.to_win)
	if castle_v < 10000.0 and b.castle and int(b.owner) == eid and not g.siege.is_empty() and int(g.siege.pid) == eid:
		castle_v = 3000.0   # breaks their hold: must try
	elif b.castle and g.castle_count(pid) + 1 >= to_win:''', '''		var their_home: bool = foe and g.homes[int(b.owner)] == int(b.id)
		castle_v = ((2500.0 if g.foes_of(pid).size() > 1 else 10000.0) if their_home else 45.0)   # a rival's home castle: wins (2 sides) or knocks them out (3)
	var to_win: int = int(GameData.rules.castles.to_win)
	if castle_v < 10000.0 and b.castle and foe and not g.siege.is_empty() and int(g.siege.pid) == int(b.owner):
		castle_v = 3000.0   # breaks their hold: must try
	elif b.castle and g.players.size() == 2 and g.castle_count(pid) + 1 >= to_win:''')
rep('''(3.0 if int(b.owner) == eid else 0.0) + adv''', '''(3.0 if foe else 0.0) + adv''')
rep('''	var tr: Array = [0.0, 0.0]
	var tl: Array = [0, 0]
	var ca: Array = [0, 0]
	var xv: Array = [0.0, 0.0]''', '''	var np: int = g.players.size()
	var tr: Array = []
	var tl: Array = []
	var ca: Array = []
	var xv: Array = []
	for k in np:
		tr.append(0.0)
		tl.append(0)
		ca.append(0)
		xv.append(0.0)
	var foes: Array = g.foes_of(pid)
	var fw: float = 0.6 if foes.size() > 1 else 1.0''')
rep('''	for i in [0, 1]:
		var sgn: float = 1.0 if i == pid else -1.0''', '''	for i in [pid] + foes:
		var sgn: float = 1.0 if i == pid else -fw''')
rep('''(250.0 if ca[i] >= to_win else 0.0)''', '''(250.0 if np == 2 and ca[i] >= to_win else 0.0)''')
rep('''	V += float(W.get("ex2", 0.3)) * exposure(g, 1 - pid)''', '''	for e in foes:
		V += float(W.get("ex2", 0.3)) * exposure(g, e) / foes.size()''')
rep('''	var eid: int = 1 - pid
	var srcs: Array = []
	for t in g.tiles:
		if int(t.owner) == eid:
			srcs.append(int(t.id))
	var dE: Array = bfs(g, srcs)''', '''	var dE: Array = bfs(g, g.foe_tiles(pid))''')
# only battles with a person go to the Arena
rep('''		if g.arena_fights and g.is_fight(int(best.from), int(best.to)):''', '''		if g.arena_fights and g.is_fight(int(best.from), int(best.to)) and g.needs_arena(pid, int(g.tiles[int(best.to)].owner)):''')
assert 'eid' not in s.replace('foes', '').replace('seid', ''), [l for l in s.split('\n') if 'eid' in l][:5]
open(F, 'w', encoding='utf-8').write(s)
print('ai3 ok')

# the distance maps are as big as the board (64 or 121)
s = open(F, encoding='utf-8').read()
for a, b in [('	dist.resize(64)', '	dist.resize(g.tiles.size())'), ('		D.resize(64)\n		for i in 64:', '		D.resize(g.tiles.size())\n		for i in g.tiles.size():')]:
    assert s.count(a) == 1, a
    s = s.replace(a, b)
open(F, 'w', encoding='utf-8').write(s)
print('ai3 sizes ok')

"""Browser commits 972c1f9, 1b8c9df, 070521a in Godot:
- the computer's turn speed follows its difficulty (Easy the old ~21 s, Medium ~12 s, Hard ~6 s, Expert ~2 s);
- the Mythical open their first turn with their starting 5 magic (nothing collected on turn 1);
- the Floating Castle makes 1 magic a turn, 3 / 6 / 10 with its upgrades (was 10 / 15 / 20 / 25).
Usage: python3 p1_rules.py PROJ"""
import sys
from common import F, T
P = sys.argv[1]
f = F(P + '/data/rules.json')
f.rep('''		"castle_magic": [
			10,
			15,
			20,
			25
		],''', '''		"castle_magic": [
			1,
			3,
			6,
			10
		],''', raw=True)
f.save()

f = F(P + '/scripts/rules/game_state.gd')
f.rep('''	p.gold = int(myth().start_magic) + catch_up(i, int(myth().second_magic), players.size())
	p.mlv = 0''', '''	p.gold = int(myth().start_magic) + catch_up(i, int(myth().second_magic), players.size())
	p.myth_first = true   # no magic collected on the first turn (Ethan, 2026-11-22)
	p.mlv = 0''', raw=True)
f.rep('''	var inc: Dictionary = income_of(current)
	var inc_g: int = roundi(float(inc.total) * gold_mult(current))   # Expert collects extra gold''', '''	var inc: Dictionary = income_of(current)
	var myth_first: bool = bool(p.get("myth_first", false))
	if myth_first:   # the Mythical's first turn: they open with their starting magic
		p.myth_first = false
		inc.total = 0
	var inc_g: int = roundi(float(inc.total) * gold_mult(current))   # Expert collects extra gold''', raw=True)
f.rep('''	add_log("%s collect %d %s%s." % [p.name, inc_g, cur_word(current), (" and %s" % mat_txt(tm)) if tm > 0 else ""])''',
      '''	if myth_first:
		add_log("%s begin with %d magic; the Floating Castle's magic starts next turn." % [p.name, int(p.gold)])
	else:
		add_log("%s collect %d %s%s." % [p.name, inc_g, cur_word(current), (" and %s" % mat_txt(tm)) if tm > 0 else ""])''', raw=True)
f.save()

f = F(P + '/scripts/ui/main.gd')
# the computer's pace
f.rep('''func _run_ai() -> void:
	busy = true
	ai_flash = []
	refresh()
	await get_tree().create_timer(0.8).timeout
	if g == null:
		return
	var game: GameState = g
	var pid: int = game.current''', '''## how much of the Easy pace each level takes (Ethan, 2026-11-22: Easy ~21 s a turn, Expert ~2 s)
const AI_SPEED := {"easy": 1.0, "medium": 0.55, "hard": 0.3, "expert": 0.085}

func _ai_wait(game: GameState, pid: int, sec: float) -> void:
	var k: float = float(AI_SPEED.get(String(game.players[pid].get("diff", "medium")), 1.0))
	await get_tree().create_timer(maxf(0.02, sec * k)).timeout


func _run_ai() -> void:
	busy = true
	ai_flash = []
	refresh()
	if g == null:
		return
	var game: GameState = g
	var pid: int = game.current
	await _ai_wait(game, pid, 0.8)
	if g != game:
		return''', raw=True)
for a, b in [("		await get_tree().create_timer(2.5 + randf() * 1.0).timeout", "		await _ai_wait(game, pid, 2.5 + randf() * 1.0)"),
             ("		await get_tree().create_timer(3.5 + randf() * 1.0).timeout", "		await _ai_wait(game, pid, 3.5 + randf() * 1.0)"),
             ("			await get_tree().create_timer(0.9).timeout", "			await _ai_wait(game, pid, 0.9)"),
             ("			await get_tree().create_timer(1.0).timeout\n			if g != game or game.over >= 0:", "			await _ai_wait(game, pid, 1.0)\n			if g != game or game.over >= 0:"),
             ("			await get_tree().create_timer(1.4).timeout", "			await _ai_wait(game, pid, 1.4)")]:
    f.rep(a, b, raw=True)
# faction info
f.rep('''				"[b]Floating Castle[/b] (home): %d magic''', '''				"[b]Start[/b] with %d magic; the Floating Castle's magic starts on your second turn." % int(M.start_magic),
				"[b]Floating Castle[/b] (home): %d magic''', raw=True)
f.save()

f = F(P + '/scripts/rules/test_rules.gd')
f.rep('"_test_three", "_test_robots"', '"_test_three", "_test_myth_start", "_test_robots"', raw=True)
i = f.s.find('\nfunc ', f.s.find('func _ready'))
f.s = f.s[:i] + '\n' + T('''
func _test_myth_start() -> void:
    var cm: Array = []
    for v in GameData.rules.mythical.castle_magic:
        cm.append(int(v))
    check("mythical: castle magic 1 / 3 / 6 / 10", cm == [1, 3, 6, 10], str(cm))
    var g := GameState.new()
    g.new_game("mythical", [], "robots")
    check("mythical: first turn opens with 5 magic", int(g.players[0].gold) == 5, str(g.players[0].gold))
    g.current = 0
    g.begin_turn()
    check("mythical: nothing collected on the first turn", int(g.players[0].gold) == 5, str(g.players[0].gold))
    var inc: int = int(g.income_of(0).total)
    g.begin_turn()
    check("mythical: the second turn collects the castle's magic", inc >= 1 and int(g.players[0].gold) == 5 + inc, "%d +%d" % [int(g.players[0].gold), inc])
''') + f.s[i:]
f.rep('check("mythical: income is the Floating Castle\'s 10 magic", int(g.income_of(0).total) == 10)',
      'check("mythical: income is the Floating Castle\'s 1 magic", int(g.income_of(0).total) == 1)', raw=True)
f.rep('check("mythical: Floating Castle level 1", g.myth_up_castle(0) and int(g.income_of(0).total) == 15)',
      'check("mythical: Floating Castle level 1", g.myth_up_castle(0) and int(g.income_of(0).total) == 3)', raw=True)
f.save()
print('ok')

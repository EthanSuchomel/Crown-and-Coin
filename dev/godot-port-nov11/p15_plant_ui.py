# Godot fix (Ethan, 2026-11-11): the Life Tree button said "Mage busy" for a Mage that had just moved. The rule
# (plant after moving) was already in game_state.gd myth_plant; the button, hint and leftover warning still wanted a ready Mage.
import sys
F = sys.argv[1] + '/scripts/ui/main.gd'
s = open(F, encoding='utf-8').read()
def rep(a, b):
    global s
    if s.count(a) != 1: print('COUNT', s.count(a), a[:120]); sys.exit(1)
    s = s.replace(a, b)
rep('''		var ready_mage: bool = false
		for k in g.MAGES:
			if int(t.ready.get(k, 0)) > 0:
				ready_mage = true
		var ok: bool = int(t.tree) == 0 and not t.castle and t.terrain == "plain" and ready_mage
		var note: String = "Has one" if int(t.tree) > 0 else ("Not here" if t.castle else ("Needs Mage" if g.mages_on(t) == 0 else ("Free · %d turns" % int(M.tree_turns) if ok else "Mage busy")))''',
'''		var ok: bool = int(t.tree) == 0 and not t.castle and t.terrain == "plain" and g.mages_on(t) > 0   # a Mage that just moved can plant too
		var note: String = "Has one" if int(t.tree) > 0 else ("Not here" if t.castle else ("Needs Mage" if g.mages_on(t) == 0 else ("Free · %d turns" % int(M.tree_turns) if ok else "Not here")))''')
rep('''Plant Life Trees: a ready Mage stays on its hex''', '''Plant Life Trees: a Mage (even one that just moved) stays on its hex''')
rep('''Tap a hex where one of your Mages is ready to plant a Life Tree.''', '''Tap a hex with one of your Mages (one that just moved is fine) to plant a Life Tree.''')
rep('''			for k in g.MAGES:
				if int(t.ready.get(k, 0)) > 0:
					return "A Mage of yours is ready to plant a [b]Life Tree[/b]."''', '''			if g.mages_on(t) > 0:
				return "A Mage of yours can still plant a [b]Life Tree[/b]."''')
open(F, 'w', encoding='utf-8').write(s); print('plant ui ok')

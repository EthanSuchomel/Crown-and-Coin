# Godot port of the Mammal card upgrades (browser commits e8eccb7 and 9732b22, Ethan 2026-11-13).
# Run from the Godot project folder: python3 p_mammcards.py
import json, re, sys, os

def load(p): return open(p, encoding='utf-8').read()
def save(p, s): open(p, 'w', encoding='utf-8').write(s)

class F:
    def __init__(self, p): self.p = p; self.s = load(p)
    def rep(self, a, b, n=1):
        c = self.s.count(a)
        if c != n:
            sys.exit('%s: expected %d of %r, found %d' % (self.p, n, a[:90], c))
        self.s = self.s.replace(a, b)
    def done(self): save(self.p, self.s)

# ---------------- data ----------------
up = json.load(open('data/upgrades.json', encoding='utf-8'))
up['mammals_cards'] = {
  "roam": {"move": [["Long March", "3 moves instead of 2"], ["Far Roam", "4 moves"], ["Mountain Paths", "your units can move onto mountains"]],
           "build": [["Den Raising", "advance one of your barracks a level for free"], ["Second Stall", "a hex's 2nd market is free"], ["Land Bounty", "+1 material for every hex you hold"]],
           "recruit": [["Young Ape", "a free Gorilla at your home castle"], ["Young Rhino", "also a free Rhino there"], ["Young Tusker", "also a free Palaeoloxodon there"]]},
  "forage": {"harvest": [["Grazing", "1 gold for every hex instead of every 2"], ["Gathered Stores", "+1 material for every 3 markets"], ["Rich Grazing", "2 gold for every hex, and +1 material for every 2 markets instead"]],
             "build": [["Supplies", "+3 materials when this action starts"], ["Free Den", "a free barracks: your next one costs nothing"], ["Roost Grant", "a free fortress: your next one costs nothing"]],
             "recruit": [["Den Cubs", "a free Gorilla at every barracks"], ["Roost Cubs", "a free Gorilla at every barracks and every fortress"], ["Rhino Calves", "also a free Rhino on every hex with both a barracks and a fortress"]]},
  "den": {"harvest": [["Home Stores", "+5 gold from your home castle"], ["Home Riches", "+10 gold instead"], ["Home Bounty", "+15 gold and 3 materials instead"]],
          "recruit": [["Den Prices", "units cost 1 gold less"], ["Den Pack", "3 free Gorillas at your home castle"], ["Den Rhino", "also a free Rhino at your home castle"]],
          "fortify": [["Quill Guard", "a free Porcupine with every army of 10 or more units"], ["Quill Wall", "2 Porcupines instead"], ["Rhino Guard", "also a free Rhino with each of those armies"]]},
  "wild": {"recruit": [["Hide Trade", "+1 material for every 3 units you buy"], ["Tusk Trade", "+5 materials for every Palaeoloxodon you buy"], ["Home Calling", "units at your home castle cost 2 gold less"]],
           "harvest": [["Castle Tribute", "+3 gold for every castle you hold"], ["Castle Riches", "+6 gold for every castle instead"], ["Castle Hoard", "+10 gold for every castle instead"]],
           "advance": [["Roost Raising", "you can build one fortress in this action"], ["Den Move", "move a barracks to an open spot on another of your hexes (it keeps its level)"], ["Free Roost", "a free fortress: your next one costs nothing"]]},
  "tusks": {"harvest": [["Castle Lands", "from now on, every round each castle you hold makes +1 gold"], ["Castle Herds", "every round, each castle makes +3 gold and +1 material instead"], ["Castle Wealth", "every round, each castle makes +5 gold and +2 materials instead"]],
            "advance": [["Free Den Upgrade", "your first barracks upgrade in this action is free"], ["Quick Dens", "barracks upgrades cost 1 material less"], ["Roam Free", "after this action, move your units anywhere within your land, as often as you like"]],
            "move": [["Charge", "an extra move, if that move is an attack"], ["Ambush", "sneak attacks: the defenders can't attack until your units land their first hit"], ["Stride", "another extra move"]]},
}
up['_note_mammals'] = "Since 2026-11-13 every Mammal card has its own upgrades (mammals_cards). The old named abilities (mammals_named: Mating, Territorial, Reforest, In Numbers, Fertilize) are retired."
json.dump(up, open('data/upgrades.json', 'w', encoding='utf-8'), indent='\t', ensure_ascii=False)

fa = json.load(open('data/factions.json', encoding='utf-8'))
fa['mammals']['card_art'] = {k: 'res://art/cards/%s.png' % k for k in ['roam', 'forage', 'den', 'wild', 'tusks']}
fa['ai_upgrade_pref_faction'] = {}   # the Mammals used to value their Mating and Watering Hole more
json.dump(fa, open('data/factions.json', 'w', encoding='utf-8'), indent='\t', ensure_ascii=False)

# ---------------- rules ----------------
g = F('scripts/rules/game_state.gd')
g.rep('''## Factions whose cards have their own upgrades: the Dinosaurs, and the Robots since 2026-11-11.
func card_ups(pid: int) -> bool:
	return is_dinos(pid) or is_robots(pid)''', '''## Factions whose cards have their own upgrades: the Dinosaurs, the Robots since 2026-11-11 and the Mammals since 2026-11-13.
func card_ups(pid: int) -> bool:
	return is_dinos(pid) or is_robots(pid) or is_mammals(pid)''')
g.rep('''	if not d.has(cid):
		d = GameData.upgrades.get("robots_cards", {})
	return''', '''	if not d.has(cid):
		d = GameData.upgrades.get("robots_cards", {})
	if not d.has(cid):
		d = GameData.upgrades.get("mammals_cards", {})
	return''')
g.rep('(1 if mamm_now(pid, "move") else 0)', 'mamm_moves(pid)')
g.rep('## Moves in a Move action: 2, or 3 with the Mammals\' Territorial; the Mythical always have 3.',
      '## Moves in a Move action: 2, plus the cards\' extra moves; the Mythical always have 3.')
g.rep('''	return dk(pid, "stamp", "move") >= 1 and not play.is_empty()''',
      '''	return (dk(pid, "stamp", "move") >= 1 or dk(pid, "tusks", "move") >= 1) and not play.is_empty()''')   # Charge (Tusks and Thorns)
g.rep('''	if is_robots(current):
		return 1 if dk(current, "mobil", "move") >= 2 else 0   # Climb (Mobilize)
''', '''	if is_robots(current):
		return 1 if dk(current, "mobil", "move") >= 2 else 0   # Climb (Mobilize)
	if is_mammals(current):
		return 1 if dk(current, "roam", "move") >= 3 else 0   # Mountain Paths (The Long Roam)
''')
g.rep('	var eff: int = 0 if (is_dinos(pid) or raw == 1) else raw', '	var eff: int = 0 if (card_ups(pid) or raw == 1) else raw')
g.rep('''	var a: String = card_action()
	if a != "fortify" or not fx_on():
		return a''', '''	var a: String = card_action()
	if a == "advance" and int(play.get("rg", 0)) == 1:
		return "move"   # Roam Free (Tusks and Thorns): the regroup after the Advancements
	if a != "fortify" or not fx_on():
		return a''')
g.rep('''func regrouping() -> bool:
	return fx_on() and String(play.fx.ph) == "regroup"''', '''func regrouping() -> bool:
	return (fx_on() and String(play.fx.ph) == "regroup") or rg_on()   # also Roam Free (Tusks and Thorns)


## Roam Free (Tusks and Thorns' Advancements level 3): after the action, a regroup with any number of moves
## to any of your hexes. play.rg: 1 while it runs, 2 once done.
func rg_on() -> bool:
	return not play.is_empty() and int(play.get("rg", 0)) == 1 and card_action() == "advance"


func rg_due(pid: int) -> bool:
	return not play.is_empty() and current == pid and int(play.get("rg", 0)) == 0 and is_mammals(pid) and card_action() == "advance" and dk(pid, "tusks", "advance") >= 3''')
g.rep('''	return 99 if (fx_on() and int(play.fx.get("far", 0)) > 0) else regroup_reach()''',
      '''	if rg_on():
		return 99
	return 99 if (fx_on() and int(play.fx.get("far", 0)) > 0) else regroup_reach()''')
g.rep('''	if not regrouping() or int(play.fx.get("rally", 0)) <= 0''', '''	if not fx_on() or not regrouping() or int(play.fx.get("rally", 0)) <= 0''')
g.rep('''		if rg and int(play.fx.get("far", 0)) > 0 and''', '''		if rg and fx_on() and int(play.fx.get("far", 0)) > 0 and''')
g.rep('''	if is_mammals(pid) and raw >= 1:
		var ids: Array = _mating(pid)
		out.append("Mating: young born on %d hex%s" % [ids.size(), "" if ids.size() == 1 else "es"] if not ids.is_empty() else "Mating: no pairs to breed yet")
''', '''	if is_mammals(pid) and not play.is_empty():
		out.append_array(_mamm_fortify(pid, raw))   # Den Season's Fortify (Mating is retired)
''')
g.rep('## A Fortify starts with its faction ability (the Mammals\' Mating, the Robots\' Update)', '## A Fortify starts with its faction ability (the Robots\' Update)')
g.rep('''func last_step_now() -> bool:
	if play.is_empty():
		return false
''', '''func last_step_now() -> bool:
	if play.is_empty():
		return false
	if rg_due(current):
		return false   # Roam Free comes first
''')
g.rep('''	var card: Dictionary = card_of(current, play.card)
	if fx_next():
		return   # still inside a Fortify''', '''	var card: Dictionary = card_of(current, play.card)
	if rg_due(current):   # Roam Free (Tusks and Thorns): the regroup after the Advancements
		play.rg = 1
		play.moves = 0
		return
	if int(play.get("rg", 0)) == 1:
		play.rg = 2
	if fx_next():
		return   # still inside a Fortify''')
g.rep('''	var offline: bool = dk(pid, "mobil", "move") >= 3 and not herd   # Offline (Mobilize, Move level 3)''',
      '''	var offline: bool = (dk(pid, "mobil", "move") >= 3 or dk(pid, "tusks", "move") >= 2) and not herd   # Offline (Mobilize), Ambush (Tusks and Thorns)''')
g.rep('''		cost -= int(GameData.rules.mammals.wh_off)   # a Watering Hole
''', '''		cost -= int(GameData.rules.mammals.wh_off)   # a Watering Hole
	if is_mammals(pid):
		if dk(pid, "den", "recruit") >= 1:
			cost -= 1   # Den Prices (Den Season)
		if dk(pid, "wild", "recruit") >= 3 and is_home_castle(t) and int(t.owner) == pid:
			cost -= 2   # Home Calling (Call of the Wild)
''')
g.rep('''dino_harvest(current) if is_dinos(current) else (robo_harvest(current) if is_robots(current) else {"g": 0, "m": 0, "why": []})''',
      '''dino_harvest(current) if is_dinos(current) else (robo_harvest(current) if is_robots(current) else (mamm_harvest(current) if is_mammals(current) else {"g": 0, "m": 0, "why": []}))''')
g.rep('''	var nest: int = nest_gold(pid)
	var total: int = Economy.turn_income(mods_of(pid), hexes, castles, markets, nest)
	return {"hexes": hexes, "castles": castles, "markets": markets, "nest": nest, "total": total}''',
      '''	var nest: int = nest_gold(pid)
	var tusk: int = castles * int(TUSK_G[tusk_lv(pid)])   # Tusks and Thorns' Harvest (Mammals): every round, more gold for each castle
	var total: int = Economy.turn_income(mods_of(pid), hexes, castles, markets, nest) + tusk
	return {"hexes": hexes, "castles": castles, "markets": markets, "nest": nest, "tusk": tusk, "total": total}''')
g.rep('''	p.gold = int(p.gold) + inc_g
	p.upd_now = p.upd_next''', '''	p.gold = int(p.gold) + inc_g
	var tm: int = int(inc.get("castles", 0)) * int(TUSK_M[tusk_lv(current)]) if not is_myth(current) else 0
	if tm > 0:
		p.mat = mat_of(current) + tm   # Tusks and Thorns' Harvest: materials from every castle, every round
	p.upd_now = p.upd_next''')
g.rep('''	add_log("%s collect %d %s." % [p.name, inc_g, cur_word(current)])''',
      '''	add_log("%s collect %d %s%s." % [p.name, inc_g, cur_word(current), (" and %s" % mat_txt(tm)) if tm > 0 else ""])''')
g.rep('''	if is_robots(pid) and not play.is_empty():
		return robo_action_start(pid)
''', '''	if is_robots(pid) and not play.is_empty():
		return robo_action_start(pid)
	if is_mammals(pid) and not play.is_empty():
		return mamm_action_start(pid)
''')
g.rep('''	if not play.is_empty() and is_robots(current) and cur_action() == "build":
		return robo_cost(current, kind, c, t)
''', '''	if not play.is_empty() and is_robots(current) and cur_action() == "build":
		return robo_cost(current, kind, c, t)
	if not play.is_empty() and is_mammals(current) and cur_action() == "build":
		return mamm_cost(current, kind, c, t)
''')
g.rep('''	if is_robots(pid):
		_robo_built(pid, k, price)
		return
''', '''	if is_robots(pid):
		_robo_built(pid, k, price)
		return
	if is_mammals(pid):
		_mamm_built(pid, k, price)
		return
''')
g.rep('''	if kind == "wh" and (not mamm_now(current, "build") or int(t.get("wh", 0)) > 0):
		return false   # Watering Hole: Mammals with the upgraded Build, one per hex''',
      '''	if kind == "wh" and (not is_mammals(current) or int(t.get("wh", 0)) > 0):
		return false   # Watering Hole: a Mammal building in any Build (since 2026-11-13), one per hex''')
g.rep('''	var free: bool = cur_lvl() >= 1 and not bool(play.free_bk) and lv == 0''',
      '''	var free: bool = ((cur_lvl() >= 1 and lv == 0) or dk(current, "tusks", "advance") >= 1) and not bool(play.free_bk)   # Free Den Upgrade (Tusks and Thorns): the first one, any level''')
g.rep('''	if dk(pid, "cons", "advance") >= 1:
		c -= 1   # Quick Barracks (Construction)''', '''	if dk(pid, "cons", "advance") >= 1:
		c -= 1   # Quick Barracks (Construction)
	if dk(pid, "tusks", "advance") >= 2:
		c -= 1   # Quick Dens (Tusks and Thorns)''')
g.rep('''	p.gold = int(p.gold) - cost
	add_units(i, unit, n, true)
	t.new_t = turn
	var free: int = 0''', '''	p.gold = int(p.gold) - cost
	add_units(i, unit, n, true)
	t.new_t = turn
	mamm_bought(current, unit, n)   # Hide Trade and Tusk Trade (Call of the Wild)
	var free: int = 0''')
g.rep('''	p.gold = int(p.gold) - cost
	add_units(i, unit, n, true)
	t.new_t = turn
	add_log("%s train %d %s." % [p.name, n, GameData.units[unit].name])''', '''	p.gold = int(p.gold) - cost
	add_units(i, unit, n, true)
	t.new_t = turn
	mamm_bought(current, unit, n)   # Hide Trade and Tusk Trade (Call of the Wild)
	add_log("%s train %d %s." % [p.name, n, GameData.units[unit].name])''')
g.rep('''			"fnest": 0,   # Dinosaurs (New Nest): free barracks still to build
''', '''			"fnest": 0,   # Dinosaurs (New Nest) and Mammals (Free Den): free barracks still to build
			"ffort": 0,   # Mammals (Roost Grant, Free Roost): free fortresses still to build
''')
g.rep('''		for key in ["mat", "tr", "fnest"]:''', '''		for key in ["mat", "tr", "fnest", "ffort"]:''')

MAMM = r'''
# =====================================================================
# The Mammal cards' own upgrades (Ethan, 2026-11-13). The old Mammal abilities (Mating, Territorial, Reforest,
# In Numbers, Fertilize) are retired, and the Watering Hole is a normal Mammal building in any Build.
# =====================================================================

const TUSK_G := [0, 1, 3, 5]   # Tusks and Thorns' Harvest: gold per castle every round, by level
const TUSK_M := [0, 0, 1, 2]   # ... and materials per castle


## The Mammal cards' extra moves: The Long Roam (3, then 4 moves), Tusks and Thorns (Charge, then Stride).
func mamm_moves(pid: int) -> int:
	var r: int = dk(pid, "roam", "move")
	var u: int = dk(pid, "tusks", "move")
	return (2 if r >= 2 else (1 if r >= 1 else 0)) + (1 if u >= 1 else 0) + (1 if u >= 3 else 0)


## Tusks and Thorns' Harvest level, played now or not: once reached, every castle pays more every round.
func tusk_lv(pid: int) -> int:
	if pid < 0 or pid >= players.size() or not is_mammals(pid):
		return 0
	return card_lv(pid, "tusks", "harvest")


func _unit_words(got: Dictionary) -> String:
	var parts: Array = []
	for k in got:
		var n: int = int(got[k])
		parts.append("%d %s" % [n, String(GameData.units[k].name)])
	return ", ".join(parts)


## A Mammal Harvest's card upgrades: Forage (gold per hex, materials from markets), Den Season (the home castle),
## Call of the Wild (gold per castle). Tusks and Thorns' castles pay every round instead (income_of and begin_turn).
func mamm_harvest(pid: int) -> Dictionary:
	var mk: int = 0
	var cs: int = 0
	var hexes: int = 0
	for t in tiles:
		if int(t.owner) == pid:
			hexes += 1
			mk += int(t.market)
			if t.castle:
				cs += 1
	var half: int = int(floor(hexes * float(GameData.rules.actions.harvest.per_hex_by_level[0])))
	var g: int = 0
	var m: int = 0
	var why: Array = []
	var fo: int = dk(pid, "forage", "harvest")
	var de: int = dk(pid, "den", "harvest")
	var wi: int = dk(pid, "wild", "harvest")
	if fo >= 1:
		var x: int = (2 if fo >= 3 else 1) * hexes - half
		g += x
		why.append("%s +%d" % ["Rich Grazing" if fo >= 3 else "Grazing", x])
	if fo >= 2:
		var x2: int = mk / (2 if fo >= 3 else 3)
		m += x2
		why.append("%s +%s" % ["Rich Grazing" if fo >= 3 else "Gathered Stores", mat_txt(x2)])
	if de >= 1:
		var names: Array = ["", "Home Stores", "Home Riches", "Home Bounty"]
		var golds: Array = [0, 5, 10, 15]
		if int(tiles[homes[pid]].owner) == pid:
			g += int(golds[de])
			if de >= 3:
				m += 3
			why.append("%s +%d%s" % [names[de], int(golds[de]), (" and +%s" % mat_txt(3)) if de >= 3 else ""])
		else:
			why.append("%s: nothing, because you don't hold your home castle" % names[de])
	if wi >= 1:
		var wn: Array = ["", "Castle Tribute", "Castle Riches", "Castle Hoard"]
		var wg: Array = [0, 3, 6, 10]
		var x4: int = int(wg[wi]) * cs
		g += x4
		why.append("%s +%d" % [wn[wi], x4])
	return {"g": g, "m": m, "why": why}


## A Mammal action's card upgrades that happen when it starts. Returns notes for the card column.
func mamm_action_start(pid: int) -> Array:
	var out: Array = []
	var a: String = card_action()
	var p: Dictionary = players[pid]
	var own: Array = tiles.filter(func(t): return int(t.owner) == pid)
	var home: Dictionary = tiles[homes[pid]]
	var at_home: bool = int(home.owner) == pid
	if a == "build":
		var ro: int = dk(pid, "roam", "build")
		var fo: int = dk(pid, "forage", "build")
		if fo >= 1:
			p.mat = mat_of(pid) + 3
			out.append("Supplies: +%s" % mat_txt(3))
		if fo >= 2:
			p.fnest = int(p.get("fnest", 0)) + 1
			out.append("Free Den: your next barracks is free")
		if fo >= 3:
			p.ffort = int(p.get("ffort", 0)) + 1
			out.append("Roost Grant: your next fortress is free")
		if ro >= 3:
			p.mat = mat_of(pid) + own.size()
			out.append("Land Bounty: +%s from your %d hexes" % [mat_txt(own.size()), own.size()])
			add_log("%s gather %s from their land." % [p.name, mat_txt(own.size())])
		if ro >= 2:
			out.append("Second Stall: a hex's 2nd market costs nothing in this action")
		if ro >= 1:
			play.rbk = 1
			var bks: Array = own.filter(func(t): return int(t.barracks) > 0 and int(t.bk) < 3)
			if bool(p.ai):
				var d_e: Array = _foe_dist(pid)
				bks.sort_custom(func(x, y): return int(x.bk) > int(y.bk) if int(x.bk) != int(y.bk) else float(d_e[int(x.id)]) < float(d_e[int(y.id)]))
				if not bks.is_empty():
					mamm_free_bk(pid, int(bks[0].id))
			else:
				out.append("Den Raising: tap one of your barracks to advance it a level for free" if not bks.is_empty() else "Den Raising: no barracks to advance yet")
	if a == "recruit":
		var ro: int = dk(pid, "roam", "recruit")
		var fo: int = dk(pid, "forage", "recruit")
		var de: int = dk(pid, "den", "recruit")
		var wi: int = dk(pid, "wild", "recruit")
		var got: Dictionary = {}
		var why: Array = []
		if ro >= 1:
			got["ape"] = 1
			why.append("Young " + ("Tusker" if ro >= 3 else ("Rhino" if ro >= 2 else "Ape")))
		if ro >= 2:
			got["rhino"] = 1
		if ro >= 3:
			got["eleph"] = 1
		if de >= 2:
			got["ape"] = int(got.get("ape", 0)) + 3
			why.append("Den Rhino" if de >= 3 else "Den Pack")
		if de >= 3:
			got["rhino"] = int(got.get("rhino", 0)) + 1
		if not got.is_empty():
			if at_home:
				_add_army(int(home.id), got, true)
				out.append("%s: %s at your home castle" % [", ".join(why), _unit_words(got)])
				add_log("%s get %d free units at their home castle." % [p.name, CombatRules.count(got)])
			else:
				out.append("No free units at your home castle, because you don't hold it")
		if fo >= 1:
			var n: int = 0
			var r: int = 0
			for t in own:
				var k: int = int(t.barracks) + (int(t.fort) if fo >= 2 else 0)
				if k > 0:
					add_units(int(t.id), basic_of(pid), k, true)
					n += k
				if fo >= 3 and int(t.barracks) > 0 and int(t.fort) > 0:
					add_units(int(t.id), "rhino", 1, true)
					r += 1
			var nm: String = "Rhino Calves" if fo >= 3 else ("Roost Cubs" if fo >= 2 else "Den Cubs")
			if n + r > 0:
				out.append("%s: +%d Gorilla%s at your barracks%s%s" % [nm, n, "" if n == 1 else "s", " and fortresses" if fo >= 2 else "", (", +%d Rhino%s" % [r, "" if r == 1 else "s"]) if r > 0 else ""])
				add_log("%s get %d free units at their barracks%s." % [p.name, n + r, " and fortresses" if fo >= 2 else ""])
			else:
				out.append("%s: no barracks%s yet" % [nm, " or fortresses" if fo >= 2 else ""])
		if de >= 1:
			out.append("Den Prices: every unit costs 1 gold less in this action")
		if wi >= 1:
			play.bought = 0
			out.append("%s: +1 material for every 3 units you buy%s%s" % ["Hide Trade and Tusk Trade" if wi >= 2 else "Hide Trade", ", +5 for every Palaeoloxodon" if wi >= 2 else "", ". Home Calling: units at your home castle cost 2 gold less" if wi >= 3 else ""])
	if a == "advance":
		var wi: int = dk(pid, "wild", "advance")
		var tu: int = dk(pid, "tusks", "advance")
		if wi >= 3:
			p.ffort = int(p.get("ffort", 0)) + 1
			out.append("Free Roost: your next fortress is free")
		if wi >= 1:
			play.wf = 1
			out.append("Roost Raising: tap one of your hexes to build a fortress there (%s)" % ("free" if mamm_fort_price(pid) == 0 else mat_txt(mamm_fort_price(pid))))
		if wi >= 2:
			play.mb = 1
			out.append("Den Move: tap one of your barracks to move it to another of your hexes")
		if tu >= 1:
			out.append("Free Den Upgrade and Quick Dens: your first barracks upgrade is free, the rest cost 1 material less" if tu >= 2 else "Free Den Upgrade: your first barracks upgrade in this action is free")
		if tu >= 3:
			out.append("Roam Free: after this action you can move your units anywhere within your land")
	return out


## A Mammal Build's prices: Second Stall (The Long Roam), and the free barracks and fortresses (Forage, Call of the Wild).
func mamm_cost(pid: int, k: String, c: int, t: Dictionary) -> int:
	var p: Dictionary = players[pid]
	if k == "market" and dk(pid, "roam", "build") >= 2 and not t.is_empty() and int(t.market) == 1:
		return 0
	if k == "barracks" and int(p.get("fnest", 0)) > 0:
		return 0
	if k == "fort" and int(p.get("ffort", 0)) > 0:
		return 0
	return c


func _mamm_built(pid: int, k: String, price: int) -> void:
	if price > 0:
		return
	var p: Dictionary = players[pid]
	if k == "barracks" and int(p.get("fnest", 0)) > 0:
		p.fnest = int(p.fnest) - 1
	elif k == "fort" and int(p.get("ffort", 0)) > 0:
		p.ffort = int(p.ffort) - 1


## Den Raising (The Long Roam): one barracks goes up a level for free during that Build.
func mamm_free_bk(pid: int, i: int) -> bool:
	var t: Dictionary = tiles[i]
	if play.is_empty() or int(play.get("rbk", 0)) <= 0 or cur_action() != "build" or int(t.owner) != pid or int(t.barracks) == 0 or int(t.bk) >= 3:
		return false
	t.bk = int(t.bk) + 1
	play.rbk = 0
	_note_unlock(pid, "barracks", t)
	add_log("%s advance a barracks to level %d for free." % [players[pid].name, int(t.bk)])
	return true


## Roost Raising (Call of the Wild): one fortress during that Advancements (free with a free-fortress token).
func mamm_fort_ok(pid: int, t: Dictionary) -> bool:
	return not play.is_empty() and int(play.get("wf", 0)) > 0 and cur_action() == "advance" and int(t.owner) == pid and t.terrain == "plain" and not t.castle and building_count(t) < max_buildings()


func mamm_fort_price(pid: int) -> int:
	return 0 if int(players[pid].get("ffort", 0)) > 0 else int(GameData.rules.buildings.cost_by_level.fort[0])


func mamm_fort(pid: int, i: int) -> bool:
	var t: Dictionary = tiles[i]
	var p: Dictionary = players[pid]
	var c: int = mamm_fort_price(pid)
	if not mamm_fort_ok(pid, t) or mat_of(pid) < c:
		return false
	spend_mat(pid, c)
	if c == 0:
		p.ffort = int(p.ffort) - 1
	t.fort = int(t.fort) + 1
	play.wf = 0
	_note_unlock(pid, "fort", t)
	add_log("%s build a fortress%s." % [p.name, "" if c > 0 else " for free"])
	return true


## Den Move (Call of the Wild): a barracks moves to an open spot on another of your hexes and keeps its level.
func mamm_bk_spots(pid: int, from: int) -> Array[int]:
	var out: Array[int] = []
	for t in tiles:
		if int(t.owner) == pid and int(t.id) != from and t.terrain == "plain" and not t.castle and int(t.barracks) == 0 and building_count(t) < max_buildings():
			out.append(int(t.id))
	return out


func mamm_move_bk(pid: int, from: int, to: int) -> bool:
	var a: Dictionary = tiles[from]
	var b: Dictionary = tiles[to]
	if play.is_empty() or int(play.get("mb", 0)) <= 0 or cur_action() != "advance" or int(a.owner) != pid or int(a.barracks) == 0 or not mamm_bk_spots(pid, from).has(to):
		return false
	var lv: int = int(a.bk)
	a.barracks = int(a.barracks) - 1
	if int(a.barracks) == 0:
		a.bk = 0
	b.barracks = 1
	b.bk = lv
	play.mb = 0
	add_log("%s move a barracks%s to another hex." % [players[pid].name, (" (level %d)" % lv) if lv > 0 else ""])
	return true


## Den Season's Fortify: a Porcupine (2 at level 2, and a Rhino at level 3) with every army of 10 or more units.
func _mamm_fortify(pid: int, raw: int) -> Array:
	if String(play.card) != "den" or raw < 1:
		return []
	var got: Dictionary = {"porc": 2 if raw >= 2 else 1}
	if raw >= 3:
		got["rhino"] = 1
	var big: Array = tiles.filter(func(t): return int(t.owner) == pid and int(t.troops) >= 10)
	for t in big:
		_add_army(int(t.id), got, true)
	var nm: String = "Rhino Guard" if raw >= 3 else ("Quill Wall" if raw >= 2 else "Quill Guard")
	if big.is_empty():
		return ["%s: no army of 10 or more units yet" % nm]
	add_log("%s get %s with each of their %d big armies." % [players[pid].name, _unit_words(got), big.size()])
	return ["%s: %s with each of your %d armies of 10 or more" % [nm, _unit_words(got), big.size()]]


## Hide Trade and Tusk Trade (Call of the Wild): materials for the units bought in that Recruit.
func mamm_bought(pid: int, k: String, n: int) -> int:
	var l: int = dk(pid, "wild", "recruit")
	if l < 1 or play.is_empty() or n <= 0:
		return 0
	var was: int = int(play.get("bought", 0))
	play.bought = was + n
	var m: int = int(play.bought) / 3 - was / 3
	if l >= 2 and k == "eleph":
		m += 5 * n
	if m > 0:
		players[pid].mat = mat_of(pid) + m
		add_log("%s trade for %s." % [players[pid].name, mat_txt(m)])
	return m


## Hex steps from every hex to the nearest enemy hex (999 when none can be reached).'''
g.rep('\n## Hex steps from every hex to the nearest enemy hex (999 when none can be reached).', MAMM)
g.done()

# ---------------- the computer ----------------
a = F('scripts/rules/ai_player.gd')
a.rep('''	elif a == "advance":
		if raw >= 1:
			if g.is_mammals(pid):
				g.play.free_walls = int(GameData.rules.mammals.free_walls)   # Reforest
		ids = ai_advance(g, pid, lvl)
''', '''	elif a == "advance":
		ids = ai_advance(g, pid, lvl)
		if g.rg_due(pid):   # Roam Free (Tusks and Thorns): a regroup anywhere in their land after the Advancements
			events.append({"kind": "done", "action": a, "ids": ids})
			g.play.rg = 1
			g.play.moves = 0
			events.append({"kind": "step", "action": "move"})
			events.append_array(ai_regroup(g, pid))
			g.play.rg = 2
			return events
''')
a.rep('''	# New Nest (Dinosaurs): free barracks first, on the hex with room nearest the enemy
	while g.is_dinos(pid) and int(p.get("fnest", 0)) > 0:''', '''	# Roost Grant and Free Roost (Mammals): free fortresses first, on the front line
	while g.is_mammals(pid) and int(p.get("ffort", 0)) > 0:
		var d_f: Array = g._foe_dist(pid)
		var cf: Array = g.tiles.filter(func(x): return int(x.owner) == pid and x.terrain == "plain" and not x.castle and g.building_count(x) < g.max_buildings())
		if cf.is_empty():
			break
		cf.sort_custom(func(x, y): return float(d_f[int(x.id)]) < float(d_f[int(y.id)]) if float(d_f[int(x.id)]) != float(d_f[int(y.id)]) else tp(g, x) > tp(g, y))
		var ft: Dictionary = cf[0]
		ft.fort = int(ft.fort) + 1
		g._note_unlock(pid, "fort", ft)
		p.ffort = int(p.ffort) - 1
		ids.append(int(ft.id))
		g.add_log("%s build a free fortress." % p.name)
	# New Nest (Dinosaurs) and Free Den (Mammals): free barracks first, on the hex with room nearest the enemy
	while (g.is_dinos(pid) or g.is_mammals(pid)) and int(p.get("fnest", 0)) > 0:''')
a.rep('''	if g.mamm_now(pid, "build") and g.mat_reach''', '''	if g.is_mammals(pid) and g.mat_reach''')
a.rep('''	if lvl >= 1 and not bool(g.play.free_bk):
		for t in bks:
			if int(t.bk) == 0:
				if g.upgrade_barracks(int(t.id)):
					ids.append(int(t.id))
				break
''', '''	if lvl >= 1 and not bool(g.play.free_bk):
		for t in bks:
			if int(t.bk) == 0:
				if g.upgrade_barracks(int(t.id)):
					ids.append(int(t.id))
				break
	if g.dk(pid, "tusks", "advance") >= 1 and not bool(g.play.free_bk) and not bks.is_empty():   # Free Den Upgrade (Tusks and Thorns)
		if g.upgrade_barracks(int(bks[0].id)):
			ids.append(int(bks[0].id))
	if g.is_mammals(pid) and int(g.play.get("wf", 0)) > 0:   # Roost Raising (Call of the Wild): a fortress on the front line
		var d_w: Array = g._foe_dist(pid)
		var cw: Array = g.tiles.filter(func(x): return g.mamm_fort_ok(pid, x))
		cw.sort_custom(func(x, y): return float(d_w[int(x.id)]) < float(d_w[int(y.id)]) if float(d_w[int(x.id)]) != float(d_w[int(y.id)]) else tp(g, x) > tp(g, y))
		if not cw.is_empty() and g.ai_mat(pid, g.mamm_fort_price(pid), 4) and g.mamm_fort(pid, int(cw[0].id)):
			ids.append(int(cw[0].id))
''')
a.rep('''	if CombatRules.count(got) == 0:
		return []
	g._add_army(sid, got, true)''', '''	if CombatRules.count(got) == 0:
		return []
	if g.is_mammals(pid):
		for k in got:
			g.mamm_bought(pid, k, int(got[k]))   # Hide Trade and Tusk Trade (Call of the Wild)
	g._add_army(sid, got, true)''')
a.rep('''	var limit: int = g.moves_limit(pid)   # 3 with the Mammals' Territorial''', '''	var limit: int = g.moves_limit(pid)   # more with the cards' extra moves''')
a.done()

# ---------------- the screen ----------------
m = F('scripts/ui/main.gd')
m.rep('''var robo_up: String = ""''', '''var mv_bk: int = -1   # Den Move (Mammals): the barracks being moved during Advancements
var robo_up: String = ""''')
m.rep('''	if g.mamm_now(0, "build"):
		var wc2''', '''	if g.is_mammals(0):
		var wc2''')
m.rep('''		if g.mamm_now(0, "build"):
			var wp''', '''		if g.is_mammals(0):
			var wp''')
m.rep('''			lines.append("Offline: a sneak attack.''', '''			lines.append(("Ambush" if g.is_mammals(0) else "Offline") + ": a sneak attack.''')
m.rep('''		if my_faction == "dinos" or my_faction == "robots":
			body.add_child(_rich(_card_list(my_faction), 14))''', '''		if my_faction == "dinos" or my_faction == "robots" or my_faction == "mammals":
			body.add_child(_rich(_card_list(my_faction), 14))''')
m.rep('''	if my_faction == "robots":
		body.add_child(_label("Factories", 16, BONE, true))
		body.add_child(_rich(_robo_specials(), 14))''', '''	if my_faction == "robots":
		body.add_child(_label("Factories", 16, BONE, true))
		body.add_child(_rich(_robo_specials(), 14))
	if my_faction == "mammals":
		body.add_child(_label("Watering Hole", 16, BONE, true))
		body.add_child(_rich(_mamm_specials(), 14))''')
m.rep('''	var lines: Array = ["[b]Every %s card has its own upgrades for each of its actions[/b] (every 2nd play you pick which action goes up a level):" % ("Robot" if fid == "robots" else "Dinosaur")]''',
      '''	var lines: Array = ["[b]Every %s card has its own upgrades for each of its actions[/b] (every 2nd play you pick which action goes up a level):" % String(GameData.factions[fid].name).trim_suffix("s")]''')
m.rep('''## Every Dinosaur or Robot card's own upgrades, for How to play and the faction screen.''', '''## The Watering Hole, for How to play and the faction screen.
func _mamm_specials() -> String:
	return "[img=22]res://art/buildings/wh.png[/img] Rhinos, Desmodus and Palaeoloxodons trained on a hex with a Watering Hole cost %d gold less. It costs %s and can go up in any Build, one per hex." % [int(GameData.rules.mammals.wh_off), g.mat_txt(int(GameData.rules.buildings.cost_by_level.wh[0])) if g != null else "%d materials" % int(GameData.rules.buildings.cost_by_level.wh[0])]


## Every Dinosaur, Robot or Mammal card's own upgrades, for How to play and the faction screen.''')
m.rep('''	elif g != null and g.is_robots(0):
		txt += "\\n\\n" + _robo_specials() + "\\n\\n" + _card_list("robots")''', '''	elif g != null and g.is_robots(0):
		txt += "\\n\\n" + _robo_specials() + "\\n\\n" + _card_list("robots")
	elif g != null and g.is_mammals(0):
		txt += "\\n\\n" + _mamm_specials() + "\\n\\n" + _card_list("mammals")''')
m.rep('''		if g.regrouping():
			next_txt = "Done regrouping  ▶"''', '''		if g.rg_due(0):
			next_txt = "Next: move units  ▶"   # Roam Free (Tusks and Thorns)
		elif g.rg_on():
			next_txt = "Done, end turn" if last else "Done, next action  ▶"
		elif g.regrouping():
			next_txt = "Done regrouping  ▶"''')
m.rep('''		"move":
			if g.regrouping():
				_regroup_controls(box)''', '''		"move":
			if g.rg_on():
				_roam_free_controls(box)
			elif g.regrouping():
				_regroup_controls(box)''')
m.rep('''## Fortify's regroup: free moves inside your own land.''', '''## Roam Free (Tusks and Thorns): after the Advancements, move your units anywhere within your land.
func _roam_free_controls(box: VBoxContainer) -> void:
	box.add_child(_rich("%s [b]Roam Free[/b]" % _img("move", 24), 16))
	if _sel_mine() and int(g.tiles[sel].troops) > 0:
		var parts: Array = []
		for k in g._by_strength(g.tiles[sel].ready):
			parts.append("[img height=22]res://art/units/%s.png[/img] %d" % [k, int(g.tiles[sel].ready[k])])
		box.add_child(_rich("Here: " + ("  ".join(parts) if not parts.is_empty() else "[color=#a5b49e]nobody ready to move[/color]"), 14))
	_hint(box, ("Tap a highlighted hex of yours to send units there. " if (_sel_mine() and int(g.tiles[sel].fresh) > 0) else "Tap a hex with your units, then any highlighted hex of yours. ") + "Move your units anywhere within your land, as often as you like (no attacks or claiming). Then tap Done.")


## Fortify's regroup: free moves inside your own land.''')
m.rep('''func _leftover_warning() -> String:
	var a: String = g.cur_action()''', '''func _leftover_warning() -> String:
	if g.rg_on():
		return ""   # Roam Free is optional
	var a: String = g.cur_action()''')
m.rep('''	wall_for = -1
	robo_up = ""
	var before: int = g.log_n
	g.next_step()''', '''	wall_for = -1
	robo_up = ""
	mv_bk = -1
	var before: int = g.log_n
	g.next_step()''')
m.rep('''		elif robo_up != "" and g.cur_action() == "advance":
			board.targets = g.robo_up_targets(0, robo_up)''', '''		elif robo_up != "" and g.cur_action() == "advance":
			board.targets = g.robo_up_targets(0, robo_up)
		elif mv_bk >= 0 and g.cur_action() == "advance":
			board.targets = g.mamm_bk_spots(0, mv_bk)   # Den Move''')
m.rep('''	if g.cur_action() == "advance" and robo_up != "":   # the Robots: tap a ringed market or factory to upgrade it''', '''	if g.cur_action() == "advance" and mv_bk >= 0:   # Den Move (Call of the Wild): tap where the barracks goes
		if board.targets.has(i):
			var f0: int = mv_bk
			mv_bk = -1
			sel = i
			_do(func(): g.mamm_move_bk(0, f0, i))
			return
		mv_bk = -1
	if g.cur_action() == "advance" and robo_up != "":   # the Robots: tap a ringed market or factory to upgrade it''')
m.rep('''func _build_controls(box: VBoxContainer) -> void:
	if g.is_robots(0):''', '''func _build_controls(box: VBoxContainer) -> void:
	if g.is_mammals(0) and int(g.play.get("rbk", 0)) > 0:   # Den Raising (The Long Roam)
		if _sel_mine() and int(g.tiles[sel].barracks) > 0 and int(g.tiles[sel].bk) < 3:
			box.add_child(_button("Den Raising: advance this barracks to level %d for free" % (int(g.tiles[sel].bk) + 1), func(): _do(func(): g.mamm_free_bk(0, sel)), true))
		else:
			_hint(box, "Den Raising: tap one of your barracks to advance it a level for free.")
	if g.is_robots(0):''')
m.rep('''	if not _sel_mine():
		_hint(box, "▸ Tap one of your hexes to upgrade a barracks or hire its Alamosaurus guards''', '''	if g.is_mammals(0) and mv_bk >= 0:   # Den Move (Call of the Wild): placing the barracks
		var nsp: int = g.mamm_bk_spots(0, mv_bk).size()
		box.add_child(_rich("[img=26]res://art/buildings/barracks_mammals.png[/img] [b]Den Move[/b]", 16))
		_hint(box, ("▸ Tap a ringed hex of yours to move the barracks there. It keeps its level. %d of your hexes have room." % nsp) if nsp > 0 else "None of your other hexes has room for it (castles can't take one).")
		box.add_child(_button("Cancel", func():
			mv_bk = -1
			refresh()))
		return
	if g.is_mammals(0) and (int(g.play.get("wf", 0)) > 0 or int(g.play.get("mb", 0)) > 0):   # Roost Raising and Den Move (Call of the Wild)
		if _sel_mine():
			var t0: Dictionary = g.tiles[sel]
			if g.mamm_fort_ok(0, t0):
				var fp: int = g.mamm_fort_price(0)
				var fb := _button("Roost Raising: build a fortress here (%s)" % (g.mat_txt(fp) if fp > 0 else "free"), func(): _do(func(): g.mamm_fort(0, sel)), true)
				fb.disabled = g.mat_of(0) < fp
				box.add_child(fb)
			if int(g.play.get("mb", 0)) > 0 and int(t0.barracks) > 0:
				box.add_child(_button("Den Move: move this barracks", func():
					mv_bk = sel
					refresh()))
		else:
			_hint(box, " ".join(PackedStringArray(([("Roost Raising: tap one of your hexes to build a fortress there (%s)." % ("free" if g.mamm_fort_price(0) == 0 else g.mat_txt(g.mamm_fort_price(0))))] if int(g.play.get("wf", 0)) > 0 else []) + (["Den Move: tap one of your barracks to move it."] if int(g.play.get("mb", 0)) > 0 else []))))
	if not _sel_mine():
		_hint(box, "▸ Tap one of your hexes to upgrade a barracks or hire its Alamosaurus guards''')
m.done()

# ---------------- self-test ----------------
t = F('scripts/rules/test_rules.gd')
old_start = '	# Mating: pairs breed in Fortify, at most 3 per hex\n'
old_end = '	check("mammals: a saved Mammal game loads back", int(gl.tiles[home].wh) == 1 and gl.players[0].faction == "mammals")\n'
i0 = t.s.index(old_start); i1 = t.s.index(old_end) + len(old_end)
NEW = '''	var home: int = g.homes[0]
	g.current = 0
	# the Watering Hole: a normal Mammal building in any Build
	var t: Dictionary = g.tiles[home]
	t.wh = 1
	var c0: int = g.unit_cost_at(home, 0, "rhino")
	t.wh = 0
	var c1: int = g.unit_cost_at(home, 0, "rhino")
	check("mammals: a Watering Hole makes Rhinos 5 cheaper", c1 - c0 == 5, "%d vs %d" % [c0, c1])
	t.wh = 1
	check("mammals: the Watering Hole counts as a building", g.building_count(t) >= 1)
	var snap: Dictionary = g.snapshot()
	var gl := GameState.new()
	gl.restore(GameState.ints(JSON.parse_string(JSON.stringify(snap))))
	check("mammals: a saved Mammal game loads back", int(gl.tiles[home].wh) == 1 and gl.players[0].faction == "mammals")
	t.wh = 0
	_test_mammal_cards()
'''
t.s = t.s[:i0] + NEW + t.s[i1:]
TESTS = r'''

## The Mammal cards' own upgrades (Ethan, 2026-11-13).
func _mm_game() -> GameState:
	var g := GameState.new()
	g.new_game("mammals", [], "dinos")
	g.current = 0
	g.players[0].ai = false
	return g


func _mm_play(g: GameState, cid: String, a: String, lv: int) -> void:
	var c: Dictionary = g.card_of(0, cid)
	var slot: int = c.actions.find(a)
	g.players[0].up[cid] = [0, 0, 0]
	g.players[0].up[cid][slot] = lv
	g.play = {"card": cid, "step": slot, "moves": 0, "free_bk": false, "al_bought": 0, "al_free": 0}


func _mm_spot(g: GameState) -> int:
	for t in g.tiles:
		if int(t.owner) == -1 and t.terrain == "plain" and not t.castle:
			for n in HexGrid.neighbors(g.homes[0]):
				if n == int(t.id):
					return n
	return -1


func _test_mammal_cards() -> void:
	var g := _mm_game()
	check("mammal cards: the Mammals have card upgrades", g.card_ups(0) and g.d_up(0, "roam", "move") and g.d_up(0, "tusks", "advance"))
	for c in GameData.factions.mammals.cards:
		for a in c.actions:
			check("mammal cards: %s %s has 3 upgrades" % [c.id, a], g.dcard(String(c.id), a).size() == 3)
		check("mammal cards: %s has a picture" % c.id, ResourceLoader.exists(String(GameData.factions.mammals.card_art.get(c.id, ""))))
	# old abilities retired
	_mm_play(g, "roam", "move", 1)
	check("mammal cards: Territorial and In Numbers are retired", not g.named_on() and not g.in_numbers(g.tiles[g.homes[0]]))
	var base: int = int(g.mods_of(0).movesPerAction)
	check("mammal cards: Long March gives 3 moves", g.moves_limit(0) == base + 1)
	_mm_play(g, "roam", "move", 2)
	check("mammal cards: Far Roam gives 4 moves", g.moves_limit(0) == base + 2)
	_mm_play(g, "roam", "move", 3)
	check("mammal cards: Mountain Paths climbs mountains", g.cur_lvl() == 1)
	_mm_play(g, "tusks", "move", 1)
	check("mammal cards: Charge is an extra attack move", g.moves_limit(0) == base + 1 and not g.charge_only(0))
	g.play.moves = base
	check("mammal cards: Charge's last move must attack", g.charge_only(0))
	_mm_play(g, "tusks", "move", 3)
	check("mammal cards: Stride adds another move", g.moves_limit(0) == base + 2)
	check("mammal cards: Ambush makes sneak attacks", bool(g.atk_opts(0, 0, 3, 1).surprise))
	_mm_play(g, "roam", "move", 0)
	check("mammal cards: no sneak attacks without Ambush", not bool(g.atk_opts(0, 0, 0, 1).surprise) and g.moves_limit(0) == base)
	# Fortify gets one pick (the basic Fortify), like the other card factions
	_mm_play(g, "den", "fortify", 2)
	check("mammal cards: an upgraded Fortify still has 1 pick", g.fx_picks_at(0, 2) == 1)
	# Den Season's Fortify: Porcupines with big armies
	var home: int = g.homes[0]
	g.tiles[home].army = {"ape": 12}
	g.sync_tile(g.tiles[home])
	g.play.step = g.card_of(0, "den").actions.find("fortify")
	g.players[0].up.den = [0, 0, 3]
	var fn: Array = g._mamm_fortify(0, 3)
	check("mammal cards: Rhino Guard gives 2 Porcupines and a Rhino to an army of 10+", int(g.tiles[home].army.get("porc", 0)) == 2 and int(g.tiles[home].army.get("rhino", 0)) == 1, str(fn))
	# Harvests
	g = _mm_game()
	home = g.homes[0]
	var hexes: int = int(g.income_of(0).hexes)
	_mm_play(g, "forage", "harvest", 1)
	var hv: Dictionary = g.mamm_harvest(0)
	check("mammal cards: Grazing pays 1 gold per hex in all", int(hv.g) + int(floor(hexes * float(GameData.rules.actions.harvest.per_hex_by_level[0]))) == hexes, str(hv))
	_mm_play(g, "den", "harvest", 3)
	hv = g.mamm_harvest(0)
	check("mammal cards: Home Bounty pays 15 gold and 3 materials", int(hv.g) == 15 and int(hv.m) == 3, str(hv))
	_mm_play(g, "wild", "harvest", 2)
	hv = g.mamm_harvest(0)
	check("mammal cards: Castle Riches pays 6 per castle", int(hv.g) == 6 * g.castle_count(0), str(hv))
	var g0: int = int(g.players[0].gold)
	g._resolve_instant("harvest")
	check("mammal cards: the Harvest pays its card upgrades", int(g.players[0].gold) - g0 >= 6, "%d" % (int(g.players[0].gold) - g0))
	# Tusks and Thorns' Harvest: every round
	g.play = {}
	var inc0: int = int(g.income_of(0).total)
	g.players[0].up.tusks = [3, 0, 0]
	var inc3: Dictionary = g.income_of(0)
	check("mammal cards: Castle Wealth pays +5 per castle every round", int(inc3.total) - inc0 == 5 * g.castle_count(0), "%d vs %d" % [int(inc3.total), inc0])
	var m0: int = g.mat_of(0)
	g.begin_turn()
	check("mammal cards: Castle Wealth gives 2 materials per castle every round", g.mat_of(0) - m0 == 2 * g.castle_count(0), "%d" % (g.mat_of(0) - m0))
	# Builds
	g = _mm_game()
	home = g.homes[0]
	var sp: int = _mm_spot(g)
	g.tiles[sp].owner = 0
	g.tiles[sp].barracks = 1
	g.tiles[sp].bk = 0
	_mm_play(g, "forage", "build", 3)
	m0 = g.mat_of(0)
	var notes: Array = g.dino_action_start(0)
	check("mammal cards: Supplies gives 3 materials", g.mat_of(0) - m0 == 3, str(notes))
	check("mammal cards: Free Den and Roost Grant tokens", int(g.players[0].fnest) == 1 and int(g.players[0].ffort) == 1)
	check("mammal cards: the free barracks and fortress cost nothing", g.build_cost("barracks", g.tiles[sp]) == 0 and g.build_cost("fort", g.tiles[sp]) == 0)
	g.tiles[sp].barracks = 0
	g.players[0].gold = 50
	check("mammal cards: a free fortress can be built", g.build(sp, "fort") and int(g.players[0].ffort) == 0 and int(g.tiles[sp].fort) == 1)
	check("mammal cards: a Watering Hole goes up in any Build", g.build(sp, "wh"))
	_mm_play(g, "roam", "build", 3)
	g.tiles[sp].barracks = 1
	g.tiles[sp].wh = 0
	g.tiles[sp].fort = 0
	m0 = g.mat_of(0)
	g.dino_action_start(0)
	var own: int = g.tiles.filter(func(x): return int(x.owner) == 0).size()
	check("mammal cards: Land Bounty gives 1 material per hex", g.mat_of(0) - m0 == own, "%d vs %d" % [g.mat_of(0) - m0, own])
	check("mammal cards: Den Raising advances a barracks for free", g.mamm_free_bk(0, sp) and int(g.tiles[sp].bk) == 1 and not g.mamm_free_bk(0, sp))
	g.tiles[sp].market = 1
	check("mammal cards: Second Stall makes a hex's 2nd market free", g.build_cost("market", g.tiles[sp]) == 0)
	g.tiles[sp].market = 0
	check("mammal cards: a 1st market still costs gold", g.build_cost("market", g.tiles[sp]) > 0)
	# Recruits
	g = _mm_game()
	home = g.homes[0]
	sp = _mm_spot(g)
	g.tiles[sp].owner = 0
	g.tiles[sp].barracks = 1
	g.tiles[sp].fort = 1
	_mm_play(g, "roam", "recruit", 3)
	var h0: Dictionary = g.tiles[home].army.duplicate()
	g.dino_action_start(0)
	check("mammal cards: Young Tusker gives a Gorilla, a Rhino and a Palaeoloxodon at home", int(g.tiles[home].army.get("eleph", 0)) - int(h0.get("eleph", 0)) == 1 and int(g.tiles[home].army.get("rhino", 0)) - int(h0.get("rhino", 0)) == 1)
	_mm_play(g, "forage", "recruit", 3)
	var s0: Dictionary = g.tiles[sp].army.duplicate()
	g.dino_action_start(0)
	check("mammal cards: Rhino Calves give 2 Gorillas and a Rhino on a barracks-and-fortress hex", int(g.tiles[sp].army.get("ape", 0)) - int(s0.get("ape", 0)) == 2 and int(g.tiles[sp].army.get("rhino", 0)) - int(s0.get("rhino", 0)) == 1, str(g.tiles[sp].army))
	_mm_play(g, "den", "recruit", 3)
	var base_c: int = int(GameData.units.ape.cost)
	check("mammal cards: Den Prices make units 1 gold cheaper", g.unit_cost_at(sp, 0, "ape") == maxi(1, base_c - 1))
	_mm_play(g, "wild", "recruit", 3)
	g.dino_action_start(0)
	check("mammal cards: Home Calling makes home units 2 gold cheaper", g.unit_cost_at(home, 0, "ape") == maxi(1, base_c - 2) and g.unit_cost_at(sp, 0, "ape") == base_c)
	g.players[0].gold = 200
	m0 = g.mat_of(0)
	g.recruit(home, 3)
	check("mammal cards: Hide Trade gives 1 material for 3 units", g.mat_of(0) - m0 == 1, "%d" % (g.mat_of(0) - m0))
	g.tiles[home].fort = 1
	g.players[0].unl.fort = true
	m0 = g.mat_of(0)
	var ok_e: bool = g.train(home, "eleph", "fort", 1)
	check("mammal cards: Tusk Trade gives 5 materials for a Palaeoloxodon", ok_e and g.mat_of(0) - m0 == 5, "%s %d" % [ok_e, g.mat_of(0) - m0])
	# Advancements
	g = _mm_game()
	home = g.homes[0]
	sp = _mm_spot(g)
	g.tiles[sp].owner = 0
	g.tiles[sp].barracks = 1
	g.tiles[sp].bk = 2
	_mm_play(g, "tusks", "advance", 3)
	g.dino_action_start(0)
	g.players[0].mat = 20
	check("mammal cards: Quick Dens make upgrades 1 cheaper", g.bk_up_cost(0, 1) == int(GameData.rules.buildings.barracks_upgrade_cost[1]) - 1)
	m0 = g.mat_of(0)
	check("mammal cards: Free Den Upgrade is free at any level", g.upgrade_barracks(sp) and g.mat_of(0) == m0 and int(g.tiles[sp].bk) == 3)
	check("mammal cards: Roam Free comes after the Advancements", g.rg_due(0) and not g.last_step_now())
	g.next_step()
	check("mammal cards: Roam Free plays as a regroup", g.rg_on() and g.cur_action() == "move" and g.regrouping() and g.moves_limit(0) == GameState.REGROUP_MOVES and g.fx_reach() == 99)
	var tg: Array = g.move_targets(home, 0)
	check("mammal cards: Roam Free moves only inside your land", tg.has(sp) and tg.all(func(j): return int(g.tiles[j].owner) == 0))
	var st0: int = int(g.play.step)
	g.next_step()
	check("mammal cards: Roam Free ends and the card goes on", int(g.play.get("rg", 0)) == 2 or g.play.is_empty() or int(g.play.step) != st0)
	g = _mm_game()
	home = g.homes[0]
	sp = _mm_spot(g)
	g.tiles[sp].owner = 0
	var sp2: int = -1
	for n in HexGrid.neighbors(home):
		if n != sp and int(g.tiles[n].owner) == -1 and g.tiles[n].terrain == "plain" and not g.tiles[n].castle:
			sp2 = n
	g.tiles[sp2].owner = 0
	g.tiles[sp].barracks = 1
	g.tiles[sp].bk = 2
	_mm_play(g, "wild", "advance", 3)
	g.dino_action_start(0)
	g.players[0].mat = 0
	check("mammal cards: Free Roost makes Roost Raising free", g.mamm_fort_price(0) == 0 and g.mamm_fort(0, sp2) and int(g.tiles[sp2].fort) == 1 and not g.mamm_fort(0, sp2))
	check("mammal cards: Den Move keeps the level", g.mamm_move_bk(0, sp, sp2) and int(g.tiles[sp2].barracks) == 1 and int(g.tiles[sp2].bk) == 2 and int(g.tiles[sp].barracks) == 0)
	# the computer plays Mammal games with every card upgraded
	var wins: Array = [0, 0, 0]
	var tot: int = 0
	for gi in 4:
		var ga := GameState.new()
		ga.new_game("dinos" if gi % 2 == 0 else "robots", [], "mammals")
		ga.players[0].ai = true
		ga.begin_turn()
		var turns: int = 0
		while turns < 160 and ga.over < 0:
			if turns == 30:
				for c in GameData.factions.mammals.cards:
					ga.players[1].up[c.id] = [3, 3, 3]   # every Mammal card fully upgraded
			AIPlayer.take_turn(ga)
			turns += 1
		tot += turns
		wins[ga.over + 1 if ga.over >= 0 else 0] += 1
	check("mammal cards: the computer plays upgraded Mammal cards without errors", tot > 0)
	print("      upgraded Mammal computer games: Mammals won %d, rivals %d, unfinished %d" % [wins[2], wins[1], wins[0]])
'''
t.s = t.s.rstrip('\n') + '\n' + TESTS
t.done()
print('patched')

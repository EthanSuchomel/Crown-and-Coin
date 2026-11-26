

# =====================================================================
# The new cards' upgrades (Ethan, 2026-11-24; the browser's NU_UPS). Every faction plays the same five cards, so the
# upgrades go by the card's place in its deck (1st to 5th). Every 2nd favor raises one action on the card a level;
# a later level's bigger amount replaces the earlier one. The Mythical have no markets, barracks or fortresses: an
# upgrade about those makes a unit 1 magic cheaper instead (level 1 the Minotaur, 2 the Griffin, 3 the Mage).
# The texts are in upgrades.json new_cards; the numbers live here, as in the browser.
# =====================================================================

const NU_SET := {"dinos": "mega", "robots": "rknight", "mammals": "rhino", "mythical": "griffin"}
const NU_BUFF := 1.1
const NU_FREEZE := 2
const NU_HARV_M := [0, 2, 5, 10]
const NU_HARV_MY := [0, 1, 3, 5]
const NU_CASTLE := [0, 3, 10, 20]
const NU_CASTLE_MY := [0, 1, 5, 10]
const NU_MUSTER := [0, 2, 5, 10]

static func new_ups() -> bool:
	return bool(GameData.rules.cards.get("new_ups", false))


## The card's place in its deck, 1 to 5 (0: not one of this faction's cards).
func nu_slot(pid: int, cid: String) -> int:
	var cards: Array = faction_of(pid).cards
	for i in cards.size():
		if String(cards[i].id) == cid:
			return i + 1
	return 0


## An action's level on the nth card, whether or not it's being played.
func nu_lv(pid: int, n: int, a: String) -> int:
	if not new_ups() or pid < 0 or pid >= players.size():
		return 0
	var cards: Array = faction_of(pid).cards
	if n < 1 or n > cards.size():
		return 0
	var c: Dictionary = cards[n - 1]
	var i: int = c.actions.find(a)
	return 0 if i < 0 else lvl_of(pid, String(c.id), i)


## ...and only while that card's action is being played (a Fortify's picks play basic).
func nu_k(pid: int, n: int, a: String) -> int:
	if not new_ups() or play.is_empty() or current != pid or nu_slot(pid, String(play.card)) != n or card_action() != a:
		return 0
	if a != "fortify" and fx_on():
		return 0
	return lvl_of(pid, String(play.card), int(play.step))


func nu_see(pid: int) -> bool:
	return nu_lv(pid, 4, "advance") >= 1   # Scouts


func buff_on(t: Dictionary) -> bool:
	var b = t.get("buff", null)
	return b is Dictionary and not b.is_empty() and int(t.owner) == int(b.pid) and turn <= int(b.until)


func nu_move_lvl(pid: int) -> int:
	return 1 if (nu_k(pid, 1, "move") >= 2 or nu_k(pid, 3, "move") >= 1) else 0   # Climb


func nu_text(cid: String, a: String) -> Array:
	return GameData.upgrades.get("new_cards", {}).get(cid, {}).get(a, [])


## The Mythical's cheaper units: 1 magic off a unit while any upgrade that stands for it is owned.
func myth_off(pid: int, k: String) -> int:
	if not new_ups() or pid < 0 or not is_myth(pid):
		return 0
	if k == "minotaur":
		return 1 if (nu_lv(pid, 2, "build") >= 1 or nu_lv(pid, 4, "build") >= 1) else 0
	if k == "griffin":
		return 1 if (nu_lv(pid, 1, "build") >= 2 or nu_lv(pid, 2, "build") >= 2 or nu_lv(pid, 2, "recruit") >= 2) else 0
	if k == "mage":
		return 1 if (nu_lv(pid, 2, "build") >= 3 or nu_lv(pid, 2, "advance") >= 3) else 0
	return 0


## A Build's prices: Free Market and Free Barracks (card 1), Cheap Markets and Cheap Barracks (card 2).
func nu_cost(kind: String, c: int) -> int:
	if not new_ups() or play.is_empty() or cur_action() != "build" or is_myth(current):
		return c
	var b1: int = nu_k(current, 1, "build")
	var b2: int = nu_k(current, 2, "build")
	if kind == "market":
		if b1 >= 1 and not bool(play.get("nfm", false)):
			return 0
		if b2 >= 1:
			c -= 1
	if kind == "barracks":
		if b1 >= 2 and not bool(play.get("nfb", false)) and not is_robots(current):
			return 0
		if b2 >= 2:
			c -= 1
	return maxi(0, c)


func nu_built(pid: int, k: String, price: int) -> void:
	if not new_ups() or play.is_empty() or price > 0:
		return
	if k == "market" and nu_k(pid, 1, "build") >= 1 and not bool(play.get("nfm", false)):
		play.nfm = true
	elif k == "barracks" and nu_k(pid, 1, "build") >= 2 and not bool(play.get("nfb", false)):
		play.nfb = true


func _nu_name(a: String, lv: int, fallback: String) -> String:
	var t: Array = nu_text(String(play.card), a)
	return String(t[lv][0]) if lv >= 0 and lv < t.size() else fallback


func _nu_gain(pid: int, g: int, m: int, why: String, out: Array) -> void:
	var p: Dictionary = players[pid]
	if g > 0:
		p.gold = int(p.gold) + g
	if m > 0:
		p.mat = mat_of(pid) + m
	if g > 0 or m > 0:
		var bits: Array = []
		if g > 0:
			bits.append("%d %s" % [g, cur_word(pid)])
		if m > 0:
			bits.append(mat_txt(m))
		out.append("%s: +%s" % [why, ", ".join(PackedStringArray(bits))])
		add_log("%s get %s (%s)." % [p.name, " and ".join(PackedStringArray(bits)), why])


## What an action's upgrades do as it starts (once per action). Returns notes for the card column.
func nu_action_start(pid: int) -> Array:
	var out: Array = []
	if not new_ups() or play.is_empty():
		return out
	if not play.has("nu_s"):
		play.nu_s = {}
	var key: String = str(int(play.step))
	if play.nu_s.has(key):
		return out
	play.nu_s[key] = true
	var a: String = card_action()
	var p: Dictionary = players[pid]
	var my: bool = is_myth(pid)
	var f: String = String(p.faction)
	var home: Dictionary = tiles[homes[pid]]
	var hold: bool = int(home.owner) == pid
	if a == "build":
		var b1: int = nu_k(pid, 1, "build")
		var b2: int = nu_k(pid, 2, "build")
		var b4: int = nu_k(pid, 4, "build")
		if b1 >= 3:
			_nu_gain(pid, 2 if my else 0, 0 if my else 3, _nu_name(a, 2, "Supplies"), out)
		if b4 >= 2:
			_nu_gain(pid, 3 if my else 0, 0 if my else 3, _nu_name(a, 1, "Supplies"), out)
		if b4 >= 3:
			_nu_gain(pid, 5 if my else 10, 0, _nu_name(a, 2, "Funding"), out)
		if not my:
			if b1 >= 1:
				out.append("Free Market: your first market in this action costs nothing")
			if b1 >= 2:
				if is_robots(pid):
					p.rbk_free = int(p.get("rbk_free", 0)) + 1
					out.append("Free Barracks: your next factory barracks is free")
				else:
					out.append("Free Barracks: your first barracks in this action costs nothing")
			if b2 >= 1:
				out.append("Cheap Markets: markets cost 1 gold less")
			if b2 >= 2:
				if is_robots(pid):
					p.rbk_off = turn
					out.append("Cheap Barracks: factory barracks cost 1 material less this turn")
				else:
					out.append("Cheap Barracks: barracks cost 1 material less")
			if b2 >= 3:
				out.append("Market Day: every market you own makes 1 gold at the end of this action")
			if b4 >= 1:
				out.append("Relocate: you can move one of your buildings to a hex of yours next door")
		elif b1 >= 1:
			out.append("Quick Roots: a Mage that plants a Life Tree in this action stays 1 turn instead of 2")
	if a == "advance":
		var v1: int = nu_k(pid, 1, "advance")
		var v2: int = nu_k(pid, 2, "advance")
		var v4: int = nu_k(pid, 4, "advance")
		if v1 >= 1:
			if my:
				_nu_gain(pid, 8 if v1 >= 3 else (3 if v1 >= 2 else 1), 0, _nu_name(a, v1 - 1, "Stores"), out)
			else:
				_nu_gain(pid, 10 if v1 >= 3 else (5 if v1 >= 2 else 0), 4 if v1 >= 3 else 2, _nu_name(a, v1 - 1, "Stores"), out)
		if not bool(p.ai):
			if v2 >= 1:
				out.append("Border Claim: you can claim one empty, open hex on your border")
			if v2 >= 2:
				out.append("Early Harvest: you can take a Harvest now (your next Harvest then gives nothing)")
			if v4 >= 2:
				out.append("Rally Cry: you can give one of your armies +10% health until the end of your next turn")
			if v4 >= 3:
				out.append("Freeze: you can freeze one enemy army for its next %d turns" % NU_FREEZE)
		if v2 >= 3 and not my:
			out.append("Free Upgrade: your first barracks upgrade in this action is free")
	if a == "recruit":
		var r2: int = nu_k(pid, 2, "recruit")
		var r3: int = nu_k(pid, 3, "recruit")
		var bas: String = basic_of(pid)
		var got: Array = []
		if r2 >= 1 and hold:
			add_units(int(home.id), bas, 1, true)
			got.append("1 %s at your home castle" % GameData.units[bas].name)
		if r2 >= 2 and not my:
			var n: int = 0
			for t in tiles:
				if int(t.owner) == pid and int(t.barracks) > 0:
					add_units(int(t.id), bas, int(t.barracks), true)
					n += int(t.barracks)
			if n > 0:
				got.append("%d %s at your barracks" % [n, GameData.units[bas].name])
		if r2 >= 3:
			var k: String = String(NU_SET.get(f, bas))
			if my:
				if hold:
					add_units(int(home.id), k, 1, true)
					got.append("1 %s at your home castle" % GameData.units[k].name)
			else:
				var n2: int = 0
				for t in tiles:
					if int(t.owner) == pid and int(t.barracks) > 0:
						add_units(int(t.id), k, int(t.barracks), true)
						n2 += int(t.barracks)
				if n2 > 0:
					got.append("%d %s at your barracks" % [n2, GameData.units[k].name])
		if r3 >= 1 and hold:
			var nm: int = int(NU_MUSTER[r3])
			add_units(int(home.id), bas, nm, true)
			got.append("%d %s at your home castle" % [nm, GameData.units[bas].name])
		if not got.is_empty():
			out.append("Free units: " + ", ".join(PackedStringArray(got)))
			add_log("%s get free units: %s." % [p.name, ", ".join(PackedStringArray(got)).replace("your", "their")])
	return out


## Market Day (card 2 Build, level 3): every market pays 1 gold as the Build ends.
func nu_action_end(pid: int) -> void:
	if not new_ups() or play.is_empty():
		return
	if not play.has("nu_e"):
		play.nu_e = {}
	var key: String = str(int(play.step))
	if play.nu_e.has(key) or card_action() != "build" or fx_on() or nu_k(pid, 2, "build") < 3 or is_myth(pid):
		return
	play.nu_e[key] = true
	var g: int = 0
	for t in tiles:
		if int(t.owner) == pid:
			g += int(t.market)
	if g > 0:
		players[pid].gold = int(players[pid].gold) + g
		add_log("%s get %d gold from their markets (Market Day)." % [players[pid].name, g])


## A Harvest's extra: card 4 (gold and materials from land) and card 5 (materials). {g, m, why}
func nu_harvest(pid: int) -> Dictionary:
	var o: Dictionary = {"g": 0, "m": 0, "why": []}
	if not new_ups():
		return o
	var my: bool = is_myth(pid)
	var hexes: int = 0
	for t in tiles:
		if int(t.owner) == pid:
			hexes += 1
	var h4: int = nu_k(pid, 4, "harvest")
	var h5: int = nu_k(pid, 5, "harvest")
	if not my and h4 >= 1:
		var g: int = hexes * (2 if h4 >= 3 else 1)
		o.g += g
		o.why.append("%s %d" % ["Richer Land" if h4 >= 3 else "Rich Land", g])
	if not my and h4 >= 2:
		var m: int = hexes / 3
		o.m += m
		if m > 0:
			o.why.append("Quarry %s" % mat_txt(m))
	if h5 >= 1:
		if my:
			o.g += int(NU_HARV_MY[h5])
			o.why.append("Stockpile %d magic" % int(NU_HARV_MY[h5]))
		else:
			o.m += int(NU_HARV_M[h5])
			o.why.append("Stockpile %s" % mat_txt(int(NU_HARV_M[h5])))
	return o


## Every turn: captured castles (card 5 Advancements); the Mythical's home castle and trees (card 4 Harvest).
func nu_income(pid: int) -> int:
	if not new_ups():
		return 0
	var my: bool = is_myth(pid)
	var c5: int = nu_lv(pid, 5, "advance")
	var g: int = cap_castles_of(pid) * int((NU_CASTLE_MY if my else NU_CASTLE)[c5])
	if my:
		var h4: int = nu_lv(pid, 4, "harvest")
		if not myth_home(pid).is_empty():
			g += 3 if h4 >= 2 else (1 if h4 >= 1 else 0)
		if h4 >= 3:
			g += trees_of(pid)
	return g


## A Fortify's start: Border Guard and Border Wall (card 5).
func nu_fortify(pid: int) -> Array:
	var f5: int = nu_k(pid, 5, "fortify")
	if f5 < 2:
		return []
	var n: int = 2 if f5 >= 3 else 1
	var bas: String = basic_of(pid)
	var hexes: Array = []
	for t in tiles:
		if int(t.owner) != pid or t.terrain == "water":
			continue
		for j in HexGrid.neighbors(int(t.id)):
			if int(tiles[j].owner) >= 0 and int(tiles[j].owner) != pid:
				hexes.append(int(t.id))
				break
	for i in hexes:
		add_units(i, bas, n, true)
	if hexes.is_empty():
		return ["Border Guard: no hex of yours touches an enemy yet"]
	add_log("%s get %d free %s on each of their %d border hexes." % [players[pid].name, n, GameData.units[bas].name, hexes.size()])
	return ["%s: +%d %s on %d border hex%s" % ["Border Wall" if n == 2 else "Border Guard", n, GameData.units[bas].name, hexes.size(), "" if hexes.size() == 1 else "es"]]


## Border Claim's hexes: empty, open, unowned land next to yours (not a castle).
func nu_claimable(pid: int) -> Array[int]:
	var out: Array[int] = []
	for t in tiles:
		if int(t.owner) != -1 or int(t.troops) > 0 or t.terrain != "plain" or t.castle:
			continue
		for j in HexGrid.neighbors(int(t.id)):
			if int(tiles[j].owner) == pid:
				out.append(int(t.id))
				break
	return out


func nu_claim(pid: int, i: int) -> bool:
	if nu_k(pid, 2, "advance") < 1 or bool(play.get("n_cl", false)) or not nu_claimable(pid).has(i):
		return false
	var t: Dictionary = tiles[i]
	var p: Dictionary = players[pid]
	t.owner = pid
	t.army = {}
	t.ready = {}
	sync_tile(t)
	t.braced = -1
	play.n_cl = true
	if t.get("crate", false):
		t.crate = false
		if not is_myth(pid):
			p.mat = mat_of(pid) + int(GameData.rules.crate.materials)
	if t.bounty:
		t.bounty = false
		if not is_myth(pid):
			p.gold = int(p.gold) + int(GameData.rules.coin.gold)
	add_log("%s claim a hex on their border (Border Claim)." % p.name)
	check_castles()
	return true


## Early Harvest (card 2 Advancements, level 2): a Harvest now; the next Harvest gives nothing.
func nu_early(pid: int) -> bool:
	var home: Dictionary = tiles[homes[pid]]
	if nu_k(pid, 2, "advance") < 2 or bool(play.get("n_eh", false)) or int(home.owner) != pid:
		return false
	play.n_eh = true
	var was_step: int = int(play.step)
	_nu_harvest_now = true
	_resolve_instant("harvest")
	_nu_harvest_now = false
	play.step = was_step
	players[pid].no_harv = turn + 1
	add_log("%s take their next Harvest early (Early Harvest)." % players[pid].name)
	return true
var _nu_harvest_now: bool = false


func nu_buff(pid: int, i: int) -> bool:
	var t: Dictionary = tiles[i]
	if nu_k(pid, 4, "advance") < 2 or bool(play.get("n_bf", false)) or int(t.owner) != pid or int(t.troops) <= 0:
		return false
	t.buff = {"pid": pid, "until": turn + 1}
	play.n_bf = true
	add_log("%s rally an army: +10%% health until the end of their next turn (Rally Cry)." % players[pid].name)
	return true


func nu_freezable(pid: int) -> Array[int]:
	var out: Array[int] = []
	for t in tiles:
		if int(t.owner) >= 0 and int(t.owner) != pid and int(t.troops) > 0:
			out.append(int(t.id))
	return out


func nu_freeze(pid: int, i: int) -> bool:
	if nu_k(pid, 4, "advance") < 3 or bool(play.get("n_fz", false)) or not nu_freezable(pid).has(i):
		return false
	var t: Dictionary = tiles[i]
	t.frz = NU_FREEZE
	play.n_fz = true
	add_log("%s freeze an army of the %s: it can't move for %d turns (Freeze)." % [players[pid].name, players[int(t.owner)].name, NU_FREEZE])
	return true


## Relocate (card 4 Build): one building moves to a hex of yours next door (a Robot factory moves whole).
func nu_movable(pid: int, t: Dictionary) -> Array:
	if t.is_empty() or int(t.owner) != pid:
		return []
	if is_robots(pid):
		return ["factory"] if building_count(t) > 0 and not t.castle else []
	var out: Array = []
	for k in ["market", "barracks", "fort", "wh"]:
		if int(t.get(k, 0)) > 0:
			out.append(k)
	return out


func nu_move_spots(pid: int, from: int, k: String) -> Array[int]:
	var out: Array[int] = []
	for j in HexGrid.neighbors(from):
		var b: Dictionary = tiles[j]
		if int(b.owner) != pid or b.terrain != "plain":
			continue
		if k == "factory":
			if not b.castle and building_count(b) == 0:
				out.append(j)
			continue
		if (k == "barracks" or k == "fort") and b.castle:
			continue
		if k == "wh" and int(b.get("wh", 0)) > 0:
			continue
		if building_count(b) < int(GameData.rules.buildings.max_per_hex):
			out.append(j)
	return out


func nu_move_b(pid: int, from: int, k: String, to: int) -> bool:
	if nu_k(pid, 4, "build") < 1 or bool(play.get("n_mb", false)) or not nu_movable(pid, tiles[from]).has(k) or not nu_move_spots(pid, from, k).has(to):
		return false
	var a: Dictionary = tiles[from]
	var b: Dictionary = tiles[to]
	if k == "factory":
		for x in ["market", "barracks", "fort", "bk", "wh"]:
			b[x] = int(a.get(x, 0))
			a[x] = 0
	else:
		a[k] = int(a[k]) - 1
		b[k] = int(b.get(k, 0)) + 1
		if k == "barracks":
			var lv: int = int(a.bk)
			if int(a.barracks) == 0:
				a.bk = 0
			b.bk = maxi(int(b.bk), lv)
	play.n_mb = true
	add_log("%s move a %s to the hex next door (Relocate)." % [players[pid].name, "factory" if k == "factory" else ("Watering Hole" if k == "wh" else k)])
	return true


func _nu_dist(sources: Array) -> Dictionary:
	var d: Dictionary = {}
	var q: Array = []
	for s in sources:
		d[int(s)] = 0
		q.append(int(s))
	var h: int = 0
	while h < q.size():
		var c: int = q[h]
		h += 1
		for n in HexGrid.neighbors(c):
			if not d.has(n) and tiles[n].terrain != "water" and tiles[n].terrain != "void":
				d[n] = int(d[c]) + 1
				q.append(n)
	return d


## The computer's Advancements powers: claim, rally its army nearest the enemy, freeze the biggest enemy army near it.
func nu_ai_advance(pid: int) -> Array:
	var ids: Array = []
	if not new_ups() or play.is_empty():
		return ids
	var foes: Array = []
	var mine: Array = []
	for t in tiles:
		if int(t.owner) >= 0 and int(t.owner) != pid:
			foes.append(int(t.id))
		elif int(t.owner) == pid:
			mine.append(int(t.id))
	var dE: Dictionary = _nu_dist(foes)
	if nu_k(pid, 2, "advance") >= 1 and not bool(play.get("n_cl", false)):
		var best: int = -1
		var bv: float = -INF
		for i in nu_claimable(pid):
			var v: float = float(dE.get(i, 99)) + (100.0 if (tiles[i].bounty or tiles[i].get("crate", false)) else 0.0)
			if v > bv:
				bv = v
				best = i
		if best >= 0 and nu_claim(pid, best):
			ids.append(best)
	if nu_k(pid, 4, "advance") >= 2 and not bool(play.get("n_bf", false)):
		var best2: int = -1
		var bv2: float = INF
		for i in mine:
			if int(tiles[i].troops) <= 0:
				continue
			var v2: float = float(dE.get(i, 99)) * 1000.0 - int(tiles[i].troops)
			if v2 < bv2:
				bv2 = v2
				best2 = i
		if best2 >= 0 and nu_buff(pid, best2):
			ids.append(best2)
	if nu_k(pid, 4, "advance") >= 3 and not bool(play.get("n_fz", false)):
		var dO: Dictionary = _nu_dist(mine)
		var best3: int = -1
		var most: int = 0
		for i in nu_freezable(pid):
			if int(dO.get(i, 99)) <= 2 and int(tiles[i].troops) > most:
				most = int(tiles[i].troops)
				best3 = i
		if best3 >= 0 and nu_freeze(pid, best3):
			ids.append(best3)
	return ids

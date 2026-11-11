# Godot port, step 2: game_state.gd (materials, Fortify as a wild card, the Dinosaur cards' own upgrades, Armor,
# planting after a move). Mirrors the browser version 136 (repo commits 09864e4 .. c8c8bfc).
import sys
F = sys.argv[1] + '/scripts/rules/game_state.gd'
s = open(F, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        print('COUNT', n, 'for', old[:160]); sys.exit(1)
    s = s.replace(old, new)

# ---------------- new players ----------------
rep('''			"volc": {},   # Dinosaurs: the home castle's volcano, {lv, cd} once woken
		})''', '''			"volc": {},   # Dinosaurs: the home castle's volcano, {lv, cd} once woken
			"mat": 0,     # materials in store (bought at markets; pay for forts, barracks, upgrades, walls, trebuchets)
			"tr": 0,      # materials bought this turn
			"fnest": 0,   # Dinosaurs (New Nest): free barracks still to build
			"armor": false,   # Dinosaurs (The Hunt): Armor forged
		})''')

# ---------------- levels: a Fortify plays at the basic level; the Dinosaurs use their cards' own upgrades ----------------
rep('''func cur_action() -> String:
	if play.is_empty():
		return ""
	return String(card_of(current, play.card).actions[int(play.step)])


## The current action's real upgrade level, 0 to 3.
func raw_lvl() -> int:
	if play.is_empty():
		return 0
	return lvl_of(current, play.card, int(play.step))


## The level the usual upgrade tables use. Both factions replace level 1 with a named ability,
## so a named level 1 counts as 0 here.
func cur_lvl() -> int:
	var raw: int = raw_lvl()
	return 0 if raw == 1 else raw


## True when the current action's named faction ability is active (level 1 or higher).
func named_on() -> bool:
	return raw_lvl() >= 1''', '''## The action printed on the card at the current step.
func card_action() -> String:
	if play.is_empty():
		return ""
	return String(card_of(current, play.card).actions[int(play.step)])


## The action being played now. Inside a Fortify, the regroup plays as a Move and each pick as its own action.
func cur_action() -> String:
	var a: String = card_action()
	if a != "fortify" or not fx_on():
		return a
	var f: Dictionary = play.fx
	if f.ph == "regroup":
		return "move"
	if f.ph == "act":
		return String(f.cur)
	return "fortify"


## The current action's real upgrade level, 0 to 3 (a Fortify's regroup and picks play at the basic level).
func raw_lvl() -> int:
	if play.is_empty() or fx_on():
		return 0
	return lvl_of(current, play.card, int(play.step))


## The level the usual upgrade tables use. The Robots and Mammals replace level 1 with a named ability,
## so a named level 1 counts as 0 here. The Dinosaurs' cards have their own upgrades (dk), so their usual level
## stays 0, except Siege of Teeth's Climb, which plays as a mountain-climbing Move.
func cur_lvl() -> int:
	if play.is_empty():
		return 0
	if is_dinos(current):
		return 1 if dk(current, "siege", "move") >= 1 else 0
	var raw: int = raw_lvl()
	return 0 if raw == 1 else raw


## True when the current action's named faction ability is active (level 1 or higher). The Dinosaurs' old abilities
## (Herd, Migrate, Nesting, Populate, Abundance, Rainy Season) are retired.
func named_on() -> bool:
	if play.is_empty() or is_dinos(current):
		return false
	return raw_lvl() >= 1


# =====================================================================
# The Dinosaur cards' own upgrades (Ethan, 2026-11-11). dk = the level of that card's action while it is being played
# (0 when it isn't that card and action).
# =====================================================================

func dk(pid: int, cid: String, a: String) -> int:
	if play.is_empty() or current != pid or not is_dinos(pid) or String(play.card) != cid or card_action() != a:
		return 0
	return lvl_of(pid, cid, int(play.step))


func dcard(cid: String, a: String) -> Array:
	return GameData.upgrades.get("dinos_cards", {}).get(cid, {}).get(a, [])


## Does this Dinosaur card's action have its own upgrades?
func d_up(pid: int, cid: String, a: String) -> bool:
	return is_dinos(pid) and not dcard(cid, a).is_empty()


func armor_on(pid: int) -> bool:
	return pid >= 0 and pid < players.size() and bool(players[pid].get("armor", false))


func armor_rules() -> Dictionary:
	return GameData.rules.dinos.armor


func unit_total(pid: int) -> int:
	var n: int = 0
	for t in tiles:
		if int(t.owner) == pid:
			n += int(t.troops)
	return n


## A Dinosaur Harvest's card upgrades: extra gold and materials.
func dino_harvest(pid: int) -> Dictionary:
	var mk: int = 0
	var cs: int = 0
	var nests: int = 0
	var own: int = 0
	for t in tiles:
		if int(t.owner) == pid:
			own += 1
			mk += int(t.market)
			nests += int(t.barracks)
			if t.castle:
				cs += 1
	var g: int = 0
	var m: int = 0
	var why: Array = []
	var pk: int = dk(pid, "pack", "harvest")
	var hu: int = dk(pid, "hunt", "harvest")
	var si: int = dk(pid, "siege", "harvest")
	var ne: int = dk(pid, "nest", "harvest")
	if pk >= 1:
		g += mk
		why.append("Trade Calls +%d" % mk)
	if pk >= 2:
		g += 5 * cs
		why.append("Castle Tolls +%d" % (5 * cs))
	if pk >= 3:
		var x: int = 2 * (unit_total(pid) / 5)
		g += x
		why.append("Big Herd +%d" % x)
	if hu >= 1:
		var x: int = own - own / 2
		g += x
		why.append("Hunting Grounds +%d" % x)
	if hu >= 2:
		g += 2 * nests
		why.append("Nest Feast +%d" % (2 * nests))
	if hu >= 3:
		g += 5 * cs
		why.append("Castle Feast +%d" % (5 * cs))
	if si >= 1:
		var x: int = own / (2 if si >= 2 else 3)
		m += x
		why.append("%s +%s" % ["Big Quarry" if si >= 2 else "Quarry", mat_txt(x)])
	if si >= 3:
		m += cs
		why.append("Castle Stores +%s" % mat_txt(cs))
	if ne >= 1:
		var x: int = 10 if ne >= 3 else (5 if ne >= 2 else 3)
		m += x
		why.append("%s +%s" % ["Great Store" if ne >= 3 else ("Stockpile" if ne >= 2 else "Gathering"), mat_txt(x)])
	return {"g": g, "m": m, "why": why}


## A Dinosaur Build's or Recruit's card upgrades that happen when it starts. Returns notes for the card column.
func dino_action_start(pid: int) -> Array:
	var out: Array = []
	if not is_dinos(pid) or play.is_empty():
		return out
	var a: String = card_action()
	var p: Dictionary = players[pid]
	if a == "build":
		if dk(pid, "stamp", "build") >= 2:
			p.mat = mat_of(pid) + 2
			out.append("Supplies: +2 materials")
		if dk(pid, "nest", "build") >= 3:
			p.fnest = int(p.get("fnest", 0)) + 1
			out.append("New Nest: your next barracks is free")
		if dk(pid, "stamp", "build") >= 1:
			out.append("Free Market: your first market in this action costs nothing")
	if a == "recruit":
		var home: Dictionary = tiles[homes[pid]]
		if dk(pid, "hunt", "recruit") >= 2:
			var n: int = 0
			for t in tiles:
				if int(t.owner) == pid and t.castle:
					add_units(int(t.id), "galli", 2, true)
					n += 2
			if n > 0:
				out.append("Castle Herds: +%d Pachycephalosaurus at your castles" % n)
				add_log("%s get %d free Pachycephalosaurus at their castles." % [p.name, n])
		if dk(pid, "pack", "recruit") >= 3 and int(home.owner) == pid:
			add_units(int(home.id), "mega", 2, true)
			out.append("Castle Raptors: +2 Megaraptors at your home castle")
			add_log("%s get 2 free Megaraptors at their home castle." % p.name)
		var pk: int = dk(pid, "pack", "recruit")
		if pk >= 1:
			var got: Dictionary = {"galli": 3}
			if pk >= 2:
				got["mega"] = 1
			var nests: Array = tiles.filter(func(t): return int(t.owner) == pid and int(t.barracks) > 0)
			if nests.is_empty():
				if int(home.owner) == pid:
					_add_army(int(home.id), got, true)
					out.append("Calling: no nesting ground yet, so the free units wait at your home castle")
			elif bool(p.ai) or nests.size() == 1:
				var d_e: Array = _foe_dist(pid)
				nests.sort_custom(func(x, y): return float(d_e[int(x.id)]) < float(d_e[int(y.id)]))
				_add_army(int(nests[0].id), got, true)
				out.append("Calling: free units at a nesting ground")
			else:
				play.dpick = got
				out.append("Calling: tap one of your nesting grounds for the free units")
			add_log("%s call %s to a nesting ground." % [p.name, "3 Pachycephalosaurus and a Megaraptor" if pk >= 2 else "3 Pachycephalosaurus"])
	return out


## Hex steps from every hex to the nearest enemy hex (999 when none can be reached).
func _foe_dist(pid: int) -> Array:
	var d: Array = []
	d.resize(tiles.size())
	d.fill(999.0)
	var q: Array = []
	for t in tiles:
		if int(t.owner) >= 0 and int(t.owner) != pid:
			d[int(t.id)] = 0.0
			q.append(int(t.id))
	while not q.is_empty():
		var c: int = q.pop_front()
		for n in HexGrid.neighbors(c):
			if tiles[n].terrain == "plain" and float(d[n]) > float(d[c]) + 1.0:
				d[n] = float(d[c]) + 1.0
				q.append(n)
	return d


## Calling (Pack Call): the free units go to the nesting ground the player taps.
func place_dpick(i: int) -> bool:
	var t: Dictionary = tiles[i]
	if play.is_empty() or not (play.get("dpick") is Dictionary) or play.dpick.is_empty() or int(t.owner) != current or int(t.barracks) == 0:
		return false
	_add_army(i, play.dpick, true)
	play.dpick = {}
	return true


func dpick_waiting() -> bool:
	return not play.is_empty() and play.get("dpick") is Dictionary and not play.dpick.is_empty()


## A Dinosaur Build's price changes: Free Market (Stampede), Cheap Markets and Market Row (Nesting Season),
## New Nest (the next barracks is free) and Cheap Nests (Stampede: every building 1 cheaper).
func dino_cost(pid: int, k: String, c: int, t: Dictionary) -> int:
	var st: int = dk(pid, "stamp", "build")
	var ne: int = dk(pid, "nest", "build")
	if k == "market":
		if st >= 1 and not bool(play.get("free_mk", false)):
			return 0
		if ne >= 1:
			c -= 1
		if ne >= 2 and not t.is_empty() and int(t.market) >= 1:
			c -= 1
		if st >= 3:
			c -= 1
		return maxi(0, c)
	if k == "barracks" and int(players[pid].get("fnest", 0)) > 0:
		return 0
	if st >= 3:
		c -= 1
	return maxi(0, c)


func _dino_built(pid: int, k: String, price: int) -> void:
	if not is_dinos(pid) or price > 0 or play.is_empty():
		return
	var p: Dictionary = players[pid]
	if k == "market" and dk(pid, "stamp", "build") >= 1 and not bool(play.get("free_mk", false)):
		play.free_mk = true
	elif k == "barracks" and int(p.get("fnest", 0)) > 0:
		p.fnest = int(p.fnest) - 1


func bk_up_cost(pid: int, lv: int) -> int:
	return int(GameData.rules.buildings.barracks_upgrade_cost[lv]) - (1 if dk(pid, "hunt", "advance") >= 1 else 0)   # Quick Nests


## Armor (The Hunt, Advancements level 3): bought at the home castle.
func do_armor(pid: int) -> bool:
	var p: Dictionary = players[pid]
	var h: Dictionary = tiles[homes[pid]]
	var cost: int = int(armor_rules().cost)
	if not is_dinos(pid) or armor_on(pid) or int(h.owner) != pid or dk(pid, "hunt", "advance") < 3 or int(p.gold) < cost:
		return false
	p.gold = int(p.gold) - cost
	p.armor = true
	add_log("%s forge Armor: all their units get +%d damage and +10%% health." % [p.name, int(armor_rules().dmg)])
	return true


func can_armor(pid: int) -> bool:
	return is_dinos(pid) and dk(pid, "hunt", "advance") >= 3 and int(tiles[homes[pid]].owner) == pid


# =====================================================================
# Materials (Ethan, 2026-11-10): each market sells up to 3 a turn and the home castle counts as one, 2 gold each, any time
# on your turn. Forts, barracks, barracks upgrades, walls, trebuchets and Watering Holes are paid with them.
# =====================================================================

func mat_price() -> int:
	return int(GameData.rules.materials.price)


func mat_txt(n: int) -> String:
	return "%d material%s" % [n, "" if n == 1 else "s"]


func uses_mat(pid: int) -> bool:
	return pid >= 0 and pid < players.size() and not is_myth(pid)


func mat_of(pid: int) -> int:
	return int(players[pid].get("mat", 0))


func in_mat(k: String) -> bool:
	return k != "market"


func markets_of(pid: int) -> int:
	var n: int = 0
	for t in tiles:
		if int(t.owner) == pid:
			n += int(t.market)
	return n


func home_market(pid: int) -> bool:
	return int(tiles[homes[pid]].owner) == pid


## How many materials a side's markets sell it each turn: 3 for every market, and 3 more while it holds its home castle.
func mat_cap(pid: int) -> int:
	if not uses_mat(pid):
		return 0
	return int(GameData.rules.materials.per_market) * (markets_of(pid) + (1 if home_market(pid) else 0))


func mat_left(pid: int) -> int:
	return maxi(0, mat_cap(pid) - int(players[pid].get("tr", 0)))


## Buys up to n materials (as many as the markets and the gold allow). Returns how many it bought.
func buy_mat(pid: int, n: int) -> int:
	var p: Dictionary = players[pid]
	n = mini(n, mini(mat_left(pid), int(p.gold) / mat_price()))
	if n < 1:
		return 0
	p.gold = int(p.gold) - n * mat_price()
	p.mat = mat_of(pid) + n
	p.tr = int(p.get("tr", 0)) + n
	add_log("%s buy %s at the market for %d gold." % [p.name, mat_txt(n), n * mat_price()])
	return n


func spend_mat(pid: int, n: int) -> void:
	players[pid].mat = maxi(0, mat_of(pid) - n)


## Pay for a building: markets in gold, the rest in materials.
func can_pay_b(pid: int, k: String, n: int) -> bool:
	return mat_of(pid) >= n if in_mat(k) else int(players[pid].gold) >= n


func pay_b(pid: int, k: String, n: int) -> void:
	if in_mat(k):
		spend_mat(pid, n)
	else:
		players[pid].gold = int(players[pid].gold) - n


## Materials a side could have now: what it holds plus what its markets can still sell it, keeping "keep" gold back.
func mat_reach(pid: int, keep: int = 0) -> int:
	return mat_of(pid) + mini(mat_left(pid), maxi(0, (int(players[pid].gold) - keep) / mat_price()))


## The computer buys the materials it's short of (all or nothing), keeping "keep" gold back.
func ai_mat(pid: int, need: int, keep: int = 0) -> bool:
	var short: int = need - mat_of(pid)
	if short <= 0:
		return true
	if mat_reach(pid, keep) < need:
		return false
	buy_mat(pid, short)
	return mat_of(pid) >= need


## The gold a purchase of "mats" materials would still take, after what's already in store.
func gold_for(pid: int, mats: int) -> int:
	return maxi(0, mats - mat_of(pid)) * mat_price()


## The computer: affordable, counting the materials it can buy.
func can_b(pid: int, k: String, n: int, keep: int = 0) -> bool:
	return mat_reach(pid, keep) >= n if in_mat(k) else int(players[pid].gold) - keep >= n


# =====================================================================
# Fortify is a wild card (Ethan, 2026-11-10). First a regroup: units move up to 2 hexes between the player's own hexes,
# as often as they like (no attacks or claiming), and stay ready to move again. Then the player picks Build,
# Advancements or Recruit (two of them at level 2, all three at level 3), each played like the basic action.
# While it runs, play.fx = {ph: "regroup" | "pick" | "act", n: picks allowed, done: picks made, cur: the pick being played,
# far: Join Up moves left, mv: Move is a pick, rally: Rally left}.
# =====================================================================

const REGROUP_MOVES := 99

func fx_on() -> bool:
	return not play.is_empty() and play.get("fx") is Dictionary and not play.fx.is_empty() and card_action() == "fortify"


func regrouping() -> bool:
	return fx_on() and String(play.fx.ph) == "regroup"


func regroup_reach() -> int:
	return int(GameData.rules.fortify.regroup_reach)


func fx_reach() -> int:
	return 99 if (fx_on() and int(play.fx.get("far", 0)) > 0) else regroup_reach()


func fx_pick_list() -> Array:
	var out: Array = GameData.rules.fortify.picks.duplicate()
	if fx_on() and bool(play.fx.get("mv", false)):
		out.append("move")
	return out


## How many picks a Fortify at this upgrade level gets (the Dinosaurs' Fortify upgrades are their cards' own).
func fx_picks_at(pid: int, raw: int) -> int:
	var eff: int = 0 if (is_dinos(pid) or raw == 1) else raw
	return 3 if eff >= 3 else (2 if eff >= 1 else 1)


## A Fortify's regroup: your own open hexes (not mountains) within maxd steps through your own land.
func regroup_targets(from: int, maxd: int = -1) -> Array[int]:
	var pid: int = int(tiles[from].owner)
	if maxd < 0:
		maxd = regroup_reach()
	var seen: Dictionary = {from: true}
	var fr: Array[int] = [from]
	var out: Array[int] = []
	var d: int = 0
	while not fr.is_empty() and d < maxd:
		d += 1
		var nx: Array[int] = []
		for c in fr:
			for n in HexGrid.neighbors(c):
				if not seen.has(n) and _own_road(n, pid):
					seen[n] = true
					nx.append(n)
					out.append(n)
		fr = nx
	return out


## A Fortify starts with its faction ability (the Mammals' Mating, the Robots' Update) and the Dinosaur card's upgrades.
## Returns notes for the card column.
func fortify_start(pid: int, raw: int) -> Array:
	var p: Dictionary = players[pid]
	var out: Array = []
	if is_mammals(pid) and raw >= 1:
		var ids: Array = _mating(pid)
		out.append("Mating: young born on %d hex%s" % [ids.size(), "" if ids.size() == 1 else "es"] if not ids.is_empty() else "Mating: no pairs to breed yet")
	if is_robots(pid) and raw >= 1:
		p.upd_next = true
		add_log("%s run an Update: +1 attack and +1 damage on their next turn." % p.name)
		out.append("Update: +1 attack and +1 damage on %s next turn" % ("your" if pid == 0 else "their"))
	if is_dinos(pid) and not play.is_empty():
		out.append_array(_dino_fortify(pid, raw))
	var n: int = fx_picks_at(pid, raw)
	add_log("%s fortify: a regroup, then %s." % [p.name, "Build, Advancements and Recruit" if n >= 3 else ("two of Build, Advancements and Recruit" if n == 2 else "Build, Advancements or Recruit")])
	return out


## Sets up play.fx for the Fortify at the current step.
func fx_begin(pid: int) -> Array:
	var raw: int = lvl_of(pid, play.card, int(play.step))
	var notes_out: Array = fortify_start(pid, raw)
	var l: int = dk(pid, "pack", "fortify")
	play.fx = {"ph": "regroup", "n": fx_picks_at(pid, raw), "done": [], "cur": "",
		"far": 1 if l >= 1 else 0, "mv": l >= 2, "rally": 1 if l >= 3 else 0}
	play.moves = 0
	return notes_out


## A Dinosaur Fortify's card upgrades.
func _dino_fortify(pid: int, raw: int) -> Array:
	var cid: String = String(play.card)
	var p: Dictionary = players[pid]
	var out: Array = []
	var nests: Array = tiles.filter(func(t): return int(t.owner) == pid and int(t.barracks) > 0)
	if cid == "stamp":
		if raw >= 1 and not nests.is_empty():
			for t in nests:
				add_units(int(t.id), "galli", int(t.barracks), true)
			out.append("Hatchlings: +1 Pachycephalosaurus at each nesting ground")
		if raw >= 2 and not nests.is_empty():
			for t in nests:
				add_units(int(t.id), "mega", int(t.barracks), true)
			out.append("Raptor Brood: +1 Megaraptor at each nesting ground")
		if raw >= 3:
			p.fnest = int(p.get("fnest", 0)) + 1
			out.append("New Nest: your next barracks is free")
		if raw >= 1:
			add_log("%s hatch new dinosaurs at their nesting grounds." % p.name)
	elif cid == "siege":
		if raw >= 1:
			var best: Dictionary = {}
			for t in tiles:
				if int(t.owner) == pid and int(t.market) > 0 and (best.is_empty() or int(t.market) > int(best.market)):
					best = t
			if not best.is_empty():
				var g: int = 2 * int(best.market)
				p.gold = int(p.gold) + g
				out.append("Market Day: +%d gold" % g)
				add_log("%s hold a market day: +%d gold." % [p.name, g])
		var free: int = 2 if raw >= 3 else (1 if raw >= 2 else 0)
		if free > 0:
			var d_e: Array = _foe_dist(pid)
			var got: int = 0
			for k in free:
				var c: Array = nests.filter(func(x): return guards_at(x) < guard_max(x))
				if c.is_empty():
					break
				c.sort_custom(func(x, y): return float(d_e[int(x.id)]) < float(d_e[int(y.id)]))
				add_units(int(c[0].id), "alamo", 1, false)
				got += 1
			if got > 0:
				out.append("Guardian: +%d free Alamosaurus guard%s" % [got, "s" if got > 1 else ""])
				add_log("%s get %d free Alamosaurus guard%s." % [p.name, got, "s" if got > 1 else ""])
	elif cid == "nest" and raw >= 1:
		var got2: Dictionary = {"galli": 2, "mega": 1} if raw >= 3 else {"galli": 3 if raw >= 2 else 1}
		var cs: Array = tiles.filter(func(t): return int(t.owner) == pid and t.castle and int(t.id) != homes[pid])
		for t in cs:
			_add_army(int(t.id), got2, true)
		var nm: String = "Castle Guard" if raw >= 3 else ("Castle Brood" if raw >= 2 else "Castle Hatch")
		out.append(("%s: new dinosaurs at each captured castle" % nm) if not cs.is_empty() else "%s: no captured castles yet" % nm)
		if not cs.is_empty():
			add_log("%s send new dinosaurs to their %d captured castle%s." % [p.name, cs.size(), "s" if cs.size() > 1 else ""])
	return out


## The human picks what their Fortify does next.
func fx_choose(k: String) -> bool:
	if not fx_on() or String(play.fx.ph) != "pick" or not fx_pick_list().has(k) or play.fx.done.has(k):
		return false
	if play.fx.done.size() >= int(play.fx.n):
		return false
	play.fx.ph = "act"
	play.fx.cur = k
	play.free_walls = 0   # no Reforest walls left over from an earlier action
	if k == "move":
		play.moves = 0
	return true


## A Fortify's phases: the regroup, then the picks one at a time. True while the Fortify goes on.
func fx_next() -> bool:
	if not fx_on():
		return false
	var f: Dictionary = play.fx
	if f.ph == "regroup":
		f.ph = "pick"
		play.moves = 0
		return true
	if f.ph == "act":
		f.done.append(f.cur)
		f.cur = ""
		if f.done.size() < int(f.n) and fx_pick_list().any(func(k): return not f.done.has(k)):
			f.ph = "pick"
			return true
	play.fx = {}
	return false


## Does the main button end the turn? (not while a Fortify still has its picks to come)
func last_step_now() -> bool:
	if play.is_empty():
		return false
	if fx_on():
		var f: Dictionary = play.fx
		if f.ph == "regroup" or (f.ph == "act" and f.done.size() + 1 < int(f.n)):
			return false
	return int(play.step) >= card_of(current, play.card).actions.size() - 1


## Rally (Pack Call): every ready unit you have, from anywhere in your land, comes to one hex.
func rally_to(i: int) -> int:
	if not regrouping() or int(play.fx.get("rally", 0)) <= 0 or int(tiles[i].owner) != current:
		return 0
	var n: int = 0
	for t in tiles:
		if int(t.owner) != current or int(t.id) == i or int(t.fresh) <= 0:
			continue
		var sel: Dictionary = t.ready.duplicate()
		sel.erase("alamo")
		var m: int = _count(sel)
		if m == 0:
			continue
		take_units(int(t.id), sel)
		_add_army(i, sel, true)
		n += m
	play.fx.rally = 0
	add_log("%s rally %d unit%s to one hex." % [players[current].name, n, "" if n == 1 else "s"])
	return n


## Two Herds (Stampede Move level 3): your hex next to the attack target with the most ready units, or -1.
func two_herds_hex(from: int, to: int) -> int:
	if dk(current, "stamp", "move") < 3 or not is_fight(from, to):
		return -1
	var best: int = -1
	var bv: int = -1
	for j in HexGrid.neighbors(to):
		var x: Dictionary = tiles[j]
		if int(x.owner) == current and j != from and int(x.fresh) > 0:
			var v: int = _army_gold(x.ready)
			if v > bv:
				bv = v
				best = j
	return best''')

# the Mammals' named Move and In Numbers stay; a regroup has as many moves as you like; Charge adds a move
rep('''func moves_limit(pid: int) -> int:
	return int(mods_of(pid).movesPerAction) + (1 if mamm_now(pid, "move") else 0) + (1 if is_myth(pid) else 0)''',
'''func moves_limit(pid: int) -> int:
	if regrouping() and current == pid:
		return REGROUP_MOVES
	return (1 if dk(pid, "stamp", "move") >= 1 else 0) + int(mods_of(pid).movesPerAction) + (1 if mamm_now(pid, "move") else 0) + (1 if is_myth(pid) else 0)


## Charge (Stampede): the extra move must be an attack.
func charge_only(pid: int) -> bool:
	return dk(pid, "stamp", "move") >= 1 and not play.is_empty() and int(play.moves) >= moves_limit(pid) - 1''')

# Nesting is retired
rep('''func nest_gold(pid: int) -> int:
	if not is_dinos(pid):
		return 0''', '''func nest_gold(pid: int) -> int:
	if true:   # Nesting is retired (2026-11-11): the Dinosaurs' Build upgrades are their cards' own
		return 0''')

# a new turn: materials bought this turn reset
rep('''	p.upd_next = false
	p.herd = false
	for t in tiles:''', '''	p.upd_next = false
	p.herd = false
	p.tr = 0   # materials bought from the markets this turn
	for t in tiles:''')

# Fortify is no longer an instant action
rep('''## Runs "instant" actions (Harvest, Fortify) by themselves, then sets up the first action that needs the player.
func _enter_step() -> void:
	var card: Dictionary = card_of(current, play.card)
	while _is_instant(cur_action()):
		_resolve_instant(cur_action())
		if int(play.step) >= card.actions.size() - 1:
			break
		play.step = int(play.step) + 1
	var a: String = cur_action()''', '''## Runs "instant" actions (Harvest, Channeling) by themselves, then sets up the first action that needs the player.
## Notes for the card column go in step_notes.
var step_notes: Array = []
func _enter_step() -> void:
	var card: Dictionary = card_of(current, play.card)
	while _is_instant(cur_action()):
		_resolve_instant(cur_action())
		if int(play.step) >= card.actions.size() - 1:
			break
		play.step = int(play.step) + 1
	if card_action() == "fortify" and not fx_on():   # Fortify: its ability, then the regroup
		step_notes.append_array(fx_begin(current))
	step_notes.append_array(dino_action_start(current))
	var a: String = cur_action()''')
rep('''func _is_instant(a: String) -> bool:
	return a == "harvest" or a == "fortify" or a == "channel"''', '''func _is_instant(a: String) -> bool:
	return a == "harvest" or a == "channel"''')
rep('''	var card: Dictionary = card_of(current, play.card)
	if int(play.step) < card.actions.size() - 1:
		play.step = int(play.step) + 1
		_enter_step()
	else:
		finish_turn()''', '''	var card: Dictionary = card_of(current, play.card)
	if fx_next():
		return   # still inside a Fortify: the regroup, then the picks
	if int(play.step) < card.actions.size() - 1:
		play.step = int(play.step) + 1
		_enter_step()
	else:
		finish_turn()''')

# Harvest: the Dinosaur cards' upgrades; the old Fortify branch goes
a = s.index('		var rain: bool = is_dinos(current) and named_on()')
b = s.index('## An upgraded Recruit starts with free troops')
s = s[:a] + '''		var hexes: int = int(income_of(current).hexes)
		var fert: int = 0
		if is_mammals(current) and named_on():   # Fertilize: 1 gold for every 2 units they have
			for t in tiles:
				if int(t.owner) == current:
					fert += int(t.troops)
			fert /= 2
		var dh: Dictionary = dino_harvest(current) if is_dinos(current) else {"g": 0, "m": 0, "why": []}
		var g: int = roundi(float(Economy.harvest_gold(mods_of(current), lvl, hexes, false) + industry + fert + int(dh.g)) * gold_mult(current))
		p.gold = int(p.gold) + g
		if int(dh.m) > 0:
			p.mat = mat_of(current) + int(dh.m)
		if not dh.why.is_empty():
			add_log("%s harvest %d gold%s (%s)." % [p.name, g, (" and %s" % mat_txt(int(dh.m))) if int(dh.m) > 0 else "", ", ".join(dh.why)])
		else:
			add_log("%s harvest %d %s%s." % [p.name, g, cur_word(current), (" (%d from fertile land)" % fert) if fert > 0 else ""])


''' + s[b:]

# Recruit prices: Abundance retired; Home Hunters and Nest Hunters (The Hunt)
rep('''	if (unit == "galli" or unit == "dilo") and is_dinos(pid) and pid == current and cur_action() == "recruit" and named_on():
		cost -= 1   # Abundance''', '''	var hu: int = dk(pid, "hunt", "recruit")
	if hu >= 1 and is_home_castle(t) and int(t.owner) == pid:
		cost -= 1   # Home Hunters (The Hunt)
	if hu >= 3 and int(t.barracks) > 0:
		cost -= 1   # Nest Hunters (The Hunt)''')

# ---------------- Build: prices in materials ----------------
rep('''func build_cost(kind: String) -> int:
	return int(GameData.rules.buildings.cost_by_level[kind][cur_lvl()])''', '''## A building's price now (markets in gold, the rest in materials); t is the hex it goes on, when known.
func build_cost(kind: String, t: Dictionary = {}) -> int:
	var c: int = int(GameData.rules.buildings.cost_by_level[kind][cur_lvl()])
	if not play.is_empty() and is_dinos(current) and cur_action() == "build":
		return dino_cost(current, kind, c, t)
	return c''')
rep('''	var price: int = build_cost(kind)
	if cur_action() != "build" or building_count(t) >= max_buildings() or int(p.gold) < price:
		return false''', '''	var price: int = build_cost(kind, t)
	if cur_action() != "build" or building_count(t) >= max_buildings() or not can_pay_b(current, kind, price):
		return false''')
rep('''	p.gold = int(p.gold) - price
	t[kind] = int(t.get(kind, 0)) + 1
	_note_unlock(current, kind, t)
	add_log("%s build a %s." % [p.name, kind])''', '''	pay_b(current, kind, price)
	_dino_built(current, kind, price)
	t[kind] = int(t.get(kind, 0)) + 1
	_note_unlock(current, kind, t)
	add_log("%s build a %s." % [p.name, kind])''')
rep('''	var price: int = 0 if free else int(GameData.rules.buildings.barracks_upgrade_cost[lv])
	if int(p.gold) < price:
		return false
	p.gold = int(p.gold) - price
	if free:
		play.free_bk = true''', '''	var price: int = 0 if free else bk_up_cost(current, lv)
	if mat_of(current) < price:
		return false
	spend_mat(current, price)
	if free:
		play.free_bk = true''')
rep('''	var price: int = treb_price(t)
	if int(p.gold) < price:
		return false
	p.gold = int(p.gold) - price
	var turns: int = treb_turns(t, cur_lvl())''', '''	var price: int = treb_price(t)
	if mat_of(current) < price:
		return false
	spend_mat(current, price)
	var turns: int = treb_turns(t, cur_lvl())''')
rep('''	if cur_action() != "advance" or int(t.owner) != current or not wall_sides(i).has(j) or was >= hp or int(p.gold) < price:
		return false
	p.gold = int(p.gold) - price''', '''	if cur_action() != "advance" or int(t.owner) != current or not wall_sides(i).has(j) or was >= hp or mat_of(current) < price:
		return false
	spend_mat(current, price)''')

# ---------------- moving: the regroup, Home Run, Dash, Over the Top, Charge ----------------
rep('''	var out: Array[int] = []
	for i in _move_targets_core(from, lvl, far):
		var f: Callable = move_filter(from, i, lvl)''', '''	var out: Array[int] = []
	var co: bool = charge_only(pid)
	for i in _move_targets_core(from, lvl, far):
		if co and not (int(tiles[i].owner) >= 0 and int(tiles[i].owner) != pid):
			continue   # Charge: the extra move is an attack
		var f: Callable = move_filter(from, i, lvl)''')
rep('''	var pid: int = int(tiles[from].owner)
	var any_run: Array = GameData.rules.moves.any_run''', '''	var pid: int = int(tiles[from].owner)
	if regrouping() and pid == current:
		return regroup_targets(from, fx_reach())
	var any_run: Array = GameData.rules.moves.any_run''')
rep('''	var run: int = int(own_run[lvl])
	if is_dinos(pid) and pid == current and cur_action() == "move" and named_on():
		run = 999   # Migrate''', '''	var run: int = int(own_run[lvl])''')
rep('''		if next.is_empty():
			break
		frontier = next
	out.erase(from)''', '''		if next.is_empty():
			break
		frontier = next
	if is_dinos(pid) and not play.is_empty() and current == pid:
		if dk(pid, "stamp", "move") >= 2 and from == homes[pid]:
			for i in regroup_targets(from, 99):   # Home Run
				out[i] = true
		var sg: int = dk(pid, "siege", "move")
		if sg >= 2:   # Dash: 2 hexes, both empty
			for a in HexGrid.neighbors(from):
				var A: Dictionary = tiles[a]
				if not can_enter(a, lvl) or int(A.troops) > 0 or not _pass_through(from, a, lvl, pid):
					continue
				for b in HexGrid.neighbors(a):
					if b != from and can_enter(b, lvl) and int(tiles[b].troops) == 0 and home_guards(tiles[b]).is_empty():
						out[b] = true
		if sg >= 3:   # Over the Top: across a mountain, attacking on the far side
			for a in HexGrid.neighbors(from):
				if tiles[a].terrain == "mountain" and _pass_through(from, a, maxi(lvl, 1), pid):
					for b in HexGrid.neighbors(a):
						if b != from and can_enter(b, lvl):
							out[b] = true
	out.erase(from)''')

# Two Herds in move(); units that regroup stay ready (and Join Up gets used up)
rep('''func move(from: int, to: int, sel: Dictionary) -> Dictionary:
	if cur_action() != "move" or moves_left() <= 0:
		return {}''', '''func move(from: int, to: int, sel: Dictionary, join: bool = false) -> Dictionary:
	if cur_action() != "move" or moves_left() <= 0:
		return {}''')
rep('''	clean = _move_sel(from, to, clean, cur_lvl())
	if clean.is_empty():
		return {}
	play.moves = int(play.moves) + 1''', '''	clean = _move_sel(from, to, clean, cur_lvl())
	if clean.is_empty():
		return {}
	var jh: int = two_herds_hex(from, to) if join else -1
	play.moves = int(play.moves) + 1
	if jh >= 0:   # Two Herds: the ready units next door join the attack
		var add: Dictionary = tiles[jh].ready.duplicate()
		add.erase("alamo")
		take_units(jh, add)
		_add_army(from, add, true)
		for k in add:
			clean[k] = int(clean.get(k, 0)) + int(add[k])
		add_log("Two Herds: %d more units join the attack." % _count(add))''')
rep('''	if int(B.owner) == pid:
		_add_army(to, sel, false)
		return res''', '''	if int(B.owner) == pid:
		var rg: bool = regrouping() and pid == current
		if rg and int(play.fx.get("far", 0)) > 0 and not regroup_targets(from, regroup_reach()).has(to):
			play.fx.far = int(play.fx.far) - 1   # Join Up used
		_add_army(to, sel, rg)   # a regroup leaves them ready to move again
		return res''')

# ---------------- battles: Armor; Fortify no longer adds defense ----------------
rep('''	var offline: bool = is_robots(pid) and raw >= 1 and not herd
	return {"adv_a": lvl >= 2, "a_bonus": 1 if up else 0, "a_plus": 1 if up else 0, "surprise": offline}''',
'''	var offline: bool = is_robots(pid) and raw >= 1 and not herd
	var a_arm: bool = armor_on(pid)   # Armor (The Hunt): +2 damage and +10% health for that side
	var d_arm: bool = armor_on(defender)
	var ad: int = int(armor_rules().dmg)
	return {"adv_a": lvl >= 2 and not is_dinos(pid), "a_bonus": 1 if up else 0, "a_plus": (1 if up else 0) + (ad if a_arm else 0),
		"d_plus": ad if d_arm else 0, "a_arm": a_arm, "d_arm": d_arm, "arm_hp": float(armor_rules().hp), "surprise": offline}''')
rep('''	return {"sneak": bool(o.surprise), "plus": int(o.a_plus), "mult": UPDATE_MULT if int(o.a_bonus) > 0 else 1.0}''',
'''	return {"sneak": bool(o.surprise), "plus": int(o.a_plus) - (int(armor_rules().dmg) if bool(o.a_arm) else 0), "mult": UPDATE_MULT if int(o.a_bonus) > 0 else 1.0,
		"arm_a": bool(o.a_arm), "arm_d": bool(o.d_arm)}''')
rep('''	var out: Dictionary = {"sneak": t if bool(m.get("sneak", false)) else -1, "plus": [0, 0], "mult": [1.0, 1.0]}
	out.plus[t] = int(m.get("plus", 0))
	out.mult[t] = float(m.get("mult", 1.0))
	return out''', '''	var out: Dictionary = {"sneak": t if bool(m.get("sneak", false)) else -1, "plus": [0, 0], "mult": [1.0, 1.0], "hp": [1.0, 1.0]}
	out.plus[t] = int(m.get("plus", 0))
	out.mult[t] = float(m.get("mult", 1.0))
	var ar: Dictionary = armor_rules()
	if bool(m.get("arm_a", false)):   # Armor (The Hunt)
		out.plus[t] = int(out.plus[t]) + int(ar.dmg)
		out.hp[t] = float(ar.hp)
	if bool(m.get("arm_d", false)):
		out.plus[1 - t] = int(out.plus[1 - t]) + int(ar.dmg)
		out.hp[1 - t] = float(ar.hp)
	return out''')

# guards: Cheap Guards (The Hunt)
rep('''func guard_cost() -> int:''', '''func guard_cost(pid: int = -1) -> int:
	if pid < 0:
		pid = current
	return int(GameData.rules.dinos.guard_cost) - (3 if dk(pid, "hunt", "advance") >= 2 else 0)   # Cheap Guards (The Hunt)


func _guard_cost_base() -> int:''')

# ---------------- the Mythical: a Mage that moved this turn can plant a Life Tree ----------------
rep('''	if int(t.owner) != pid or int(t.tree) > 0 or t.castle or t.terrain != "plain":
		return false
	var ready_mage: bool = false
	for k in MAGES:
		if int(t.ready.get(k, 0)) > 0:
			ready_mage = true
	if not ready_mage:
		return false
	t.tree = 1
	t.root = int(myth().tree_turns)
	_lock_mage(t)''', '''	if int(t.owner) != pid or int(t.tree) > 0 or t.castle or t.terrain != "plain" or mages_on(t) <= 0:
		return false
	t.tree = 1
	t.root = int(myth().tree_turns)
	var ready_mages: int = 0
	for k in MAGES:
		ready_mages += int(t.ready.get(k, 0))
	if ready_mages >= mages_on(t):
		_lock_mage(t)   # a Mage that already moved this turn is the one that stays''')

# ---------------- saves from before materials and the wild-card Fortify ----------------
rep('''		else:
			set(k, v.duplicate(true) if (v is Array or v is Dictionary) else v)''', '''		else:
			set(k, v.duplicate(true) if (v is Array or v is Dictionary) else v)
	for p in players:
		for key in ["mat", "tr", "fnest"]:
			if not p.has(key):
				p[key] = 0
		if not p.has("armor"):
			p["armor"] = false
	if not play.is_empty() and card_action() == "fortify" and not fx_on():
		play.fx = {"ph": "pick", "n": 1, "done": [], "cur": "", "far": 0, "mv": false, "rally": 0}   # a game saved before Fortify became a wild card''')

open(F, 'w', encoding='utf-8').write(s)
print('rules ok')

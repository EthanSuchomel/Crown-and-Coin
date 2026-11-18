extends RefCounted
## The computer opponent. Ported from the browser version's AI: enemyNear, trebSpot, aiTrebSite,
## aiBuildPlan, aiBuild, aiRecruit, aiAdvance, aiMoveScore, guardUnits, aiMoveGen, aiCardGen,
## tileWorth, exposure, evalFor, aiChooseCard, winEst and runAI.
##
## How it picks a card: for each card in hand it plays the card out 4 times on a copy of the game,
## scores how good the board looks afterwards, and plays the card with the best average.
##
## Use it with: const AIPlayer = preload("res://scripts/rules/ai_player.gd")
##   AIPlayer.take_turn(game)      plays the computer's whole turn and passes the turn on
##   AIPlayer.choose_card(game, pid) and AIPlayer.run_card(game, pid, card_id) for a paced, animated turn

const CombatRules = preload("res://scripts/rules/combat.gd")
const TRIES := 2
## Difficulty. Easy is the old computer. Medium and up spend every action well: markets early, a barracks and a fort to
## unlock better units, barracks upgrades and trebuchets, and attacks that gather troops first. Hard and Expert think
## further ahead by trying out their best moves on a copy of the board first; Expert tries more of them and attacks
## more boldly (and collects 40% more gold, see GameState.AI_GOLD).
const PROF := {
	"easy": {"smart": false, "tries": 2, "blunder": 0.3, "atk": 0.66},
	"medium": {"smart": true, "tries": 3, "blunder": 0.05, "atk": 0.6, "stage": true},
	"hard": {"smart": true, "tries": 3, "blunder": 0.0, "atk": 0.55, "stage": true, "search": 4},
	"expert": {"smart": true, "tries": 5, "blunder": 0.0, "atk": 0.5, "stage": true, "search": 6, "ss": 3, "ev": {"ca": 30.0, "ex": 0.6, "ex2": 0.5}},
}
static var _searching: bool = false
## true: the computer's guesses run full battle simulations, as in the browser (much slower in Godot).
## false: a fast strength comparison (health x damage, luck, walls, defense bonuses).
const ACCURATE_ESTIMATES := false

static var _est: Dictionary = {}


# =====================================================================
# Playing a turn
# =====================================================================

## Plays the current player's whole turn: picks a card, carries it out, then passes the turn.
## Returns the list of things that happened, for the screen to show.
static func take_turn(g) -> Array:
	var pid: int = g.current
	var cid: String = choose_card(g, pid)
	var events: Array = run_card(g, pid, cid)
	if g.over < 0:
		g.finish_turn()
	return events


static func level(g, pid: int) -> String:
	var d: String = String(g.players[pid].get("diff", "medium"))
	return d if PROF.has(d) else "medium"


static func prof(g, pid: int) -> Dictionary:
	return PROF[level(g, pid)]


static func smart(g, pid: int) -> bool:
	return bool(prof(g, pid).smart)


static func choose_card(g, pid: int) -> String:
	var pr: Dictionary = prof(g, pid)
	var hand: Array = g.players[pid].hand
	if float(pr.blunder) > 0.0 and randf() < float(pr.blunder):
		return String(hand[randi() % hand.size()])   # Easy: sometimes just plays a card
	var tries: int = int(pr.tries)
	var best: String = String(hand[0])
	var best_value: float = -INF
	for cid in hand:
		var total: float = 0.0
		for r in tries:
			var c = g.clone()
			run_card(c, pid, String(cid))
			total += eval_for(c, pid)
		if total / tries > best_value:
			best_value = total / tries
			best = String(cid)
	return best


## Carries out one card for the computer. Each event is a Dictionary with "kind":
## "step" (an action is starting), "done" (an action finished; "ids" are the hexes it changed),
## or "move" (from, to, res).
static func run_card(g, pid: int, cid: String) -> Array:
	var events: Array = []
	start_card(g, pid, cid)
	var n: int = g.card_of(pid, cid).actions.size()
	for s in n:
		if g.over >= 0:
			break
		events.append_array(run_step(g, pid, cid, s))
	if g.over < 0:
		ai_stock(g, pid)
	return events


## The markets only sell so many materials a turn, so after its card the computer keeps a store of them for its next
## Build or Advancements.
static func ai_stock(g, pid: int) -> void:
	if not g.uses_mat(pid):
		return
	var p: Dictionary = g.players[pid]
	var want: int = 14 if smart(g, pid) else 8
	if g.mat_of(pid) >= want:
		return
	var keep: int = maxi(6, int(floor(int(p.gold) * 0.35)))
	var n: int = mini(want - g.mat_of(pid), mini(g.mat_left(pid), (int(p.gold) - keep) / g.mat_price()))
	if n > 0:
		g.buy_mat(pid, n)


## Puts the card in play and earns its favor (upgrading an action when one is due).
static func start_card(g, pid: int, cid: String) -> void:
	var card: Dictionary = g.card_of(pid, cid)
	g.play = {"card": cid, "step": 0, "moves": 0, "free_bk": false, "al_bought": 0, "al_free": 0}
	g.add_log("%s play %s." % [g.players[pid].name, card.name])
	var slot: int = g.ai_upgrade_pick(pid, cid) if g.upgrade_due(pid, cid) else -1
	g.gain_favor(pid, cid, slot)


## Carries out action number s (0, 1 or 2) of the card in play.
static func run_step(g, pid: int, cid: String, s: int) -> Array:
	var events: Array = []
	if g.over >= 0:
		return events
	var actions: Array = g.card_of(pid, cid).actions
	g.play.step = s
	var a: String = actions[s]
	var raw: int = g.lvl_of(pid, cid, s)
	var lvl: int = g.cur_lvl()   # the Dinosaurs' cards have their own upgrades, so their usual level stays 0
	events.append({"kind": "step", "action": a})
	var ids: Array = []
	if a == "fortify":
		events.append_array(ai_fortify(g, pid, actions.slice(s + 1)))
		return events
	if a == "build" or a == "recruit" or a == "advance":
		g.dino_action_start(pid)   # the Dinosaur and Robot cards' own upgrades that happen when the action starts
	if a == "harvest" or a == "channel":
		g._resolve_instant(a)
	elif g.is_myth(pid) and (a == "recruit" or a == "build" or a == "advance"):
		if a == "recruit":
			g._free_troops(pid, lvl)
		ids = myth_ai(g, pid, a, actions.slice(s + 1))
	elif a == "recruit":
		g._free_troops(pid, lvl)
		var bi: int = actions.find("build")
		var build_lvl: int = 0
		if bi > s and not g.card_ups(pid):
			var braw: int = g.lvl_of(pid, cid, bi)
			build_lvl = 0 if braw == 1 else braw
		ids = ai_recruit(g, pid, actions.slice(s + 1), build_lvl)
	elif a == "build":
		ids = ai_build(g, pid, lvl, actions.slice(s + 1))
	elif a == "advance":
		ids = ai_advance(g, pid, lvl)
		if g.rg_due(pid):   # Roam Free (Tusks and Thorns): a regroup anywhere in their land after the Advancements
			events.append({"kind": "done", "action": a, "ids": ids})
			g.play.rg = 1
			g.play.moves = 0
			events.append({"kind": "step", "action": "move"})
			events.append_array(ai_regroup(g, pid))
			g.play.rg = 2
			return events
	elif a == "move":
		g.play.moves = 0
		var lz: Array = ai_laser(g, pid)   # Laser Strike (Onslaught): the tanks fire first
		if not lz.is_empty():
			events.append({"kind": "flash", "ids": lz})
		events.append_array(ai_moves(g, pid, lvl))
	if a != "move":
		events.append({"kind": "done", "action": a, "ids": ids})
	return events


# =====================================================================
# The computer's Fortify: its ability, a regroup toward the front (or into a castle in danger), then its picks.
# =====================================================================

static func ai_fortify(g, pid: int, later: Array) -> Array:
	var events: Array = []
	g.fx_begin(pid)
	events.append_array(ai_regroup(g, pid))
	g.play.fx.ph = "pick"
	var n: int = int(g.play.fx.n)
	var order: Array = ai_fx_order(g, pid, n, later)
	for i in order.size():
		if g.over >= 0:
			break
		var k: String = order[i]
		g.play.fx.ph = "act"
		g.play.fx.cur = k
		g.play.free_walls = 0
		events.append({"kind": "step", "action": k})
		events.append({"kind": "done", "action": k, "ids": ai_do_pick(g, pid, k, order.slice(i + 1) + later)})
		g.play.fx.done.append(k)
	if bool(g.play.fx.get("mvx", false)) and g.over < 0:   # Sortie (Siege Protocol): a real Move after the picks
		g.play.fx.ph = "act"
		g.play.fx.cur = "move"
		g.play.moves = 0
		events.append({"kind": "step", "action": "move"})
		events.append_array(ai_moves(g, pid, 0))
	g.play.fx = {}
	return events


static func ai_do_pick(g, pid: int, k: String, later: Array) -> Array:
	if g.is_myth(pid):
		return myth_ai(g, pid, k, later)
	if k == "recruit":
		return ai_recruit(g, pid, later, 0)
	if k == "build":
		return ai_build(g, pid, 0, later)
	return ai_advance(g, pid, 0)


## Which picks: each is tried on a copy of the board, the best kept (then the next, from the board that one leaves).
static func ai_fx_order(g, pid: int, n: int, later: Array) -> Array:
	var picks: Array = GameData.rules.fortify.picks.duplicate()
	if n >= 3:
		return ["build", "advance", "recruit"]
	if not smart(g, pid) and randf() < 0.5:   # Easy: a quick guess half the time
		picks.shuffle()
		return picks.slice(0, n)
	var out: Array = []
	var cur = g.clone()
	for r in n:
		var best: String = ""
		var bv: float = -INF
		for k in picks:
			if out.has(k):
				continue
			var c = cur.clone()
			c.play.fx.ph = "act"
			c.play.fx.cur = k
			var got: Array = ai_do_pick(c, pid, k, later)
			var v: float = eval_for(c, pid) + (2.0 * got.size() if k == "build" else 0.0) + (0.5 if not got.is_empty() else 0.0)
			if v > bv:
				bv = v
				best = k
		out.append(best)
		cur.play.fx.ph = "act"
		cur.play.fx.cur = best
		ai_do_pick(cur, pid, best, later)
	return out


## The regroup: troops in safe land walk up to the front line nearest the castles it wants, or into a castle in danger.
static func ai_regroup(g, pid: int) -> Array:
	var events: Array = []
	var lim: int = 3 if smart(g, pid) else 2
	for step in lim:
		if g.over >= 0:
			break
		var foes: Array = []
		var castles: Array = []
		for t in g.tiles:
			if int(t.owner) >= 0 and int(t.owner) != pid:
				foes.append(int(t.id))
			if t.castle and int(t.owner) != pid:
				castles.append(int(t.id))
		var dE: Array = bfs(g, foes)
		var dC: Array = bfs(g, castles, func(i): return g.can_enter(i, 0))
		var best: Dictionary = {}
		for s in g.tiles:
			if int(s.owner) != pid or int(s.fresh) <= 0:
				continue
			var guard: int = 0
			if s.castle:
				var near: float = enemy_near(g, int(s.id), pid, 3)
				guard = guard_units(g, s, maxf(2.0, near + 1.0) if int(s.id) == g.homes[pid] else near)
			var avail: int = mini(int(s.fresh), int(s.troops) - guard)
			if avail <= 0:
				continue
			var ds: float = fin(float(dE[int(s.id)]))
			if ds <= 1.0 and enemy_near(g, int(s.id), pid, 1) > 0.0:
				continue   # already facing the enemy: stays
			for i in g.regroup_targets(int(s.id), g.fx_reach()):
				var b: Dictionary = g.tiles[i]
				var thr: float = enemy_near(g, i, pid, 2)
				var danger: bool = b.castle and thr > tp(g, b)
				var di: float = fin(float(dE[i]))
				var v: float
				if danger:
					v = 8.0 + 2.0 * minf(thr - tp(g, b), 10.0)
				elif di == 1.0 and di < ds:
					v = 4.0 + maxf(0.0, 6.0 - fin(float(dC[i]))) + 0.3 * minf(enemy_near(g, i, pid, 1), 10.0)
				else:
					continue
				var sel: Dictionary = g.pick_units(int(s.id), avail)
				var sc: float = v * float(g._army_gold(sel)) / 3.0
				if best.is_empty() or sc > float(best.v):
					best = {"v": sc, "from": int(s.id), "to": i, "sel": sel}
		if best.is_empty():
			break
		g.play.moves = int(g.play.moves) + 1
		var res: Dictionary = g.execute_move(int(best.from), int(best.to), best.sel, 0)
		events.append({"kind": "move", "from": int(best.from), "to": int(best.to), "res": res})
	return events


## Laser Strike (Onslaught, Move level 2): every hex with ready Laser Tanks fires at the biggest enemy army next door.
static func ai_laser(g, pid: int) -> Array:
	var ids: Array = []
	if not g.is_robots(pid) or g.dk(pid, "onsl", "move") < 2:
		return ids
	for t in g.tiles:
		if int(t.owner) != pid or int(t.ready.get("ltank", 0)) <= 0:
			continue
		var best: int = -1
		var bv: float = -1.0
		for j in HexGrid.neighbors(int(t.id)):
			if g.laser_ok(pid, int(t.id), j) and tp(g, g.tiles[j]) > bv:
				bv = tp(g, g.tiles[j])
				best = j
		if best >= 0 and not g.do_laser(pid, int(t.id), best).is_empty():
			ids.append(best)
	return ids


## The Robots' factory upgrades: tries the hexes in order and makes the first one it can pay for.
static func _try_up(g, pid: int, k: String, list: Array, ids: Array) -> bool:
	for i in list:
		if g.ai_mat(pid, g.robo_up_cost(pid, k, g.tiles[i])) and g.do_robo_up(pid, int(i), k):
			ids.append(int(i))
			return true
	return false


# =====================================================================
# Helpers
# =====================================================================

## An army's strength in old 3-gold troops, for the computer's sums.
static func tp(g, t: Dictionary) -> float:
	return g._army_gold(t.army) / 3.0


static func enemy_near(g, i: int, pid: int, radius: int) -> float:
	var s: float = 0.0
	for t in g.tiles:
		if int(t.owner) >= 0 and int(t.owner) != pid and int(t.troops) > 0 and HexGrid.distance(i, int(t.id)) <= radius:
			s += tp(g, t)
	return s


## Steps from the nearest source hex. enter decides which hexes can be walked through
## (default: plain land). Unreached hexes are INF.
static func bfs(g, sources: Array, enter: Callable = Callable()) -> Array:
	var dist: Array = []
	dist.resize(g.tiles.size())
	dist.fill(INF)
	var queue: Array = []
	for s in sources:
		dist[int(s)] = 0.0
		queue.append(int(s))
	while not queue.is_empty():
		var c: int = queue.pop_front()
		for n in HexGrid.neighbors(c):
			var ok: bool = enter.call(n) if enter.is_valid() else g.tiles[n].terrain == "plain"
			if ok and dist[n] == INF:
				dist[n] = float(dist[c]) + 1.0
				queue.append(n)
	return dist


static func fin(x: float) -> float:
	return 999.0 if x == INF else x


static func cost_of(kind: String, lvl: int) -> int:
	if not GameData.rules.buildings.cost_by_level.has(kind):
		return 999
	return int(GameData.rules.buildings.cost_by_level[kind][lvl])


static func treb_cost() -> int:
	return int(GameData.rules.trebuchet.field_cost)


## Average-luck estimate of the attacker's chance to win, cached.
static func win_est(att: Dictionary, defn: Dictionary, o: Dictionary) -> float:
	if CombatRules.count(att) == 0:
		return 0.0
	if CombatRules.count(defn) == 0 and int(o.get("wall", 0)) == 0:
		return 1.0
	var key: String = str([att, defn, o])
	if _est.has(key):
		return _est[key]
	var won: bool
	var m: float
	if ACCURATE_ESTIMATES:
		var oo: Dictionary = o.duplicate()
		oo.avg = true
		var b: Dictionary = CombatRules.fight(att, defn, oo)
		won = bool(b.won)
		m = float(b.a_hp) / maxf(1.0, float(b.a_hp0)) - float(b.d_hp) / maxf(1.0, float(b.d_hp0))
	else:
		var r: float = _strength_ratio(att, defn, o)
		won = r > 1.0
		m = sqrt(1.0 - 1.0 / r) if won else -sqrt(maxf(0.0, 1.0 - r))
	var sig: float = 1.0 / (1.0 + exp(-7.0 * m))
	var p: float = maxf(0.5, sig) if won else minf(0.45, sig)
	if _est.size() > 5000:
		_est.clear()
	_est[key] = p
	return p


## Fast estimate: attacker strength / defender strength, where strength = total health x damage
## per second x luck. Above 1 the attacker should win. Units that can't reach flyers only count
## against the ground part of the enemy army.
static func _strength_ratio(att: Dictionary, defn: Dictionary, o: Dictionary) -> float:
	var a_hp: float = _hp(att)
	var d_hp: float = _hp(defn) + float(o.get("wall", 0)) * CombatRules.WALL_PT
	var a_dps: float = _side_dps(att, defn, float(o.get("a_plus", 0)))
	var d_dps: float = _side_dps(defn, att, 0.0)
	if a_dps <= 0.0:
		return 0.0001
	if d_dps <= 0.0:
		return 1000.0
	if bool(o.get("arena", false)):
		a_dps *= float(CombatRules.ARENA_CAL.get(String(o.get("map", "open")), 1.0))
	var la: float = 0.6 + 0.12 * ((4.47 if bool(o.get("adv_a", false)) else 3.5) + float(o.get("a_bonus", 0)))
	var ld: float = 0.6 + 0.12 * ((4.47 if bool(o.get("adv_d", false)) else 3.5) + float(o.get("bonus", 0)))
	var r: float = (a_hp * a_dps * la) / maxf(0.0001, d_hp * d_dps * ld)
	if bool(o.get("surprise", false)):
		r *= 1.15   # Offline: the defenders hold fire until the first hit lands
	return maxf(0.0001, r)


static func _hp(a: Dictionary) -> float:
	var h: float = 0.0
	for k in a:
		h += int(a[k]) * float(GameData.units[k].hp)
	return h


static func _side_dps(mine: Dictionary, foe: Dictionary, plus: float) -> float:
	var foe_n: int = 0
	var foe_ground: int = 0
	var foe_hp: float = 0.0
	var foe_air_hp: float = 0.0
	for k in foe:
		var U: Dictionary = GameData.units[k]
		var n: int = int(foe[k])
		foe_n += n
		foe_hp += n * float(U.hp)
		if U.get("air", false):
			foe_air_hp += n * float(U.hp)
		else:
			foe_ground += n
	var ground_share: float = 1.0 if foe_hp <= 0.0 else (foe_hp - foe_air_hp) / foe_hp
	var total: float = 0.0
	for k in mine:
		var U2: Dictionary = GameData.units[k]
		var n2: int = int(mine[k])
		var d: float
		if U2.has("beam"):
			d = float(U2.dmg) * minf(float(U2.beam.n), float(maxi(1, foe_n))) / 8.0
		else:
			d = (float(U2.dmg) + plus) * float(U2.get("shots", 1)) * (1.25 if U2.get("charged", false) else 1.0) / float(U2.rate)
			if U2.has("multi"):
				d *= maxf(1.0, minf(float(U2.multi), float(foe_ground)))
			if U2.get("sweep", false):
				d *= 1.0 + 0.25 * maxf(0.0, minf(2.0, float(foe_n) - 1.0))
			if U2.has("riders"):
				var dilo: Dictionary = GameData.units.dilo
				d += float(U2.riders) * float(dilo.dmg) / float(dilo.rate)
		var reach: float = 1.0 if U2.get("aa", false) else ground_share
		total += n2 * d * reach
	return total


# =====================================================================
# Building, recruiting and Advancements
# =====================================================================

static func treb_spot(g, i: int, pid: int) -> float:
	var v: float = 0.0
	for j in HexGrid.neighbors(i):
		var b: Dictionary = g.tiles[j]
		if int(b.owner) >= 0 and int(b.owner) != pid:
			v += 1.0 + 0.3 * minf(tp(g, b), 5.0)
	return v


static func ai_treb_site(g, pid: int) -> int:
	var best: int = -1
	var best_spot: float = 0.0
	for t in g.tiles:
		if int(t.owner) != pid or not g.can_treb_at(t) or g.mat_reach(pid, 0) < g.treb_price(t):
			continue
		var spot: float = treb_spot(g, int(t.id), pid)
		if spot > best_spot:
			best_spot = spot
			best = int(t.id)
	return best


## What the computer wants to build next: {k, id}, or an empty Dictionary.
static func build_plan(g, pid: int, treb: bool, lvl: int) -> Dictionary:
	var own: Array = g.tiles.filter(func(t): return int(t.owner) == pid and t.terrain == "plain")
	var max_b: int = g.max_buildings()
	# When an Advancements action follows: a fort on the front line, to put a trebuchet on.
	if treb and not g.is_dinos(pid) and ai_treb_site(g, pid) < 0 and g.mat_reach(pid, 0) >= cost_of("fort", lvl) + treb_cost():
		var best: int = -1
		var best_spot: float = -INF
		for t in own:
			if t.castle or int(t.fort) > 0 or int(t.treb) > 0 or g.building_count(t) >= max_b or int(t.troops) <= 0:
				continue
			var spot: float = treb_spot(g, int(t.id), pid)
			if spot >= 2.0 and spot > best_spot:
				best_spot = spot
				best = int(t.id)
		if best >= 0:
			return {"k": "fort", "id": best}
	var markets: int = 0
	for t in own:
		markets += int(t.market)
	if markets < 1 + own.size() / 10:
		var d_enemy: Array = bfs(g, g.foe_tiles(pid))
		var best_m: int = -1
		var far: float = -INF
		for t in own:
			if g.building_count(t) >= max_b:
				continue
			var d: float = fin(float(d_enemy[int(t.id)]))
			if d > far:
				far = d
				best_m = int(t.id)
		if best_m >= 0:
			return {"k": "market", "id": best_m}
	var has_barracks: bool = false
	for t in own:
		if int(t.barracks) > 0:
			has_barracks = true
	if own.size() >= 8 and not has_barracks:
		var d_home: Array = bfs(g, g.foe_homes(pid))
		var best_b: int = -1
		var near: float = INF
		for t in own:
			if t.castle or g.building_count(t) >= max_b:
				continue
			var d2: float = fin(float(d_home[int(t.id)]))
			if d2 < near:
				near = d2
				best_b = int(t.id)
		if best_b >= 0:
			return {"k": "barracks", "id": best_b}
	return {}


## Medium and up: an economy first (markets pay for themselves in 3 turns), a barracks and a fort early so the home
## castle can train the better units, more markets while there's time for them to pay, then forts on the front line.
static func build_plan2(g, pid: int, treb: bool, lvl: int, keep: int = 0) -> Dictionary:
	var p: Dictionary = g.players[pid]
	var gold: int = int(p.gold) - keep
	var max_b: int = g.max_buildings()
	var own: Array = g.tiles.filter(func(t): return int(t.owner) == pid and t.terrain == "plain")
	if own.is_empty():
		return {}
	var room := func(t): return g.building_count(t) < max_b
	var can := func(k): return g.can_b(pid, k, cost_of(k, lvl), keep)
	var d_en: Array = bfs(g, g.foe_tiles(pid))
	var dE := func(t): return fin(float(d_en[int(t.id)]))
	var u: Dictionary = g.unlocks_of(pid)
	if treb and not g.is_dinos(pid) and ai_treb_site(g, pid) < 0 and g.mat_reach(pid, keep) >= cost_of("fort", lvl) + treb_cost():
		var c0: Array = own.filter(func(t): return not t.castle and int(t.fort) == 0 and int(t.treb) == 0 and room.call(t) and int(t.troops) > 0 and treb_spot(g, int(t.id), pid) >= 2.0)
		c0.sort_custom(func(a, b): return treb_spot(g, int(a.id), pid) > treb_spot(g, int(b.id), pid))
		if not c0.is_empty():
			return {"k": "fort", "id": int(c0[0].id)}
	if g.is_mammals(pid) and g.mat_reach(pid, keep + 6) >= cost_of("wh", lvl) and not own.any(func(t): return int(t.get("wh", 0)) > 0):
		var cw: Array = own.filter(func(t): return int(t.get("wh", 0)) == 0 and room.call(t) and (g.has_menu(t, "fort") or g.has_menu(t, "barracks")))
		cw.sort_custom(func(a, b): return dE.call(a) < dE.call(b))
		if not cw.is_empty():
			return {"k": "wh", "id": int(cw[0].id)}
	var markets: int = 0
	var bks: int = 0
	for t in own:
		markets += int(t.market)
		if int(t.barracks) > 0:
			bks += 1
	# where markets go: far from the enemy
	var m_site := func() -> int:
		var c1: Array = own.filter(func(t): return room.call(t))
		c1.sort_custom(func(a, b): return dE.call(a) > dE.call(b))
		return int(c1[0].id) if not c1.is_empty() else -1
	var turns_left: int = maxi(0, 24 - int(g.turn))
	var pays: float = float(cost_of("market", lvl)) / float(g.mods_of(pid).marketGold) + 1.0
	# the first barracks: one step back from the front, so its troops are close but safe
	var bk_site := func() -> int:
		var c2: Array = own.filter(func(t): return not t.castle and room.call(t))
		c2.sort_custom(func(a, b):
			var ka: float = absf(dE.call(a) - 2.0)
			var kb: float = absf(dE.call(b) - 2.0)
			return ka < kb if ka != kb else dE.call(a) < dE.call(b))
		return int(c2[0].id) if not c2.is_empty() else -1
	if bks == 0 and treb and own.size() >= 2 and can.call("barracks"):
		var s0: int = bk_site.call()
		if s0 >= 0:
			return {"k": "barracks", "id": s0}   # an Advancements follows: something to upgrade
	if markets < (2 if bks > 0 else 1) and turns_left > pays and can.call("market"):
		var s1: int = m_site.call()
		if s1 >= 0:
			return {"k": "market", "id": s1}
	if bks == 0 and own.size() >= 3 and can.call("barracks"):
		var s2: int = bk_site.call()
		if s2 >= 0:
			return {"k": "barracks", "id": s2}
	# the first fort unlocks the fort's units at the home castle; on the front, where its defense helps
	if not g.is_dinos(pid) and not bool(u.fort) and own.size() >= 6 and can.call("fort"):   # (the Dinosaurs build no forts)
		var c3: Array = own.filter(func(t): return not t.castle and room.call(t))
		c3.sort_custom(func(a, b): return dE.call(a) - (1.0 if int(a.troops) > 0 else 0.0) < dE.call(b) - (1.0 if int(b.troops) > 0 else 0.0))
		if not c3.is_empty():
			return {"k": "fort", "id": int(c3[0].id)}
	var rich: bool = gold >= 45
	if (markets < 2 + own.size() / 3 or (rich and markets < own.size())) and turns_left > pays and can.call("market"):
		var s3: int = m_site.call()
		if s3 >= 0:
			return {"k": "market", "id": s3}
	if own.size() >= 11 and bks < 2 and can.call("barracks"):
		var c4: Array = own.filter(func(t): return not t.castle and int(t.barracks) == 0 and room.call(t) and dE.call(t) >= 2.0)
		c4.sort_custom(func(a, b): return dE.call(a) < dE.call(b))
		if not c4.is_empty():
			return {"k": "barracks", "id": int(c4[0].id)}
	if rich and own.size() >= 6 and can.call("barracks") and bks < own.size() / 5:
		var c5: Array = own.filter(func(t): return not t.castle and room.call(t) and dE.call(t) >= 2.0)
		c5.sort_custom(func(a, b): return dE.call(a) < dE.call(b))
		if not c5.is_empty():
			return {"k": "barracks", "id": int(c5[0].id)}
	# spare gold: forts where troops hold the front line
	if not g.is_dinos(pid) and g.mat_reach(pid, keep + 12) >= cost_of("fort", lvl):
		var c6: Array = own.filter(func(t): return not t.castle and room.call(t) and int(t.fort) < 2 and int(t.troops) >= 3 and dE.call(t) <= 1.0)
		c6.sort_custom(func(a, b): return tp(g, a) > tp(g, b))
		if not c6.is_empty():
			return {"k": "fort", "id": int(c6[0].id)}
	return {}


## Gold to hold back for a Recruit later on the same card: more when the home castle is in danger.
static func keep_for_recruit(g, pid: int, later: Array) -> int:
	if not later.has("recruit"):
		return 0
	var p: Dictionary = g.players[pid]
	var h: Dictionary = g.tiles[g.homes[pid]]
	var thr: float = enemy_near(g, int(h.id), pid, 3) if int(h.owner) == pid else 0.0
	var share: float = 0.65 if thr > tp(g, h) * 0.8 else (0.15 if int(g.turn) <= 4 else 0.35)
	return int(floor(int(p.gold) * share))


static func ai_build(g, pid: int, lvl: int, later: Array) -> Array:
	var p: Dictionary = g.players[pid]
	var ids: Array = []
	var treb: bool = later.has("advance")
	var sm: bool = smart(g, pid)
	var keep_r: int = keep_for_recruit(g, pid, later) if sm else 0
	# Roost Grant and Free Roost (Mammals): free fortresses first, on the front line
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
	while (g.is_dinos(pid) or g.is_mammals(pid)) and int(p.get("fnest", 0)) > 0:
		var d_e: Array = g._foe_dist(pid)
		var c0: Array = g.tiles.filter(func(x): return int(x.owner) == pid and x.terrain == "plain" and not x.castle and g.building_count(x) < g.max_buildings())
		if c0.is_empty():
			break
		c0.sort_custom(func(x, y): return int(x.barracks) < int(y.barracks) if int(x.barracks) != int(y.barracks) else float(d_e[int(x.id)]) < float(d_e[int(y.id)]))
		var nt: Dictionary = c0[0]
		nt.barracks = int(nt.barracks) + 1
		g._note_unlock(pid, "barracks", nt)
		p.fnest = int(p.fnest) - 1
		ids.append(int(nt.id))
		g.add_log("%s build a free Barracks (New Nest)." % p.name)
	for n in (8 if sm else 6):
		var plan: Dictionary = build_plan2(g, pid, treb, lvl, keep_r) if sm else build_plan(g, pid, treb, lvl)
		if plan.is_empty():
			break
		if g.is_robots(pid):   # Robots: markets on an empty hex or a resource hex; barracks and forts are factory upgrades (Advancements)
			if plan.k == "market" and not g.robo_can_market(g.tiles[int(plan.id)]):
				var d_e: Array = bfs(g, g.foe_tiles(pid))
				var best_m: int = -1
				var far: float = -INF
				for x in g.tiles:
					if int(x.owner) == pid and x.terrain == "plain" and g.robo_can_market(x) and fin(float(d_e[int(x.id)])) > far:
						far = fin(float(d_e[int(x.id)]))
						best_m = int(x.id)
				if best_m < 0:
					break
				plan = {"k": "market", "id": best_m}
			elif plan.k != "market":
				var pt: Dictionary = g.tiles[int(plan.id)]
				if plan.k == "barracks" and not pt.castle and g.building_count(pt) == 0 and g.robo_up_targets(pid, "barracks").is_empty():
					plan = {"k": "market", "id": int(plan.id)}   # a market, to give a barracks later
				else:
					break
		var keep: int = treb_cost() if (treb and plan.k != "fort" and ai_treb_site(g, pid) >= 0) else 0   # materials kept for the trebuchet
		var t: Dictionary = g.tiles[int(plan.id)]
		var cost: int = g.build_cost(plan.k, t) if g.cur_action() == "build" else cost_of(plan.k, lvl)
		if g.in_mat(plan.k):
			if not g.ai_mat(pid, cost + keep, keep_r):
				break
			g.spend_mat(pid, cost)
		else:
			if int(p.gold) - cost < g.gold_for(pid, keep):
				break
			p.gold = int(p.gold) - cost
		g._dino_built(pid, plan.k, cost)
		t[plan.k] = int(t[plan.k]) + 1
		g._note_unlock(pid, plan.k, t)
		ids.append(int(plan.id))
		g.add_log("%s build a %s." % [p.name, plan.k])
	return ids


static func ai_recruit(g, pid: int, later: Array, build_lvl: int) -> Array:
	var p: Dictionary = g.players[pid]
	var sites: Array = g.tiles.filter(func(t): return int(t.owner) == pid and (g.can_recruit_at(t) or g.has_menu(t, "barracks") or g.has_menu(t, "fort")))
	if sites.is_empty():
		return []
	var keep: int = 0
	if later.has("build"):
		if smart(g, pid):   # room for the next two buildings the plan wants
			var plan2: Dictionary = build_plan2(g, pid, false, build_lvl)
			if not plan2.is_empty():
				var c2b: int = g.gold_for(pid, cost_of(plan2.k, build_lvl)) if g.in_mat(plan2.k) else cost_of(plan2.k, build_lvl)   # in gold: materials still to buy
				if int(g.turn) <= 14 and int(p.gold) >= 2 * c2b + 6:
					c2b *= 2
				if int(p.gold) >= c2b + 3:
					keep = c2b
		else:
			var plan: Dictionary = build_plan(g, pid, false, build_lvl)
			if not plan.is_empty():
				var c: int = g.gold_for(pid, cost_of(plan.k, build_lvl)) if g.in_mat(plan.k) else cost_of(plan.k, build_lvl)
				if int(p.gold) >= c + 3:
					keep = c
	if later.has("advance") and ai_treb_site(g, pid) >= 0:
		var tg: int = g.gold_for(pid, treb_cost())
		if int(p.gold) >= tg + 3:
			keep = maxi(keep, tg)
	var home: Dictionary = g.tiles[g.homes[pid]]
	var site: Dictionary
	if int(home.owner) == pid and enemy_near(g, int(home.id), pid, 3) >= tp(g, home):
		site = home
	else:
		var d_home: Array = bfs(g, g.foe_homes(pid))
		var near: float = INF
		for t in sites:
			var d: float = fin(float(d_home[int(t.id)]))
			if d < near:
				near = d
				site = t
	# What it can buy there: the basic unit at a castle or barracks, and the barracks' and fort's own units.
	var faction: Dictionary = g.faction_of(pid)
	var opts: Array = []
	if g.can_recruit_at(site):
		opts.append(g.basic_of(pid))
	if g.has_menu(site, "barracks"):
		for k in faction.training.barracks:
			if g.train_ok(site, "barracks", k) and not opts.has(k):
				opts.append(k)
	if g.has_menu(site, "fort"):
		for k in faction.training.fort:
			if not opts.has(k):
				opts.append(k)
	var budget: int = int(p.gold) - keep
	var got: Dictionary = {}
	var sid: int = int(site.id)
	for i in 300:
		var aff: Array = opts.filter(func(k): return g.unit_cost_at(sid, pid, k) <= budget)
		if aff.is_empty():
			break
		# Mostly the strongest it can afford, sometimes something cheaper, so armies come out mixed.
		var k: String
		if randf() < 0.55:
			k = aff[0]
			for x in aff:
				if int(GameData.units[x].cost) > int(GameData.units[k].cost):
					k = x
		else:
			k = aff[randi() % aff.size()]
		var c2: int = g.unit_cost_at(sid, pid, k)
		budget -= c2
		p.gold = int(p.gold) - c2
		got[k] = int(got.get(k, 0)) + 1
	var basic: String = g.basic_of(pid)
	if g.dk(pid, "mobil", "recruit") >= 1 and int(got.get(basic, 0)) >= 2:
		got[basic] = int(got[basic]) + int(got[basic]) / 2   # Assembly Line
	if CombatRules.count(got) == 0:
		return []
	if g.is_mammals(pid):
		for k in got:
			g.mamm_bought(pid, k, int(got[k]))   # Hide Trade and Tusk Trade (Call of the Wild)
	g._add_army(sid, got, true)
	g.tiles[sid].new_t = g.turn
	var parts: Array = []
	for k in got:
		parts.append("%d %s" % [int(got[k]), GameData.units[k].name])
	g.add_log("%s recruit %s." % [p.name, ", ".join(parts)])
	return [sid]


static func ai_advance(g, pid: int, lvl: int) -> Array:
	var p: Dictionary = g.players[pid]
	var ids: Array = []
	if g.is_robots(pid) and g.home_market(pid):   # the Robots' factory upgrades, made at the home castle, then Overclock
		var d_e2: Array = bfs(g, g.foe_tiles(pid))
		var own: Array = g.tiles.filter(func(t): return int(t.owner) == pid)
		var bks: int = own.filter(func(t): return int(t.barracks) > 0).size()
		var u0: Dictionary = g.unlocks_of(pid)
		if bks == 0 or (own.size() >= 11 and bks < 2) or (int(p.gold) >= 45 and bks < own.size() / 5):
			var tb: Array = g.robo_up_targets(pid, "barracks")
			tb.sort_custom(func(a, b):
				var ka: float = absf(fin(float(d_e2[a])) - 2.0)
				var kb: float = absf(fin(float(d_e2[b])) - 2.0)
				return ka < kb if ka != kb else fin(float(d_e2[a])) < fin(float(d_e2[b])))
			_try_up(g, pid, "barracks", tb, ids)
		if not bool(u0.fort) or g.mat_reach(pid, 12) >= int(GameData.rules.buildings.cost_by_level.fort[0]) + 4:
			var tf: Array = g.robo_up_targets(pid, "fort")
			tf.sort_custom(func(a, b): return fin(float(d_e2[a])) < fin(float(d_e2[b])))
			_try_up(g, pid, "fort", tf, ids)
		if not g.armor_on(pid) and g.dk(pid, "cons", "advance") >= 3 and int(p.gold) >= int(g.armor_rules().cost) + 8 and g.do_armor(pid):   # Overclock
			ids.append(g.homes[pid])
	if g.is_dinos(pid):
		# the volcano first (it hits every few turns from home), then Alamosaurus guards at the barracks the enemy is closest to
		var sp: int = 6 if smart(g, pid) else 15
		var vl: int = g.volc_lv(pid)
		if vl < 3 and int(g.tiles[g.homes[pid]].owner) == pid and int(p.gold) >= int(g.volc_levels()[vl].cost) + sp and g.do_volcano(pid):
			ids.append(g.homes[pid])
		var gb: Array = []
		for t in g.tiles:
			if int(t.owner) == pid and int(t.barracks) > 0 and g.guards_at(t) < g.guard_max(t):
				var thr: float = enemy_near(g, int(t.id), pid, 2)
				if thr > 0.0:
					gb.append([thr, int(t.id)])
		gb.sort_custom(func(x, y): return float(x[0]) > float(y[0]))
		for pair in gb:
			var gt: Dictionary = g.tiles[int(pair[1])]
			while g.guards_at(gt) < g.guard_max(gt) and int(p.gold) >= g.guard_cost(pid) + sp and g.buy_guard(int(gt.id)):
				ids.append(int(gt.id))
		if not g.armor_on(pid) and int(p.gold) >= int(g.armor_rules().cost) + sp and g.do_armor(pid):   # Armor (The Hunt)
			ids.append(g.homes[pid])
	var ts: int = ai_treb_site(g, pid)
	if ts >= 0 and g.ai_mat(pid, g.treb_price(g.tiles[ts])) and g.start_trebuchet(ts):
		ids.append(ts)
	var wall_hp: int = int(GameData.rules.walls.hp)
	var no_walls: bool = smart(g, pid) and g.arena_rules()   # walls don't count in the Arena, so a smart computer skips them
	for n in (0 if no_walls else 3 + int(GameData.rules.mammals.free_walls)):
		var free: bool = g.free_walls_left() > 0
		if n >= 3 and not free:
			break
		var best_i: int = -1
		var best_j: int = -1
		var best_value: float = 0.0
		for t in g.tiles:
			if int(t.owner) != pid or not (t.castle or int(t.treb) > 0 or (free and int(t.troops) > 0)):
				continue
			var w: float = 3.0 if g.homes[pid] == int(t.id) else (2.0 if t.castle else 1.2)
			for j in g.wall_sides(int(t.id)):
				if g.wall_on(int(t.id), j) >= wall_hp or int(g.tiles[j].owner) == pid:
					continue
				var thr: float = enemy_near(g, j, pid, 2 if free else 1)
				var v: float = w * (thr + (0.5 if free and int(g.tiles[j].owner) >= 0 else 0.0))
				if thr >= (1.0 if free else 2.0) and v > best_value:
					best_value = v
					best_i = int(t.id)
					best_j = j
		if best_i < 0 or not (free or g.ai_mat(pid, g.wall_cost())) or not g.build_wall(best_i, best_j):
			break
		ids.append(best_i)
	var bks: Array = g.tiles.filter(func(t): return int(t.owner) == pid and int(t.barracks) > 0 and int(t.bk) < 3)
	bks.sort_custom(func(a, b): return int(a.bk) > int(b.bk))
	if lvl >= 1 and not bool(g.play.free_bk):
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
	var spare: Array = [2, 4, 12] if smart(g, pid) else [8, 8, 20]
	for t in bks:
		# Levels 1 and 2 unlock units, so the computer goes for them sooner.
		while int(t.bk) < 3 and g.ai_mat(pid, g.bk_up_cost(pid, int(t.bk), t), int(spare[int(t.bk)])):
			if not g.upgrade_barracks(int(t.id)):
				break
			ids.append(int(t.id))
	if ids.is_empty() and smart(g, pid) and not g.arena_rules() and g.mat_reach(pid, 8) >= g.wall_cost():
		var h: Dictionary = g.tiles[g.homes[pid]]
		if int(h.owner) == pid:
			var d_eh: Array = bfs(g, g.foe_homes(pid))
			var sides: Array = g.wall_sides(int(h.id)).filter(func(j): return g.wall_on(int(h.id), j) < wall_hp and int(g.tiles[j].owner) != pid)
			sides.sort_custom(func(a, b): return fin(float(d_eh[a])) < fin(float(d_eh[b])))
			if not sides.is_empty() and g.ai_mat(pid, g.wall_cost(), 8) and g.build_wall(int(h.id), int(sides[0])):
				ids.append(int(h.id))
	return ids


# =====================================================================
# Moving: the computer scores every possible move and makes the best ones.
# =====================================================================

## How many of a hex's units must stay to guard it (worth "guard" troops), counting the cheapest first.
static func guard_units(g, t: Dictionary, guard: float) -> int:
	if guard <= 0.0:
		return 0
	var n: int = 0
	var v: float = 0.0
	var ks: Array = g._by_strength(t.army)
	ks.reverse()
	for k in ks:
		for i in int(t.army[k]):
			if v >= guard:
				return n
			v += float(GameData.units[k].cost) / 3.0
			n += 1
	return n


static func move_score(g, pid: int, s: Dictionary, b: Dictionary, n: int, D: Array, lvl: int, claim: bool) -> float:
	var foe: bool = int(b.owner) >= 0 and int(b.owner) != pid
	var prog: float = float(D[int(s.id)]) - float(D[int(b.id)])
	var sel: Dictionary = g.pick_units(int(s.id), n, claim and n == 1)
	var st: float = g._army_gold(sel) / 3.0
	var adv: float = prog * 0.4 * st if prog > 0 else 0.0
	var castle_v: float = 0.0
	if b.castle:
		var their_home: bool = foe and g.homes[int(b.owner)] == int(b.id)
		castle_v = ((2500.0 if g.foes_of(pid).size() > 1 else 10000.0) if their_home else 45.0)   # a rival's home castle: wins (2 sides) or knocks them out (3)
	var to_win: int = int(GameData.rules.castles.to_win)
	if castle_v < 10000.0 and b.castle and foe and not g.siege.is_empty() and int(g.siege.pid) == int(b.owner):
		castle_v = 3000.0   # breaks their hold: must try
	elif b.castle and g.players.size() == 2 and g.castle_count(pid) + 1 >= to_win:
		castle_v += 150.0   # gets us to the winning count
	if int(b.owner) == pid:
		var v: float = 1.0 + adv if prog > 0 else -1.0
		if b.castle:
			var near: float = enemy_near(g, int(b.id), pid, 2)
			if near >= tp(g, b):
				v = maxf(v, 2.0 + 2.0 * minf(st, near - tp(g, b) + 2.0))
		return v
	var coin_v: float = (float(GameData.rules.coin.gold) * 0.9 if b.bounty else 0.0) + (float(GameData.rules.crate.materials) * 1.8 if b.get("crate", false) and not g.is_myth(pid) else 0.0)   # a material hex is worth about a coin
	var W: int = g.wall_facing(int(s.id), int(b.id), lvl)
	if int(b.troops) == 0 and W == 0 and g.home_guards(b).is_empty():
		return 4.0 + castle_v + coin_v + (3.0 if foe else 0.0) + adv - (2.0 if n > 1 and prog <= 0 else 0.0)
	var o: Dictionary
	if g.arena_rules():
		o = g.arena_o(pid, lvl, int(b.owner), g.arena_map(b))
	else:
		o = g.atk_opts(pid, lvl, g.raw_lvl(), int(b.owner))
		o.wall = W
		o.bonus = g.def_bonus(b)
		o.adv_d = g.def_adv(b)
		o.map = g.arena_map(b)
	var p: float = win_est(sel, g.def_army(b), o)
	var atk: float = float(prof(g, pid).atk)
	var need: float = atk
	if castle_v >= 10000.0:
		need = minf(0.5, atk)
	elif castle_v >= 3000.0:
		need = 0.15
	elif castle_v > 0.0:
		need = minf(0.5, atk)
	if p < need:
		return -1.0
	return p * (3.0 * tp(g, b) + 6.0 + castle_v + coin_v + adv) - (1.0 - p) * 3.0 * st


## Medium and up: moving troops onto one of its own hexes next to an enemy hex it couldn't take alone, so the
## combined army can attack with the next move.
static func stage_score(g, pid: int, s: Dictionary, b: Dictionary, n: int, lvl: int) -> float:
	var sel: Dictionary = g.pick_units(int(s.id), n)
	var best: float = 0.0
	var atk: float = float(prof(g, pid).atk)
	for j in HexGrid.neighbors(int(b.id)):
		var e: Dictionary = g.tiles[j]
		if int(e.owner) < 0 or int(e.owner) == pid or not g.can_enter(j, lvl):
			continue
		var o: Dictionary
		if g.arena_rules():
			o = g.arena_o(pid, lvl, int(e.owner), g.arena_map(e))
		else:
			o = g.atk_opts(pid, lvl, g.raw_lvl(), int(e.owner))
			o.wall = g.wall_on(j, int(b.id))
			o.bonus = g.def_bonus(e)
			o.adv_d = g.def_adv(e)
			o.map = g.arena_map(e)
		var defn: Dictionary = g.def_army(e)
		var mine: Dictionary = g.pick_units(int(b.id), int(b.fresh)) if int(b.fresh) > 0 else {}
		var before: float = win_est(mine, defn, o) if CombatRules.count(mine) > 0 else 0.0
		var both: Dictionary = mine.duplicate()
		for k in sel:
			both[k] = int(both.get(k, 0)) + int(sel[k])
		var after: float = win_est(both, defn, o)
		if after < atk or after <= before + 0.05:
			continue
		var castle_v: float = (400.0 if g.homes[int(e.owner)] == int(e.id) else 45.0) if e.castle else 0.0
		best = maxf(best, 0.6 * after * (3.0 * tp(g, e) + 6.0 + castle_v))
	return best


## Hard and Expert: each of the top few moves (by the quick score) is played out on a copy of the board, battles and all;
## the computer keeps the move whose board it likes best, or stops moving if none beats standing still.
static func search_move(g, pid: int, cands: Array, lvl: int, K: int) -> Dictionary:
	cands.sort_custom(func(a, b): return float(a.v) > float(b.v))
	var top: Array = cands.slice(0, K)
	var best: Dictionary = {}
	var bv: float = eval_for(g, pid) - 2.0   # standing still must win by a little, or the computer keeps moving
	var ss: int = int(prof(g, pid).get("ss", 2))
	_searching = true
	for c in top:
		var tot: float = 0.0
		for r in ss:
			var cg = g.clone()
			cg.play.moves = int(cg.play.get("moves", 0)) + 1
			cg.execute_move(int(c.from), int(c.to), c.sel, lvl)
			tot += eval_for(cg, pid)
		var v: float = tot / ss + 0.05 * float(c.v)
		if v > bv:
			bv = v
			best = c
	_searching = false
	return best


static func ai_moves(g, pid: int, lvl: int) -> Array:
	var events: Array = []
	var limit: int = g.moves_limit(pid)   # more with the cards' extra moves
	while int(g.play.moves) < limit:
		var k: int = int(g.play.moves)
		if g.over >= 0:
			break
		var castles: Array = []
		for t in g.tiles:
			if t.castle and int(t.owner) != pid:
				castles.append(int(t.id))
		var dist: Array = bfs(g, castles, func(i): return g.can_enter(i, lvl))
		# A hex the paths can't reach (a mountain held from an earlier turn) counts as one step past its nearest neighbour.
		var D: Array = []
		D.resize(g.tiles.size())
		for i in g.tiles.size():
			if float(dist[i]) != INF:
				D[i] = float(dist[i])
			else:
				var m: float = 999.0
				for j in HexGrid.neighbors(i):
					if float(dist[j]) != INF:
						m = minf(m, float(dist[j]) + 1.0)
				D[i] = m
		var best: Dictionary = {}
		var pr: Dictionary = prof(g, pid)
		var stage: bool = bool(pr.get("stage", false))
		var search: int = int(pr.get("search", 0))
		var cands: Array = []
		for t in g.tiles:
			if int(t.owner) != pid or int(t.fresh) <= 0:
				continue
			var guard: int = 0
			if t.castle:
				var near: float = enemy_near(g, int(t.id), pid, 3)
				guard = guard_units(g, t, maxf(2.0, near + 1.0) if int(t.id) == g.homes[pid] else near)
			var avail0: int = mini(int(t.fresh), int(t.troops) - guard)
			if avail0 <= 0:
				continue
			for i in g.move_targets(int(t.id), lvl):
				var b: Dictionary = g.tiles[i]
				# only the units that can make this move (flyers at a Floating Castle, Mages and Minions on a long move)
				var mf: Callable = g.move_filter(int(t.id), i, lvl)
				var keep_r: Dictionary = t.ready
				if mf.is_valid():
					var r: Dictionary = {}
					for uk in keep_r:
						if mf.call(uk):
							r[uk] = keep_r[uk]
					t.ready = r
				var avail: int = mini(avail0, CombatRules.count(t.ready))
				if avail <= 0:
					t.ready = keep_r
					continue
				var claim: bool = int(b.owner) != pid and int(b.troops) == 0 and g.wall_facing(int(t.id), i, lvl) == 0
				var counts: Array = [avail, avail - 1, 1] if (claim and avail > 1) else [avail]
				for n in counts:
					var v: float = move_score(g, pid, t, b, n, D, lvl, claim)
					if n == avail - 1 and n > 1 and k < limit - 1:
						v += 1.5   # leaves a unit free for the next move
					if stage and int(b.owner) == pid and k < limit - 1:
						v = maxf(v, stage_score(g, pid, t, b, n, lvl))
					if v > 0.0:
						var cand: Dictionary = {"v": v, "from": int(t.id), "to": i, "sel": g.pick_units(int(t.id), n, claim and n == 1)}
						if search > 0:
							cands.append(cand)
						if best.is_empty() or v > float(best.v):
							best = cand
				t.ready = keep_r
		if search > 0 and cands.size() > 1 and not _searching:
			best = search_move(g, pid, cands, lvl, search)
		if best.is_empty():
			break
		g.play.moves = int(g.play.moves) + 1
		if g.arena_fights and g.is_fight(int(best.from), int(best.to)) and g.needs_arena(pid, int(g.tiles[int(best.to)].owner)):
			# an attack on your units: stop here; the screen fights it out in the Arena, then calls ai_moves again
			events.append({"kind": "fight", "from": int(best.from), "to": int(best.to), "sel": best.sel, "lvl": lvl, "att": pid, "def": int(g.tiles[int(best.to)].owner)})
			return events
		var res: Dictionary = g.execute_move(int(best.from), int(best.to), best.sel, lvl)
		events.append({"kind": "move", "from": int(best.from), "to": int(best.to), "res": res})
	return events


# =====================================================================
# How good the board looks for pid, in rough gold terms.
# =====================================================================

static func tile_worth(g, t: Dictionary) -> float:
	var owner: int = int(t.owner)
	var m: Dictionary = g.mods_of(owner)
	var holding: bool = not g.siege.is_empty() and int(g.siege.pid) == owner
	var v: float = g._army_gold(t.army) + 1.5
	if t.castle:
		v += 45.0 + 4.0 * float(m.castleGold) + (400.0 if holding else 0.0)
	v += int(t.market) * 4.0 * float(m.marketGold)
	if g.homes[owner] == int(t.id):
		v += 600.0
	for key in ["treb", "treb2"]:
		v += 18.0 if int(t[key]) == 2 else (12.0 if int(t[key]) == 1 else 0.0)
	return v


## Expected loss if the other side attacks pid's hexes next turn.
static func exposure(g, pid: int) -> float:
	var loss: float = 0.0
	for t in g.tiles:
		if int(t.owner) != pid:
			continue
		var home: bool = g.homes[pid] == int(t.id)
		var att: Dictionary = {}
		var w: int = 999
		var pr: float = 0.0
		var base_o: Dictionary = g.arena_o(-1, 0, pid, g.arena_map(t)) if g.arena_rules() else {"bonus": g.def_bonus(t), "adv_d": g.def_adv(t), "map": g.arena_map(t)}
		for n in HexGrid.neighbors(int(t.id)):
			var b: Dictionary = g.tiles[n]
			if int(b.owner) >= 0 and int(b.owner) != pid and int(b.troops) > 0:
				var wl: int = g.wall_on(int(t.id), n)
				if home:
					for k in b.army:
						att[k] = int(att.get(k, 0)) + int(b.army[k])
					w = mini(w, wl)
				else:
					var o: Dictionary = base_o.duplicate()
					if not bool(o.get("arena", false)):
						o.wall = wl
					pr = maxf(pr, win_est(b.army, g.def_army(t), o))
		if home and CombatRules.count(att) > 0:
			var oh: Dictionary = base_o.duplicate()
			if not bool(oh.get("arena", false)):
				oh.wall = w
			pr = win_est(att, g.def_army(t), oh)
		if pr > 0.0:
			loss += pr * tile_worth(g, t) * (1.0 if home else 0.5)
	return loss


static func eval_for(g, pid: int) -> float:
	if g.over >= 0:
		return 100000.0 if g.over == pid else -100000.0
	var arena: bool = g.arena_rules()
	var W: Dictionary = prof(g, pid).get("ev", {})
	var np: int = g.players.size()
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
	var fw: float = 0.6 if foes.size() > 1 else 1.0
	for t in g.tiles:
		var o: int = int(t.owner)
		if o < 0:
			continue
		tr[o] += tp(g, t)
		tl[o] += 1
		if t.castle:
			ca[o] += 1
		var x: float = 0.0
		if int(t.treb) == 2:
			x += 10.0 + 4.0 * minf(2.0, treb_spot(g, int(t.id), o))
		elif int(t.treb) == 1:
			x += 12.0
		if not arena:
			for wv in t.walls:
				x += float(wv)
		x += 2.0 * int(t.bk)
		xv[o] += x
	var to_win: int = int(GameData.rules.castles.to_win)
	var V: float = 0.0
	for i in [pid] + foes:
		var sgn: float = 1.0 if i == pid else -fw
		var mv: float = float(GameData.rules.mythical.magic_val) if g.is_myth(i) else 1.0   # 1 magic is worth about 3 gold
		V += sgn * (float(W.get("tr", 3.0)) * tr[i] + 1.5 * tl[i] + float(W.get("ca", 40.0)) * ca[i] + (250.0 if np == 2 and ca[i] >= to_win else 0.0) + float(W.get("inc", 4.0)) * int(g.income_of(i).total) * mv + xv[i])
	var gold: float = float(g.players[pid].gold) * (float(GameData.rules.mythical.magic_val) if g.is_myth(pid) else 1.0)
	V += (0.9 * minf(gold, 40.0) + 0.4 * maxf(0.0, gold - 40.0)) if smart(g, pid) else 0.9 * gold
	V += 1.6 * g.mat_of(pid)
	V -= float(W.get("ex", 1.0)) * exposure(g, pid)
	for e in foes:
		V += float(W.get("ex2", 0.3)) * exposure(g, e) / foes.size()
	var castles: Array = []
	for t in g.tiles:
		if t.castle and int(t.owner) != pid:
			castles.append(int(t.id))
	var dist: Array = bfs(g, castles)
	for t in g.tiles:
		if int(t.owner) == pid and int(t.troops) > 0:
			V -= 0.15 * tp(g, t) * minf(10.0, fin(float(dist[int(t.id)])))
	return V


# =====================================================================
# The computer's Mythical Recruit, Build and Advancements (the browser's mythAi)
# =====================================================================

static func myth_ai(g, pid: int, a: String, later: Array) -> Array:
	var M: Dictionary = GameData.rules.mythical
	var p: Dictionary = g.players[pid]
	var ids: Array = []
	var own: Array = g.tiles.filter(func(t): return int(t.owner) == pid)
	var dE: Array = bfs(g, g.foe_tiles(pid))
	if a == "advance":
		if g.clv_of(pid) < 3 and int(p.gold) >= int(M.castle_up[g.clv_of(pid)]) + 2 and g.myth_up_castle(pid):   # pays for itself in 2 to 4 turns
			ids.append(g.homes[pid])
		while g.mlv_of(pid) < 3 and int(p.gold) >= int(M.mage_up[g.mlv_of(pid)]) + 3 and g.myth_up_mages(pid):
			ids.append(g.homes[pid])
		var threat: Array = own.filter(func(t): return g.mages_on(t) > 0 and int(t.dome) == 0 and enemy_near(g, int(t.id), pid, 1) >= 2)
		threat.sort_custom(func(x, y): return enemy_near(g, int(x.id), pid, 1) > enemy_near(g, int(y.id), pid, 1))
		for t in threat.slice(0, 2):
			if int(p.gold) >= int(M.dome_cost) + 3 and g.myth_dome(pid, int(t.id)):
				ids.append(int(t.id))
		return ids
	if a == "build":
		var spots: Array = []
		for t in own:
			if int(t.tree) > 0 or t.castle or t.terrain != "plain" or fin(float(dE[int(t.id)])) < 1.0:
				continue
			if g.mages_on(t) > 0:
				spots.append(t)
		spots.sort_custom(func(x, y): return fin(float(dE[int(x.id)])) > fin(float(dE[int(y.id)])))
		for t in spots:
			if g.myth_plant(pid, int(t.id)):
				ids.append(int(t.id))
		return ids
	# Recruit: Mages first (about one for every 4 hexes held), then the best units the Mages allow, then Minions with some magic kept back
	var keep: int = 0
	if later.has("advance"):
		keep = mini(int(p.gold) >> 1, int(M.castle_up[g.clv_of(pid)]) if g.clv_of(pid) < 3 else (int(M.mage_up[mini(2, g.mlv_of(pid))]) if g.mage_req_ok(pid, g.mlv_of(pid)) else 0))
	var want: int = maxi(2, ceili(own.size() / 4.0))
	var castles: Array = own.filter(func(t): return t.castle)
	castles.sort_custom(func(x, y): return fin(float(dE[int(x.id)])) < fin(float(dE[int(y.id)])))
	for t in castles:
		while g.mage_total(pid) < want and int(p.gold) - keep >= g.mage_price(pid) and g.myth_buy_mage(pid, int(t.id)):
			ids.append(int(t.id))
	var mage_hexes: Array = own.filter(func(t): return g.mage_lv_at(t) >= 0)
	mage_hexes.sort_custom(func(x, y): return fin(float(dE[int(x.id)])) < fin(float(dE[int(y.id)])))
	for t in mage_hexes:
		for k in ["dragon", "griffin", "minotaur"]:
			while int(p.gold) - keep >= g.conv_price(t, k) and g.myth_convert(pid, int(t.id), k):
				ids.append(int(t.id))
	if not castles.is_empty() and int(p.gold) - keep >= 1 and g.myth_buy_minions(pid, int(castles[0].id), mini(int(p.gold) - keep, 6)):
		ids.append(int(castles[0].id))
	var out: Array = []
	for i in ids:
		if not out.has(i):
			out.append(i)
	return out

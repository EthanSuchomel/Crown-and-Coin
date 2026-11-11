# Godot port, step 4: the computer (ai_player.gd): Fortify regroup and picks, materials, the Dinosaur cards.
import sys
F = sys.argv[1] + '/scripts/rules/ai_player.gd'
s = open(F, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        print('COUNT', n, 'for', old[:160]); sys.exit(1)
    s = s.replace(old, new)

rep('''	for s in n:
		if g.over >= 0:
			break
		events.append_array(run_step(g, pid, cid, s))
	return events''', '''	for s in n:
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
		g.buy_mat(pid, n)''')

rep('''	g.play.step = s
	var a: String = actions[s]
	var raw: int = g.lvl_of(pid, cid, s)
	var lvl: int = 0 if raw == 1 else raw
	events.append({"kind": "step", "action": a})
	var ids: Array = []
	if a == "harvest" or a == "fortify" or a == "channel":
		g._resolve_instant(a)''', '''	g.play.step = s
	var a: String = actions[s]
	var raw: int = g.lvl_of(pid, cid, s)
	var lvl: int = g.cur_lvl()   # the Dinosaurs' cards have their own upgrades, so their usual level stays 0
	events.append({"kind": "step", "action": a})
	var ids: Array = []
	if a == "fortify":
		events.append_array(ai_fortify(g, pid, actions.slice(s + 1)))
		return events
	if a == "build" or a == "recruit":
		g.dino_action_start(pid)
	if a == "harvest" or a == "channel":
		g._resolve_instant(a)''')
rep('''		var bi: int = actions.find("build")
		var build_lvl: int = 0
		if bi > s:
			var braw: int = g.lvl_of(pid, cid, bi)
			build_lvl = 0 if braw == 1 else braw''', '''		var bi: int = actions.find("build")
		var build_lvl: int = 0
		if bi > s and not g.is_dinos(pid):
			var braw: int = g.lvl_of(pid, cid, bi)
			build_lvl = 0 if braw == 1 else braw''')
rep('''		if raw >= 1:
			if g.is_robots(pid):
				g._factory(pid)
			elif g.is_dinos(pid):
				g._populate(pid)
			elif g.is_mammals(pid):''', '''		if raw >= 1:
			if g.is_robots(pid):
				g._factory(pid)
			elif g.is_mammals(pid):''')

# ---------------- the computer's Fortify ----------------
rep('''# =====================================================================
# Helpers
# =====================================================================''', '''# =====================================================================
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


# =====================================================================
# Helpers
# =====================================================================''')

# ---------------- materials in the computer's sums ----------------
rep('''	for t in g.tiles:
		if int(t.owner) != pid or not g.can_treb_at(t) or int(g.players[pid].gold) < g.treb_price(t):
			continue''', '''	for t in g.tiles:
		if int(t.owner) != pid or not g.can_treb_at(t) or g.mat_reach(pid, 0) < g.treb_price(t):
			continue''')
rep('''	if treb and not g.is_dinos(pid) and ai_treb_site(g, pid) < 0 and int(g.players[pid].gold) >= cost_of("fort", lvl) + treb_cost():''',
    '''	if treb and not g.is_dinos(pid) and ai_treb_site(g, pid) < 0 and g.mat_reach(pid, 0) >= cost_of("fort", lvl) + treb_cost():''')
rep('''	var can := func(k): return gold >= cost_of(k, lvl)''', '''	var can := func(k): return g.can_b(pid, k, cost_of(k, lvl), keep)''')
rep('''	if treb and not g.is_dinos(pid) and ai_treb_site(g, pid) < 0 and gold >= cost_of("fort", lvl) + treb_cost():''',
    '''	if treb and not g.is_dinos(pid) and ai_treb_site(g, pid) < 0 and g.mat_reach(pid, keep) >= cost_of("fort", lvl) + treb_cost():''')
rep('''	if g.mamm_now(pid, "build") and gold >= cost_of("wh", lvl) + 6 and not''', '''	if g.mamm_now(pid, "build") and g.mat_reach(pid, keep + 6) >= cost_of("wh", lvl) and not''')
rep('''	if not g.is_dinos(pid) and gold >= cost_of("fort", lvl) + 12:''', '''	if not g.is_dinos(pid) and g.mat_reach(pid, keep + 12) >= cost_of("fort", lvl):''')

rep('''	var keep_r: int = keep_for_recruit(g, pid, later) if sm else 0
	for n in (8 if sm else 6):
		var plan: Dictionary = build_plan2(g, pid, treb, lvl, keep_r) if sm else build_plan(g, pid, treb, lvl)
		if plan.is_empty():
			break
		var keep: int = treb_cost() if (treb and plan.k != "fort" and ai_treb_site(g, pid) >= 0) else 0
		var cost: int = cost_of(plan.k, lvl)
		if int(p.gold) - cost < keep:
			break
		var t: Dictionary = g.tiles[int(plan.id)]
		t[plan.k] = int(t[plan.k]) + 1
		g._note_unlock(pid, plan.k, t)
		p.gold = int(p.gold) - cost
		ids.append(int(plan.id))''', '''	var keep_r: int = keep_for_recruit(g, pid, later) if sm else 0
	# New Nest (Dinosaurs): free barracks first, on the hex with room nearest the enemy
	while g.is_dinos(pid) and int(p.get("fnest", 0)) > 0:
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
		ids.append(int(plan.id))''')

# ai_recruit: what a later Build or trebuchet still needs, in gold
rep('''			var plan2: Dictionary = build_plan2(g, pid, false, build_lvl)
			if not plan2.is_empty():
				var c2b: int = cost_of(plan2.k, build_lvl)''', '''			var plan2: Dictionary = build_plan2(g, pid, false, build_lvl)
			if not plan2.is_empty():
				var c2b: int = g.gold_for(pid, cost_of(plan2.k, build_lvl)) if g.in_mat(plan2.k) else cost_of(plan2.k, build_lvl)   # in gold: materials still to buy''')
rep('''			if not plan.is_empty():
				var c: int = cost_of(plan.k, build_lvl)
				if int(p.gold) >= c + 3:
					keep = c
	if later.has("advance") and ai_treb_site(g, pid) >= 0 and int(p.gold) >= treb_cost() + 3:
		keep = maxi(keep, treb_cost())''', '''			if not plan.is_empty():
				var c: int = g.gold_for(pid, cost_of(plan.k, build_lvl)) if g.in_mat(plan.k) else cost_of(plan.k, build_lvl)
				if int(p.gold) >= c + 3:
					keep = c
	if later.has("advance") and ai_treb_site(g, pid) >= 0:
		var tg: int = g.gold_for(pid, treb_cost())
		if int(p.gold) >= tg + 3:
			keep = maxi(keep, tg)''')

# ai_advance: guards at their price, Armor, materials for trebuchets, walls and upgrades
rep('''			while g.guards_at(gt) < g.guard_max(gt) and int(p.gold) >= g.guard_cost() + sp and g.buy_guard(int(gt.id)):
				ids.append(int(gt.id))''', '''			while g.guards_at(gt) < g.guard_max(gt) and int(p.gold) >= g.guard_cost(pid) + sp and g.buy_guard(int(gt.id)):
				ids.append(int(gt.id))
		if not g.armor_on(pid) and int(p.gold) >= int(g.armor_rules().cost) + sp and g.do_armor(pid):   # Armor (The Hunt)
			ids.append(g.homes[pid])''')
rep('''	var ts: int = ai_treb_site(g, pid)
	if ts >= 0 and g.start_trebuchet(ts):''', '''	var ts: int = ai_treb_site(g, pid)
	if ts >= 0 and g.ai_mat(pid, g.treb_price(g.tiles[ts])) and g.start_trebuchet(ts):''')
rep('''		if best_i < 0 or not g.build_wall(best_i, best_j):
			break''', '''		if best_i < 0 or not (free or g.ai_mat(pid, g.wall_cost())) or not g.build_wall(best_i, best_j):
			break''')
rep('''	var up_cost: Array = GameData.rules.buildings.barracks_upgrade_cost
	var spare: Array = [2, 4, 12] if smart(g, pid) else [8, 8, 20]
	for t in bks:
		# Levels 1 and 2 unlock units, so the computer goes for them sooner.
		while int(t.bk) < 3 and int(p.gold) >= int(up_cost[int(t.bk)]) + int(spare[int(t.bk)]):''', '''	var spare: Array = [2, 4, 12] if smart(g, pid) else [8, 8, 20]
	for t in bks:
		# Levels 1 and 2 unlock units, so the computer goes for them sooner.
		while int(t.bk) < 3 and g.ai_mat(pid, g.bk_up_cost(pid, int(t.bk)), int(spare[int(t.bk)])):''')
rep('''	if ids.is_empty() and smart(g, pid) and not g.arena_rules() and int(p.gold) >= g.wall_cost() + 8:''',
    '''	if ids.is_empty() and smart(g, pid) and not g.arena_rules() and g.mat_reach(pid, 8) >= g.wall_cost():''')
rep('''			if not sides.is_empty() and g.build_wall(int(h.id), int(sides[0])):''',
    '''			if not sides.is_empty() and g.ai_mat(pid, g.wall_cost(), 8) and g.build_wall(int(h.id), int(sides[0])):''')

# evaluation: materials in store are worth a little under the 2 gold they cost
rep('''	V += (0.9 * minf(gold, 40.0) + 0.4 * maxf(0.0, gold - 40.0)) if smart(g, pid) else 0.9 * gold''',
    '''	V += (0.9 * minf(gold, 40.0) + 0.4 * maxf(0.0, gold - 40.0)) if smart(g, pid) else 0.9 * gold
	V += 1.6 * g.mat_of(pid)''')

# the Mythical: a Mage that moved can plant
rep('''			if int(t.tree) > 0 or t.castle or t.terrain != "plain" or fin(float(dE[int(t.id)])) < 1.0:
				continue
			for k in ["mage0", "mage1", "mage2", "mage3"]:
				if int(t.ready.get(k, 0)) > 0:
					spots.append(t)
					break''', '''			if int(t.tree) > 0 or t.castle or t.terrain != "plain" or fin(float(dE[int(t.id)])) < 1.0:
				continue
			if g.mages_on(t) > 0:
				spots.append(t)''')

open(F, 'w', encoding='utf-8').write(s)
print('ai ok')

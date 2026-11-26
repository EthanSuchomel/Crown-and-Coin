"""Godot: the new cards' upgrades (browser commit 627cb37, dev/card-upgrades-v2). Card upgrades on again, for every
faction (the Mythical too); the old per-card and generic upgrade effects are off.
Usage: python3 p22_card_ups.py GODOT_FOLDER NEW_CARDS_JSON"""
import sys, json, os
R=sys.argv[1].rstrip('/')+'/'; NC=json.load(open(sys.argv[2]))
D=os.path.dirname(os.path.abspath(__file__))+'/../card-upgrades-v2/godot/'
def edit(f, pairs):
    t=open(R+f,encoding='utf8').read()
    for a,b in pairs:
        assert t.count(a)==1,(f,t.count(a),a[:100]); t=t.replace(a,b)
    open(R+f,'w',encoding='utf8').write(t)
# ---- data ----
rj=R+'data/rules.json'; t=open(rj,encoding='utf8').read()
t=t.replace('"upgrades": false','"upgrades": true, "new_ups": true',1) if '"upgrades": false' in t else t
assert '"new_ups": true' in t, 'rules.json'
t=t.replace("card upgrades off while the new cards settle (no favors toward upgrades, no faction card upgrades)","card upgrades off while the new cards settle; on again 2026-11-24 with the new cards' own upgrades (new_ups, upgrades.json new_cards)")
open(rj,'w',encoding='utf8').write(t)
uj=R+'data/upgrades.json'; u=json.load(open(uj,encoding='utf8')); u['new_cards']=NC
u['_note_new_cards']="Ethan, 2026-11-24: the new cards' upgrades, by card id: [name, what it does] for levels 1-3 of each action. The numbers are in game_state.gd (NU_*)."
json.dump(u,open(uj,'w',encoding='utf8'),indent='\t',ensure_ascii=False)
# ---- game_state.gd ----
G='scripts/rules/game_state.gd'
edit(G,[
("""func card_ups(pid: int) -> bool:
	return ups_on() and (is_dinos(pid) or is_robots(pid) or is_mammals(pid))""","""func card_ups(pid: int) -> bool:
	return ups_on() and (new_ups() or is_dinos(pid) or is_robots(pid) or is_mammals(pid))"""),
("""	if is_myth(pid) or not ups_on():   # Mythical cards don't upgrade yet
		return false""","""	if (is_myth(pid) and not new_ups()) or not ups_on():   # the Mythical upgrade too with the new cards (2026-11-24)
		return false"""),
("""func card_lv(pid: int, cid: String, a: String) -> int:
	var c: Dictionary = card_of(pid, cid)""","""func card_lv(pid: int, cid: String, a: String) -> int:
	if new_ups():
		return 0   # the old card upgrades are off
	var c: Dictionary = card_of(pid, cid)"""),
("""func dk(pid: int, cid: String, a: String) -> int:
	if play.is_empty()""","""func dk(pid: int, cid: String, a: String) -> int:
	if new_ups() or play.is_empty()"""),
("""func dcard(cid: String, a: String) -> Array:
""","""func dcard(cid: String, a: String) -> Array:
	if new_ups():
		return nu_text(cid, a)
"""),
("""func cur_lvl() -> int:
	if play.is_empty():
		return 0
""","""func cur_lvl() -> int:
	if play.is_empty():
		return 0
	if new_ups():   # the new cards: only Climb changes how a Move plays
		return nu_move_lvl(current) if (cur_action() == "move" and not regrouping()) else 0
"""),
("""	if is_robots(pid):
		return 2 if raw >= 1 else 1   # Dual Core (Siege Protocol)""","""	if is_robots(pid) and not new_ups():
		return 2 if raw >= 1 else 1   # Dual Core (Siege Protocol)"""),
("""	if is_robots(pid) and raw >= 2:   # Siege Protocol, the Robots' only Fortify card""","""	if not play.is_empty():
		out.append_array(nu_fortify(pid))   # Border Guard, Border Wall (card 5)
	if is_robots(pid) and raw >= 2 and not new_ups():   # Siege Protocol, the Robots' only Fortify card"""),
("""	if is_robots(pid) and raw >= 3:
		out.append("Home Link""","""	if is_robots(pid) and raw >= 3 and not new_ups():
		out.append("Home Link"""),
("""+ int(mods_of(pid).movesPerAction) + mamm_moves(pid) + (1 if is_myth(pid) else 0)""","""+ int(mods_of(pid).movesPerAction) + mamm_moves(pid) + (1 if is_myth(pid) else 0) + (1 if nu_k(pid, 1, "move") >= 1 else 0) + (1 if nu_k(pid, 1, "move") >= 3 else 0)   # Long March and Charge (card 1)"""),
("""	return (dk(pid, "stamp", "move") >= 1 or dk(pid, "tusks", "move") >= 1) and not play.is_empty()""","""	return (dk(pid, "stamp", "move") >= 1 or dk(pid, "tusks", "move") >= 1 or nu_k(pid, 1, "move") >= 3) and not play.is_empty()"""),
("""	if regrouping() and pid == current:
		return regroup_targets(from, 99 if (dk(pid, "sprot", "fortify") >= 3 and from == homes[pid]) else fx_reach())   # Home Link (Siege Protocol)""","""	if regrouping() and pid == current:
		var c3: int = nu_k(pid, 3, "fortify")   # Home Roads, Home Highways, Open Roads (card 3 Fortify)
		var hm: bool = from == homes[pid]
		var reach: int = 99 if (dk(pid, "sprot", "fortify") >= 3 and hm) else fx_reach()   # Home Link (Siege Protocol)
		if c3 >= 3 or (c3 >= 2 and hm):
			reach = 99
		elif c3 >= 1 and hm:
			reach = maxi(reach, 3)
		var rt: Array[int] = regroup_targets(from, reach)
		if nu_k(pid, 5, "fortify") >= 1 and fx_on() and not bool(play.fx.get("oc", false)):   # Outpost (card 5)
			for x in HexGrid.neighbors(from):
				var X: Dictionary = tiles[x]
				if int(X.owner) == -1 and int(X.troops) == 0 and X.terrain == "plain" and not X.castle and home_guards(X).is_empty() and not rt.has(x):
					rt.append(x)
		return rt"""),
("""	var run: int = int(own_run[lvl])
	var frontier: Array[int] = [from]""","""	if nu_k(pid, 1, "move") >= 1:   # Long March (card 1): across two empty hexes
		for a in HexGrid.neighbors(from):
			var A: Dictionary = tiles[a]
			if not can_enter(a, lvl) or int(A.owner) != -1 or int(A.troops) > 0 or A.castle:
				continue
			for b in HexGrid.neighbors(a):
				var B: Dictionary = tiles[b]
				if b != from and can_enter(b, lvl) and int(B.owner) == -1 and int(B.troops) == 0 and not B.castle:
					out[b] = true
	var run: int = int(own_run[lvl])
	var frontier: Array[int] = [from]"""),
("""	else:
		res.kind = "claim" if prev == -1 else "capture"
	# The hex changes hands.""","""	else:
		res.kind = "claim" if prev == -1 else "capture"
		if prev == -1 and regrouping() and fx_on():
			play.fx.oc = true   # Outpost used
		if prev == -1 and not regrouping() and nu_k(pid, 1, "move") >= 1 and HexGrid.distance(from, to) == 2:   # Long March: the hex crossed is claimed too
			for m in HexGrid.neighbors(from):
				var M: Dictionary = tiles[m]
				if HexGrid.neighbors(to).has(m) and int(M.owner) == -1 and int(M.troops) == 0 and not M.castle and can_enter(m, lvl):
					M.owner = pid
					M.army = {}
					M.ready = {}
					sync_tile(M)
					res.mid = m
					add_log("%s claim two hexes in one move (Long March)." % p.name)
					break
	# The hex changes hands."""),
("""	B.owner = pid
	B.army = {}
	B.ready = {}
	_add_army(to, survivors, false)
	B.braced = -1""","""	B.owner = pid
	B.army = {}
	B.ready = {}
	_add_army(to, survivors, false)
	B.braced = -1
	B.frz = 0
	B.buff = {}"""),
("""	var offline: bool = (dk(pid, "mobil", "move") >= 3 or dk(pid, "tusks", "move") >= 2) and not herd""","""	var offline: bool = (dk(pid, "mobil", "move") >= 3 or dk(pid, "tusks", "move") >= 2 or nu_k(pid, 3, "move") >= 2) and not herd   # ...and Sneak Attack (card 3 Move)"""),
("""		"d_plus": ad if d_arm else 0, "a_arm": a_arm, "d_arm": d_arm, "arm_hp": float(armor_rules().hp), "surprise": offline}""","""		"d_plus": ad if d_arm else 0, "a_arm": a_arm, "d_arm": d_arm, "arm_hp": float(armor_rules().hp), "surprise": offline, "volley": nu_k(pid, 3, "move") >= 3}   # Volley (card 3 Move)"""),
("""	o.map = arena_map(B, int(o.wall))
	return o""","""	o.map = arena_map(B, int(o.wall))
	o.hp_a = NU_BUFF if buff_on(A) else 0.0   # Rally Cry
	o.hp_d = NU_BUFF if buff_on(B) else 0.0
	return o"""),
("""			"mods": fight_mods(current, cur_lvl(), int(tiles[to].owner))}""","""			"mods": nu_mods(fight_mods(current, cur_lvl(), int(tiles[to].owner)), from, to)}"""),
("""	return {"sneak": bool(o.surprise), "plus":""","""	return {"sneak": bool(o.surprise), "volley": bool(o.get("volley", false)), "plus":"""),
("""	if bool(m.get("arm_d", false)):
		out.plus[1 - t] = int(out.plus[1 - t]) + int(ar.dmg)
		out.hp[1 - t] = float(ar.hp)
	return out""","""	if bool(m.get("arm_d", false)):
		out.plus[1 - t] = int(out.plus[1 - t]) + int(ar.dmg)
		out.hp[1 - t] = float(ar.hp)
	if bool(m.get("buf_a", false)):   # Rally Cry
		out.hp[t] = float(out.hp[t]) * NU_BUFF
	if bool(m.get("buf_d", false)):
		out.hp[1 - t] = float(out.hp[1 - t]) * NU_BUFF
	out.volley = t if bool(m.get("volley", false)) else -1   # Volley
	return out


## Rally Cry on either army, for an Arena fight's mods.
func nu_mods(m: Dictionary, from: int, to: int) -> Dictionary:
	m.buf_a = buff_on(tiles[from])
	m.buf_d = buff_on(tiles[to])
	return m"""),
("""		if in_arena:
			o = arena_o(pid, lvl, prev, arena_map(B, W))""","""		if in_arena:
			var hpa: float = float(o.get("hp_a", 0.0))
			var hpd: float = float(o.get("hp_d", 0.0))
			o = arena_o(pid, lvl, prev, arena_map(B, W))
			o.hp_a = hpa
			o.hp_d = hpd"""),
("""		o.surprise = bool(a.surprise)
		o.a_plus = int(a.a_plus)""","""		o.surprise = bool(a.surprise)
		o.volley = bool(a.get("volley", false))
		o.a_plus = int(a.a_plus)"""),
("""			t.ready = t.army.duplicate()
			t.ready.erase("alamo")   # Alamosaurus guards never move
			sync_tile(t)""","""			t.ready = t.army.duplicate()
			t.ready.erase("alamo")   # Alamosaurus guards never move
			if int(t.get("frz", 0)) > 0:   # a frozen army (Freeze) can't move
				t.ready = {}
				t.frz = int(t.frz) - 1
			sync_tile(t)"""),
("""	var total: int = Economy.turn_income(mods_of(pid), hexes, castles, markets, nest) + tusk
	return {"hexes": hexes, "castles": castles, "markets": markets, "nest": nest, "tusk": tusk, "total": total}""","""	var nu: int = nu_income(pid)   # Castle Tax, Tolls, Vaults (card 5 Advancements)
	var total: int = Economy.turn_income(mods_of(pid), hexes, castles, markets, nest) + tusk + nu
	return {"hexes": hexes, "castles": castles, "markets": markets, "nest": nest, "tusk": tusk, "nu": nu, "total": total}"""),
("""	return {"hexes": hexes, "castles": castles, "markets": 0, "nest": 0, "trees": trees, "tree_m": tree_m, "home": home, "total": home + tree_m}""","""	var nu: int = nu_income(pid)   # Castle Magic, Tree Magic (card 4 Harvest); Castle Tax (card 5 Advancements)
	return {"hexes": hexes, "castles": castles, "markets": 0, "nest": 0, "trees": trees, "tree_m": tree_m, "home": home, "nu": nu, "total": home + tree_m + nu}"""),
("""	if a == "harvest":
		var industry: int = 0""","""	if a == "harvest" and int(p.get("no_harv", 0)) > 0:   # taken early (Early Harvest)
		var skip: bool = int(p.no_harv) == turn
		if skip or int(p.no_harv) < turn:
			p.no_harv = 0
		if skip:
			add_log("%s get nothing from this Harvest: they took it early." % p.name)
			return
	if a == "harvest":
		var nh: Dictionary = nu_harvest(current)
		if int(nh.g) > 0:
			p.gold = int(p.gold) + int(nh.g)
		if int(nh.m) > 0:
			p.mat = mat_of(current) + int(nh.m)
		if not nh.why.is_empty():
			add_log("%s harvest more: %s." % [p.name, ", ".join(PackedStringArray(nh.why))])
		var industry: int = 0"""),
("""func dino_action_start(pid: int) -> Array:
	var out: Array = []""","""func dino_action_start(pid: int) -> Array:
	var nu_out: Array = nu_action_start(pid)   # the new cards' upgrades
	if not nu_out.is_empty():
		var rest: Array = _dino_action_start(pid)
		nu_out.append_array(rest)
		return nu_out
	return _dino_action_start(pid)


func _dino_action_start(pid: int) -> Array:
	var out: Array = []"""),
("""	var card: Dictionary = card_of(current, play.card)
	if rg_due(current):""","""	var card: Dictionary = card_of(current, play.card)
	nu_action_end(current)   # Market Day
	if rg_due(current):"""),
("""	var c: int = int(GameData.rules.buildings.cost_by_level[kind][cur_lvl()])
	if not play.is_empty() and is_dinos(current) and cur_action() == "build":""","""	return nu_cost(kind, _build_cost(kind, t))   # the new cards' Free and Cheap Markets and Barracks


func _build_cost(kind: String, t: Dictionary = {}) -> int:
	var c: int = int(GameData.rules.buildings.cost_by_level[kind][cur_lvl()])
	if not play.is_empty() and is_dinos(current) and cur_action() == "build":"""),
("""	pay_b(current, kind, price)
	_dino_built(current, kind, price)""","""	pay_b(current, kind, price)
	nu_built(current, kind, price)
	_dino_built(current, kind, price)"""),
("""func robo_up_cost(pid: int, k: String, t: Dictionary = {}) -> int:
	var c: int = int(GameData.rules.buildings.cost_by_level[k][0])""","""func robo_up_cost(pid: int, k: String, t: Dictionary = {}) -> int:
	var c: int = int(GameData.rules.buildings.cost_by_level[k][0])
	if k == "barracks" and int(players[pid].get("rbk_free", 0)) > 0:
		return 0   # Free Barracks (the new cards)
	if k == "barracks" and int(players[pid].get("rbk_off", -1)) == turn:
		c -= 1   # Cheap Barracks"""),
("""	spend_mat(pid, c)
	t[nk] = 1
	_note_unlock(pid, nk, t)""","""	spend_mat(pid, c)
	if nk == "barracks" and c == 0 and int(players[pid].get("rbk_free", 0)) > 0:
		players[pid].rbk_free = int(players[pid].rbk_free) - 1
	t[nk] = 1
	_note_unlock(pid, nk, t)"""),
("""	var free: bool = ((cur_lvl() >= 1 and lv == 0) or dk(current, "tusks", "advance") >= 1) and not bool(play.free_bk)""","""	var free: bool = ((cur_lvl() >= 1 and lv == 0) or dk(current, "tusks", "advance") >= 1 or nu_k(current, 2, "advance") >= 3) and not bool(play.free_bk)   # ...and Free Upgrade (card 2)"""),
("""	return int(myth().mage_base) + maxi(0, mage_total(pid) - 4) + mlv_of(pid) - (1 if mlv_of(pid) >= 3 else 0)""","""	return int(myth().mage_base) + maxi(0, mage_total(pid) - 4) + mlv_of(pid) - (1 if mlv_of(pid) >= 3 else 0) - myth_off(pid, "mage")"""),
("""	return int(myth().conv[k].m) - (1 if mage_lv_at(t) >= 3 else 0)""","""	return int(myth().conv[k].m) - (1 if mage_lv_at(t) >= 3 else 0) - myth_off(int(t.owner), k)   # and the card upgrades' cheaper units"""),
("""	t.tree = 1
	t.root = int(myth().tree_turns)""","""	t.tree = 1
	t.root = 1 if nu_k(pid, 1, "build") >= 1 else int(myth().tree_turns)   # Quick Roots (card 1 Build)"""),
])
t=open(R+G,encoding='utf8').read().rstrip('\n')+'\n'+open(D+'nu_module.gd',encoding='utf8').read()
open(R+G,'w',encoding='utf8').write(t)
# ---- combat.gd: Volley and Rally Cry in the board's battles ----
edit('scripts/rules/combat.gd',[
("""	var a_plus: float = float(o.get("a_plus", 0))
	while not _alive(A).is_empty()""","""	var a_plus: float = float(o.get("a_plus", 0))
	if bool(o.get("volley", false)):   # Volley (the new cards): the attackers' shooters fire once before it starts
		var V: Dictionary = {}
		for k in A:
			if bool(unit(k).get("rng", false)) and int(A[k].n) > 0:
				V[k] = A[k]
		if not V.is_empty() and not D.is_empty():
			var hv: Dictionary = _strike(V, D, 1.0, 1, {"wall": 0.0, "arm": arm[1], "plus": a_plus, "shield_foe": shield[1], "shield_mine": 0.0,
				"stunned": {}, "sprint": 0.0, "rally": false, "miss_one": false, "wall0": 0.0})
			for k in hv.dmg:
				if bool(o.get("d_arm", false)):
					hv.dmg[k] = float(hv.dmg[k]) / float(o.get("arm_hp", 1.1))
				if float(o.get("hp_d", 0.0)) > 0.0:
					hv.dmg[k] = float(hv.dmg[k]) / float(o.hp_d)
			_apply(D, hv.dmg)
			if bool(hv.any):
				held = false
	while not _alive(A).is_empty()"""),
("""		if bool(o.get("a_arm", false)):
			for k in hits_on_a.dmg:
				hits_on_a.dmg[k] = float(hits_on_a.dmg[k]) / arm_hp""","""		if bool(o.get("a_arm", false)):
			for k in hits_on_a.dmg:
				hits_on_a.dmg[k] = float(hits_on_a.dmg[k]) / arm_hp
		if float(o.get("hp_d", 0.0)) > 0.0:   # Rally Cry: 10% more health
			for k in hits_on_d.dmg:
				hits_on_d.dmg[k] = float(hits_on_d.dmg[k]) / float(o.hp_d)
		if float(o.get("hp_a", 0.0)) > 0.0:
			for k in hits_on_a.dmg:
				hits_on_a.dmg[k] = float(hits_on_a.dmg[k]) / float(o.hp_a)"""),
])
# ---- the Arena: Volley ----
edit('scripts/arena/arena_battle.gd',[
("""var _sneak_t: float = -1.0
""","""var _sneak_t: float = -1.0
var volley: int = -1   # Volley (Crown & Coin's card upgrade): the attacking team, whose shooters fire once as the battle starts
var volley_done: bool = false
"""),
("""	sneak = int(mods.get("sneak", -1)); sneak_hit = false; _sneak_t = -1.0""","""	sneak = int(mods.get("sneak", -1)); sneak_hit = false; _sneak_t = -1.0
	volley = int(mods.get("volley", -1)); volley_done = false"""),
("""func update(dt: float) -> void:
	clock += dt
""","""func update(dt: float) -> void:
	clock += dt
	if volley >= 0 and not volley_done:
		_do_volley()
"""),
])
t=open(R+'scripts/arena/arena_battle.gd',encoding='utf8').read().rstrip('\n')+'''


## Volley: each of the attackers' shooters on the field fires once, at a random enemy it can hit.
func _do_volley() -> void:
	volley_done = true
	for f in F.duplicate():
		if f.team != volley or f.dead or not (bool(f.T.get("ranged", false)) or f.T.has("rocket")):
			continue
		var fs: Array = []
		for t in F:
			if t.team != volley and not t.dead and (not _flying(t) or bool(f.T.get("antiAir", false))):
				fs.append(t)
		if fs.is_empty():
			break
		hit(fs[int(rng.randf() * fs.size()) % fs.size()], f, 1.0, true)
'''
open(R+'scripts/arena/arena_battle.gd','w',encoding='utf8').write(t)
# ---- the computer ----
edit('scripts/rules/ai_player.gd',[
("""		if a == "recruit":
			g._free_troops(pid, lvl)
		ids = myth_ai(g, pid, a, actions.slice(s + 1))""","""		if a == "recruit":
			g._free_troops(pid, lvl)
		if a == "advance":
			ids.append_array(g.nu_ai_advance(pid))   # the new cards' Advancements powers
		ids.append_array(myth_ai(g, pid, a, actions.slice(s + 1)))"""),
("""	elif a == "build":
		ids = ai_build(g, pid, lvl, actions.slice(s + 1))""","""	elif a == "build":
		ids = ai_build(g, pid, lvl, actions.slice(s + 1))
		g.nu_action_end(pid)   # Market Day"""),
("""	elif a == "advance":
		ids = ai_advance(g, pid, lvl)""","""	elif a == "advance":
		ids = g.nu_ai_advance(pid)   # the new cards' Advancements powers
		ids.append_array(ai_advance(g, pid, lvl))"""),
])
print('ok')

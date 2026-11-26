"""Godot main.gd: the new card upgrades' buttons (Border Claim, Early Harvest, Rally Cry, Freeze, Relocate), Scouts
(without it an enemy hex shows how many units, not which), and the Mythical's upgrades. Usage: python3 p22_card_ups_ui.py GODOT_FOLDER"""
import sys
R=sys.argv[1].rstrip('/')+'/'
def edit(f, pairs):
    t=open(R+f,encoding='utf8').read()
    for a,b in pairs:
        assert t.count(a)==1,(f,t.count(a),a[:100]); t=t.replace(a,b)
    open(R+f,'w',encoding='utf8').write(t)
M='scripts/ui/main.gd'
edit(M,[
("""var robo_up: String = ""   # the Robots' factory upgrade being placed during Advancements: "barracks" or "fort"
""","""var robo_up: String = ""   # the Robots' factory upgrade being placed during Advancements: "barracks" or "fort"
var nu_mode: Dictionary = {}   # the new card upgrades: {m: claim | freeze | mvb, from, k} while picking a hex
"""),
("""Mythical cards don't upgrade yet." % [int(M.ch_mage), int(M.ch_castle)], 14, LICHEN))""","""%s" % [int(M.ch_mage), int(M.ch_castle), "Every 2nd time you play a card, one of its actions goes up a level." if GameState.ups_on() else "Mythical cards don't upgrade yet."], 14, LICHEN))"""),
("""	if g.is_myth(pid) or not GameState.ups_on():   # no upgrades (Mythical, or card upgrades off): just the colour edge""","""	if (g.is_myth(pid) and not GameState.new_ups()) or not GameState.ups_on():   # no upgrades (card upgrades off): just the colour edge"""),
("""		if g.is_myth(0):
			up_txt = ("This card has no other actions. " """,""" 		if g.is_myth(0) and not GameState.new_ups():
			up_txt = ("This card has no other actions. " """.replace(' \t\t','\t\t')),
("""	if g.is_myth(pid) and a != "fortify":
		return _myth_action_desc(a, pid)""","""	if g.is_myth(pid) and a != "fortify":
		var md: String = _myth_action_desc(a, pid)
		if raw >= 1 and g.d_up(pid, cid, a):   # the new cards' upgrades (the Mythical too)
			md += ". " + ". ".join(PackedStringArray(g.dcard(cid, a).slice(0, raw).map(func(x): return "%s: %s" % [x[0], x[1]])))
		return md"""),
("""func _action_controls(box: VBoxContainer) -> void:
	var a0: String = g.cur_action()""","""func _action_controls(box: VBoxContainer) -> void:
	_nu_controls(box)   # the new card upgrades' buttons
	var a0: String = g.cur_action()"""),
("""		elif mv_bk >= 0 and g.cur_action() == "advance":
			board.targets = g.mamm_bk_spots(0, mv_bk)   # Den Move""","""		elif not nu_mode.is_empty():
			board.targets = _nu_targets()   # Border Claim, Freeze, Relocate
		elif mv_bk >= 0 and g.cur_action() == "advance":
			board.targets = g.mamm_bk_spots(0, mv_bk)   # Den Move"""),
("""	if g.cur_action() == "move" and sel >= 0 and board.targets.has(i):
		_open_move(sel, i)
		return""","""	if not nu_mode.is_empty():   # Border Claim, Freeze, Relocate: tap a ringed hex
		var md: Dictionary = nu_mode
		nu_mode = {}
		if _nu_targets_for(md).has(i):
			if String(md.m) != "freeze":
				sel = i
			_do(func(): _nu_tap(md, i))
			return
	if g.cur_action() == "move" and sel >= 0 and board.targets.has(i):
		_open_move(sel, i)
		return"""),
("""	robo_up = ""
	mv_bk = -1
	var before: int = g.log_n
	g.next_step()""","""	robo_up = ""
	mv_bk = -1
	nu_mode = {}
	var before: int = g.log_n
	g.next_step()"""),
("""	if int(t.troops) > 0:
		vb.add_child(_rich(_army_icons(t.army), 14))""","""	if int(t.troops) > 0:
		if owner == 0 or owner < 0 or g.nu_see(0):
			vb.add_child(_rich(_army_icons(t.army), 14))
		else:   # without Scouts (card 4 Advancements) an enemy army shows only how many
			vb.add_child(_rich("%d unit%s" % [int(t.troops), "" if int(t.troops) == 1 else "s"], 14))"""),
("""			lines.append("Defending: " + _army_icons(b.army))""","""			lines.append("Defending: " + (_army_icons(b.army) if g.nu_see(0) else "%d unit%s" % [int(b.troops), "" if int(b.troops) == 1 else "s"]))"""),
])
t=open(R+M,encoding='utf8').read().rstrip('\n')+'''


# =====================================================================
# The new cards' upgrades (2026-11-24): the Advancements powers and Relocate, in the card you're playing
# =====================================================================

func _nu_targets_for(md: Dictionary) -> Array:
	match String(md.get("m", "")):
		"claim":
			return g.nu_claimable(0)
		"freeze":
			return g.nu_freezable(0)
		"mvb":
			return g.nu_move_spots(0, int(md.from), String(md.k))
	return []


func _nu_targets() -> Array:
	return _nu_targets_for(nu_mode)


func _nu_tap(md: Dictionary, i: int) -> void:
	match String(md.m):
		"claim":
			g.nu_claim(0, i)
		"freeze":
			g.nu_freeze(0, i)
		"mvb":
			g.nu_move_b(0, int(md.from), String(md.k), i)


func _nu_kind_name(k: String) -> String:
	return "factory" if k == "factory" else ("Watering Hole" if k == "wh" else ("fortress" if k == "fort" else k))


func _nu_controls(box: VBoxContainer) -> void:
	if not GameState.new_ups() or g.play.is_empty() or g.current != 0:
		return
	if sel >= 0 and int(g.tiles[sel].owner) > 0 and int(g.tiles[sel].troops) > 0 and g.nu_see(0) and g.cur_action() != "move":
		box.add_child(_rich("[color=#b9a984]Enemy (Scouts):[/color] " + _army_icons(g.tiles[sel].army), 14))
	if g.fx_on():
		if g.regrouping() and g.nu_k(0, 5, "fortify") >= 1 and not bool(g.play.fx.get("oc", false)):
			box.add_child(_label("Outpost: one regroup move can claim an empty hex next to your land.", 13, LICHEN))
		return
	var a: String = g.card_action()
	var cancel := func():
		nu_mode = {}
		refresh()
	if a == "build" and not g.is_myth(0) and g.nu_k(0, 4, "build") >= 1 and not bool(g.play.get("n_mb", false)):
		if String(nu_mode.get("m", "")) == "mvb":
			var n: int = g.nu_move_spots(0, int(nu_mode.from), String(nu_mode.k)).size()
			box.add_child(_label(("Relocate: tap a ringed hex of yours next door to move the %s there." % _nu_kind_name(String(nu_mode.k))) if n > 0 else "Relocate: none of your hexes next door has room for it.", 13, LICHEN))
			box.add_child(_button("Cancel", cancel))
		elif _sel_mine() and not g.nu_movable(0, g.tiles[sel]).is_empty():
			for k in g.nu_movable(0, g.tiles[sel]):
				var kk: String = String(k)
				box.add_child(_button("Relocate: move this %s" % _nu_kind_name(kk), func():
					nu_mode = {"m": "mvb", "from": sel, "k": kk}
					refresh()))
		else:
			box.add_child(_label("Relocate: tap one of your hexes with a building to move it to a hex of yours next door.", 13, LICHEN))
	if a == "advance":
		var v2: int = g.nu_k(0, 2, "advance")
		var v4: int = g.nu_k(0, 4, "advance")
		var m: String = String(nu_mode.get("m", ""))
		if m == "claim" or m == "freeze":
			box.add_child(_label("Border Claim: tap a ringed hex to claim it." if m == "claim" else "Freeze: tap a ringed enemy army to freeze it for its next %d turns." % GameState.NU_FREEZE, 13, LICHEN))
			box.add_child(_button("Cancel", cancel))
			return
		if v2 >= 1 and not bool(g.play.get("n_cl", false)) and not g.nu_claimable(0).is_empty():
			box.add_child(_button("Border Claim: claim a hex", func():
				nu_mode = {"m": "claim"}
				refresh()))
		if v2 >= 2 and not bool(g.play.get("n_eh", false)) and int(g.tiles[g.homes[0]].owner) == 0:
			box.add_child(_button("Early Harvest: harvest now", func(): _do(func(): g.nu_early(0))))
		if v4 >= 2 and not bool(g.play.get("n_bf", false)):
			if _sel_mine() and int(g.tiles[sel].troops) > 0:
				box.add_child(_button("Rally Cry: +10% health here", func(): _do(func(): g.nu_buff(0, sel))))
			else:
				box.add_child(_label("Rally Cry: tap one of your armies to give it +10% health until the end of your next turn.", 13, LICHEN))
		if v4 >= 3 and not bool(g.play.get("n_fz", false)) and not g.nu_freezable(0).is_empty():
			box.add_child(_button("Freeze an enemy army", func():
				nu_mode = {"m": "freeze"}
				refresh()))
'''
open(R+M,'w',encoding='utf8').write(t)
print('ui ok')

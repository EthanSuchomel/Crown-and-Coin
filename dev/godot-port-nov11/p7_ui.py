# Godot port, step 7: main.gd (the Fortify picks and regroup, buying materials, prices in materials, the Dinosaur
# cards' own upgrades and head shots, Armor, Calling, Two Herds, texts).
import sys
F = sys.argv[1] + '/scripts/ui/main.gd'
s = open(F, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        print('COUNT', n, 'for', old[:160]); sys.exit(1)
    s = s.replace(old, new)

MAT = 'res://art/ui/mat.png'

# ---------------- the header: materials, tap to buy more ----------------
rep('''	for spec in [["Full", func(): _toggle_full()], ["?", func(): _open_help()], ["Log", func(): _open_log()], ["New", func(): show_title()]]:
		var b := _button(spec[0], spec[1])
		b.add_theme_font_size_override("font_size", 13)
		b.add_theme_stylebox_override("normal", _small_button_box())
		btns.add_child(b)''', '''	for spec in [["Full", func(): _toggle_full()], ["?", func(): _open_help()], ["Log", func(): _open_log()], ["New", func(): show_title()]]:
		var b := _button(spec[0], spec[1])
		b.add_theme_font_size_override("font_size", 13)
		b.add_theme_stylebox_override("normal", _small_button_box())
		btns.add_child(b)
	if g.uses_mat(0):   # materials: tap to buy more at your markets
		var spacer := Control.new()
		spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		btns.add_child(spacer)
		var mb := _button("%%d materials" %% g.mat_of(0), func(): _open_trade())
		mb.tooltip_text = "Materials: tap to buy more at your markets"
		mb.add_theme_font_size_override("font_size", 13)
		mb.add_theme_stylebox_override("normal", _small_button_box())
		if ResourceLoader.exists("%s"):
			mb.icon = load("%s")
			mb.add_theme_constant_override("icon_max_width", 18)
		btns.add_child(mb)''' % (MAT, MAT))

# ---------------- cards: the Dinosaur upgrade names and head shots ----------------
rep('''		if l > 0:
			up = "  [color=#efc15a]%s[/color]" % _level_name(0, a, l)''', '''		if l > 0:
			up = "  [color=#efc15a]%s[/color]" % _level_name(0, a, l, cid)''')
rep('''	if g.upgrade_due(0, cid):
		vb.add_child(_label("▲ Playing it now upgrades an action", 12, GOLD))
	_ignore_mouse(hb)''', '''	if g.upgrade_due(0, cid):
		vb.add_child(_label("▲ Playing it now upgrades an action", 12, GOLD))
	var art: TextureRect = _card_art(0, cid, 92.0)
	if art != null:
		hb.add_child(art)
	_ignore_mouse(hb)''')
rep('''func _level_name(pid: int, a: String, l: int) -> String:
	var named: Dictionary = GameData.upgrades[g.players[pid].faction + "_named"][a]''', '''## A Dinosaur card's head shot (Ethan's OpenArt pictures), or null.
func _card_art(pid: int, cid: String, h: float) -> TextureRect:
	var path: String = String(GameData.factions[g.players[pid].faction].get("card_art", {}).get(cid, ""))
	if path == "" or not ResourceLoader.exists(path):
		return null
	var p := _pic(path, Vector2(h, h))
	p.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	p.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return p


func _level_name(pid: int, a: String, l: int, cid: String = "") -> String:
	if g.d_up(pid, cid, a):   # the Dinosaurs: each card's own upgrades
		var d: Array = g.dcard(cid, a)
		return ", ".join(PackedStringArray(d.slice(0, l).map(func(x): return String(x[0]))))
	var named: Dictionary = GameData.upgrades[g.players[pid].faction + "_named"][a]''')
rep('''	var head := HBoxContainer.new()
	head.add_child(_label(String(card.name), 21, BONE, true))''', '''	var head := HBoxContainer.new()
	var hart: TextureRect = _card_art(pid, cid, 40.0)
	if hart != null:
		head.add_child(hart)
	head.add_child(_label(String(card.name), 21, BONE, true))''')
rep('''		var desc: String = _action_desc(a, pid, raw)
		var name_txt: String = "[s]%s[/s]" % ACTION_NAMES[a] if done else ACTION_NAMES[a]
		var lvl_txt: String = ("  [color=#efc15a]%s[/color]" % _level_name(pid, a, raw)) if raw > 0 else ""''',
    '''		var desc: String = _action_desc(a, pid, raw, cid)
		var name_txt: String = "[s]%s[/s]" % ACTION_NAMES[a] if done else ACTION_NAMES[a]
		var lvl_txt: String = ("  [color=#efc15a]%s[/color]" % _level_name(pid, a, raw, cid)) if raw > 0 else ""''')
rep('''	elif pid == 0:
		var last: bool = step >= card.actions.size() - 1
		if not undo_stack.is_empty():
			var ub := _button("↶ Undo", func(): _undo())
			ub.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			foot.add_child(ub)
		var next := _button("End turn" if last else "Next action  ▶", func(): _next_action(), true)''', '''	elif pid == 0:
		var last: bool = g.last_step_now()
		if not undo_stack.is_empty():
			var ub := _button("↶ Undo", func(): _undo())
			ub.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			foot.add_child(ub)
		var next_txt: String = "End turn" if last else "Next action  ▶"
		if g.regrouping():
			next_txt = "Done regrouping  ▶"
		elif g.fx_on() and String(g.play.fx.ph) == "pick" and g.play.fx.done.size() < int(g.play.fx.n):
			next_txt = "Skip: end turn" if last else "Skip  ▶"
		var next := _button(next_txt, func(): _next_action(), true)''')

# ---------------- action texts ----------------
rep('''func _action_desc(a: String, pid: int, raw: int) -> String:
	if g.is_myth(pid) and a != "fortify":
		return _myth_action_desc(a, pid)
	var lvl: int = 0 if raw == 1 else raw''', '''func _action_desc(a: String, pid: int, raw: int, cid: String = "") -> String:
	if g.is_myth(pid) and a != "fortify":
		return _myth_action_desc(a, pid)
	var lvl: int = 0 if (raw == 1 or g.is_dinos(pid)) else raw   # the Dinosaurs' cards use their own upgrades''')
rep('''		"build":
			txt = "Build as many Markets and Barracks as you can afford" if g.is_dinos(pid) else "Build as many Markets, Forts and Barracks as you can afford"
			if lvl > 0:
				var c: Dictionary = GameData.rules.buildings.cost_by_level
				if g.is_dinos(pid):
					txt += " (Market %d, Barracks %d gold)" % [int(c.market[lvl]), int(c.barracks[lvl])]
				else:
					txt += " (Market %d, Fort %d, Barracks %d gold)" % [int(c.market[lvl]), int(c.fort[lvl]), int(c.barracks[lvl])]''',
    '''		"build":
			var c: Dictionary = GameData.rules.buildings.cost_by_level
			if g.is_dinos(pid):
				txt = "Build as many as you can afford: Markets (%d gold) and Barracks (%s). Buy materials at your markets" % [int(c.market[lvl]), g.mat_txt(int(c.barracks[lvl]))]
			else:
				txt = "Build as many as you can afford: Markets (%d gold), Forts (%s) and Barracks (%s). Buy materials at your markets" % [int(c.market[lvl]), g.mat_txt(int(c.fort[lvl])), g.mat_txt(int(c.barracks[lvl]))]''')
rep('''				txt = "Spend gold on as many as you can afford: upgrade a barracks (%d, %d, %d gold for levels 1 to 3%s), hire Alamosaurus guards for a barracks (%d gold each, up to %d per barracks), wake or stoke the volcano at your home castle (%d, %d, %d gold for levels 1 to 3), or build walls on a hex's sides (%d gold each)" % [''',
    '''				txt = "Do as many as you can afford: upgrade a barracks (%d, %d, %d materials for levels 1 to 3%s), hire Alamosaurus guards for a barracks (%d gold each, up to %d per barracks), wake or stoke the volcano at your home castle (%d, %d, %d gold for levels 1 to 3), or build walls on a hex's sides (%d materials each)" % [''')
rep('''				txt = "Spend gold on as many as you can afford: upgrade a barracks (%d, %d, %d gold for levels 1 to 3%s), start a trebuchet on a hex with a fort (%d gold) or on a castle (up to 2: %d then %d gold), or build walls on a hex's sides (%d gold each)" % [''',
    '''				txt = "Do as many as you can afford, all paid in materials: upgrade a barracks (%d, %d, %d for levels 1 to 3%s), start a trebuchet on a hex with a fort (%d) or on a castle (up to 2: %d then %d), or build walls on a hex's sides (%d each)" % [''')
rep('''		"fortify":
			txt = ("First, every castle and fort you hold gains 1 troop. Then every" if lvl >= 3 else "Every") + " hex with your troops gets +%d defense" % int(m.fortifyBonus)
			if lvl >= 1:
				txt += " (+2 at forts and castles)"
			txt += " until your next turn"
			if lvl >= 2:
				txt += ". Troops in forts and castles also defend with advantage"
	if raw >= 1:
		txt += ". " + String(GameData.upgrades[g.players[pid].faction + "_named"][a].desc)
	return txt''', '''		"fortify":
			var n: int = g.fx_picks_at(pid, raw)
			txt = "A wild card. First regroup: move your units up to %d hexes between your own hexes, as often as you like (no attacks or claiming). Then %s Build, Advancements and Recruit, played like the basic action" % [g.regroup_reach(), "do all three of" if n >= 3 else ("pick two of" if n == 2 else "pick one of")]
	if g.is_dinos(pid):
		if raw >= 1 and g.d_up(pid, cid, a):
			var d: Array = g.dcard(cid, a)
			txt += ". " + ". ".join(PackedStringArray(d.slice(0, raw).map(func(x): return "%s: %s" % [x[0], x[1]])))
	elif raw >= 1:
		txt += ". " + String(GameData.upgrades[g.players[pid].faction + "_named"][a].desc)
	return txt''')

# ---------------- the card column during a Fortify, and materials ----------------
rep('''func _action_controls(box: VBoxContainer) -> void:
	var a0: String = g.cur_action()
	if g.is_myth(0) and (a0 == "recruit" or a0 == "build" or a0 == "advance"):
		_myth_controls(box, a0)
		return
	match g.cur_action():
		"recruit":
			_recruit_controls(box)
		"build":
			_build_controls(box)
		"advance":
			_advance_controls(box)
		"move":
			_move_controls(box)''', '''func _action_controls(box: VBoxContainer) -> void:
	var a0: String = g.cur_action()
	if g.fx_on():
		_fx_head(box)
		if a0 == "fortify":
			_fx_pick_controls(box)
			return
	if g.is_myth(0) and (a0 == "recruit" or a0 == "build" or a0 == "advance"):
		_myth_controls(box, a0)
		return
	match a0:
		"recruit":
			if g.dpick_waiting():
				box.add_child(_rich("[color=#efc15a]Calling: tap one of your nesting grounds for the free units: %s[/color]" % _army_icons(g.play.dpick), 14))
			_recruit_controls(box)
		"build":
			_mat_row(box)
			_build_controls(box)
		"advance":
			_mat_row(box)
			_advance_controls(box)
		"move":
			if g.regrouping():
				_regroup_controls(box)
			else:
				_move_controls(box)


## The heading while a Fortify runs: the regroup, or which pick is being played.
func _fx_head(box: VBoxContainer) -> void:
	var f: Dictionary = g.play.fx
	if f.ph == "regroup":
		box.add_child(_rich("%s [b]Regroup[/b]" % _img("fortify", 24), 16))
	elif f.ph == "act":
		box.add_child(_rich("%s [b]Fortify%s: %s %s[/b]" % [_img("fortify", 24), (" (%d of %d)" % [f.done.size() + 1, int(f.n)]) if int(f.n) > 1 else "", _img(String(f.cur), 24), ACTION_NAMES[String(f.cur)]], 16))


const FX_NOTES := {"build": "Markets, forts, barracks", "advance": "Barracks, trebuchets, walls", "recruit": "Train units", "move": "Claim and attack"}
const FX_NOTES_DINO := {"build": "Markets and barracks", "advance": "Barracks, guards, volcano, walls"}
const FX_NOTES_MYTH := {"build": "Life Trees", "advance": "Mages, castle, domes", "recruit": "Minions, Mages, monsters"}

## Fortify's picks: Build, Advancements or Recruit (and Move with Pack Call's On the Move).
func _fx_pick_controls(box: VBoxContainer) -> void:
	var f: Dictionary = g.play.fx
	var left: int = int(f.n) - f.done.size()
	var head: String = "Pick one"
	if left <= 0:
		head = "Fortify done"
	elif int(f.n) >= 3:
		head = ("%d more to do, in any order" % left) if f.done.size() > 0 else "Do all three, in any order"
	elif f.done.size() > 0:
		head = "Pick one more"
	elif int(f.n) == 2:
		head = "Pick two, one at a time"
	box.add_child(_rich("%s [b]%s[/b]" % [_img("fortify", 24), head], 16))
	var grid := GridContainer.new()
	var picks: Array = g.fx_pick_list()
	grid.columns = picks.size()
	grid.add_theme_constant_override("h_separation", 6)
	box.add_child(grid)
	for k in picks:
		var did: bool = f.done.has(k)
		var note: String = String(FX_NOTES_MYTH.get(k, FX_NOTES[k])) if g.is_myth(0) else String((FX_NOTES_DINO if g.is_dinos(0) else {}).get(k, FX_NOTES[k]))
		var kk: String = k
		var b := _build_button("res://art/ui/%s.png" % k, ACTION_NAMES[k], "Done" if did else note, func(): _do(func(): g.fx_choose(kk)), not did and left > 0)
		b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		b.alignment = HORIZONTAL_ALIGNMENT_CENTER
		b.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
		b.vertical_icon_alignment = VERTICAL_ALIGNMENT_TOP
		b.add_theme_font_size_override("font_size", 13)
		b.autowrap_mode = TextServer.AUTOWRAP_WORD
		b.custom_minimum_size.y = 96
		grid.add_child(b)
	var tail: String = "Each plays like the basic action, without this card's upgrades."
	if g.uses_mat(0):
		tail += " You have %d gold and %s." % [int(g.players[0].gold), g.mat_txt(g.mat_of(0))]
	_hint(box, tail)


## Fortify's regroup: free moves inside your own land.
func _regroup_controls(box: VBoxContainer) -> void:
	var ready: int = 0
	for t in g.tiles:
		if int(t.owner) == 0:
			ready += int(t.fresh)
	if _sel_mine() and int(g.tiles[sel].troops) > 0:
		var parts: Array = []
		for k in g._by_strength(g.tiles[sel].ready):
			parts.append("[img=30x20]res://art/units/%s.png[/img] %d" % [k, int(g.tiles[sel].ready[k])])
		box.add_child(_rich("Here: " + ("  ".join(parts) if not parts.is_empty() else "[color=#a5b49e]nobody ready to move[/color]"), 14))
	_hint(box, "Tap a hex with your units, then a highlighted hex of yours. Regroup moves are free: as many as you like, up to %d hexes through your own land (not mountains), but no attacks or claiming. Units that regroup can still move again later this turn. You have %d unit%s ready." % [g.regroup_reach(), ready, "" if ready == 1 else "s"])
	if int(g.play.fx.get("rally", 0)) > 0 and _sel_mine():
		box.add_child(_button("Rally: bring every unit you have here", func(): _do(func(): g.rally_to(sel))))
	if int(g.play.fx.get("far", 0)) > 0:
		_hint(box, "Join Up: one regroup move can go any distance through your land.")
	var n: int = int(g.play.fx.n)
	_hint(box, "Then tap Done regrouping to pick %s." % ("the order of Build, Advancements and Recruit" if n >= 3 else ("two of Build, Advancements and Recruit" if n == 2 else "Build, Advancements or Recruit")))


## Gold and materials, with a button to buy materials (Build and Advancements).
func _mat_row(box: VBoxContainer) -> void:
	if not g.uses_mat(0):
		return
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 8)
	box.add_child(row)
	var l := _rich("[img=20x20]%s[/img] [b]%s[/b]  ·  %s %d gold" % ["%s", g.mat_txt(g.mat_of(0)), _img("coin", 18), int(g.players[0].gold)], 15)
	l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	l.autowrap_mode = TextServer.AUTOWRAP_OFF
	row.add_child(l)
	var left: int = g.mat_left(0)
	var b := _button(("Buy materials (%d left)" % left) if left > 0 else "Buy materials", func(): _open_trade())
	b.add_theme_font_size_override("font_size", 13)
	b.disabled = left <= 0 or int(g.players[0].gold) < g.mat_price()
	row.add_child(b)


## Buying materials at your markets: up to 3 a turn from each market (and from your home castle), 2 gold each.
func _open_trade() -> void:
	if g == null or not g.uses_mat(0):
		return
	var me: Dictionary = g.players[0]
	var left: int = g.mat_left(0)
	var mx: int = mini(left, int(me.gold) / g.mat_price())
	var mk: int = g.markets_of(0)
	var hm: bool = g.home_market(0)
	var mine: bool = g.current == 0 and not busy and g.over < 0
	var srcs: Array = []
	if mk > 0:
		srcs.append("%d market%s" % [mk, "" if mk == 1 else "s"])
	if hm:
		srcs.append("your home castle")
	var box := _open_overlay("Materials", 520.0)
	var uses: String = "barracks, barracks upgrades and walls" if g.is_dinos(0) else ("forts, barracks, barracks upgrades, walls, trebuchets and Watering Holes" if g.is_mammals(0) else "forts, barracks, barracks upgrades, walls and trebuchets")
	box.add_child(_rich("You have [b]%s[/b] and [b]%d gold[/b]. Materials pay for %s. Units and markets cost gold." % [g.mat_txt(g.mat_of(0)), int(me.gold), uses], 15))
	var per: int = int(GameData.rules.materials.per_market)
	box.add_child(_label("Each market sells up to %d a turn, and your home castle counts as one, at %d gold each. " % [per, g.mat_price()] + (("With %s you can buy %d a turn; %d left this turn." % [" and ".join(srcs), g.mat_cap(0), left]) if not srcs.is_empty() else "You have no markets and no home castle to buy from."), 14, LICHEN))
	if not mine:
		box.add_child(_label("You can buy on your turn.", 14, LICHEN))
		box.add_child(_button("OK", func(): _close_overlay(), true))
		return
	if mx <= 0:
		box.add_child(_label("Your markets have sold all they can this turn. More markets sell more." if left <= 0 else "You need %d gold for each material." % g.mat_price(), 14, LICHEN))
		box.add_child(_button("OK", func(): _close_overlay(), true))
		return
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 8)
	box.add_child(row)
	var spin := HSlider.new()
	spin.min_value = 1
	spin.max_value = mx
	spin.step = 1
	spin.value = mx
	spin.custom_minimum_size = Vector2(220, 28)
	spin.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	spin.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	var minus := _button("−", func(): spin.value = maxf(1.0, spin.value - 1.0))
	var plus := _button("+", func(): spin.value = minf(float(mx), spin.value + 1.0))
	for pb in [minus, plus]:
		pb.custom_minimum_size = Vector2(40, 36)
		pb.add_theme_font_size_override("font_size", 20)
	var count_l := _label(str(mx), 22, BONE, true)
	count_l.custom_minimum_size.x = 40
	count_l.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	row.add_child(minus)
	row.add_child(spin)
	row.add_child(plus)
	row.add_child(count_l)
	var btns := HBoxContainer.new()
	btns.add_theme_constant_override("separation", 8)
	box.add_child(btns)
	btns.add_child(_button("Cancel", func(): _close_overlay()))
	var buy := _button("Buy %d for %d gold" % [mx, mx * g.mat_price()], func():
		var v: int = int(spin.value)
		_close_overlay()
		_do(func(): g.buy_mat(0, v)), true)
	buy.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	btns.add_child(buy)
	var upd := func(v):
		count_l.text = str(int(v))
		buy.text = "Buy %d for %d gold" % [int(v), int(v) * g.mat_price()]
		minus.disabled = v <= 1
		plus.disabled = v >= mx
	spin.value_changed.connect(upd)
	upd.call(spin.value)''')
s = s.replace('[img=20x20]%s[/img] [b]%s[/b]  ·  %s %d gold" % ["%s", ', '[img=20x20]%s[/img] [b]%%s[/b]  ·  %%s %%d gold" %% [' % MAT if False else '[img=20x20]' + MAT + '[/img] [b]%s[/b]  ·  %s %d gold" % [', 1)

rep('''		_hint(box, "▸ Tap a building above the hex to build it. Markets earn +2 gold a turn; %s unlock units.%s" % ["barracks" if g.is_dinos(0) else "forts and barracks", " Castles can only take markets." if g.tiles[sel].castle else ""])''',
    '''		_hint(box, "▸ Tap a building above the hex to build it. Markets earn +2 gold a turn and sell you materials; %s unlock units.%s" % ["barracks" if g.is_dinos(0) else "forts and barracks", " Castles can only take markets." if g.tiles[sel].castle else ""])''')
rep('''		_hint(box, "▸ Tap an option above the hex: upgrade the barracks, hire an Alamosaurus guard (the volcano, at your home castle), or build walls." if g.is_dinos(0) else "▸ Tap an option above the hex: upgrade the barracks, start a trebuchet, or build walls.")''',
    '''		_hint(box, ("▸ Tap an option above the hex: upgrade the barracks, hire an Alamosaurus guard (the volcano%s, at your home castle), or build walls." % (" and Armor" if g.can_armor(0) else "")) if g.is_dinos(0) else "▸ Tap an option above the hex: upgrade the barracks, start a trebuchet, or build walls.")''')

# ---------------- leftover warnings ----------------
rep('''func _leftover_warning() -> String:
	var a: String = g.cur_action()
	var gold: int = int(g.players[0].gold)''', '''func _leftover_warning() -> String:
	var a: String = g.cur_action()
	var gold: int = int(g.players[0].gold)
	var mats: int = g.mat_of(0)
	if g.fx_on():
		var f: Dictionary = g.play.fx
		if f.ph == "regroup":
			return ""   # regrouping is optional
		if f.ph == "pick":
			var left: int = int(f.n) - f.done.size()
			if left <= 0:
				return ""
			return "Your Fortify can still [b]%s[/b] of Build, Advancements and Recruit." % ("pick one" if (left == 1 and f.done.is_empty()) else ("pick one more" if left == 1 else "pick %d more" % left))
	if a == "recruit" and g.dpick_waiting():
		return "You haven't placed your free units from [b]Calling[/b] yet: tap one of your nesting grounds."''')
rep('''					for k in (["market"] if t.castle else (["market", "barracks"] if g.is_dinos(0) else ["market", "fort", "barracks"])):
						if gold >= g.build_cost(k):
							return "You have [b]%d gold[/b] and room to build more." % gold''', '''					for k in (["market"] if t.castle else (["market", "barracks"] if g.is_dinos(0) else ["market", "fort", "barracks"])):
						if g.can_pay_b(0, k, g.build_cost(k, t)):
							return "You have [b]%d gold[/b] and [b]%s[/b], and room to build more." % [gold, g.mat_txt(mats)]''')
rep('''				if g.is_dinos(0) and int(t.barracks) > 0 and g.guards_at(t) < g.guard_max(t) and gold >= g.guard_cost():''',
    '''				if g.is_dinos(0) and int(t.barracks) > 0 and g.guards_at(t) < g.guard_max(t) and gold >= g.guard_cost(0):''')
rep('''					if free or gold >= int(GameData.rules.buildings.barracks_upgrade_cost[int(t.bk)]):
						return "You have [b]%d gold[/b] and can still %s." % [gold, adv_txt]
				if g.can_treb_at(t) and gold >= g.treb_price(t):
					return "You have [b]%d gold[/b] and can still %s." % [gold, adv_txt]
				if gold >= g.wall_cost():
					for j in g.wall_sides(int(t.id)):
						if g.wall_on(int(t.id), j) < int(GameData.rules.walls.hp):
							return "You have [b]%d gold[/b] and can still %s." % [gold, adv_txt]''', '''					if free or mats >= g.bk_up_cost(0, int(t.bk)):
						return "You have [b]%s[/b] and can still %s." % [g.mat_txt(mats), adv_txt]
				if g.can_treb_at(t) and mats >= g.treb_price(t):
					return "You have [b]%s[/b] and can still %s." % [g.mat_txt(mats), adv_txt]
				if mats >= g.wall_cost() or g.free_walls_left() > 0:
					for j in g.wall_sides(int(t.id)):
						if g.wall_on(int(t.id), j) < int(GameData.rules.walls.hp):
							return "You have [b]%s[/b] and can still %s." % [g.mat_txt(mats), adv_txt]''')
rep('''func _confirm_leftover(msg: String) -> void:
	var last: bool = int(g.play.step) >= g.card_of(0, String(g.play.card)).actions.size() - 1''', '''func _confirm_leftover(msg: String) -> void:
	var last: bool = g.last_step_now()''')

# ---------------- the round buttons: prices in materials, Armor ----------------
rep('''			var price: int = g.build_cost(kind)
			var castle_no: bool = t.castle and kind != "market"
			var can: bool = not full and not castle_no and gold >= price
			var note: String = "Full" if full else ("Not here" if castle_no else "%d gold" % price)''', '''			var price: int = g.build_cost(kind, t)
			var castle_no: bool = t.castle and kind != "market"
			var can: bool = not full and not castle_no and g.can_pay_b(0, kind, price)
			var note: String = "Full" if full else ("Not here" if castle_no else ("Free" if price == 0 else (("%d|mat" % price) if g.in_mat(kind) else "%d gold" % price)))''')
rep('''			var wp: int = g.build_cost("wh")
			var has_wh: bool = int(t.get("wh", 0)) > 0
			var can_wh: bool = not full and not has_wh and gold >= wp
			_bubble(post.call(2, 210), R, "res://art/buildings/wh.png", "Watering Hole", "Built" if has_wh else ("Full" if full else "%d gold" % wp), can_wh, false, can_wh,''', '''			var wp: int = g.build_cost("wh", t)
			var has_wh: bool = int(t.get("wh", 0)) > 0
			var can_wh: bool = not full and not has_wh and g.mat_of(0) >= wp
			_bubble(post.call(2, 210), R, "res://art/buildings/wh.png", "Watering Hole", "Built" if has_wh else ("Full" if full else "%d|mat" % wp), can_wh, false, can_wh,''')
rep('''		var bp: int = 0 if (free or lv >= 3) else int(GameData.rules.buildings.barracks_upgrade_cost[lv])
		var can_bk: bool = int(t.barracks) > 0 and lv < 3 and gold >= bp
		var bk_note: String = "None here" if int(t.barracks) == 0 else ("Max level" if lv >= 3 else ("Free" if free else "%d gold" % bp))''', '''		var bp: int = 0 if (free or lv >= 3) else g.bk_up_cost(0, lv)
		var can_bk: bool = int(t.barracks) > 0 and lv < 3 and g.mat_of(0) >= bp
		var bk_note: String = "None here" if int(t.barracks) == 0 else ("Max level" if lv >= 3 else ("Free" if free else "%d|mat" % bp))''')
rep('''				_bubble(post.call(0, 90), R, "res://art/terrain/castle_dinos.png", ("Volcano %d" % (vl + 1)) if vl < 3 else "Volcano", "Max level" if vl >= 3 else "%d gold" % vc, can_v, false, can_v,
					func(): _do(func(): g.do_volcano(0)))''', '''				_bubble(post.call(0, 90), R, "res://art/terrain/castle_dinos.png", ("Volcano %d" % (vl + 1)) if vl < 3 else "Volcano", "Max level" if vl >= 3 else "%d gold" % vc, can_v, false, can_v,
					func(): _do(func(): g.do_volcano(0)))
				if g.can_armor(0):   # Armor (The Hunt, Advancements level 3)
					var ac: int = int(g.armor_rules().cost)
					var can_a: bool = not g.armor_on(0) and gold >= ac
					_bubble(post.call(2, 210), R, "res://art/units/bow.png", "Armor", "Forged" if g.armor_on(0) else "%d gold" % ac, can_a, false, can_a,
						func(): _do(func(): g.do_armor(0)))''')
rep('''				var can_g: bool = int(t.barracks) > 0 and gn < gm and gold >= g.guard_cost()
				var g_note: String = "Needs barracks" if int(t.barracks) == 0 else (("%d guarding" % gn) if gn >= gm else "%d gold" % g.guard_cost())''',
    '''				var can_g: bool = int(t.barracks) > 0 and gn < gm and gold >= g.guard_cost(0)
				var g_note: String = "Needs barracks" if int(t.barracks) == 0 else (("%d guarding" % gn) if gn >= gm else "%d gold" % g.guard_cost(0))''')
rep('''			var can_tr: bool = g.can_treb_at(t) and gold >= g.treb_price(t)
			var tr_note: String = ("%d gold" % g.treb_price(t)) if g.can_treb_at(t)''', '''			var can_tr: bool = g.can_treb_at(t) and g.mat_of(0) >= g.treb_price(t)
			var tr_note: String = ("%d|mat" % g.treb_price(t)) if g.can_treb_at(t)''')
rep('''		var can_w: bool = open_sides and gold >= wc
		var w_note: String = ("Free (%d left)" % g.free_walls_left() if g.free_walls_left() > 0 else "%d gold" % wc) if open_sides else "All walled"''',
    '''		var can_w: bool = open_sides and (g.mat_of(0) >= wc or g.free_walls_left() > 0)
		var w_note: String = ("Free (%d left)" % g.free_walls_left() if g.free_walls_left() > 0 else "%d|mat" % wc) if open_sides else "All walled"''')
# a price in materials shows the crate
rep('''	if note != "":
		var nl := _label(note, maxi(9, fs - 3), GOLD if on else LICHEN)
		nl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		nl.clip_text = true
		nl.custom_minimum_size.x = 2 * r - 8
		vb.add_child(nl)''', '''	if note.ends_with("|mat"):   # a price in materials: the number and the crate
		var mrow := HBoxContainer.new()
		mrow.alignment = BoxContainer.ALIGNMENT_CENTER
		mrow.add_theme_constant_override("separation", 2)
		mrow.add_child(_label(note.trim_suffix("|mat"), maxi(9, fs - 2), GOLD if on else LICHEN, true))
		var mi := _pic("%s", Vector2(fs, fs))
		mi.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		mrow.add_child(mi)
		vb.add_child(mrow)
	elif note != "":
		var nl := _label(note, maxi(9, fs - 3), GOLD if on else LICHEN)
		nl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		nl.clip_text = true
		nl.custom_minimum_size.x = 2 * r - 8
		vb.add_child(nl)''' % MAT)

# ---------------- tapping a hex: Calling's free units ----------------
rep('''	if g.cur_action() == "move" and sel >= 0 and board.targets.has(i):
		_open_move(sel, i)
		return''', '''	if g.cur_action() == "recruit" and g.dpick_waiting() and int(g.tiles[i].owner) == 0 and int(g.tiles[i].barracks) > 0:
		sel = i   # Calling (Pack Call): the free units go to the nesting ground you tap
		_do(func(): g.place_dpick(i))
		return
	if g.cur_action() == "move" and sel >= 0 and board.targets.has(i):
		_open_move(sel, i)
		return''')

# notes under the card: what the Dinosaur cards and Fortify did
rep('''		notes.append("%s %s" % [icon, line])''', '''		notes.append("%s %s" % [icon, line])
	for n2 in g.step_notes:
		var a2: String = g.card_action()
		notes.append("%s %s" % [_img(a2 if a2 != "" else "fortify", 22), n2])
	g.step_notes.clear()''')

# ---------------- the upgrade picker ----------------
rep('''		if l < 3:
			next_txt = String(GameData.upgrades[fac + "_named"][a].next) if l == 0 else String(GameData.upgrades.general[a].next[l])''',
    '''		if l < 3:
			if g.d_up(0, cid, a):   # the Dinosaurs: each card's own upgrades
				var d: Array = g.dcard(cid, a)
				next_txt = "%s: %s" % [d[l][0], d[l][1]]
			else:
				next_txt = String(GameData.upgrades[fac + "_named"][a].next) if l == 0 else String(GameData.upgrades.general[a].next[l])''')

# ---------------- the move dialog: Two Herds ----------------
rep('''		if bool(ao.surprise):
			lines.append("Offline: a sneak attack. They can't attack until your units land their first hit")
		text = "\\n".join(lines)''', '''		if bool(ao.surprise):
			lines.append("Offline: a sneak attack. They can't attack until your units land their first hit")
		if bool(ao.get("a_arm", false)):
			lines.append("Your units wear Armor: +%d damage, +10%% health" % int(g.armor_rules().dmg))
		if bool(ao.get("d_arm", false)):
			lines.append("Their units wear Armor: +%d damage, +10%% health" % int(g.armor_rules().dmg))
		text = "\\n".join(lines)''')
rep('''	var box := _open_overlay(title, 600.0)
	box.add_child(_rich(text, 15))''', '''	var box := _open_overlay(title, 600.0)
	box.add_child(_rich(text, 15))
	var join := {"on": false}   # Two Herds (Stampede): the ready units next door join the attack
	var jh: int = g.two_herds_hex(from, to) if fight else -1
	if jh >= 0:
		join.on = true
		var cb := CheckBox.new()
		cb.button_pressed = true
		cb.text = "Two Herds: the %d ready unit%s next door join in" % [int(g.tiles[jh].fresh), "s" if int(g.tiles[jh].fresh) > 1 else ""]
		cb.add_theme_font_size_override("font_size", 14)
		cb.toggled.connect(func(on): join.on = on)
		box.add_child(cb)''')
rep('''		_close_overlay()
		_go_move(from, to, a.ready.duplicate()))''', '''		_close_overlay()
		_go_move(from, to, a.ready.duplicate(), bool(join.on)))''')
rep('''		_close_overlay()
		_go_move(from, to, picked2)''', '''		_close_overlay()
		_go_move(from, to, picked2, bool(join.on))''')
rep('''func _go_move(from: int, to: int, units: Dictionary) -> void:
	var before: int = g.log_n
	var snap: Dictionary = g.snapshot()
	var res: Dictionary = g.move(from, to, units)''', '''func _go_move(from: int, to: int, units: Dictionary, join: bool = false) -> void:
	var before: int = g.log_n
	var snap: Dictionary = g.snapshot()
	var res: Dictionary = g.move(from, to, units, join)''')

# ---------------- How to play and the faction screen ----------------
rep('''%s [b]Move[/b] to claim land and attack.  %s [b]Fortify[/b] your hexes.  %s [b]Advancements[/b]: barracks upgrades, trebuchets and walls.\\n\\n"''',
    '''%s [b]Move[/b] to claim land and attack.  %s [b]Fortify[/b]: a wild card (below).  %s [b]Advancements[/b]: barracks upgrades, trebuchets and walls.\\n\\n"''')
rep('''	txt += "[b]Ways to win[/b]''', '''	txt += "[b]Gold and materials.[/b] Gold pays for units and markets%s. Forts, barracks, barracks upgrades, walls and trebuchets cost [b]materials[/b] [img=18x18]%s[/img]: each market sells up to %d a turn and your home castle counts as one, at %d gold each, any time on your turn. Tap the materials button at the top, or Buy materials during Build and Advancements. What you don't use keeps. (The Mythical use magic for everything.)\\n\\n" %% [", Alamosaurus guards and the volcano" if (g != null and g.is_dinos(0)) else "", int(GameData.rules.materials.per_market), int(GameData.rules.materials.price)]
	txt += "%%s [b]Fortify[/b] is a wild card. First you regroup: move your units up to %%d hexes between your own hexes, as often as you like (no attacks or claiming), and they can still move again later in the turn. Then pick one of Build, Advancements and Recruit (two once Fortify is upgraded twice, all three at three upgrades). Each plays like the basic action.\\n\\n" %% [_img("fortify", 20), int(GameData.rules.fortify.regroup_reach)]
	txt += "[b]Ways to win[/b]''' .replace('%s[/img]', MAT + '[/img]').replace('%%', '%'))
rep('''	if g != null and g.is_dinos(0):
		txt += "\\n\\n" + _dino_specials()
	box.add_child(_rich(txt, 15))''', '''	if g != null and g.is_dinos(0):
		txt += "\\n\\n" + _dino_specials() + "\\n\\n" + _dino_card_list()
	box.add_child(_rich(txt, 15))''')
rep('''func _dino_specials() -> String:''', '''## Every Dinosaur card's own upgrades, for How to play and the faction screen.
func _dino_card_list() -> String:
	var lines: Array = ["[b]Every Dinosaur card has its own upgrades for each of its actions[/b] (every 2nd play you pick which action goes up a level):"]
	for c in GameData.factions.dinos.cards:
		var parts: Array = []
		for a in c.actions:
			var d: Array = GameData.upgrades.dinos_cards.get(c.id, {}).get(a, [])
			var lv: Array = []
			for i in d.size():
				lv.append("%d %s: %s." % [i + 1, d[i][0], d[i][1]])
			parts.append("%s %s %s" % [_img(a, 20), ACTION_NAMES[a], " ".join(lv)])
		lines.append("  •  [b]%s[/b]: %s" % [c.name, "  ".join(parts)])
	return "\\n".join(lines)


func _dino_specials() -> String:''')
rep('''	else:
		body.add_child(_label("Each turn you hold 3 of these and play one, carrying out its actions in order. Every 2nd time you play a card, you upgrade one of its actions.", 14, LICHEN))''',
    '''	else:
		body.add_child(_label("Each turn you hold 3 of these and play one, carrying out its actions in order. Every 2nd time you play a card, you upgrade one of its actions.", 14, LICHEN))
		body.add_child(_rich({"dinos": "The Dinosaurs lean on [b]Fortify[/b] and [b]Harvest[/b].", "robots": "The Robots lean on [b]Move[/b] and [b]Advancements[/b].", "mammals": "The Mammals lean on [b]Harvest[/b] and [b]Recruit[/b]."}.get(my_faction, "") + " [b]Fortify[/b] is a wild card: regroup your army inside your land, then Build, Advancements or Recruit.", 14))
		body.add_child(_rich("[b]Gold and materials[/b]", 16))
		body.add_child(_rich("Gold pays for units and markets. %s cost [b]materials[/b] [img=18x18]%s[/img], which your markets sell you: up to %d a turn from each market and from your home castle, %d gold each." % ["Barracks, upgrades and walls" if my_faction == "dinos" else "Forts, barracks, upgrades, walls and trebuchets", int(GameData.rules.materials.per_market), int(GameData.rules.materials.price)], 14))
		if my_faction == "dinos":
			body.add_child(_rich(_dino_card_list(), 14))''' .replace('%s[/img]", 14', MAT + '[/img]", 14') if False else '''	else:
		body.add_child(_label("Each turn you hold 3 of these and play one, carrying out its actions in order. Every 2nd time you play a card, you upgrade one of its actions.", 14, LICHEN))
		body.add_child(_rich({"dinos": "The Dinosaurs lean on [b]Fortify[/b] and [b]Harvest[/b].", "robots": "The Robots lean on [b]Move[/b] and [b]Advancements[/b].", "mammals": "The Mammals lean on [b]Harvest[/b] and [b]Recruit[/b]."}.get(my_faction, "") + " [b]Fortify[/b] is a wild card: regroup your army inside your land, then Build, Advancements or Recruit.", 14))
		body.add_child(_rich("[b]Gold and materials[/b]", 16))
		body.add_child(_rich("Gold pays for units and markets. %s cost [b]materials[/b] [img=18x18]''' + MAT + '''[/img], which your markets sell you: up to %d a turn from each market and from your home castle, %d gold each." % ["Barracks, upgrades and walls" if my_faction == "dinos" else "Forts, barracks, upgrades, walls and trebuchets", int(GameData.rules.materials.per_market), int(GameData.rules.materials.price)], 14))
		if my_faction == "dinos":
			body.add_child(_rich(_dino_card_list(), 14))''')
rep('''		body.add_child(_label("Each turn you hold 3 of these and play one, carrying out its actions in order. Channeling has no other actions''',
    '''		body.add_child(_rich("The Mythical lean on [b]Advancements[/b] and [b]Fortify[/b]. Fortify is a wild card: regroup your army inside your land, then Build, Advancements or Recruit.", 14))
		body.add_child(_label("Each turn you hold 3 of these and play one, carrying out its actions in order. Channeling has no other actions''')

# notes under the card: only what happened since the last action change (so a Fortify's picks stay in view)
rep('''	var before: int = g.log_n
	g.next_step()
	if g.current == 0:
		_collect_notes(before)''', '''	var before: int = g.log_n
	g.next_step()
	if g.current == 0:
		notes = []
		_collect_notes(before)''')

open(F, 'w', encoding='utf-8').write(s)
print('ui ok')

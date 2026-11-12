# Godot port, step 13: three-player screens (browser patch2_rules.py screens): a Players 2 / 3 choice and two rival
# pickers on the faction screen, both rivals in the header and stats, computer turns one after the other, the right
# sides and colours in Arena battles, the 3-player end screen and How to play.
import sys
W = sys.argv[1]
F = W + '/scripts/ui/main.gd'
s = open(F, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    if s.count(a) != n: print('COUNT', s.count(a), a[:140]); sys.exit(1)
    s = s.replace(a, b)

# ---------------- settings ----------------
rep('''var pref_opp: String = ""   # the faction the computer plays ("" = the usual one)''', '''var pref_opp: String = ""   # the faction the computer plays ("" = the usual one)
var pref_np: int = 2        # 2 or 3 players (remembered)
var pref_opps: Array = []   # 3 players: the two rivals' factions''')
rep('''		pref_opp = String(cfg.get_value("player", "opponent", ""))''', '''		pref_opp = String(cfg.get_value("player", "opponent", ""))
		pref_np = 3 if int(cfg.get_value("player", "players", 2)) == 3 else 2
		pref_opps = Array(cfg.get_value("player", "opponents3", []))''')

# ---------------- the faction screen: Players 2 / 3, and the rivals ----------------
rep('''	vs.add_child(_label("You'll face", 15, LICHEN, true))
	for of in GameData.factions.order:
		if of == my_faction:
			continue
		var ofid: String = of
		var ob := _button(String(GameData.factions[of].name), func():
			pref_opp = ofid
			var cfg := ConfigFile.new()
			cfg.load(SETTINGS)
			cfg.set_value("player", "opponent", ofid)
			cfg.save(SETTINGS)
			show_factions(), of == other)
		ob.add_theme_font_size_override("font_size", 14)
		vs.add_child(ob)''', '''	var np_row := HBoxContainer.new()
	np_row.add_theme_constant_override("separation", 6)
	ht.add_child(np_row)
	np_row.add_child(_label("Players", 15, LICHEN, true))
	for n in [2, 3]:
		var nn: int = n
		var nb := _button(str(n), func():
			pref_np = nn
			var cfg := ConfigFile.new()
			cfg.load(SETTINGS)
			cfg.set_value("player", "players", nn)
			cfg.save(SETTINGS)
			show_factions(), n == pref_np)
		nb.add_theme_font_size_override("font_size", 14)
		nb.custom_minimum_size.x = 40
		np_row.add_child(nb)
	if pref_np == 3:
		np_row.add_child(_label("  (a bigger 79-hex map; last side standing wins)", 13, LICHEN))
	ht.move_child(np_row, vs.get_index())   # Players above who you face
	vs.add_child(_label("You'll face" if pref_np == 2 else "Rivals (pick 2)", 15, LICHEN, true))
	var three: Array = GameState.three_opps(my_faction, pref_opps)
	for of in GameData.factions.order:
		if of == my_faction:
			continue
		var ofid: String = of
		var picked: bool = (of == other) if pref_np == 2 else three.has(of)
		var ob := _button(String(GameData.factions[of].name), func():
			var cfg := ConfigFile.new()
			cfg.load(SETTINGS)
			if pref_np == 3:   # pick 2: tapping a third swaps out the one picked longest ago
				var cur3: Array = GameState.three_opps(my_faction, pref_opps)
				pref_opps = cur3 if cur3.has(ofid) else [cur3[1], ofid]
				cfg.set_value("player", "opponents3", pref_opps)
			else:
				pref_opp = ofid
				cfg.set_value("player", "opponent", ofid)
			cfg.save(SETTINGS)
			show_factions(), picked)
		ob.add_theme_font_size_override("font_size", 14)
		vs.add_child(ob)''')
rep('''		g.new_game(fid, [], _opponent_for(fid))
		g.arena_fights = true
		_apply_colors()
		g.set_level(1, pref_level)
		g.add_log("The computer plays on %s." % String(GameState.AI_LEVEL_NAME[String(g.players[1].diff)]))''',
    '''		g.new_game(fid, [], _opponent_for(fid), pref_np, pref_opps)
		g.arena_fights = true
		_apply_colors()
		for k in range(1, g.players.size()):
			g.set_level(k, pref_level)
		g.add_log("The computer plays on %s." % String(GameState.AI_LEVEL_NAME[String(g.players[1].diff)]))''')
rep('''	if g.current == 1 and g.over < 0:   # saved just as your turn ended: the computer plays its turn now''',
    '''	if g.current != 0 and g.over < 0:   # saved just as your turn ended: the computer plays its turn now''')

# ---------------- colours ----------------
rep('''func _other_color(taken: String, fid: String) -> String:
	var d: String = String(FAC_COLOR.get(fid, ""))
	if d != "" and d != taken:
		return d
	for c in ["red", "blue", "purple", "green", "yellow"]:
		if c != taken:
			return c
	return "red"


func _apply_colors() -> void:
	var mine: String = _my_color_for(String(g.players[0].faction))
	var theirs: String = _other_color(mine, String(g.players[1].faction))
	for pc in [[0, mine], [1, theirs]]:''', '''func _other_color(taken, fid: String) -> String:
	var tk: Array = taken if taken is Array else [taken]
	var d: String = String(FAC_COLOR.get(fid, ""))
	if d != "" and not tk.has(d):
		return d
	for c in ["red", "blue", "purple", "green", "yellow"]:
		if not tk.has(c):
			return c
	return "red"


func _apply_colors() -> void:
	var mine: String = _my_color_for(String(g.players[0].faction))
	var taken: Array = [mine]
	var pcs: Array = [[0, mine]]
	for k in range(1, g.players.size()):
		var c: String = _other_color(taken, String(g.players[k].faction))
		taken.append(c)
		pcs.append([k, c])
	for pc in pcs:''')

# ---------------- the Arena: the two sides in this fight ----------------
rep('''## Each Arena side's faction name (the Mammals take the side the other faction doesn't use).
func _arena_factions() -> Array:
	var out: Array = ["Dinosaurs", "Robots"]
	for pid in 2:
		out[g.arena_team(pid)] = String(GameData.factions[g.players[pid].faction].name)
	return out


## Both players' colours for the Arena, by Arena team (Blue 0, Red 1).
func _arena_cols() -> Array:
	var out: Array = [{}, {}]
	for pid in 2:
		var t: int = g.arena_team(pid)''', '''## Each Arena side's faction name (the Mammals take the side the other faction doesn't use). a, d: the two sides fighting.
func _arena_factions(a: int = 0, d: int = 1) -> Array:
	var out: Array = ["Dinosaurs", "Robots"]
	for pc in [[a, d], [d, a]]:
		out[g.arena_team(pc[0], pc[1])] = String(GameData.factions[g.players[pc[0]].faction].name)
	return out


## Both sides' colours for the Arena, by Arena team (Blue 0, Red 1).
func _arena_cols(a: int = 0, d: int = 1) -> Array:
	var out: Array = [{}, {}]
	for pc in [[a, d], [d, a]]:
		var pid: int = pc[0]
		var t: int = g.arena_team(pid, pc[1])''')
rep('''	screen.start(g.fight_armies(fight), g.arena_team(0), {"title": "Battle %s" % map_names.get(map, "in the open"), "sub": sub, "map": play_map, "hold": g.arena_team(int(fight.def)), "mods": g.arena_mods(fight), "cols": _arena_cols(), "factions": _arena_factions(), "ai_level": String(g.players[1].get("diff", "medium"))}, _font_bold)''',
    '''	var fa: int = int(fight.att)
	var fd: int = int(fight.def)
	var rival: int = fd if fa == 0 else fa
	screen.start(g.fight_armies(fight), g.arena_team(0, rival), {"title": "Battle %s" % map_names.get(map, "in the open"), "sub": sub, "map": play_map, "hold": g.arena_team(fd, fa), "mods": g.arena_mods(fight), "cols": _arena_cols(fa, fd), "factions": _arena_factions(fa, fd), "ai_level": String(g.players[rival].get("diff", "medium"))}, _font_bold)''')

# ---------------- computer turns: whoever's turn it is, one after the other ----------------
rep('''	var game: GameState = g
	var cid: String = AIPlayer.choose_card(game, 1)
	AIPlayer.start_card(game, 1, cid)
	refresh()
	var n: int = game.card_of(1, cid).actions.size()''', '''	var game: GameState = g
	var pid: int = game.current
	var cid: String = AIPlayer.choose_card(game, pid)
	AIPlayer.start_card(game, pid, cid)
	refresh()
	var n: int = game.card_of(pid, cid).actions.size()''')
rep('''		var events: Array = AIPlayer.run_step(game, 1, cid, s)''', '''		var events: Array = AIPlayer.run_step(game, pid, cid, s)''')
rep('''			events = AIPlayer.ai_moves(game, 1, int(fe.lvl))''', '''			events = AIPlayer.ai_moves(game, pid, int(fe.lvl))''')
rep('''	if game.over < 0:
		var before: int = game.log_n
		game.finish_turn()
		notes = []
		_collect_notes(before)
		notes = ai_notes + notes.filter(func(n2): return (String(n2).contains("trebuchet") or String(n2).contains("volcano")) and not String(n2).contains(String(game.players[1].name)))
		ai_notes = []
	ai_flash = []
	busy = false
	refresh()''', '''	if game.over < 0:
		AIPlayer.ai_stock(game, pid)
		var before: int = game.log_n
		game.finish_turn()
		notes = []
		_collect_notes(before)
		var kept: Array = notes.filter(func(n2): return (String(n2).contains("trebuchet") or String(n2).contains("volcano") or String(n2).contains("out of the game")) and not String(n2).contains(String(game.players[pid].name) + " "))
		if game.current == 0:
			notes = ai_notes + kept
			ai_notes = []
		else:   # 3 players: the next computer goes on; its notes wait for your turn
			ai_notes = ai_notes + kept
			notes = []
	ai_flash = []
	busy = false
	refresh()
	if g == game and game.over < 0 and game.current != 0:   # 3 players: the next computer's turn
		_run_ai()''')
rep('''	if g.over < 0 and g.current == 1:
		notes = []''', '''	if g.over < 0 and g.current != 0:
		notes = []''')

# ---------------- the card column and header ----------------
rep('''		_big_card(body, 1, String(g.play.get("card", "")), "Playing", false)''', '''		_big_card(body, g.current, String(g.play.get("card", "")), "Playing", false)''')
rep('''		var wait := _label("The %s are choosing a card…" % g.players[1].name, 17, GOLD, true)''', '''		var wait := _label("The %s are choosing a card…" % g.players[pid].name, 17, GOLD, true)''')
rep('''	var tagl := _label("  " + tag if pid == 0 else "  %s are playing" % g.players[1].name, 13, LICHEN)''', '''	var tagl := _label("  " + tag if pid == 0 else "  %s are playing" % g.players[pid].name, 13, LICHEN)''')
rep('''	var who: String = "[color=#8db0ff]your move[/color]" if (g.current == 0 and not busy) else "%s' move" % g.players[1].name''',
    '''	var who: String = "[color=#8db0ff]your move[/color]" if (g.current == 0 and not busy) else "[color=%s]%s'[/color] move" % [_ink(g.current), g.players[g.current].name]''')
rep('''	var castles := _rich("[img=22x16]res://art/terrain/castle_neutral.png[/img] [b][color=%s]%d[/color]–[color=%s]%d[/color][/b] [color=#a5b49e]of %d[/color]   %s [b][color=#efc15a]%d[/color][/b]" % [my_ink, g.castle_count(0), their_ink, g.castle_count(1), to_win, _img("magic" if g.is_myth(0) else "coin", 18), int(g.players[0].gold)], 15)''',
    '''	var race: String = "[b][color=%s]%d[/color]–[color=%s]%d[/color][/b] [color=#a5b49e]of %d[/color]" % [my_ink, g.castle_count(0), their_ink, g.castle_count(1), to_win]
	if g.players.size() > 2:   # 3 players: everyone's castles, no count to win by; a side that's out is struck through
		var parts: PackedStringArray = []
		for q in g.players:
			parts.append(("[s][color=%s]%d[/color][/s]" if g.is_out(int(q.id)) else "[color=%s]%d[/color]") % [_ink(int(q.id)), g.castle_count(int(q.id))])
		race = "[b]%s[/b]" % "–".join(parts)
	var castles := _rich("[img=22x16]res://art/terrain/castle_neutral.png[/img] %s   %s [b][color=#efc15a]%d[/color][/b]" % [race, _img("magic" if g.is_myth(0) else "coin", 18), int(g.players[0].gold)], 15)''')

# ---------------- stats: every rival ----------------
rep('''	var mine: Dictionary = g.income_of(0)
	var theirs: Dictionary = g.income_of(1)
	var them: String = String(g.players[1].name)
	var open: int = 0
	for t in g.tiles:
		if t.terrain == "plain" or t.terrain == "mountain":
			open += 1
	var units := [0, 0]
	for t in g.tiles:
		if int(t.owner) >= 0:
			units[int(t.owner)] += int(t.troops)
	_stat_tile("Magic production" if g.is_myth(0) else "Coin production", "+%d" % int(mine.total), "/ turn", "%s +%d%s" % [them, int(theirs.total), (" " + g.cur_word(1)) if g.is_myth(0) != g.is_myth(1) else ""], true)
	_stat_tile("Territories captured", str(int(mine.hexes)), "of %d" % open, "%d castle%s · %s %d" % [int(mine.castles), "" if int(mine.castles) == 1 else "s", them, int(theirs.hexes)], false)
	_stat_tile("Unit total", str(units[0]), "", "%s %d" % [them, units[1]], false)''', '''	var mine: Dictionary = g.income_of(0)
	var open: int = 0
	for t in g.tiles:
		if t.terrain == "plain" or t.terrain == "mountain":
			open += 1
	var units: Array = []
	for q in g.players:
		units.append(0)
	for t in g.tiles:
		if int(t.owner) >= 0:
			units[int(t.owner)] += int(t.troops)
	var ops: Array = g.foes_of(0)
	var inc: PackedStringArray = []
	var land: PackedStringArray = []
	var uni: PackedStringArray = []
	for o in ops:
		var nm: String = String(g.players[o].name)
		var th: Dictionary = g.income_of(o)
		inc.append("%s +%d%s" % [nm, int(th.total), (" " + g.cur_word(o)) if g.is_myth(0) != g.is_myth(o) else ""])
		land.append("%s %d" % [nm, int(th.hexes)])
		uni.append("%s %d" % [nm, units[o]])
	_stat_tile("Magic production" if g.is_myth(0) else "Coin production", "+%d" % int(mine.total), "/ turn", " · ".join(inc), true)
	_stat_tile("Territories captured", str(int(mine.hexes)), "of %d" % open, "%d castle%s · %s" % [int(mine.castles), "" if int(mine.castles) == 1 else "s", " · ".join(land)], false)
	_stat_tile("Unit total", str(units[0]), "", " · ".join(uni), false)''')

# ---------------- hex info ----------------
rep('''		kind = "Home castle" if g.homes.has(sel) else "Castle"''', '''		kind = "Home castle" if g.is_home_castle(t) else "Castle"''')
rep('''		who = "you" if owner == 0 else String(g.players[1].name)''', '''		who = "you" if owner == 0 else String(g.players[owner].name)''')

# ---------------- the end of the game ----------------
rep('''func _game_over(body: VBoxContainer) -> void:
	var won: bool = g.over == 0''', '''func _game_over(body: VBoxContainer) -> void:
	if g.players.size() > 2:
		_game_over3(body)
		return
	var won: bool = g.over == 0''')
rep('''# =====================================================================
# Small builders
# =====================================================================''', '''## 3 players: the last side standing, or you were knocked out.
func _game_over3(body: VBoxContainer) -> void:
	var won: bool = g.over == 0
	var me: Dictionary = g.players[0]
	var p := PanelContainer.new()
	p.add_theme_stylebox_override("panel", _frame(MOSS2, 16))
	p.size_flags_vertical = Control.SIZE_EXPAND_FILL
	var vb := VBoxContainer.new()
	vb.alignment = BoxContainer.ALIGNMENT_CENTER
	vb.add_theme_constant_override("separation", 10)
	p.add_child(vb)
	var big := _label("You rule the land!" if won else ("You are out" if g.is_out(0) else "The %s rule the land" % g.players[g.over].name), 36, GOLD if won else RED, true)
	big.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	big.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	big.add_theme_color_override("font_shadow_color", OUTLINE)
	big.add_theme_constant_override("shadow_offset_x", 3)
	big.add_theme_constant_override("shadow_offset_y", 3)
	vb.add_child(big)
	var txt: String = ""
	if won:
		var parts: PackedStringArray = []
		for q in g.players:
			if int(q.id) == 0:
				continue
			var by: int = int(q.get("out_by", -1))
			parts.append("The %s fell in round %d%s." % [q.name, int(q.get("out_round", g.turn)), " to you" if by == 0 else (" to the %s" % g.players[by].name if by > 0 else "")])
		txt = "You're the last side standing. " + " ".join(parts)
	else:
		var by2: int = int(me.get("out_by", -1))
		var why: String = String(me.get("out_why", ""))
		txt = ("The %s took your home castle" % g.players[by2].name) if (why == "home" and by2 >= 0) else ("You have no land left" if why == "wipe" else "You were knocked out")
		txt += " in round %d." % int(me.get("out_round", g.turn))
		if g.over_why == "last":
			txt += " The %s were the last side standing." % g.players[g.over].name
	var line := _label(txt, 17, BONE)
	line.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	line.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	vb.add_child(line)
	var again := _button("Play again" if won else "Try again", func(): show_factions(), true)
	again.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	vb.add_child(again)
	body.add_child(p)


# =====================================================================
# Small builders
# =====================================================================''')

# ---------------- How to play ----------------
rep('''	txt += "[b]Ways to win[/b]\\n 1. Take the enemy's home castle.\\n 2. Hold %d castles for %d enemy turns.\\n 3. Wipe the enemy off the map.\\n\\n" % [to_win, int(GameData.rules.castles.hold_turns)]''',
    '''	if g != null and g.players.size() > 2:
		txt += "[b]Three players: the last side standing wins[/b]\\n 1. Take a rival's home castle and they're out. Their units, walls and trebuchets are gone and all their land turns neutral, buildings and all, for anyone to walk into.\\n 2. A side with no hexes left is out too.\\n 3. When only one side remains, it wins. There's no castle count to win by with 3 players.\\nThe 3-player map has 79 hexes: 6 neutral castles, 10 mountains, 4 lakes and 26 bonus coins. The 2nd and 3rd sides start with 6 and 12 extra gold.\\n\\n"
	else:
		txt += "[b]Ways to win[/b]\\n 1. Take the enemy's home castle.\\n 2. Hold %d castles for %d enemy turns.\\n 3. Wipe the enemy off the map.\\n\\n" % [to_win, int(GameData.rules.castles.hold_turns)]''')

open(F, 'w', encoding='utf-8').write(s)
print('ui3 ok')

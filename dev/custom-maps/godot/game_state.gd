class_name GameState
extends RefCounted
## The whole game state and the turn flow: players, the board, cards, card actions,
## recruiting, training, building and Advancements. Moving and combat come in the next stage.
## Ported from the browser version's newGame, beginTurn, playCard, enterStep, resolveInstant,
## nextStep, finishTurn, advanceTurn, recruit, train, build and the Advancements functions.
##
## Every function that takes "pid" means a player number: 0 is you, 1 is the opponent.
## Every function that takes "i" means a hex number, 0 to 63.

const CombatRules = preload("res://scripts/rules/combat.gd")
const HAND_SIZE := 3
## Computer difficulty. Easy to Hard play fair; Expert also collects 40% more gold (income and Harvest).
const AI_LEVELS := ["easy", "medium", "hard", "expert"]
const AI_LEVEL_NAME := {"easy": "Easy", "medium": "Medium", "hard": "Hard", "expert": "Expert"}
const AI_LEVEL_NOTE := {"easy": "The old computer: slow to build, makes mistakes", "medium": "Uses every action and builds an economy",
	"hard": "Tries out its moves before making them", "expert": "Plans deeper, attacks boldly and collects 40% more gold"}
const AI_GOLD := {"expert": 0.4}
static var sim_arena: bool = false   # test runs: computer-vs-computer games judged as if fought in the Arena

var players: Array = []
var tiles: Array = []
var homes: Array[int] = []
var map_id: String = ""   # a hand-made map's id ("" for a random map)
var current: int = 0
var first: int = 0
var turn: int = 1
var play: Dictionary = {}          # the card being played: {card, step, moves, ...}; empty between cards
var siege: Dictionary = {}         # {pid, left} while someone holds enough castles to win
var over: int = -1                 # the winner's number once the game ends
var over_why: String = ""
var extra_castle: int = -1
var log_lines: Array[String] = []
var log_n: int = 0                 # log lines written this session (the log itself keeps only the last 80)
var arena_fights: bool = false     # true in the real game: attacks on units are fought in Megaraptor Arena
var quiet: bool = false            # true while the computer tries out cards in its head (no log)
var volley: Array[int] = []        # your finished trebuchets (and the Dinosaurs' volcano) still waiting to be aimed this turn
var volc_fx: Array = []            # volcano eruptions for the board to animate: {from, to, dice} (not saved)
var treb_fx: Array = []            # trebuchet shots for the board to animate: {from, to, pid} (not saved)


# =====================================================================
# Starting a game
# =====================================================================

## np: 2 or 3 players. opps: the two rivals' factions for 3 players (filled up from the faction list).
func new_game(your_faction: String = "dinos", board: Array = [], opponent: String = "", np: int = 2, opps: Array = [], map: String = "") -> void:
	np = 3 if np == 3 else 2
	var cmap: Dictionary = GameData.map_by_id(map) if map != "" else {}
	if not cmap.is_empty() and int(cmap.players) != np:
		cmap = {}
	map_id = String(cmap.get("id", ""))
	var other: String = opponent if (opponent != "" and opponent != your_faction and GameData.factions.has(opponent)) else ("robots" if your_faction == "dinos" else "dinos")
	var faction_ids: Array = [your_faction, other] if np == 2 else [your_faction] + three_opps(your_faction, opps)
	HexGrid.use_board(np)
	var built: Dictionary = BoardGen.from_map(cmap) if not cmap.is_empty() else {}
	tiles = built.tiles if not built.is_empty() else (board if not board.is_empty() else BoardGen.generate(np))
	for t in tiles:
		_init_tile(t)
	homes = built.homes if not built.is_empty() else BoardGen.homes_for(np)
	players.clear()
	current = 0
	first = 0
	turn = 1
	play = {}
	siege = {}
	over = -1
	over_why = ""
	extra_castle = -1
	log_lines.clear()
	for i in np:
		var fid: String = faction_ids[i]
		var faction: Dictionary = GameData.factions[fid]
		var deck: Array = []
		for card in faction.cards:
			deck.append(card.id)
		deck.shuffle()
		var m: Dictionary = Economy.mods_for(fid)
		var second_gold: int = catch_up(i, int(GameData.rules.second_player_gold), np)
		var start_gold: int = int(m.startGold) + second_gold
		players.append({
			"id": i,
			"name": "You" if i == 0 else String(faction.name),
			"faction": fid,
			"ai": i != 0,
			"gold": start_gold,
			"hand": deck.slice(0, HAND_SIZE),
			"reserve": deck.slice(HAND_SIZE),
			"last": "",
			"favor": {},
			"up": {},
			"unl": {"bk": -1, "fort": false},
			"upd_now": false,
			"upd_next": false,
			"herd": false,
			"mlv": 0,   # Mythical: Mage level and Floating Castle level
			"clv": 0,
			"volc": {},   # Dinosaurs: the home castle's volcano, {lv, cd} once woken
			"mat": 0,     # materials in store (bought at markets; pay for forts, barracks, upgrades, walls, trebuchets)
			"tr": 0,      # materials bought this turn
			"fnest": 0,   # Dinosaurs (New Nest) and Mammals (Free Den): free barracks still to build
			"ffort": 0,   # Mammals (Roost Grant, Free Roost): free fortresses still to build
			"armor": false,   # Dinosaurs (The Hunt): Armor forged
			"out": false,     # 3 players: knocked out
		})
	for i in np:
		if is_myth(i):
			_myth_setup(i)   # 1 Mage, 4 Minions and 5 magic
		else:
			add_basic(homes[i], i, int(mods_of(i).startTroops), true)
	if np == 3:
		add_log("A new age begins: you, the %s and the %s. Take a side's home castle, or wipe them off the map, and they're out. The last side standing wins." % [players[1].name, players[2].name])
	else:
		add_log("A new age begins. Win by taking the enemy home castle, holding %d castles, or wiping them off the map." % int(GameData.rules.castles.to_win))


## Extra gold (or magic) for a seat that moves later: 2 players, the 2nd seat gets it all; 3 players, 3/4 of it per seat behind.
static func catch_up(i: int, base: int, np: int) -> int:
	if np > 2:
		return roundi(base * float(GameData.rules.three_players.catch_up) * i)
	return base if i == 1 else 0


## 3 players: the two rivals' factions (the ones picked, filled up from the faction list).
static func three_opps(fid: String, want: Array) -> Array:
	var o: Array = []
	for f in want:
		if GameData.factions.has(f) and f != fid and not o.has(f) and o.size() < 2:
			o.append(f)
	for f in GameData.factions.order:
		if o.size() >= 2:
			break
		if f != fid and not o.has(f):
			o.append(f)
	return o


## The sides still in the game other than pid.
func foes_of(pid: int) -> Array:
	var out: Array = []
	for q in players:
		if int(q.id) != pid and not bool(q.get("out", false)):
			out.append(int(q.id))
	return out


func foe_homes(pid: int) -> Array:
	return foes_of(pid).map(func(e): return homes[e])


func foe_tiles(pid: int) -> Array:
	var out: Array = []
	for t in tiles:
		if int(t.owner) >= 0 and int(t.owner) != pid:
			out.append(int(t.id))
	return out


func is_out(pid: int) -> bool:
	return bool(players[pid].get("out", false))


## 3 players: a side whose home castle falls (or that has no land left) is out. Its land goes neutral: its units, walls,
## trebuchets, Life Trees and domes are gone; the buildings stay for whoever walks in. The last side standing wins.
func knock_out(pid: int, by: int, why: String) -> void:
	var p: Dictionary = players[pid]
	if bool(p.get("out", false)):
		return
	p.out = true
	p.out_by = by
	p.out_why = why
	p.out_round = turn
	p.volc = {}
	for t in tiles:
		if int(t.braced) == pid:
			t.braced = -1
		if int(t.owner) != pid:
			continue
		t.owner = -1
		t.army = {}
		t.ready = {}
		t.troops = 0
		t.fresh = 0
		t.walls = [0, 0, 0, 0, 0, 0]
		t.braced = -1
		t.treb = 0
		t.treb_due = 0
		t.treb2 = 0
		t.treb2_due = 0
		t.tree = 0
		t.root = 0
		t.dome = 0
	var who: String = "You are" if pid == 0 else "The %s are" % p.name
	if by >= 0:
		add_log("%s out of the game: %s took %s home castle, and %s land goes neutral." % [who, "you" if by == 0 else "the " + String(players[by].name), "your" if pid == 0 else "their", "your" if pid == 0 else "their"])
	else:
		add_log("%s out of the game: no land left." % who)
	var left: Array = players.filter(func(q): return not bool(q.get("out", false)))
	if left.size() == 1:
		_end_game(int(left[0].id), "last")
	elif pid == 0 and not bool(p.ai):
		# you're out: the game is over for you. "over" names the side that put you out (or the biggest one left).
		var w: int = by
		if w < 0:
			var best: int = -1
			for q in left:
				var n: int = tiles.filter(func(t): return int(t.owner) == int(q.id)).size()
				if n > best:
					best = n
					w = int(q.id)
		_end_game(w, "out")


func _init_tile(t: Dictionary) -> void:
	for key in ["army", "ready"]:
		if not t.has(key):
			t[key] = {}
	var defaults: Dictionary = {"troops": 0, "fresh": 0, "braced": -1, "bl": 0, "wh": 0,
		"treb": 0, "treb_due": 0, "treb2": 0, "treb2_due": 0, "tree": 0, "root": 0, "dome": 0,
		"new_t": -1, "cap_t": -1, "cap_by": -1}   # Robots: the round units were made here; when and by whom it was captured
	for key in defaults:
		if not t.has(key):
			t[key] = defaults[key]


# =====================================================================
# Small lookups
# =====================================================================

func mods_of(pid: int) -> Dictionary:
	return Economy.mods_for(players[pid].faction)


func faction_of(pid: int) -> Dictionary:
	return GameData.factions[players[pid].faction]


func card_of(pid: int, cid: String) -> Dictionary:
	for c in faction_of(pid).cards:
		if c.id == cid:
			return c
	return {}


func basic_of(pid: int) -> String:
	return String(faction_of(pid).basic_unit)


func is_robots(pid: int) -> bool:
	return players[pid].faction == "robots"


func is_dinos(pid: int) -> bool:
	return players[pid].faction == "dinos"


func is_mammals(pid: int) -> bool:
	return players[pid].faction == "mammals"


## Is the Mammals' named ability on for action a, being played right now by pid?
func mamm_now(pid: int, a: String) -> bool:
	return not play.is_empty() and current == pid and cur_action() == a and is_mammals(pid) and named_on()


## In Numbers: during that Recruit, a hex of theirs with 10 or more units recruits like a level 2 barracks.
func in_numbers(t: Dictionary) -> bool:
	return int(t.owner) >= 0 and int(t.owner) == current and int(t.troops) >= int(GameData.rules.mammals.in_numbers) and mamm_now(current, "recruit")


## Moves in a Move action: 2, plus the cards' extra moves; the Mythical always have 3.
func moves_limit(pid: int) -> int:
	if regrouping() and current == pid:
		return REGROUP_MOVES
	return (1 if dk(pid, "stamp", "move") >= 1 else 0) + (1 if dk(pid, "mobil", "move") >= 1 else 0) + int(mods_of(pid).movesPerAction) + mamm_moves(pid) + (1 if is_myth(pid) else 0)


## Charge (Stampede): the extra move must be an attack.
func charge_only(pid: int) -> bool:
	return (dk(pid, "stamp", "move") >= 1 or dk(pid, "tusks", "move") >= 1) and not play.is_empty() and int(play.moves) >= moves_limit(pid) - 1


func add_log(text: String) -> void:
	if quiet:
		return
	log_lines.push_front(text)
	log_n += 1
	if log_lines.size() > 80:
		log_lines.resize(80)


func building_count(t: Dictionary) -> int:
	return int(t.market) + int(t.fort) + int(t.barracks) + int(t.get("wh", 0))


func is_home_castle(t: Dictionary) -> bool:
	return t.castle and int(t.owner) >= 0 and homes[int(t.owner)] == int(t.id)


func castle_count(pid: int) -> int:
	var n: int = 0
	for t in tiles:
		if t.castle and int(t.owner) == pid:
			n += 1
	return n


# =====================================================================
# Card levels and favor (every 2 plays of a card upgrades one of its actions)
# =====================================================================

func ups_of(pid: int, cid: String) -> Array:
	return players[pid].up.get(cid, [0, 0, 0])


func lvl_of(pid: int, cid: String, slot: int) -> int:
	return int(ups_of(pid, cid)[slot])


func favor_of(pid: int, cid: String) -> int:
	return int(players[pid].favor.get(cid, 0))


## True when playing this card now will upgrade one of its actions, so the player must pick which.
func upgrade_due(pid: int, cid: String) -> bool:
	if is_myth(pid):   # Mythical cards don't upgrade yet
		return false
	var per: int = int(GameData.rules.cards.favors_per_upgrade)
	if (favor_of(pid, cid) + 1) % per != 0:
		return false
	for v in ups_of(pid, cid):
		if int(v) < int(GameData.rules.cards.max_upgrade):
			return true
	return false


func gain_favor(pid: int, cid: String, slot: int) -> int:
	var p: Dictionary = players[pid]
	var f: int = favor_of(pid, cid) + 1
	p.favor[cid] = f
	if f % int(GameData.rules.cards.favors_per_upgrade) != 0 or slot < 0:
		return -1
	if not p.up.has(cid):
		p.up[cid] = [0, 0, 0]
	var u: Array = p.up[cid]
	if int(u[slot]) >= int(GameData.rules.cards.max_upgrade):
		return -1
	u[slot] = int(u[slot]) + 1
	var action: String = card_of(pid, cid).actions[slot]
	add_log("%s upgrade %s: %s is now level %d." % [p.name, card_of(pid, cid).name, action, int(u[slot])])
	return slot


## The computer's choice of which action to upgrade.
func ai_upgrade_pick(pid: int, cid: String) -> int:
	var c: Dictionary = card_of(pid, cid)
	var u: Array = ups_of(pid, cid)
	var best: int = -1
	var best_value: float = -INF
	for i in c.actions.size():
		if int(u[i]) >= int(GameData.rules.cards.max_upgrade):
			continue
		var fp: Dictionary = GameData.factions.get("ai_upgrade_pref_faction", {}).get(String(players[pid].faction), {})
		var value: float = float(fp.get(c.actions[i], GameData.factions.ai_upgrade_pref[c.actions[i]])) - 1.2 * int(u[i])
		if value > best_value:
			best_value = value
			best = i
	return best


## The action printed on the card at the current step.
func card_action() -> String:
	if play.is_empty():
		return ""
	return String(card_of(current, play.card).actions[int(play.step)])


## The action being played now. Inside a Fortify, the regroup plays as a Move and each pick as its own action.
func cur_action() -> String:
	var a: String = card_action()
	if a == "advance" and int(play.get("rg", 0)) == 1:
		return "move"   # Roam Free (Tusks and Thorns): the regroup after the Advancements
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
	if is_robots(current):
		return 1 if dk(current, "mobil", "move") >= 2 else 0   # Climb (Mobilize)
	if is_mammals(current):
		return 1 if dk(current, "roam", "move") >= 3 else 0   # Mountain Paths (The Long Roam)
	var raw: int = raw_lvl()
	return 0 if raw == 1 else raw


## True when the current action's named faction ability is active (level 1 or higher). The Dinosaurs' old abilities
## (Herd, Migrate, Nesting, Populate, Abundance, Rainy Season) are retired.
func named_on() -> bool:
	if play.is_empty() or card_ups(current):
		return false
	return raw_lvl() >= 1


# =====================================================================
# The Dinosaur cards' own upgrades (Ethan, 2026-11-11). dk = the level of that card's action while it is being played
# (0 when it isn't that card and action).
# =====================================================================

## Factions whose cards have their own upgrades: the Dinosaurs, the Robots since 2026-11-11 and the Mammals since 2026-11-13.
func card_ups(pid: int) -> bool:
	return is_dinos(pid) or is_robots(pid) or is_mammals(pid)


## The level a card's action has reached, played now or not (Mobilize's Cheap Markets stays on once reached).
func card_lv(pid: int, cid: String, a: String) -> int:
	var c: Dictionary = card_of(pid, cid)
	if c.is_empty():
		return 0
	var i: int = c.actions.find(a)
	return 0 if i < 0 else lvl_of(pid, cid, i)


func dk(pid: int, cid: String, a: String) -> int:
	if play.is_empty() or current != pid or not card_ups(pid) or String(play.card) != cid or card_action() != a:
		return 0
	return lvl_of(pid, cid, int(play.step))


func dcard(cid: String, a: String) -> Array:
	var d: Dictionary = GameData.upgrades.get("dinos_cards", {})
	if not d.has(cid):
		d = GameData.upgrades.get("robots_cards", {})
	if not d.has(cid):
		d = GameData.upgrades.get("mammals_cards", {})
	return d.get(cid, {}).get(a, [])


## Does this card's action have its own upgrades? (the Dinosaurs' and the Robots' cards)
func d_up(pid: int, cid: String, a: String) -> bool:
	return card_ups(pid) and not dcard(cid, a).is_empty()


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
	if is_robots(pid) and not play.is_empty():
		return robo_action_start(pid)
	if is_mammals(pid) and not play.is_empty():
		return mamm_action_start(pid)
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
	if is_robots(pid):
		_robo_built(pid, k, price)
		return
	if is_mammals(pid):
		_mamm_built(pid, k, price)
		return
	if not is_dinos(pid) or price > 0 or play.is_empty():
		return
	var p: Dictionary = players[pid]
	if k == "market" and dk(pid, "stamp", "build") >= 1 and not bool(play.get("free_mk", false)):
		play.free_mk = true
	elif k == "barracks" and int(p.get("fnest", 0)) > 0:
		p.fnest = int(p.fnest) - 1


func bk_up_cost(pid: int, lv: int, t: Dictionary = {}) -> int:
	var c: int = int(GameData.rules.buildings.barracks_upgrade_cost[lv]) - (1 if dk(pid, "hunt", "advance") >= 1 else 0)   # Quick Nests
	if dk(pid, "cons", "advance") >= 1:
		c -= 1   # Quick Barracks (Construction)
	if dk(pid, "tusks", "advance") >= 2:
		c -= 1   # Quick Dens (Tusks and Thorns)
	if not t.is_empty() and dk(pid, "mobil", "advance") >= 1 and HexGrid.neighbors(homes[pid]).has(int(t.id)):
		c -= 1   # Home Grid (Mobilize)
	return maxi(0, c)


## Armor (The Hunt, Advancements level 3): bought at the home castle.
func do_armor(pid: int) -> bool:
	var p: Dictionary = players[pid]
	var h: Dictionary = tiles[homes[pid]]
	var cost: int = int(armor_rules().cost)
	if armor_on(pid) or int(h.owner) != pid or not (dk(pid, "hunt", "advance") >= 3 or dk(pid, "cons", "advance") >= 3) or int(p.gold) < cost:
		return false   # Armor (The Hunt) or Overclock (Construction)
	p.gold = int(p.gold) - cost
	p.armor = true
	add_log("%s %s: all their units get +%d damage and +10%% health." % [p.name, "run Overclock" if is_robots(pid) else "forge Armor", int(armor_rules().dmg)])
	return true


func can_armor(pid: int) -> bool:
	return ((is_dinos(pid) and dk(pid, "hunt", "advance") >= 3) or (is_robots(pid) and dk(pid, "cons", "advance") >= 3)) and int(tiles[homes[pid]].owner) == pid


# =====================================================================
# The Robots (Ethan, 2026-11-11/12). One building per hex. It starts as a market and then takes one of two paths:
# a resource hex (more markets on that hex, up to 4), or a factory (from the home castle during Advancements: a barracks,
# then a fortress, paid in materials). Never both. Each Robot card has its own upgrades (upgrades.json robots_cards).
# Ported from the browser's dev/robots/patch1_factory.py, patch2_resource.py and patch3_cards.py.
# =====================================================================

func robo_markets() -> int:
	return int(GameData.rules.robots.markets_max)


## A Robot hex's factory level: 1 a market, 2 with a barracks, 3 with its fortress (0: nothing built).
func robo_lv(t: Dictionary) -> int:
	if int(t.market) <= 0:
		return 0
	if int(t.barracks) <= 0:
		return 1
	return 3 if int(t.fort) > 0 else 2


## What the home castle can add to this hex next: "barracks" (on a single market), then "fort"; "" when nothing
## (a resource hex, a castle, a full factory).
func robo_next(t: Dictionary) -> String:
	if int(t.market) <= 0 or t.castle:
		return ""
	if int(t.barracks) <= 0:
		return "barracks" if int(t.market) == 1 else ""
	return "fort" if int(t.fort) <= 0 else ""


## Can this hex take another Robot market? (an empty hex, or a market on the resource path)
func robo_can_market(t: Dictionary) -> bool:
	return int(t.barracks) <= 0 and int(t.fort) <= 0 and int(t.get("wh", 0)) <= 0 and int(t.market) < robo_markets()


func robo_up_targets(pid: int, k: String) -> Array[int]:
	var out: Array[int] = []
	for t in tiles:
		if int(t.owner) == pid and robo_next(t) == k:
			out.append(int(t.id))
	return out


## A factory upgrade's price in materials: Quick Barracks, Quick Fortress, and Home Grid next to the home castle.
func robo_up_cost(pid: int, k: String, t: Dictionary = {}) -> int:
	var c: int = int(GameData.rules.buildings.cost_by_level[k][0])
	if k == "barracks" and dk(pid, "cons", "advance") >= 1:
		c -= 1
	if k == "fort" and dk(pid, "cons", "advance") >= 2:
		c -= 1
	if not t.is_empty() and dk(pid, "mobil", "advance") >= 1 and HexGrid.neighbors(homes[pid]).has(int(t.id)):
		c -= 1
	return maxi(0, c)


## The cheapest that upgrade comes to now (for the buttons); its base price when nothing can take it.
func robo_up_best(pid: int, k: String) -> int:
	var tg: Array[int] = robo_up_targets(pid, k)
	if tg.is_empty():
		return robo_up_cost(pid, k)
	var best: int = 999
	for i in tg:
		best = mini(best, robo_up_cost(pid, k, tiles[i]))
	return best


## Adds a barracks (or then the fortress) to one of pid's markets, paid in materials: during Advancements, while the
## Robots hold their home castle.
func do_robo_up(pid: int, i: int, k: String = "") -> bool:
	var t: Dictionary = tiles[i]
	var nk: String = robo_next(t)
	if not is_robots(pid) or int(t.owner) != pid or nk == "" or (k != "" and k != nk) or not home_market(pid) or cur_action() != "advance":
		return false
	var c: int = robo_up_cost(pid, nk, t)
	if mat_of(pid) < c:
		return false
	spend_mat(pid, c)
	t[nk] = 1
	_note_unlock(pid, nk, t)
	add_log("%s upgrade a factory with a %s." % [players[pid].name, "fortress" if nk == "fort" else "barracks"])
	if nk == "barracks":
		robo_muster(pid, t)
	return true


## Muster (Onslaught, Advancements): every barracks upgrade also makes units on that hex.
func robo_muster(pid: int, t: Dictionary) -> void:
	var l: int = dk(pid, "onsl", "advance")
	if l < 1 or not is_robots(pid):
		return
	var got: Dictionary = {"rknight": 1, "rlong": 1} if l >= 3 else ({"brawler": 2, "rarch": 1} if l >= 2 else {"brawler": 2})
	_add_army(int(t.id), got, true)
	t.new_t = turn
	add_log("%s muster %s at the new barracks." % [players[pid].name, _army_words(got)])


func _army_words(a: Dictionary) -> String:
	var parts: Array = []
	for k in a:
		parts.append("%d %s" % [int(a[k]), String(GameData.units[k].name)])
	return ", ".join(PackedStringArray(parts))


## The Robots' market prices in a Build: Free Market(s) (Siege Protocol), Fourth Free, Cheap Markets (Mobilize, for good
## once reached), Fresh Ground (Construction) and Border Market (Siege Protocol).
func robo_cost(pid: int, k: String, c: int, t: Dictionary) -> int:
	if k != "market":
		return c
	var sb: int = dk(pid, "sprot", "build")
	if sb >= 2 and int(play.get("free_used", 0)) < (2 if sb >= 3 else 1):
		return 0
	if dk(pid, "cons", "build") >= 2 and not t.is_empty() and int(t.market) == 3:
		return 0
	if card_lv(pid, "mobil", "advance") >= 3:
		c -= 3
	if not t.is_empty() and int(t.market) == 0 and int(t.get("cap_by", -1)) == pid:
		if dk(pid, "cons", "build") >= 1 and int(t.get("cap_t", -1)) == turn:
			c -= 1
		if sb >= 1 and HexGrid.neighbors(homes[pid]).has(int(t.id)):
			c -= 2
	return maxi(0, c)


func _robo_built(pid: int, k: String, price: int) -> void:
	if k != "market" or play.is_empty():
		return
	var sb: int = dk(pid, "sprot", "build")
	if price == 0 and sb >= 2 and int(play.get("free_used", 0)) < (2 if sb >= 3 else 1):
		play.free_used = int(play.get("free_used", 0)) + 1
	if dk(pid, "cons", "build") >= 3:   # Scrap
		play.mk_b = int(play.get("mk_b", 0)) + 1
		if int(play.mk_b) % 2 == 0:
			players[pid].mat = mat_of(pid) + 1
			add_log("%s salvage 1 material from their new markets (Scrap)." % players[pid].name)


## A Robot Harvest's card upgrades: castle gold (Deploy), Full Yield, Market Hubs and Hub Stores (Onslaught).
func robo_harvest(pid: int) -> Dictionary:
	var cs: int = 0
	var hubs: int = 0
	for t in tiles:
		if int(t.owner) == pid:
			if t.castle:
				cs += 1
			if int(t.market) >= robo_markets():
				hubs += 1
	var hexes: int = int(income_of(pid).hexes)
	var g: int = 0
	var m: int = 0
	var why: Array = []
	var de: int = dk(pid, "deploy", "harvest")
	var on: int = dk(pid, "onsl", "harvest")
	if de >= 1:
		var per: Array = [0, 2, 5, 12]
		var names: Array = ["", "Castle Tax", "Castle Tolls", "Castle Vaults"]
		var x: int = int(per[de]) * cs
		g += x
		if x > 0:
			why.append("%s +%d" % [names[de], x])
	if on >= 1:
		var y: int = hexes - hexes / 2
		g += y
		if y > 0:
			why.append("Full Yield +%d" % y)
	if on >= 2 and hubs > 0:
		g += 5 * hubs
		why.append("Market Hubs +%d" % (5 * hubs))
	if on >= 3 and hubs > 0:
		m += 2 * hubs
		why.append("Hub Stores +%s" % mat_txt(2 * hubs))
	return {"g": g, "m": m, "why": why}


## A Robot action's card upgrades that happen when it starts: Factory, Barracks and Fortress Run (Siege Protocol's
## Advancements), and the notes for the free markets and Scrap. Returns notes for the card column.
func robo_action_start(pid: int) -> Array:
	var out: Array = []
	var a: String = card_action()
	var p: Dictionary = players[pid]
	if a == "advance":
		var l: int = dk(pid, "sprot", "advance")
		if l >= 1:   # (the log lines become the notes under your card, so the runs only log)
			if int(tiles[homes[pid]].owner) == pid:
				add_units(homes[pid], "brawler", int(GameData.rules.robots.factory_units), true)
				tiles[homes[pid]].new_t = turn
				add_log("%s run the factory: +%d Brawlers at %s home castle (Factory Run)." % [p.name, int(GameData.rules.robots.factory_units), "your" if pid == 0 else "their"])
			else:
				out.append("Factory Run: no Brawlers, because you don't hold your home castle")
		if l >= 2:
			var n: int = 0
			for t in tiles:
				if int(t.owner) == pid and int(t.barracks) > 0:
					add_units(int(t.id), "brawler", 3, true)
					t.new_t = turn
					n += 1
			if n > 0:
				add_log("%s get 3 free Brawlers at each of %d barracks (Barracks Run)." % [p.name, n])
		if l >= 3:
			var nf: int = 0
			for t in tiles:
				if int(t.owner) == pid and int(t.fort) > 0:
					add_units(int(t.id), "rknight", 2, true)
					t.new_t = turn
					nf += 1
			if nf > 0:
				add_log("%s get 2 free Robot Knights at each of %d fortress%s (Fortress Run)." % [p.name, nf, "es" if nf > 1 else ""])
	if a == "build":
		var sb: int = dk(pid, "sprot", "build")
		if sb >= 2:
			out.append("Two Free Markets: your first 2 markets in this action cost nothing" if sb >= 3 else "Free Market: your first market in this action costs nothing")
		if dk(pid, "cons", "build") >= 3:
			out.append("Scrap: +1 material for every 2 markets you build")
	return out


## Laser Strike (Onslaught, Move level 2): the ready Laser Tanks on a hex fire at an enemy hex next door like a trebuchet,
## with no battle (twice with Double Strike). It uses a move, and the tanks.
func laser_ok(pid: int, from: int, to: int) -> bool:
	if play.is_empty() or not is_robots(pid) or cur_action() != "move" or dk(pid, "onsl", "move") < 2:
		return false
	var s: Dictionary = tiles[from]
	var b: Dictionary = tiles[to]
	return int(s.owner) == pid and int(s.ready.get("ltank", 0)) > 0 and int(b.owner) >= 0 and int(b.owner) != pid and int(b.troops) > 0 and HexGrid.neighbors(from).has(to) and moves_left() > 0


func do_laser(pid: int, from: int, to: int) -> Dictionary:
	if not laser_ok(pid, from, to):
		return {}
	var s: Dictionary = tiles[from]
	var n: int = int(s.ready.ltank)
	s.ready.erase("ltank")
	sync_tile(s)
	play.moves = int(play.moves) + 1
	var shots: int = 0
	var kl: int = 0
	var hits: int = 0
	for q in (2 if dk(pid, "onsl", "move") >= 3 else 1):
		if int(tiles[to].troops) > 0:
			var r: Dictionary = fire_treb(from, to, "laser strike")
			shots += 1
			kl += int(r.killed)
			hits += int(r.hits)
	return {"n": n, "shots": shots, "killed": kl, "hits": hits}


## Robot trades (Mobilize): Recompile in Advancements (5 Brawlers for a Knight), Rebuild and Refit in Recruit.
func trades_at(i: int) -> Array:
	var out: Array = []
	if i < 0 or play.is_empty() or fx_on() or not is_robots(current):
		return out
	var t: Dictionary = tiles[i]
	if int(t.owner) != current:
		return out
	var T: Dictionary = GameData.rules.robots.trades
	for k in T:
		var x: Dictionary = T[k]
		if cur_action() == String(x["a"]) and dk(current, "mobil", String(x["a"])) >= int(x["l"]) and int(t.army.get(String(x["from"]), 0)) >= int(x["n"]):
			out.append(String(k))
	return out


func robo_trade(i: int, k: String) -> bool:
	if not trades_at(i).has(k):
		return false
	var x: Dictionary = GameData.rules.robots.trades[k]
	var t: Dictionary = tiles[i]
	var fk: String = String(x["from"])
	var n: int = int(x["n"])
	var rdy: bool = int(t.ready.get(fk, 0)) >= n
	take_units(i, {fk: n})
	add_units(i, String(x["to"]), 1, rdy)
	add_log("%s trade %d %s for a %s (%s)." % [players[current].name, n, GameData.units[fk].name, GameData.units[String(x["to"])].name, x["name"]])
	return true


## The Robots' card moves: extra hexes a move can reach, each only for the units that can make it.
## [{hexes: {hex: true}, ok: Callable(unit) -> bool, every: true when every unit can, why: the note}]
func robo_move_extra(from: int, lvl: int) -> Array:
	var out: Array = []
	var t: Dictionary = tiles[from]
	var pid: int = int(t.owner)
	if pid < 0 or not is_robots(pid) or play.is_empty() or current != pid or regrouping():
		return out
	var dep: int = dk(pid, "deploy", "move")
	var con: int = dk(pid, "cons", "move")
	var ons: int = dk(pid, "onsl", "move")
	var flyer := func(k): return bool(GameData.units[k].get("air", false))
	if dep >= 1 or con >= 3:   # Air Lanes (Deploy 1, Construction 3)
		var st: Dictionary = {}
		for x in tiles:
			if int(x.owner) == pid and int(x.id) != from and can_enter(int(x.id), 1):
				st[int(x.id)] = true
		if not st.is_empty():
			out.append({"hexes": st, "ok": flyer, "every": false, "why": "Only flyers can go this far (Air Lanes)."})
	if dep >= 2:   # Ridge Hop
		var st2: Dictionary = {}
		for a in HexGrid.neighbors(from):
			if tiles[a].terrain == "mountain":
				for b in HexGrid.neighbors(a):
					if b != from and can_enter(b, lvl):
						st2[b] = true
		if not st2.is_empty():
			out.append({"hexes": st2, "ok": flyer, "every": false, "why": "Only flyers can hop the mountain (Ridge Hop)."})
	if dep >= 3:   # Overflight
		var st3: Dictionary = {}
		for a in HexGrid.neighbors(from):
			var A: Dictionary = tiles[a]
			if int(A.owner) >= 0 and int(A.owner) != pid and int(A.troops) > 0:
				for b in HexGrid.neighbors(a):
					if b != from and can_enter(b, lvl):
						st3[b] = true
		if not st3.is_empty():
			out.append({"hexes": st3, "ok": flyer, "every": false, "why": "Only flyers can fly over the enemy army (Overflight)."})
	if con >= 2:   # Brawler Dash: 2 hexes, both empty
		var st4: Dictionary = {}
		for a in HexGrid.neighbors(from):
			if not can_enter(a, lvl) or int(tiles[a].troops) > 0 or not _pass_through(from, a, lvl, pid):
				continue
			for b in HexGrid.neighbors(a):
				if b != from and can_enter(b, lvl) and int(tiles[b].troops) == 0 and home_guards(tiles[b]).is_empty():
					st4[b] = true
		if not st4.is_empty():
			out.append({"hexes": st4, "ok": func(k): return k == "brawler", "every": false, "why": "Only Brawlers can dash this far (Brawler Dash)."})
	if ons >= 1 and int(t.get("new_t", -1)) == turn:   # Fresh Units: a hex where you made units this turn
		var st5: Dictionary = {}
		for a in HexGrid.neighbors(from):
			if can_enter(a, lvl) and _pass_through(from, a, lvl, pid):
				for b in HexGrid.neighbors(a):
					if b != from and can_enter(b, lvl):
						st5[b] = true
		if not st5.is_empty():
			out.append({"hexes": st5, "ok": func(_k): return true, "every": true, "why": "Units made this turn go 2 hexes (Fresh Units)."})
	return out


func _robo_move_filter(from: int, to: int, lvl: int) -> Callable:
	if _move_targets_core(from, lvl, false).has(to):
		return Callable()
	var xs: Array = robo_move_extra(from, lvl).filter(func(x): return x["hexes"].has(to))
	if xs.is_empty() or xs.any(func(x): return bool(x["every"])):
		return Callable()
	return func(k): return xs.any(func(x): return bool(x["ok"].call(k)))


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
	return (fx_on() and String(play.fx.ph) == "regroup") or rg_on()   # also Roam Free (Tusks and Thorns)


## Roam Free (Tusks and Thorns' Advancements level 3): after the action, a regroup with any number of moves
## to any of your hexes. play.rg: 1 while it runs, 2 once done.
func rg_on() -> bool:
	return not play.is_empty() and int(play.get("rg", 0)) == 1 and card_action() == "advance"


func rg_due(pid: int) -> bool:
	return not play.is_empty() and current == pid and int(play.get("rg", 0)) == 0 and is_mammals(pid) and card_action() == "advance" and dk(pid, "tusks", "advance") >= 3


func regroup_reach() -> int:
	return int(GameData.rules.fortify.regroup_reach)


func fx_reach() -> int:
	if rg_on():
		return 99
	return 99 if (fx_on() and int(play.fx.get("far", 0)) > 0) else regroup_reach()


func fx_pick_list() -> Array:
	var out: Array = GameData.rules.fortify.picks.duplicate()
	if fx_on() and bool(play.fx.get("mv", false)):
		out.append("move")
	return out


## How many picks a Fortify at this upgrade level gets (the Dinosaurs' Fortify upgrades are their cards' own).
func fx_picks_at(pid: int, raw: int) -> int:
	if is_robots(pid):
		return 2 if raw >= 1 else 1   # Dual Core (Siege Protocol)
	var eff: int = 0 if (card_ups(pid) or raw == 1) else raw
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


## A Fortify starts with its faction ability (the Robots' Update) and the Dinosaur card's upgrades.
## Returns notes for the card column.
func fortify_start(pid: int, raw: int) -> Array:
	var p: Dictionary = players[pid]
	var out: Array = []
	if is_mammals(pid) and not play.is_empty():
		out.append_array(_mamm_fortify(pid, raw))   # Den Season's Fortify (Mating is retired)
	if is_robots(pid) and raw >= 2:   # Siege Protocol, the Robots' only Fortify card
		out.append("Sortie: after your picks, a real Move that can attack or claim")
	if is_robots(pid) and raw >= 3:
		out.append("Home Link: units at your home castle can regroup to any of your hexes")
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
		"far": 1 if l >= 1 else 0, "mv": l >= 2, "rally": 1 if l >= 3 else 0, "mvx": dk(pid, "sprot", "fortify") >= 2}   # mvx: Sortie
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
	if bool(f.get("mvx", false)) and not f.done.has("move"):   # Sortie (Siege Protocol): a real Move after the picks
		f.ph = "act"
		f.cur = "move"
		play.moves = 0
		return true
	play.fx = {}
	return false


## Does the main button end the turn? (not while a Fortify still has its picks to come)
func last_step_now() -> bool:
	if play.is_empty():
		return false
	if rg_due(current):
		return false   # Roam Free comes first
	if fx_on():
		var f: Dictionary = play.fx
		var sortie: bool = bool(f.get("mvx", false)) and String(f.cur) != "move" and not f.done.has("move")
		if f.ph == "regroup" or (f.ph == "act" and (f.done.size() + 1 < int(f.n) or sortie)) or (f.ph == "pick" and sortie):
			return false
	return int(play.step) >= card_of(current, play.card).actions.size() - 1


## Rally (Pack Call): every ready unit you have, from anywhere in your land, comes to one hex.
func rally_to(i: int) -> int:
	if not fx_on() or not regrouping() or int(play.fx.get("rally", 0)) <= 0 or int(tiles[i].owner) != current:
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
	return best


# =====================================================================
# Armies on hexes. t.army = {unit: count}; t.ready = the units that can still move this turn.
# =====================================================================

func sync_tile(t: Dictionary) -> void:
	for k in t.army.keys():
		if int(t.army[k]) <= 0:
			t.army.erase(k)
	for k in t.ready.keys():
		t.ready[k] = mini(int(t.ready[k]), int(t.army.get(k, 0)))
		if int(t.ready[k]) <= 0:
			t.ready.erase(k)
	t.troops = _count(t.army)
	t.fresh = _count(t.ready)


func _count(a: Dictionary) -> int:
	var n: int = 0
	for k in a:
		n += maxi(0, int(a[k]))
	return n


func add_units(i: int, unit: String, n: int, ready: bool) -> void:
	if n <= 0:
		return
	var t: Dictionary = tiles[i]
	t.army[unit] = int(t.army.get(unit, 0)) + n
	if ready:
		t.ready[unit] = int(t.ready.get(unit, 0)) + n
	sync_tile(t)


func take_units(i: int, a: Dictionary) -> void:
	var t: Dictionary = tiles[i]
	for k in a:
		t.army[k] = int(t.army.get(k, 0)) - int(a[k])
		if t.ready.has(k):
			t.ready[k] = int(t.ready[k]) - mini(int(a[k]), int(t.ready[k]))
	sync_tile(t)


func lose_units(i: int, a: Dictionary) -> void:
	var t: Dictionary = tiles[i]
	for k in a:
		t.army[k] = int(t.army.get(k, 0)) - int(a[k])
	sync_tile(t)


## Adds "troops" of the faction's basic unit. A Robot troop is 2 Brawlers. Returns the units added.
func add_basic(i: int, pid: int, troops: int, ready: bool) -> int:
	var n: int = troops * int(faction_of(pid).basic_per_troop)
	add_units(i, basic_of(pid), n, ready)
	return n


# =====================================================================
# Economy
# =====================================================================

func income_of(pid: int) -> Dictionary:
	if is_myth(pid):
		return myth_income(pid)
	var hexes: int = 0
	var castles: int = 0
	var markets: int = 0
	for t in tiles:
		if int(t.owner) == pid:
			hexes += 1
			if t.castle:
				castles += 1
			markets += int(t.market)
	var nest: int = nest_gold(pid)
	var tusk: int = castles * int(TUSK_G[tusk_lv(pid)])   # Tusks and Thorns' Harvest (Mammals): every round, more gold for each castle
	var total: int = Economy.turn_income(mods_of(pid), hexes, castles, markets, nest) + tusk
	return {"hexes": hexes, "castles": castles, "markets": markets, "nest": nest, "tusk": tusk, "total": total}


## Dinosaur Nesting: once any Build action is upgraded, every hex with 3 buildings pays 2 extra gold.
func nest_gold(pid: int) -> int:
	if true:   # Nesting is retired (2026-11-11): the Dinosaurs' Build upgrades are their cards' own
		return 0
	var has_nesting: bool = false
	for c in faction_of(pid).cards:
		for slot in c.actions.size():
			if c.actions[slot] == "build" and lvl_of(pid, c.id, slot) >= 1:
				has_nesting = true
	if not has_nesting:
		return 0
	var n: int = 0
	for t in tiles:
		if int(t.owner) == pid and building_count(t) >= int(GameData.rules.dinos.nesting_buildings_needed):
			n += int(GameData.rules.dinos.nest_gold)
	return n


# =====================================================================
# Turn flow. A turn: collect income, play one card, carry out its 3 actions in order,
# then the played card goes to reserve and a random reserve card takes its place.
# =====================================================================

func begin_turn() -> void:
	var p: Dictionary = players[current]
	var inc: Dictionary = income_of(current)
	var inc_g: int = roundi(float(inc.total) * gold_mult(current))   # Expert collects extra gold
	p.gold = int(p.gold) + inc_g
	var tm: int = int(inc.get("castles", 0)) * int(TUSK_M[tusk_lv(current)]) if not is_myth(current) else 0
	if tm > 0:
		p.mat = mat_of(current) + tm   # Tusks and Thorns' Harvest: materials from every castle, every round
	p.upd_now = p.upd_next
	p.upd_next = false
	p.herd = false
	p.tr = 0   # materials bought from the markets this turn
	for t in tiles:
		if int(t.owner) == current:
			t.ready = t.army.duplicate()
			t.ready.erase("alamo")   # Alamosaurus guards never move
			sync_tile(t)
			if int(t.braced) == current:
				t.braced = -1
	if is_myth(current):
		_myth_turn_start(p)   # dome upkeep, the Floating Castle's Minions, Mages rooted to new trees
	play = {}
	add_log("%s collect %d %s%s." % [p.name, inc_g, cur_word(current), (" and %s" % mat_txt(tm)) if tm > 0 else ""])
	if p.upd_now:
		add_log("%s are updated: +1 attack and +1 damage this turn." % p.name)
	# Finished trebuchets fire once at the start of the turn, at an enemy hex next to them.
	volley = ready_trebs(current)
	if p.ai:
		for h in volley:
			var target: int = ai_treb_target(h)
			if target >= 0:
				fire_treb(h, target)
		volley = []
	else:
		run_volley()
	# The Dinosaurs' volcano erupts when it's due: once, at an enemy hex with units in reach.
	var vh: int = volc_ready(current) if is_dinos(current) else -1
	if vh >= 0:
		if p.ai:
			var vt: int = ai_volc_target(current)
			if vt >= 0:
				fire_volcano(vh, vt)
		else:
			volley.push_front(vh)
			run_volley()


## Plays a card from the current player's hand. If an upgrade is due, pass the action slot (0, 1 or 2)
## to upgrade. Returns false if the card can't be played.
func play_card(cid: String, upgrade_slot: int = -1) -> bool:
	var p: Dictionary = players[current]
	if over >= 0 or not play.is_empty() or not p.hand.has(cid):
		return false
	if upgrade_due(current, cid) and upgrade_slot < 0:
		if p.ai:
			upgrade_slot = ai_upgrade_pick(current, cid)
		else:
			return false
	play = {"card": cid, "step": 0, "moves": 0, "free_bk": false, "al_bought": 0, "al_free": 0}
	add_log("%s play %s." % [p.name, card_of(current, cid).name])
	gain_favor(current, cid, upgrade_slot)
	_enter_step()
	return true


## Runs "instant" actions (Harvest, Channeling) by themselves, then sets up the first action that needs the player.
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
	var a: String = cur_action()
	if a == "move":
		play.moves = 0
	if a == "advance" and named_on():
		if is_dinos(current):
			_populate(current)
		elif is_mammals(current):
			play.free_walls = int(GameData.rules.mammals.free_walls)   # Reforest
	if a == "recruit":
		_free_troops(current, cur_lvl())


func _is_instant(a: String) -> bool:
	return a == "harvest" or a == "channel"


## True when the card's last action is an instant one that has already run, so the turn can end.
func card_done() -> bool:
	if play.is_empty():
		return false
	var card: Dictionary = card_of(current, play.card)
	return int(play.step) >= card.actions.size() - 1 and _is_instant(cur_action())


## Moves on to the next action on the card, or ends the turn after the last one.
func next_step() -> void:
	if play.is_empty():
		return
	var card: Dictionary = card_of(current, play.card)
	if rg_due(current):   # Roam Free (Tusks and Thorns): the regroup after the Advancements
		play.rg = 1
		play.moves = 0
		return
	if int(play.get("rg", 0)) == 1:
		play.rg = 2
	if fx_next():
		return   # still inside a Fortify: the regroup, then the picks
	if int(play.step) < card.actions.size() - 1:
		play.step = int(play.step) + 1
		_enter_step()
	else:
		finish_turn()


func finish_turn() -> void:
	if over >= 0 or play.is_empty():
		return
	_rotate_cards(current)
	_advance_turn()
	if over < 0:
		begin_turn()


func _rotate_cards(pid: int) -> void:
	var p: Dictionary = players[pid]
	var cid: String = play.card
	var hand_index: int = p.hand.find(cid)
	var r: int = randi() % p.reserve.size()
	var new_card: String = p.reserve[r]
	p.reserve.remove_at(r)
	p.hand[hand_index] = new_card
	p.reserve.append(cid)
	p.last = cid


func _advance_turn() -> void:
	var done: int = current
	play = {}
	# Trebuchets being built count down at the end of their owner's turn.
	for t in tiles:
		if int(t.owner) != done:
			continue
		if int(t.treb) == 1:
			t.treb_due = int(t.treb_due) - 1
			if int(t.treb_due) <= 0:
				t.treb = 2
				add_log("%s trebuchet is finished." % players[done].name)
		if int(t.treb2) == 1:
			t.treb2_due = int(t.treb2_due) - 1
			if int(t.treb2_due) <= 0:
				t.treb2 = 2
				add_log("%s second castle trebuchet is finished." % players[done].name)
	# The side under pressure has just used one of its turns without breaking the hold.
	if not siege.is_empty() and done != int(siege.pid):
		siege.left = int(siege.left) - 1
		if int(siege.left) <= 0:
			add_log("%s held %d castles and win!" % [players[int(siege.pid)].name, int(GameData.rules.castles.to_win)])
			_end_game(int(siege.pid), "hold")
			return
	# the next side still in the game; a new round starts each time play passes the first seat
	var n: int = players.size()
	var c: int = done
	var round_done: bool = false
	for k in n:
		c = (c + 1) % n
		if c == first:
			round_done = true
		if not bool(players[c].get("out", false)):
			break
	current = c
	if round_done:
		turn += 1
		if turn == int(GameData.rules.castles.new_neutral_after_round) + 1 and extra_castle < 0:
			_spawn_castle()


func _end_game(winner: int, why: String) -> void:
	over = winner
	over_why = why


## Checks the win conditions. Call after anything that changes who owns a hex.
func check_castles() -> void:
	if over >= 0:
		return
	if players.size() > 2:   # 3 players: no castle-count win; a side with no land left is out
		for q in players:
			if bool(q.get("out", false)) or over >= 0:
				continue
			if not tiles.any(func(t): return int(t.owner) == int(q.id)):
				knock_out(int(q.id), -1, "wipe")
		return
	for pid in [0, 1]:
		var has_land: bool = false
		for t in tiles:
			if int(t.owner) == pid:
				has_land = true
				break
		if not has_land:
			add_log("%s have no land left." % players[pid].name)
			_end_game(1 - pid, "wipe")
			return
	var to_win: int = int(GameData.rules.castles.to_win)
	var holder: int = -1
	for pid in [0, 1]:
		if castle_count(pid) >= to_win:
			holder = pid
	if not siege.is_empty() and holder != int(siege.pid):
		add_log("%s no longer hold %d castles." % [players[int(siege.pid)].name, to_win])
		siege = {}
	if holder >= 0 and siege.is_empty():
		siege = {"pid": holder, "left": int(GameData.rules.castles.hold_turns)}
		add_log("%s hold %d castles! %s have %d turns to take one back." % [players[holder].name, to_win, players[1 - holder].name, int(GameData.rules.castles.hold_turns)])


## After round 18, a new neutral castle appears about as far from one home as the other.
func _spawn_castle() -> void:
	var open: Array = tiles.filter(func(t): return t.terrain == "plain" and not t.castle and int(t.owner) < 0 and int(t.troops) == 0)
	var hs: Array = []
	for k in players.size():
		if not is_out(k):
			hs.append(homes[k])
	var pool: Array = open.filter(func(t):
		var ds: Array = hs.map(func(h): return HexGrid.distance(t.id, h))
		return ds.max() - ds.min() <= 1)
	if pool.is_empty():
		pool = open
	if pool.is_empty():
		pool = tiles.filter(func(t): return t.terrain == "plain" and not t.castle and int(t.troops) == 0)
	if pool.is_empty():
		return
	var t: Dictionary = pool[randi() % pool.size()]
	t.castle = true
	t.owner = -1
	t.bounty = false
	t.crate = false
	t.market = 0
	t.fort = 0
	t.barracks = 0
	t.braced = -1
	extra_castle = int(t.id)
	add_log("Round %d is over: a new neutral castle rises." % int(GameData.rules.castles.new_neutral_after_round))


# =====================================================================
# Instant actions: Harvest and Fortify
# =====================================================================

func _resolve_instant(a: String) -> void:
	var p: Dictionary = players[current]
	var lvl: int = cur_lvl()
	if a == "channel":
		myth_channel(current)
		return
	if a == "harvest":
		var industry: int = 0
		if is_robots(current) and named_on():
			for t in tiles:
				if int(t.owner) == current:
					industry += int(t.barracks)
			industry *= int(mods_of(current).marketGold)
		var hexes: int = int(income_of(current).hexes)
		var fert: int = 0
		if is_mammals(current) and named_on():   # Fertilize: 1 gold for every 2 units they have
			for t in tiles:
				if int(t.owner) == current:
					fert += int(t.troops)
			fert /= 2
		var dh: Dictionary = dino_harvest(current) if is_dinos(current) else (robo_harvest(current) if is_robots(current) else (mamm_harvest(current) if is_mammals(current) else {"g": 0, "m": 0, "why": []}))
		var g: int = roundi(float(Economy.harvest_gold(mods_of(current), lvl, hexes, false) + industry + fert + int(dh.g)) * gold_mult(current))
		p.gold = int(p.gold) + g
		if int(dh.m) > 0:
			p.mat = mat_of(current) + int(dh.m)
		if not dh.why.is_empty():
			add_log("%s harvest %d gold%s (%s)." % [p.name, g, (" and %s" % mat_txt(int(dh.m))) if int(dh.m) > 0 else "", ", ".join(dh.why)])
		else:
			add_log("%s harvest %d %s%s." % [p.name, g, cur_word(current), (" (%d from fertile land)" % fert) if fert > 0 else ""])


## An upgraded Recruit starts with free troops at every castle and barracks.
func _free_troops(pid: int, lvl: int) -> int:
	if lvl <= 0:
		return 0
	var at_castle: Array = GameData.rules.actions.recruit.free_at_castle_by_level
	var at_barracks: Array = GameData.rules.actions.recruit.free_at_barracks_by_level
	var n: int = 0
	for t in tiles:
		if int(t.owner) != pid:
			continue
		var k: int = 0
		if t.castle:
			k = int(at_castle[lvl])
		elif int(t.barracks) > 0:
			k = int(at_barracks[lvl]) * int(t.barracks)
		if k > 0:
			n += add_basic(int(t.id), pid, k, true)
	if n > 0:
		add_log("%s get %d free units from an upgraded Recruit." % [players[pid].name, n])
	return n


## Robots' Factory: 5 Brawlers at the home castle.
func _factory(pid: int) -> void:
	var h: Dictionary = tiles[homes[pid]]
	if int(h.owner) != pid:
		return
	var n: int = int(GameData.rules.robots.factory_units)
	add_units(homes[pid], "brawler", n, true)
	add_log("%s factory builds %d Brawlers at their home castle." % [players[pid].name, n])


## The Mammals' Mating: on every hex they hold, each pair of the same unit makes one more of it, up to 3 new units per hex.
## Every kind with a pair gets its first young before any kind gets a second (strongest kinds first).
func _mating(pid: int) -> Array:
	var ids: Array = []
	var n: int = 0
	var cap: int = int(GameData.rules.mammals.mate_max)
	for t in tiles:
		if int(t.owner) != pid or int(t.troops) == 0:
			continue
		var pairs: Dictionary = {}
		for k in _by_strength(t.army):
			var q: int = int(t.army[k]) / 2
			if q > 0:
				pairs[k] = q
		var got: Dictionary = {}
		var room: int = cap
		while room > 0 and not pairs.is_empty():
			for k in pairs.keys():
				if room <= 0:
					break
				got[k] = int(got.get(k, 0)) + 1
				room -= 1
				pairs[k] = int(pairs[k]) - 1
				if int(pairs[k]) <= 0:
					pairs.erase(k)
		var m: int = _count(got)
		if m > 0:
			_add_army(int(t.id), got, true)
			n += m
			ids.append(int(t.id))
	if n > 0:
		add_log("%s breed: %d young born on %d hex%s." % [players[pid].name, n, ids.size(), "" if ids.size() == 1 else "es"])
	return ids


## Dinosaurs' Populate: 1 free Gallimimus per fort and barracks.
func _populate(pid: int) -> void:
	var n: int = 0
	for t in tiles:
		if int(t.owner) != pid:
			continue
		var k: int = int(t.barracks)   # the Dinosaurs have no forts
		if k > 0:
			add_units(int(t.id), "galli", k, true)
			n += k
	if n > 0:
		add_log("%s populate: %d free %s at their barracks." % [players[pid].name, n, GameData.units.galli.name])


# =====================================================================
# Recruit: basic units at castles and barracks; other units from barracks and fort menus
# =====================================================================

func can_recruit_at(t: Dictionary) -> bool:
	return t.castle or int(t.barracks) > 0 or in_numbers(t)


func unit_cost_at(i: int, pid: int, unit: String) -> int:
	var t: Dictionary = tiles[i]
	var cost: int = int(GameData.units[unit].cost)
	if int(t.barracks) > 0 and int(t.bk) >= 3:
		cost -= 1
	var hu: int = dk(pid, "hunt", "recruit")
	if hu >= 1 and is_home_castle(t) and int(t.owner) == pid:
		cost -= 1   # Home Hunters (The Hunt)
	if hu >= 3 and int(t.barracks) > 0:
		cost -= 1   # Nest Hunters (The Hunt)
	if is_robots(pid) and bool(GameData.units[unit].get("air", false)):
		cost -= dk(pid, "deploy", "recruit")   # Drone Line, Air Wing, Sky Fleet (Deploy)
	if int(t.get("wh", 0)) > 0 and is_mammals(pid) and GameData.rules.mammals.wh_units.has(unit):
		cost -= int(GameData.rules.mammals.wh_off)   # a Watering Hole
	if is_mammals(pid):
		if dk(pid, "den", "recruit") >= 1:
			cost -= 1   # Den Prices (Den Season)
		if dk(pid, "wild", "recruit") >= 3 and is_home_castle(t) and int(t.owner) == pid:
			cost -= 2   # Home Calling (Call of the Wild)
	return maxi(1, cost)


func unlocks_of(pid: int) -> Dictionary:
	return players[pid].unl


func _note_unlock(pid: int, kind: String, t: Dictionary) -> void:
	var u: Dictionary = unlocks_of(pid)
	if kind == "barracks":
		u.bk = maxi(int(u.bk), int(t.bk))
	elif kind == "fort":
		u.fort = true


func has_menu(t: Dictionary, menu: String) -> bool:
	if int(t.get(menu, 0)) > 0:
		return true
	if menu == "barracks" and in_numbers(t):
		return true   # In Numbers: the army itself is the barracks
	if not is_home_castle(t):
		return false
	if menu == "barracks":
		return true
	if menu == "fort":
		return bool(unlocks_of(int(t.owner)).fort)
	return false


func barracks_needed(unit: String) -> int:
	return int(GameData.rules.barracks_unlocks.get(unit, 0))


func train_ok(t: Dictionary, menu: String, unit: String) -> bool:
	if menu != "barracks":
		return true
	var herd: int = 2 if in_numbers(t) else -1   # In Numbers: a big enough army recruits like a level 2 barracks
	if int(t.barracks) == 0 and is_home_castle(t):
		var u: Dictionary = unlocks_of(int(t.owner))
		return unit == basic_of(int(t.owner)) or maxi(int(u.bk), herd) >= barracks_needed(unit)
	if int(t.barracks) == 0 and herd >= 0:
		return herd >= barracks_needed(unit)
	return maxi(int(t.bk), herd) >= barracks_needed(unit)


## Buys n of the basic unit at a castle or barracks. Robots' Assembly Line gives a free Brawler per 2 bought.
func recruit(i: int, n: int) -> bool:
	var t: Dictionary = tiles[i]
	var p: Dictionary = players[current]
	var unit: String = basic_of(current)
	var cost: int = n * unit_cost_at(i, current, unit)
	if cur_action() != "recruit" or n < 1 or int(p.gold) < cost or int(t.owner) != current or not can_recruit_at(t):
		return false
	p.gold = int(p.gold) - cost
	add_units(i, unit, n, true)
	t.new_t = turn
	mamm_bought(current, unit, n)   # Hide Trade and Tusk Trade (Call of the Wild)
	var free: int = 0
	if dk(current, "mobil", "recruit") >= 1:   # Assembly Line (Mobilize)
		play.al_bought = int(play.al_bought) + n
		free = int(play.al_bought) / 2 - int(play.al_free)
		if free > 0:
			play.al_free = int(play.al_free) + free
			add_units(i, unit, free, true)
	var extra: String = (" and %d free" % free) if free > 0 else ""
	add_log("%s recruit %d %s%s." % [p.name, n, GameData.units[unit].name, extra])
	return true


## Trains n units from a barracks or fort menu.
func train(i: int, unit: String, menu: String, n: int = 1) -> bool:
	var t: Dictionary = tiles[i]
	var p: Dictionary = players[current]
	var menu_units: Array = faction_of(current).training.get(menu, [])
	var cost: int = n * unit_cost_at(i, current, unit)
	if cur_action() != "recruit" or n < 1 or not menu_units.has(unit) or not has_menu(t, menu):
		return false
	if int(t.owner) != current or int(p.gold) < cost or not train_ok(t, menu, unit):
		return false
	if unit == basic_of(current) and menu == "barracks":
		return recruit(i, n)   # keeps the Assembly Line bonus
	p.gold = int(p.gold) - cost
	add_units(i, unit, n, true)
	t.new_t = turn
	mamm_bought(current, unit, n)   # Hide Trade and Tusk Trade (Call of the Wild)
	add_log("%s train %d %s." % [p.name, n, GameData.units[unit].name])
	return true


# =====================================================================
# Build: markets, forts and barracks
# =====================================================================

func max_buildings() -> int:
	if not play.is_empty() and is_robots(current):
		return robo_markets()   # Robots: one factory per hex, or up to 4 markets on a resource hex
	return int(GameData.rules.buildings.max_per_hex)


## A building's price now (markets in gold, the rest in materials); t is the hex it goes on, when known.
func build_cost(kind: String, t: Dictionary = {}) -> int:
	var c: int = int(GameData.rules.buildings.cost_by_level[kind][cur_lvl()])
	if not play.is_empty() and is_dinos(current) and cur_action() == "build":
		return dino_cost(current, kind, c, t)
	if not play.is_empty() and is_robots(current) and cur_action() == "build":
		return robo_cost(current, kind, c, t)
	if not play.is_empty() and is_mammals(current) and cur_action() == "build":
		return mamm_cost(current, kind, c, t)
	return c


func build(i: int, kind: String) -> bool:
	var t: Dictionary = tiles[i]
	var p: Dictionary = players[current]
	var price: int = build_cost(kind, t)
	if cur_action() != "build" or building_count(t) >= max_buildings() or not can_pay_b(current, kind, price):
		return false
	if int(t.owner) != current or t.terrain != "plain":
		return false
	if kind == "wh" and (not is_mammals(current) or int(t.get("wh", 0)) > 0):
		return false   # Watering Hole: a Mammal building in any Build (since 2026-11-13), one per hex
	if t.castle and kind != "market" and kind != "wh":
		return false
	if kind == "fort" and is_dinos(current):
		return false   # the Dinosaurs build no forts
	if is_robots(current) and (kind != "market" or not robo_can_market(t)):
		return false   # Robots: markets only; barracks and fortresses are factory upgrades from the home castle
	pay_b(current, kind, price)
	_dino_built(current, kind, price)
	t[kind] = int(t.get(kind, 0)) + 1
	_note_unlock(current, kind, t)
	add_log("%s build a %s." % [p.name, kind])
	return true


# =====================================================================
# Advancements: barracks upgrades, trebuchets and walls
# =====================================================================

func upgrade_barracks(i: int) -> bool:
	var t: Dictionary = tiles[i]
	var p: Dictionary = players[current]
	var lv: int = int(t.bk)
	if cur_action() != "advance" or int(t.owner) != current or int(t.barracks) == 0 or lv >= 3:
		return false
	var free: bool = ((cur_lvl() >= 1 and lv == 0) or dk(current, "tusks", "advance") >= 1) and not bool(play.free_bk)   # Free Den Upgrade (Tusks and Thorns): the first one, any level
	var price: int = 0 if free else bk_up_cost(current, lv, t)
	if mat_of(current) < price:
		return false
	spend_mat(current, price)
	if free:
		play.free_bk = true
	t.bk = lv + 1
	_note_unlock(current, "barracks", t)
	add_log("%s upgrade a barracks to level %d%s." % [p.name, int(t.bk), " for free" if free else ""])
	robo_muster(current, t)   # Muster (Onslaught)
	return true


func treb_count(t: Dictionary) -> int:
	return (1 if int(t.treb) > 0 else 0) + (1 if int(t.treb2) > 0 else 0)


func can_treb_at(t: Dictionary) -> bool:
	if int(t.owner) >= 0 and is_dinos(int(t.owner)):
		return false   # the Dinosaurs have the volcano instead
	if t.castle:
		return treb_count(t) < int(GameData.rules.trebuchet.castle_max)
	return int(t.fort) > 0 and int(t.treb) == 0


func treb_price(t: Dictionary) -> int:
	var tr: Dictionary = GameData.rules.trebuchet
	if t.castle:
		return int(tr.castle_cost[mini(1, treb_count(t))])
	return int(tr.field_cost)


func treb_turns(t: Dictionary, lvl: int) -> int:
	var tr: Dictionary = GameData.rules.trebuchet
	if t.castle:
		return int(tr.castle_build_turns) - (1 if lvl >= 3 else 0)
	return int(tr.field_build_turns_level_3) if lvl >= 3 else int(tr.field_build_turns)


func start_trebuchet(i: int) -> bool:
	var t: Dictionary = tiles[i]
	var p: Dictionary = players[current]
	if cur_action() != "advance" or int(t.owner) != current or not can_treb_at(t):
		return false
	var price: int = treb_price(t)
	if mat_of(current) < price:
		return false
	spend_mat(current, price)
	var turns: int = treb_turns(t, cur_lvl())
	if int(t.treb) == 0:
		t.treb = 1
		t.treb_due = turns
	else:
		t.treb2 = 1
		t.treb2_due = turns
	add_log("%s start building a trebuchet, ready in %d turns." % [p.name, turns])
	return true


## The sides of hex i that can hold a wall: those facing plain land or a mountain.
func wall_sides(i: int) -> Array[int]:
	var out: Array[int] = []
	for j in HexGrid.neighbors(i):
		var tr: String = tiles[j].terrain
		if tr == "plain" or tr == "mountain":
			out.append(j)
	return out


## The edge number (0 to 5) of hex i that faces hex j, or -1 if they aren't neighbours.
func side_of(i: int, j: int) -> int:
	return HexGrid.neighbor_dirs(i).find(j)


func wall_on(i: int, j: int) -> int:
	if int(tiles[i].get("dome", 0)) > 0:   # a magic dome guards every side
		return int(tiles[i].dome)
	var k: int = side_of(i, j)
	return int(tiles[i].walls[k]) if k >= 0 else 0


func set_wall(i: int, j: int, hp: int) -> void:
	if int(tiles[i].get("dome", 0)) > 0:
		tiles[i].dome = maxi(0, hp)
		return
	var k: int = side_of(i, j)
	if k >= 0:
		tiles[i].walls[k] = maxi(0, hp)


func wall_cost() -> int:
	if free_walls_left() > 0:
		return 0
	return int(GameData.rules.walls.cost_by_level[cur_lvl()])


## Reforest (Mammals): free walls still to place in this Advancements.
func free_walls_left() -> int:
	return int(play.get("free_walls", 0)) if (not play.is_empty() and cur_action() == "advance") else 0


func build_wall(i: int, j: int) -> bool:
	var t: Dictionary = tiles[i]
	var p: Dictionary = players[current]
	var price: int = wall_cost()
	var hp: int = int(GameData.rules.walls.hp)
	var was: int = wall_on(i, j)
	if cur_action() != "advance" or int(t.owner) != current or not wall_sides(i).has(j) or was >= hp or mat_of(current) < price:
		return false
	spend_mat(current, price)
	if free_walls_left() > 0:
		play.free_walls = int(play.free_walls) - 1
	set_wall(i, j, hp)
	add_log("%s %s a wall." % [p.name, "repair" if was > 0 else "build"])
	return true


# =====================================================================
# Moving. Ported from canEnter, passThrough, moveTargets, approachOf and wallFacing.
# One move goes 1 hex into new land, onto a mountain, or into an attack (2 at Move level 3),
# and up to 2 hexes through your own land (3 at level 3). Dinosaur Migrate: any distance through your own land.
# =====================================================================

func moves_left() -> int:
	if play.is_empty():
		return 0
	return maxi(0, moves_limit(current) - int(play.moves))


func can_enter(i: int, lvl: int) -> bool:
	var tr: String = tiles[i].terrain
	return tr == "plain" or (tr == "mountain" and lvl >= 1)


func _pass_through(from: int, a: int, lvl: int, pid: int) -> bool:
	var t: Dictionary = tiles[a]
	if not can_enter(a, lvl):
		return false
	return not (int(t.owner) != pid and (int(t.troops) > 0 or wall_on(a, from) > 0))


func _own_road(i: int, pid: int) -> bool:
	return int(tiles[i].owner) == pid and tiles[i].terrain == "plain"


## Every hex the units on "from" can reach with one move at this Move level (units that can't make a particular move,
## see move_filter, are left out of it).
func move_targets(from: int, lvl: int) -> Array[int]:
	var t: Dictionary = tiles[from]
	var pid: int = int(t.owner)
	var far: bool = false
	if is_myth(pid):
		for k in t.ready:
			if int(t.ready[k]) > 0 and fast_unit(k):
				far = true
	var out: Array[int] = []
	var co: bool = charge_only(pid)
	var cand: Array[int] = _move_targets_core(from, lvl, far)
	if pid >= 0 and is_robots(pid):   # the Robots' card moves: flyers, Brawlers and new units
		for x in robo_move_extra(from, lvl):
			for i in x["hexes"]:
				if not cand.has(int(i)):
					cand.append(int(i))
	for i in cand:
		if co and not (int(tiles[i].owner) >= 0 and int(tiles[i].owner) != pid):
			continue   # Charge: the extra move is an attack
		var f: Callable = move_filter(from, i, lvl)
		if not f.is_valid():
			out.append(i)
			continue
		for k in t.ready:
			if int(t.ready[k]) > 0 and f.call(k):
				out.append(i)
				break
	return out


func _move_targets_core(from: int, lvl: int, far: bool) -> Array[int]:
	var pid: int = int(tiles[from].owner)
	if regrouping() and pid == current:
		return regroup_targets(from, 99 if (dk(pid, "sprot", "fortify") >= 3 and from == homes[pid]) else fx_reach())   # Home Link (Siege Protocol)
	var any_run: Array = GameData.rules.moves.any_run
	var own_run: Array = GameData.rules.moves.own_run
	var out: Dictionary = {}
	for a in HexGrid.neighbors(from):
		if not can_enter(a, lvl):
			continue
		out[a] = true
		if (int(any_run[lvl]) >= 2 or far) and _pass_through(from, a, lvl, pid):
			for b in HexGrid.neighbors(a):
				if b != from and can_enter(b, lvl):
					out[b] = true
	var run: int = int(own_run[lvl])
	var frontier: Array[int] = [from]
	var seen: Dictionary = {from: true}
	for d in run:
		var next: Array[int] = []
		for c in frontier:
			for n in HexGrid.neighbors(c):
				if not seen.has(n) and _own_road(n, pid):
					seen[n] = true
					out[n] = true
					next.append(n)
		if next.is_empty():
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
	out.erase(from)
	var result: Array[int] = []
	for k in out:
		result.append(int(k))
	return result


## The hex a move into "to" comes across from: "from" when next door, otherwise the in-between hex
## facing the weakest wall.
func approach_of(from: int, to: int, lvl: int) -> int:
	if HexGrid.neighbors(from).has(to):
		return from
	var pid: int = int(tiles[from].owner)
	var best: int = from
	var best_wall: int = 999
	for a in HexGrid.neighbors(from):
		if HexGrid.neighbors(a).has(to) and _pass_through(from, a, lvl, pid):
			var w: int = wall_on(to, a)
			if w < best_wall:
				best_wall = w
				best = a
	return best


## An enemy castle with nobody in it (not a home castle) falls without a fight.
func open_castle(t: Dictionary) -> bool:
	return t.castle and int(t.troops) == 0 and home_guards(t).is_empty()


## The enemy wall a move must break first (0 if none).
func wall_facing(from: int, to: int, lvl: int) -> int:
	var A: Dictionary = tiles[from]
	var B: Dictionary = tiles[to]
	if int(B.owner) >= 0 and int(B.owner) != int(A.owner) and not open_castle(B):
		return wall_on(to, approach_of(from, to, lvl))
	return 0


# =====================================================================
# Defense. Ported from homeGuards, defArmy, realLosses, braced, bracedBonus, castleDef,
# defBonus, defAdv, atkOpts and arenaMap.
# =====================================================================

## A home castle's hidden guards: 5 of the faction's archers, there for every fight.
func home_guards(t: Dictionary) -> Dictionary:
	if not is_home_castle(t):
		return {}
	var k: String = String(faction_of(int(t.owner)).guard_unit)
	if is_myth(int(t.owner)):   # the Floating Castle: 1 Griffin (Claude's stand-in)
		return {k: int(GameData.rules.mythical.guards)}
	return {k: int(GameData.rules.castles.home_guards_archers)}


func def_army(t: Dictionary) -> Dictionary:
	var a: Dictionary = t.army.duplicate()
	var g: Dictionary = home_guards(t)
	for k in g:
		a[k] = int(a.get(k, 0)) + int(g[k])
	return a


## Losses from a fight at a home castle: the guards fall first; the rest come off the real garrison.
func real_losses(t: Dictionary, lost: Dictionary) -> Dictionary:
	var g: Dictionary = home_guards(t)
	if g.is_empty():
		return lost
	var r: Dictionary = {}
	for k in lost:
		var m: int = int(lost[k]) - int(g.get(k, 0))
		if m > 0:
			r[k] = m
	return r


## Fortify gave +1 defense until 2026-11-10; it's a wild card now, so nothing is braced any more.
func braced(t: Dictionary) -> bool:
	return false


func braced_bonus(t: Dictionary) -> int:
	if not braced(t):
		return 0
	if int(t.bl) >= 1 and (t.castle or int(t.fort) > 0):
		return 2
	return int(mods_of(int(t.owner)).fortifyBonus)


func castle_def(t: Dictionary) -> int:
	if is_home_castle(t):
		return int(GameData.rules.castles.home_defense)
	if int(t.owner) >= 0:
		return int(mods_of(int(t.owner)).castleDefense)
	return int(GameData.factions.base_mods.castleDefense)


## The defender's bonus on the luck die: castles, +1 per fort, and Fortify.
func def_bonus(t: Dictionary) -> int:
	var b: int = 0
	if t.castle:
		b = castle_def(t)
	elif int(t.owner) >= 0 and not is_myth(int(t.owner)) and not is_dinos(int(t.owner)):   # captured forts do nothing for the Mythical or the Dinosaurs
		b = int(t.fort) * int(mods_of(int(t.owner)).fortDefense)
	return b + braced_bonus(t)


func def_adv(t: Dictionary) -> bool:
	return braced(t) and int(t.bl) >= 2 and (t.castle or int(t.fort) > 0)


## The attacker's options: Move level 2+ attacks with advantage; Robot Update and Offline.
func atk_opts(pid: int, lvl: int, raw: int, defender: int) -> Dictionary:
	var p: Dictionary = players[pid]
	var up: bool = bool(p.upd_now)
	var herd: bool = defender >= 0 and bool(players[defender].herd)
	var offline: bool = (dk(pid, "mobil", "move") >= 3 or dk(pid, "tusks", "move") >= 2) and not herd   # Offline (Mobilize), Ambush (Tusks and Thorns)
	var a_arm: bool = armor_on(pid)   # Armor (The Hunt): +2 damage and +10% health for that side
	var d_arm: bool = armor_on(defender)
	var ad: int = int(armor_rules().dmg)
	return {"adv_a": lvl >= 2 and not is_dinos(pid), "a_bonus": 1 if up else 0, "a_plus": (1 if up else 0) + (ad if a_arm else 0),
		"d_plus": ad if d_arm else 0, "a_arm": a_arm, "d_arm": d_arm, "arm_hp": float(armor_rules().hp), "surprise": offline}


## Which Arena map a fight on this hex uses.
func arena_map(t: Dictionary) -> String:
	if t.castle:
		return "castle"
	if int(t.fort) > 0:
		return "fortress"
	if t.terrain == "mountain":
		return "mountain"
	if t.forest:
		return "trees"
	if t.fern:
		return "ferns"
	return "open"


## True when a move from "from" into "to" is a battle against units (or a home castle's guards).
func is_fight(from: int, to: int) -> bool:
	var A: Dictionary = tiles[from]
	var B: Dictionary = tiles[to]
	return int(B.owner) >= 0 and int(A.owner) >= 0 and int(B.owner) != int(A.owner) and (int(B.troops) > 0 or not home_guards(B).is_empty())


## The full battle options for an attack from "from" into "to", for odds or the fight itself.
func battle_options(from: int, to: int, lvl: int) -> Dictionary:
	var A: Dictionary = tiles[from]
	var B: Dictionary = tiles[to]
	var raw: int = raw_lvl() if (not play.is_empty() and current == int(A.owner)) else 0
	var o: Dictionary = atk_opts(int(A.owner), lvl, raw, int(B.owner))
	o.wall = wall_facing(from, to, lvl)
	o.bonus = def_bonus(B)
	o.adv_d = def_adv(B)
	o.map = arena_map(B)
	return o


# =====================================================================
# Carrying out a move. Ported from pickUnits and executeMove (the auto-resolved battle;
# live Arena battles come once the Arena is ported).
# =====================================================================

func _by_strength(a: Dictionary) -> Array:
	var ks: Array = a.keys().filter(func(k): return int(a[k]) > 0)
	ks.sort_custom(func(x, y): return int(GameData.units[x].cost) > int(GameData.units[y].cost))
	return ks


## n ready units from a hex, strongest first (or weakest first).
func pick_units(i: int, n: int, weak: bool = false) -> Dictionary:
	var t: Dictionary = tiles[i]
	var out: Dictionary = {}
	var ks: Array = _by_strength(t.ready)
	if weak:
		ks.reverse()
	for k in ks:
		if n <= 0:
			break
		var m: int = mini(n, int(t.ready[k]))
		out[k] = m
		n -= m
	return out


## The player's move during a Move action. sel is {unit: count} from the units ready on "from".
## Returns the result (see execute_move), or an empty Dictionary if the move isn't allowed.
func move(from: int, to: int, sel: Dictionary, join: bool = false) -> Dictionary:
	if cur_action() != "move" or moves_left() <= 0:
		return {}
	if int(tiles[from].owner) != current or not move_targets(from, cur_lvl()).has(to):
		return {}
	var clean: Dictionary = {}
	for k in sel:
		var m: int = mini(int(sel[k]), int(tiles[from].ready.get(k, 0)))
		if m > 0:
			clean[k] = m
	clean = _move_sel(from, to, clean, cur_lvl())
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
		add_log("Two Herds: %d more units join the attack." % _count(add))
	if arena_fights and is_fight(from, to) and needs_arena(current, int(tiles[to].owner)):
		return {"kind": "fight", "from": from, "to": to, "sel": clean, "lvl": cur_lvl(), "att": current, "def": int(tiles[to].owner),
			"mods": fight_mods(current, cur_lvl(), int(tiles[to].owner))}
	return execute_move(from, to, clean, cur_lvl())


## The Arena's side for a player: Blue (0) is the Dinosaurs, Red (1) the Robots.
## A side's Arena team (Blue 0, Red 1) against "other" (with 2 players, the other player).
func arena_team(pid: int, other: int = -1) -> int:
	if other < 0:
		other = 1 - pid if players.size() == 2 else (1 if pid == 0 else 0)
	var T: Dictionary = GameData.factions.arena_team
	var f: String = String(players[pid].faction)
	var o: String = String(players[other].faction)
	if f == o:
		return 0 if pid < other else 1
	if T.has(f):
		return int(T[f])
	return 1 - int(T[o]) if T.has(o) else (0 if pid < other else 1)


## The attacker's abilities that go into an Arena battle: Offline (unless the defenders are in a Herd) and Update.
## Only these carry over; the board's walls, defense bonuses and luck dice don't count in the Arena.
const UPDATE_MULT := 1.12   # the board's +1 on the luck die is about 12% more damage
func fight_mods(att: int, lvl: int, defender: int) -> Dictionary:
	var raw: int = raw_lvl() if (not play.is_empty() and current == att) else 0
	var o: Dictionary = atk_opts(att, lvl, raw, defender)
	return {"sneak": bool(o.surprise), "plus": int(o.a_plus) - (int(armor_rules().dmg) if bool(o.a_arm) else 0), "mult": UPDATE_MULT if int(o.a_bonus) > 0 else 1.0,
		"arm_a": bool(o.a_arm), "arm_d": bool(o.d_arm)}


## The same, as the Arena takes them: by Arena team (Blue 0, Red 1).
func arena_mods(fight: Dictionary) -> Dictionary:
	var m: Dictionary = fight.get("mods", {})
	var t: int = arena_team(int(fight.att), int(fight.def))
	var out: Dictionary = {"sneak": t if bool(m.get("sneak", false)) else -1, "plus": [0, 0], "mult": [1.0, 1.0], "hp": [1.0, 1.0]}
	out.plus[t] = int(m.get("plus", 0))
	out.mult[t] = float(m.get("mult", 1.0))
	var ar: Dictionary = armor_rules()
	if bool(m.get("arm_a", false)):   # Armor (The Hunt)
		out.plus[t] = int(out.plus[t]) + int(ar.dmg)
		out.hp[t] = float(ar.hp)
	if bool(m.get("arm_d", false)):
		out.plus[1 - t] = int(out.plus[1 - t]) + int(ar.dmg)
		out.hp[1 - t] = float(ar.hp)
	return out


## Both armies for an Arena fight, as [blue, red].
func fight_armies(fight: Dictionary) -> Array:
	var armies: Array = [{}, {}]
	var ta: int = arena_team(int(fight.att), int(fight.def))
	armies[ta] = fight.sel
	armies[1 - ta] = def_army(tiles[int(fight.to)])
	return armies


## Applies what the Arena handed back: the units left, fled and lost on each side.
func finish_fight(fight: Dictionary, out: Dictionary) -> Dictionary:
	return execute_move(int(fight.from), int(fight.to), fight.sel, int(fight.lvl), out)


func execute_move(from: int, to: int, sel: Dictionary, lvl: int, ar: Dictionary = {}) -> Dictionary:
	var A: Dictionary = tiles[from]
	var B: Dictionary = tiles[to]
	var pid: int = int(A.owner)
	var p: Dictionary = players[pid]
	sel = _move_sel(from, to, sel, lvl)
	if CombatRules.count(sel) == 0:
		return {"from": from, "to": to, "n": 0, "sent": {}, "kind": "none", "att": pid}
	var src: int = approach_of(from, to, lvl)
	var W: int = 0
	if int(B.owner) >= 0 and int(B.owner) != pid and not open_castle(B):
		W = wall_on(to, src)
	take_units(from, sel)
	var res: Dictionary = {"from": from, "to": to, "n": CombatRules.count(sel), "sent": sel.duplicate(), "kind": "move", "att": pid}
	if int(B.owner) == pid:
		var rg: bool = regrouping() and pid == current
		if rg and fx_on() and int(play.fx.get("far", 0)) > 0 and not regroup_targets(from, regroup_reach()).has(to):
			play.fx.far = int(play.fx.far) - 1   # Join Up used
		_add_army(to, sel, rg)   # a regroup leaves them ready to move again
		return res
	var prev: int = int(B.owner)
	res.def_owner = prev
	var survivors: Dictionary = sel
	if not ar.is_empty() and (int(B.troops) > 0 or not home_guards(B).is_empty()):
		# fought in the Arena: what was left standing decides it
		var tA: int = arena_team(pid, prev)
		var tD: int = 1 - tA
		var def_start: Dictionary = def_army(B)
		var att_left: Dictionary = ar.left[tA]
		var def_left: Dictionary = ar.left[tD]
		var att_esc: Dictionary = ar.esc[tA]
		var def_esc: Dictionary = ar.esc[tD]
		var att_lost: Dictionary = _minus(sel, [att_left, att_esc])
		var def_lost: Dictionary = _minus(def_start, [def_left, def_esc])
		var gone: Dictionary = real_losses(B, _minus(def_start, [def_left]))   # dead or fled; home guards count first
		var fled: Dictionary = _clip(def_esc, gone)
		fled.erase("alamo")   # an Alamosaurus guard never leaves its barracks: if it runs, it's lost
		var dead_units: Dictionary = _minus(gone, [fled])
		lose_units(to, gone)
		var won: bool = CombatRules.count(def_left) == 0 and CombatRules.count(att_left) > 0 and not bool(ar.stalemate) and int(ar.fled) != tA
		res.kind = "battle"
		res.arena = true
		res.def_start = def_start
		res.att_lost = att_lost
		res.def_lost = def_lost
		res.won = won
		res.wall_start = 0
		res.wall_lost = 0
		# defenders who got away fall back to their own land next door (the biggest garrison), if there is any
		if CombatRules.count(fled) > 0:
			var back: int = -1
			var most: int = -1
			for j in HexGrid.neighbors(to):
				var nt: Dictionary = tiles[j]
				if int(nt.owner) == prev and nt.terrain != "water" and nt.terrain != "void" and int(nt.troops) > most:
					most = int(nt.troops)
					back = j
			if back >= 0:
				_add_army(back, fled, false)
		if CombatRules.count(att_esc) > 0:
			_add_army(from, att_esc, false)   # attackers who fled go home
		var a_n: int = CombatRules.count(att_lost)
		var d_n: int = CombatRules.count(dead_units)
		if not won:
			if CombatRules.count(att_left) > 0:
				_add_army(from, att_left, false)   # a stalled attack falls back
			var how: String = "pull back" if int(ar.fled) == tA else ("can't break them" if bool(ar.stalemate) else "are beaten")
			add_log("%s attack %s and %s (attacker lost %d, defender lost %d)." % [p.name, players[prev].name, how, a_n, d_n])
			return res
		survivors = att_left
		add_log("%s %s %s%s (lost %d)." % [p.name, "drive off" if int(ar.fled) == tD else "defeat", players[prev].name, " and storm a castle" if B.castle else "", a_n])
	elif int(B.troops) > 0 or W > 0 or not home_guards(B).is_empty():
		var in_arena: bool = arena_rules() and (int(B.troops) > 0 or not home_guards(B).is_empty())
		var o: Dictionary = battle_options(from, to, lvl)
		o.wall = W
		if in_arena:
			o = arena_o(pid, lvl, prev, arena_map(B))
		var def_start: Dictionary = def_army(B)
		var b: Dictionary = CombatRules.fight(sel, def_start, o)
		var w_left: int = W if in_arena else int(ceil(float(b.wall_left) / CombatRules.WALL_PT - CombatRules.EPS))
		if W > 0 and not in_arena:
			set_wall(to, src, w_left)
		res.merge(b, true)
		res.kind = "battle"
		res.def_start = def_start
		res.wall_start = W
		res.wall_lost = W - w_left
		lose_units(to, real_losses(B, b.def_lost))
		var a_lost: int = CombatRules.count(b.att_lost)
		var d_lost: int = CombatRules.count(b.def_lost)
		if not bool(b.won):
			if CombatRules.count(b.att_left) > 0:
				_add_army(from, b.att_left, false)   # survivors of a stalled attack fall back
			add_log("%s attack %s and are pushed back (attacker lost %d, defender lost %d)." % [p.name, players[prev].name, a_lost, d_lost])
			return res
		survivors = b.att_left
		add_log("%s win the fight%s (lost %d)." % [p.name, " and storm a castle" if B.castle else "", a_lost])
	else:
		res.kind = "claim" if prev == -1 else "capture"
	# The hex changes hands.
	if prev >= 0:   # captured from an enemy (Fresh Ground, Border Market)
		B.cap_t = turn
		B.cap_by = pid
	B.owner = pid
	B.army = {}
	B.ready = {}
	_add_army(to, survivors, false)
	B.braced = -1
	B.tree = 0   # a Life Tree is destroyed and a dome falls when the hex is captured
	B.root = 0
	B.dome = 0
	if int(B.treb) == 1:
		B.treb = 0
		B.treb_due = 0
		add_log("A trebuchet under construction is wrecked.")
	if int(B.treb2) == 1:
		B.treb2 = 0
		B.treb2_due = 0
		add_log("A trebuchet under construction is wrecked.")
	if int(B.treb) == 0 and int(B.treb2) > 0:
		B.treb = B.treb2
		B.treb_due = B.treb2_due
		B.treb2 = 0
		B.treb2_due = 0
	if is_robots(pid) and not B.castle and building_count(B) > 0:   # the Robots: what stood there becomes one factory, or a resource hex
		var bkx: bool = int(B.barracks) > 0 or int(B.fort) > 0
		var ftx: bool = int(B.fort) > 0 and int(B.barracks) > 0
		B.market = 1 if bkx else clampi(int(B.market), 1, robo_markets())
		B.barracks = 1 if bkx else 0
		B.fort = 1 if ftx else 0
		B.wh = 0
		if not bkx:
			B.bk = 0
		add_log("%s turn the captured buildings into a factory." % p.name)
	if is_dinos(pid) and (int(B.treb) > 0 or int(B.treb2) > 0):
		B.treb = 0
		B.treb_due = 0
		B.treb2 = 0
		B.treb2_due = 0
		add_log("The Dinosaurs wreck the trebuchets they captured.")
	if B.get("crate", false):   # a material hex (2026-11-17)
		B.crate = false
		if not is_myth(pid):
			var mb: int = int(GameData.rules.crate.materials)
			p.mat = mat_of(pid) + mb
			res["crate"] = mb
			add_log("%s take a materials cache: +%d materials." % [p.name, mb])
	if B.bounty:
		B.bounty = false
		if not is_myth(pid):   # the Mythical only use magic
			var coin: int = int(GameData.rules.robots.scavenger_gold) if dk(pid, "cons", "move") >= 1 else int(GameData.rules.coin.gold)   # Scavenger
			p.gold = int(p.gold) + coin
			res.coin = coin
			add_log("%s take a bonus coin: +%d gold%s." % [p.name, coin, " (Scavenger)" if coin > int(GameData.rules.coin.gold) else ""])
	if B.castle:
		if prev == -1:
			add_log("%s claim a neutral castle." % p.name)
		elif to == homes[prev]:
			if players.size() > 2:   # 3 players: it knocks them out
				add_log("%s capture %s home castle!" % [p.name, "your" if prev == 0 else "the %s'" % players[prev].name])
				res.knockout = prev
				knock_out(prev, pid, "home")
				if over >= 0:
					return res
			else:
				add_log("%s capture the enemy home castle!" % p.name)
				_end_game(pid, "home")
				return res
		elif is_myth(pid):
			add_log("%s capture an enemy castle." % p.name)
		else:
			var plunder: int = int(GameData.rules.castles.plunder)
			p.gold = int(p.gold) + plunder
			add_log("%s capture an enemy castle (+%d gold plunder)." % [p.name, plunder])
	check_castles()
	return res


func _add_army(i: int, a: Dictionary, ready: bool) -> void:
	for k in a:
		add_units(i, k, int(a[k]), ready)


# =====================================================================
# Trebuchets. A finished one fires once per turn at an enemy hex next to it:
# 5 dice, every 4 or higher is a hit; a wall facing it takes the hits first, then 10 damage per hit.
# Ported from trebTargets, readyTrebs, fireTreb, aiTrebTarget, runVolley and shootVolley.
# =====================================================================

func treb_targets(i: int) -> Array[int]:
	var pid: int = int(tiles[i].owner)
	var out: Array[int] = []
	for j in HexGrid.neighbors(i):
		var b: Dictionary = tiles[j]
		if int(b.owner) >= 0 and int(b.owner) != pid and (int(b.troops) > 0 or wall_on(j, i) > 0):
			out.append(j)
	return out


## The trebuchets ready to fire this turn (a castle with 2 finished ones is listed twice).
func ready_trebs(pid: int) -> Array[int]:
	var out: Array[int] = []
	if is_myth(pid) or is_dinos(pid):
		return out
	for t in tiles:
		if int(t.owner) != pid or treb_targets(int(t.id)).is_empty():
			continue
		if int(t.treb) == 2:
			out.append(int(t.id))
		if int(t.treb2) == 2:
			out.append(int(t.id))
	return out


func fire_treb(i: int, j: int, nm: String = "") -> Dictionary:
	var tr: Dictionary = GameData.rules.trebuchet
	var b: Dictionary = tiles[j]
	var pid: int = int(tiles[i].owner)
	var dice: Array[int] = []
	var hits: int = 0
	for d in int(tr.dice):
		var v: int = randi_range(1, 6)
		dice.append(v)
		if v >= int(tr.hit_on):
			hits += 1
	var w: int = wall_on(j, i)
	var wall_hits: int = mini(w, hits)
	if wall_hits > 0:
		set_wall(j, i, w - wall_hits)
	# The rest of the hits: 10 damage each, front of the line first.
	var dmg: float = float(hits - wall_hits) * float(tr.damage_per_hit)
	var ks: Array = b.army.keys()
	ks.sort_custom(func(x, y): return int(GameData.units[x].rank) < int(GameData.units[y].rank))
	var lost: Dictionary = {}
	for k in ks:
		if dmg <= 0.0:
			break
		var hp: float = float(GameData.units[k].hp)
		var n: int = int(b.army[k])
		var killed: int = mini(n, int(floor(dmg / hp + CombatRules.EPS)))
		var used: float = minf(dmg, n * hp)
		# Damage that doesn't finish a unit is lost, as in the browser version's whole-unit losses.
		if killed > 0:
			lost[k] = killed
		dmg -= used
	lose_units(j, lost)
	var killed_total: int = CombatRules.count(lost)
	var what: String = nm if nm != "" else "trebuchet"
	if hits > 0:
		add_log("%s %s hits: %d units killed%s." % [players[pid].name, what, killed_total, (", a wall loses %d" % wall_hits) if wall_hits > 0 else ""])
	else:
		add_log("%s %s misses." % [players[pid].name, what])
	if not quiet and treb_fx.size() < 24 and nm == "":
		treb_fx.append({"from": i, "to": j, "pid": pid})
	return {"from": i, "to": j, "dice": dice, "hits": hits, "wall_lost": wall_hits, "killed": killed_total, "lost": lost}


func _army_gold(a: Dictionary) -> int:
	var g: int = 0
	for k in a:
		g += int(a[k]) * int(GameData.units[k].cost)
	return g


func ai_treb_target(i: int) -> int:
	var best: int = -1
	var best_value: float = -INF
	for j in treb_targets(i):
		var b: Dictionary = tiles[j]
		var value: float = minf(_army_gold(b.army) / 3.0, 5.0) * (1.5 if b.castle else 1.0) - 0.7 * wall_on(j, i) + (2.0 if is_home_castle(b) else 0.0)
		if value > best_value:
			best_value = value
			best = j
	return best


## Fires your trebuchets that have only one target. One with several targets waits for shoot_volley.
func run_volley() -> void:
	while not volley.is_empty():
		var h: int = volley[0]
		var targets: Array[int] = shot_targets(h)
		if targets.size() > 1:
			return
		volley.pop_front()
		if targets.size() == 1:
			shot_fire(h, targets[0])


## Aims the next waiting trebuchet (hex h) at hex j.
func shoot_volley(h: int, j: int) -> bool:
	if volley.is_empty() or volley[0] != h or not shot_targets(h).has(j):
		return false
	volley.pop_front()
	shot_fire(h, j)
	run_volley()
	return true


# =====================================================================
# The Dinosaurs (Ethan, 2026-11-09): no forts or trebuchets. Instead they hire Alamosaurus guards for their barracks
# and wake the volcano in their home castle. Ported from the browser's dev/dino-board/patch4_guard.py and patch5_volcano.py.
# =====================================================================

## Alamosaurus guards on a hex: units that are never ready, so they never move or attack; they fight whenever
## the hex is attacked, can hold it alone, and a dead (or fled) one is gone until it's hired again.
func guards_at(t: Dictionary) -> int:
	return int(t.army.get("alamo", 0))


func guard_cost(pid: int = -1) -> int:
	if pid < 0:
		pid = current
	return int(GameData.rules.dinos.guard_cost) - (3 if dk(pid, "hunt", "advance") >= 2 else 0)   # Cheap Guards (The Hunt)


func _guard_cost_base() -> int:
	return int(GameData.rules.dinos.guard_cost)


func guard_max(t: Dictionary) -> int:
	return int(GameData.rules.dinos.guard_max) * int(t.barracks)


## Advancements: hires an Alamosaurus to guard the barracks on hex i (25 gold, up to 2 per barracks).
func buy_guard(i: int) -> bool:
	var t: Dictionary = tiles[i]
	var p: Dictionary = players[current]
	if cur_action() != "advance" or int(t.owner) != current or not is_dinos(current) or int(t.barracks) == 0:
		return false
	if guards_at(t) >= guard_max(t) or int(p.gold) < guard_cost():
		return false
	p.gold = int(p.gold) - guard_cost()
	add_units(i, "alamo", 1, false)
	add_log("%s station an Alamosaurus to guard a barracks (%d there now)." % [p.name, guards_at(t)])
	return true


## The volcano, levels 1 to 3: {cost, reach (99 = the whole map), every (turns), dice}.
func volc_levels() -> Array:
	return GameData.rules.dinos.volcano


func volc_lv(pid: int) -> int:
	return int(players[pid].get("volc", {}).get("lv", 0))


func volc_say(l: int) -> String:
	var v: Dictionary = volc_levels()[l - 1]
	var reach: String = "the whole map" if int(v.reach) >= 99 else "%d hexes" % int(v.reach)
	var every: String = "every turn" if int(v.every) == 1 else "every %d turns" % int(v.every)
	return "reaches %s, erupts %s, %d dice" % [reach, every, int(v.dice)]


## Advancements at the home castle: wakes the volcano (level 1) or stokes it a level higher.
func do_volcano(pid: int) -> bool:
	var p: Dictionary = players[pid]
	var lv: int = volc_lv(pid)
	var h: int = homes[pid]
	if cur_action() != "advance" or pid != current or not is_dinos(pid) or lv >= 3 or int(tiles[h].owner) != pid:
		return false
	var cost: int = int(volc_levels()[lv].cost)
	if int(p.gold) < cost:
		return false
	p.gold = int(p.gold) - cost
	var cd: int = mini(int(p.volc.cd), int(volc_levels()[lv].every)) if lv > 0 else 0
	p.volc = {"lv": lv + 1, "cd": cd}
	add_log("%s %s the volcano at %s home castle: level %d, %s." % [p.name, "stoke" if lv > 0 else "awaken", "your" if pid == 0 else "their", lv + 1, volc_say(lv + 1)])
	return true


func is_volc_hex(i: int) -> bool:
	var o: int = int(tiles[i].owner)
	return o >= 0 and is_dinos(o) and homes[o] == i and volc_lv(o) > 0


## Enemy hexes with units the volcano on hex i can reach.
func volc_targets(i: int) -> Array[int]:
	var out: Array[int] = []
	var pid: int = int(tiles[i].owner)
	if pid < 0 or volc_lv(pid) == 0:
		return out
	var reach: int = int(volc_levels()[volc_lv(pid) - 1].reach)
	for b in tiles:
		if int(b.owner) >= 0 and int(b.owner) != pid and int(b.troops) > 0 and HexGrid.distance(i, int(b.id)) <= reach:
			out.append(int(b.id))
	return out


func shot_targets(i: int) -> Array[int]:
	return volc_targets(i) if is_volc_hex(i) else treb_targets(i)


func shot_fire(i: int, j: int) -> Dictionary:
	return fire_volcano(i, j) if is_volc_hex(i) else fire_treb(i, j)


## At the start of the Dinosaurs' turn: counts the volcano down; returns the home hex if it erupts now (and has a target).
func volc_ready(pid: int) -> int:
	if volc_lv(pid) == 0:
		return -1
	var p: Dictionary = players[pid]
	var h: int = homes[pid]
	if int(tiles[h].owner) != pid:
		p.volc = {}
		add_log("%s lost their home castle, and its volcano with it." % p.name)
		return -1
	if int(p.volc.cd) > 0:
		p.volc.cd = int(p.volc.cd) - 1
	return h if int(p.volc.cd) <= 0 and not volc_targets(h).is_empty() else -1


## Lava rains on hex j: every die of 4 or more is a hit of 10 damage, front of the line first. Walls don't stop it.
func fire_volcano(i: int, j: int) -> Dictionary:
	var tr: Dictionary = GameData.rules.trebuchet
	var b: Dictionary = tiles[j]
	var pid: int = int(tiles[i].owner)
	var p: Dictionary = players[pid]
	var v: Dictionary = volc_levels()[volc_lv(pid) - 1]
	var dice: Array[int] = []
	var hits: int = 0
	for d in int(v.dice):
		var r: int = randi_range(1, 6)
		dice.append(r)
		if r >= int(tr.hit_on):
			hits += 1
	var dmg: float = float(hits) * float(tr.damage_per_hit)
	var ks: Array = b.army.keys()
	ks.sort_custom(func(x, y): return int(GameData.units[x].rank) < int(GameData.units[y].rank))
	var lost: Dictionary = {}
	for k in ks:
		if dmg <= 0.0:
			break
		var hp: float = float(GameData.units[k].hp)
		var n: int = int(b.army[k])
		var killed: int = mini(n, int(floor(dmg / hp + CombatRules.EPS)))
		if killed > 0:
			lost[k] = killed
		dmg -= minf(dmg, n * hp)
	lose_units(j, lost)
	var killed_total: int = CombatRules.count(lost)
	p.volc.cd = int(v.every)
	var who: String = "Your" if pid == 0 else "The %s'" % p.name
	if hits > 0:
		add_log("%s volcano erupts: %d unit%s killed." % [who, killed_total, "" if killed_total == 1 else "s"])
	else:
		add_log("%s volcano erupts: every lava bomb misses." % who)
	if not quiet:
		volc_fx.append({"from": i, "to": j, "dice": dice})
	return {"from": i, "to": j, "dice": dice, "hits": hits, "wall_lost": 0, "killed": killed_total, "lost": lost, "volc": true}


## The computer's aim: the biggest army in reach, castles and the home castle first.
func ai_volc_target(pid: int) -> int:
	var h: int = homes[pid]
	var best: int = -1
	var best_value: float = -INF
	for j in volc_targets(h):
		var b: Dictionary = tiles[j]
		var value: float = minf(_army_gold(b.army) / 3.0, 8.0) * (1.5 if b.castle else 1.0) + (3.0 if is_home_castle(b) else 0.0) - 0.05 * HexGrid.distance(h, j)
		if value > best_value:
			best_value = value
			best = j
	return best


## Sets the computer's difficulty for player pid.
func set_level(pid: int, level: String) -> void:
	if not AI_LEVEL_NAME.has(level):
		level = "medium"
	players[pid]["diff"] = level
	players[pid]["gold_bonus"] = float(AI_GOLD.get(level, 0.0))


## How much of its gold a player collects: Expert's computer gets 40% more.
func gold_mult(pid: int) -> float:
	var p: Dictionary = players[pid]
	return 1.0 + float(p.get("gold_bonus", 0.0)) if bool(p.ai) else 1.0


## True when attacks on units are fought in the Arena (a person is playing), so the board's walls,
## defense bonuses and attack advantage don't count: only the Robots' Offline and Update (and the Dinosaurs' Herd).
## A battle goes to the Arena when a person fights in it; computer-vs-computer battles are settled on the board.
func needs_arena(att: int, def: int) -> bool:
	if def < 0 or def >= players.size():
		return true
	return not (bool(players[att].ai) and bool(players[def].ai))


func arena_rules() -> bool:
	if sim_arena or arena_fights:
		return true
	for p in players:
		if not bool(p.ai):
			return true
	return false


## The battle options for an Arena fight, for the computer's estimates (att -1: no attacker abilities).
func arena_o(att: int, lvl: int, defender: int, map: String) -> Dictionary:
	var o: Dictionary = {"map": map, "arena": true, "surprise": false, "a_plus": 0, "a_bonus": 0}
	if att >= 0:
		var a: Dictionary = atk_opts(att, lvl, raw_lvl() if (not play.is_empty() and current == att) else 0, defender)
		o.surprise = bool(a.surprise)
		o.a_plus = int(a.a_plus)
		o.a_bonus = int(a.a_bonus)
	return o


## Everything that makes up a game, as plain data: Undo puts it back, and saving writes it to disk.
const SAVED := ["map_id", "players", "tiles", "homes", "current", "first", "turn", "play", "siege", "over", "over_why",
	"extra_castle", "log_lines", "arena_fights", "volley"]

func snapshot() -> Dictionary:
	var d: Dictionary = {}
	for k in SAVED:
		var v = get(k)
		d[k] = v.duplicate(true) if (v is Array or v is Dictionary) else v
	return d


## A game read back from a save file: JSON turns every number into a decimal, so whole ones go back to whole numbers.
static func ints(v):
	if v is float and v == floorf(v) and absf(v) < 1e15:
		return int(v)
	if v is Array:
		var a: Array = []
		for x in v:
			a.append(ints(x))
		return a
	if v is Dictionary:
		var d: Dictionary = {}
		for k in v:
			d[k] = ints(v[k])
		return d
	return v


func restore(d: Dictionary) -> void:
	if d.has("players"):
		HexGrid.use_board(d.players.size())
	if d.has("tiles"):
		for t in d.tiles:
			if not t.has("wh"):
				t["wh"] = 0
			for key in ["new_t", "cap_t", "cap_by"]:
				if not t.has(key):
					t[key] = -1
			t["fern"] = false   # ferns taken off the map (Ethan, 2026-11-17): a game saved with ferns loses them
	for k in SAVED:
		if not d.has(k):
			continue
		var v = d[k]
		if k == "homes" or k == "volley":
			var a: Array[int] = []
			for x in v:
				a.append(int(x))
			set(k, a)
		elif k == "log_lines":
			var l: Array[String] = []
			for x in v:
				l.append(String(x))
			set(k, l)
		elif k in ["current", "first", "turn", "over", "extra_castle"]:
			set(k, int(v))
		else:
			set(k, v.duplicate(true) if (v is Array or v is Dictionary) else v)
	HexGrid.use_board(players.size())
	if map_id != "":   # a game on a hand-made map keeps its shape
		var voids: Array = []
		for t in tiles:
			if t.terrain == "void":
				voids.append(int(t.id))
		HexGrid.use_shape(players.size(), int(round(sqrt(tiles.size()))), voids)
	for p in players:
		if not p.has("out"):
			p["out"] = false
		for key in ["mat", "tr", "fnest", "ffort"]:
			if not p.has(key):
				p[key] = 0
		if not p.has("armor"):
			p["armor"] = false
	if not tiles.is_empty() and not tiles.any(func(t): return t.has("crate")):   # a game saved before material hexes
		for t in tiles:
			t["crate"] = false
		BoardGen.place_crates(tiles, homes, int(HexGrid.board_rules(players.size()).get("crates", 0)))
	if not play.is_empty() and card_action() == "fortify" and not fx_on():
		play.fx = {"ph": "pick", "n": 1, "done": [], "cur": "", "far": 0, "mv": false, "rally": 0}   # a game saved before Fortify became a wild card


## A full copy of the game, so the computer can try a card out without changing the real game.
func clone():
	var c = get_script().new()
	c.players = players.duplicate(true)
	c.tiles = tiles.duplicate(true)
	c.homes = homes.duplicate()
	c.map_id = map_id
	c.current = current
	c.first = first
	c.turn = turn
	c.play = play.duplicate(true)
	c.siege = siege.duplicate(true)
	c.over = over
	c.over_why = over_why
	c.extra_castle = extra_castle
	c.quiet = true
	return c


func _minus(a: Dictionary, bs: Array) -> Dictionary:
	var out: Dictionary = {}
	for k in a:
		var d: int = int(a[k])
		for b in bs:
			d -= int(b.get(k, 0))
		if d > 0:
			out[k] = d
	return out


func _clip(a: Dictionary, most: Dictionary) -> Dictionary:
	var out: Dictionary = {}
	for k in a:
		var m: int = mini(int(a[k]), int(most.get(k, 0)))
		if m > 0:
			out[k] = m
	return out


# =====================================================================
# The Mythical (Ethan's rules, 2026-11-07). They earn and spend only magic (kept in the player's gold field and shown as
# magic). Magic comes from Life Trees and the Floating Castle (their home castle). Mages are moving barracks: on the hex they
# stand on they turn Minions into bigger units, plant Life Trees and raise magic domes. Mages and Minions are made at castles.
# Captured enemy buildings do nothing for them. Ported from the browser's MYTH rules.
# =====================================================================

const MAGES := ["mage0", "mage1", "mage2", "mage3"]   # a Mage keeps the level it was made at


func myth() -> Dictionary:
	return GameData.rules.mythical


func is_myth(pid: int) -> bool:
	return pid >= 0 and pid < players.size() and String(players[pid].faction) == "mythical"


## "magic" for the Mythical, "gold" for everyone else.
func cur_word(pid: int) -> String:
	return "magic" if is_myth(pid) else "gold"


func is_mage(k: String) -> bool:
	return MAGES.has(k)


func mlv_of(pid: int) -> int:
	return int(players[pid].get("mlv", 0))


func clv_of(pid: int) -> int:
	return int(players[pid].get("clv", 0))


func mages_on(t: Dictionary) -> int:
	var n: int = 0
	for k in MAGES:
		n += int(t.army.get(k, 0))
	return n


## Mages on one hex at a time: 2 (3 once Mages reach level 3).
func mage_cap(pid: int) -> int:
	return 3 if mlv_of(pid) >= 3 else 2


## The best Mage on the hex, or -1.
func mage_lv_at(t: Dictionary) -> int:
	for l in range(3, -1, -1):
		if int(t.army.get(MAGES[l], 0)) > 0:
			return l
	return -1


func mage_total(pid: int) -> int:
	var n: int = 0
	for t in tiles:
		if int(t.owner) == pid:
			n += mages_on(t)
	return n


## A new Mage: the base price, +1 for each Mage past the 5th, +1 for each level, and level 3 takes 1 off every unit.
func mage_price(pid: int) -> int:
	return int(myth().mage_base) + maxi(0, mage_total(pid) - 4) + mlv_of(pid) - (1 if mlv_of(pid) >= 3 else 0)


func conv_price(t: Dictionary, k: String) -> int:
	return int(myth().conv[k].m) - (1 if mage_lv_at(t) >= 3 else 0)


func myth_home(pid: int) -> Dictionary:
	var h: Dictionary = tiles[homes[pid]]
	return h if int(h.owner) == pid else {}


func is_floating(t: Dictionary) -> bool:
	return t.castle and int(t.owner) >= 0 and homes[int(t.owner)] == int(t.id) and is_myth(int(t.owner))


func tree_magic(t: Dictionary) -> int:
	return int(myth().tree_rich) if int(t.army.get("minion", 0)) >= int(myth().tree_minions) else int(myth().tree_magic)


## Mages and Minions move 2 hexes anywhere.
func fast_unit(k: String) -> bool:
	return k == "minion" or is_mage(k)


func myth_income(pid: int) -> Dictionary:
	var hexes: int = 0
	var castles: int = 0
	var trees: int = 0
	var tree_m: int = 0
	for t in tiles:
		if int(t.owner) != pid:
			continue
		hexes += 1
		if t.castle:
			castles += 1
		if int(t.tree) > 0:
			trees += 1
			tree_m += tree_magic(t)
	var home: int = int(myth().castle_magic[clv_of(pid)]) if not myth_home(pid).is_empty() else 0
	return {"hexes": hexes, "castles": castles, "markets": 0, "nest": 0, "trees": trees, "tree_m": tree_m, "home": home, "total": home + tree_m}


func _lock_mage(t: Dictionary) -> bool:
	for k in MAGES:
		if int(t.ready.get(k, 0)) > 0:
			t.ready[k] = int(t.ready[k]) - 1
			sync_tile(t)
			return true
	return false


## The start of a Mythical turn (after income): dome upkeep, the Floating Castle's Minions, Mages rooted to new trees.
func _myth_turn_start(p: Dictionary) -> void:
	var pid: int = int(p.id)
	var domes: Array = tiles.filter(func(t): return int(t.owner) == pid and int(t.dome) > 0)
	var kept: int = 0
	for t in domes:
		if int(p.gold) >= int(myth().dome_upkeep):
			p.gold = int(p.gold) - int(myth().dome_upkeep)
			kept += 1
		else:
			t.dome = 0
	if not domes.is_empty():
		if kept == domes.size():
			add_log("%s pay %d magic to keep %s up." % [p.name, kept, "a dome" if kept == 1 else "%d domes" % kept])
		else:
			add_log("%s can't pay for every dome: %d fade away." % [p.name, domes.size() - kept])
	var h: Dictionary = myth_home(pid)
	if not h.is_empty():
		var n: int = int(myth().minions[clv_of(pid)])
		add_units(int(h.id), "minion", n, true)
		add_log("The Floating Castle makes %d Minions." % n)
	for t in tiles:
		if int(t.owner) == pid and int(t.root) > 0:
			_lock_mage(t)
			t.root = int(t.root) - 1


func _myth_setup(i: int) -> void:
	var p: Dictionary = players[i]
	p.gold = int(myth().start_magic) + catch_up(i, int(myth().second_magic), players.size())
	p.mlv = 0
	p.clv = 0
	add_units(homes[i], "mage0", 1, true)
	add_units(homes[i], "minion", 4, true)


## The special card: no actions, but every Mage makes 2 magic and every castle 5.
func myth_channel(pid: int) -> int:
	var p: Dictionary = players[pid]
	var mg: int = mage_total(pid)
	var cs: int = castle_count(pid)
	var g: int = mg * int(myth().ch_mage) + cs * int(myth().ch_castle)
	p.gold = int(p.gold) + g
	add_log("%s channel magic: +%d (%d Mage%s, %d castle%s)." % [p.name, g, mg, "" if mg == 1 else "s", cs, "" if cs == 1 else "s"])
	return g


func myth_buy_minions(pid: int, i: int, packs: int) -> bool:
	var t: Dictionary = tiles[i]
	var p: Dictionary = players[pid]
	packs = mini(packs, int(p.gold))
	if int(t.owner) != pid or not t.castle or packs < 1:
		return false
	p.gold = int(p.gold) - packs
	add_units(i, "minion", packs * int(myth().minion_pack), true)
	add_log("%s make %d Minions." % [p.name, packs * int(myth().minion_pack)])
	return true


func myth_buy_mage(pid: int, i: int) -> bool:
	var t: Dictionary = tiles[i]
	var p: Dictionary = players[pid]
	var c: int = mage_price(pid)
	if int(t.owner) != pid or not t.castle or mages_on(t) >= mage_cap(pid) or int(p.gold) < c:
		return false
	p.gold = int(p.gold) - c
	add_units(i, MAGES[mlv_of(pid)], 1, true)
	add_log("%s make a level %d Mage." % [p.name, mlv_of(pid)])
	return true


func myth_convert(pid: int, i: int, k: String) -> bool:
	var t: Dictionary = tiles[i]
	var p: Dictionary = players[pid]
	if not myth().conv.has(k):
		return false
	var C: Dictionary = myth().conv[k]
	if int(t.owner) != pid or mage_lv_at(t) < int(C.lv) or int(t.army.get("minion", 0)) < int(C.min):
		return false
	var c: int = conv_price(t, k)
	if int(p.gold) < c:
		return false
	p.gold = int(p.gold) - c
	take_units(i, {"minion": int(C.min)})
	add_units(i, k, 1, true)
	add_log("%s Mage turns %s into a %s." % ["Your" if pid == 0 else "The %s'" % p.name, "a Minion" if int(C.min) == 1 else "%d Minions" % int(C.min), String(GameData.units[k].name)])
	return true


func myth_plant(pid: int, i: int) -> bool:
	var t: Dictionary = tiles[i]
	if int(t.owner) != pid or int(t.tree) > 0 or t.castle or t.terrain != "plain" or mages_on(t) <= 0:
		return false
	t.tree = 1
	t.root = int(myth().tree_turns)
	var ready_mages: int = 0
	for k in MAGES:
		ready_mages += int(t.ready.get(k, 0))
	if ready_mages >= mages_on(t):
		_lock_mage(t)   # a Mage that already moved this turn is the one that stays
	add_log("%s Mage plants a Life Tree and stays with it for %d turns." % ["Your" if pid == 0 else "The %s'" % players[pid].name, int(myth().tree_turns)])
	return true


func myth_dome(pid: int, i: int) -> bool:
	var t: Dictionary = tiles[i]
	var p: Dictionary = players[pid]
	if int(t.owner) != pid or int(t.dome) > 0 or mages_on(t) == 0 or t.terrain == "water" or int(p.gold) < int(myth().dome_cost):
		return false
	p.gold = int(p.gold) - int(myth().dome_cost)
	t.dome = int(GameData.rules.walls.hp)
	add_log("%s Mage raises a magic dome." % ("Your" if pid == 0 else "The %s'" % p.name))
	return true


func trees_of(pid: int) -> int:
	var n: int = 0
	for t in tiles:
		if int(t.owner) == pid and int(t.get("tree", 0)) > 0:
			n += 1
	return n


## Castles held other than your own home castle.
func cap_castles_of(pid: int) -> int:
	var n: int = 0
	for t in tiles:
		if t.castle and int(t.owner) == pid and int(t.id) != homes[pid]:
			n += 1
	return n


## Mage level l+1 also needs Life Trees and captured castles (Ethan, 2026-11-11).
func mage_req_ok(pid: int, l: int) -> bool:
	if l >= 3:
		return false
	var q: Dictionary = myth().mage_req[l]
	return trees_of(pid) >= int(q.trees) and cap_castles_of(pid) >= int(q.castles)


func mage_req_txt(l: int) -> String:
	var q: Dictionary = myth().mage_req[l]
	var t: String = "%d Life Tree%s" % [int(q.trees), "s" if int(q.trees) > 1 else ""]
	if int(q.castles) > 0:
		t += " and %d captured castle%s" % [int(q.castles), "s" if int(q.castles) > 1 else ""]
	return t


func mage_req_all() -> String:
	var parts: PackedStringArray = []
	for l in 3:
		parts.append("level %d: %s" % [l + 1, mage_req_txt(l)])
	return "; ".join(parts)


func myth_up_mages(pid: int) -> bool:
	var p: Dictionary = players[pid]
	var l: int = mlv_of(pid)
	if l >= 3 or myth_home(pid).is_empty() or int(p.gold) < int(myth().mage_up[l]) or not mage_req_ok(pid, l):
		return false
	p.gold = int(p.gold) - int(myth().mage_up[l])
	p.mlv = l + 1
	add_log("%s raise their Mages to level %d: new Mages come out at that level." % [p.name, l + 1])
	return true


func myth_up_castle(pid: int) -> bool:
	var p: Dictionary = players[pid]
	var l: int = clv_of(pid)
	if l >= 3 or myth_home(pid).is_empty() or int(p.gold) < int(myth().castle_up[l]):
		return false
	p.gold = int(p.gold) - int(myth().castle_up[l])
	p.clv = l + 1
	add_log("%s raise the Floating Castle to level %d: %d magic and %d Minions a turn." % [p.name, l + 1, int(myth().castle_magic[l + 1]), int(myth().minions[l + 1])])
	return true


## Which units can make this move: only flyers can attack the Floating Castle; only Mages and Minions reach 2 hexes away into
## new land or an attack. An invalid Callable means everyone can.
func move_filter(from: int, to: int, lvl: int) -> Callable:
	var A: Dictionary = tiles[from]
	var B: Dictionary = tiles[to]
	var pid: int = int(A.owner)
	if pid >= 0 and is_robots(pid):
		var rf: Callable = _robo_move_filter(from, to, lvl)
		if rf.is_valid():
			return rf
	var air: bool = int(B.owner) >= 0 and int(B.owner) != pid and is_floating(B)
	var far: bool = is_myth(pid) and not _move_targets_core(from, lvl, false).has(to)
	if air and far:
		return func(_k): return false
	if air:
		return func(k): return bool(GameData.units[k].get("air", false))
	if far:
		return func(k): return fast_unit(k)
	return Callable()


func move_filter_note(from: int, to: int) -> String:
	var B: Dictionary = tiles[to]
	if is_robots(int(tiles[from].owner)) and not _move_targets_core(from, cur_lvl(), false).has(to):
		for x in robo_move_extra(from, cur_lvl()):
			if x["hexes"].has(to):
				return String(x["why"])
	if int(B.owner) >= 0 and int(B.owner) != int(tiles[from].owner) and is_floating(B):
		return "The Floating Castle can only be attacked by flyers."
	return "Only Mages and Minions can go this far in one move."


## The units that can actually make a move: the filter above, and at most 2 Mages on a hex (3 at level 3).
func _move_sel(from: int, to: int, sel: Dictionary, lvl: int) -> Dictionary:
	var out: Dictionary = sel.duplicate()
	var f: Callable = move_filter(from, to, lvl)
	if f.is_valid():
		for k in out.keys():
			if not f.call(k):
				out.erase(k)
	var A: Dictionary = tiles[from]
	var B: Dictionary = tiles[to]
	if is_myth(int(A.owner)):
		var room: int = mage_cap(int(A.owner)) - (mages_on(B) if int(B.owner) == int(A.owner) else 0)
		var n: int = 0
		for l in range(3, -1, -1):
			var k: String = MAGES[l]
			if out.has(k):
				var m: int = maxi(0, mini(int(out[k]), room - n))
				n += m
				if m > 0:
					out[k] = m
				else:
					out.erase(k)
	return out

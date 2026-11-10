# Godot port of the browser's Dinosaur rework (2026-11-09), rules: no forts or trebuchets for the Dinosaurs,
# Alamosaurus guards, the volcano strike, the Triceratops' immunity to shots, and the computer player.
import sys; sys.path.insert(0,sys.path[0])
from common import F
P=sys.argv[1].rstrip('/')+'/scripts/'
g=F(P+'rules/game_state.gd')
g.rep('''var volley: Array[int] = []        # your finished trebuchets still waiting to be aimed this turn''',
'''var volley: Array[int] = []        # your finished trebuchets (and the Dinosaurs' volcano) still waiting to be aimed this turn
var volc_fx: Array = []            # volcano eruptions for the board to animate: {from, to, dice} (not saved)''')
g.rep('''            "mlv": 0,   # Mythical: Mage level and Floating Castle level
            "clv": 0,''','''            "mlv": 0,   # Mythical: Mage level and Floating Castle level
            "clv": 0,
            "volc": {},   # Dinosaurs: the home castle's volcano, {lv, cd} once woken''')
# guards never move
g.rep('''            t.ready = t.army.duplicate()
            sync_tile(t)
            if int(t.braced) == current:''','''            t.ready = t.army.duplicate()
            t.ready.erase("alamo")   # Alamosaurus guards never move
            sync_tile(t)
            if int(t.braced) == current:''')
g.rep('''    else:
        run_volley()


## Plays a card''','''    else:
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


## Plays a card''')
# Populate: barracks only (the Dinosaurs have no forts)
g.rep('''        var k: int = int(t.fort) + int(t.barracks)
        if k > 0:
            add_units(int(t.id), "galli", k, true)
            n += k
    if n > 0:
        add_log("%s populate: %d free Gallimimus at their forts and barracks." % [players[pid].name, n])''',
'''        var k: int = int(t.barracks)   # the Dinosaurs have no forts
        if k > 0:
            add_units(int(t.id), "galli", k, true)
            n += k
    if n > 0:
        add_log("%s populate: %d free %s at their barracks." % [players[pid].name, n, GameData.units.galli.name])''')
g.rep('''    if t.castle and kind != "market" and kind != "wh":
        return false
    p.gold = int(p.gold) - price''','''    if t.castle and kind != "market" and kind != "wh":
        return false
    if kind == "fort" and is_dinos(current):
        return false   # the Dinosaurs build no forts
    p.gold = int(p.gold) - price''')
g.rep('''    elif int(t.owner) >= 0 and not is_myth(int(t.owner)):   # captured forts do nothing for the Mythical''',
      '''    elif int(t.owner) >= 0 and not is_myth(int(t.owner)) and not is_dinos(int(t.owner)):   # captured forts do nothing for the Mythical or the Dinosaurs''')
g.rep('''func can_treb_at(t: Dictionary) -> bool:
    if t.castle:''','''func can_treb_at(t: Dictionary) -> bool:
    if int(t.owner) >= 0 and is_dinos(int(t.owner)):
        return false   # the Dinosaurs have the volcano instead
    if t.castle:''')
g.rep('''    var out: Array[int] = []
    if is_myth(pid):
        return out
    for t in tiles:
        if int(t.owner) != pid or treb_targets(int(t.id)).is_empty():''','''    var out: Array[int] = []
    if is_myth(pid) or is_dinos(pid):
        return out
    for t in tiles:
        if int(t.owner) != pid or treb_targets(int(t.id)).is_empty():''')
g.rep('''        var fled: Dictionary = _clip(def_esc, gone)
        var dead_units: Dictionary = _minus(gone, [fled])''','''        var fled: Dictionary = _clip(def_esc, gone)
        fled.erase("alamo")   # an Alamosaurus guard never leaves its barracks: if it runs, it's lost
        var dead_units: Dictionary = _minus(gone, [fled])''')
g.rep('''    if int(B.treb) == 0 and int(B.treb2) > 0:
        B.treb = B.treb2
        B.treb_due = B.treb2_due
        B.treb2 = 0
        B.treb2_due = 0''','''    if int(B.treb) == 0 and int(B.treb2) > 0:
        B.treb = B.treb2
        B.treb_due = B.treb2_due
        B.treb2 = 0
        B.treb2_due = 0
    if is_dinos(pid) and (int(B.treb) > 0 or int(B.treb2) > 0):
        B.treb = 0
        B.treb_due = 0
        B.treb2 = 0
        B.treb2_due = 0
        add_log("The Dinosaurs wreck the trebuchets they captured.")''')
# the volley: trebuchets and the volcano share it
g.rep('''        var h: int = volley[0]
        var targets: Array[int] = treb_targets(h)
        if targets.size() > 1:
            return
        volley.pop_front()
        if targets.size() == 1:
            fire_treb(h, targets[0])''','''        var h: int = volley[0]
        var targets: Array[int] = shot_targets(h)
        if targets.size() > 1:
            return
        volley.pop_front()
        if targets.size() == 1:
            shot_fire(h, targets[0])''')
g.rep('''    if volley.is_empty() or volley[0] != h or not treb_targets(h).has(j):
        return false
    volley.pop_front()
    fire_treb(h, j)
    run_volley()
    return true''','''    if volley.is_empty() or volley[0] != h or not shot_targets(h).has(j):
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


func guard_cost() -> int:
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
        var value: float = minf(_army_gold(b.army) / 3.0, 8.0) * (1.5 if b.castle else 1.0) + (3.0 if homes.has(j) else 0.0) - 0.05 * HexGrid.distance(h, j)
        if value > best_value:
            best_value = value
            best = j
    return best''')
g.save()

c=F(P+'rules/combat.gd')
c.rep('''    var reduce: Dictionary = T.get("reduce", {})
    if reduce.has(w.hk):
        d = maxf(1.0, d - float(reduce[w.hk]))''','''    var reduce: Dictionary = T.get("reduce", {})
    if reduce.has(w.hk):
        d = maxf(1.0, d - float(reduce[w.hk]))
    if T.get("noProj", false) and (w.get("rng", false) or w.hk == "gunship" or w.hk == "magic") and w.hk != "beam":
        return 0.0   # Triceratops: shots and spells do nothing to it (the Laser Tank's beam does)''')
c.save()

a=F(P+'rules/ai_player.gd')
a.rep('''    if treb and ai_treb_site(g, pid) < 0 and int(g.players[pid].gold) >= cost_of("fort", lvl) + treb_cost():''',
      '''    if treb and not g.is_dinos(pid) and ai_treb_site(g, pid) < 0 and int(g.players[pid].gold) >= cost_of("fort", lvl) + treb_cost():''')
a.rep('''    if treb and ai_treb_site(g, pid) < 0 and gold >= cost_of("fort", lvl) + treb_cost():''',
      '''    if treb and not g.is_dinos(pid) and ai_treb_site(g, pid) < 0 and gold >= cost_of("fort", lvl) + treb_cost():''')
a.rep('''    if not bool(u.fort) and own.size() >= 6 and can.call("fort"):''','''    if not g.is_dinos(pid) and not bool(u.fort) and own.size() >= 6 and can.call("fort"):   # (the Dinosaurs build no forts)''')
a.rep('''    if gold >= cost_of("fort", lvl) + 12:''','''    if not g.is_dinos(pid) and gold >= cost_of("fort", lvl) + 12:''')
a.rep('''static func ai_advance(g, pid: int, lvl: int) -> Array:
    var p: Dictionary = g.players[pid]
    var ids: Array = []''','''static func ai_advance(g, pid: int, lvl: int) -> Array:
    var p: Dictionary = g.players[pid]
    var ids: Array = []
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
            while g.guards_at(gt) < g.guard_max(gt) and int(p.gold) >= g.guard_cost() + sp and g.buy_guard(int(gt.id)):
                ids.append(int(gt.id))''')
a.save()
print('p11 rules ok')

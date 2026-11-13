# The Robot rework for the Godot version, step 3: the computer (ai_player.gd), as in the browser's patch1-3:
# markets only on an empty hex or a resource hex (the safest one); its barracks and fort plans become factory upgrades,
# made in Advancements at the home castle; Overclock; Laser Strike at the start of its Move; Sortie after its Fortify
# picks; Assembly Line from Mobilize. The old Factory (5 Brawlers from an upgraded Advancements) is gone. It doesn't
# use the trades (Recompile, Rebuild, Refit), like the browser's.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import F
f = F(sys.argv[1] + '/scripts/rules/ai_player.gd')

f.rep('''    if a == "build" or a == "recruit":
        g.dino_action_start(pid)''', '''    if a == "build" or a == "recruit" or a == "advance":
        g.dino_action_start(pid)   # the Dinosaur and Robot cards' own upgrades that happen when the action starts''')
f.rep('''        if bi > s and not g.is_dinos(pid):''', '''        if bi > s and not g.card_ups(pid):''')
f.rep('''        if raw >= 1:
            if g.is_robots(pid):
                g._factory(pid)
            elif g.is_mammals(pid):''', '''        if raw >= 1:
            if g.is_mammals(pid):''')
f.rep('''    elif a == "move":
        g.play.moves = 0
        events.append_array(ai_moves(g, pid, lvl))''', '''    elif a == "move":
        g.play.moves = 0
        var lz: Array = ai_laser(g, pid)   # Laser Strike (Onslaught): the tanks fire first
        if not lz.is_empty():
            events.append({"kind": "flash", "ids": lz})
        events.append_array(ai_moves(g, pid, lvl))''')

# Sortie (Siege Protocol): a real Move after the Fortify's picks
f.rep('''        g.play.fx.done.append(k)
    g.play.fx = {}
    return events''', '''        g.play.fx.done.append(k)
    if bool(g.play.fx.get("mvx", false)) and g.over < 0:   # Sortie (Siege Protocol): a real Move after the picks
        g.play.fx.ph = "act"
        g.play.fx.cur = "move"
        g.play.moves = 0
        events.append({"kind": "step", "action": "move"})
        events.append_array(ai_moves(g, pid, 0))
    g.play.fx = {}
    return events''')

# Laser Strike
f.rep('''# =====================================================================
# Helpers
# =====================================================================''', '''## Laser Strike (Onslaught, Move level 2): every hex with ready Laser Tanks fires at the biggest enemy army next door.
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
# =====================================================================''')

# Build: Robot markets only
f.rep('''        var plan: Dictionary = build_plan2(g, pid, treb, lvl, keep_r) if sm else build_plan(g, pid, treb, lvl)
        if plan.is_empty():
            break''', '''        var plan: Dictionary = build_plan2(g, pid, treb, lvl, keep_r) if sm else build_plan(g, pid, treb, lvl)
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
                    break''')

# Recruit: Assembly Line (Mobilize); the hex made units this turn (Fresh Units)
f.rep('''    if g.is_robots(pid) and g.named_on() and int(got.get(basic, 0)) >= 2:''',
      '''    if g.dk(pid, "mobil", "recruit") >= 1 and int(got.get(basic, 0)) >= 2:''')
f.rep('''    g._add_army(sid, got, true)
    var parts: Array = []''', '''    g._add_army(sid, got, true)
    g.tiles[sid].new_t = g.turn
    var parts: Array = []''')

# Advancements: the factory upgrades at the home castle, then Overclock
f.rep('''    var p: Dictionary = g.players[pid]
    var ids: Array = []
    if g.is_dinos(pid):
        # the volcano first''', '''    var p: Dictionary = g.players[pid]
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
        # the volcano first''')
f.rep('''        while int(t.bk) < 3 and g.ai_mat(pid, g.bk_up_cost(pid, int(t.bk)), int(spare[int(t.bk)])):''',
      '''        while int(t.bk) < 3 and g.ai_mat(pid, g.bk_up_cost(pid, int(t.bk), t), int(spare[int(t.bk)])):''')
f.save(); print('p3 ai ok')

"""Ethan, 2026-11-24 (afternoon): no building walls (rules.json walls.on false: build_wall refuses, no Walls
buttons, the computer can't build them, Advancements texts drop them); the neutral castle is the old whole-hex tile
again (the keep picture isn't used); a castle battle is always on the Castle map (no ballistas). As the browser's
dev/castle-walls/patch_nowalls.py.
Usage: python3 p19_nowalls.py PROJ"""
import sys, json
sys.path.insert(0, __file__.rsplit('/', 2)[0] + '/godot-port-nov22')
from common import F
P = sys.argv[1]
rj = P + '/data/rules.json'; r = json.load(open(rj)); r['walls']['on'] = False
json.dump(r, open(rj, 'w'), indent='\t', ensure_ascii=False)
g = F(P + '/scripts/rules/game_state.gd')
g.rep('''func build_wall(i: int, j: int) -> bool:
    var t: Dictionary = tiles[i]''', '''## Walls can be built at all (rules.json walls.on; off since 2026-11-24).
static func walls_on() -> bool:
    return bool(GameData.rules.walls.get("on", true))


func build_wall(i: int, j: int) -> bool:
    if not walls_on():
        return false
    var t: Dictionary = tiles[i]''')
g.rep('''        return "castle" if w != 0 else "open"''', '''        return "castle"''')
g.save()
m = F(P + '/scripts/ui/main.gd')
m.rep('''        _bubble(post.call(5, 30), R, "res://art/buildings/wall.png", "Walls", w_note, can_w, wall_for == sel, can_w,''',
      '''        if GameState.walls_on(): _bubble(post.call(5, 30), R, "res://art/buildings/wall.png", "Walls", w_note, can_w, wall_for == sel, can_w,''')
m.rep('''    box.add_child(_build_button("res://art/buildings/wall.png", "Walls · %d gold each" % wc,''', '''    if GameState.walls_on(): box.add_child(_build_button("res://art/buildings/wall.png", "Walls · %d gold each" % wc,''')
m.rep(''', or build walls on a hex's sides (%d materials each)" % [''', '''%s" % [''')
m.rep('''int(D.volcano[2].cost), int(GameData.rules.walls.cost_by_level[lvl])]''', '''int(D.volcano[2].cost), (", or build walls on a hex's sides (%d materials each)" % int(GameData.rules.walls.cost_by_level[lvl])) if GameState.walls_on() else ""]''')
m.rep(''', or build walls on a hex's sides (%d each)" % [''', '''%s" % [''')
m.rep('''int(tr.castle_cost[1]), int(GameData.rules.walls.cost_by_level[lvl])]''', '''int(tr.castle_cost[1]), (", or build walls on a hex's sides (%d each)" % int(GameData.rules.walls.cost_by_level[lvl])) if GameState.walls_on() else ""]''')
m.rep('''wake or stoke its volcano, or build walls." if g.is_dinos(0)''', '''wake or stoke its volcano." if g.is_dinos(0)''')
m.rep('''upgrade a barracks, start a trebuchet or build walls." if g.is_robots(0) else "▸ Tap one of your hexes to upgrade a barracks, start a trebuchet or build walls."))''',
      '''upgrade a barracks or start a trebuchet." if g.is_robots(0) else "▸ Tap one of your hexes to upgrade a barracks or start a trebuchet."))''')
m.save()
b = F(P + '/scripts/ui/board_view.gd')
b.rep('''and tex("castle_keep") == null:''', ''':   # the old whole-hex castle tile with its walls (back again 2026-11-24 afternoon)''')
b.rep('''        var keep: bool = art == "castle_neutral" and tex("castle_keep") != null   # the single keep (2026-11-24)''', '''        var keep: bool = false   # the single keep picture isn't used (Ethan went back to the walled tile, 2026-11-24)''')
b.save()
print('ok')

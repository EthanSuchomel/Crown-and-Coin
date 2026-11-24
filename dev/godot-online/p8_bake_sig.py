"""Ethan, 2026-11-23: in an online game on The great divide the river vanished and forests were in the wrong places.
Every board picked up from the friend went through GameState.restore, which sets the board's shape again (shape_id goes
up even though nothing changed), so the baked ground was redrawn after every move; the redrawn picture came out wrong
(tiles missing, only the joins left). The baked ground now depends on what it shows (grid size and which hex is what),
not on how many times the shape was set, so it's drawn once per map.
Usage: python3 p8_bake_sig.py PROJ"""
import sys
sys.path.insert(0, __file__.rsplit('/', 2)[0] + '/godot-port-nov22')
from common import F
f = F(sys.argv[1] + '/scripts/ui/board_view.gd')
f.rep('''    var parts := PackedStringArray([str(HexGrid.shape_id), str(N)])
    for t in live:''', '''    var parts := PackedStringArray([str(N), "/"])
    for t in live:
        parts.append(str(int(t.id)))''')
f.save()
print('ok')

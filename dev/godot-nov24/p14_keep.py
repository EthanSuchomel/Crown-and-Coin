"""Ethan, 2026-11-24: the neutral castle is a single keep with no walls (art/terrain/castle_keep.png, from OpenArt),
standing on the grass a little smaller than its hex so walls run round it; every faction's walls are stone.
Usage: python3 p14_keep.py PROJ"""
import sys, shutil, os
sys.path.insert(0, __file__.rsplit('/', 2)[0] + '/godot-port-nov22')
from common import F
P = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
shutil.copy(os.path.join(here, 'files/art/terrain/castle_keep.png'), P + '/art/terrain/castle_keep.png')
b = F(P + '/scripts/ui/board_view.gd')
b.rep('''        "castle_neutral": "res://art/terrain/castle_neutral.png",''', '''        "castle_neutral": "res://art/terrain/castle_neutral.png",
        "castle_keep": "res://art/terrain/castle_keep.png",''')
b.rep('''    elif t.castle and not (game.homes.has(int(t.id)) and int(t.owner) >= 0):
        key = "hex_castle_neutral"''', '''    elif t.castle and not (game.homes.has(int(t.id)) and int(t.owner) >= 0) and tex("castle_keep") == null:
        key = "hex_castle_neutral"   # (the old whole-hex castle tile, only if the keep picture is missing)''')
b.rep('''        var ct: Texture2D = tex(art)
        if art == "castle_neutral" and _whole_tile(t) == "hex_castle_neutral":
            ct = null   # the neutral castle tile already fills the hex
        if ct != null:
            var ratio: float = ct.get_size().y / ct.get_size().x
            var w: float = 26.0 if art == "castle_mythical" else minf(_hh - 3.5, 2.0 * HFIT / (ratio + 1.0 / sqrt(3.0)))   # the Floating Castle is drawn big, filling its hex (Ethan, 2026-11-10)
            var h: float = w * ratio
            _draw_rect_tex(ct, Rect2(c - Vector2(w, h) * u / 2.0, Vector2(w, h) * u))''', '''        var keep: bool = art == "castle_neutral" and tex("castle_keep") != null   # the single keep (2026-11-24)
        var ct: Texture2D = tex("castle_keep") if keep else tex(art)
        if art == "castle_neutral" and _whole_tile(t) == "hex_castle_neutral":
            ct = null   # the neutral castle tile already fills the hex
        if ct != null:
            var ratio: float = ct.get_size().y / ct.get_size().x
            var w: float = 19.0 if keep else (26.0 if art == "castle_mythical" else minf(_hh - 3.5, 2.0 * HFIT / (ratio + 1.0 / sqrt(3.0))))   # the Floating Castle is drawn big, filling its hex (Ethan, 2026-11-10)
            var h: float = w * ratio
            _draw_rect_tex(ct, Rect2(c - Vector2(w * 0.5, h * (0.58 if keep else 0.5)) * u, Vector2(w, h) * u))''')
b.rep('''    var wood: bool = int(t.owner) >= 0 and String(game.players[int(t.owner)].faction) == "mammals"''', '''    var wood: bool = false   # every faction's walls are the castle's stone walls (2026-11-24)''')
b.save()
print('ok')

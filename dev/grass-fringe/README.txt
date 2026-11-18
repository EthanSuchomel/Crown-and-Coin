Grass edge over mountains and forests (Ethan, 2026-11-17: "make new hexes for the trees and mountains that have a better
transitional edge from the grass? or ... a new grass edge that transitions into the tree and mountain hex?"). Went with the
grass edge: one ragged strip cut from the OpenArt grass tile (grass_0), tufts reaching in, a soft shadow on the tile, the
hex corners rounded off. Drawn on each side of a mountain or forest hex that faces a plain grass hex (not castles, water,
other forests/mountains or the map edge), so any terrain can use it.
  make_fringe.py SRC OUT   fringe.png, 164x56: edge 128 px, 18 px past each corner, 12 px outward of the edge
  patch_fringe.py index.html fringe.png   browser: GRASS_FRINGE, <image id="gfr">, drawn on top of the terrain layer
  Godot: board_view.gd (FRINGE_* consts, _is_grass), art/terrain/hex_grass_fringe.png

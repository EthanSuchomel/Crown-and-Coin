Castle hex grounds (Ethan, 2026-11-12: "create a texture for each castle's hex so it can look more unified")

Each castle hex is drawn with a ground that matches the castle picture on it, in place of the grass:
  - Dinosaurs (volcano): dark volcanic ash and basalt with thin lava cracks (OpenArt)
  - Robots (war factory): riveted gunmetal deck plates with soot and rust (OpenArt)
  - Mammals (waterfall mesa): red savanna earth with dry golden grass tufts (OpenArt)
  - Mythical (floating castle): Ethan asked for "a black hexagon like it's floating over a space of nothing";
    drawn in code by make_tiles.py (black, lifting faintly toward the rim)
  - neutral castles keep the grass (Ethan didn't take the cobblestone texture)
The ground follows the castle picture: a home castle shows its owner's faction ground; any other castle is neutral.
The team colour wash is left off castle hexes so the ground keeps its colours; the team border still shows the owner.

  src/              Ethan's three OpenArt textures (1360x1360)
  make_tiles.py     OUTDIR [faction=src.png ...]: the middle half of each texture, cut to the hex (222x256, pointy top,
                    transparent outside), plus the Mythical void
  tiles/            the tiles used in the game
  patch_ground.py   index.html tiles/: CASTLE_GND, castleGnd(t), drawn as the hex's ground in renderMap
  preview.js        screenshots of each castle hex

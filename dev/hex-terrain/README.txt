Grass and mountain hex tiles (Ethan, 2026-11-16: the grass "still looks too sloppy and awkward"; wanted "a mountain hex
that actually has the whole hex as a mountain instead of the out of place mountain image"; then "for the grass instead of
placing that over the entire map can you use that texture for each individual hex?")

  src/grass_openart.png      Ethan's pick: crisp pixel-art grass (OpenArt, GPT Image 2.6 Sunburst, text2image)
  src/mountain_openart.png   Ethan's pick: a hex-shaped mountain on magenta (same model)
  make_tiles.py              OUTDIR grass.png mountain.png: three grass tiles (different crops of the texture, same scale
                             as the castle grounds) and the mountain fitted to the hex row by row (the OpenArt hexagon is a
                             little squashed); 222x256, pointy top, transparent outside, like the water tile
  tiles/                     the tiles used in the game
  patch_terrain.py           index.html tiles/: HEX_TERRAIN; every hex drawn on its own grass tile (one of three, by hex
                             number), mountain hexes on the mountain tile; the terrain key icon uses the new mountain
  castle_neutral (2026-11-16): Ethan's OpenArt hex castle (src/castle_neutral_openart.png), drawn on every neutral
                             castle hex in place of the stone castle picture and the grass; no colour wash, the team border
                             still shows the owner
  forest, fern (2026-11-16): Ethan's own four trees / four ferns (sheets uploaded to OpenArt) built into whole-hex tiles
                             in the mountain's style (OpenArt image2image); drawn on forest / fern hexes in place of the
                             trees and ferns placed one by one; fitted by the hexagon's own points (the forest has a tree tip
                             poking above the top edge, which is trimmed)
  soft edges (2026-11-17, "everything looks very choppy... flow together better"): make_tiles.py also writes *_soft.png
                             (the tile fading out over a ragged band; mountains wider and more uneven); the board draws grass,
                             mountain, forest and fern soft tiles 10% bigger than the hex in their own layers (grass, then
                             terrain, then owner tint and borders), so neighbours overlap and blend; the hex grid lines are faint
  2026-11-17: new forest (small trees, full canopy) and fern field (small clumps) tiles that thin out to grass at the
  edges, and a beach lake for water (src/water_openart.png; old forest/fern sources kept as *_v1.png)
  2026-11-17 (later): forest and ferns made clearly different: a dark, cool, dense forest (tips of the back row kept
  above the hex as forest_top.png, drawn over the hex behind) and a bright, low, muddy fern meadow with puddles, a creek,
  horsetails and mist (previous sources kept as *_v2.png)

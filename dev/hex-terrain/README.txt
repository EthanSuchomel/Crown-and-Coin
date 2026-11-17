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

Edge-aware terrain (Ethan, 2026-11-17: "Is it possible for the forests mountains and water to mesh together or seam together
when placed next to each other?" -> preview -> "The trees need a little more meshing" -> "please implement that into the
godot game"). Godot only so far (the iPad/browser version is unchanged).
Each forest / mountain / lake hex fades side by side by its neighbour on that side:
  grass, castle, map edge: as before (the soft tile's fade)
  same terrain: forests fade well before their grassy rim along a ragged line, over a canopy bridge; mountains run solid
     to the shared edge (a solid layer under the join) and cross-fade over it; lakes are joined by a water bridge
     laid over their beaches (centre to centre, soft shores; the middle of three lakes is filled too)
  other terrain: a wider fade, so they overlap with no grass between
preview.py          the Python preview (edge_aware_preview.png)
godot/              terrain_bake.gd (draws the ground once into a picture in a SubViewport, on the GPU), terrain_tile.gdshader,
                    terrain_bridge.gdshader, board_view.gd (uses the picture; rebuilt when the terrain changes; plain soft
                    tiles until it's ready or if it can't be made), art/ (edge_noise.png, hex_forest_patch.png and
                    hex_water_patch.png cut from the middle of the soft tiles)
godot_edge_aware.png  a Godot render (AOE 2, 3 players, with owned land)

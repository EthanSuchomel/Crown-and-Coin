Hand-made maps in the game (Ethan, 2026-11-17: "ive now made a few maps. can you implement them into the game now as options?")
Maps come from the Map Maker's store (artifact 699ae73a-a440-4f96-924a-a191e79de556, collection "maps"; see map-maker.md).
maps.json   the 2- and 3-player maps (the two 4-player ones wait for a 4-player mode)
Browser: patch_maps.py index.html maps.json  (re-run with a new maps.json to swap the list). New-game screen: Map row under
  Players (Random + the maps for that many players, remembered). S.map / S.mapName; syncShape() keeps VOID, HOMES and the
  framing on the map's own shape (also after loading a save and for online games).
Godot: port_godot.py made godot/: data/maps.json, GameData.maps / map_by_id / maps_for, HexGrid.use_shape (custom, shape_id),
  BoardGen.from_map, GameState.new_game(..., map) and map_id (saved), board view frames by shape_id, the Map row on the
  faction screen (pref_map, remembered).
Tested: computer games on every map in both versions, save/load keeps the shape, a random game afterwards is normal.

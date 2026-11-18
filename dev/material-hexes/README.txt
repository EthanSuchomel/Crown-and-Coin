Material hexes (Ethan, 2026-11-17: "add material icons to 6 hexes just like the coins on the map")
6 on the 2-player board, 9 on the 3-player board (3 nearest each side). The first side to take one gets 4 materials
(MAT_BONUS / rules.crate.materials; 4 materials = 8 gold at market price, the same as a coin); the Mythical get nothing,
like coins. Placed like the coins (fair distance to every home), never on a coin, castle or forest. Tile flag: crate.
Old saves get them placed on load. The computer values one like a coin.
  patch_crates.py index.html   browser
  godot/                        the changed Godot files (rules.json, board_gen, game_state, ai_player, board_view, main, test_rules)

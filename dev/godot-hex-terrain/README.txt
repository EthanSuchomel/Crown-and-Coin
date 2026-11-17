Godot side of dev/hex-terrain (2026-11-16): scripts/ui/board_view.gd loads art/terrain/hex_grass_0..2.png and hex_mountain.png
(the tiles in dev/hex-terrain/tiles), draws every hex on its own grass tile (same pick as the browser) and mountain hexes
on the mountain tile; falls back to the old grass and mountain picture if the tiles are missing. The old board_view.gd is in
_backup_before_hex_terrain/ in the Godot project. Parse-checked with Godot 4.7.2 only (not run on a board).

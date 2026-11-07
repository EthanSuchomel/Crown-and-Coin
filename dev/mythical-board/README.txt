The Mythical on the Crown & Coin board (Ethan's rules, 2026-11-07).
build.py: takes the repo's index.html and arena.html (before this change: commit 0d5e4d6), applies
  patch_arena_mages.py to the arena (Mages by level: mage0..mage3, hidden from the army controls) and
  patch_board_myth.py to the board code (everything outside window.ARENA_HTML), then re-embeds the arena.
myth_board_art.json: the board pictures (Floating Castle, Life Tree, unit pictures, magic crystal and dome icons).
edits-myth-board-arena.html.json: the arena edits as find/replace pairs (plain arena.html text).

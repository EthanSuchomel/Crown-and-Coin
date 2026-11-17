Painted map test (2026-11-17), claude.ai link only. To publish it there (from a chat opened from the Crown & Coin artifact page):
  python3 dev/claude-version/make_claude_version.py index.html OUT.html && python3 dev/painted-map/patch_painted.py OUT.html
then publish OUT.html to the existing artifact. Not applied to the repo index.html (iPad) or Godot.
Shaped pieces (2026-11-17): src/*_pieces.png are Ethan's OpenArt sheets; cut_pieces.py cuts them into pieces/; patch_painted.py
draws one piece per forest/mountain/fern hex and a long piece between same-kind neighbours (no hex tiles for those).

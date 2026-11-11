Themed faction decks, Fortify as a wild card, and materials (Ethan, 2026-11-10)

patch1.py .. patch5.py were run in order on the claude.ai link version of index.html (repo b3b855e
through dev/claude-version/make_claude_version.py), followed by a few small one-line fixes made by hand
(short "Advance" label on small screens, materials wording per faction, a guard for games saved mid-Fortify).
The finished page was then carried into index.html line by line; make_claude_version.py on the new
index.html gives exactly the published link version (1794378911-d681, link version 132).

Tests (Playwright, run from a folder holding test.html):
  bal.js  - computer-vs-computer games for every faction pair (quick board battles)
  sim2.js - the same with counts of materials bought, Fortify picks, regroup moves and buildings
  ui.js   - clicks through a human Fortify: regroup, pick Build, buy materials, build a barracks

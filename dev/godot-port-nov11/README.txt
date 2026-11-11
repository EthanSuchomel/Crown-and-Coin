The 2026-11-10/11 browser changes ported to the Godot version (Ethan's CrownAndCoin-Godot, Godot 4.7.2):
themed decks, Fortify as a wild card (regroup up to 2 hexes, then Build / Advancements / Recruit picks), materials bought
at markets, the Dinosaur cards' own upgrades (Cheap Nests = every building 1 cheaper), Armor (board and Arena), the card
head shots, the crate icon, no home-castle crown, the bigger Floating Castle, the centred Life Tree, and planting a Life
Tree with a Mage that moved this turn.
Apply to a copy of the project, in order: p1_data.py PROJ, p2_rules.py, p3_battle.py, p4_ai.py, p5_test.py, p6_board.py,
p7_ui.py, then copy art/ over PROJ/art/ (build.sh does it all from base/ to work/).
check/ (not shipped): ui2.gd drives the new screens (SHOTS=dir for screenshots under xvfb-run --rendering-driver opengl3),
soak2.gd computer vs computer for every pairing, mam.gd the Mammals against the Dinosaurs and Robots.
Results: self-test 215 passed, 0 failed (45 new checks). Written to Ethan's computer on 2026-11-11 with the replaced files
in _backup_before_nov11_update/. Three-player mode is not ported yet.

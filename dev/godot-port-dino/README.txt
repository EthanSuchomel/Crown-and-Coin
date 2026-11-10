The Dinosaur rework (browser, 2026-11-09) ported to the Godot version (Ethan's CrownAndCoin-Godot, Godot 4.7.2).
Apply to a copy of the Godot project, in order:  python3 p10_data.py PROJ; p11_rules.py; p12_ui.py; p13_arena.py; p14_tests.py
(common.py: shared helpers; the GDScript in the patches is written with 4 spaces and turned into tabs).
art/: the new pictures, named <folder>_<file>.png (terrain_castle_dinos.png -> art/terrain/castle_dinos.png, and so on).
check/: not shipped. soak.gd (computer vs computer, volcano and guard use), ui_smoke.gd (drives the new screens for script
errors), ui_shots.gd (screenshots; run under xvfb-run with --rendering-driver opengl3).
Results on 2026-11-09: self-test 168 passed, 0 failed (22 new Dinosaur checks); written to Ethan's computer with a backup of
every replaced file in _backup_before_dino_rework/ (Godot ignores it: .gdignore).

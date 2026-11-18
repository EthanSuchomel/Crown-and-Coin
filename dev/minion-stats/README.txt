Minion (Ethan, 2026-11-17): 0.5 damage every 2 s (was 2), speed 60 (was 70; arena 3.24 field units/s, was 3.78), Floating Castle
free Minions 1/3/5/8 by castle level (was 5/7/9/11). Browser: patch.py index.html arena.html (board UNIT_STATS, arena unit,
arena help table, MYTH.minions, faction text). Godot: port_godot.py -> godot/ (units.json, rules.json mythical.minions,
arena_battle.gd, main.gd: _num() so 0.5 shows instead of 0, faction text).

# Godot port of the 2026-11-22 browser updates

Run in order on the Godot project (after copying `files/` and `art/` in):

    cp files/scripts/ui/* PROJ/scripts/ui/
    cp art/title_battle.jpg art/title_battle_dim.jpg PROJ/art/ui/
    python3 p1_rules.py PROJ   # Mythical 5 magic first turn, castle magic 1/3/6/10, computer pace by difficulty
    python3 p2_theme.py PROJ   # home screen painting + carved-gold title, iron/bronze theme everywhere
    python3 p3_setup.py PROJ   # setup screen in three tabs, rival colours, map pictures, themed pop-ups
    python3 p4_board.py PROJ   # map as background layer, zoom, turn-change slide, numbers box, header buttons

`title_battle_dim.jpg` is the painting blurred 2px, darkened to 62% and vignetted (the setup screen's backdrop).
`check/ui_nov22.gd` (not shipped) takes screenshots: `SHOTS=dir/ WHAT=title,setup,game,play`.
Skipped (browser only): online nudge, phone safe-area margins, iPad updates.

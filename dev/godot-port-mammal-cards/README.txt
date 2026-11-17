Godot port of the Mammal card upgrades (browser commits e8eccb7 and 9732b22), 2026-11-16.
Run from the Godot project folder:
  python3 p_mammcards.py         data, rules, computer, screens and self-tests
  python3 card_png.py <src dir>  the five card pictures (dev/mammal-cards/src), cut out like the browser's
Also fixed a combat.gd bug: a sneak attack's held-back defender hits had no "recoil" key, so an Ambush
into Porcupines crashed (a one-line fix, applied by hand: add "recoil": {} to the stub at hits_on_a).
And the old Fortify test now expects 1 pick for the Mammals (card upgrades replace the usual levels).
Self-test: 345 passed, 0 failed (62 new Mammal card checks).

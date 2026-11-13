The board Mammal numbers (browser commit 5d2cd9e) ported to the Godot version, 2026-11-12.
Rhino 12 damage; Porcupine 8 health with quills (thorns 1: a melee hit that lands pricks the attacker for 1, Rhino tramples too;
Armor divides it like other damage); no Procoptodon in the Mammal barracks, barracks unlocks or Watering Hole list
(its numbers stay for old saves); Watering Hole and barracks-level texts as in the browser.
Apply: python3 p1_mammals.py PROJ. Checked: self-test 287 passed (7 new checks). A field-by-field compare of the browser
UNIT_STATS / arena TYPES against Godot found no other differences.

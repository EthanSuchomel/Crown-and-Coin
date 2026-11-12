## Mage level test (2026-11-11)
Run in the Godot copy of the Arena (its numbers matched the browser's round 7 within a few points), with the Minion attacking every 2 s. The Mythical default army (25 Minions, 3 Minotaurs, 1 Griffin, 1 Dragon) with its 2 Mages at each level, against each faction's default army on all 6 Godot maps, from both sides, 4 seeds: 144 battles per level, computer on both sides (Medium). No stalemates. Script: repo dev/godot-port-nov11/check/magelv.gd.

What a level changes in battle: lightning reach 30 / 60 / 90 / 120, damage 5 / 6 / 7 / 7, Minotaur chance 20 / 30 / 40 / 50%. Level 3 also allows a third Mage on a hex.

| Mages | Mythical win | vs Dinosaurs | vs Robots | vs Mammals |
|---|---|---|---|---|
| 2 at level 0 | 26% | 25% | 25% | 29% |
| 2 at level 1 | 80% | 79% | 83% | 77% |
| 2 at level 2 | 88% | 85% | 88% | 92% |
| 2 at level 3 | 92% | 90% | 94% | 94% |
| 3 at level 3 | 99% | 96% | 100% | 100% |

- Level 0 is weak (0% on the open field); the jump to level 1 (reach 30 → 60) is the big one. After that each level adds only a little.
- Their worst map at every level is the Mountain (29–92%).

## Changed after the test (Ethan, 2026-11-11)
Mage reach is now 30 / 45 / 60 / 90 and damage 2 / 3 / 4 / 5 for levels 0–3 (Minotaur chances unchanged). Done in the claude.ai link (version 137), the iPad app (repo commit f8aea99) and the Godot folder (arena_battle.gd, data/units.json for board battles, the level 3 note; old files in `_backup_before_mage_levels/`). The arena-only "Mage" in the Megaraptor Arena army picker (reach 120, damage 5) is unchanged. The win rates above are from before this change.

## Re-test with the new numbers (2026-11-11 evening)
Same test (144 battles per level, 6 maps, both sides, Minion every 2 s). No stalemates except 1 at level 1.

| Mages | Before | Now | vs Dinosaurs | vs Robots | vs Mammals |
|---|---|---|---|---|---|
| 2 at level 0 | 26% | **10%** | 15% | 6% | 8% |
| 2 at level 1 | 80% | **30%** | 38% | 29% | 23% |
| 2 at level 2 | 88% | **58%** | 69% | 50% | 54% |
| 2 at level 3 | 92% | **83%** | 90% | 75% | 83% |
| 3 at level 3 | 99% | **97%** | 94% | 98% | 98% |

- Each level now matters: a steady climb from 10% to 83%. Level 2 is close to even.
- Level 3 is still strong, and with a third Mage almost unbeatable (the third Mage is the biggest single boost left).
- Open field is now their worst map at low levels (0% at level 0, 4% at level 1); castles their best (33–92%).

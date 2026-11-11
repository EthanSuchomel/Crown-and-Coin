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

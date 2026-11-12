# Mythical on the Crown & Coin board (Ethan's rules, 2026-11-07)

The arena side is in mythical-faction-crown-and-coin.md. Some numbers in its stats table are out of date:
- The Mage's speed is now **50** (was 65); see Mage levels.
- The **Minion attacks every 2 s** (Ethan, 2026-11-09; was 1 s), in the arena and in the board's battle model.
- The Mage's lightning reach and damage by level changed on 2026-11-11 (see Mage levels).

## Where it's live
- **iPad site:** GitHub EthanSuchomel/Crown-and-Coin, commit bf3495b (Mage level requirements). The faction screen lists Mythical as a fourth faction, against any of the other three, and the computer can play it.
- **Main claude.ai Crown & Coin link** (7jbdEk6pGqUo5z36bGR7gj): version 138 (2026-11-11), the same game as the iPad site.
- **Main Megaraptor Arena link** (W2mCEC5RuMRsu3ouCSX8rk): brought level with the repo on 2026-11-08 (see dinosaur-rewrite.md).
  - **Behind the repo:** it doesn't have the Minion 2 s change.
  - It's public, so only a session that can publish it can update it: publish the repo's arena.html as the page.
  - It was at version 1794269897-9f67 on 2026-11-09. Check it for changes the repo lacks before overwriting.
  - Its own Mage (army picker, reach 120, damage 5) is separate from the levelled Mages the board sends.
- **Godot:** up to date with the link as of 2026-11-11 (godot-port-status.md), including plant-after-moving, the new Mage numbers and the level requirements.
- **The old test link** (NWaNyJaFK6cmGmYuQgDanm) is retired: don't publish to it.
- **Rebuilding:** dev/mythical-board/build.py BASE_INDEX BASE_ARENA applies patch_board_myth.py (board) and patch_arena_mages.py (arena) to the files from commit 0d5e4d6. Later arena changes are in dev/mythical-board/, dev/mage-levels/ and in other sessions' commits.
  - Normally, just edit the repo's current arena.html and index.html and re-embed the arena.
  - Always `git pull` first.

## How the human player chooses (Ethan, 2026-11-07)
Ethan asked for the same round buttons on posts around the tapped hex that the other factions use (`mythBubbles` and `mythBubbleItems`). The card column only shows the magic total and a hint.
- **Recruit:** tap a castle or a hex with a Mage.
  - At a castle: +3 Minions, +15 Minions, All, and a Mage.
  - On a hex with a Mage: Minotaur, Griffin and Dragon (faded with "Mage 1" or "Mage 2" until a Mage of that level is there).
  - Up to 7 buttons go all the way round the hex, smaller when there are more than 3.
- **Build:** tap a plain non-castle hex to get the Life Tree button.
- **Advancements:** tap any of your hexes to get Mage level, Dome and Floating Castle level.
- Tapping a button acts at once (no stats card first), and Undo works.

## Magic economy
- The Mythical earn and spend only **magic**, never coin.
  - In the code, magic is kept in `p.gold`; `cur$(pid)` gives the word "magic" or "gold" for display.
- Magic comes from Life Trees, the Floating Castle, Harvest and the Channeling card. Captured castles and markets give no magic.
- Captured enemy buildings do nothing for the Mythical: markets, forts (no defense bonus), barracks and trebuchets.
- **Claude's choice:** they don't take bonus coins or castle plunder.
- Magic can't be traded for coin.
- They have no materials and can't buy them (2026-11-10): markets sell materials only to the other factions.
- Harvest gives the basic amount in magic: 2, plus 1 for every 2 hexes. Ethan will expand this when he designs the cards.

## Cards (Ethan's theme, 2026-11-10: Advancements and Fortify; names are Claude's placeholders)
| Card | Actions |
|---|---|
| March of Minions | Move → Recruit → Fortify |
| Gathering | Harvest → Recruit → Advancements |
| The Grove | Fortify → Advancements → Move |
| Arcanum | Build → Advancements → Fortify |
| Channeling | No actions; every Mage makes 2 magic and every castle 5 |

Before 2026-11-10: March of Minions was Move → Build → Recruit, Gathering Harvest → Recruit → Move, The Grove Harvest → Advancements → Fortify, Arcanum Build → Advancements → Recruit.

Mythical cards don't upgrade yet, so their Fortify always regroups and then picks one of Build (Life Trees), Advancements (Mages, castle, domes) or Recruit (Minions, Mages, monsters).

## Units and prices
- **Minions:** 3 for 1 magic, made at the home castle and captured castles.
- **Mages:** made at castles.
  - **Base price:** 4 magic. This is Claude's placeholder; Ethan didn't give one.
  - **Extra cost:** +1 for each Mage past the 5th (the 6th costs +1, the 7th +2), and +1 for each Mage level.
- **Upgraded units:** a Mage turns Minions on its hex into units. Minions must be on the hex.

  | Unit | Magic | Minions used | Mage level needed (board only) |
  |---|---|---|---|
  | Minotaur | 7 | 1 | 0 |
  | Griffin | 10 | 2 | 1 |
  | Dragon | 15 | 4 | 2 |

  The highest-level Mage on the hex decides what's allowed.
- Mages recruit anywhere they stand, as many units as the magic covers, and can move and recruit in the same turn.
- **Hex limit:** at most 2 Mages on a hex (3 at Mage level 3). Any number can be on the map. Extra Mages in a move stay behind.

## Mage levels
- 3 levels, upgraded at the home castle for **7, 9 and 12 magic** (Ethan, 2026-11-07; was 4 each). Ethan first listed 5, 7, 9, 12, then chose to drop the 5.
- **Upgrade requirements** (Ethan, 2026-11-11): besides the magic, raising the Mages needs Life Trees and captured castles (castles you hold other than your home) at the moment you upgrade:
  - Level 1: 1 Life Tree.
  - Level 2: 3 Life Trees and 1 captured castle.
  - Level 3: 5 Life Trees and 2 captured castles.
  - Losing a castle (or a tree) later doesn't take the level away. The Mages button shows what's missing ("1/3 trees", "0/1 castles"). The computer follows the same rule.
- Each Mage keeps the level it was made at.
- **Board unlocks:**
  - Level 1: the Griffin.
  - Level 2: the Dragon.
  - Level 3: every unit costs 1 magic less (not Minions), and 3 Mages can share a hex.
- **In battle, by level** (Ethan, 2026-11-11: reach 30 / 45 / 60 / 90 and damage 2 / 3 / 4 / 5; were 30 / 60 / 90 / 120 and 5 / 6 / 7 / 7; Minotaur chance Ethan, 2026-11-07):

  | Level | Lightning range | Damage | Minotaur chance every 2 s |
  |---|---|---|---|
  | 0 | 30 | 2 | 20% |
  | 1 | 45 | 3 | 30% |
  | 2 | 60 | 4 | 40% |
  | 3 | 90 | 5 | 50% |

  - These are arena types mage0 to mage3, hidden from the arena's army controls, with up to 3 per army from the board. The damage applies to board battles too.
  - Win rates by level before and after the change: mage-level-test.md.
- **Arena Mage speed:** 50 (2.7 field units a second), at every level. Ethan set it on 2026-11-07; it was 65.
- **Standalone Megaraptor Arena** (patch_arena_magelv.py, then patch_arena_magelv2.py):
  - A Mythical side has a "Mage level" picker (0 to 3) above its units.
  - **Ethan, 2026-11-07:** in the arena the level only changes the Mages' lightning and Minotaur chance (the table above). Griffins and Dragons need no level, the Mage limit stays 2, and the gold total doesn't change with the level.
  - The default level is 2.
  - Battles sent from Crown & Coin don't show the picker; each Mage arrives with its own level.

## Movement (Ethan, 2026-11-07)
- 3 moves per Move action.
- Mages and Minions move up to 2 hexes anywhere. Other units use the normal rules.
- If a long move includes other units, only the Mages and Minions go.
- Fortify's regroup (2026-11-10/11) moves units up to 2 hexes through their own land; the Mage limit per hex still applies.

## Life Trees
- Planting (the Build action) costs no magic, but the Mage can't move for 2 whole turns: the rest of this turn and the next 2.
- **Plant after moving** (Ethan, 2026-11-10): a Mage that moved this turn can still plant a Life Tree on the hex it reached, on the same card (March of Minions: Move → Build) or later in the turn. Planting needs any Mage on the hex, not a ready one (edits in dev/mythical-board/edits-plant-after-move.json).
  - If a Mage there has already moved, it is the one that stays: a still-ready Mage on the hex isn't locked.
- **Claude's choice:** trees can't go on castles.
- Each tree makes 3 magic a turn, or 5 with 5 or more Minions on the hex.
- It's the hex's one building, and it's destroyed when the hex is captured.
- **On the map** (Ethan asked for it bigger, 2026-11-07; centred 2026-11-10): the tree is drawn large in the middle of its hex (`TREE_SIZE` 25 board units, the hex is about 31 wide).

## Magic domes (instead of walls)
- Made by a Mage on its hex during Advancements: 1 magic, then 1 magic every turn. A Mage that moved this turn can already make one.
- Unpaid domes fade.
- **Claude's choice:** a dome counts as a full wall (strength 3) on every side. It's damaged like walls, and it falls when the hex is captured.

## Floating Castle (the home castle)
- Makes 10 magic and 5 Minions a turn.
- 3 upgrades costing 10, 15 and 20 magic raise it to 15, 20 and 25 magic a turn, each with +2 Minions.
- Only flyers can attack it, and only flyers can be sent at it.
- **Claude's choice:** 1 Griffin guards it in every fight, instead of the 5 archers other home castles get.
- Drawn bigger, filling its hex (2026-11-10).

## Start
- 1 Mage, 4 Minions and 5 magic.
- **Claude's choice:** if Mythical moves second, it starts with +3 magic instead of +8 gold.

## Win conditions
- Captured castles count toward the 4-castle win, as for everyone.

## Balance checks
- **2026-11-07, first build:** in 12 quick computer-vs-computer games on Medium, the Mythical won all 12 against the other three factions, from either seat.
- **After the Mage upgrade price change:** still 12 of 12.
- **2026-11-11:** still every game in quick board tests (Godot and browser), and with the level requirements the computer still wins its test games by turn 8–10 on Hard.
- These games settle battles with the board's odds model, not the arena.
- The likely causes are the economy (10 magic and 5 free Minions a turn from the start) and cheap Minotaurs.

## Art
- Board pictures: Ethan's Floating Castle, Life Tree and unit pictures, shrunk down.
- The magic crystal icon and the dome are Claude's stand-ins.

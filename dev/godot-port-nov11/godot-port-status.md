# Crown & Coin — Godot port status

Project folder: C:\Users\ethan\Documents\CrownAndCoin-Godot (Godot 4.7.2). The browser version stays the reference for rules and numbers.
Self-test: open scenes/test_rules.tscn and press F6; every line should say PASS (215 checks as of 2026-11-11; the scene stays open when done).
Map preview: scenes/arena_preview.tscn (pick the map and holder in the Inspector).

## Done
- Board, cards, all six actions, home castle +4 defense and 5 guard archers, home-castle unlocks, favor strip.
- Arena battles on Open field, Ferns, Trees, Mountain, Castle and Fortress maps.
- 2026-11-04: castle gate fix, Brawler 1 s attack, board Robot Archer fires 2 lasers, Offline/Update (blocked by Herd) in Arena battles.
- 2026-11-05 controls: round buttons around the hex for Build / Recruit / Advancements, unit info card with +1/+5/All, undo until the next action (battles and trebuchet shots lock in), end-of-action warning, move sliders with − / +, player color (Red, Blue, Green, Yellow, Purple; remembered), computer takes 6–8 s per action.
- 2026-11-05 saving: autosave after every action (user://save.json); Continue on the title screen.
- 2026-11-05 difficulty: Easy / Medium / Hard / Expert picker on the faction screen (remembered). Expert gets 40% more gold (and magic). The computer judges fights by Arena rules (map calibration 0.825 open … 0.3 castle) and the Arena general plays by level.
- 2026-11-05 Fortress map; Mammals faction, complete (arena and board).

## 2026-11-09: brought up to date with the browser (changes from 2026-11-06 to 2026-11-08)
Written straight into the folder (55 files: 9 scripts/data changed, test_rules.gd, 45 new pictures).
- **Arena (arena_battle.gd, arena_view.gd):**
  - Dinosaur rewrite: Pachycephalosaurus, Dilophosaurus, Megaraptor, Triceratops, Stegosaurus with all their abilities, new pictures and Claude's walk/attack sheets (art/arena/dns_*). The Procoptodon is retired from the arena (any sent from the board are dropped).
  - Mythical: Minion, Mage (levels 0–3 from the board: lightning reach/damage, Minotaur chance), Minotaur (charge kill), Griffin (swoop, landing, screech), Dragon (fire run with burning streak, fire breath, landing). Pictures and wing sheets in art/arena/myth_*; the Dragon's 24-frame sheets are stored as 2 rows of 12 (T.sheetRows) because file transfer stops at 8,000 px.
  - Unit changes: Robot Brawler 4 hp, Archer 1 s, Knight 25 hp / 12 dmg / 1 s / 16 vs Triceratops, shield wall 50, Longbow 65% speed + never misses + gives up on a Triceratops after 2 harmless shots, Laser Tank beam 2.5 s and follows its bunch; Porcupine 8 hp + quills; Rhino 12; Bat 2 gold; Palaeoloxodon 50; Desmodus counts as large.
  - Headless check (4 factions × 6 maps, both sides): Mythical 83%, Dinosaurs 48%, Robots 47%, Mammals 20% — in line with the browser's round 7 (89 / 48 / 43.5 / 18).
- **Board (game_state.gd, ai_player.gd, main.gd, board_view.gd, data/*.json):** the Mythical as a fourth faction — magic economy (Floating Castle levels, Life Trees, Channeling card), Mages made at castles and levelled, Minion → Minotaur/Griffin/Dragon conversions where a Mage stands, Life Trees (Mage rooted 2 turns), magic domes (a full wall on every side, 1 magic upkeep), 3 moves with Mages/Minions going 2 hexes anywhere, only flyers can attack the Floating Castle (guarded by 1 Griffin), no forts/plunder/coins/trebuchets for them, round buttons round the hex like the browser, faction screen info and Magic unit table, computer plays them (myth_ai).
- **Later the same day:** Triceratops takes half damage from shots fired from walls and towers (on_wall) and from ballistas (browser commit f334a8f; one more self-test check).

## 2026-11-09 (evening): the Dinosaur rework (see dinosaur-board-rework.md)
Written into the folder from a cloud session through the desktop app's file bridge: 11 scripts/data files and 20 pictures. Every replaced file was first copied to `_backup_before_dino_rework/` in the project (Godot ignores it: `.gdignore`); Ethan can delete it once he's happy. (No .git folder is visible in the project from the file bridge, so the backup is the way back.)
- **Board roster = the arena's:** Pachycephalosaurus (3 gold, basic), Dilophosaurus (8), Megaraptor (12, barracks 1), Pterodactyl (5, barracks 2), Triceratops (25, barracks 3, shots and spells do nothing to it), Stegosaurus (30, barracks 3). The barracks menu puts its 6 units evenly round the hex; the home castle ring holds all of them. New board unit pictures from the browser's.
- **No forts or trebuchets** for the Dinosaurs (no Fort button, forts give them no defense, captured trebuchets are wrecked; the computer doesn't build forts for them).
- **Alamosaurus guards:** Advancements at a barracks, 25 gold, up to 2 per barracks; never ready, so they never move or attack; fight when the hex is attacked; a fled guard is lost. In the arena the Alamosaurus is back (120 hp, 15 every 2 s to up to 4 enemies, no riders/charge/stomp), with the rider-free body and cleaned legs.
- **Volcano** at the home castle: 40 / 60 / 100 gold, reach 5 / 7 / whole map, every 3 / 2 / 1 turns, 5 / 6 / 8 dice (4+ hits for 10). Fires in the volley at the start of the turn (you aim it; the computer picks the biggest army), with a lava-bomb animation on the board. Hex details show its level and when it erupts next.
- **Art:** volcano home castle, nesting-ground barracks (drawn 1.5x), ammonite fossil market (1.18x).
- **Texts:** action descriptions, hints, the leftover warning, How to play, the faction screen (Alamosaurus row and a Volcano and guards section), Populate/Abundance.
- **Also fixed:** notes under the card stopped appearing once the log reached 80 lines (main.gd counted the log's size); now a running count (GameState.log_n).
- **Checked here before writing:** self-test 168 passed (22 new Dinosaur checks); a headless run through the new screens with no script errors; screenshots under a virtual display. Computer vs computer (6 games each): the Dinosaur computer wins 3 of 18, the same as before the rework; it wakes the volcano and hires guards, but not often (only when it has the gold when an Advancements comes up).
- Port scripts, art and checks: repo EthanSuchomel/Crown-and-Coin, dev/godot-port-dino/ (commit dd7e465). Godot itself can run in the cloud session for tests (download Godot 4.7.2 from GitHub).

## 2026-11-09 (night): matched to the claude.ai version
Ethan asked for the Godot version to match the claude.ai link. A side-by-side check of both versions' numbers (board unit stats, arena unit types, rules, Mythical numbers, cards, what each building trains) found them already the same after the Dinosaur rework. Three things were left, now done (8 files written; the 7 replaced ones copied first to `_backup_before_browser_match/`):
- **3D trebuchet firing animation** (new scripts/ui/treb_anim.gd): when a finished trebuchet fires, yours or the computer's, its 3D model stands where its picture is, swings its arm and lobs the stone at the target hex, with a puff of dust where it lands. Steel model for the Robots, bone for everyone else, team colour on the bands. A port of the browser's three.js one (same model, timings, light and camera angle; drawn at 3/4 resolution with chunky pixels like the browser's canvas). Shots play one after another. As in the browser, a target more than a hex or so away is outside the model's little window, so the stone flies out of view.
- **Rhino and Palaeoloxodon walk:** their walk frames now step with the ground they cover (browser `stride`), so their feet don't slide.
- **Unit notes:** Robot Archer "Fires 2 lasers a shot"; Robot Longbow "shots 1, 5, 9…".
- Checked first: self-test 170 passed (2 new checks), screenshots of a Robot and a Mammal shot, and a headless arena run of the walk frames.
- Port script: dev/godot-port-dino/p15_match.py + treb_anim.gd in the repo.
- **Kept different on purpose:** the browser's Minion note says "The only Mythical unit that captures castles", but neither version enforces that rule, so Godot keeps the accurate note. Godot also keeps its Nov 1 computer calibration (ARENA_CAL), which the repo version lacks.

## 2026-11-09 (late): Minion attacks every 2 s
Ethan's change (browser commit 80f442c), written into the folder through the file bridge:
- data/units.json, the board's battle math: minion "rate" 2.0 (was 1.0).
- scripts/arena/arena_battle.gd, the arena: minion "rate" 2.0 (was 1.0).
- The two old files are in `_backup_before_minion_rate/` (with `.gdignore`).
- Not re-run in Godot here: there's no self-test check on the Minion's rate.

## 2026-11-11: themed decks, wild-card Fortify, materials, the Dinosaur cards (browser v132–v136)
Ethan asked for the Godot version to catch up with the browser. Written into the folder through the file bridge: 10 scripts/data files and 6 new pictures (art/cards/stamp, pack, siege, hunt, nest = the Dinosaur head shots; art/ui/mat.png = the crate). The 10 replaced files are in `_backup_before_nov11_update/` (with `.gdignore` and a README).
- **Decks** (data/factions.json): the themed decks from cards-fortify-materials.md; the Dinosaur cards carry `card_art`.
- **Fortify is a wild card** (game_state.gd `play.fx`, `fx_begin`, `fx_choose`, `fx_next`, `last_step_now`, `regroup_targets`): the faction ability (Mating, Update), a regroup of moves up to 2 hexes through your own land (units stay ready), then Build / Advancements / Recruit at the basic level (2 picks at level 2, 3 at level 3). The +1 defense is gone (`braced()` always false). Screens: Regroup with **Done regrouping**, three pick buttons, "Fortify: Build" heading, **Skip**. Undo works inside each phase. Old saves sitting on a Fortify step open at the pick.
- **Materials** (rules.json `materials`, game_state.gd `buy_mat`, `mat_cap`, `ai_mat`…): 3 a turn per market and from the home castle, 2 gold each; forts 5/5/4/3, barracks 5/5/5/4, barracks upgrades 3/4/5, walls 3/3/2/2, field trebuchet 8, castle trebuchets 10/15, Watering Hole 4. The header has a **materials** button (opens the buying sheet with − / slider / +); Build and Advancements show materials and **Buy materials**; the round buttons show prices with the crate. The Mythical keep magic.
- **The Dinosaur cards' own upgrades** (upgrades.json `dinos_cards`, game_state.gd `dk`, `dino_harvest`, `dino_action_start`, `_dino_fortify`, `dino_cost`): all 45 of Ethan's upgrades, including Cheap Nests as "every building 1 cheaper", Calling's tap on a nesting ground, Join Up / On the Move / Rally, Two Herds (a checkbox in the attack dialog), Charge, Home Run, Dash, Over the Top, the free nest token, Quick Nests, Cheap Guards and **Armor** (40 gold at the home castle; +2 damage and +10% health on the board and in the Arena via `hp` per team). Herd, Migrate, Nesting, Populate, Abundance and Rainy Season are retired. Card head shots on the hand cards and the playing card; the upgrade picker, How to play and the faction screen list each card's upgrades.
- **Map art:** no crown on home castles, the Floating Castle drawn 26 wide, the Life Tree centred.
- **Mythical:** a Mage that moved this turn can still plant a Life Tree (the browser's rule).
- **Computer:** regroups toward the front, picks by trying each option on a copy, buys and stocks materials, builds free nests first, forges Armor, values Fortify upgrades at 4.2.
- **Arena bottom line:** already used the real colour names in Godot (nothing to change).
- **Checked first:** self-test 215 passed (45 new checks), a headless click-through of every new screen with no script errors, screenshots under a virtual display, computer vs computer for every pairing.
- **Balance note:** the Mammal computer wins less than before (Godot quick test 5 of 24 against Dinosaurs and Robots, was 15 of 24). The browser shows the same drop with the new rules (bal.js: Mammals 28% → 11%, Robots 44% → 67%), so it comes from the rules, not the port.
- Port scripts and checks: repo dev/godot-port-nov11/ (commit 9c91a69).

## Still to bring over
1. Online play (later, likely through Steam).
2. **Three-player mode** (browser commit b3b855e, 2026-11-10; Ethan chose "browser first, Godot after"). Not in the 2026-11-11 update. Everything needed is in three-player-mode.md and the repo's dev/three-player/:
   - the 79-hex board and its symmetric map maker;
   - turn order that skips sides who are out, and knock-outs where the land goes neutral;
   - starting gold for the second and third sides;
   - the computer weighing two rivals;
   - computer-vs-computer battles settled on the board;
   - the Players 2/3 toggle and a picker for each rival.
   The online half waits for online play.

## Notes
- The Godot computer uses a fast strength estimate instead of full battle simulations, so Medium's edge over Easy is smaller than in the browser.
- The Dinosaurs are the computer's weakest side in the Godot version (about 1 win in 6 against each of the others at Medium, before and after the rework).

# Crown & Coin — Godot port status

Project folder: C:\Users\ethan\Documents\CrownAndCoin-Godot (Godot 4.7.2). The browser version stays the reference for rules and numbers.
Self-test: open scenes/test_rules.tscn and press F6; every line should say PASS (168 checks as of 2026-11-09, evening; the scene stays open when done).
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

## Still to bring over
1. Online play (later, likely through Steam).

## Notes
- The Godot computer uses a fast strength estimate instead of full battle simulations, so Medium's edge over Easy is smaller than in the browser.
- The Dinosaurs are the computer's weakest side in the Godot version (about 1 win in 6 against each of the others at Medium, before and after the rework).

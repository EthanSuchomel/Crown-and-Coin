# Dinosaur faction rework on the Crown & Coin board (2026-11-09)

Ethan wanted the Dinosaurs to look and play differently from the other factions, the way the Mythical do. The board now matches the arena's new Dinosaur roster, and the Dinosaurs have their own buildings and specials.

## New art (OpenArt, GPT Image 2.6 Sunburst, magenta background, cut out by Claude)
- **Home castle:** a black volcano with classic orange lava (see dinosaur-volcano-castle.md).
- **Barracks:** a large volcanic nesting ground with volcano walls and steam vents, but no baby dinosaurs. It's drawn 1.5x bigger on the hex because it's flat.
- **Market:** an ammonite-shell fossil market.
- **Alamosaurus guard:** Claude edited the existing arena sprite, with Ethan's OK. The tower, the two Dilophosaurus riders, the saddle cloth and the armour plates are gone. The body was repainted with the neck's own stripes, which taper out at the hips. Both teams use the same body; the team shows in the coloured ring under its feet. The board's unit picture was remade from it.

## Rules (Ethan's choices)
- **No forts and no trebuchets** for the Dinosaurs. They can't build forts. Forts don't count for them, and trebuchets they capture are wrecked.
- **Board roster (same as the arena):**
  - Pachycephalosaurus (basic)
  - Dilophosaurus (archer)
  - Megaraptor: barracks level 1
  - Pterodactyl: barracks level 2
  - Triceratops and Stegosaurus: barracks level 3 (level 3 still gives 1 gold off everything bought there)
- **Alamosaurus guards** (an Advancements upgrade at a barracks):
  - 25 gold each, up to 2 per barracks.
  - Stats: 120 health, 15 damage every 2 seconds. Each stomp hits up to 4 enemies; that is its only ability (no charge, no stomp stun, no riders).
  - They fight only when the hex is attacked and can hold it on their own. They never move or attack.
  - Dead guards stay dead and must be hired again. A guard that flees is lost too.
  - In the standalone arena, the Alamosaurus is hidden from the army controls.
- **Volcano strike** (replaces the trebuchets; bought with Advancements at the home castle):

  | Level | Cost | Reach | Erupts | Dice |
  |---|---|---|---|---|
  | 1 | 40 gold | 5 hexes | every 3 turns | 5 |
  | 2 | 60 gold | 7 hexes | every 2 turns | 6 |
  | 3 | 100 gold | whole map | every turn | 8 |

  - One volley a turn, at the start of the Dinosaurs' turn, at an enemy hex with units that they pick. With only one target, it fires by itself.
  - Each die of 4 or more is a hit of 10 damage, front of the line first. Walls don't stop it.
  - If the home castle falls, the volcano is lost.
  - A 2D lava-bomb animation plays from the volcano to the target.
  - The hex details show the volcano's level and when it erupts next.
- **Card ability text:**
  - Populate now gives 1 free Pachycephalosaurus at each barracks (no forts).
  - Abundance now names the Pachycephalosaurus and Dilophosaurus.

## Assumptions Claude made (Ethan can change these)
- Lava has no extra effect beyond the dice damage.
- The Pterodactyl unlocks at barracks level 2.
- The computer player buys volcano levels first, then guards at barracks with enemies within 2 hexes.

## Where it lives
- **iPad site:** repo EthanSuchomel/Crown-and-Coin, commit 6fe608d (index.html, arena.html, sw.js bumped). Patch scripts and art are in dev/dino-board/.
- **claude.ai Crown & Coin link** (7jbdEk6pGqUo5z36bGR7gj): updated to the repo version the same evening (version 1794284534-6f89), with the Mythical faction and this rework; online play kept.
- **Godot version:** ported the same evening and written to Ethan's computer, with a backup of the replaced files (see godot-port-status.md; scripts in the repo's dev/godot-port-dino/).
- **Not done:**
  - A board picture of a barracks with guards standing at it (to discuss with Ethan before making it in OpenArt).
  - Volcano-style walls for the arena's Castle map.

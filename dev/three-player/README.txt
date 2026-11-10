Three-player mode (Ethan, 2026-11-09/10)

What it is
- 3 sides, any mix of people and computers, offline (you + 2 computers) and online (each person on their own device).
- Board: 79 hexes (about 1.5x the 2-player 52) cut from an 11x11 grid: a radius-5 hexagon minus the 6 corners and the
  2 edge hexes beside each of the 3 corners between the homes. 10 mountains, 4 lakes, 26 coins, 6 neutral castles,
  15 forests, 15 fern patches. Homes 8 apart; terrain is placed in 120-degree symmetric sets (genMap3) so no side is favored.
- Take a side's home castle (or wipe out all its land) and they're out: their land goes neutral (buildings stay), their
  old home becomes an ordinary castle. Last side standing wins. No castle-count win and no siege with 3 sides.
- Moving second/third gives 6/12 extra gold at the start.
- The computer weighs both rivals (each counts 0.6x), and a rival's home is worth 2500 to it (knocks them out).
- Computer vs computer battles are settled on the board; any battle with a person in it goes to the arena.
- Online: the game doc stores the board from seat 0's side; each device turns it so it is seat 0 (rotSeats).
  A computer seat's turn is played by the device of the person who just handed over (S.runner); if that device goes
  quiet for 45 s another device takes over. Battles: the two people in it fight live, the third watches;
  computer attacks a person: the runner hosts with the computer leading the attackers.

Files
- board3.py / board3.json: works out the 79-hex board (void hexes, homes, centre).
- gensim*.py, preview.py: map-generation trials used while designing (not needed to build).
- patch1_board.py   board size per game (useBoard), the 3-player board and its map generator
- patch2_rules.py   turns, knock-outs, gold, colors, the new-game screen, win/lose screens, How to play
- patch3_ai.py      the computer plays against two rivals
- patch4_online.py  3 seats online: lobby, seat turning, computer seats online, battles with a watcher, names
- patch5_arena_names.py  the arena's bottom line names each side by its color (was always "Blue ... Red")
- patch6_names.py   "vs Sam and the computer" in the online bar; battle messages name the right person

Build: run each patch in order on index.html from commit 2e1d210:  python3 patchN_*.py index.html
(patch5 also rewrites arena.html from the arena embedded in index.html and re-embeds it).

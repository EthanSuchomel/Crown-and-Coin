Mythical movement (Ethan, 2026-11-17): "the mage can only move one hex per action", "only mages can capture castles and the
areas that minions move to are not captures hexes. Everything but minions can capture hexes but only mages can capture castles."
- Mages: 1 hex per move (no 2-hex moves through your own land either, and 1 hex in a Fortify regroup).
- Minions: still up to 2 hexes, but only onto your own land. A move into new land (or an attack) needs a unit that isn't a
  Minion; a castle needs a Mage. Minions can go along with them. Exception: an enemy Floating Castle only takes flyers.
- A picked group that lacks the needed unit: the browser's Move sheet keeps the button off and says what's needed; the
  computer (and Godot's sheet) adds the strongest such unit from the hex. A castle attack that loses its Mage in the battle
  still takes the castle if it wins.
Browser: patch_moves.py (fastUnit, mythNeed, mythHas, moveFilter, moveTargets, executeMove, openMove, texts).
Godot: port_godot.py -> godot/ (game_state.gd: fast_unit, myth_need, myth_has, move_filter, move_targets, _move_sel,
execute_move; main.gd texts and the Move sheet note).
Tested: rule checks in both, computer games with the Mythical in both.

Computer fix (Ethan, 2026-11-17: Expert Mythical "didnt capture a castle and it didnt try and fight me"): it spent its moves
marching big Minion stacks around its own land (a march was scored by the stack's size) and attacked with 1 Minotaur + 1 Minion.
Now Minions count 20% when scoring a march, and Mages are walked up to castles they can take and along with the army.
Browser patch_ai.py; Godot ai_player.gd move_score. Tests (20-40 rounds, Expert Mythical vs Hard): Godot 6 games, castles 1-3,
2 wins by taking the home castle, 1 loss; browser 6 games, 1-13 hexes taken from the other side, up to 4 castles held.

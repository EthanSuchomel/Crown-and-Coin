The castle hex grounds (browser commit 5946b18) ported to the Godot version, 2026-11-12 (night).
  p1_ground.py PROJECT   scripts/ui/board_view.gd: loads art/terrain/gnd_<faction>.png, _castle_gnd(t) (follows the
                         castle picture: a home castle shows its owner's ground, any other castle the neutral one,
                         which doesn't exist yet), draws it over the grass, and leaves the team colour wash off.
  pictures               dev/castle-ground/tiles/gnd_{dinos,robots,mammals,mythical}.png -> art/terrain/
  check/shots_ground.gd  3-player boards (Mammals or Mythical against Robots and Dinosaurs), screenshots to SHOTS;
                         run under xvfb-run with --rendering-driver opengl3.
Written into Ethan's project through the file bridge; the old board_view.gd is in _backup_before_castle_ground/.

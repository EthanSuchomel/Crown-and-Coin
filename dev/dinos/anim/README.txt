Dinosaur walk + attack animations (work in progress, 2026-11-06; not in the game yet).
anim.py builds sheet_<unit>_<side>.png from the full-size cut-outs (<unit>_<side>.png):
frame 0 standing, 1-8 walk, then the attack frames. Run: python3 anim.py [units...]
Leg rig: 2-bone IK per leg (hip/knee from the UNITS table), feet planted in stance, the swing
fades in below each leg's belly line ("top"). Attacks bend the head (Stegosaurus: tail).
Still to do: wire the sheets into arena.html (sheetClass, walkSheet, runFrames 8, atkFrames 9,
atkSteps from sheets_meta.txt; w and ratio change because of the padding), check in battle, publish.

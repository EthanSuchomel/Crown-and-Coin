# Godot fix (Ethan, 2026-11-11): unit pictures in text (hex details, battle results, the regroup and move lists) were
# squeezed into a fixed 30 x 20 box, so the square Mythical pictures came out stretched. Now only the height is set
# and each picture keeps its own shape.
import sys
F = sys.argv[1] + '/scripts/ui/main.gd'
s = open(F, encoding='utf-8').read()
n = s.count('[img=30x20]res://art/units/')
assert n == 3, n
s = s.replace('[img=30x20]res://art/units/', '[img height=22]res://art/units/')
open(F, 'w', encoding='utf-8').write(s); print('unit icons ok', n)

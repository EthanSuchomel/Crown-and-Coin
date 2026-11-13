"""Ethan, 2026-11-12: the numbers box moves to the board's bottom-right corner. Usage: python3 p4_right.py PROJ"""
import sys
from common import F
f = F(sys.argv[1] + '/scripts/ui/main.gd')
f.rep('''    sbox.border_width_left = 0
    sbox.border_width_bottom = 0
    sbox.corner_radius_top_left = 0
    sbox.corner_radius_bottom_left = 0
    sbox.corner_radius_bottom_right = 0''', '''    sbox.border_width_right = 0
    sbox.border_width_bottom = 0
    sbox.corner_radius_top_right = 0
    sbox.corner_radius_bottom_left = 0
    sbox.corner_radius_bottom_right = 0''')
f.rep('''    sp.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
    sp.grow_vertical = Control.GROW_DIRECTION_BEGIN''', '''    sp.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)   # the board's bottom-right corner (Ethan)
    sp.grow_vertical = Control.GROW_DIRECTION_BEGIN
    sp.grow_horizontal = Control.GROW_DIRECTION_BEGIN''')
f.rep("# left: the framed board, your numbers in its bottom-left corner", "# left: the framed board, your numbers in its bottom-right corner", raw=False)
f.rep("Tap the materials line in the map's bottom-left corner", "Tap the materials line in the map's bottom-right corner", raw=True)
f.save(); print('ok')

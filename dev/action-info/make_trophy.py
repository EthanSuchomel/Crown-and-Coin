"""A small pixel-art gold trophy (16x16, drawn x4 = 64x64), the mark for each upgrade on an action."""
from PIL import Image
import sys
G = {'o': (42, 29, 5, 255), 'g': (239, 193, 90, 255), 'h': (255, 236, 160, 255), 'd': (201, 149, 47, 255), 's': (150, 100, 25, 255)}
art = [
"................",
"..oooooooooooo..",
".oohgggggggddoo.",
"oo.ohggggggdo.oo",
"o..ohggggggdo..o",
"o..ohggggggdo..o",
"oo.ohggggggdo.oo",
".oo.ohggggdo.oo.",
"....oohgggdoo...",
".....oohgdoo....",
"......ogdso.....",
"......ogdso.....",
".....oohgdoo....",
"....ohggggddo...",
"....oooooooooo..",
"................",
]
im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
for y, row in enumerate(art):
    for x, c in enumerate(row):
        if c in G: im.putpixel((x, y), G[c])
im.resize((64, 64), Image.NEAREST).save(sys.argv[1] if len(sys.argv) > 1 else 'trophy.png')

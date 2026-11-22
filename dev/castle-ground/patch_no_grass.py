"""Ethan, 2026-11-22: home castles didn't quite cover the grass. Every hex sits on its own oversized grass patch (so
neighbours blend); under a castle drawn on its own ground that patch stuck out past the hex as a green fringe (most
visible at the map's edge). A hex drawn on a castle ground no longer gets the grass patch. Usage: python3 patch_no_grass.py index.html"""
import sys
P = sys.argv[1]; s = open(P).read()
a = "    grs+=`<use href=\"#sgr-${(Math.imul(i+5,2654435761)>>>7)%HEX_TERRAIN.grass.length}\" x=\"${sx}\" y=\"${sy}\"/>`;"
assert s.count(a) == 1
s = s.replace(a, "    if(!gnd) grs+=`<use href=\"#sgr-${(Math.imul(i+5,2654435761)>>>7)%HEX_TERRAIN.grass.length}\" x=\"${sx}\" y=\"${sy}\"/>`;   // not under a castle's own ground: it would show as a green fringe")
open(P, 'w').write(s); print('ok')

"""Ethan, 2026-11-23: Minions are 2 for 1 magic (were 3). Every price, button (+2, +10, All) and text reads MYTH.minionPack.
Usage: python3 patch_price.py index.html"""
import sys
P = sys.argv[1]; s = open(P).read()
a = "chMage:2, chCastle:5, minionPack:3,"
assert s.count(a) == 1
s = s.replace(a, "chMage:2, chCastle:5, minionPack:2,")   # Minions: 2 for 1 magic (Ethan, 2026-11-23; was 3)
open(P, 'w').write(s); print('ok')

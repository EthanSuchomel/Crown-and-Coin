"""Ethan, 2026-11-24: his second pick for the up-and-down wall (as the browser's patch_wallv2.py).
Usage: python3 p18_wallv2.py PROJ"""
import sys, shutil, os, json, re
sys.path.insert(0, __file__.rsplit('/', 2)[0] + '/godot-port-nov22')
from common import F
P = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
shutil.copy(os.path.join(here, 'files/art/walls/wall_v.png'), P + '/art/walls/wall_v.png')
V = json.load(open(os.path.join(here, '..', 'castle-walls', 'art', 'walls.json')))['v']
b = F(P + '/scripts/ui/board_view.gd')
s = b.s
i = s.index('const WALL_V := '); j = s.index('\n', i)
s = s[:i] + 'const WALL_V := ' + json.dumps(V) + s[j:]
s, n = re.subn(r'const WALL_VW := [0-9.]+', 'const WALL_VW := 0.9', s); assert n == 1
b.s = s; b.save(); print('ok')

"""Ethan, 2026-11-24: "let's try this wall for the sides instead": his second pick from the OpenArt up-and-down walls
(a wider walkway between two rows of merlons), straightened like the first (art/wall_v.png re-cut), width .9.
Usage: python3 patch_wallv2.py index.html"""
import sys, os, json, base64, io
from PIL import Image
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
here = os.path.dirname(os.path.abspath(__file__))
V = json.load(open(os.path.join(here, 'art', 'walls.json')))['v']
im = Image.open(os.path.join(here, 'art', 'wall_v.png')); b = io.BytesIO(); im.save(b, 'WEBP', lossless=True)
V['uri'] = 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
i = s.index("WALL_ART.v={"); j = s.index(";   // the wall running straight up and down", i)
s = s[:i] + "WALL_ART.v=" + json.dumps(V) + s[j:]
import re
s, n = re.subn(r"const WALL_VW=[0-9.]+;", "const WALL_VW=0.9;", s); assert n == 1
open(p, 'w', encoding='utf-8').write(s); print('ok')

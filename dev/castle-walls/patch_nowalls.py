"""Ethan, 2026-11-24 (afternoon): "scratch the wall mechanic. Go back to the hex neutral castle with the walls, but
remove the ballistas when a battle happens." Walls can't be built any more (WALLS_ON false: no Walls button, the
computer doesn't build them, Advancements texts drop them); the neutral castle is the old whole-hex tile with its own
walls again (the keep picture is no longer used); a castle battle is always on the Castle map (still no ballistas).
Usage: python3 patch_nowalls.py index.html"""
import sys, re
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (c, a[:120]); s = s.replace(a, b)
rep("const WALL_HP=3, WALL_COSTS=[3,3,2,2];", "const WALLS_ON=false;   // Ethan, 2026-11-24: no building walls\nconst WALL_HP=3, WALL_COSTS=[3,3,2,2];")
rep("  if(t.owner!==pid||!wallSides(i).includes(j)||was>=WALL_HP||matOf(pid)<price) return false;", "  if(!WALLS_ON||t.owner!==pid||!wallSides(i).includes(j)||was>=WALL_HP||matOf(pid)<price) return false;")
rep("      return (matOf(0)>=wallCost(lvl)||freeWallsLeft(0)>0)&&wallSides(t.id).some(j=>wallOn(t.id,j)<WALL_HP);", "      return WALLS_ON&&(matOf(0)>=wallCost(lvl)||freeWallsLeft(0)>0)&&wallSides(t.id).some(j=>wallOn(t.id,j)<WALL_HP);")
rep("and can still upgrade a barracks, start a trebuchet or build walls.`", "and can still upgrade a barracks${WALLS_ON?', start a trebuchet or build walls':' or start a trebuchet'}.`")
rep("""      ...[],
      {k:'walls', img:ART.icons.wall, name:'Walls',""", """      ...[],
      ...(WALLS_ON?[{k:'walls', img:ART.icons.wall, name:'Walls',""")
rep("""        label:freeWallsLeft(0)>0?`Build walls: ${freeWallsLeft(0)} free (Reforest), then ${matTxt(wc)} each`:`Build walls, ${matTxt(wc)} each`},
    ];""", """        label:freeWallsLeft(0)>0?`Build walls: ${freeWallsLeft(0)} free (Reforest), then ${matTxt(wc)} each`:`Build walls, ${matTxt(wc)} each`}]:[]),
    ];""")
s, n = re.subn(r", or build walls on a hex's sides \(\$\{matTxt\(wallCost\(lvl\)\)\} each\)`", "`", s); assert n == 1
s, n = re.subn(r", or build walls on a hex's sides \(\$\{wallCost\(lvl\)\} each\)`", "`", s); assert n == 1
# back to the old neutral castle tile
s, n = re.subn(r"\nART\.castle_neutral=\{uri:'data:image/webp;base64,[^']*',ratio:[0-9.]+\};[^\n]*", "", s); assert n == 1
rep("const castleTile=t=>false;   // the neutral castle stands on the grass since 2026-11-24 (it was a whole-hex tile)", "const castleTile=t=>!!(t.castle&&castleArt(t)==='neutral'&&HEX_TERRAIN.castle_neutral);")
rep("const castleW=f=>f==='mythical'?26:f==='neutral'?19:", "const castleW=f=>f==='mythical'?26:")
rep("y=\"${(cy-ch*(f==='neutral'?0.58:0.5)).toFixed(2)}\"", "y=\"${(cy-ch/2).toFixed(2)}\"")
# a castle battle: always the Castle map
rep("const arenaMap=(t,w)=>t.castle?((w==null||w>0)?'castle':'open'):   // a castle with no wall on the attacked side: the Open field (2026-11-24)\n  ", "const arenaMap=(t,w)=>t.castle?'castle':")
open(p, 'w', encoding='utf-8').write(s); print('ok')

"""Grass and mountains as hex tiles (Ethan, 2026-11-16).
  - Every hex is drawn on its own grass tile, cut to the hex, in place of one grass texture repeated over the map.
    Three tiles (different parts of the texture) are picked by hex number.
  - A mountain hex is drawn with a mountain tile that fills the whole hex, in place of the mountain picture standing
    on the grass. The terrain icon in the key and the help uses the new tile too.
python3 patch_terrain.py index.html tiles/   (re-running replaces the tiles)"""
import sys, os, re, base64

p, d = sys.argv[1], sys.argv[2]
s = open(p, encoding='utf-8').read()
uri = lambda f: 'data:image/png;base64,' + base64.b64encode(open(os.path.join(d, f), 'rb').read()).decode()
grass = sorted(f for f in os.listdir(d) if re.fullmatch(r'grass_\d\.png', f))
line = ('/*HEX_TERRAIN*/const HEX_TERRAIN={"grass":[' + ','.join('"%s"' % uri(f) for f in grass) + '],"mountain":"%s","castle_neutral":"%s"};' % (uri('mountain.png'), uri('castle_neutral.png'))
        + '   // hex-shaped tiles (222x256): the grass under every hex, and the mountain hex\n')


def rep(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new)


if '/*HEX_TERRAIN*/' in s:
    s = re.sub(r'/\*HEX_TERRAIN\*/const HEX_TERRAIN=\{.*?\};[^\n]*\n', lambda m: line, s, count=1, flags=re.S)
else:
    i = s.index('/*CASTLE_GND*/const CASTLE_GND=')
    s = s[:i] + line + s[i:]
    rep("  for(const f in CASTLE_GND) d+=img('gd-'+f,CASTLE_GND[f],+(GND_R*Math.sqrt(3)).toFixed(2),2*GND_R,0);   // castle hex grounds\n",
        "  for(const f in CASTLE_GND) d+=img('gd-'+f,CASTLE_GND[f],+(GND_R*Math.sqrt(3)).toFixed(2),2*GND_R,0);   // castle hex grounds\n"
        "  HEX_TERRAIN.grass.forEach((g,k)=>{ d+=img('gr-'+k,g,+(GND_R*Math.sqrt(3)).toFixed(2),2*GND_R,0); });   // each hex's own grass tile\n"
        "  d+=img('mth',HEX_TERRAIN.mountain,+(GND_R*Math.sqrt(3)).toFixed(2),2*GND_R,0);   // the mountain hex\n")
    rep("    h+=`<g class=\"cell\" data-id=\"${i}\"><polygon points=\"${hexPts(cx,cy,HR+.3)}\" fill=\"url(#grassPat)\"/>`;\n",
        "    // every hex sits on its own grass tile (one of three, by hex number, so neighbours don't match)\n"
        "    const gx=(cx-GND_R*Math.sqrt(3)/2).toFixed(2), gy=(cy-GND_R).toFixed(2);\n"
        "    h+=`<g class=\"cell\" data-id=\"${i}\"><polygon points=\"${hexPts(cx,cy,HR+.3)}\" fill=\"#2f7d22\"/>`;\n"
        "    if(t.terrain!=='mountain') h+=`<use class=\"ico\" href=\"#gr-${(Math.imul(i+5,2654435761)>>>7)%HEX_TERRAIN.grass.length}\" x=\"${gx}\" y=\"${gy}\"/>`;\n")
    rep("    if(t.terrain==='mountain') h+=`<use class=\"ico\" href=\"#mt\" x=\"${(cx-MW/2).toFixed(2)}\" y=\"${(cy+10-MH).toFixed(2)}\"/>`;\n",
        "    if(t.terrain==='mountain') h+=`<use class=\"ico\" href=\"#mth\" x=\"${gx}\" y=\"${gy}\"/>`;   // the whole hex is mountain\n")
    rep("css+=`.px-t-mountain{background-image:url(${ART.mountain_img.uri});image-rendering:auto}",
        "css+=`.px-t-mountain{background-image:url(${HEX_TERRAIN.mountain});background-size:contain;background-repeat:no-repeat;background-position:center;image-rendering:auto}")
if '/*CASTLE_TILE*/' not in s:
    # neutral castles (2026-11-16): Ethan's OpenArt castle fills the hex, in place of the stone castle picture on grass
    rep("  d+=img('mth',HEX_TERRAIN.mountain,+(GND_R*Math.sqrt(3)).toFixed(2),2*GND_R,0);   // the mountain hex\n",
        "  d+=img('mth',HEX_TERRAIN.mountain,+(GND_R*Math.sqrt(3)).toFixed(2),2*GND_R,0);   // the mountain hex\n"
        "  d+=img('ctn',HEX_TERRAIN.castle_neutral,+(GND_R*Math.sqrt(3)).toFixed(2),2*GND_R,0);   // /*CASTLE_TILE*/ the neutral castle hex\n")
    rep("const castleGnd=t=>{",
        "const castleTile=t=>!!(t.castle&&castleArt(t)==='neutral'&&HEX_TERRAIN.castle_neutral);   // a neutral castle is one tile filling its hex\nconst castleGnd=t=>{")
    rep("    if(t.terrain==='mountain') h+=`<use class=\"ico\" href=\"#mth\" x=\"${gx}\" y=\"${gy}\"/>`;   // the whole hex is mountain\n",
        "    if(t.terrain==='mountain') h+=`<use class=\"ico\" href=\"#mth\" x=\"${gx}\" y=\"${gy}\"/>`;   // the whole hex is mountain\n"
        "    const ctile=castleTile(t); if(ctile) h+=`<use class=\"ico\" href=\"#ctn\" x=\"${gx}\" y=\"${gy}\"/>`;   // the neutral castle hex\n")
    rep("      if(!gnd) h+=`<polygon class=\"ico\" points=\"${hexPts(cx,cy,HR)}\" fill=\"${col}\" opacity=\".2\"/>`;",
        "      if(!gnd&&!ctile) h+=`<polygon class=\"ico\" points=\"${hexPts(cx,cy,HR)}\" fill=\"${col}\" opacity=\".2\"/>`;")
    rep("    if(t.castle){\n      const f=castleArt(t), w=castleW(f), ch=w*ART['castle_'+f].ratio;\n      castles+=",
        "    if(t.castle&&!castleTile(t)){\n      const f=castleArt(t), w=castleW(f), ch=w*ART['castle_'+f].ratio;\n      castles+=")
open(p, 'w', encoding='utf-8').write(s)
print('patched;', len(grass), 'grass tiles')

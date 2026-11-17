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
soft = lambda f: uri(f.replace('.png', '_soft.png'))
line = ('/*HEX_TERRAIN*/const HEX_TERRAIN={"grass":[' + ','.join('"%s"' % uri(f) for f in grass) + '],"mountain":"%s","castle_neutral":"%s","forest":"%s","fern":"%s",' % (uri('mountain.png'), uri('castle_neutral.png'), uri('forest.png'), uri('fern.png'))
        + '"soft":{"scale":1.10,"grass":[' + ','.join('"%s"' % soft(f) for f in grass) + '],"mountain":"%s","forest":"%s","fern":"%s","water":"%s"}};' % (soft('mountain.png'), soft('forest.png'), soft('fern.png'), soft('water.png'))
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
if '/*GROVE_TILES*/' not in s:
    # forest and fern hexes (2026-11-16): Ethan's own trees and ferns built into whole-hex tiles in OpenArt, in place of
    # the trees and ferns placed one by one over the grass
    rep("  d+=img('ctn',HEX_TERRAIN.castle_neutral,",
        "  d+=img('fot',HEX_TERRAIN.forest,+(GND_R*Math.sqrt(3)).toFixed(2),2*GND_R,0)+img('fnt',HEX_TERRAIN.fern,+(GND_R*Math.sqrt(3)).toFixed(2),2*GND_R,0);   // /*GROVE_TILES*/ forest and fern hexes\n"
        "  d+=img('ctn',HEX_TERRAIN.castle_neutral,")
    rep("    if((t.forest||t.fern)&&t.owner<0) h+=forestSvg(cx,cy,i);\n",
        "    if(t.forest||t.fern) h+=`<use class=\"ico\" href=\"#${t.forest?'fot':'fnt'}\" x=\"${gx}\" y=\"${gy}\"/>`;   // the whole hex is forest / ferns\n")
    rep("      if(t.forest||t.fern) h+=forestSvg(cx,cy,i);\n", "")
    rep("    if(t.fern) trees+=fernPatch(cx,cy,i);\n    if(t.forest) trees+=forestTrees(cx,cy,i);", "")
if '/*SOFT_TILES*/' not in s:
    # soft edges (Ethan, 2026-11-17: "everything looks very choppy now... flow together better"): grass, mountain, forest
    # and fern tiles fade out over a ragged band and are drawn 10% bigger than the hex, so neighbours overlap and blend.
    # The board draws in layers so the overlaps stack right: the clickable hexes, then every hex's grass, then the
    # mountain/forest/fern tiles with the water, castle grounds and castle tile, then the owner's tint and borders.
    rep("  d+=img('ctn',HEX_TERRAIN.castle_neutral,",
        "  { const sw=+(GND_R*Math.sqrt(3)*HEX_TERRAIN.soft.scale).toFixed(2), sh=+(2*GND_R*HEX_TERRAIN.soft.scale).toFixed(2);   // /*SOFT_TILES*/ the soft-edged tiles\n"
        "    HEX_TERRAIN.soft.grass.forEach((g,k)=>{ d+=img('sgr-'+k,g,sw,sh,0); });\n"
        "    for(const k of ['mountain','forest','fern']) d+=img('s-'+k,HEX_TERRAIN.soft[k],sw,sh,0); }\n"
        "  d+=img('ctn',HEX_TERRAIN.castle_neutral,")
    i0 = s.index("    // every hex sits on its own grass tile (one of three, by hex number, so neighbours don't match)\n")
    i1 = s.index("    if(owned){\n", i0)
    s = s[:i0] + r"""    // every hex is clickable; its pictures go in the layers above (soft-edged, so neighbours blend into each other)
    const gx=(cx-GND_R*Math.sqrt(3)/2).toFixed(2), gy=(cy-GND_R).toFixed(2);
    const SK=HEX_TERRAIN.soft.scale, sx=(cx-GND_R*Math.sqrt(3)*SK/2).toFixed(2), sy=(cy-GND_R*SK).toFixed(2);
    h+=`<g class="cell" data-id="${i}"><polygon points="${hexPts(cx,cy,HR+.3)}" fill="#2f7d22"/>`;
    const gnd=castleGnd(t);   // a castle's hex is drawn with that castle's ground (the Mythical's: a black drop into nothing)
    const ctile=castleTile(t), whole=t.terrain==='mountain'?'mountain':t.forest?'forest':t.fern?'fern':'';
    // every hex sits on its own grass (one of three, by hex number, so neighbours don't match); it shows round the edges of the rest
    grs+=`<use href="#sgr-${(Math.imul(i+5,2654435761)>>>7)%HEX_TERRAIN.grass.length}" x="${sx}" y="${sy}"/>`;
    if(gnd) terr+=`<use href="#gd-${gnd}" x="${gx}" y="${gy}"/>`;
    if(t.terrain==='water') terr+=`<use href="#wa" x="${(cx-HH/2).toFixed(2)}" y="${(cy-HR).toFixed(2)}"/>`;
    if(whole) terr+=`<use href="#s-${whole}" x="${sx}" y="${sy}"/>`;   // the whole hex is mountain / forest / ferns
    if(ctile) terr+=`<use href="#ctn" x="${gx}" y="${gy}"/>`;   // the neutral castle hex
""" + s[i1:]
    rep("      if(!gnd&&!ctile) h+=`<polygon class=\"ico\" points=\"${hexPts(cx,cy,HR)}\" fill=\"${col}\" opacity=\".2\"/>`;",
        "      if(!gnd&&!ctile) own+=`<polygon points=\"${hexPts(cx,cy,HR)}\" fill=\"${col}\" opacity=\".2\"/>`;")
    j0 = s.index("      nbrDirs(i).forEach((j,k)=>{\n        if(j>=0&&S.tiles[j].owner===t.owner) return;")
    j1 = s.index("      });\n", j0)
    s = s[:j0] + s[j0:j1].replace("        h+=`<line", "        own+=`<line") + s[j1:]
    rep("  let h='', marks='', castles='', tops='', walls='', trees='';", "  let h='', marks='', castles='', tops='', walls='', trees='', grs='', terr='', own='';")
    rep("  $('#cells').innerHTML=h;", "  $('#cells').innerHTML=h; $('#grs').innerHTML=grs; $('#terr').innerHTML=terr; $('#own').innerHTML=own;")
    rep('d+=`</defs><g id="cells"></g><path class="ico" d="${grid}" stroke="#060907" stroke-width=".7" opacity=".45" fill="none"/>',
        'd+=`</defs><g id="cells"></g><g id="grs" class="ico"></g><g id="terr" class="ico"></g><g id="own" class="ico"></g><path class="ico" d="${grid}" stroke="#060907" stroke-width=".6" opacity=".16" fill="none"/>')
if '/*BEACH_WATER*/' not in s:
    # water (Ethan, 2026-11-17: "change the water tile to have a beach instead of rocks"): the OpenArt beach lake, soft-edged
    rep("    for(const k of ['mountain','forest','fern']) d+=img('s-'+k,HEX_TERRAIN.soft[k],sw,sh,0); }",
        "    for(const k of ['mountain','forest','fern','water']) d+=img('s-'+k,HEX_TERRAIN.soft[k],sw,sh,0); }   // /*BEACH_WATER*/")
    rep("    if(t.terrain==='water') terr+=`<use href=\"#wa\" x=\"${(cx-HH/2).toFixed(2)}\" y=\"${(cy-HR).toFixed(2)}\"/>`;\n",
        "    if(t.terrain==='water') terr+=`<use href=\"#s-water\" x=\"${sx}\" y=\"${sy}\"/>`;   // the beach lake\n")
open(p, 'w', encoding='utf-8').write(s)
print('patched;', len(grass), 'grass tiles')

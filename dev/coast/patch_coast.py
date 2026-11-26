"""Ethan, 2026-11-26: the iPad (browser) version gets the Godot version's sea and beach round the maps.
Usage: python3 patch_coast.py index.html"""
import sys, os
p=sys.argv[1]; D=os.path.dirname(os.path.abspath(__file__))
s=open(p,encoding='utf8').read()
def rep(a,b,n=1):
    global s
    c=s.count(a); assert c==n,(c,a[:100]); s=s.replace(a,b)
JS=open(D+'/coast.js',encoding='utf8').read()
rep("function initMap(){\n", JS+"function initMap(){\n")
rep("""  d+=`</defs><g id="cells"></g><g id="grs" class="ico"></g><g id="terr" class="ico"></g>""",
    """  const OT=150;   // the open sea's tile, board units
  d+=`<pattern id="oceanPat" width="${OT}" height="${OT}" patternUnits="userSpaceOnUse"><image href="${oceanTile()}" width="${OT}" height="${OT}" preserveAspectRatio="none"/></pattern>`;
  d+=`</defs><rect x="-3000" y="-3000" width="6000" height="6000" fill="url(#oceanPat)" style="pointer-events:none"/><g id="cells"></g><g id="grs" class="ico"></g><g class="ico">${coastSvg('lo')}</g><g id="terr" class="ico"></g><g class="ico">${coastSvg('hi')}</g>""")
rep("const VB_M=HM-1.4,","const VB_M=HM-7,")   # room round the board for the beach, now outside the hexes
open(p,'w',encoding='utf8').write(s); print('coast ok')

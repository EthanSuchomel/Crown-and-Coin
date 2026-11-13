"""Mammal rework, step 1 (2026-11-12):
- Ethan's new Mammal home castle: the siege-ready waterfall mesa (OpenArt), cut out by castle_cut.py.
- The board's Mammal numbers brought back in line with the arena (they were changed on the claude.ai link on Nov 7 and
  lost when the link was replaced by this repo's version on Nov 9): Rhino damage 12 (Ethan, Nov 8), Porcupine 8 health
  with quills that prick melee attackers for 1, and no Procoptodon in the Mammal barracks.
python3 dev/mammal-castle/patch_castle.py index.html castle_256.png"""
import sys, base64, io, re
from PIL import Image

p, art = sys.argv[1], sys.argv[2]
s = open(p, encoding='utf-8').read()


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (old[:80], n)
    s = s.replace(old, new)


# 1. the castle picture
im = Image.open(art)
bio = io.BytesIO(); im.save(bio, 'PNG', optimize=True)
uri = 'data:image/png;base64,' + base64.b64encode(bio.getvalue()).decode()
ratio = round(im.height / im.width, 4)
m = re.search(r'/\*MAMMAL_ART\*/const MAMMAL_ART=\{"castle": \{"uri": "(data:image/png;base64,[A-Za-z0-9+/=]+)", "ratio": ([0-9.]+)\}', s)
assert m
s = s[:m.start(1)] + uri + s[m.end(1):m.start(2)] + str(ratio) + s[m.end(2):]
rep("// the Mammals' castle, Den (barracks), Crag Roost (fort) and market tent, from Ethan's OpenArt pictures; the Watering Hole is a stand-in",
    "// the Mammals' castle (the war-fortress waterfall mesa, 2026-11-12), Den (barracks), Crag Roost (fort) and market tent, from Ethan's OpenArt pictures; the Watering Hole is a stand-in")

# 2. Porcupine: 8 health, quills prick melee attackers for 1
rep("porc:   {name:'Porcupine',hp:16,dmg:4,rate:1.2,cost:6,rank:2,rng:true,aa:true,basic:true,missAir:.2,hk:'archer',mammal:true}",
    "porc:   {name:'Porcupine',hp:8,dmg:4,rate:1.2,cost:6,rank:2,rng:true,aa:true,basic:true,missAir:.2,hk:'archer',thorns:1,mammal:true}")
rep("porc:'Shooter: quills, like Archer arrows. Hits flyers (misses 20%)'",
    "porc:'Shooter: quills, like Archer arrows. Hits flyers (misses 20%). Its quills prick back: a melee attacker that lands a hit on it takes 1 damage'")
# 3. Rhino damage 12, as in the arena (Ethan, 2026-11-08)
rep("rhino:  {name:'Rhino',hp:28,dmg:15,", "rhino:  {name:'Rhino',hp:28,dmg:12,")
# 4. no Procoptodon (Ethan, 2026-11-07); its numbers stay in UNIT_STATS so old saved games still load
rep("['rhino','Rhino','Rhino'],['kanga','Procoptodon','Procoptodon']],", "['rhino','Rhino','Rhino']],", 1)
rep("const PRICEY=new Set(['rhino','kanga','gbat','eleph']);   // the Watering Hole's units: the barracks' level 1 and 2 units, the fort's two pricier ones",
    "const PRICEY=new Set(['rhino','gbat','eleph']);   // the Watering Hole's units: the barracks' level 1 unit, the fort's two pricier ones")
rep("rhino:1,kanga:2,ptero:2", "rhino:1,ptero:2")
rep("'Unlocks the Longbow and Procoptodon'", "'Unlocks the Longbow'")
rep("(l===3?BARRACKS_LV[2]:'—')", "(l===3?BARRACKS_LV[2]:'No new unit at this level')")
rep("Rhinos, Procoptodons, Desmodus and Palaeoloxodons", "Rhinos, Desmodus and Palaeoloxodons", 4)
rep("  kanga:  {name:'Procoptodon',", "  // the Procoptodon was taken out of the game (2026-11-07); its numbers stay so old saved games still load\n  kanga:  {name:'Procoptodon',")

# 5. the quills in board battles: each melee hit landed on a Porcupine costs the attacker 1 health (a charging Rhino too)
rep("function strike(S1,S2,me,mult,round,ctx){\n  const out={dmg:{},wall:0,any:false};",
    "function strike(S1,S2,me,mult,round,ctx){\n  const out={dmg:{},wall:0,any:false,recoil:{}};   // recoil: damage back on this side's own units (Porcupine quills)")
rep("      out.dmg[tk]=(out.dmg[tk]||0)+dd; left[tk]-=dd; time-=use;\n",
    "      out.dmg[tk]=(out.dmg[tk]||0)+dd; left[tk]-=dd; time-=use;\n"
    "      // Porcupine quills: every melee hit that lands pricks the attacker for 1 (shots, lasers, rockets and magic don't)\n"
    "      if(T.thorns&&w.key&&dd>0&&!w.rng&&!w.beam&&w.hk!=='gunship'&&w.hk!=='magic'){\n"
    "        const one=hitOne({...w,shots:1,charged:false,multi:0,sweep:false,cleave:false,missAir:0,missHeavy:0},{...T,dodge:0,deflect:null},tk);\n"
    "        if(one>0) out.recoil[w.key]=(out.recoil[w.key]||0)+dd/one*T.thorns; }\n")
rep("        const per=tk==='mega'?.25:1, dd=Math.min(left[tk],pool*per); out.dmg[tk]=(out.dmg[tk]||0)+dd; left[tk]-=dd; pool-=dd/per; }",
    "        const per=tk==='mega'?.25:1, dd=Math.min(left[tk],pool*per); out.dmg[tk]=(out.dmg[tk]||0)+dd; left[tk]-=dd; pool-=dd/per;\n"
    "        if(T.thorns&&dd>0) out.recoil.rhino=(out.recoil.rhino||0)+dd/((RC.dmg+RC.next*(hits-1))/hits*m)*T.thorns; }   // trampling Porcupines pricks the Rhinos")
rep("    const w0={...U,hk:U.hk,airOnly:false};", "    const w0={...U,hk:U.hk,airOnly:false,key:k};")
rep("    apply(D,hitsOnD.dmg); apply(A,hitsOnA.dmg);\n",
    "    apply(D,hitsOnD.dmg); apply(A,hitsOnA.dmg);\n"
    "    // Porcupine quills prick back the melee attackers that hit them\n"
    "    const rcA=hitsOnD.recoil||{}, rcD=hitsOnA.recoil||{};\n"
    "    if(o.aArm) for(const k in rcA) rcA[k]/=ARMOR_HP; if(o.dArm) for(const k in rcD) rcD[k]/=ARMOR_HP;\n"
    "    apply(A,rcA); apply(D,rcD);\n")
open(p, 'w', encoding='utf-8').write(s)
print('ok', im.size, ratio, len(uri) // 1024, 'KB')

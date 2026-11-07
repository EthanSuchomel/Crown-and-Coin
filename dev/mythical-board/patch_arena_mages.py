"""Crown & Coin sends Mages by level (mage0..mage3). Each is the arena Mage with its own reach and damage
(Ethan, 2026-11-07): level 0 a quarter of the field and 5, level 1 half and 6, level 2 three quarters and 7,
level 3 the whole field and 7. They're hidden from the army controls; a board hex holds up to 3 of them.
Usage: patch_arena_mages.py IN OUT EDITS_JSON"""
import sys, json
s=open(sys.argv[1]).read(); edits=[]
def rep(old,new):
    global s
    assert s.count(old)==1,(s.count(old),old[:80]); s=s.replace(old,new); edits.append({'old_text':old,'new_text':new})
rep("const FACTIONS=['Dinosaurs','Robots','Mammals','Mythical'];",
    "// Crown & Coin's Mages by level (the board sends these): reach in field units and damage. Not in the army controls.\n"
    "[['mage0',30,5],['mage1',60,6],['mage2',90,7],['mage3',120,7]].forEach(([k,r,d])=>{ TYPES[k]={...TYPES.mage,label:'Mage',range:r,dmg:d,hidden:true,maxN:3}; ORDER.push(k); });\n"
    "const FACTIONS=['Dinosaurs','Robots','Mammals','Mythical'];")
rep("const teamKeys=t=>ORDER.filter(k=>facOf(k)===TEAM_FACTION[t]);", "const teamKeys=t=>ORDER.filter(k=>facOf(k)===TEAM_FACTION[t]&&!TYPES[k].hidden);")
rep('  mage:{"blue": "myth/mage_blue.png", "red": "myth/mage_red.png"},',
    '  mage:{"blue": "myth/mage_blue.png", "red": "myth/mage_red.png"},\n  mage0:{"blue": "myth/mage_blue.png", "red": "myth/mage_red.png"}, mage1:{"blue": "myth/mage_blue.png", "red": "myth/mage_red.png"},\n  mage2:{"blue": "myth/mage_blue.png", "red": "myth/mage_red.png"}, mage3:{"blue": "myth/mage_blue.png", "red": "myth/mage_red.png"},')
open(sys.argv[2],'w').write(s); json.dump(edits,open(sys.argv[3],'w')); print('arena ok',len(edits))

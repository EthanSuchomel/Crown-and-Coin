# Dinosaur board rework, step 8: the help text (How to play, the faction screen, card abilities) for the new Dinosaurs.
import sys
p=sys.argv[1]; s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:100]); s=s.replace(a,b)
# what the Dinosaurs get instead of forts and trebuchets, for the faction screen and How to play
rep("// a table of one faction's units, for How to play and the faction screen",
"""// the Dinosaurs' volcano and Alamosaurus guards, for How to play and the faction screen
const dinoSpecialsHtml=()=>`<img src="${ART.castle_dinos.uri}" alt="" style="height:1.3em;vertical-align:-.3em"> <b>Volcano</b>: the Dinosaurs build no forts and no trebuchets. Instead, Advancements at your home castle wake its volcano and stoke it higher: ${VOLC.map((v,i)=>`level ${i+1} (${v.cost} gold) ${volcSay(i+1)}`).join('; ')}. When it's due it erupts at the start of your turn, once, at an enemy hex with units in reach (you pick): every ${TREB_HIT} or higher does ${TREB_DMG} damage to the front of their line, and walls don't stop it. If your home castle falls, the volcano is lost.
  <img src="${UNIT_ART.alamo}" alt="" style="height:1.3em;vertical-align:-.3em"> <b>Alamosaurus guards</b>: Advancements at a barracks hire them, ${GUARD_COST} gold each, up to ${GUARD_MAX} per barracks. A guard never moves or attacks; it joins the fight whenever that hex is attacked, and can hold it on its own. Each stomp hits up to 4 enemies. A guard that dies is gone until you hire another.`;
// a table of one faction's units, for How to play and the faction screen""")
rep("  const ks=[BASIC[fid]].concat(UNITS[fid].barracks.map(x=>x[0]).filter(k=>k!==BASIC[fid]),UNITS[fid].fort.map(x=>x[0]));",
    "  const ks=[BASIC[fid]].concat(UNITS[fid].barracks.map(x=>x[0]).filter(k=>k!==BASIC[fid]),UNITS[fid].fort.map(x=>x[0]),fid==='dinos'?['alamo']:[]);")
rep("""    <h3>Your units</h3>${unitTable(fid)}
    <h3>Card abilities</h3>""","""    <h3>Your units</h3>${unitTable(fid)}
    ${fid==='dinos'?`<h3>Volcano and guards</h3><p>${dinoSpecialsHtml()}</p>`:''}
    <h3>Card abilities</h3>""")
# How to play: Advancements, barracks levels and buildings
rep("""<li><b>Advancements.</b> <span class="px px-treb" aria-hidden="true"></span> <b>Trebuchets</b> go on""",
    """<li><b>Advancements.</b> ${isDino(0)?dinoSpecialsHtml()+'\\n      ':''}${isDino(0)?'':`<span class="px px-treb" aria-hidden="true"></span> <b>Trebuchets</b> go on""")
rep("""if the enemy takes the hex they get the trebuchet, and one still being built is wrecked.
      <span class="px px-wall\"""","""if the enemy takes the hex they get the trebuchet, and one still being built is wrecked.`}
      <span class="px px-wall\"""")
rep("""<b>Barracks upgrades</b>: a new barracks trains basic units and archers; level 1 (${BARRACKS_UP[0]} gold) unlocks""",
    """<b>Barracks upgrades</b>: a new barracks trains basic units and archers; ${isDino(0)?barracksLv(0).map((d,i)=>`level ${i+1} (${BARRACKS_UP[i]} gold) ${d.charAt(0).toLowerCase()+d.slice(1)}`).join('; ')+'.':`level 1 (${BARRACKS_UP[0]} gold) unlocks""")
rep("""level 3 (${BARRACKS_UP[2]} gold) makes every unit bought on that hex cost 1 gold less.</li>""",
    """level 3 (${BARRACKS_UP[2]} gold) makes every unit bought on that hex cost 1 gold less.`}</li>""")
rep("""<span class="px px-fort" aria-hidden="true"></span> Forts for defense (and to hold a trebuchet), <span class="px px-barracks\"""",
    """${isDino(0)?'':'<span class="px px-fort" aria-hidden="true"></span> Forts for defense (and to hold a trebuchet), '}<span class="px px-barracks\"""")
# card abilities: the new roster's names, and Populate works at barracks (the Dinosaurs have no forts)
rep("""  advance:{name:'Populate',     next:'Populate: when this action starts, every fort and barracks you own gets 1 free Gallimimus',
           desc:'Populate: first, every fort and barracks you own gets 1 free Gallimimus'},""",
"""  advance:{name:'Populate',     next:'Populate: when this action starts, every barracks you own gets 1 free Pachycephalosaurus',
           desc:'Populate: first, every barracks you own gets 1 free Pachycephalosaurus'},""")
rep("""  recruit:{name:'Abundance',    next:'Abundance: Gallimimus and Dilophosaurus Archers cost 1 gold less',
           desc:'Abundance: Gallimimus and Dilophosaurus Archers cost 1 gold less'},""",
"""  recruit:{name:'Abundance',    next:'Abundance: Pachycephalosaurus and Dilophosaurus cost 1 gold less',
           desc:'Abundance: Pachycephalosaurus and Dilophosaurus cost 1 gold less'},""")
rep("""  S.tiles.forEach(t=>{ if(t.owner!==pid) return; const k=(t.fort|0)+(t.barracks|0); if(k){ addUnits(t,'galli',k,true); n+=k; ids.push(t.id); } });
  if(n) addLog(`${S.players[pid].name} populate: ${n} free Gallimimus at their forts and barracks.`,pid);""",
"""  S.tiles.forEach(t=>{ if(t.owner!==pid) return; const k=(t.barracks|0); if(k){ addUnits(t,'galli',k,true); n+=k; ids.push(t.id); } });
  if(n) addLog(`${S.players[pid].name} populate: ${n} free Pachycephalosaurus at their barracks.`,pid);""")
open(p,'w').write(s); print('patch8 ok')

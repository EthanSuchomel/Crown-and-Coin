# Dinosaur board rework: the Advancements wording for the Dinosaurs talks about guards and the volcano, not trebuchets
import sys
p=sys.argv[1]; s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:100]); s=s.replace(a,b)
rep("  if(a==='advance') return `Spend gold on as many as you can afford: upgrade a barracks (${BARRACKS_UP.join(', ')} gold for levels 1 to 3${lvl>=1?', your first level 1 free':''}), start a trebuchet",
    "  if(a==='advance'&&isDino(pid)) return `Spend gold on as many as you can afford: upgrade a barracks (${BARRACKS_UP.join(', ')} gold for levels 1 to 3${lvl>=1?', your first level 1 free':''}), hire Alamosaurus guards for a barracks (${GUARD_COST} gold each, up to ${GUARD_MAX} per barracks), wake or stoke the volcano at your home castle (${VOLC.map(v=>v.cost).join(', ')} gold for levels 1 to 3), or build walls on a hex's sides (${wallCost(lvl)} gold each)`;\n  if(a==='advance') return `Spend gold on as many as you can afford: upgrade a barracks (${BARRACKS_UP.join(', ')} gold for levels 1 to 3${lvl>=1?', your first level 1 free':''}), start a trebuchet")
rep("""        +`<li><span class="px px-${trebIc(0)}" aria-hidden="true"></span> <b>Trebuchet</b> ${TREB_COST} gold""",
    """        +(isDino(0)?`<li><img src="${UNIT_ART.alamo}" alt="" style="height:1.3em;vertical-align:-.3em"> <b>Alamosaurus guard</b> ${GUARD_COST} gold each, up to ${GUARD_MAX} per barracks${sel.barracks?` (${guardsAt(sel)} of ${GUARD_MAX*sel.barracks} here)`:''}. Guards fight only when this hex is attacked, can hold it on their own, and never move. Each stomp hits up to 4 attackers. A guard that dies is gone until you hire another</li>`
          +`<li><img src="${ART.castle_dinos.uri}" alt="" style="height:1.3em;vertical-align:-.3em"> <b>Volcano</b> at your home castle, ${VOLC.map(v=>v.cost).join(' / ')} gold for levels 1 to 3: ${volcLv(0)>=3?'fully awake':`level ${volcLv(0)+1} ${volcSay(volcLv(0)+1)}`}. At the start of your turn it rains lava on an enemy hex you choose (each 4 or more is a hit of 10 damage; walls don't stop it). Lost if your home castle falls</li>`:'')
        +(isDino(0)?'':`<li><span class="px px-${trebIc(0)}" aria-hidden="true"></span> <b>Trebuchet</b> ${TREB_COST} gold""")
rep("""ready in ${CASTLE_TREB_TURNS-(lvl>=3?1:0)} turns. Each hits an enemy hex next to it at the start of each of your turns</li>`""",
    """ready in ${CASTLE_TREB_TURNS-(lvl>=3?1:0)} turns. Each hits an enemy hex next to it at the start of each of your turns</li>`)""")
rep("""    } else h+=`<p class="hint">Tap one of your hexes to upgrade a barracks <span class="px px-barracks" aria-hidden="true"></span>, start a trebuchet""",
    """    } else if(isDino(0)) h+=`<p class="hint">Tap one of your hexes to upgrade a barracks <span class="px px-barracks" aria-hidden="true"></span> or hire its Alamosaurus guards (${GUARD_COST} gold each), tap your home castle to wake or stoke its volcano (${VOLC.map(v=>v.cost).join(' / ')} gold), or build walls (${wc} gold each). You have <b>${me.gold} gold</b>.</p>`;
    else h+=`<p class="hint">Tap one of your hexes to upgrade a barracks <span class="px px-barracks" aria-hidden="true"></span>, start a trebuchet""")
# lava bombs a touch bigger so they read on a phone
rep("c.setAttribute('r','2'); c.setAttribute('fill','#e8541a')","c.setAttribute('r','2.7'); c.setAttribute('fill','#e8541a')")
rep("core.setAttribute('r','.9'); core.setAttribute('fill','#ffd54a')","core.setAttribute('r','1.2'); core.setAttribute('fill','#ffd54a')")
open(p,'w').write(s); print('patch5b ok')

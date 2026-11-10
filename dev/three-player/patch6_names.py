# Three-player mode, step 6: names online (Ethan, 2026-11-10).
# The bar above the board says who you're playing against: both rivals in a 3-way game ("vs Sam and the computer").
# The battle messages ("Waiting for Sam to click OK…") name the person in this battle, not just the first other player.
import sys
p=sys.argv[1]; s=open(p,encoding='utf8').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:100]); s=s.replace(a,b)
rep("""Online game <b>${escH(NET.code)}</b>${NET.oppName?` · vs ${escH(NET.oppName)}`:''}</span>""",
    """Online game <b>${escH(NET.code)}</b>${netVs()?` · vs ${escH(netVs())}`:''}</span>""")
rep("""// the name of the person playing a side (by this device's numbering), if we know it""",
"""// who you're up against, for the bar above the board
function netVs(){
  if(!NET) return ''; if(!S||S.players.length<3) return NET.oppName||'';
  const ns=[1,2].map(i=>S.players[i].cpu?'the computer':(netNameOf(i)||'the '+FACTIONS[S.players[i].faction].name));
  return ns[0]==='the computer'&&ns[1]==='the computer'?'2 computers':ns.join(' and ');
}
// the person on the other side of this battle (3 players: whoever NF.peerSeat is), if we know their name
function netPeerName(){
  if(!NET) return ''; if(!S||S.players.length<3||NF.peerSeat==null) return NET.oppName||'';
  return (NET.names&&NET.names[NF.peerSeat])||'';
}
// the name of the person playing a side (by this device's numbering), if we know it""")
rep("""fightWaiting(`Waiting for ${NET.oppName?escH(NET.oppName):'the other player'} to click OK…`);""",
    """fightWaiting(`Waiting for ${netPeerName()?escH(netPeerName()):'the other player'} to click OK…`);""")
rep("""  const opp=NET.oppName?escH(NET.oppName):'The other player';""","""  const opp=netPeerName()?escH(netPeerName()):'The other player';""")
rep("""  const opp=NET&&NET.oppName?escH(NET.oppName):'the other player';""","""  const opp=netPeerName()?escH(netPeerName()):'the other player';""")
open(p,'w',encoding='utf8').write(s); print('patch6 ok')

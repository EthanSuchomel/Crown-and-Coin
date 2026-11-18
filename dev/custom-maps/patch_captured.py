"""index.html: on a hand-made map with its own castle count (maps.json "castles"), only captured castles count toward it,
not the side's own home castle (Ethan, 2026-11-17). Random maps keep the usual 4 castles, home included."""
import sys
P = sys.argv[1]; s = open(P).read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90]); s = s.replace(a, b)
rep("const winCastles=()=>S?winCastlesFor(S.players.length,S.map):CASTLES_TO_WIN;", """const winCastles=()=>S?winCastlesFor(S.players.length,S.map):CASTLES_TO_WIN;
// does the home castle count toward the win? Not on a hand-made map with its own number (only captured castles count there)
const homeCounts=()=>{ const m=S&&S.map?mapById(S.map):null; return !(m&&m.players===S.players.length&&m.castles!=null); };
const winCount=pid=>castleCount(pid)-(!homeCounts()&&S.tiles[S.homes[pid]]&&S.tiles[S.homes[pid]].owner===pid?1:0);   // castles toward the win""")
rep("const holder=S.players.map(q=>q.id).find(pid=>!S.players[pid].out&&castleCount(pid)>=need);", "const holder=S.players.map(q=>q.id).find(pid=>!S.players[pid].out&&winCount(pid)>=need);")
rep("else if(b.castle&&winCastles()&&castleCount(pid)+1>=winCastles()) castleV+=150;", "else if(b.castle&&winCastles()&&winCount(pid)+1>=winCastles()) castleV+=150;")
rep("(winCastles()&&ca[i]>=winCastles()?250:0)", "(winCastles()&&ca[i]-(homeCounts()?0:(S.tiles[S.homes[i]]&&S.tiles[S.homes[i]].owner===i?1:0))>=winCastles()?250:0)")
rep("${castleCount(p.id)}</b>`).join(' – ');", "${winCastles()&&!homeCounts()?winCount(p.id):castleCount(p.id)}</b>`).join(' – ');")
# words: say "captured castles" on those maps
for a, b in [
    ("hold ${need} castles! ${rivalsName(holder)}", "hold ${need} ${homeCounts()?'':'captured '}castles! ${rivalsName(holder)}"),
    ("You hold ${winCastles()} castles. Keep them", "You hold ${winCastles()} ${homeCounts()?'':'captured '}castles. Keep them"),
    ("hold ${winCastles()} castles. Take one back", "hold ${winCastles()} ${homeCounts()?'':'captured '}castles. Take one back"),
    ("title=\"${!winCastles()?'Castles held':`Castles held: hold ${winCastles()} to win`}\"", "title=\"${!winCastles()?'Castles held':homeCounts()?`Castles held: hold ${winCastles()} to win`:`Captured castles: hold ${winCastles()} to win`}\""),
]:
    rep(a, b)
s = s.replace("<li><b>Hold ${need} castles</b> while each rival", "<li><b>Hold ${need} captured castles</b> (not counting your home) while each rival")
s = s.replace("<li><b>Hold ${need} castles</b> for ${HOLD_TURNS} of their turns.</li>", "<li><b>Hold ${need} ${fsMap&&(mapById(fsMap)||{}).castles!=null&&(mapById(fsMap)||{}).players===fsNP?'captured castles</b> (not counting your home)':'castles</b>'} for ${HOLD_TURNS} of their turns.</li>")
s = s.replace("<b>On this map you can also win by holding ${winCastles()} castles:</b>", "<b>On this map you can also win by holding ${winCastles()} captured castles</b> (your home doesn't count):")
s = s.replace("<li><b>Hold ${winCastles()} castles.</b> When a side holds ${winCastles()} castles,", "<li><b>Hold ${winCastles()} ${homeCounts()?'':'captured '}castles${homeCounts()?'':' (not counting your home)'}.</b> When a side holds ${winCastles()} ${homeCounts()?'':'captured '}castles,")
open(P, 'w').write(s); print('patched')

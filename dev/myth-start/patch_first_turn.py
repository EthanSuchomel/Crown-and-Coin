"""Ethan, 2026-11-22: the Mythical open their first turn with 5 magic. They start with 5 (plus the usual catch-up if they
move later) and collect nothing on their very first turn; the Floating Castle's magic starts on turn 2.
Usage: python3 patch_first_turn.py index.html"""
import sys
P = sys.argv[1]; s = open(P).read()
def rep(a, b):
    global s; assert s.count(a) == 1, a[:80]; s = s.replace(a, b)
rep("  p.gold=MYTH.startMagic+catchUp(i,MYTH.secondMagic,S.players.length); p.mlv=0; p.clv=0;",
    "  p.gold=MYTH.startMagic+catchUp(i,MYTH.secondMagic,S.players.length); p.mlv=0; p.clv=0; p.mythFirst=true;   // no magic collected on the first turn (Ethan)")
rep("function beginTurn(){\n  const p=cur(), inc=incomeOf(p.id);",
    "function beginTurn(){\n  const p=cur(), inc=incomeOf(p.id);\n  if(p.mythFirst){ p.mythFirst=false; inc.total=0; inc.home=0; inc.treeM=0; }   // the Mythical's first turn: they open with their starting 5 magic")
rep("      <li><b>Floating Castle</b> (home): ${MYTH.castleMagic[0]} magic and ${MYTH.minions[0]} Minions every turn.",
    "      <li><b>Start</b> with ${MYTH.startMagic} magic; the Floating Castle's magic starts on your second turn.</li>\n      <li><b>Floating Castle</b> (home): ${MYTH.castleMagic[0]} magic and ${MYTH.minions[0]} Minions every turn.")
open(P, 'w').write(s); print('ok')

s = open(P).read()
a = "  if(p.mythFirst){ p.mythFirst=false; inc.total=0; inc.home=0; inc.treeM=0; }"
assert s.count(a) == 1
s = s.replace(a, "  const mythFirst=!!p.mythFirst;\n  if(p.mythFirst){ p.mythFirst=false; inc.total=0; inc.home=0; inc.treeM=0; }")
a = "  addLog(`${p.name} collect ${inc.total} ${cur$(p.id)}${tm?` and ${matTxt(tm)}`:''}.`,p.id);"
assert s.count(a) == 1
s = s.replace(a, "  if(mythFirst) addLog(`${p.name} begin with ${p.gold} magic; the Floating Castle's magic starts next turn.`,p.id); else\n" + a)
open(P, 'w').write(s); print('ok2')

"""Minion (Ethan, 2026-11-17): 0.5 damage every 2 s (was 2), speed 60 (was 70; arena field units 3.24, was 3.78), and the
Floating Castle's free Minions per round 1 / 3 / 5 / 8 by castle level (was 5 / 7 / 9 / 11). Browser index.html and arena.html."""
import sys
def fix(P, pairs):
    s = open(P).read()
    for a, b, n in pairs:
        assert s.count(a) == n, (P, s.count(a), a[:80]); s = s.replace(a, b)
    open(P, 'w').write(s)
ARENA = ("minion:{label:'Minion',faction:'Mythical',cost:1,hp:5,dmg:2,rate:2.0,range:3.5,speed:3.78,", "minion:{label:'Minion',faction:'Mythical',cost:1,hp:5,dmg:0.5,rate:2.0,range:3.5,speed:3.24,", 1)
fix(sys.argv[1], [ARENA,
  ("  minion:  {name:'Minion',hp:5,dmg:2,rate:2.0,cost:1,rank:0,basic:true,hk:'melee'},", "  minion:  {name:'Minion',hp:5,dmg:0.5,rate:2.0,cost:1,rank:0,basic:true,hk:'melee'},", 1),
  ("castleUp:[10,15,20], minions:[5,7,9,11],", "castleUp:[10,15,20], minions:[1,3,5,8],", 1),
  ("magic and +2 Minions each. Only flyers can attack it.", "magic and ${MYTH.minions.slice(1).join(', ')} Minions. Only flyers can attack it.", 1)])
fix(sys.argv[2], [ARENA])
for P in sys.argv[1:3]:
    fix(P, [("Minion</td><td>1 gold</td><td>5</td><td>2</td><td>2.0s</td><td>70%</td>", "Minion</td><td>1 gold</td><td>5</td><td>0.5</td><td>2.0s</td><td>60%</td>", 1)])
print('patched')

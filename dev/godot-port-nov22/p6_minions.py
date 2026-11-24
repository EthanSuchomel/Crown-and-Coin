"""Ethan, 2026-11-23 in Godot: Minions are 2 for 1 magic (were 3). Usage: python3 p6_minions.py PROJ"""
import sys
from common import F
P = sys.argv[1]
f = F(P + '/data/rules.json')
f.rep('"minion_pack": 3,', '"minion_pack": 2,', raw=True)
f.save()
f = F(P + '/scripts/rules/test_rules.gd')
f.rep('check("mythical: 3 Minions for 1 magic", g.myth_buy_minions(0, home, 2) and int(g.tiles[home].army.minion) == 10 and int(g.players[0].gold) == 38)',
      'check("mythical: 2 Minions for 1 magic", g.myth_buy_minions(0, home, 2) and int(g.tiles[home].army.minion) == 8 and int(g.players[0].gold) == 38)', raw=True)
f.save()
print('ok')

# Godot port of the browser's Dinosaur rework (2026-11-09), arena: the Alamosaurus comes back as the barracks guard
# (120 health, 15 damage every 2 s to up to 4 enemies; no riders, saddle, charge or stomp). It comes only from the board.
import sys; sys.path.insert(0,sys.path[0])
from common import F
P=sys.argv[1].rstrip('/')+'/scripts/'
a=F(P+'arena/arena_battle.gd')
a.rep('''    "alamo": {"label": "Alamosaurus", "heavy": true, "cost": 30, "hp": 108, "dmg": 15, "rate": 2.25, "range": 2.5, "footX": 8.8, "footY": 2.0, "speed": 3.861, "w": 21, "ratio": 0.7621, "aimFrac": 0.27, "hitKey": "melee", "reduce": {"archer": 3, "longbow": 3, "rider": 3}, "rank": 0, "preferGround": true, "riderType": "dilo", "riders": [[0.517, 0.335], [0.74, 0.303]], "lungeDur": 0.6, "strikeAt": 0.3, "bob": 0.4, "bobRate": 0.5, "legs": true, "multi": 5, "superStomp": {"stun": 2}, "charge": {"mult": 1.5, "dist": 21, "max": 4}, "art": "alamo"},''',
'''    "alamo": {"label": "Alamosaurus", "heavy": true, "cost": 25, "hp": 120, "dmg": 15, "rate": 2.0, "range": 2.5, "footX": 8.8, "footY": 2.0, "speed": 3.861, "w": 21, "ratio": 0.7621, "aimFrac": 0.27, "hitKey": "melee", "rank": 0, "preferGround": true, "hidden": true, "guard": true, "lungeDur": 0.6, "strikeAt": 0.3, "bob": 0.4, "bobRate": 0.5, "legs": true, "multi": 4, "art": "alamo"},   # the Dinosaurs' barracks guard (2026-11-09): each stomp hits up to 4 enemies''')
a.rep('''const ORDER := ["galli", "dilo", "ptero", "mega", "bow", "quetz", "robot",''','''const ORDER := ["galli", "dilo", "ptero", "mega", "bow", "quetz", "alamo", "robot",''')
a.rep('''"mage0", "mage1", "mage2", "mage3"]   # (the Alamosaurus and the Procoptodon are retired)''','''"mage0", "mage1", "mage2", "mage3"]   # (the Procoptodon is retired; the Alamosaurus only comes from the board, as a barracks guard)''')
a.rep('''        if TYPES.has(ak) and ORDER.has(ak):   # (the Alamosaurus and the Procoptodon are retired from the arena: any sent are dropped)''',
      '''        if TYPES.has(ak) and ORDER.has(ak):   # (the Procoptodon is retired from the arena: any sent are dropped)''')
a.save()
print('p13 arena ok')

# Godot port, step 1: the data files (decks, prices in materials, Fortify texts, the Dinosaur cards' own upgrades).
import json, sys
W = sys.argv[1] + '/data/'

def load(n): return json.load(open(W + n, encoding='utf-8'))
def save(n, d):
    open(W + n, 'w', encoding='utf-8').write(json.dumps(d, indent='\t', ensure_ascii=False) + '\n')

# ---------- factions.json: the themed decks (Ethan, 2026-11-10) ----------
f = load('factions.json')
decks = {
    'dinos': [('stamp', 'Stampede', ['move', 'build', 'fortify']), ('pack', 'Pack Call', ['harvest', 'recruit', 'fortify']),
              ('siege', 'Siege of Teeth', ['fortify', 'harvest', 'move']), ('hunt', 'The Hunt', ['harvest', 'recruit', 'advance']),
              ('nest', 'Nesting Season', ['harvest', 'build', 'fortify'])],
    'robots': [('mobil', 'Mobilize', ['recruit', 'advance', 'move']), ('deploy', 'Deploy', ['harvest', 'recruit', 'move']),
               ('onsl', 'Onslaught', ['harvest', 'advance', 'move']), ('cons', 'Construct', ['move', 'build', 'advance']),
               ('sprot', 'Siege Protocol', ['build', 'advance', 'fortify'])],
    'mammals': [('roam', 'The Long Roam', ['move', 'build', 'recruit']), ('forage', 'Forage', ['harvest', 'build', 'recruit']),
                ('den', 'Den Season', ['harvest', 'recruit', 'fortify']), ('wild', 'Call of the Wild', ['recruit', 'harvest', 'advance']),
                ('tusks', 'Tusks and Thorns', ['harvest', 'advance', 'move'])],
    'mythical': [('march', 'March of Minions', ['move', 'recruit', 'fortify']), ('gather', 'Gathering', ['harvest', 'recruit', 'advance']),
                 ('grove', 'The Grove', ['fortify', 'advance', 'move']), ('arcan', 'Arcanum', ['build', 'advance', 'fortify']),
                 ('chan', 'Channeling', ['channel'])],
}
for fid, cards in decks.items():
    f[fid]['cards'] = [{'id': i, 'name': n, 'actions': a} for i, n, a in cards]
f['dinos']['card_art'] = {c: 'res://art/cards/%s.png' % c for c in ['stamp', 'pack', 'siege', 'hunt', 'nest']}
f['themes'] = {'_note': 'The two actions each faction leans on (Ethan, 2026-11-10): each is on 4 of the 5 cards (3 of 4 for the Mythical).',
               'dinos': ['fortify', 'harvest'], 'robots': ['move', 'advance'], 'mammals': ['harvest', 'recruit'], 'mythical': ['advance', 'fortify']}
f['ai_upgrade_pref']['fortify'] = 4.2   # Fortify's upgrades add picks
save('factions.json', f)

# ---------- rules.json: materials ----------
r = load('rules.json')
r['_note'] = r['_note'] + ' Since 2026-11-10 forts, barracks, barracks upgrades, walls, trebuchets and Watering Holes are paid in materials (bought at markets).'
r['buildings']['cost_by_level'] = {'market': [6, 4, 4, 4], 'fort': [5, 5, 4, 3], 'barracks': [5, 5, 5, 4], 'wh': [4, 4, 4, 4]}
r['buildings']['in_materials'] = ['fort', 'barracks', 'wh']
r['buildings']['barracks_upgrade_cost'] = [3, 4, 5]
r['buildings']['_note'] = 'Markets cost gold; forts, barracks and Watering Holes cost materials, as do barracks upgrades.'
r['trebuchet']['field_cost'] = 8
r['trebuchet']['castle_cost'] = [10, 15]
r['trebuchet']['shot_note'] = 'a trebuchet: 8 materials on a hex with a fort; each shot rolls 5 dice and every 4 or higher kills one unit'
r['walls']['cost_by_level'] = [3, 3, 2, 2]
r['walls']['_note'] = 'prices in materials'
r['materials'] = {'_note': "Ethan, 2026-11-10: each market (and the home castle, while you hold it) sells up to 3 materials a turn at 2 gold each, any time on your turn. Units, markets, Alamosaurus guards and the volcano stay gold. The Mythical keep magic for everything.",
                  'price': 2, 'per_market': 3}
r['fortify'] = {'_note': 'Fortify is a wild card (Ethan, 2026-11-10/11): a regroup (moves of up to 2 hexes through your own land, as many as you like; the units stay ready), then Build, Advancements or Recruit at the basic level: 2 picks at level 2, all 3 at level 3. The old +1 defense is gone.',
                'regroup_reach': 2, 'picks': ['build', 'advance', 'recruit']}
r['actions'].pop('fortify_bonus', None)
r['dinos']['armor'] = {'cost': 40, 'dmg': 2, 'hp': 1.1, '_note': 'The Hunt, Advancements level 3: bought at the home castle; +2 damage and +10% health in every battle (Arena battles too).'}
r['dinos']['_note'] = r['dinos']['_note'] + ' Since 2026-11-11 every Dinosaur card has its own upgrades (upgrades.json dinos_cards); Herd, Migrate, Nesting, Populate, Abundance and Rainy Season are retired.'
save('rules.json', r)

# ---------- upgrades.json: texts ----------
u = load('upgrades.json')
g = u['general']
g['build'] = {'next': ['Markets cost 4 gold', 'Forts cost 4 materials', 'Forts 3 and Barracks 4 materials'],
              'now': ['Market 4', 'Market 4, Fort 4', 'Market 4, Fort 3, Barracks 4']}
g['fortify'] = {'next': ['Pick two of Build, Advancements and Recruit', 'Pick two of Build, Advancements and Recruit', 'Do all three: Build, Advancements and Recruit'],
                'now': ['pick 2', 'pick 2', 'all 3']}
g['advance']['next'] = ['Your first barracks upgrade to level 1 in this action is free', 'Walls cost 2 materials', 'Trebuchets you start finish at the end of this turn']
mn = u['mammals_named']['build']
mn['next'] = mn['next'].replace('(8 gold)', '(4 materials)')
mn['desc'] = mn['desc'].replace('(8 gold,', '(4 materials,')
u['dinos_named']['_note'] = 'Retired on 2026-11-11: the Dinosaurs use dinos_cards instead. Kept so old texts still load.'
u['dinos_cards'] = {
    '_note': "Ethan's per-card Dinosaur upgrades (2026-11-11). Each action on each card has its own 3 levels, which add up (except where one says 'instead'). The names are Claude's placeholders. [name, what it does]",
    'stamp': {'move': [['Charge', 'an extra move, if that move is an attack'], ['Home Run', 'units from your home castle can move to any of your hexes'], ['Two Herds', 'when you attack, the ready units on another of your hexes next to the target join in']],
              'build': [['Free Market', 'your first market in this action is free'], ['Supplies', '+2 materials when this action starts'], ['Cheap Nests', 'every building costs 1 less (markets 1 gold, the rest 1 material)']],
              'fortify': [['Hatchlings', '1 free Pachycephalosaurus at every nesting ground'], ['Raptor Brood', 'also 1 free Megaraptor at every nesting ground'], ['New Nest', 'a free nesting ground: your next barracks costs nothing']]},
    'pack': {'harvest': [['Trade Calls', '+1 gold for every market'], ['Castle Tolls', '+5 gold for every castle'], ['Big Herd', '+2 gold for every 5 of your units']],
             'recruit': [['Calling', '3 free Pachycephalosaurus at a nesting ground you pick'], ['Raptor Call', 'also 1 free Megaraptor there'], ['Castle Raptors', '2 free Megaraptors at your home castle']],
             'fortify': [['Join Up', 'one regroup move can go any distance through your land'], ['On the Move', "Move becomes one of Fortify's picks"], ['Rally', 'rally every unit you have onto one of your hexes']]},
    'siege': {'fortify': [['Market Day', '+2 gold for every market on your best market hex, once'], ['Guardian', 'a free Alamosaurus guard at a nesting ground'], ['Second Guardian', 'a second free Alamosaurus guard']],
              'harvest': [['Quarry', '+1 material for every 3 hexes you own'], ['Big Quarry', '+1 material for every 2 hexes instead'], ['Castle Stores', '+1 material for every castle']],
              'move': [['Climb', 'troops can move onto mountains'], ['Dash', 'troops go 2 hexes when both are empty'], ['Over the Top', 'cross a mountain and attack on the far side in one move']]},
    'hunt': {'harvest': [['Hunting Grounds', '1 gold for every hex you own, instead of every 2'], ['Nest Feast', '+2 gold for every nesting ground'], ['Castle Feast', '+5 gold for every castle']],
             'recruit': [['Home Hunters', 'units bought at your home castle cost 1 gold less'], ['Castle Herds', '2 free Pachycephalosaurus at every castle'], ['Nest Hunters', 'units bought at a barracks cost 1 gold less']],
             'advance': [['Quick Nests', 'barracks upgrades cost 1 material less'], ['Cheap Guards', 'Alamosaurus guards cost 3 gold less'], ['Armor', 'buy Armor at your home castle: 40 gold, all your units +2 damage and +10% health, in every battle']]},
    'nest': {'harvest': [['Gathering', '+3 materials when this action starts'], ['Stockpile', '+5 materials instead'], ['Great Store', '+10 materials instead']],
             'build': [['Cheap Markets', 'markets cost 1 gold less'], ['Market Row', "a hex's 2nd and 3rd market cost 1 gold less again"], ['New Nest', 'a free nesting ground: your next barracks costs nothing']],
             'fortify': [['Castle Hatch', 'captured castles get 1 Pachycephalosaurus'], ['Castle Brood', '3 instead'], ['Castle Guard', '2 Pachycephalosaurus and 1 Megaraptor instead']]},
}
save('upgrades.json', u)
print('data ok')

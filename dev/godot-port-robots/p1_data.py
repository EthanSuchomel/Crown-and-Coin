# The Robot rework (browser 2026-11-11/12) for the Godot version, step 1: the data.
# - factions.json: Mobilize is Advancements -> Recruit -> Move, Construct is Construction, the punch-card pictures.
# - upgrades.json: robots_cards, each Robot card's own 3 upgrades per action (Ethan's effects, Claude's placeholder names).
# - rules.json: robots.markets_max (a resource hex holds up to 4 markets); the old Efficiency number is gone.
import json, sys, os
P = sys.argv[1]
def load(n): return json.load(open(os.path.join(P, 'data', n), encoding='utf-8'))
def save(n, d): open(os.path.join(P, 'data', n), 'w', encoding='utf-8').write(json.dumps(d, indent='\t', ensure_ascii=False) + '\n')

f = load('factions.json')
r = f['robots']
for c in r['cards']:
    if c['id'] == 'mobil':
        assert c['actions'] == ['recruit', 'advance', 'move']; c['actions'] = ['advance', 'recruit', 'move']
    if c['id'] == 'cons':
        assert c['name'] == 'Construct'; c['name'] = 'Construction'
r['card_art'] = {cid: 'res://art/cards/%s.png' % cid for cid in ['mobil', 'deploy', 'onsl', 'cons', 'sprot']}
save('factions.json', f)

u = load('upgrades.json')
u['robots_cards'] = {
    'mobil': {'advance': [['Home Grid', 'factory and barracks upgrades on hexes next to your home castle cost 1 material less'], ['Recompile', 'trade 5 Brawlers on a hex for a Robot Knight'], ['Cheap Markets', 'markets cost 3 gold less, from now on']],
              'recruit': [['Assembly Line', 'for every 2 Brawlers you buy, a 3rd is free'], ['Rebuild', 'trade 8 Brawlers on a hex for a Robot Knight'], ['Refit', 'trade 5 Robot Archers on a hex for a Robot Longbow']],
              'move': [['Extra Thread', '3 moves instead of 2'], ['Climb', 'troops can move onto mountains'], ['Offline', "sneak attacks: the defenders can't attack until your units land their first hit"]]},
    'deploy': {'harvest': [['Castle Tax', '+2 gold for every castle you hold'], ['Castle Tolls', '+5 gold for every castle instead'], ['Castle Vaults', '+12 gold for every castle instead']],
               'recruit': [['Drone Line', 'flyers cost 1 gold less'], ['Air Wing', 'flyers cost 2 gold less instead'], ['Sky Fleet', 'flyers cost 3 gold less instead']],
               'move': [['Air Lanes', 'flyers can move to any of your hexes'], ['Ridge Hop', 'flyers can cross a mountain and land on the far side'], ['Overflight', 'flyers can fly over an enemy army and land 2 hexes away']]},
    'onsl': {'harvest': [['Full Yield', '1 gold for every hex you own, instead of every 2'], ['Market Hubs', '+5 gold for every hex with 4 markets'], ['Hub Stores', '+2 materials for every hex with 4 markets']],
             'advance': [['Muster', 'every barracks upgrade also makes 2 Brawlers on that hex'], ['Muster Archers', 'and a Robot Archer'], ['Elite Muster', 'a Robot Knight and a Robot Longbow instead']],
             'move': [['Fresh Units', 'units on a hex where you recruited this turn go 2 hexes'], ['Laser Strike', 'Laser Tanks next to an enemy hex can fire like a trebuchet instead of attacking: no battle'], ['Double Strike', 'a laser strike fires twice']]},
    'cons': {'move': [['Scavenger', 'bonus coins pay 12 gold instead of 8'], ['Brawler Dash', 'Brawlers go 2 hexes when both are empty'], ['Air Lanes', 'flyers can move to any of your hexes']],
             'build': [['Fresh Ground', 'a hex you captured this turn: its first market costs 1 gold less'], ['Fourth Free', "a hex's 4th market is free"], ['Scrap', '+1 material for every 2 markets you build']],
             'advance': [['Quick Barracks', 'barracks upgrades cost 1 material less'], ['Quick Fortress', 'fortress upgrades cost 1 material less'], ['Overclock', 'buy Overclock at your home castle: 40 gold, all your units +2 damage and +10% health, in every battle']]},
    'sprot': {'build': [['Border Market', 'a captured hex next to your home castle: its first market costs 2 gold less'], ['Free Market', 'your first market in this action is free'], ['Two Free Markets', 'your first 2 markets in this action are free']],
              'advance': [['Factory Run', '5 free Brawlers at your home castle when this action starts'], ['Barracks Run', 'also 3 free Brawlers at every barracks'], ['Fortress Run', 'also 2 free Robot Knights at every fortress']],
              'fortify': [['Dual Core', 'pick two of Build, Advancements and Recruit'], ['Sortie', 'then a real Move: one move that can attack or claim'], ['Home Link', 'units at your home castle can regroup to any of your hexes']]},
}
u['_note_robots'] = "Since 2026-11-11 every Robot card has its own upgrades (robots_cards), like the Dinosaurs'. Update, Offline, Efficiency, Factory, Assembly Line and Industrialization (robots_named) are retired; Offline and Assembly Line live on as Mobilize upgrades."
save('upgrades.json', u)

rl = load('rules.json')
rb = rl['robots']
rb.pop('efficiency_max_buildings', None)
rb['markets_max'] = 4
rb['trades'] = {'ak': {'a': 'advance', 'l': 2, 'from': 'brawler', 'n': 5, 'to': 'rknight', 'name': 'Recompile'},
                'rk': {'a': 'recruit', 'l': 2, 'from': 'brawler', 'n': 8, 'to': 'rknight', 'name': 'Rebuild'},
                'rl': {'a': 'recruit', 'l': 3, 'from': 'rarch', 'n': 5, 'to': 'rlong', 'name': 'Refit'}}
rb['scavenger_gold'] = 12
rb['_note'] = "Ethan, 2026-11-11: one Robot building per hex. It starts as a market; then either more markets on that hex (a resource hex, up to markets_max) or, from the home castle during Advancements, a barracks and then a fortress (a factory). Never both. factory_units: Factory Run's Brawlers. trades: Mobilize's Recompile, Rebuild and Refit."
save('rules.json', rl)
print('p1 data ok')

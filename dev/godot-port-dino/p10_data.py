# Godot port of the browser's Dinosaur rework (2026-11-09), data: the board roster, barracks unlocks, guards and volcano numbers.
import json,sys
P=sys.argv[1].rstrip('/')+'/data/'
def load(n): return json.load(open(P+n))
def save(n,d): json.dump(d,open(P+n,'w'),indent='\t',ensure_ascii=False); open(P+n,'a').write('\n')
u=load('units.json')
u['galli']={"name":"Pachycephalosaurus","hp":15,"dmg":5,"rate":1.0,"cost":3,"rank":0,"basic":True,"hk":"galli",
  "note":"Charges in. Each head-butt slows the enemy it hits for the rest of the battle"}
u['dilo']={"name":"Dilophosaurus","hp":15,"dmg":2,"rate":0.6,"cost":8,"rank":2,"rng":True,"aa":True,"basic":True,"hk":"archer",
  "note":"Shooter that spits venom half the field. Grounds flyers it hits for 3s. Dodges half of charging hits"}
big=["mega","bow","quetz","alamo","rknight","ltank","rhino","gbat","eleph","minotaur","griffin","dragon"]   # as the browser's UNIT_STATS.mega.bonus at runtime
u['mega']={"name":"Megaraptor","hp":35,"dmg":12,"rate":1.0,"cost":12,"rank":0,"heavy":True,"hk":"melee","multi":2,"noStun":True,
  "sprint":{"dur":2,"mult":3},"bonus":{k:8 for k in big},
  "note":"Its bite also catches a second enemy. 20 damage to big units. Can't be stunned. Sprints in from reserve"}
u['bow']={"name":"Triceratops","hp":45,"dmg":15,"rate":1.2,"cost":25,"rank":0,"heavy":True,"hk":"melee","noProj":True,
  "note":"Shots and spells do nothing to it (except the Laser Tank's beam). Charges, knocking back up to 6, and stops enemy charges"}
u['quetz']={"name":"Stegosaurus","hp":65,"dmg":20,"rate":2.0,"cost":30,"rank":0,"heavy":True,"hk":"melee","multi":8,
  "note":"Tail swing hits up to 8 ground enemies around it and stuns the ones left standing for 2s"}
u['alamo']={"name":"Alamosaurus","hp":120,"dmg":15,"rate":2.0,"cost":25,"rank":0,"heavy":True,"hk":"melee","multi":4,"guard":True,
  "note":"Barracks guard: bought at a barracks, never moves or attacks, and fights whenever the hex is attacked. Each stomp hits up to 4 enemies"}
u['brawler']['note']=u['brawler']['note'].replace('every Gallimimus','every Pachycephalosaurus')
missing=[k for k in big if k not in u]; assert not missing, missing
save('units.json',u)
f=load('factions.json')
f['dinos']['training']={"barracks":["galli","dilo","mega","ptero","bow","quetz"],"fort":[]}
save('factions.json',f)
r=load('rules.json')
r['barracks_unlocks']={"mega":1,"rknight":1,"rlong":2,"rhino":1,"kanga":2,"ptero":2,"bow":3,"quetz":3}
r['dinos'].update({"_note":"The Dinosaurs build no forts or trebuchets (Ethan, 2026-11-09). Alamosaurus guards are hired for a barracks; the home castle's volcano replaces trebuchets.",
  "guard_cost":25,"guard_max":2,
  "volcano":[{"cost":40,"reach":5,"every":3,"dice":5},{"cost":60,"reach":7,"every":2,"dice":6},{"cost":100,"reach":99,"every":1,"dice":8}]})
save('rules.json',r)
up=load('upgrades.json')
up['dinos_named']['advance'].update({"next":"Populate: when this action starts, every barracks you own gets 1 free Pachycephalosaurus","desc":"Populate: first, every barracks you own gets 1 free Pachycephalosaurus"})
up['dinos_named']['recruit'].update({"next":"Abundance: Pachycephalosaurus and Dilophosaurus cost 1 gold less","desc":"Abundance: Pachycephalosaurus and Dilophosaurus cost 1 gold less"})
save('upgrades.json',up)
print('p10 data ok')

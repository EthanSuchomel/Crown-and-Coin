extends RefCounted
## Megaraptor Arena: one real-time battle, on the Open field, Ferns, Trees, Mountain or Castle map. Ported from the browser Arena's build, addUnit,
## update, pickTarget, hit, shoot, tankStep, the Robot Knight shield walls, reinforce and tally.
## This file only runs the battle; arena_view.gd draws it and arena_screen.gd holds the buttons.
##
## The field is 100 wide and 60 tall. x runs left to right; y runs top to bottom and marks a unit's feet.
## Team 0 is Blue (the Dinosaurs) and starts on the left; team 1 is Red (the Robots) on the right.
## Mammals are left out until they're added to the game.

const AW := 100.0
const AH := 60.0
const ALT := 7.6               # flyers' cruising height
const LOW_ALT := 2.2           # how low flyers come to fight ground units
const FIELD_MAX := 25.0        # spaces on the field per side (Brawlers and Drones take half)
const SEP_SAME := 1.6
const SEP_ENEMY := 2.0
const ARROW_SPEED := 60.0
const STEP := 1.0 / 30.0       # one slice of battle time
const MEGA_CHARGE_DODGE := 0.75
var HOLD: int = 0              # the side holding the map: it always starts on the left (the screen mirrors when Red holds)
var map: String = "open"
const HELD_MAPS := ["trees", "mountain", "castle", "fortress"]   # maps one side holds

## Unit stats, as in the browser Arena's TYPES. The level-specific Mages (mage0-mage3) are added by _types().
const TYPES := {
	"robot": {"label": "Robot Brawler", "cost": 1, "slot": 0.5, "hp": 4, "dmg": 2, "rate": 1.0, "missHeavy": 0.25, "range": 3.0, "speed": 9.11, "w": 2.854, "ratio": 0.9517, "hitKey": "robot", "rank": 0, "basic": true, "lungeDur": 0.3, "strikeAt": 0.13, "bob": 0.7, "bobRate": 2.17, "sheet": 17, "runFrames": 10, "runCycle": 0.32, "art": "rbs"},
	"rarch": {"label": "Robot Archer", "cost": 4, "hp": 6, "dmg": 2, "rate": 1.0, "range": 24, "speed": 4.05, "w": 2.632, "ratio": 1.0749, "ranged": true, "hitKey": "laser", "antiAir": true, "missAir": 0.2, "rank": 2, "basic": true, "lungeDur": 0.32, "strikeAt": 0.14, "bob": 0.4, "bobRate": 1.13, "sheet": 12, "runFrames": 8, "runCycle": 0.62, "gun": [[0.8758, 0.4172], [0.6359, 0.3917]], "art": "ras"},
	"rlong": {"label": "Robot Longbow", "retargetNoDmg": true, "cost": 10, "hp": 22, "dmg": 4, "rate": 2.2, "range": 36, "speed": 3.51, "w": 5.371, "ratio": 0.8669, "ranged": true, "hitKey": "longbow", "antiAir": true, "rank": 2, "bonusAir": 2, "lungeDur": 0.32, "strikeAt": 0.14, "bob": 0.15, "bobRate": 3, "stunShot": {"every": 4, "dur": 1}, "noHide": true, "sheet": 10, "runFrames": 6, "runCycle": 0.25, "gun": [[0.9213, 0.3378], [0.4572, 0.3378]], "noRecoil": true, "art": "rls"},
	"rjet": {"label": "Robot Gunship", "cost": 14, "hp": 30, "dmg": 12, "rate": 1.7, "range": 12, "speed": 5.94, "w": 9.784, "ratio": 0.6634, "aimFrac": 0.678, "rocket": true, "hover": true, "hitKey": "gunship", "flying": true, "antiAir": true, "rank": 1, "preferMelee": true, "lungeDur": 0.7, "strikeAt": 0.35, "sheet": 6, "jet": true, "weapons": {"laser": {"dmg": 8, "rate": 1.5}, "rocket": {"dmg": 10, "rate": 2}}, "hatch": [0.6, 0.3333], "gunPivot": [0.6634, 0.4457], "gunTip": [0.8699, 0.6255], "gunTurn": 320, "art": "rjs"},
	"rtank": {"label": "Laser Tank", "heavy": true, "stunImmune": true, "cost": 40, "slot": 3, "fieldMax": 2, "hp": 100, "dmg": 1, "rate": 5, "range": 70, "speed": 0.54, "w": 19.845, "ratio": 0.6172, "aimFrac": 0.3, "footX": 7.65, "footY": 1.8, "ranged": true, "hitKey": "beam", "antiAir": true, "rank": 3, "noHide": true, "back": true, "bob": 0.01, "sheet": 7, "runFrames": 6, "runCycle": 0.9, "muzzle": [0.8865, 0.3088], "pivot": [0.2042, 0.2623], "aimMax": 22, "turnRate": 70, "beam": {"dur": 2.5, "tick": 0.2, "ticks": 12, "follow": 12.0, "n": 10, "radius": 8.4, "cool": 6, "shots": 4, "startDelay": 2}, "art": "rts"},
	"rdrone": {"label": "Robot Drone", "cost": 2, "slot": 0.5, "hp": 5, "dmg": 1, "rate": 0.5, "range": 3.0, "speed": 10.48, "w": 2.796, "ratio": 0.9554, "aimFrac": 0.35, "hitKey": "drone", "flying": true, "rank": 1, "basic": true, "lungeDur": 0.3, "strikeAt": 0.15, "sheet": 12, "prop": 0.16, "dodge": 0.05, "art": "rds"},
	"rknight": {"label": "Robot Knight", "heavy": true, "cost": 9, "hp": 25, "dmg": 12, "rate": 1.0, "range": 4.3, "speed": 4.86, "w": 7.058, "ratio": 0.9437, "aimFrac": 0.371, "hitKey": "melee", "armor": {"archer": 3, "longbow": 1, "galli": 1, "rider": 2, "laser": 3}, "deflect": {"galli": 0.1}, "rank": 0, "bonus": {"bow": 4}, "sweep": {"n": 2, "mult": 0.25, "reach": 3.5}, "lungeDur": 0.32, "strikeAt": 0.14, "bob": 0.5, "bobRate": 1.0, "sheet": 12, "runFrames": 8, "runCycle": 0.78, "swing": true, "wall": {"size": 3, "max": 4, "hp": 50, "hide": 6, "stun": 1, "speedMult": 0.5}, "art": "rks"},
	"galli": {"label": "Pachycephalosaurus", "cost": 3, "hp": 15, "dmg": 5, "rate": 1.0, "range": 4.3, "speed": 5.4, "w": 6.6, "artW": 7.538, "ratio": 0.6365, "aimFrac": 0.417, "hitKey": "melee",
		"walkSheet": true, "sheet": 13, "runFrames": 8, "runCycle": 0.5, "atkFrames": 9, "atkSteps": [0.15, 0.35, 0.6], "pcharge": {"mult": 1.6}, "slowHit": {"spd": 0.81, "rate": 0.3}, "noRepeat": true,
		"rank": 0, "basic": true, "lungeDur": 0.32, "strikeAt": 0.14, "lungeFwd": 0.012, "bob": 0.5, "bobRate": 1.6, "art": "dns_pachy"},
	"dilo": {"label": "Dilophosaurus", "cost": 8, "hp": 15, "dmg": 2, "rate": 0.6, "range": 50, "dodgeCharge": 0.5, "speed": 5.4, "w": 6.4, "artW": 7.31, "ratio": 0.5919, "aimFrac": 0.415, "ranged": true, "hitKey": "archer",
		"walkSheet": true, "sheet": 12, "runFrames": 8, "runCycle": 0.55, "atkFrames": 9, "atkSteps": [0.25, 0.6], "preferAir": true, "noRepeat": true, "grounds": {"dur": 3}, "spit": true, "shotAt": [0.912, 0.287],
		"antiAir": true, "rank": 2, "basic": true, "lungeDur": 0.3, "strikeAt": 0.12, "bob": 0.4, "bobRate": 1.4, "art": "dns_dilo"},
	"ptero": {"label": "Pterodactyl", "cost": 5, "hp": 10, "dmg": 5, "rate": 1.5, "range": 3.5, "speed": 7.02, "w": 2.961, "ratio": 1.2717, "aimFrac": 0.352, "hitKey": "air", "flying": true, "rank": 1, "basic": true, "lungeDur": 0.5, "strikeAt": 0.25, "flap": 0.4, "art": "ptero"},
	"mega": {"label": "Megaraptor", "heavy": true, "stunImmune": true, "cost": 12, "hp": 35, "dmg": 12, "bigDmg": 20, "twin": true, "rate": 1.0, "range": 4.3, "speed": 6.21, "w": 9.5, "artW": 10.821, "ratio": 0.5293, "aimFrac": 0.412, "hitKey": "melee",
		"walkSheet": true, "sheet": 13, "runFrames": 8, "runCycle": 0.5, "atkFrames": 9, "atkSteps": [0.2, 0.4, 0.65], "entryBurst": {"dur": 1e9, "mult": 1.6087},
		"rank": 0, "lungeDur": 0.4, "strikeAt": 0.18, "lungeFwd": 0.012, "bob": 0.4, "bobRate": 1.3, "art": "dns_mega"},
	"bow": {"label": "Triceratops", "heavy": true, "noProj": true, "fieldFirst": true, "cost": 25, "hp": 45, "dmg": 15, "rate": 1.2, "range": 3.0, "footX": 3.2, "footY": 1.0, "speed": 5.4, "w": 11.5, "artW": 12.888, "ratio": 0.6197, "aimFrac": 0.417, "hitKey": "melee",
		"walkSheet": true, "sheet": 13, "runFrames": 8, "runCycle": 0.7, "atkFrames": 9, "atkSteps": [0.2, 0.4, 0.7], "tcharge": {"mult": 1.5, "n": 6}, "knock": 3, "hornSweep": {"n": 5}, "stopsCharge": true,
		"rank": -1, "lungeDur": 0.45, "strikeAt": 0.2, "lungeFwd": 0.012, "bob": 0.2, "bobRate": 0.9, "art": "dns_trike"},
	"alamo": {"label": "Alamosaurus", "heavy": true, "cost": 25, "hp": 120, "dmg": 15, "rate": 2.0, "range": 2.5, "footX": 8.8, "footY": 2.0, "speed": 3.861, "w": 21, "ratio": 0.7621, "aimFrac": 0.27, "hitKey": "melee", "rank": 0, "preferGround": true, "hidden": true, "guard": true, "lungeDur": 0.6, "strikeAt": 0.3, "bob": 0.4, "bobRate": 0.5, "legs": true, "multi": 4, "art": "alamo"},   # the Dinosaurs' barracks guard (2026-11-09): each stomp hits up to 4 enemies
	"quetz": {"label": "Stegosaurus", "heavy": true, "cost": 30, "hp": 65, "dmg": 20, "rate": 2.0, "range": 3.0, "footX": 4.0, "footY": 1.2, "speed": 5.4, "w": 13.5, "artW": 15.375, "ratio": 0.6945, "aimFrac": 0.382, "hitKey": "melee",
		"walkSheet": true, "sheet": 13, "runFrames": 8, "runCycle": 0.8, "atkFrames": 9, "atkSteps": [0.25, 0.45, 0.75], "tail": {"n": 8, "reach": 3, "stun": 2},
		"rank": 0, "lungeDur": 0.6, "strikeAt": 0.3, "lungeFwd": 0.006, "bob": 0.15, "bobRate": 0.8, "art": "dns_stego"},
	# ---- Mammals (OpenArt art, cut into walk sheets: frame 0 standing, then the walk; bats beat their wings in 16 frames) ----
	"ape": {"label": "Gorilla", "faction": "Mammals", "cost": 4, "hp": 14, "dmg": 3, "rate": 1.0, "range": 4.3, "speed": 5.67, "w": 4.6, "ratio": 0.7816, "aimFrac": 0.5, "hitKey": "melee",
		"walkSheet": true, "sheet": 9, "runFrames": 8, "runCycle": 0.6, "rank": 0, "basic": true, "lungeDur": 0.32, "strikeAt": 0.14, "lungeFwd": 0.007, "bob": 0.15, "bobRate": 1.4, "art": "mms_ape"},
	"porc": {"label": "Porcupine", "faction": "Mammals", "cost": 6, "hp": 8, "quills": 1, "dmg": 4, "rate": 1.2, "range": 24, "speed": 4.59, "w": 4.2, "ratio": 0.7881, "aimFrac": 0.45, "ranged": true, "hitKey": "archer",
		"walkSheet": true, "sheet": 9, "runFrames": 8, "runCycle": 0.5, "antiAir": true, "missAir": 0.2, "rank": 2, "basic": true, "lungeDur": 0.32, "strikeAt": 0.14, "bob": 0.15, "bobRate": 1.6, "shotAt": [0.62, 0.3], "art": "mms_porc"},
	"rhino": {"label": "Rhino", "faction": "Mammals", "heavy": true, "rhinoCharge": {"mult": 1.5, "dmg": 20, "next": 10}, "fieldFirst": true, "cost": 15, "hp": 28, "dmg": 12, "rate": 1.2, "range": 4.3, "speed": 6.21,
		"w": 11.408, "ratio": 0.5065, "aimFrac": 0.404, "hitKey": "melee", "walkSheet": true, "sheet": 13, "runFrames": 12, "runCycle": 0.8, "stride": 4.962, "rank": 0, "lungeDur": 0.4, "strikeAt": 0.18, "lungeFwd": 0.012, "bob": 0.15, "bobRate": 1.0, "art": "mms_rhino"},
	"kanga": {"label": "Procoptodon", "faction": "Mammals", "cost": 18, "hp": 20, "dmg": 9, "rate": 1.0, "range": 36, "speed": 5.4, "w": 5.0, "ratio": 0.9245, "aimFrac": 0.5, "ranged": true, "hitKey": "longbow",
		"walkSheet": true, "sheet": 9, "runFrames": 8, "runCycle": 0.75, "antiAir": true, "missAir": 0.15, "rank": 2, "lungeDur": 0.32, "strikeAt": 0.14, "bob": 0.01, "bobRate": 0.9, "shotAt": [0.93, 0.47], "art": "mms_kanga"},
	"bat": {"label": "Bat", "faction": "Mammals", "cost": 2, "slot": 0.5, "hp": 5, "dmg": 2, "rate": 1.0, "range": 3.5, "speed": 7.29, "w": 4.2, "ratio": 0.8333, "aimFrac": 0.246, "sheet": 16, "flapSheet": true,
		"hitKey": "air", "flying": true, "rank": 1, "basic": true, "lungeDur": 0.3, "strikeAt": 0.15, "flap": 1.4, "art": "mms_bat"},
	"gbat": {"label": "Desmodus", "large": true, "faction": "Mammals", "cost": 20, "hp": 20, "dmg": 15, "rate": 1.0, "range": 4, "speed": 6.21, "w": 8.8, "ratio": 0.9094, "aimFrac": 0.241, "sheet": 16, "flapSheet": true,
		"hitKey": "air", "flying": true, "antiAir": true, "rank": 1, "preferMelee": true, "lungeDur": 0.6, "strikeAt": 0.3, "flap": 2.1, "art": "mms_gbat"},
	"eleph": {"label": "Palaeoloxodon", "faction": "Mammals", "heavy": true, "cost": 50, "hp": 80, "dmg": 18, "rate": 1.0, "range": 2.5, "footX": 5.4, "footY": 1.5, "speed": 5.94, "w": 19.432, "ratio": 0.6133, "aimFrac": 0.322,
		"hitKey": "melee", "walkSheet": true, "sheet": 25, "runFrames": 12, "runCycle": 0.7, "stride": 4.14, "atkFrames": 13, "atk2Frames": 19, "atkSteps": [0.15, 0.3, 0.45, 0.6, 0.8], "rank": 0, "preferGround": true, "multi": 5, "knock": 2.2,
		"trumpet": {"at": 2.0, "dur": 1.3, "dmg": 2, "rate": 0.2, "speed": 1.15, "delay": 2.0}, "lungeDur": 0.7, "strikeAt": 0.35, "lungeFwd": 0.003, "bob": 0.1, "bobRate": 0.6, "art": "mms_eleph"},
	# ---- Mythical (Ethan's stats; speed 100% = 5.4). Pictures: myth_* (OpenArt, cut out; the Griffin's and Dragon's wing beats drawn by Claude) ----
	"minion": {"label": "Minion", "faction": "Mythical", "cost": 1, "hp": 5, "dmg": 0.5, "rate": 2.0, "range": 3.5, "speed": 3.24, "w": 1.5, "ratio": 1.3727, "aimFrac": 0.45, "hitKey": "melee",
		"rank": 0, "basic": true, "lungeDur": 0.3, "strikeAt": 0.13, "lungeFwd": 0.008, "bob": 0.6, "bobRate": 2.2, "art": "myth_minion"},
	"mage": {"label": "Mage", "faction": "Mythical", "cost": 15, "maxN": 2, "hp": 15, "dmg": 5, "rate": 3, "range": 120, "speed": 2.7, "w": 2.8, "ratio": 1.4636, "aimFrac": 0.5, "ranged": true, "hitKey": "magic",
		"antiAir": true, "rank": 2, "lightning": {"n": 20, "jump": 9}, "morph": {"every": 2, "chance": 0.2, "into": "minotaur"}, "lungeDur": 0.6, "strikeAt": 0.3, "noRecoil": true, "bob": 0.2, "bobRate": 1.2, "staff": [0.17, 0.06], "art": "myth_mage"},
	"mage0": {"label": "Mage", "faction": "Mythical", "cost": 15, "maxN": 3, "hidden": true, "hp": 15, "dmg": 2, "rate": 3, "range": 30.0, "speed": 2.7, "w": 2.8, "ratio": 1.4636, "aimFrac": 0.5, "ranged": true, "hitKey": "magic",
		"antiAir": true, "rank": 2, "lightning": {"n": 20, "jump": 9}, "morph": {"every": 2, "chance": 0.2, "into": "minotaur"}, "lungeDur": 0.6, "strikeAt": 0.3, "noRecoil": true, "bob": 0.2, "bobRate": 1.2, "staff": [0.17, 0.06], "art": "myth_mage"},
	"mage1": {"label": "Mage", "faction": "Mythical", "cost": 15, "maxN": 3, "hidden": true, "hp": 15, "dmg": 3, "rate": 3, "range": 45.0, "speed": 2.7, "w": 2.8, "ratio": 1.4636, "aimFrac": 0.5, "ranged": true, "hitKey": "magic",
		"antiAir": true, "rank": 2, "lightning": {"n": 20, "jump": 9}, "morph": {"every": 2, "chance": 0.3, "into": "minotaur"}, "lungeDur": 0.6, "strikeAt": 0.3, "noRecoil": true, "bob": 0.2, "bobRate": 1.2, "staff": [0.17, 0.06], "art": "myth_mage"},
	"mage2": {"label": "Mage", "faction": "Mythical", "cost": 15, "maxN": 3, "hidden": true, "hp": 15, "dmg": 4, "rate": 3, "range": 60.0, "speed": 2.7, "w": 2.8, "ratio": 1.4636, "aimFrac": 0.5, "ranged": true, "hitKey": "magic",
		"antiAir": true, "rank": 2, "lightning": {"n": 20, "jump": 9}, "morph": {"every": 2, "chance": 0.4, "into": "minotaur"}, "lungeDur": 0.6, "strikeAt": 0.3, "noRecoil": true, "bob": 0.2, "bobRate": 1.2, "staff": [0.17, 0.06], "art": "myth_mage"},
	"mage3": {"label": "Mage", "faction": "Mythical", "cost": 15, "maxN": 3, "hidden": true, "hp": 15, "dmg": 5, "rate": 3, "range": 90.0, "speed": 2.7, "w": 2.8, "ratio": 1.4636, "aimFrac": 0.5, "ranged": true, "hitKey": "magic",
		"antiAir": true, "rank": 2, "lightning": {"n": 20, "jump": 9}, "morph": {"every": 2, "chance": 0.5, "into": "minotaur"}, "lungeDur": 0.6, "strikeAt": 0.3, "noRecoil": true, "bob": 0.2, "bobRate": 1.2, "staff": [0.17, 0.06], "art": "myth_mage"},
	"minotaur": {"label": "Minotaur", "faction": "Mythical", "heavy": true, "cost": 25, "hp": 35, "dmg": 15, "rate": 1.0, "range": 4.3, "speed": 6.21, "w": 6.6, "ratio": 1.1228, "aimFrac": 0.45, "hitKey": "melee",
		"walkSheet": true, "sheet": 15, "runFrames": 8, "runCycle": 0.6, "atkFrames": 9, "atkSteps": [0.15, 0.32, 0.55, 0.75, 0.9], "mcharge": {"mult": 1.6, "stun": 4},
		"rank": 0, "multi": 5, "lungeDur": 0.6, "strikeAt": 0.36, "lungeFwd": 0.006, "bob": 0.3, "bobRate": 1.1, "art": "myth_minotaur"},
	"griffin": {"label": "Griffin", "large": true, "faction": "Mythical", "cost": 40, "hp": 45, "dmg": 25, "rate": 1.0, "range": 4, "speed": 7.02, "walkSpeed": 5.4, "w": 10.0, "ratio": 0.9808, "sheet": 24, "flapSheet": true,
		"soar": {"period": 1.6}, "walkCycle": 0.6, "gswoop": {"mult": 2, "radius": 5, "dmg": 2, "miss": 2}, "knock": 3, "aimFrac": 0.45, "hitKey": "air",
		"flying": true, "antiAir": true, "rank": 1, "lungeDur": 0.6, "strikeAt": 0.3, "flap": 0.75, "art": "myth_griffin"},
	"dragon": {"label": "Dragon", "large": true, "faction": "Mythical", "cost": 85, "hp": 150, "dmg": 30, "rate": 1.0, "range": 5, "speed": 6.48, "walkSpeed": 4.86, "w": 21.35, "ratio": 0.8571, "sheet": 24, "sheetRows": 2, "flapSheet": true,
		"soar": {"period": 2.2}, "walkCycle": 0.8, "swoop": {"mult": 6, "back": 1.5, "land": 0.3, "wait": 1.2, "ahead": 14, "fire": {"dur": 5, "after": 5, "dps": 5, "r": 2.4, "gap": 1.6}}, "aimFrac": 0.45, "hitKey": "air",
		"flying": true, "antiAir": true, "rank": 1, "breath": {"dmg": 15, "n": 15, "rate": 8, "reach": 16, "first": 2}, "mouth": [0.918, 0.571], "mouthLand": [0.825, 0.608], "lungeDur": 0.7, "strikeAt": 0.35, "flap": 1.1, "art": "myth_dragon"},
}
const ORDER := ["galli", "dilo", "ptero", "mega", "bow", "quetz", "alamo", "robot", "rarch", "rdrone", "rknight", "rlong", "rjet", "rtank",
	"ape", "porc", "bat", "rhino", "gbat", "eleph", "minion", "mage", "minotaur", "griffin", "dragon", "mage0", "mage1", "mage2", "mage3"]   # (the Procoptodon is retired; the Alamosaurus only comes from the board, as a barracks guard)
## Crown & Coin's Mages by level: lightning reach and damage, and each level's chance every 2 s to turn a Minion into a Minotaur.
const MAGE_LV := [[30.0, 5, 0.2], [60.0, 6, 0.3], [90.0, 7, 0.4], [120.0, 7, 0.5]]
const SPECIAL := ["rtank", "alamo", "eleph"]
const DEFAULT_ARMY := {"Dinosaurs": {"galli": 15, "dilo": 6, "ptero": 5, "mega": 5, "bow": 2, "quetz": 1}, "Robots": {"robot": 4, "rarch": 28, "rdrone": 8, "rknight": 6, "rlong": 4, "rtank": 1},
	"Mammals": {"ape": 14, "porc": 6, "bat": 10, "rhino": 3, "gbat": 2, "eleph": 1}, "Mythical": {"minion": 25, "mage": 2, "minotaur": 3, "griffin": 1, "dragon": 1}}
## Crown & Coin's unit names -> the Arena's, and back.
const KEY_IN := {"galli": "galli", "dilo": "dilo", "mega": "mega", "bow": "bow", "ptero": "ptero", "quetz": "quetz", "alamo": "alamo",
	"brawler": "robot", "rarch": "rarch", "rknight": "rknight", "rlong": "rlong", "drone": "rdrone", "gunship": "rjet", "ltank": "rtank",
	"ape": "ape", "porc": "porc", "rhino": "rhino", "kanga": "kanga", "bat": "bat", "gbat": "gbat", "eleph": "eleph",
	"minion": "minion", "mage": "mage", "mage0": "mage0", "mage1": "mage1", "mage2": "mage2", "mage3": "mage3", "minotaur": "minotaur", "griffin": "griffin", "dragon": "dragon"}


class Unit:
	var id: int = 0
	var team: int = 0
	var key: String = ""
	var T: Dictionary = {}
	var h: float = 0.0
	var x: float = 0.0
	var y: float = 0.0
	var hp: float = 0.0
	var armor: Dictionary = {}
	var cd: float = 0.0
	var lunge: float = -1.0
	var struck: bool = false
	var flash: float = 0.0
	var miss_next: bool = false
	var dead: bool = false
	var dead_t: float = 0.0
	var gone: bool = false
	var engaged: bool = false
	var vx: float = 0.0
	var vy: float = 0.0
	var target: Unit = null
	var face: int = 1
	var walking: bool = false
	var phase: float = 0.0
	var odo: float = 0.0          # ground covered, for units whose walk frames follow their feet (T.stride)
	var alt: float = 0.0
	var base_alt: float = 0.0
	var boost: float = 0.0
	var stun: float = 0.0
	var super_used: bool = false
	var riders: Array = []          # Alamosaurus riders: {fx, fy, cd, aiming, att: Unit}
	var fleeing: bool = false
	var wall_ref = null             # the ShieldWall this knight stands in
	var slot: int = 0
	var hide = null                 # the ShieldWall this unit shelters behind
	var hide_slot: int = 0
	var charged: bool = false
	var shots: int = 0
	var shot_mult: float = 1.0
	var stun_next: bool = false
	var arm: String = "r"
	var leg: String = "n"
	var charge_used: bool = false
	var charge_t: float = 0.0
	var charge_hit: bool = false
	var rcharge: bool = false       # Rhino Charge: thundering through the enemy army
	var rcharge_wait: bool = false  # ...or still on its way out from behind its own walls
	var trampled: Dictionary = {}
	var stuck_t: float = 0.0
	var chk_t: float = 0.0
	var chk_x: float = 0.0
	var last_x: float = 0.0
	var last_y: float = 0.0
	var shout_t: float = 0.0        # Palaeoloxodon: rearing up and trumpeting
	var alt2: bool = false          # Palaeoloxodon: stomp, then head swing, in turn
	var delayed: bool = false
	var dust_t: float = 0.0
	var miss_volley: bool = false
	var hit_key: String = ""        # set for Alamosaurus riders ("rider")
	var is_rider: bool = false
	# Laser Tank
	var shots_left: int = -1
	var cool: float = 0.0
	var beam_on: bool = false
	var beam_t: float = 0.0
	var ticks: int = 0
	var spot: Vector2 = Vector2.ZERO
	var has_spot: bool = false
	var plan: Vector2 = Vector2.ZERO
	var has_plan: bool = false
	var plan_t: float = 0.0
	var aim: float = 0.0
	var aim_set: bool = false
	# Gunship
	var gun_aim: float = 0.0
	var gun_set: bool = false
	# looks only
	var spin: float = 0.0
	var enter_t: float = 0.0
	var stomp_t: float = -1.0
	var stomp_leg: String = ""
	# Trees map
	var hid: bool = false
	var hid_since: float = 0.0
	var burst_ready: float = 0.0
	var tp_set: bool = false        # its current route through the trees
	var tp_t: float = 0.0
	var tp_tx: float = 0.0
	var tp_ty: float = 0.0
	var tp_wp: Vector2 = Vector2.ZERO
	var tp_has_wp: bool = false
	var ts_tree: int = -1           # the side it keeps to round a tree
	var ts_s: int = 1
	var ts_t: float = 0.0
	# high ground (Mountain shelves; later the walls): which level it's on, or climbing up to / down from (-1: none)
	var on_wall: int = -1
	var climbing: int = -1
	var descending: int = -1
	var wall_goal: int = -1         # the shelf it's heading for, to take its spot there
	var slot_w: int = -1            # its spot: shelf and slot
	var slot_i: int = -1
	var pass_pts: Array = []        # coming down a mountain pass from reserve: the points still to walk
	var pass_i: int = 0
	var pass_shelf: int = -1
	var burst_pending: bool = false
	# Castle map
	var is_ballista: bool = false
	var kick: float = 0.0
	var stand_y: float = 0.0
	var gate_swing: bool = false
	var in_fort: bool = false
	var rt_set: bool = false        # its current way round the walls
	var rt_t: float = 0.0
	var rt_d: Vector2 = Vector2.ZERO
	var rt_p: Vector2 = Vector2.ZERO
	# Dinosaurs (2026-11-06 rewrite) and the Mythical
	var mcharge: bool = false       # Minotaur: charging until its first hit
	var pcharge: bool = false       # Pachycephalosaurus: charging until its first hit
	var tcharge: bool = false       # Triceratops: its opening charge, until it reaches the enemy line
	var lane: Unit = null           # Triceratops: the enemy Rhino whose lane it keeps to while that Rhino charges
	var slowed: bool = false        # head-butted by a Pachycephalosaurus: slower for the rest of the battle
	var slow_spd: float = 0.0
	var slow_rate: float = 0.0
	var down_t: float = -1.0        # a flyer knocked to the ground by a Dilophosaurus, until this time
	var grounded: bool = false      # a Griffin or Dragon that has landed (it stays on the ground)
	var last_shot: int = -1         # never attacks the same enemy twice in a row (Pachycephalosaurus, Dilophosaurus)
	var ignore_t: int = -1          # Robot Longbow: a target it has given up on (a Triceratops)
	var no_dmg: int = 0
	var no_dmg_t: int = -1
	var miss_shots: int = 0         # Griffin screech: shots still to miss
	var morph_t: float = 0.0        # Mage: time toward its next try at making a Minotaur
	var fire_at: float = -1.0       # Dragon: when it can breathe fire next
	var fire_n: int = 0
	var force_stun: float = -1.0    # a Minotaur's charge stuns even the stun-immune, until this time
	var burn_until: float = 0.0     # caught in the Dragon's fire streak
	var burn_acc: float = 0.0
	var burn_by: int = 0
	var burn_dps: float = 0.0
	var swoop: Dictionary = {}      # Dragon fire run at the start of the battle (empty: none)
	var gswoop: Dictionary = {}     # Griffin swoop to the enemy's front line (empty: none)
	var is_pseudo: bool = false     # a stand-in attacker: fire, or the blow of a Minotaur's charge
	var wph: float = -1.0           # looks only: a flyer's own steady wing-beat clock


class ShieldWall:
	var team: int = 0
	var face: int = 1
	var knights: Array = []
	var ys: Array = []
	var x: float = 0.0
	var hp: float = 30.0
	var broken: bool = false
	var broken_t: float = 0.0
	var hidden: Array = []
	var flash: float = 0.0
	var T: Dictionary = {}
	var mx: float = 0.0
	var my: float = 0.0


class Shot:
	var att: Unit
	var t: Unit
	var miss: bool = false
	var mult: float = 1.0
	var stun: float = 0.0
	var kind: String = "arrow"       # arrow, short, laser, rocket
	var air: bool = false
	var spd: float = 60.0
	var off: Vector2 = Vector2.ZERO
	var x: float = 0.0
	var y: float = 0.0
	var aim: Vector2 = Vector2.ZERO
	var ang: float = 0.0
	var team: int = 0
	var sx: float = 0.0             # where it was shot from on the ground, and its spot on the ground as it flies
	var sy: float = 0.0
	var gx: float = 0.0
	var gy: float = 0.0
	var big: bool = false           # a ballista's shot (drawn longer)


var rng := RandomNumberGenerator.new()
var F: Array = []                 # every unit on the field
var shots: Array = []             # arrows, lasers and rockets in flight
var walls: Array = []             # Robot Knight shield walls
var RES: Array = [[], []]         # each side's reserve, in the order they come in
var stance: Array = ["attack", "attack"]
var esc: Array = [{"n": 0, "hp": 0.0, "k": {}}, {"n": 0, "hp": 0.0, "k": {}}]
var retreat: int = -1
var over: bool = false
var stalemate: bool = false
var clock: float = 0.0
var last_hit: float = 0.0
var uid: int = 0
var hide_t: float = 0.5
var hp0: Array = [1.0, 1.0]
var ai_teams: Array = [1]
var fx: Array = []                # things for the screen to show once: dust, quakes, flashes, booms, shakes
var factions: Array = ["Dinosaurs", "Robots"]
## Crown & Coin abilities brought into a battle (none in a plain Arena battle):
##   Offline (Robots): a sneak attack. sneak is the attacking team; the other side can't attack until it lands its first hit.
##     (A Dinosaur Herd blocks it: Crown & Coin just doesn't send it.)
##   Update (Robots): mod_plus extra damage on every hit and mod_mult more damage, per team.
var ai_level: String = "medium"
var rally: Array = [false, false]    # War Trumpet: whose Mammals are rallied
var cursed: Array = [false, false]   # ...and whose army is shaken (their next attack misses)
var shouted: bool = false   # the computer's difficulty, for how it commands its army
var sneak: int = -1
var sneak_hit: bool = false
var mod_plus: Array = [0, 0]
var mod_mult: Array = [1.0, 1.0]
var mod_hp: Array = [1.0, 1.0]   # Armor (the Dinosaurs' The Hunt): +10% health for that team
var _sneak_t: float = -1.0


# =====================================================================
# Setting up
# =====================================================================

## counts: [blue, red], each {arena_unit_key: count}.
## map: open, ferns or trees. hold: the side holding the map (the defender).
func setup(counts: Array, seed_value: int = -1, ai: Array = [1], map_name: String = "open", hold: int = 0, mods: Dictionary = {}) -> void:
	sneak = int(mods.get("sneak", -1)); sneak_hit = false; _sneak_t = -1.0
	mod_plus = [0, 0]; mod_mult = [1.0, 1.0]; mod_hp = [1.0, 1.0]
	for t in 2:
		mod_plus[t] = int(mods.get("plus", [0, 0])[t])
		mod_mult[t] = float(mods.get("mult", [1.0, 1.0])[t])
		mod_hp[t] = float(mods.get("hp", [1.0, 1.0])[t])
	if seed_value >= 0:
		rng.seed = seed_value
	else:
		rng.randomize()
	ai_teams = ai
	F.clear(); shots.clear(); walls.clear(); fx.clear(); fires.clear()
	map = map_name
	HOLD = hold if HELD_MAPS.has(map) else 0
	trees = []; ferns = []; _grids = {}
	mside = false; levels = []; pass_turn = 0
	fort = {}; bal = []; bal_att = null; path_rect = Rect2(); _rects_cache = {}; treb_spots = []
	if map == "trees":
		_make_trees()
	elif map == "ferns":
		_make_ferns(true)
	elif map == "mountain":
		_make_mountainside()
	elif map == "castle":
		_make_castle()
	elif map == "fortress":
		_make_fortress()
	RES = [[], []]
	stance = ["attack", "attack"]
	esc = [{"n": 0, "hp": 0.0, "k": {}}, {"n": 0, "hp": 0.0, "k": {}}]
	retreat = -1; over = false; stalemate = false; clock = 0.0; last_hit = 0.0; uid = 0; hide_t = 0.5
	rally = [false, false]; cursed = [false, false]; shouted = false
	for team in 2:
		var c: Dictionary = counts[team]
		var list: Array = _mix_list(c)
		var WK: String = "rknight" if c.get("rknight", 0) >= int(TYPES.rknight.wall.size) else ""
		if team == HOLD and not fort.is_empty():   # the castle's knights start behind its walls with everyone else
			WK = ""
		if WK != "":
			list = list.filter(func(k): return k == WK) + list.filter(func(k): return k != WK)
		# Rhinos always start on the field (their Charge opens the battle)
		list = list.filter(func(k): return TYPES[k].get("fieldFirst", false)) + list.filter(func(k): return not TYPES[k].get("fieldFirst", false))
		var backs_keys: Array = ORDER.filter(func(k): return TYPES[k].get("back", false))
		list = list.filter(func(k): return backs_keys.has(k)) + list.filter(func(k): return not backs_keys.has(k))
		var parts: Array = _split_field(list)
		var first: Array = parts[0]
		RES[team] = parts[1]
		var backs: Array = first.filter(func(k): return TYPES[k].get("back", false))
		first = first.filter(func(k): return not TYPES[k].get("back", false))
		var n_walls: int = 0
		if WK != "":
			var WS: Dictionary = TYPES[WK].wall
			n_walls = mini(int(WS.max), first.filter(func(k): return k == WK).size() / int(WS.size))
			var take: int = n_walls * int(WS.size)
			var kept: Array = []
			for k in first:
				if k == WK and take > 0:
					take -= 1
				else:
					kept.append(k)
			first = kept
		# shuffled, then melee in front, flyers next, archers at the back (a stable sort, as in the browser)
		var ordered: Array = first.duplicate()
		for i in range(ordered.size() - 1, 0, -1):
			var j: int = int(rng.randf() * (i + 1))
			var tmp = ordered[i]; ordered[i] = ordered[j]; ordered[j] = tmp
		var indexed: Array = []
		for i in ordered.size():
			indexed.append([ordered[i], i])
		indexed.sort_custom(func(a, b): return int(TYPES[a[0]].rank) < int(TYPES[b[0]].rank) or (int(TYPES[a[0]].rank) == int(TYPES[b[0]].rank) and a[1] < b[1]))
		ordered = indexed.map(func(p): return p[0])
		if n_walls > 0:
			_build_walls(team, WK, n_walls)
		var n_out: int = 0
		for i in backs.size():
			var key: String = backs[i]
			var T: Dictionary = TYPES[key]
			var h: float = float(T.w) * float(T.ratio)
			var top: float = h + 1.0
			var bot: float = AH - 1.5
			var by: float = top + (bot - top) * (i + 1) / (backs.size() + 1)
			var bx: float = float(T.w) / 2.0 if team == HOLD else AW - float(T.w) / 2.0
			if mside and team == HOLD:   # on the mountain: just off the rock
				bx = _ms_keep_T(T, by) + 0.5
			if not fort.is_empty() and team == HOLD:   # the castle: out in front of its walls
				var op: Vector2 = _out_pos(T, n_out)
				n_out += 1
				bx = op.x
				by = op.y
			var u: Unit = _add_unit(team, key, bx, by, false)
			u.cool = float(T.beam.startDelay)
		var n: int = ordered.size()
		var rows: int = maxi(1, mini(n, 9))
		var cols: int = int(ceil(float(n) / rows))
		var step: float = minf(5.5, 20.0 / (cols - 1)) if cols > 1 else 5.5
		var has_wall: bool = walls.any(func(w): return w.team == team)
		if team == HOLD and not levels.is_empty():
			# the side holding the mountain or the castle: its shooters start up high, spread so each part gets a mix
			# (castle: the centre wall first, then along both angled walls in turn)
			var k: int = 0
			var cap: int = 0
			var order_slots: Array = []
			for wi0 in levels.size():
				cap += levels[wi0].slots.size()
				for si0 in levels[wi0].slots.size():
					order_slots.append([wi0, si0, float(levels[wi0].get("pri", 0)) + float(si0) / levels[wi0].slots.size()])
			order_slots.sort_custom(func(a, b): return a[2] < b[2])
			var i2: int = 0
			while i2 < ordered.size() and k < cap:
				var T2: Dictionary = TYPES[ordered[i2]]
				if not T2.get("ranged", false) or T2.get("flying", false):
					i2 += 1
					continue
				var wi: int = k % levels.size()
				var si: int = k / levels.size()
				if not fort.is_empty():
					wi = order_slots[k][0]
					si = order_slots[k][1]
				var sl: Dictionary = levels[wi].slots[si]
				var su: Unit = _add_unit(team, ordered[i2], float(sl.x), float(sl.y), false)
				su.on_wall = wi
				_take_slot(su, wi, si)
				su.wall_goal = -1
				ordered.remove_at(i2)
				k += 1
			if not fort.is_empty():   # the Alamosaurus starts out in front of the castle too
				for i3 in range(ordered.size() - 1, -1, -1):
					if ordered[i3] == "alamo" or ordered[i3] == "rtank":
						var op2: Vector2 = _out_pos(TYPES[ordered[i3]], n_out)
						n_out += 1
						_add_unit(team, ordered[i3], op2.x, op2.y, false)
						ordered.remove_at(i3)
			n = ordered.size()
			rows = maxi(1, mini(n, 9))
		var cols2: int = int(ceil(float(n) / rows))
		for i in n:
			var c2: int = i / rows
			var r: int = i % rows
			var col_x: float = maxf(4.0, (17.0 if has_wall else 24.0) - step * c2)
			var x: float = (col_x if team == HOLD else AW - col_x) + _rnd(-2, 2)
			var y: float = 7.0 + (AH - 9.0) * (r + 0.5 + (c2 % 2) * 0.3 + _rnd(-0.32, 0.32)) / rows
			if mside and team == HOLD:   # lined up along the mountain's foot, the front rank furthest out
				x = _ms_keep_T(TYPES[ordered[i]], y) + 1.2 + step * (cols2 - 1 - c2) + _rnd(-0.6, 0.6)
			if not fort.is_empty() and team == HOLD and fort.castle:   # inside the castle
				x = maxf(3.5, 20.0 - step * c2) + _rnd(-2, 2)
				y = 15.0 + 31.0 * (r + 0.5 + (c2 % 2) * 0.3) / rows + _rnd(-1.1, 1.1)
			elif not fort.is_empty() and team == HOLD:   # behind the fortress's walls
				x = maxf(3.5, (WALL_X0 - 18.0) - step * c2) + _rnd(-2, 2)
			_add_unit(team, ordered[i], x, y, false)
	_line_up_trikes()
	_assign_hiders(true)
	for t in 2:
		var total: float = 0.0
		for f in _alive(t):
			total += maxf(0.0, f.hp)
		for k in RES[t]:
			total += float(TYPES[k].hp)
		hp0[t] = maxf(1.0, total)


func _rnd(a: float, b: float) -> float:
	return a + rng.randf() * (b - a)


## Spread unit types evenly through the army list, so the field and the reserve keep the same mix.
func _mix_list(c: Dictionary) -> Array:
	var out: Array = []
	var done: Dictionary = {}
	var total: int = 0
	for k in ORDER:
		done[k] = 0
		total += int(c.get(k, 0))
	for i in total:
		var best: String = ""
		var bv: float = INF
		for k in ORDER:
			var ck: int = int(c.get(k, 0))
			if done[k] < ck:
				var v: float = (done[k] + 0.5) / ck
				if v < bv:
					bv = v
					best = k
		done[best] += 1
		out.append(best)
	return out


func _slot(k: String) -> float:
	return float(TYPES[k].get("slot", 1))


## The first units in the list that fit on the field; the rest wait in reserve.
func _split_field(list: Array) -> Array:
	var used: float = 0.0
	var full: bool = false
	var first: Array = []
	var rest: Array = []
	var n: Dictionary = {}
	for k in list:
		var cap: int = int(TYPES[k].get("fieldMax", 0))
		var capped: bool = cap > 0 and int(n.get(k, 0)) >= cap
		if not full and not capped and used + _slot(k) <= FIELD_MAX + 1e-9:
			first.append(k)
			used += _slot(k)
			n[k] = int(n.get(k, 0)) + 1
		else:
			rest.append(k)
			if not capped:
				full = true
	return [first, rest]


func _add_unit(team: int, key: String, x: float, y: float, entering: bool) -> Unit:
	var T: Dictionary = TYPES[key]
	var u := Unit.new()
	u.id = uid
	uid += 1
	u.team = team
	u.key = key
	u.T = T
	u.h = float(T.w) * float(T.ratio)
	u.x = x
	u.y = y
	u.hp = unit_hp(team, key)
	u.armor = T.get("armor", {}).duplicate()
	u.cd = _rnd(0.15, 1.1)
	u.face = 1 if team == HOLD else -1
	u.phase = _rnd(0, 6)
	u.alt = ALT if T.get("flying", false) else 0.0
	u.base_alt = u.alt
	u.boost = float(T.entryBurst.dur) if (entering and T.has("entryBurst")) else 0.0
	u.enter_t = 0.5 if entering else 0.0
	u.burst_pending = entering and T.has("entryBurst") and not fort.is_empty() and team == HOLD
	u.miss_next = cursed[team]   # comes in after a War Trumpet: its first attack misses
	if cursed[team] and T.has("beam"):
		u.cool += 2.0
		u.delayed = true
	u.mcharge = T.has("mcharge")
	u.pcharge = T.has("pcharge")
	u.tcharge = T.has("tcharge") and not entering
	if T.has("swoop") and not entering:
		u.swoop = {"st": 0}
	if T.has("gswoop") and not entering:
		u.gswoop = {"st": 0}
	u.rcharge = T.has("rhinoCharge") and not entering and not _behind_own_walls(team)
	u.rcharge_wait = T.has("rhinoCharge") and not entering and _behind_own_walls(team)
	u.last_x = x
	u.last_y = y
	u.chk_x = x
	if T.has("riders"):
		for p in T.riders:
			var rider := Unit.new()
			rider.T = TYPES[T.riderType]
			rider.key = String(T.riderType)
			rider.team = team
			rider.hit_key = "rider"
			rider.is_rider = true
			u.riders.append({"fx": p[0], "fy": p[1], "cd": _rnd(0.3, 1.2), "aiming": false, "att": rider})
	F.append(u)
	return u


func _alive(team: int) -> Array:
	return F.filter(func(f): return f.team == team and not f.dead)


# =====================================================================
# Robot Knight shield walls: every 3 knights lock shields (up to 4 walls). Arrows and lasers bounce off;
# 6 other units shelter behind each wall; only melee breaks it (30 health), then its knights are stunned 1s.
# =====================================================================

func _build_walls(team: int, WK: String, n: int) -> void:
	var T: Dictionary = TYPES[WK]
	var WS: Dictionary = T.wall
	var face: int = 1 if team == HOLD else -1
	var off: float = 27.0
	if team == HOLD and not trees.is_empty():
		off = FOREST_X + 5.0
	elif team == HOLD and mside:
		off = MS_FOOT.max() + 6.0
	var x0: float = off if team == HOLD else AW - off
	var dy: float = 3.8
	var gap_w: float = 1.4
	var k: int = n * int(WS.size)
	var top: float = float(T.w) * float(T.ratio) + 1.5
	var mid: float = (top + AH - 1.5) / 2.0
	for w in n:
		var W := ShieldWall.new()
		W.team = team
		W.face = face
		W.x = x0
		W.hp = float(WS.hp)
		W.T = T
		for j in int(WS.size):
			var idx: int = w * int(WS.size) + j
			var yy: float = mid + (idx - (k - 1) / 2.0) * dy + (w - (n - 1) / 2.0) * gap_w
			W.ys.append(yy)
			var f: Unit = _add_unit(team, WK, x0, yy, false)
			f.wall_ref = W
			f.slot = j
			W.knights.append(f)
		walls.append(W)


func _slot_pos(W: ShieldWall, i: int) -> Vector2:
	var row: int = i % 3
	var col: int = i / 3
	return Vector2(W.x - W.face * (6.5 + col * 4.5), float(W.ys[row]) + (1.3 if col > 0 else -1.3))


func _hide_slot(f: Unit) -> Vector2:
	return _slot_pos(f.hide, f.hide_slot)


func _wall_slot(f: Unit) -> Vector2:
	return Vector2(f.wall_ref.x, float(f.wall_ref.ys[f.slot]))


## Shielded from arrows and lasers: knights in a standing wall, and units sheltering in their spot behind one.
func shielded(o: Unit) -> bool:
	if o.wall_ref != null and not o.wall_ref.broken:
		return true
	return o.hide != null and not o.hide.broken and Vector2(o.x, o.y).distance_to(_hide_slot(o)) < 3.0


func _assign_hiders(start: bool) -> void:
	var open: Array = []
	for W in walls:
		if W.broken:
			continue
		W.hidden = W.hidden.filter(func(h): return not h.dead and h.hide == W)
		for i in int(W.T.wall.hide):
			if not W.hidden.any(func(h): return h.hide_slot == i):
				open.append({"W": W, "i": i})
	if open.is_empty():
		return
	open.sort_custom(func(a, b): return a.i < b.i)
	for ranged in [true, false]:
		var cand: Array = F.filter(func(f): return not f.dead and not f.T.get("flying", false) and not f.T.has("wall") and not f.T.get("noHide", false) and f.hide == null and f.wall_ref == null and f.on_wall < 0 and f.wall_goal < 0 and f.pass_pts.is_empty() and f.climbing < 0 and bool(f.T.get("ranged", false)) == ranged and (ranged or start or not f.engaged))
		for n in open.size():
			if cand.is_empty():
				break
			var o = open[n]
			if o == null:
				continue
			var W: ShieldWall = o.W
			var sp: Vector2 = _slot_pos(W, o.i)
			var best: Unit = null
			var bd: float = 1e9
			for f in cand:
				if f.team != W.team:
					continue
				if not ranged and not start and (W.x - f.x) * W.face < 0:
					continue
				var d: float = Vector2(f.x, f.y).distance_to(sp)
				if d < bd:
					bd = d
					best = f
			if best == null:
				continue
			best.hide = W
			best.hide_slot = o.i
			W.hidden.append(best)
			if start:
				best.x = sp.x
				best.y = sp.y
			cand.erase(best)
			open[n] = null


## split: the wall comes apart against the mountain (no stun)
func _break_wall(W: ShieldWall, split: bool = false) -> void:
	if W.broken:
		return
	W.broken = true
	for k in W.knights:
		k.wall_ref = null
		if not k.dead and not split:
			k.stun = maxf(k.stun, float(W.T.wall.stun))
	for h in W.hidden:
		h.hide = null


func _update_walls(dt: float) -> void:
	hide_t -= dt
	if hide_t <= 0:
		hide_t = 0.5
		_assign_hiders(false)
	for W in walls:
		W.mx = 0.0
		W.my = 0.0
		if W.broken:
			W.broken_t += dt
			continue
		if W.knights.any(func(k): return k.dead) or stance[W.team] == "flee":
			_break_wall(W)
			continue
		if stance[W.team] == "hold":
			continue
		W.flash = maxf(0.0, W.flash - dt)
		var T: Dictionary = W.T
		var enemies: Array = F.filter(func(o): return o.team != W.team and not o.dead and not o.T.get("flying", false))
		if enemies.is_empty() or W.knights.any(func(k): return k.stun > 0):
			continue
		var reached: bool = false
		for k in W.knights:
			for o in enemies:
				if gap(k, o) <= float(T.range):
					reached = true
		if reached:
			continue
		# march at half speed toward the nearest enemy on the ground, sliding up or down past either end
		var n: int = W.ys.size()
		var cy: float = (float(W.ys[0]) + float(W.ys[n - 1])) / 2.0
		var tg: Unit = null
		var bd: float = 1e9
		for o in enemies:
			var d: float = Vector2(o.x - W.x, o.y - cy).length()
			if d < bd:
				bd = d
				tg = o
		var gx: float = tg.x - W.face * float(T.range) * 0.5 - W.x
		var gy: float = 0.0
		if tg.y < float(W.ys[0]):
			gy = tg.y - float(W.ys[0])
		elif tg.y > float(W.ys[n - 1]):
			gy = tg.y - float(W.ys[n - 1])
		var length: float = Vector2(gx, gy).length()
		if length < 0.2:
			continue
		var step: float = minf(length, float(T.speed) * float(T.wall.speedMult) * dt)
		var x0: float = W.x
		W.x = clampf(W.x + gx / length * step, 4.0, AW - 4.0)
		W.mx = W.x - x0
		var sy: float = gy / length * step
		var top: float = float(T.w) * float(T.ratio) + 1.5
		var lo: float = top - float(W.ys[0])
		var hi: float = AH - 1.5 - float(W.ys[n - 1])
		for o in walls:
			if o == W or o.team != W.team or o.broken:
				continue
			if float(o.ys[0]) >= float(W.ys[n - 1]):
				hi = minf(hi, float(o.ys[0]) - 3.8 - float(W.ys[n - 1]))
			elif float(o.ys[o.ys.size() - 1]) <= float(W.ys[0]):
				lo = maxf(lo, float(o.ys[o.ys.size() - 1]) + 3.8 - float(W.ys[0]))
		sy = maxf(minf(sy, maxf(0.0, hi)), minf(0.0, lo))
		for i in n:
			W.ys[i] = float(W.ys[i]) + sy
		W.my = sy
		if mside and W.knights.any(func(kn): return kn.x <= _ms_keep(kn) + 0.8):
			_break_wall(W, true)
		if not fort.is_empty():   # a shield wall that marches into the stone breaks up; the knights find their own way round
			for j in n:
				for rr in _wall_rects(W.knights[j]):
					if W.x > rr.x0 and W.x < rr.x1 and float(W.ys[j]) > rr.y0 and float(W.ys[j]) < rr.y1:
						_break_wall(W, true)


# =====================================================================
# Targets and damage
# =====================================================================

func _flying(u: Unit) -> bool:
	return u.T.get("flying", false)


## (the forest hides ground units from arrows, lasers and rockets, but not from the Laser Tank's beam or from melee;
## a Dragon on its fire run can't be shot; a flyer that is on the ground can be hit by anyone)
func can_hit(f: Unit, o: Unit) -> bool:
	if not o.pass_pts.is_empty():
		return false
	if soaring_over(o) and _shooter(f):
		return false
	if _flying(o) and not f.T.get("antiAir", false) and not downed(o):
		return false
	if f.T.has("beam"):   # the forest doesn't hide anyone from the Laser Tank's beam; the castle does
		return fort.is_empty() or _flying(o) or fort_fade(o) >= 0.5
	return not (_shooter(f) and hidden_in(o))


func _shooter(f: Unit) -> bool:
	return f.T.get("ranged", false) or f.T.get("rocket", false)


func _prio(f: Unit, o: Unit) -> int:
	if f.T.get("preferGround", false):
		return 0 if _flying(o) else 1
	if f.T.get("preferAir", false):   # Dilophosaurus: flyers still in the air first
		return 1 if (_flying(o) and not downed(o)) else 0
	if f.T.get("preferMelee", false):
		return 1 if (not o.T.get("ranged", false) and not _flying(o)) else 0
	return 0


func dist(a: Unit, b: Unit) -> float:
	return Vector2(a.x - b.x, a.y - b.y).length()


## The gap between two units' bodies: big units have a footprint, everyone else is a point.
func gap(a: Unit, b: Unit) -> float:
	var gx: float = maxf(0.0, absf(b.x - a.x) - float(a.T.get("footX", 0)) - float(b.T.get("footX", 0)))
	var gy: float = maxf(0.0, absf(b.y - a.y) - float(a.T.get("footY", 0)) - float(b.T.get("footY", 0)))
	return Vector2(gx, gy).length()


func _min_y(f: Unit) -> float:
	return f.h + 1.0 + (f.base_alt + 1.0 if _flying(f) else 0.0)


## The Gunship never comes down: near the top edge, a ground unit further up still counts as in reach when close sideways.
func _reach_gap(f: Unit, o: Unit) -> float:
	var g: float = gap(f, o)
	if not f.T.get("hover", false) or _flying(o):
		return g
	if f.y <= _min_y(f) + 0.6 and o.y < f.y:
		return maxf(0.0, absf(o.x - f.x) - float(o.T.get("footX", 0)))
	return g


func _pick_target(f: Unit) -> Unit:
	var best: Unit = null
	var bp: float = -1e9
	var bd: float = 1e9
	for o in F:
		if o.team == f.team or o.dead or not can_hit(f, o):
			continue
		if _out_of_reach(f, o):   # up on a shelf, and this one is too big for the steps
			continue
		if is_dino(f) and charging(o) and _reach_gap(f, o) > range_of(f):   # Dinosaurs don't chase a charging enemy running past
			continue
		var p: float = _prio(f, o) - (2.0 if (f.T.get("ranged", false) and shielded(o)) else 0.0)
		if f.T.get("noRepeat", false) and o.id == f.last_shot:
			p -= 5.0
		if f.ignore_t == o.id:
			p -= 5.0
		if f.on_wall >= 0 and f.T.get("ranged", false) and _reach_gap(f, o) <= range_of(f):
			p += 10.0   # high-ground shooters take what they can reach first
		var d: float = dist(f, o)
		if p < bp or (p == bp and d >= bd):
			continue
		if (not trees.is_empty() or not fort.is_empty()) and f.T.get("ranged", false) and not clear_shot(f, o):   # rather something with nothing in the way
			p -= 0.5
		if p > bp or (p == bp and d < bd):
			bp = p
			bd = d
			best = o
	if f.T.get("ranged", false) or _flying(f):   # castle ballistas: only shooters and flyers can reach them
		for o in bal:
			if o.team == f.team or o.dead:
				continue
			var p2: float = 0.0
			if f.T.get("ranged", false) and not clear_shot(f, o):
				p2 -= 0.5
			if f.on_wall >= 0 and f.T.get("ranged", false) and _reach_gap(f, o) <= range_of(f):
				p2 += 10.0
			var d2: float = dist(f, o)
			if p2 > bp or (p2 == bp and d2 < bd):
				bp = p2
				bd = d2
				best = o
	return best


## The sneak attack also ends if the attackers have nothing left that can hurt the defenders (Brawlers against flyers, say).
func _sneak_can_land() -> bool:
	var me: Array = []
	var foe: Array = []
	for f in F:
		if not f.dead and not f.is_ballista:
			(me if f.team == sneak else foe).append(f.T)
	for k in RES[sneak]:
		me.append(TYPES[k])
	for k in RES[1 - sneak]:
		foe.append(TYPES[k])
	if me.is_empty():
		return false
	for T in foe:
		if not T.get("flying", false):
			return true
	for T in me:
		if T.get("antiAir", false) or (T.has("riders") and TYPES[T.riderType].get("antiAir", false)):
			return true
	return false


## Is f held back by the other side's sneak attack?
func held(f: Unit) -> bool:
	if sneak < 0 or sneak_hit or f.team == sneak:
		return false
	if _sneak_t != clock:
		_sneak_t = clock
		if not _sneak_can_land():
			sneak_hit = true
	return not sneak_hit


func hit(t: Unit, att: Unit, mult: float = 1.0, proj: bool = false, how: String = "") -> bool:
	var sure: bool = att.T.has("beam")   # the Laser Tank's beam can't miss and nothing blocks it (fire and a Minotaur's charge kill work the same way)
	var from_wall: bool = att.on_wall >= 0 or att.key == "ballista"   # shooters up on a wall or tower, and ballistas
	if t.T.get("noProj", false) and from_wall and not sure and (proj or att.T.get("ranged", false) or att.T.get("rocket", false)):
		mult *= 0.5   # Triceratops: shots from walls do half damage
	elif t.T.get("noProj", false) and not sure and (proj or att.T.get("ranged", false) or att.T.get("rocket", false)):
		# Triceratops: shots and spells can't hurt it, except the Laser Tank's beam (a Robot Longbow gives up on it after 2 shots)
		if att.T.get("retargetNoDmg", false):
			att.no_dmg = (att.no_dmg if att.no_dmg_t == t.id else 0) + 1
			att.no_dmg_t = t.id
			var per: int = (att.T.gun as Array).size() if att.T.has("gun") else 1
			if att.no_dmg >= 2 * per:
				att.ignore_t = t.id
				att.target = null
				att.no_dmg = 0
		return false
	if t.T.has("dodgeCharge") and (att.rcharge or att.charge_hit or att.pcharge or att.mcharge) and rng.randf() < float(t.T.dodgeCharge):
		return false   # Dilophosaurus: jumps aside from half the hits of a charging enemy
	if proj and soaring_over(t):
		return false   # shots already in the air miss a Dragon soaring over
	if not sure:
		if proj and shielded(t):
			return false
		if t.T.has("dodge") and rng.randf() < float(t.T.dodge):
			return false
		if _high(t) and rng.randf() < WALL_DODGE:   # up high: 10% of attacks miss
			return false
	var k: String = att.hit_key if att.hit_key != "" else String(att.T.hitKey)
	if not sure:
		if att.T.has("missHeavy") and t.T.get("heavy", false) and rng.randf() < float(att.T.missHeavy):
			return false
		var shared: String = "archer" if k == "rider" else ""
		if int(t.armor.get(k, 0)) > 0 and (shared == "" or int(t.armor.get(shared, 0)) > 0):
			t.armor[k] = int(t.armor[k]) - 1
			if shared != "":
				t.armor[shared] = int(t.armor[shared]) - 1
			return false
		var deflect: Dictionary = t.T.get("deflect", {})
		if deflect.has(k) and rng.randf() < float(deflect[k]):
			return false
	var dmg_f: float = float(att.T.dmg) + (0.0 if sure else float(mod_plus[att.team])) + (2.0 if rallied(att) else 0.0) + (WALL_DMG if att.on_wall >= 0 else 0.0) + (FORT_DMG if fort_buff(att.team) else 0.0) + float(att.T.get("bonus", {}).get(t.key, 0))
	if att.T.has("bigDmg") and is_large(t):   # Megaraptor: 20 to large units
		dmg_f += float(att.T.bigDmg) - float(att.T.dmg)
	if _flying(t):
		dmg_f += float(att.T.get("bonusAir", 0))
	if not t.T.get("ranged", false):
		dmg_f += float(att.T.get("bonusMelee", 0))
	if t.T.get("basic", false):
		dmg_f += float(att.T.get("bonusBasic", 0))
	var dmg: int = roundi(dmg_f * mult * float(mod_mult[att.team]))
	var reduce: Dictionary = t.T.get("reduce", {})
	if reduce.has(k):
		dmg = maxi(1, dmg - int(reduce[k]))
	if dmg == 0 and sure:
		dmg = 1
	if dmg == 0:
		return false
	if sneak >= 0 and att.team == sneak and not sneak_hit:
		sneak_hit = true   # Offline: the defenders can fight back from now on
	if t.wall_ref != null and not t.wall_ref.broken and not sure:   # melee blows land on the shield wall, not the knight
		var W: ShieldWall = t.wall_ref
		W.hp -= dmg
		W.flash = 0.16
		t.flash = 0.16
		last_hit = clock
		if W.hp <= 0:
			_break_wall(W)
		return false
	if t.rcharge:   # Rhino Charge: nothing can stop it, even past 0 health
		t.hp -= dmg
		t.flash = 0.16
		last_hit = clock
		return true
	t.hp = maxf(0.0, t.hp - dmg)
	t.flash = 0.16
	last_hit = clock
	if t.hp == 0:
		t.dead = true
		t.target = null
		t.beam_on = false
	if t.T.has("quills") and not proj and how != "breath" and not att.is_pseudo and not att.is_rider and not att.is_ballista and not _shooter(att) and not sure:
		_quill_back(att, int(t.T.quills))   # Porcupine quills
	return true


## Porcupine quills: a melee attacker that lands a hit on a Porcupine takes 1 damage back (straight to the unit, past any armor or
## shield wall). A charging Rhino takes it too, and falls when its charge ends if that leaves it with no health.
func _quill_back(a: Unit, n: int) -> void:
	if a.dead:
		return
	a.hp -= n
	if not a.rcharge:
		a.hp = maxf(0.0, a.hp)
	a.flash = 0.16
	last_hit = clock
	if not a.rcharge and a.hp <= 0:
		a.dead = true
		a.target = null
		a.beam_on = false


## A stand-in attacker for damage that comes from no unit's own attack (the Dragon's fire, a Minotaur's charge kill).
func _pseudo(team: int, dmg: float, hk: String) -> Unit:
	var u := Unit.new()
	u.team = team
	u.T = {"dmg": dmg, "beam": true, "hitKey": hk}
	u.is_pseudo = true
	return u


func _stomp_around(f: Unit, t: Unit) -> void:
	var near: Array = F.filter(func(o): return o != t and not o.dead and o.team != f.team and not _flying(o) and gap(f, o) <= float(f.T.range) + 1.5)
	near.sort_custom(func(a, b): return gap(f, a) < gap(f, b))
	var hits: Array = near.slice(0, int(f.T.multi) - 1)
	for o in hits:
		hit(o, f)
	if f.T.has("knock"):
		_knock_back(f, t)
		for o in hits:
			_knock_back(f, o)
	if f.alt2:
		return   # a head swing shoves them back but doesn't shake the ground
	fx.append({"type": "quake", "x": f.x, "y": f.y, "w": float(f.T.w), "big": false})


# =====================================================================
# Mammals: Rhino Charge, the tusk sweep's shove and the War Trumpet
# =====================================================================

func rallied(f: Unit) -> bool:
	return rally[f.team] and String(f.T.get("faction", "")) == "Mammals"


func _behind_own_walls(team: int) -> bool:
	return not fort.is_empty() and team == HOLD


func _wall_exit() -> Vector2:
	return Vector2(float(fort.gateX) + 3.5, float(fort.gy)) if not fort.is_empty() else Vector2(AW / 2.0, AH / 2.0)


func _end_charge(f: Unit) -> void:
	f.rcharge = false
	if f.hp <= 0:   # it kept going on nothing but momentum: it drops where it stops
		f.hp = 0.0
		f.dead = true
		f.target = null
		last_hit = clock


## Rhino Charge: at the start of the battle each Rhino thunders straight through the enemy army to the far side, 50% faster,
## trampling every enemy on the ground it runs into: 20 damage to the first, 10 to each after (once each). At the far side it
## turns round and fights normally. If something stops it dead (a closed gate, the foot of the mountain) the charge ends there.
func _rhino_run(f: Unit, spd: float, dt: float) -> void:
	var T: Dictionary = f.T
	var dir: int = 1 if f.team == HOLD else -1
	var edge: float = AW - float(T.w) / 2.0 + 0.5 if dir > 0 else float(T.w) / 2.0 - 0.5
	if (edge - f.x) * dir <= 0.6:   # made it through: turn round (or fall)
		f.face = -dir
		f.target = null
		_end_charge(f)
		return
	# the nearest enemy on the ground still ahead of it, and not too far off to the side to swing over to
	var aim: Unit = null
	var best: float = 1e9
	for o in F:
		if o.team == f.team or o.dead or not o.pass_pts.is_empty() or _flying(o) or o.is_ballista or f.trampled.has(o.id):
			continue
		if not levels.is_empty() and not _same_level(f, o):
			continue
		var ax: float = (o.x - f.x) * dir
		var ay: float = absf(o.y - f.y)
		if ax < 1.0 or ay > ax * 1.2:
			continue
		var c: float = ax + ay * 1.5
		if c < best:
			best = c
			aim = o
	var g: Vector2 = Vector2(aim.x + dir * float(T.w) * 0.3, aim.y) if aim != null else Vector2(edge, f.y)
	if mside:
		g = Vector2(maxf(g.x, _ms_keep(f) + 1.0), g.y)
	elif not trees.is_empty():
		g = _path_to(f, g.x, g.y)
	elif not levels.is_empty():
		g = _goal_point(f, g.x, g.y, aim.on_wall if aim != null else -1)
	var ux: float = g.x - f.x
	var uy: float = g.y - f.y
	var ud: float = maxf(Vector2(ux, uy).length(), 1e-6)
	ux /= ud
	uy /= ud
	if ux * dir < 0.55:   # can't turn round: at most a wide swerve
		ux = dir * 0.55
		uy = (-1.0 if uy < 0 else 1.0) * sqrt(1.0 - 0.55 * 0.55)
	var st: float = spd * dt
	f.vx = ux * st
	f.vy = uy * st
	f.walking = true
	f.phase += dt * 9.0
	f.face = dir
	f.engaged = false
	f.target = null
	f.lunge = -1.0
	var moved: float = Vector2(f.x - f.last_x, f.y - f.last_y).length()
	f.last_x = f.x
	f.last_y = f.y
	f.stuck_t = f.stuck_t + dt if moved < st * 0.25 else 0.0
	f.chk_t += dt
	var no_way: bool = false
	if f.chk_t >= 0.6:   # hardly any headway in 0.6 s: it's up against something
		no_way = (f.x - f.chk_x) * dir < 0.5
		f.chk_t = 0.0
		f.chk_x = f.x
	if f.stuck_t > 0.8 or no_way:   # stopped dead: the charge is over
		if _gate_blocks(f, null):
			fort["hp"] = maxf(0.0, float(fort.hp) - float(T.rhinoCharge.dmg))
			fort["flash"] = 0.12
			if float(fort.hp) == 0.0:
				fort["broken"] = true
		_end_charge(f)
		return
	var rb: float = 2.0 if rallied(f) else 0.0
	for o in F:
		if o.team == f.team or o.dead or not o.pass_pts.is_empty() or _flying(o) or o.is_ballista or f.trampled.has(o.id):
			continue
		if not levels.is_empty() and not _same_level(f, o):
			continue
		if absf(o.x - f.x) <= float(T.w) * 0.42 + float(o.T.get("footX", float(o.T.w) * 0.25)) and absf(o.y - f.y) <= 1.8 + float(o.T.get("footY", 0.0)):
			if o.T.get("stopsCharge", false):   # a Triceratops stops it dead
				_end_charge(f)
				return
			var d: float = float(T.rhinoCharge.next) if not f.trampled.is_empty() else float(T.rhinoCharge.dmg)
			f.trampled[o.id] = true
			if o.wall_ref != null and not o.wall_ref.broken:   # a shield wall in its path is smashed apart
				_break_wall(o.wall_ref)
				last_hit = clock
				continue
			hit(o, f, (d + rb) / (float(T.dmg) + rb))


## Palaeoloxodon: pushes a struck ground unit a little way back (heavy units half as far); not off a wall, out of a shield
## wall, through a wall, into the rock or off the field.
func _knock_back(f: Unit, o: Unit) -> void:
	if o.dead or _flying(o) or o.on_wall >= 0 or o.climbing >= 0 or o.descending >= 0 or o.wall_ref != null or o.T.has("beam") or o.is_ballista:
		return
	var d: float = float(f.T.knock) * (0.5 if o.T.get("heavy", false) else 1.0)
	var dir: float = signf(o.x - f.x) if o.x != f.x else float(f.face)
	var nx: float = clampf(o.x + dir * d, 1.0, AW - 1.0)
	for r in _wall_rects(o):
		if _seg_hits(o.x, o.y, nx, o.y, r):
			return
	if mside and nx < _ms_keep(o):
		return
	if not fort.is_empty() and not fort.broken and absf(o.y - float(fort.gy)) < float(fort.half) + 1.5 and (o.x - float(fort.gateX)) * (nx - float(fort.gateX)) < 0:
		return
	o.x = nx


## Palaeoloxodon special move, War Trumpet: 2 seconds into the battle it rears its head and trumpets. Its side's Mammals get
## +2 damage, attack 0.2 s faster and move 15% faster for the rest of the battle; every enemy's next attack misses (a Laser
## Tank waits 2 more seconds before its first beam) and any enemy speed boost or Rhino Charge is lost.
func _war_trumpet(f: Unit) -> void:
	var W: Dictionary = f.T.trumpet
	var foe: int = 1 - f.team
	f.shout_t = float(W.dur)
	fx.append({"type": "roar", "x": f.x + f.face * float(f.T.w) * (0.708 - 0.5), "y": f.y - f.h * 0.84})
	rally[f.team] = true
	cursed[foe] = true
	for o in F:
		if o.team != foe or o.dead:
			continue
		if o.T.has("beam"):
			if not o.beam_on and not o.delayed:
				o.cool += float(W.delay)
				o.delayed = true
		else:
			o.miss_next = true
		for rd in o.riders:
			rd.att.miss_next = true
		o.boost = 0.0
		o.burst_pending = false
		o.rcharge_wait = false
		o.mcharge = false
		o.pcharge = false
		o.tcharge = false
		if o.rcharge:
			_end_charge(o)
		o.charge_t = 0.0
		o.charge_hit = false


## Alamosaurus Super Stomp, once per battle on its first stomp: every enemy ground unit is stunned.
func _super_stomp(f: Unit) -> void:
	for o in F:
		if o.team != f.team and not o.dead and not _flying(o) and not o.T.get("stunImmune", false):
			o.stun = maxf(o.stun, float(f.T.superStomp.stun))
	# ...and it's the counter to the Rhino Charge: every enemy Rhino still charging (or waiting to) is stopped in its tracks
	for o in F:
		if o.team == f.team or o.dead or not (o.rcharge or o.rcharge_wait):
			continue
		o.rcharge_wait = false
		if o.rcharge:
			_end_charge(o)
	fx.append({"type": "quake", "x": f.x, "y": f.y, "w": float(f.T.w), "big": true})
	fx.append({"type": "shake"})


## Megaraptor: its bite also catches a second basic unit next to the first for half damage.
func _cleave(f: Unit, t: Unit) -> void:
	var best: Unit = null
	var bd: float = 1e9
	for o in F:
		if o == t or o.dead or o.team == f.team or not o.T.get("basic", false) or not can_hit(f, o):
			continue
		var d_t: float = dist(o, t)
		if d_t <= float(f.T.cleaveBasic) and dist(o, f) <= float(f.T.range) + 2.0 and d_t < bd:
			bd = d_t
			best = o
	if best != null:
		hit(best, f, 0.5)


## Robot Knight: every cut also hits up to 2 more enemy ground units close by, for 25%.
func _sweep(f: Unit, t: Unit) -> void:
	var S: Dictionary = f.T.sweep
	var near: Array = F.filter(func(o): return o != t and not o.dead and o.team != f.team and can_hit(f, o) and dist(o, t) <= float(S.reach) and dist(o, f) <= float(f.T.range) + 2.0)
	near.sort_custom(func(a, b): return dist(a, t) < dist(b, t))
	for o in near.slice(0, int(S.n)):
		hit(o, f, float(S.mult))


# =====================================================================
# Shooting
# =====================================================================

func _shoot(f: Unit, t: Unit) -> void:
	f.miss_volley = f.miss_next
	f.miss_next = false
	if not f.miss_volley and f.miss_shots > 0:   # Griffin screech: its next 2 shots miss
		f.miss_shots -= 1
		f.miss_volley = true
	if f.T.has("lightning"):
		_cast_lightning(f, t)
		return
	if f.T.get("rocket", false):   # Gunship: a rocket from the hatch at flyers, a laser from its gun at ground units
		var Wp: Dictionary = f.T.weapons
		if _flying(t):
			var hx: float = f.x + f.face * (float(f.T.hatch[0]) - 0.5) * float(f.T.w)
			var hy: float = f.y - f.alt - f.h * (1.0 - float(f.T.hatch[1]))
			_shoot_from(f, hx, hy, t, float(Wp.rocket.dmg) / float(f.T.dmg), "rocket", 0.0)
		else:
			var m: Vector2 = gun_tip(f)
			_shoot_from(f, m.x, m.y, t, float(Wp.laser.dmg) / float(f.T.dmg), "laser", 0.0)
			fx.append({"type": "mflash", "x": m.x, "y": m.y, "team": f.team})
		return
	if f.T.has("gun"):   # robots: two lasers, one from each cannon
		var st: float = float(f.T.stunShot.dur) if f.stun_next else 0.0
		f.stun_next = false
		for mz in f.T.gun:
			_shoot_from(f, f.x + f.face * (float(mz[0]) - 0.5) * float(f.T.w), f.y - f.alt - f.h * (1.0 - float(mz[1])), t, 1.0, "laser", st)
		return
	var sa = f.T.get("shotAt", null)
	var sx: float = f.x + f.face * ((float(sa[0]) - 0.5) if sa != null else 0.35) * float(f.T.get("artW", f.T.w))
	var sy: float = f.y - f.alt - f.h * ((1.0 - float(sa[1])) if sa != null else 0.55)
	_shoot_from(f, sx, sy, t, f.shot_mult, "spit" if f.T.get("spit", false) else ("short" if f.key == "porc" else "arrow"), 0.0)


func _shoot_from(f: Unit, ox: float, oy: float, t: Unit, mult: float, kind: String, stun: float) -> void:
	var s := Shot.new()
	var forced: bool = f.miss_volley
	if not forced and f.miss_next and f.hit_key == "rider":
		forced = true
		f.miss_next = false
	if not forced and f.miss_shots > 0 and f.hit_key == "rider":
		forced = true
		f.miss_shots -= 1
	var miss: bool = forced or (_flying(t) and rng.randf() < float(f.T.get("missAir", 0)))
	s.off = Vector2(_rnd(-1.5, 1.5), (-1.0 if rng.randf() < 0.5 else 1.0) * _rnd(2.5, 3.5)) if miss else Vector2.ZERO
	s.att = f
	s.t = t
	s.miss = miss
	s.mult = mult
	s.stun = stun
	s.kind = kind
	s.air = _flying(f) if not f.is_rider else false
	s.spd = ARROW_SPEED * (2.2 if kind == "laser" else (1.5 if kind == "rocket" else 1.0))
	s.x = ox
	s.y = oy
	s.sx = ox if f.is_rider else f.x
	s.sy = oy if f.is_rider else f.y
	s.gx = s.sx
	s.gy = s.sy
	s.team = f.team
	s.aim = Vector2(t.x + s.off.x, t.y - t.alt - t.h * float(t.T.get("aimFrac", 0.5)) + s.off.y)
	shots.append(s)


# ---- Robot Gunship gun: turns on its mount toward the ground unit it's fighting ----

func _gun_rest(T: Dictionary) -> float:
	return rad_to_deg(atan2((float(T.gunTip[1]) - float(T.gunPivot[1])) * float(T.w) * float(T.ratio), (float(T.gunTip[0]) - float(T.gunPivot[0])) * float(T.w)))


func _gun_pivot(f: Unit) -> Vector2:
	return Vector2(f.x + f.face * (float(f.T.gunPivot[0]) - 0.5) * float(f.T.w), f.y - f.alt - f.h * (1.0 - float(f.T.gunPivot[1])))


func _aim_pt(t: Unit) -> Vector2:
	return Vector2(t.x, t.y - t.alt - t.h * float(t.T.get("aimFrac", 0.5)))


func _aim_gun(f: Unit, dt: float) -> void:
	var rest: float = _gun_rest(f.T)
	if not f.gun_set:
		f.gun_aim = rest
		f.gun_set = true
	var want: float = rest
	var t: Unit = f.target
	if t != null and not t.dead and not _flying(t):
		var p: Vector2 = _gun_pivot(f)
		var q: Vector2 = _aim_pt(t)
		want = clampf(rad_to_deg(atan2(q.y - p.y, (q.x - p.x) * f.face)), -5.0, 150.0)
	var m: float = float(f.T.gunTurn) * dt
	f.gun_aim += clampf(want - f.gun_aim, -m, m)


func gun_rot(f: Unit) -> float:
	return (f.gun_aim if f.gun_set else _gun_rest(f.T)) - _gun_rest(f.T)


func gun_tip(f: Unit) -> Vector2:
	var T: Dictionary = f.T
	var p: Vector2 = _gun_pivot(f)
	var a: float = deg_to_rad(gun_rot(f))
	var vx: float = (float(T.gunTip[0]) - float(T.gunPivot[0])) * float(T.w)
	var vy: float = (float(T.gunTip[1]) - float(T.gunPivot[1])) * f.h
	return Vector2(p.x + f.face * (vx * cos(a) - vy * sin(a)), p.y + (vx * sin(a) + vy * cos(a)))


# =====================================================================
# Laser Tank: picks the spot where the enemy is most bunched up and burns it for 2 seconds:
# every 0.2s the 10 units closest to that spot take 1 damage. Then 6 seconds to cool; 4 beams a battle.
# It never stops rolling forward at its slow pace.
# =====================================================================

func rest_aim() -> float:
	var T: Dictionary = TYPES.rtank
	return rad_to_deg(atan2((float(T.muzzle[1]) - float(T.pivot[1])) * float(T.w) * float(T.ratio), (float(T.muzzle[0]) - float(T.pivot[0])) * float(T.w)))


func _pivot_pt(f: Unit) -> Vector2:
	return Vector2(f.x + f.face * (float(f.T.pivot[0]) - 0.5) * float(f.T.w), f.y - f.alt - f.h * (1.0 - float(f.T.pivot[1])))


func cannon_rot(f: Unit) -> float:
	return (f.aim if f.aim_set else rest_aim()) - rest_aim()


func muzzle_pt(f: Unit) -> Vector2:
	var T: Dictionary = f.T
	var pv: Vector2 = _pivot_pt(f)
	var a: float = deg_to_rad(cannon_rot(f))
	var vx: float = (float(T.muzzle[0]) - float(T.pivot[0])) * float(T.w)
	var vy: float = (float(T.muzzle[1]) - float(T.pivot[1])) * f.h
	return Vector2(pv.x + f.face * (vx * cos(a) - vy * sin(a)), pv.y + (vx * sin(a) + vy * cos(a)))


func _best_spot(f: Unit) -> Variant:
	var T: Dictionary = f.T
	var R: float = float(T.beam.radius)
	var mz: Vector2 = muzzle_pt(f)
	var foes: Array = F.filter(func(o): return not o.dead and o.team != f.team and can_hit(f, o) and gap(f, o) <= float(T.range) and (o.x - mz.x) * f.face > 1.0 and _beam_clear(f, o))
	if foes.is_empty():
		return null
	var score := func(x: float, y: float) -> float:
		var n: int = 0
		var c: float = 0.0
		for o in foes:
			var d: float = Vector2(o.x - x, o.y - y).length()
			if d <= R:
				n += 1
				c += R - d
		return n * 1000.0 + c
	var x0: float = 1e9
	var x1: float = -1e9
	var y0: float = 1e9
	var y1: float = -1e9
	for o in foes:
		x0 = minf(x0, o.x); x1 = maxf(x1, o.x); y0 = minf(y0, o.y); y1 = maxf(y1, o.y)
	var best: Vector2 = Vector2(foes[0].x, foes[0].y)
	var bs: float = -1.0
	var x: float = x0
	while x <= x1 + 0.01:
		var y: float = y0
		while y <= y1 + 0.01:
			var v: float = score.call(x, y)
			if v > bs:
				bs = v
				best = Vector2(x, y)
			y += 1.5
		x += 1.5
	var c0: Vector2 = best
	var xx: float = c0.x - 1.5
	while xx <= c0.x + 1.5:
		var yy: float = c0.y - 1.5
		while yy <= c0.y + 1.5:
			var v2: float = score.call(xx, yy)
			if v2 > bs:
				bs = v2
				best = Vector2(xx, yy)
			yy += 0.5
		xx += 0.5
	return best


func _aim_for(f: Unit, p: Vector2) -> float:
	var pv: Vector2 = _pivot_pt(f)
	var a: float = rad_to_deg(atan2(p.y - pv.y, (p.x - pv.x) * f.face))
	return clampf(a, -float(f.T.aimMax), float(f.T.aimMax))


func _turn_to(f: Unit, a: float, dt: float) -> bool:
	if not f.aim_set:
		f.aim = rest_aim()
		f.aim_set = true
	var m: float = float(f.T.turnRate) * dt
	f.aim += clampf(a - f.aim, -m, m)
	return absf(a - f.aim) < 1.0


func _tank_step(f: Unit, dt: float) -> void:
	var T: Dictionary = f.T
	var B: Dictionary = T.beam
	if f.shots_left < 0:
		f.shots_left = int(B.shots)
	var fwd: int = 1 if f.team == HOLD else -1
	var edge: float = AW - float(T.w) / 2.0 if fwd > 0 else float(T.w) / 2.0
	f.face = fwd
	if stance[f.team] != "hold" and (edge - f.x) * fwd > 0.02 and not (mside and fwd < 0 and f.x - 0.6 < _ms_keep(f)):
		var st: float = minf(float(T.speed) * dt, absf(edge - f.x))
		if not trees.is_empty() or not fort.is_empty():   # it steers round trees and walls
			var g: Vector2 = _path_to(f, edge, f.y) if fort.is_empty() else _route(f, edge, f.y)
			var gl: float = maxf(Vector2(g.x - f.x, g.y - f.y).length(), 1e-6)
			f.vx = (g.x - f.x) / gl * st
			f.vy = (g.y - f.y) / gl * st
		else:
			f.vx = fwd * st
		f.walking = true
		f.phase += dt * 9.0
	if f.beam_on:
		f.beam_t += dt
		# the beam stays on the bunch it was fired at: it slides toward the middle of the enemies around its spot as they move
		var sp0: Vector2 = f.spot
		var near: Array = F.filter(func(o): return not o.dead and o.team != f.team and can_hit(f, o) and _beam_clear(f, o) and Vector2(o.x - sp0.x, o.y - sp0.y).length() <= float(B.radius) * 1.5)
		if not near.is_empty():
			var c := Vector2.ZERO
			for o in near:
				c += Vector2(o.x, o.y)
			c /= near.size()
			var dv: Vector2 = c - f.spot
			var mv: float = float(B.follow) * dt
			f.spot = (f.spot + dv / dv.length() * mv) if dv.length() > mv else c
		_turn_to(f, _aim_for(f, f.spot), dt)
		while f.ticks < int(B.ticks) and f.beam_t >= f.ticks * float(B.tick) - 1e-9:
			f.ticks += 1
			var hits: Array = F.filter(func(o): return not o.dead and o.team != f.team and can_hit(f, o) and _beam_clear(f, o) and Vector2(o.x - f.spot.x, o.y - f.spot.y).length() <= float(B.radius))
			hits.sort_custom(func(a, b): return Vector2(a.x - f.spot.x, a.y - f.spot.y).length() < Vector2(b.x - f.spot.x, b.y - f.spot.y).length())
			for o in hits.slice(0, int(B.n)):
				hit(o, f)
		if f.beam_t >= float(B.dur) - 1e-9:
			f.beam_on = false
			f.has_spot = false
			f.cool = float(B.cool)
		return
	f.cool = maxf(0.0, f.cool - dt)
	if f.shots_left <= 0:
		_turn_to(f, rest_aim(), dt)
		return
	f.plan_t -= dt
	if f.plan_t <= 0:
		f.plan_t = 0.25
		var sp = _best_spot(f)
		f.has_plan = sp != null
		if sp != null:
			f.plan = sp
	if f.has_plan:
		var lined: bool = _turn_to(f, _aim_for(f, f.plan), dt)
		if f.cool <= 0 and lined and not held(f):
			var now = _best_spot(f)
			if now != null and absf(_aim_for(f, now) - f.aim) < 4.0:
				f.beam_on = true
				f.beam_t = 0.0
				f.ticks = 0
				f.spot = now
				f.has_spot = true
				f.shots_left -= 1
			else:
				f.has_plan = now != null
				if now != null:
					f.plan = now
				f.plan_t = 0.25
		return
	_turn_to(f, rest_aim(), dt)


# =====================================================================
# One slice of battle time
# =====================================================================

func update(dt: float) -> void:
	clock += dt
	if not shouted and clock >= 2.0:
		shouted = true
		for f in F:
			if f.T.has("trumpet") and not f.dead and f.pass_pts.is_empty():
				_war_trumpet(f)
	_ai_orders()
	_update_walls(dt)
	_update_fort(dt)
	_update_ballistas(dt)
	_fire_step(dt)
	_trike_stops()
	# everyone decides from the same snapshot, in a shuffled order, so neither side acts first
	var order: Array = F.duplicate()
	for i in range(order.size() - 1, 0, -1):
		var j: int = int(rng.randf() * (i + 1))
		var tmp = order[i]; order[i] = order[j]; order[j] = tmp
	for f in order:
		f.vx = 0.0
		f.vy = 0.0
	for f in order:
		if f.dead:
			continue
		f.flash = maxf(0.0, f.flash - dt)
		f.enter_t = maxf(0.0, f.enter_t - dt)
		if f.stomp_t >= 0:
			f.stomp_t += dt
			if f.stomp_t >= float(f.T.lungeDur):
				f.stomp_t = -1.0
		f.walking = false
		if over:
			continue
		var T: Dictionary = f.T
		if f.shout_t > 0:   # rearing up and trumpeting: stands still
			f.shout_t -= dt
			continue
		if T.get("stunImmune", false) and not (f.force_stun > clock):   # (a Minotaur's charge stuns even these)
			f.stun = 0.0
		if not f.pass_pts.is_empty():   # coming down a mountain pass from reserve: just walk; can't fight or be fought yet
			if stance[f.team] == "flee":   # still in the mountain: slips away at once
				f.fleeing = true
				continue
			var Q: Array = f.pass_pts[f.pass_i]
			var qx: float = float(Q[0]) - f.x
			var qy: float = maxf(_min_y(f), float(Q[1])) - f.y
			var qd: float = Vector2(qx, qy).length()
			if qd < 0.8:
				f.pass_i += 1
				if f.pass_i >= f.pass_pts.size():
					f.on_wall = f.pass_shelf
					f.pass_pts = []
					if T.has("entryBurst"):
						f.burst_pending = true
				continue
			var psp: float = float(T.speed) * (float(T.entryBurst.mult) if T.has("entryBurst") else 1.0) * dt   # a Megaraptor comes down at a sprint
			f.vx = qx / qd * minf(psp, qd)
			f.vy = qy / qd * minf(psp, qd)
			f.walking = true
			f.phase += dt * 9.0
			if absf(qx) > 0.5:
				f.face = 1 if qx > 0 else -1
			continue
		if f.burst_pending:   # still sprinting across the shelf and down the steps, then 1.5 seconds more out on the ground
			f.boost = float(T.entryBurst.dur)
			if f.on_wall < 0 and f.climbing < 0 and f.descending < 0 and not (not fort.is_empty() and f.team == HOLD and f.x < float(fort.gateX) + 1.0):
				f.burst_pending = false
				fx.append({"type": "dust", "x": f.x, "y": f.y, "face": f.face, "w": float(T.w)})
		if f.stun > 0:
			f.stun = maxf(0.0, f.stun - dt)
			continue
		if stance[f.team] == "flee":   # turn round and run for their own edge
			if f.beam_on:
				f.beam_on = false
			f.lunge = -1.0
			f.target = null
			f.engaged = false
			f.fleeing = true
			f.swoop = {}
			f.gswoop = {}
			var home: int = -1 if f.team == HOLD else 1
			f.face = home
			if mside and f.team == HOLD and not _flying(f):   # back into the mountain, off the back of a shelf or into the rock at its foot
				if f.climbing >= 0:
					f.on_wall = f.climbing
					f.climbing = -1
				f.descending = -1
				var rx0: float = float(levels[f.on_wall].x0) if f.on_wall >= 0 else _ms_foot_at(f.y) - 3.0
				var rgx: float = rx0 - f.x
				f.vx = signf(rgx) * minf(absf(rgx), float(T.speed) * dt)
				if absf(rgx) > 1.0:
					f.face = 1 if rgx > 0 else -1
			elif not fort.is_empty() and f.team == HOLD and not _flying(f):   # down off the wall, then off the back edge
				var gc: Vector2 = _goal_point(f, -12.0, clampf(f.y, f.h + 1.0, AH - 2.0), -1)
				var gcl: float = maxf(Vector2(gc.x - f.x, gc.y - f.y).length(), 1e-6)
				f.vx = (gc.x - f.x) / gcl * float(T.speed) * dt
				f.vy = (gc.y - f.y) / gcl * float(T.speed) * dt
				if absf(gc.x - f.x) > 1.0:
					f.face = 1 if gc.x > f.x else -1
			elif not trees.is_empty() and not _flying(f):
				var gf: Vector2 = _path_to(f, -12.0 if f.team == HOLD else AW + 12.0, f.y)
				var gfl: float = maxf(Vector2(gf.x - f.x, gf.y - f.y).length(), 1e-6)
				f.vx = (gf.x - f.x) / gfl * float(T.speed) * dt
				f.vy = (gf.y - f.y) / gfl * float(T.speed) * dt
				if absf(gf.x - f.x) > 1.0:
					f.face = 1 if gf.x > f.x else -1
			else:
				f.vx = home * float(T.speed) * dt
			f.walking = true
			f.phase += dt * 9.0
			continue
		f.fleeing = false
		if not f.swoop.is_empty():   # Dragon: its fire run at the start of the battle
			_swoop_step(f, dt)
			continue
		if not f.gswoop.is_empty() and _gswoop_step(f, dt):   # Griffin: swooping in to land on the enemy's front line
			continue
		if T.has("morph"):   # Mage: may turn a Minion into a Minotaur
			_morph_step(f, dt)
		var hold_pos: bool = stance[f.team] == "hold"
		if T.has("beam"):
			_tank_step(f, dt)
			continue
		if not levels.is_empty() and f.slot_w >= 0:
			var S: Dictionary = levels[f.slot_w].slots[f.slot_i]
			if f.wall_goal >= 0:   # on the way to a spot up high: to the steps and up them first
				var gw: Vector2 = _goal_point(f, float(S.x), float(S.y), f.wall_goal)
				if f.on_wall == f.wall_goal and Vector2(float(S.x) - f.x, float(S.y) - f.y).length() < 0.7:
					f.wall_goal = -1
				else:
					var gwx: float = gw.x - f.x
					var gwy: float = gw.y - f.y
					var gwd: float = maxf(Vector2(gwx, gwy).length(), 1e-6)
					var wsp: float = float(T.speed) * dt
					f.vx = gwx / gwd * minf(wsp, gwd)
					f.vy = gwy / gwd * minf(wsp, gwd)
					f.walking = true
					f.phase += dt * 9.0
					if absf(gwx) > 0.5:
						f.face = 1 if gwx > 0 else -1
					f.engaged = false
					continue
			if f.on_wall >= 0:   # up high: stay at its spot and shoot from there
				hold_pos = true
				var shx: float = float(S.x) - f.x
				var shy: float = float(S.y) - f.y
				var shd: float = Vector2(shx, shy).length()
				if shd > 0.4:
					var ssp: float = minf(float(T.speed) * dt, shd)
					f.vx = shx / shd * ssp
					f.vy = shy / shd * ssp
		var spd: float = (float(T.walkSpeed) if (T.has("walkSpeed") and f.base_alt < (ALT + LOW_ALT) / 2.0) else float(T.speed)) * (float(T.entryBurst.mult) if f.boost > 0 else 1.0)
		if f.rcharge or f.rcharge_wait:
			spd *= float(T.rhinoCharge.mult)
		if rallied(f):
			spd *= 1.15
		if f.mcharge:   # a Minotaur charges until its first hit, and a Pachycephalosaurus; a Triceratops until it reaches the enemy line
			spd *= float(T.mcharge.mult)
		if f.pcharge:
			spd *= float(T.pcharge.mult)
		if f.tcharge:
			spd *= float(T.tcharge.mult)
		spd = maxf(0.5, spd - (f.slow_spd if f.slowed else 0.0))   # a Pachycephalosaurus' head-butt slows
		if (f.mcharge or f.tcharge) and not f.engaged and f.target != null and stance[f.team] != "hold":
			f.dust_t -= dt
			if f.dust_t <= 0:
				f.dust_t = 0.15
				fx.append({"type": "dust", "x": f.x, "y": f.y, "face": f.face, "w": float(T.w)})
		if f.boost > 0:
			f.boost -= dt
		if f.rcharge and not f.engaged and stance[f.team] != "hold":   # Rhino Charge: kicks up dust as it thunders in
			f.dust_t -= dt
			if f.dust_t <= 0:
				f.dust_t = 0.12
				fx.append({"type": "dust", "x": f.x, "y": f.y, "face": f.face, "w": float(T.w)})
		if f.rcharge and hold_pos:   # ordered to Hold: the charge is called off
			_end_charge(f)
			if f.dead:
				continue
		if f.rcharge:   # straight through to the far side
			_rhino_run(f, spd, dt)
			continue
		if f.rcharge_wait:   # a Rhino behind its own walls: out through the gate first, then the Charge
			var near_e: bool = false
			for o in F:
				if o.team != f.team and not o.dead and o.pass_pts.is_empty() and not _flying(o) and dist(f, o) < 6.0:
					near_e = true
					break
			if hold_pos or near_e:
				f.rcharge_wait = false
			elif f.x >= _wall_exit().x - 1.0:
				f.rcharge_wait = false
				f.rcharge = true
				f.chk_t = 0.0
				f.chk_x = f.x
				f.stuck_t = 0.0
				f.last_x = f.x
				f.last_y = f.y
				_rhino_run(f, spd, dt)
				continue
			else:
				var E: Vector2 = _wall_exit()
				var ge: Vector2 = _goal_point(f, E.x, E.y, -1)
				var gex: float = ge.x - f.x
				var gey: float = ge.y - f.y
				var ged: float = maxf(Vector2(gex, gey).length(), 1e-6)
				var esp: float = spd * dt
				f.vx = gex / ged * minf(esp, ged)
				f.vy = gey / ged * minf(esp, ged)
				f.walking = true
				f.phase += dt * 9.0
				if absf(gex) > 0.5:
					f.face = 1 if gex > 0 else -1
				f.engaged = false
				f.target = null
				f.lunge = -1.0
				continue
		# the archers riding an Alamosaurus pick their own targets and shoot while it walks
		for rd in f.riders:
			var RT: Dictionary = TYPES[T.riderType]
			rd.cd = maxf(0.0, float(rd.cd) - dt)
			if float(rd.cd) > 0 or held(f):
				continue
			var best_r: Unit = null
			var bd_r: float = 1e9
			for o in F:
				if o.team == f.team or o.dead or (_flying(o) and not RT.get("antiAir", false)) or hidden_in(o) or not clear_shot(f, o):
					continue
				var dd: float = gap(f, o) + (1000.0 if shielded(o) else 0.0)
				if gap(f, o) <= float(RT.range) and dd < bd_r:
					bd_r = dd
					best_r = o
			if best_r == null:
				rd.aiming = false
				continue
			if not rd.aiming:
				rd.aiming = true
				rd.cd = _rnd(0.05, 0.45)
				continue
			rd.cd = float(RT.rate)
			var rider: Unit = rd.att
			rider.miss_volley = false
			_shoot_from(rider, f.x + (float(rd.fx) - 0.5) * float(T.w) * f.face, f.y - f.alt - (1.0 - float(rd.fy)) * f.h, best_r, 1.0, "short", 0.0)
		var cur: Unit = f.target
		if cur == null or cur.dead or not can_hit(f, cur) or _out_of_reach(f, cur) or (is_dino(f) and charging(cur) and _reach_gap(f, cur) > range_of(f)):
			f.target = _pick_target(f)
		else:
			var best: Unit = _pick_target(f)
			if best != null and best != cur and (_prio(f, best) > _prio(f, cur) or dist(f, best) < dist(f, cur) * 0.75):
				f.target = best
		# knights in a shield wall hold their place and only fight what reaches them;
		# units sheltering behind a wall stay in their spot and fight from there
		var in_wall: bool = f.wall_ref != null and not f.wall_ref.broken
		var hiding: bool = not in_wall and f.hide != null and not f.hide.broken
		if in_wall:
			var best_w: Unit = null
			var bd_w: float = 1e9
			for o in F:
				if o.team == f.team or o.dead or _flying(o):
					continue
				var g: float = gap(f, o)
				if g <= float(T.range) and g < bd_w:
					bd_w = g
					best_w = o
			f.target = best_w
		var has_hold: bool = in_wall or hiding
		var hold: Vector2 = _wall_slot(f) if in_wall else (_hide_slot(f) if hiding else Vector2.ZERO)
		if f.target == null and not f.riders.is_empty() and not has_hold:
			# an Alamosaurus with only flyers left walks its archers into reach of them
			var RT2: Dictionary = TYPES[T.riderType]
			var fo: Unit = null
			var bd2: float = 1e9
			for o in F:
				if o.dead or o.team == f.team or not _flying(o):
					continue
				var d2: float = gap(f, o)
				if d2 < bd2:
					bd2 = d2
					fo = o
			if fo != null and bd2 > float(RT2.range) * 0.8 and not hold_pos:
				var gch: Vector2 = _path_to(f, fo.x, fo.y) if not _flying(f) else Vector2(fo.x, fo.y)
				var ddx: float = gch.x - f.x
				var ddy: float = gch.y - f.y
				var dl: float = maxf(Vector2(ddx, ddy).length(), 1e-6)
				f.vx = ddx / dl * spd * dt
				f.vy = ddy / dl * spd * dt
				f.walking = true
				f.phase += dt * 9.0
				if absf(ddx) > 2.5:
					f.face = 1 if ddx > 0 else -1
			f.engaged = false
			continue
		if T.has("breath"):
			_breath_step(f)
		var t: Unit = f.target
		if f.tcharge and t != null and (not _flying(t) or downed(t)) and gap(f, t) <= float(T.range) + 1.0 and (levels.is_empty() or _same_level(f, t)):
			_trike_impact(f, t)
		if t == null and not has_hold:
			# shooters with nothing to aim at keep marching toward the enemy's side
			if (T.get("ranged", false) or T.get("rocket", false)) and not hold_pos:
				var ex: float = AW - float(T.w) / 2.0 + 1.0 if f.team == HOLD else float(T.w) / 2.0 - 1.0
				if absf(ex - f.x) > 0.5:
					var gx0: float = ex - f.x
					if mside and not _flying(f):
						f.vx = signf(maxf(ex, _ms_keep(f) + 1.0) - f.x) * spd * dt
					elif not levels.is_empty() and not _flying(f):
						var gq: Vector2 = _goal_point(f, ex, f.y, -1)
						var gql: float = maxf(Vector2(gq.x - f.x, gq.y - f.y).length(), 1e-6)
						f.vx = (gq.x - f.x) / gql * spd * dt
						f.vy = (gq.y - f.y) / gql * spd * dt
					elif not trees.is_empty() and not _flying(f):
						var gm: Vector2 = _path_to(f, ex, f.y)
						var gml: float = maxf(Vector2(gm.x - f.x, gm.y - f.y).length(), 1e-6)
						f.vx = (gm.x - f.x) / gml * spd * dt
						f.vy = (gm.y - f.y) / gml * spd * dt
					else:
						f.vx = signf(gx0) * spd * dt
					f.walking = true
					f.phase += dt * 9.0
					if absf(gx0) > 1.0:
						f.face = 1 if gx0 > 0 else -1
			f.engaged = false
			continue
		if has_hold:
			# ride along with the wall and ease into the spot, so the formation marches together
			var W: ShieldWall = f.wall_ref if in_wall else f.hide
			var hx: float = hold.x - f.x
			var hy: float = hold.y - f.y
			var hd: float = Vector2(hx, hy).length()
			var kk: float = minf(1.0, dt * 5.0)
			var vx: float = W.mx + hx * kk
			var vy: float = W.my + hy * kk
			var cap: float = float(T.speed) * dt
			var v: float = Vector2(vx, vy).length()
			if v > cap:
				vx *= cap / v
				vy *= cap / v
			f.vx = vx
			f.vy = vy
			if Vector2(W.mx, W.my).length() > 1e-5 or hd > 0.8:
				f.walking = true
				f.phase += dt * 9.0 * maxf(0.2, minf(v, cap) / cap)
			if in_wall:
				f.face = W.face
			elif t != null:
				f.face = 1 if t.x > f.x else -1
			else:
				f.face = W.face
		if t == null:
			f.engaged = false
			continue
		var dx: float = t.x - f.x
		var dy: float = t.y - f.y
		var d: float = maxf(Vector2(dx, dy).length(), 1e-6)
		if not has_hold:
			if dx > 2.5:
				f.face = 1
			elif dx < -2.5:
				f.face = -1
		f.cd = maxf(0.0, f.cd - dt)
		# Alamosaurus Charge, once per battle: one body length from its target it rushes in 50% faster
		var mv: float = spd
		if T.has("charge"):
			var g2: float = gap(f, t)
			if not f.charge_used and not _flying(t) and g2 <= float(T.charge.dist) and g2 > float(T.range):
				f.charge_used = true
				f.charge_t = float(T.charge.max)
			if f.charge_t > 0:
				if g2 <= float(T.range):
					f.charge_t = 0.0
					f.charge_hit = true
				else:
					f.charge_t -= dt
					mv *= float(T.charge.mult)
					f.dust_t -= dt
					if f.dust_t <= 0:
						f.dust_t = 0.1
						fx.append({"type": "dust", "x": f.x, "y": f.y, "face": f.face, "w": float(T.w)})
		var no_line: bool = (not trees.is_empty() or not fort.is_empty()) and T.get("ranged", false) and not clear_shot(f, t)   # a trunk or a wall is in the way of the shot
		var off_level: bool = not levels.is_empty() and not T.get("ranged", false) and not _same_level(f, t)   # up on a shelf: walk round and up (or down) first
		if not T.get("ranged", false) and not T.get("rocket", false) and _gate_blocks(f, t):
			# at the castle's closed gate: batter it down
			f.face = -1
			f.engaged = true
			f.vx = 0.0
			f.vy = 0.0
			if f.cd == 0 and f.lunge < 0:
				f.cd = float(T.rate) - (0.2 if rallied(f) else 0.0) + (f.slow_rate if f.slowed else 0.0)
				f.lunge = 0.0
				f.struck = false
				f.gate_swing = true
				if T.has("atk2Frames"):
					f.alt2 = not f.alt2
				if T.has("sheet"):
					f.arm = "l" if f.arm == "r" else "r"
				if T.get("legs", false):
					f.leg = "f" if f.leg == "n" else "n"
					f.stomp_t = 0.0
					f.stomp_leg = f.leg
		elif _reach_gap(f, t) > range_of(f) or no_line or off_level:
			if not has_hold and not hold_pos:
				if not levels.is_empty() and not _flying(f):
					var gl2: Vector2 = _goal_point(f, t.x, t.y, t.on_wall)
					var glx: float = gl2.x - f.x
					var gll: float = maxf(Vector2(glx, gl2.y - f.y).length(), 1e-6)
					f.vx = glx / gll * mv * dt
					f.vy = (gl2.y - f.y) / gll * mv * dt
					if absf(glx) > 2.5:
						f.face = 1 if glx > 0 else -1
				elif not trees.is_empty() and not _flying(f):
					var gp: Vector2 = _path_to(f, t.x, t.y)
					var gpx: float = gp.x - f.x
					var gpl: float = maxf(Vector2(gpx, gp.y - f.y).length(), 1e-6)
					f.vx = gpx / gpl * mv * dt
					f.vy = (gp.y - f.y) / gpl * mv * dt
					if absf(gpx) > 2.5:
						f.face = 1 if gpx > 0 else -1
				else:
					f.vx = dx / d * mv * dt
					f.vy = dy / d * mv * dt
				f.walking = true
				f.phase += dt * 9.0 * mv / float(T.speed)
			f.engaged = false
		else:
			if not f.engaged:
				f.engaged = true
				f.cd = maxf(f.cd, _rnd(0.05, 0.45))   # a moment to take aim
			# Longbow: shots 1, 5, 9... are charged first (25% longer), then hit twice as hard
			var cs = T.get("chargeShot", null)
			if cs != null and f.cd == 0 and f.lunge < 0 and not f.charged and f.shots % int(cs.every) == 0 and not held(f):
				f.charged = true
				f.cd = float(T.rate) * float(cs.slow)
			if f.cd == 0 and f.lunge < 0 and not held(f):
				if T.has("weapons"):
					f.cd = float(T.weapons["rocket" if _flying(t) else "laser"].rate)
				else:
					f.cd = float(T.rate) - (0.2 if rallied(f) else 0.0) + (f.slow_rate if f.slowed else 0.0)
				if T.has("atk2Frames"):
					f.alt2 = not f.alt2
				if f.boost > 0 or f.burst_pending:   # Megaraptor: its first attack on an enemy ends the sprint
					f.boost = 0.0
					f.burst_pending = false
				f.lunge = 0.0
				f.struck = false
				if cs != null:
					f.shot_mult = float(cs.mult) if f.charged else 1.0
					f.charged = false
					f.shots += 1
				if T.has("stunShot"):
					f.shots += 1
					f.stun_next = (f.shots - 1) % int(T.stunShot.every) == 0
				if T.has("sheet"):
					f.arm = "l" if f.arm == "r" else "r"
				if T.get("legs", false):
					f.leg = "f" if f.leg == "n" else "n"
					f.stomp_t = 0.0
					f.stomp_leg = f.leg
		if f.lunge >= 0:
			f.lunge += dt
			if not f.struck and f.lunge >= float(T.strikeAt):
				f.struck = true
				if f.gate_swing:
					f.gate_swing = false
					if f.miss_next:
						f.miss_next = false
					elif not fort.is_empty() and not fort.broken:
						_hit_gate(f)
				elif not t.dead:
					if T.get("ranged", false) or T.get("rocket", false):
						_shoot(f, t)
						if T.get("noRepeat", false):
							f.last_shot = t.id
							f.target = null
					elif (not _flying(t) or T.get("antiAir", false) or downed(t)) and gap(f, t) <= float(T.range) + 1.5 and (levels.is_empty() or _same_level(f, t)):
						if f.miss_next:
							f.miss_next = false
						else:
							if f.mcharge:
								_charge_hit(f, t)
							elif T.has("slowHit"):
								_pachy_hit(f, t)
							else:
								hit(t, f)
							if T.get("twin", false):
								_twin_bite(f, t)
							if T.has("tail"):
								_tail_swing(f, t)
							if T.has("hornSweep"):
								_horn_sweep(f, t)
							if T.get("noRepeat", false):
								f.last_shot = t.id
								f.target = null
							if T.has("cleaveBasic") and t.T.get("basic", false):
								_cleave(f, t)
							if T.has("sweep"):
								_sweep(f, t)
							if T.has("multi"):
								_stomp_around(f, t)
							if T.has("superStomp") and not f.super_used:
								f.super_used = true
								_super_stomp(f)
				f.charge_hit = false
			if f.lunge >= float(T.lungeDur):
				f.lunge = -1.0
	for f in F:   # Triceratops: stays in its Rhino's lane while that Rhino charges
		if f.dead or f.lane == null:
			continue
		var lo: Unit = f.lane
		if lo.dead or not (lo.rcharge or lo.rcharge_wait) or f.stun > 0:
			f.lane = null
			continue
		var ldy: float = lo.y - f.y
		f.vy = signf(ldy) * minf(absf(ldy), float(f.T.speed) * 1.5 * dt)
	for f in F:
		if not f.dead:
			f.x += f.vx
			f.y += f.vy
			if f.T.has("stride"):
				f.odo += Vector2(f.vx, f.vy).length()
			if f.T.has("prop"):
				f.spin += dt / float(f.T.prop) * (1.4 if f.walking else 1.0)
	# flyers: glide down to just above a ground target while fighting it, back up to cruising height otherwise
	for f in F:
		if not _flying(f):
			continue
		if f.dead:
			f.alt = maxf(0.0, f.alt - dt * 22.0)
			continue
		if f.T.get("hover", false) and not downed(f):
			f.base_alt = ALT
			f.alt = ALT
			if not (f.stun > 0):
				_aim_gun(f, dt)
			continue
		var tt: Unit = f.target
		var low: bool = (not f.swoop.is_empty() and int(f.swoop.st) == 3 and f.swoop.get("near", false)) or (tt != null and not tt.dead and not _flying(tt) and (f.engaged or gap(f, tt) <= float(f.T.range) + 8.0))   # (a Dragon landing after its fire run)
		f.base_alt += ((0.0 if (f.grounded or downed(f)) else (LOW_ALT if low else ALT)) - f.base_alt) * minf(1.0, dt * 3.0)   # a Dragon or Griffin that has landed stays on the ground
		var dive: float = sin(PI * minf(1.0, f.lunge / float(f.T.lungeDur))) if f.lunge >= 0 else 0.0
		f.alt = f.base_alt * (1.0 - 0.15 * dive) + sin(TAU * (clock + f.phase) / 1.6) * 0.075 * (f.base_alt / ALT)
	_update_shots(dt)
	# a light nudge apart so stacked units never hide each other completely, and everyone stays on the field
	var L: Array = F.filter(func(f): return not f.dead)
	for i in L.size():
		for j in range(i + 1, L.size()):
			var a: Unit = L[i]
			var b: Unit = L[j]
			if _flying(a) != _flying(b) or a.on_wall != b.on_wall:
				continue
			var ddx: float = b.x - a.x
			var ddy: float = b.y - a.y
			var dd: float = Vector2(ddx, ddy).length()
			var sep: float = SEP_SAME if a.team == b.team else SEP_ENEMY
			if dd < sep:
				if dd < 0.01:
					ddx = _rnd(-1, 1)
					ddy = _rnd(-1, 1)
					dd = maxf(Vector2(ddx, ddy).length(), 1e-6)
				var p: float = (sep - dd) / 2.0 / dd
				a.x -= ddx * p; a.y -= ddy * p
				b.x += ddx * p; b.y += ddy * p
	for f in L:
		if not f.swoop.is_empty() and int(f.swoop.st) != 0:   # out on its fire run: off the field's edges for a while
			continue
		if f.fleeing:
			f.y = clampf(f.y, _min_y(f), AH - 1.5)
			continue
		f.x = clampf(f.x, float(f.T.w) / 2.0 - 1.0, AW - float(f.T.w) / 2.0 + 1.0)
		f.y = clampf(f.y, _min_y(f), AH - 1.5)
		if f.hide != null and not f.hide.broken:   # sheltering units can't step past their wall until it breaks
			var lim: float = f.hide.x - f.hide.face * 3.0
			if (f.x - lim) * f.hide.face > 0:
				f.x = lim
	if mside:
		for f in L:
			if _flying(f) or f.climbing >= 0 or f.descending >= 0 or f.on_wall >= 0 or not f.pass_pts.is_empty():
				continue
			var kx: float = _ms_keep(f)
			if f.x < kx:
				f.x = kx
	if not levels.is_empty():
		for f in L:
			if _flying(f) or f.climbing >= 0 or f.descending >= 0 or f.on_wall < 0:
				continue
			var Wl: Dictionary = levels[f.on_wall]
			match String(Wl.get("kind", "shelf")):
				"mid":   # the castle's centre walkway
					f.x = clampf(f.x, float(Wl.x0), float(Wl.x1))
					f.y = clampf(f.y, maxf(_min_y(f), float(Wl.y0)), float(Wl.y1))
				"walk":   # kept on the walkway, along the wall
					f.x = clampf(f.x, float(Wl.x0), float(Wl.x1))
					f.y = maxf(_min_y(f), float(Wl.wa) + float(Wl.wb) * f.x)
				_:
					f.x = clampf(f.x, float(Wl.x0) + 1.5, float(Wl.x1) - 1.0)
					f.y = clampf(f.y, maxf(float(Wl.y0) + 0.8, _min_y(f)), float(Wl.y1) - 0.6)
	if not fort.is_empty():
		_push_out_of_walls(L)
		for f in L:   # a Megaraptor coming out of the gate sprints off at full speed, like arriving from reserve
			if not f.T.has("entryBurst") or _flying(f) or f.team != HOLD:
				continue
			var inside: bool = fort_fade(f) < 0.5
			if f.in_fort and not inside and f.x > float(fort.gateX) - 3.0 and not f.fleeing and not f.burst_pending and clock >= f.burst_ready:
				f.boost = float(f.T.entryBurst.dur)
				f.burst_ready = clock + 3.0
				fx.append({"type": "dust", "x": f.x, "y": f.y, "face": f.face, "w": float(f.T.w)})
			f.in_fort = inside
	if not trees.is_empty():
		for f in L:
			var hd2: bool = hidden_in(f)
			if hd2 != f.hid:
				if hd2:
					f.hid_since = clock
				elif f.T.has("entryBurst") and not f.fleeing and clock - f.hid_since >= 0.5 and clock >= f.burst_ready:
					# Megaraptor: out of the trees at full sprint, like arriving from reserve
					f.boost = float(f.T.entryBurst.dur)
					f.burst_ready = clock + 3.0
					fx.append({"type": "dust", "x": f.x, "y": f.y, "face": f.face, "w": float(f.T.w)})
				f.hid = hd2
		_push_out_of_trunks(L)
	# a fleeing unit that has run fully off its own edge has escaped
	for f in F:
		if f.fleeing and not f.dead and not f.gone and (_into_rock(f) or (f.team == HOLD and f.x < -float(f.T.w) / 2.0) or (f.team != HOLD and f.x > AW + float(f.T.w) / 2.0)):
			esc[f.team].n += 1
			esc[f.team].hp += f.hp
			esc[f.team].k[f.key] = int(esc[f.team].k.get(f.key, 0)) + 1
			f.gone = true
	# the fallen leave once they've faded out
	for f in F:
		if f.dead:
			f.dead_t += dt
			if f.dead_t > 1.1:
				f.gone = true
	F = F.filter(func(f): return not f.gone)
	if not over:
		_reinforce()
	if not over:
		for t2 in 2:
			if stance[t2] == "flee" and _alive(t2).is_empty():
				over = true
				retreat = t2
				break
	if not over:
		for t3 in 2:
			if _alive(t3).is_empty() and RES[t3].is_empty():
				over = true
	if not over and shots.is_empty() and not _either_can_hit():
		over = true
		stalemate = true
	if not over and shots.is_empty() and clock - last_hit > 30.0:   # nobody has landed a blow for 30 seconds: a standoff
		over = true
		stalemate = true
	if over:
		for f in F:
			f.lunge = -1.0
			f.beam_on = false


func _update_shots(dt: float) -> void:
	for i in range(shots.size() - 1, -1, -1):
		var a: Shot = shots[i]
		if not a.t.dead:
			a.aim = Vector2(a.t.x + a.off.x, a.t.y - a.t.alt - a.t.h * float(a.t.T.get("aimFrac", 0.5)) + a.off.y)
		var dx: float = a.aim.x - a.x
		var dy: float = a.aim.y - a.y
		var d: float = maxf(Vector2(dx, dy).length(), 1e-6)
		var step: float = a.spd * dt
		a.ang = atan2(dy, dx)
		if not trees.is_empty() and not a.air and not _flying(a.t):
			# its spot on the ground moves along with it; a tree in the way stops it there
			var tx0: float = a.t.x + a.off.x
			var ty0: float = a.t.y
			var kk: float = minf(1.0, step / maxf(d, 1e-6))
			var nx: float = a.gx + (tx0 - a.gx) * kk
			var ny: float = a.gy + (ty0 - a.gy) * kk
			var ti: int = _tree_in_path(a.gx, a.gy, nx, ny, tx0, ty0)
			a.gx = nx
			a.gy = ny
			if ti >= 0:
				_stick_in_tree(a, ti)
				shots.remove_at(i)
				continue
		if d <= step + 0.6 and not a.t.dead and hidden_in(a.t):
			a.miss = true   # the target slipped into the forest
		if d <= step + 0.6:
			if a.kind == "rocket":
				fx.append({"type": "boom", "x": a.aim.x, "y": a.aim.y})
			if not a.t.dead and not a.miss:
				hit(a.t, a.att, a.mult, true)
				if a.att.T.has("grounds") and _flying(a.t) and not a.t.dead and not soaring_over(a.t):   # Dilophosaurus: knocks a flyer to the ground for 3 s
					a.t.down_t = clock + float(a.att.T.grounds.dur)
				if a.stun > 0 and not a.t.dead and not a.t.T.get("stunImmune", false):
					a.t.stun = maxf(a.t.stun, a.stun)
			shots.remove_at(i)
			continue
		a.x += dx / d * step
		a.y += dy / d * step


## Can either side still hurt the other, counting units in reserve?
func _either_can_hit() -> bool:
	var info: Array = []
	for t in 2:
		var types: Array = []
		for f in _alive(t):
			types.append(f.T)
		for k in RES[t]:
			types.append(TYPES[k])
		var ground: bool = types.any(func(T): return not T.get("flying", false))
		var air: bool = types.any(func(T): return T.get("flying", false))
		var aa: bool = types.any(func(T): return T.get("antiAir", false) or (T.has("riders") and TYPES[T.riderType].get("antiAir", false)))
		info.append({"any": not types.is_empty(), "ground": ground, "air": air, "aa": aa})
	for t in 2:
		var me: Dictionary = info[t]
		var foe: Dictionary = info[1 - t]
		if me.any and (foe.ground or (foe.air and me.aa)):
			return true
	return false


func _reinforce() -> void:
	for team in 2:
		if stance[team] == "flee":
			continue
		var live: float = 0.0
		for f in _alive(team):
			live += _slot(f.key)
		while true:
			var idx: int = -1
			for i in RES[team].size():
				var k: String = RES[team][i]
				var cap: int = int(TYPES[k].get("fieldMax", 0))
				if cap > 0 and _alive(team).filter(func(f): return f.key == k).size() >= cap:
					continue
				idx = i
				break
			if idx < 0 or live + _slot(RES[team][idx]) > FIELD_MAX + 1e-9:
				break
			var key: String = RES[team][idx]
			RES[team].remove_at(idx)
			var T: Dictionary = TYPES[key]
			var h: float = float(T.w) * float(T.ratio)
			var ry: float = _rnd(h + 2.0 + (ALT + 1.5 if T.get("flying", false) else 0.0), AH - 2.0)
			var rx: float = float(T.w) / 2.0 if team == HOLD else AW - float(T.w) / 2.0
			if mside and team == HOLD and T.has("beam"):
				rx = _ms_keep_T(T, ry) + 0.5
			if not fort.is_empty() and team == HOLD and not T.get("flying", false):
				ry = _rnd(maxf(13.0, h + 2.0), 46.0)
			var PS: Dictionary = {}
			if mside and team == HOLD and not T.get("flying", false) and not T.has("beam"):   # down one of the mountain passes
				PS = MS_PASSES[pass_turn % MS_PASSES.size()]
				pass_turn += 1
				rx = float(PS.pts[0][0])
				ry = maxf(h + 1.0, float(PS.pts[0][1]))
			var u: Unit = _add_unit(team, key, rx, ry, true)
			live += _slot(key)
			if not PS.is_empty():
				u.pass_pts = PS.pts
				u.pass_i = 1
				u.pass_shelf = int(PS.shelf)
				u.boost = 0.0
			if not levels.is_empty() and team == HOLD and T.get("ranged", false) and not T.get("flying", false) and not T.has("beam"):
				var fs: Array = _free_slots()
				if not fs.is_empty():   # coming down a pass: a spot on the shelf it leads to, if there is one
					var score := func(e: Array) -> float:
						var W2: Dictionary = levels[e[0]]
						return (-1000.0 if e[0] == u.pass_shelf else 0.0) + float(W2.get("pri", 0)) * 500.0 + Vector2(W2.foot.x - u.x, W2.foot.y - u.y).length() + float(W2.slots[e[1]].y) * 0.01
					fs.sort_custom(func(a, b): return score.call(a) < score.call(b))
					_take_slot(u, fs[0][0], fs[0][1])


## The computer's side attacks, but falls back when it's clearly beaten so it keeps what it can.
func _ai_orders() -> void:
	if over:
		return
	var hp: Array = health()
	# by difficulty: Easy only runs when nearly wiped out; Hard and Expert keep a defending army on Hold until the first hit
	# (its archers and walls get to work first), then charge, and pull back sooner to save units for the map
	var L: String = ai_level
	var flee: float = 0.1 if L == "easy" else (0.3 if L == "hard" else (0.35 if L == "expert" else 0.2))
	var wait: float = 6.0 if (L == "hard" or L == "expert") else 8.0
	for t in ai_teams:
		var want: String = "flee" if (clock > wait and hp[t] < hp[1 - t] * flee) else "attack"
		if want == "attack" and (L == "hard" or L == "expert") and t == HOLD and last_hit <= 0.0 and clock < 25.0:
			want = "hold"
		if stance[t] != want and stance[t] != "flee":
			stance[t] = want


# =====================================================================
# Dinosaurs (Ethan's rewrite, 2026-11-06) and the Mythical (2026-11-06), as in the browser Arena
# =====================================================================

var fires: Array = []   # the Dragon's fire streak: {x, y, r, until, after, dps, team, n} (kept a moment after it goes out, to fade)


## A Dragon on its fire run, until it glides down to land: shots can't reach it.
func soaring_over(o: Unit) -> bool:
	return not o.swoop.is_empty() and int(o.swoop.st) != 0 and not (int(o.swoop.st) == 3 and o.swoop.get("near", false))


## A flyer on the ground: knocked down by a Dilophosaurus, or a Griffin or Dragon that has landed.
func downed(o: Unit) -> bool:
	return o.down_t > clock or o.grounded


## What a Megaraptor bites for 20.
func is_large(o: Unit) -> bool:
	return o.T.get("heavy", false) or o.T.get("large", false)


func charging(o: Unit) -> bool:
	return o.rcharge or o.mcharge or o.pcharge or o.tcharge or o.charge_t > 0


func fac_of(k: String) -> String:
	return String(TYPES[k].get("faction", "Dinosaurs")) if TYPES.has(k) else ""


func is_dino(f: Unit) -> bool:
	return not f.is_pseudo and not f.is_ballista and fac_of(f.key) == "Dinosaurs"


# ---- Mage ----

## Chain lightning: a bolt from its staff to its target, then on to the nearest enemy within 9 of the last one hit, and so on,
## up to 20 enemies (ground or air); each takes its damage. Units hidden in the forest or inside the castle are out of its sight.
func _cast_lightning(f: Unit, t: Unit) -> void:
	var Lg: Dictionary = f.T.lightning
	var chain: Array = [t]
	var done: Dictionary = {t.id: true}
	var cur: Unit = t
	while chain.size() < int(Lg.n):
		var nx: Unit = null
		var bd: float = float(Lg.jump)
		for o in F:
			if o.dead or not o.pass_pts.is_empty() or o.is_ballista or o.team == f.team or done.has(o.id) or not can_hit(f, o):
				continue
			var d: float = dist(o, cur)
			if d < bd:
				bd = d
				nx = o
		if nx == null:
			break
		done[nx.id] = true
		chain.append(nx)
		cur = nx
	var pts: Array = [_staff_pt(f)]
	for o in chain:
		pts.append(_aim_pt(o))
	fx.append({"type": "zap", "pts": pts, "team": f.team})
	if f.miss_volley:   # War Trumpet or a Griffin's screech: the spell fizzles
		return
	for o in chain:
		if not o.dead:
			hit(o, f)


func _staff_pt(f: Unit) -> Vector2:
	var st: Array = f.T.staff
	return Vector2(f.x + f.face * (float(st[0]) - 0.5) * float(f.T.w), f.y - f.alt - f.h * (1.0 - float(st[1])))


## Every 2 seconds, a chance (20% to 50% by Mage level) to turn one of its side's Minions, picked at random, into a Minotaur.
func _morph_step(f: Unit, dt: float) -> void:
	var M: Dictionary = f.T.morph
	f.morph_t += dt
	if f.morph_t < float(M.every):
		return
	f.morph_t -= float(M.every)
	if rng.randf() >= float(M.chance):
		return
	var ms: Array = F.filter(func(o): return o.team == f.team and not o.dead and o.pass_pts.is_empty() and not o.fleeing and o.key == "minion")
	if ms.is_empty():
		return
	var m: Unit = ms[int(rng.randf() * ms.size())]
	fx.append({"type": "zap", "pts": [_staff_pt(f), _aim_pt(m)], "team": f.team})
	_morph(m, String(M.into))


func _morph(m: Unit, key: String) -> void:
	var team: int = m.team
	m.dead = true
	m.gone = true
	m.target = null
	F.erase(m)
	var u: Unit = _add_unit(team, key, m.x, m.y, false)
	u.face = m.face
	hp0[team] += maxf(0.0, u.hp - maxf(0.0, m.hp))   # the health bar grows with it
	fx.append({"type": "poof", "x": m.x, "y": m.y - u.h * 0.5})


# ---- Dragon ----

## Fire run: at the start of the battle it takes off from behind its own edge and flies low and very fast (6x its flying speed)
## straight across the field, along the middle of the enemy army, and out past the enemy's edge. Over the enemy's side it leaves a
## streak of fire on the ground that burns for 5 seconds. Any enemy on the ground that touches it catches fire: 5 damage a second
## while the streak lasts and for 5 seconds after it goes out. A moment later it comes back on from its own edge, glides down to
## land in front of the enemy's front line and then fights as normal.
func _swoop_step(f: Unit, dt: float) -> void:
	var S: Dictionary = f.swoop
	var T: Dictionary = f.T
	var Z: Dictionary = T.swoop
	var dir: int = 1 if f.team == HOLD else -1
	var mid: float = AW / 2.0
	var home: float = -float(T.w) if dir > 0 else AW + float(T.w)   # fully out of sight
	var out: float = AW + float(T.w) if dir > 0 else -float(T.w)
	f.target = null
	f.engaged = false
	f.lunge = -1.0
	if int(S.st) == 0:   # line up on the middle of the enemy army (top to bottom), just behind its own edge
		var ys: Array = []
		for o in F:
			if o.team != f.team and not o.dead and not _flying(o):
				ys.append(o.y)
		ys.sort()
		S.y1 = maxf(f.h + 3.0, minf(AH - 3.0, float(ys[ys.size() >> 1]) if not ys.is_empty() else AH / 2.0))
		f.x = home
		f.y = float(S.y1)
		S.st = 1
		S.drop = 0.0
		S.px = f.x
		S.py = f.y
	var nx: float = f.x
	var ny: float = f.y
	if int(S.st) == 1:   # the run, all the way across
		nx = f.x + dir * float(T.speed) * float(Z.mult) * dt
		if (nx - out) * dir >= 0:
			nx = out
			S.st = 2
			S.t = 0.0
	elif int(S.st) == 2:   # off past the enemy's edge a moment, then back on from its own edge
		S.t = float(S.t) + dt
		f.vx = 0.0
		f.vy = 0.0
		f.walking = true
		if float(S.t) >= float(Z.wait):
			S.st = 3
			f.x = home
			f.y = float(S.y1)
			S.lx = AW * float(Z.land) if dir > 0 else AW * (1.0 - float(Z.land))
			S.px = f.x
			S.py = f.y
		return
	elif int(S.st) == 3:   # flies in to the front of the battle and lands just in front of the enemy's front line
		var has_front: bool = false
		var fxx: float = 0.0
		var fy: float = float(S.y1)
		for o in F:
			if o.team == f.team or o.dead or not o.pass_pts.is_empty() or _flying(o) or o.is_ballista or o.on_wall >= 0:
				continue
			if not has_front or o.x * dir < fxx * dir:
				has_front = true
				fxx = o.x
				fy = o.y
		var lx: float = (fxx - dir * (float(T.w) * 0.4 + 3.0)) if has_front else float(S.lx)
		var ly: float = maxf(f.h + 2.0, minf(AH - 2.0, fy)) if has_front else f.y
		var dx: float = lx - f.x
		var dy: float = ly - f.y
		var d: float = Vector2(dx, dy).length()
		var st: float = float(T.speed) * float(Z.back) * dt
		S.near = S.get("near", false) or d < 18.0   # starts gliding down once it's close (and keeps going)
		if d <= maxf(st, 0.8) and f.base_alt <= LOW_ALT + 0.4:
			nx = lx
			ny = ly
			f.swoop = {}
			f.grounded = true
		else:
			var k: float = minf(st, d) / (d if d > 0 else 1.0)
			nx = f.x + dx * k
			ny = f.y + dy * k
	f.vx = nx - f.x
	f.vy = ny - f.y
	f.walking = true
	f.phase += dt * 9.0
	if absf(f.vx) > 1e-4:
		f.face = 1 if f.vx > 0 else -1
	if int(S.st) != 1:
		return
	# fire on the ground ahead of it, where the flame it blows hits the ground, while that's over the enemy's side of the field
	var hx: float = nx + dir * float(Z.ahead)
	var theirs: bool = (hx - mid) * dir > 0.5 and hx > 0 and hx < AW
	S.drop = (float(S.drop) + Vector2(nx - float(S.px), ny - float(S.py)).length()) if theirs else 0.0
	S.px = nx
	S.py = ny
	while theirs and float(S.drop) >= float(Z.fire.gap):   # (fast enough to need several a frame)
		S.drop = float(S.drop) - float(Z.fire.gap)
		_drop_fire(f, hx - dir * float(S.drop), ny)


func _drop_fire(f: Unit, x: float, y: float) -> void:
	var Z: Dictionary = f.T.swoop.fire
	f.fire_n += 1
	fires.append({"x": x, "y": y, "r": float(Z.r), "until": clock + float(Z.dur), "after": float(Z.after), "dps": float(Z.dps), "team": f.team, "n": f.fire_n, "t0": clock})


func _fire_step(dt: float) -> void:
	for i in range(fires.size() - 1, -1, -1):
		var P: Dictionary = fires[i]
		if clock >= float(P.until):
			if clock >= float(P.until) + 0.65:   # (the picture fades out first)
				fires.remove_at(i)
			continue
		for o in F:
			if o.team == int(P.team) or o.dead or not o.pass_pts.is_empty() or _flying(o) or o.on_wall >= 0 or o.is_ballista:
				continue
			if Vector2((o.x - float(P.x)) / 1.25, (o.y - float(P.y)) / 0.7).length() <= float(P.r):
				if not (o.burn_until > clock):
					o.burn_acc = 0.0
				o.burn_until = maxf(o.burn_until, float(P.until) + float(P.after))
				o.burn_by = int(P.team)
				o.burn_dps = float(P.dps)
	for o in F:
		if not o.dead and o.burn_until > clock:
			o.burn_acc += dt
			while o.burn_acc >= 1.0 and not o.dead:
				o.burn_acc -= 1.0
				hit(o, _pseudo(o.burn_by, o.burn_dps, "fire"))


## Fire breath: every 8 seconds, when an enemy it is going for is within reach (about a sixth of the field) and in front of it,
## it breathes a cone of fire at it. Up to 15 enemies in the cone (ground or air, nearest first) take 15 each. Its bite carries on.
func _breath_step(f: Unit) -> void:
	var B: Dictionary = f.T.breath
	if f.fire_at < 0:
		f.fire_at = clock + float(B.first) + rng.randf()
	if clock < f.fire_at or held(f):
		return
	var t: Unit = f.target
	if t == null or t.dead or t.is_ballista:
		return
	var ox: float = f.x + f.face * float(f.T.w) * 0.35   # the flame starts at its head
	var oy: float = f.y
	var ax: float = t.x - ox
	var ay: float = t.y - oy
	var L: float = Vector2(ax, ay).length()
	if L > float(B.reach) or ax * f.face < maxf(0.5, L * 0.6):   # out of reach, or not in front of it
		return
	var ux: float = ax / (L if L > 0 else 1.0)
	var uy: float = ay / (L if L > 0 else 1.0)
	var burn: Array = []
	for o in F:
		if o.dead or not o.pass_pts.is_empty() or o.is_ballista or o.team == f.team or not can_hit(f, o):
			continue
		var dx: float = o.x - ox
		var dy: float = o.y - oy
		var along: float = dx * ux + dy * uy
		if along >= -1.0 and along <= float(B.reach) and absf(dy * ux - dx * uy) <= 1.6 + maxf(0.0, along) * 0.4:
			burn.append(o)
	burn.sort_custom(func(a, b): return dist(a, f) < dist(b, f))
	burn = burn.slice(0, int(B.n))
	f.fire_at = clock + float(B.rate)
	# the picture: from its mouth along the cone, as long as its reach (or to just past the farthest unit burned)
	var M: Array = f.T.mouthLand if f.grounded else f.T.mouth
	var mx: float = f.x + f.face * (float(M[0]) - 0.5) * float(f.T.w)
	var my: float = f.y - f.alt - f.h * (1.0 - float(M[1]))
	var far: float = L
	for o in burn:
		far = maxf(far, Vector2(o.x - ox, o.y - oy).length())
	var ln: float = minf(float(B.reach) + 2.0, far + 2.0)
	var ex: float = ox + ux * ln
	var ey: float = oy + uy * ln - (t.alt if _flying(t) else 0.0) - 1.0
	var ty: float = t.y - (t.alt if _flying(t) else 0.0)
	var spray: bool = not _flying(t) and absf(t.x - mx) < 9.0 and ty > my   # close in front, on the ground: it sprays fire down at them
	fx.append({"type": "flame", "spray": spray, "mx": mx, "my": my, "ex": ex, "ey": ey, "tx": t.x, "ty": ty})
	if f.miss_next:   # War Trumpet: this breath does no harm
		f.miss_next = false
		return
	for o in burn:
		hit(o, f, float(B.dmg) / float(f.T.dmg), false, "breath")   # (fire, not a bite: no quills back)


# ---- Griffin ----

## At the start of the battle it swoops (twice its flying speed) to the enemy's front line and lands there. Every enemy on the
## ground near where it lands is knocked back a little and takes 2. Then it screeches: every enemy shooter misses its next 2 shots,
## and every enemy charge stops.
func _gswoop_step(f: Unit, dt: float) -> bool:
	var S: Dictionary = f.gswoop
	var G: Dictionary = f.T.gswoop
	var dir: int = 1 if f.team == HOLD else -1
	var tgt: Unit = S.get("t", null)
	if tgt == null or tgt.dead:
		var best: Unit = null
		var bx: float = 1e9
		for o in F:
			if o.team == f.team or o.dead or not o.pass_pts.is_empty() or _flying(o) or o.is_ballista or o.on_wall >= 0:
				continue
			var v: float = o.x * dir
			if v < bx:
				bx = v
				best = o
		if best == null:
			f.gswoop = {}
			return false
		S.t = best
		tgt = best
	var tx: float = tgt.x - dir * 2.5
	var dx: float = tx - f.x
	var dy: float = tgt.y - f.y
	var d: float = Vector2(dx, dy).length()
	f.target = tgt
	f.engaged = false
	S.time = float(S.get("time", 0.0)) + dt
	if d > 1.2 and float(S.time) < 6.0:
		var st: float = float(f.T.speed) * float(G.mult) * dt
		f.vx = dx / d * minf(st, d)
		f.vy = dy / d * minf(st, d)
		f.walking = true
		f.phase += dt * 9.0
		if absf(dx) > 0.5:
			f.face = 1 if dx > 0 else -1
		return true
	f.gswoop = {}
	f.grounded = true   # it stays on the ground from then on
	_griffin_land(f)
	return true


func _griffin_land(f: Unit) -> void:
	var G: Dictionary = f.T.gswoop
	for o in F:
		if o.team == f.team or o.dead or not o.pass_pts.is_empty() or _flying(o) or o.is_ballista or o.on_wall >= 0:
			continue
		if Vector2(o.x - f.x, o.y - f.y).length() <= float(G.radius):
			hit(o, f, float(G.dmg) / float(f.T.dmg))
			if not o.dead:
				_knock_back(f, o)
	fx.append({"type": "quake", "x": f.x, "y": f.y, "w": float(f.T.w), "big": false})
	_screech(f)


func _screech(f: Unit) -> void:
	var G: Dictionary = f.T.gswoop
	fx.append({"type": "screech", "x": f.x + f.face * float(f.T.w) * 0.32, "y": f.y - f.alt - f.h * 0.72})
	for o in F:
		if o.team == f.team or o.dead:
			continue
		if _shooter(o):
			o.miss_shots = maxi(o.miss_shots, int(G.miss))
		for rd in o.riders:
			rd.att.miss_shots = int(G.miss)
		o.rcharge_wait = false
		if o.rcharge:
			_end_charge(o)
		o.charge_t = 0.0
		if o.T.has("charge"):
			o.charge_used = true
		o.charge_hit = false
		o.boost = 0.0
		o.burst_pending = false
		o.mcharge = false
		o.pcharge = false
		o.tcharge = false


# ---- Minotaur ----

## Its charge: the first hit kills outright; the big special units (Palaeoloxodon, Laser Tank, Dragon) instead take a normal
## hammer blow and are stunned for 4 seconds, even the ones nothing else can stun.
func _charge_hit(f: Unit, t: Unit) -> void:
	f.mcharge = false
	if t.T.get("stopsCharge", false):   # a Triceratops stops the charge: a normal blow
		hit(t, f)
		return
	if t.T.has("dodgeCharge") and rng.randf() < float(t.T.dodgeCharge):   # a Dilophosaurus jumps aside
		return
	if SPECIAL.has(t.key) or t.key == "dragon":
		hit(t, f)
		if not t.dead:
			var d: float = float(f.T.mcharge.stun)
			t.stun = maxf(t.stun, d)
			t.force_stun = clock + d
		return
	hit(t, _pseudo(f.team, maxf(1.0, ceilf(t.hp)), "melee"))


# ---- Dinosaurs ----

## Pachycephalosaurus: every head-butt that lands slows that enemy for the rest of the battle (once per enemy, it doesn't build up).
func _pachy_hit(f: Unit, t: Unit) -> void:
	var landed: bool = hit(t, f)
	f.pcharge = false
	if landed and not t.dead and not t.slowed and not t.is_ballista:
		t.slowed = true
		t.slow_spd = float(f.T.slowHit.spd)
		t.slow_rate = float(f.T.slowHit.rate)


## Triceratops: when its opening charge reaches the enemy line it shoves up to 6 enemies on the ground around it back.
func _trike_impact(f: Unit, t: Unit) -> void:
	f.tcharge = false
	var near: Array = F.filter(func(o): return not o.dead and o.pass_pts.is_empty() and not o.is_ballista and o.team != f.team and (not _flying(o) or downed(o)) and gap(f, o) <= float(f.T.range) + 3.0 and (levels.is_empty() or _same_level(f, o)))
	near.sort_custom(func(a, b): return gap(f, a) < gap(f, b))
	for o in near.slice(0, int(f.T.tcharge.n)):
		_knock_back(f, o)
	fx.append({"type": "dust", "x": f.x, "y": f.y, "face": f.face, "w": float(f.T.w)})
	fx.append({"type": "quake", "x": f.x, "y": f.y, "w": float(f.T.w), "big": false})


## Triceratops: every attack also gores up to 5 enemy shooters within its reach, full damage each.
func _horn_sweep(f: Unit, t: Unit) -> void:
	var near: Array = F.filter(func(o): return o != t and not o.dead and o.pass_pts.is_empty() and not o.is_ballista and o.team != f.team and _shooter(o) and (not _flying(o) or downed(o)) and gap(f, o) <= float(f.T.range) + 1.5 and (levels.is_empty() or _same_level(f, o)))
	near.sort_custom(func(a, b): return gap(f, a) < gap(f, b))
	for o in near.slice(0, int(f.T.hornSweep.n)):
		hit(o, f)


## At the start: every Triceratops on the field moves into the lane of an enemy Rhino (spread over them if there are fewer Triceratops).
func _line_up_trikes() -> void:
	for t in 2:
		var tr: Array = F.filter(func(f): return f.team == t and not f.dead and f.T.get("stopsCharge", false))
		tr.sort_custom(func(a, b): return a.y < b.y)
		var rh: Array = F.filter(func(o): return o.team != t and not o.dead and o.T.has("rhinoCharge") and (o.rcharge or o.rcharge_wait))
		rh.sort_custom(func(a, b): return a.y < b.y)
		if tr.is_empty() or rh.is_empty():
			continue
		var pairs: Array = []
		if tr.size() >= rh.size():
			for i in rh.size():
				pairs.append([tr[i], rh[i]])
		else:
			for i in tr.size():
				pairs.append([tr[i], rh[roundi(i * (rh.size() - 1) / float(maxi(1, tr.size() - 1)))]])
		for p in pairs:
			var tk: Unit = p[0]
			tk.lane = p[1]
			tk.y = minf(AH - 1.5, maxf(_min_y(tk), (p[1] as Unit).y))


## Triceratops: an enemy charge that reaches it stops there (a Rhino, Minotaur or Pachycephalosaurus charge, or a Triceratops').
func _trike_stops() -> void:
	for f in F:
		if f.dead or not f.T.get("stopsCharge", false):
			continue
		for o in F:
			if o.dead or o.team == f.team or not charging(o) or _flying(o):
				continue
			if gap(f, o) > float(f.T.range) + 1.5 or (not levels.is_empty() and not _same_level(f, o)):
				continue
			o.mcharge = false
			o.pcharge = false
			o.tcharge = false
			if o.charge_t > 0:
				o.charge_t = 0.0
			o.rcharge_wait = false
			if o.rcharge:
				_end_charge(o)
				o.trampled[f.id] = true


## Megaraptor: every bite also catches a second enemy within reach.
func _twin_bite(f: Unit, t: Unit) -> void:
	var best: Unit = null
	var bd: float = 1e9
	for o in F:
		if o == t or o.dead or not o.pass_pts.is_empty() or o.is_ballista or o.team == f.team or not can_hit(f, o) or (_flying(o) and not downed(o)):
			continue
		if not levels.is_empty() and not _same_level(f, o):
			continue
		var g: float = gap(f, o)
		if g <= float(f.T.range) + 1.5 and g < bd:
			bd = g
			best = o
	if best != null:
		hit(best, f)


## Stegosaurus: its tail swing hits up to 8 enemies all around it (its target and the 7 nearest), and every one left standing is stunned.
func _tail_swing(f: Unit, t: Unit) -> void:
	var S: Dictionary = f.T.tail
	var reach: float = float(f.T.w) * 0.5 + float(S.reach)
	var near: Array = F.filter(func(o): return o != t and not o.dead and o.pass_pts.is_empty() and not o.is_ballista and o.team != f.team and (not _flying(o) or downed(o)) and dist(f, o) <= reach and (levels.is_empty() or _same_level(f, o)))
	near.sort_custom(func(a, b): return dist(f, a) < dist(f, b))
	near = near.slice(0, int(S.n) - 1)
	for o in near:
		hit(o, f)
	for o in [t] + near:
		if not o.dead and not o.T.get("stunImmune", false) and not o.T.has("beam"):
			o.stun = maxf(o.stun, float(S.stun))
	fx.append({"type": "quake", "x": f.x, "y": f.y, "w": float(f.T.w), "big": false})


# =====================================================================
# Trees and Ferns maps
# Trees: the field in three bands, left to right: a forest of 24 trees across the left third (the side holding the map
# starts among them), ferns out to two-thirds of the way across, and open ground for the last third. Trees block the way
# (big units need more room to get round them) and stop arrows and lasers: a shot that flies into a tree sticks in it.
# Ground units in the forest are hidden from shooters; melee and the Laser Tank's beam can still reach them.
# Ferns: ferns all over the field. They don't block anyone; they sway as units push through (drawn by the view).
# =====================================================================

const FOREST_X := AW / 3.0
const TREE_TALL := 1.25                 # the tree pictures are drawn 25% taller and 10% thicker than they came
const TREE_THICK := 1.1
const TREE_R := 1.1                     # a trunk's radius on the ground
const TREE_SHOT_R := 1.5 * TREE_THICK   # shots are stopped a little wider than the trunk (the low branches)
const TREES_X1 := 32.7                  # the furthest trunk from the left edge
const TREE_SPOTS := [[7.7, 14.5], [17.1, 14.5], [26.7, 14.5], [29.1, 21.2], [3.2, 21.4], [20.6, 23.2], [11.9, 23.4], [32.1, 28], [1.8, 30.1], [24.9, 31.5], [9.4, 32.3], [17, 32.4],
	[32.7, 36.4], [4.6, 39.6], [22, 40.4], [12.8, 41.8], [29.9, 43.7], [4.7, 48.5], [17.8, 48.9], [27, 50.3], [10.5, 56.1], [1.9, 57.5], [19, 57.5], [27.5, 57.5]]
## w = width on the field, ar = height/width, base = where the trunk meets the ground (fraction of the width), sh = shadow width
const TREE_ART := [
	{"key": "tree_conifer", "w": 6.84, "ar": 2.0231, "base": 0.4957, "sh": 0.62},
	{"key": "tree_broadleaf", "w": 9.36, "ar": 1.2385, "base": 0.4972, "sh": 0.7},
	{"key": "tree_treefern", "w": 8.46, "ar": 1.3346, "base": 0.4917, "sh": 0.5},
	{"key": "tree_gnarled", "w": 8.82, "ar": 1.2462, "base": 0.5338, "sh": 0.62}]
const TREE_KIND := [1, 3, 1, 2, 2, 0, 3, 1, 0, 3, 2, 1, 0, 1, 2, 3, 1, 2, 0, 3, 0, 1, 2, 3]
const TREE_FLIP := [1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0]
## w = width on the field, bx/by = where its roots meet the ground (fraction of the picture)
const FERN_ART := [
	{"key": "fern_clump", "w": 2.57, "bx": 0.52, "by": 0.63},
	{"key": "fern_drooping", "w": 4.59, "bx": 0.5, "by": 0.57},
	{"key": "fern_spreading", "w": 4.60, "bx": 0.52, "by": 0.65},
	{"key": "fern_fiddleheads", "w": 4.00, "bx": 0.45, "by": 0.8}]
const FERN_EACH := 40                   # Trees map: ferns reach two-thirds of the way across
const FERN_ALL_EACH := 60               # Ferns map: ferns all over the field

var trees: Array = []                   # {x, y, i}
var ferns: Array = []                   # {x, y, kind, w, flip, rx, ry}  (the view adds its sway state)
var _grids: Dictionary = {}             # route grids, one per body size


func _make_trees() -> void:
	for i in TREE_SPOTS.size():
		trees.append({"x": float(TREE_SPOTS[i][0]), "y": float(TREE_SPOTS[i][1]), "i": i})
	_make_ferns(false)


func _make_ferns(all: bool) -> void:
	var spots: Array = []
	var each: int = FERN_ALL_EACH if all else FERN_EACH
	var x1: float = AW - 1.5 if all else AW * 2.0 / 3.0
	var y0: float = 4.0 if all else 6.0
	for kind in FERN_ART.size():
		for n in each:
			var x: float = 0.0
			var y: float = 0.0
			var ok: bool = false
			var tries: int = 0
			while tries < 200 and not ok:
				x = _rnd(1.5, x1)
				y = _rnd(y0, AH - 1.0)
				ok = true
				for T in trees:   # not on a trunk
					if Vector2(x - T.x, (y - T.y) * 1.6).length() < 3.2:
						ok = false
						break
				if ok:            # and not piled on another fern
					var lim: float = 3.4 if tries < 120 else 2.4
					for p in spots:
						if Vector2(x - p.x, (y - p.y) * 1.4).length() < lim:
							ok = false
							break
				tries += 1
			spots.append({"x": x, "y": y, "kind": kind})
	for p in spots:
		var A: Dictionary = FERN_ART[p.kind]
		var w: float = float(A.w) * _rnd(0.85, 1.15)
		ferns.append({"x": p.x, "y": p.y, "kind": p.kind, "w": w, "flip": rng.randf() < 0.5, "rx": w * 0.42, "ry": w * 0.2})


## Room for a body beside an obstacle.
func m_pad(f: Unit) -> float:
	var fx0: float = float(f.T.get("footX", 0))
	return maxf(0.8, minf(4.0, fx0 if fx0 > 0 else float(f.T.w) * 0.25))


## How far a body's feet stay from a trunk side to side (big units need more room) ...
func _tree_clear(f: Unit) -> float:
	var p: float = m_pad(f)
	return TREE_R + p * 0.7 + maxf(0.0, p - 1.5) * 0.45


## ... and front to back (the Laser Tank and Alamosaurus are long but shallow).
func _tree_clear_y(f: Unit) -> float:
	var fy0: float = float(f.T.get("footY", 0))
	return TREE_R + maxf(0.8, fy0) * 0.7 + 0.3 if fy0 > 0 else _tree_clear(f)


## In the forest, or inside the castle's gateway.
func hidden_in(o: Unit) -> bool:
	if _flying(o):
		return false
	return (not trees.is_empty() and o.x < FOREST_X) or (not fort.is_empty() and fort_fade(o) < 0.5)


## Nothing blocks a shot to or from a flyer; on the ground a trunk can.
func clear_shot(a: Unit, b: Unit) -> bool:
	if _flying(a) or _flying(b):
		return true
	if not trees.is_empty() and _trunk_blocks(a.x, a.y, b.x, b.y):
		return false
	# shots to or from the walls go over the castle
	return fort.is_empty() or _high(a) or _high(b) or not _fort_blocks(a.x, a.y, b.x, b.y)


func _trunk_blocks(ax: float, ay: float, bx: float, by: float) -> bool:
	if minf(ax, bx) > TREES_X1 + TREE_SHOT_R:   # no trees out there
		return false
	var dx: float = bx - ax
	var dy: float = by - ay
	var L2: float = maxf(dx * dx + dy * dy, 1e-9)
	for T in trees:
		var t: float = clampf(((T.x - ax) * dx + (T.y - ay) * dy) / L2, 0.0, 1.0)
		if t <= 0.001 or t >= 0.999:
			continue
		if Vector2(ax + dx * t - T.x, ay + dy * t - T.y).length() < TREE_SHOT_R:
			return true
	return false


## A shot in flight: the first tree its ground track runs into (not counting a tree right at the target's feet), or -1.
func _tree_in_path(x0: float, y0: float, x1: float, y1: float, fx0: float, fy0: float) -> int:
	if minf(x0, x1) > TREES_X1 + TREE_SHOT_R:
		return -1
	var dx: float = x1 - x0
	var dy: float = y1 - y0
	var L2: float = maxf(dx * dx + dy * dy, 1e-9)
	var best: int = -1
	var bt: float = 2.0
	for T in trees:
		if Vector2(fx0 - T.x, fy0 - T.y).length() < TREE_SHOT_R + 0.4:
			continue
		var t: float = clampf(((T.x - x0) * dx + (T.y - y0) * dy) / L2, 0.0, 1.0)
		if t < bt and Vector2(x0 + dx * t - T.x, y0 + dy * t - T.y).length() < TREE_SHOT_R:
			bt = t
			best = int(T.i)
	return best


## The shot stops in the tree: an arrow sticks in the trunk for a moment, a laser fizzles out with a spark.
func _stick_in_tree(a: Shot, ti: int) -> void:
	var T: Dictionary = trees[ti]
	var lift: float = clampf(a.y - a.gy, -6.0, -0.9)   # how high the shot was flying
	var side: float = -1.0 if a.sx < T.x else 1.0      # and which side it came from
	var tip := Vector2(T.x + side * TREE_R * 0.35, T.y + lift)
	var length: float = 3.4 if a.kind == "laser" else (3.2 if a.kind == "short" else 4.4)
	var c: Vector2 = tip - Vector2.from_angle(a.ang) * length * 0.32
	fx.append({"type": "stuck", "x": c.x, "y": c.y, "ang": a.ang, "kind": a.kind, "mult": a.mult, "stun": a.stun, "team": a.team,
		"z": roundf(T.y * 10.0) + (-1.0 if a.sy < T.y else 1.0)})   # a shot from behind the tree goes in behind the trunk
	if a.kind == "laser":
		fx.append({"type": "mflash", "x": tip.x, "y": tip.y, "team": a.team})


## Is the straight walk from (x0,y0) to (x1,y1) clear of every trunk by at least c? (sy stretches distances up and down)
func _tree_seg_clear(x0: float, y0: float, x1: float, y1: float, c: float, sy: float) -> bool:
	if minf(x0, x1) > TREES_X1 + c:
		return true
	var dx: float = x1 - x0
	var dy: float = (y1 - y0) * sy
	var L2: float = maxf(dx * dx + dy * dy, 1e-9)
	for T in trees:
		var ty: float = (T.y - y0) * sy
		var t: float = clampf(((T.x - x0) * dx + ty * dy) / L2, 0.0, 1.0)
		var ex: float = x0 + dx * t - T.x
		var ey: float = dy * t - ty
		if ex * ex + ey * ey < c * c:
			return false
	return true


## The field as a grid of 1x1 squares, with the squares too close to a trunk (for this body size) shut.
func _tree_grid(c: float, sy: float, row_min: int) -> AStarGrid2D:
	var key: String = "%.2f/%.2f/%d" % [c, sy, row_min]
	if _grids.has(key):
		return _grids[key]
	var g := AStarGrid2D.new()
	g.region = Rect2i(0, 0, int(AW), int(AH))
	g.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_ONLY_IF_NO_OBSTACLES   # no cutting a corner past a shut square
	g.default_compute_heuristic = AStarGrid2D.HEURISTIC_OCTILE
	g.default_estimate_heuristic = AStarGrid2D.HEURISTIC_OCTILE
	g.update()
	var row_max: int = int(floor(AH - 2.0))
	for y in int(AH):
		if y < row_min or y > row_max:
			for x in int(AW):
				g.set_point_solid(Vector2i(x, y), true)
	var r: float = c + 0.3
	var r2: float = r * r
	for T in trees:
		var ry: float = r / maxf(sy, 0.05)
		for y in range(maxi(0, int(floor(T.y - ry - 1.0))), mini(int(AH), int(ceil(T.y + ry + 1.0)))):
			for x in range(maxi(0, int(floor(T.x - r - 1.0))), mini(int(AW), int(ceil(T.x + r + 1.0)))):
				var dx: float = x + 0.5 - T.x
				var dy: float = (y + 0.5 - T.y) * sy
				if dx * dx + dy * dy < r2:
					g.set_point_solid(Vector2i(x, y), true)
	_grids[key] = g
	return g


## The open square nearest a point, or (-1, -1).
func _near_open(g: AStarGrid2D, x: float, y: float) -> Vector2i:
	var W: int = int(AW)
	var H: int = int(AH)
	var cx: int = clampi(int(floor(x)), 0, W - 1)
	var cy: int = clampi(int(floor(y)), 0, H - 1)
	for r in 14:
		var best := Vector2i(-1, -1)
		var bd: float = 1e9
		for yy in range(cy - r, cy + r + 1):
			for xx in range(cx - r, cx + r + 1):
				if (absi(xx - cx) != r and absi(yy - cy) != r) or xx < 0 or yy < 0 or xx >= W or yy >= H:
					continue
				var q := Vector2i(xx, yy)
				if g.is_point_solid(q):
					continue
				var d: float = (xx + 0.5 - x) * (xx + 0.5 - x) + (yy + 0.5 - y) * (yy + 0.5 - y)
				if d < bd:
					bd = d
					best = q
		if best.x >= 0:
			return best
	return Vector2i(-1, -1)


## The next point to walk toward: straight there if nothing is in the way, otherwise along a route through the trees.
func _path_to(f: Unit, tx: float, ty: float) -> Vector2:
	if trees.is_empty():
		return Vector2(tx, ty)
	var c: float = _tree_clear(f)
	var sy: float = c / _tree_clear_y(f)
	if _tree_seg_clear(f.x, f.y, tx, ty, c - 0.15, sy):
		f.tp_set = false
		return Vector2(tx, ty)
	var stale: bool = not f.tp_set or clock >= f.tp_t or Vector2(f.tp_tx - tx, f.tp_ty - ty).length() > 1.5 \
		or (f.tp_has_wp and Vector2(f.tp_wp.x - f.x, f.tp_wp.y - f.y).length() < 0.8)
	if stale:
		var g: AStarGrid2D = _tree_grid(c, sy, int(ceil(_min_y(f) - 0.5)))
		var s: Vector2i = _near_open(g, f.x, f.y)
		var e: Vector2i = _near_open(g, tx, ty)
		var wp := Vector2.ZERO
		var has_wp: bool = false
		if s.x >= 0 and e.x >= 0 and s != e:
			var path: Array[Vector2i] = g.get_id_path(s, e)
			for k in range(1, path.size()):   # the farthest square along the route it can walk to in a straight line
				var q := Vector2(path[k].x + 0.5, path[k].y + 0.5)
				if _tree_seg_clear(f.x, f.y, q.x, q.y, c - 0.15, sy):
					wp = q
					has_wp = true
				elif has_wp:
					break
			if not has_wp and path.size() > 1:
				wp = Vector2(path[1].x + 0.5, path[1].y + 0.5)
				has_wp = true
		f.tp_set = true
		f.tp_t = clock + 0.35 + rng.randf() * 0.15
		f.tp_tx = tx
		f.tp_ty = ty
		f.tp_wp = wp
		f.tp_has_wp = has_wp
	return f.tp_wp if f.tp_has_wp else _tree_sidestep(f, tx, ty)


## When there's no route: step past the side of the first trunk in the way.
func _tree_sidestep(f: Unit, tx: float, ty: float) -> Vector2:
	var c: float = _tree_clear(f) + 0.4
	var dx: float = tx - f.x
	var dy: float = ty - f.y
	var L: float = maxf(Vector2(dx, dy).length(), 1e-9)
	var ux: float = dx / L
	var uy: float = dy / L
	var hit_t: Dictionary = {}
	var ht: float = 1e9
	for T in trees:
		var t: float = (T.x - f.x) * ux + (T.y - f.y) * uy
		if t <= 0 or t > L + c:
			continue
		var off: float = (T.x - f.x) * -uy + (T.y - f.y) * ux
		if absf(off) < c and t < ht:
			ht = t
			hit_t = T
	if hit_t.is_empty():
		return Vector2(tx, ty)
	if f.ts_tree != int(hit_t.i) or f.ts_t < clock:   # keep to one side of a tree once chosen
		var off2: float = (hit_t.x - f.x) * -uy + (hit_t.y - f.y) * ux
		f.ts_tree = int(hit_t.i)
		f.ts_s = -1 if off2 > 0 else 1
		f.ts_t = clock + 0.6
	var s: float = float(f.ts_s)
	var wx: float = hit_t.x + (-uy) * s * (c + 1.0)
	var wy: float = hit_t.y + ux * s * (c + 1.0)
	if wy < _min_y(f) + 0.2 or wy > AH - 1.6:   # that side is off the field: go the other way
		f.ts_s = -f.ts_s
		wx = hit_t.x + uy * s * (c + 1.0)
		wy = hit_t.y - ux * s * (c + 1.0)
	return Vector2(wx, clampf(wy, _min_y(f) + 0.2, AH - 1.6))


## Ground units are pushed back out of any trunk they've walked into.
func _push_out_of_trunks(L: Array) -> void:
	for f in L:
		if _flying(f):
			continue
		var c: float = _tree_clear(f)
		var sy: float = c / _tree_clear_y(f)
		for T in trees:
			var dx: float = f.x - T.x
			var dy: float = (f.y - T.y) * sy
			var d: float = Vector2(dx, dy).length()
			if d < c:
				if d < 1e-3:
					f.x = T.x + (-c if f.team == HOLD else c)
					f.y = clampf(T.y, _min_y(f), AH - 1.5)
				else:
					var k: float = c / d
					f.x = T.x + dx * k
					f.y = clampf(T.y + dy * k / sy, _min_y(f), AH - 1.5)


# =====================================================================
# Mountain map (a mountainside)
# The left third is the side of a mountain, held by the side on the left. Nobody on the ground can walk onto the rock: its foot
# is a ragged line. Three rock shelves hold the holder's starting shooters, with the high-ground bonus (+1 damage, 10% dodge,
# +50% range). Each shelf has steps up from the foot that melee can climb (the Alamosaurus and the Laser Tank are too big).
# The holder's other units start along the foot. Its reserves come down through two passes onto the middle and bottom shelves,
# then down those shelves' steps; they can't be attacked or fight on the way; a Megaraptor sprints the whole way down.
# Geometry traced from the picture (made in OpenArt).
# =====================================================================

const WALL_DMG := 1.0
const WALL_DODGE := 0.1
const WALL_RANGE := 1.5
const MS_FOOT := [23.32, 24.6, 25.19, 25.37, 26.13, 26.41, 27.45, 27.83, 28.35, 28.56, 28.87, 29.53, 29.74, 29.74, 29.53, 29.74, 30.5, 30.71, 31.09, 31.3, 31.3, 31.3, 31.75, 31.96, 32.13, 32.9, 33.07, 33.62, 33.62, 33.69, 33.69, 33.73, 33.9, 33.94, 33.69, 33.66, 34.28, 34.67, 34.67, 34.46, 34.67, 34.84, 34.84, 34.46, 34.87, 35.08, 35.08, 35.57, 36.12, 36.54, 36.54, 36.37, 35.88, 35.88, 35.74, 35.91, 35.91, 35.74, 35.57, 35.57, 36.19]
const MS_SHELVES := [
	{"x0": 15.27, "x1": 25.68, "y0": 6.92, "y1": 12.47, "top": Vector2(24.98, 11.77), "foot": Vector2(33.3, 19.76), "slots": [[21.0, 8.7], [23.6, 8.7], [21.0, 10.92], [23.6, 10.92]]},
	{"x0": 18.04, "x1": 30.54, "y0": 23.92, "y1": 31.91, "top": Vector2(28.11, 31.21), "foot": Vector2(36.74, 40.41), "slots": [[24.91, 26.48], [28.04, 26.48], [24.91, 29.67], [28.04, 29.67]]},
	{"x0": 18.04, "x1": 32.62, "y0": 47.52, "y1": 55.5, "top": Vector2(31.0, 48.3), "foot": Vector2(36.9, 42.6), "slots": [[26.06, 50.07], [29.7, 50.07], [26.06, 53.27], [29.7, 53.27]]}]
const MS_PASSES := [
	{"pts": [[1.39, 4.84], [3.47, 6.57], [5.21, 8.31], [6.94, 10.04], [8.68, 11.78], [10.41, 13.51], [13.88, 15.94], [17.35, 17.85], [20.82, 19.41], [24.29, 21.15], [25.85, 22.71], [26.37, 24.44]], "shelf": 1},
	{"pts": [[1.04, 30.86], [3.47, 31.91], [5.21, 32.95], [6.94, 33.99], [8.68, 35.38], [10.41, 36.76], [13.88, 38.5], [17.35, 40.41], [20.82, 41.27], [24.29, 43.01], [26.37, 44.74], [27.41, 46.48], [27.76, 48.39]], "shelf": 2}]
const MS_IMG := {"left": 0.0, "top": -0.019, "w": 36.747}

var mside: bool = false
var levels: Array = []        # the high ground: {x0, x1, y0, y1, top, foot, slots: [{x, y, u}]}
var pass_turn: int = 0


func _make_mountainside() -> void:
	mside = true
	for S in MS_SHELVES:
		var W: Dictionary = S.duplicate(true)
		var sl: Array = []
		for p in S.slots:
			sl.append({"x": float(p[0]), "y": float(p[1]), "u": null})
		W["slots"] = sl
		levels.append(W)


func _ms_foot_at(y: float) -> float:
	var yy: float = clampf(y, 0.0, AH)
	var i: int = mini(int(AH) - 1, int(floor(yy)))
	var fr: float = yy - i
	return float(MS_FOOT[i]) * (1.0 - fr) + float(MS_FOOT[i + 1]) * fr


## How close to the rock a body can stand.
func _ms_keep(f: Unit) -> float:
	return _ms_foot_at(f.y) + m_pad(f) * 0.8


func _ms_keep_T(T: Dictionary, y: float) -> float:
	var fx0: float = float(T.get("footX", 0))
	var pad: float = maxf(0.8, minf(4.0, fx0 if fx0 > 0 else float(T.w) * 0.25))
	return _ms_foot_at(y) + pad * 0.8


func _into_rock(f: Unit) -> bool:
	if not mside or f.team != HOLD or _flying(f):
		return false
	if not f.pass_pts.is_empty():
		return true
	if f.on_wall >= 0:
		return f.x <= float(levels[f.on_wall].x0) + 1.6
	return f.x <= _ms_keep(f) + 0.4


func range_of(f: Unit) -> float:
	return float(f.T.range) * (WALL_RANGE if (f.on_wall >= 0 and f.T.get("ranged", false)) else 1.0)


func _same_level(a: Unit, b: Unit) -> bool:
	return _flying(a) or _flying(b) or a.on_wall == b.on_wall


func _can_climb(f: Unit) -> bool:
	return not _flying(f) and not f.T.has("beam") and float(f.T.w) < 10.0


## Up on a shelf, and this one is too big for the steps.
func _out_of_reach(f: Unit, o: Unit) -> bool:
	return not levels.is_empty() and not f.T.get("ranged", false) and not _flying(f) and not _flying(o) and o.on_wall >= 0 and not _can_climb(f)


## Laser Tank: a shelf between it and a unit keeps the beam off (unless one of them is up on that shelf).
func _beam_clear(f: Unit, o: Unit) -> bool:
	if _flying(o):
		return true
	for i in levels.size():
		if i == o.on_wall or i == f.on_wall:
			continue
		var blocks: Array = levels[i].get("blocks", [levels[i]])
		for b in blocks:
			if _seg_hits(f.x, f.y, o.x, o.y, b):
				return false
	if not fort.is_empty() and o.on_wall < 0 and f.on_wall < 0 and _fort_blocks(f.x, f.y, o.x, o.y):
		return false
	return true


## Does the straight line a-b pass through rectangle r?
func _seg_hits(ax: float, ay: float, bx: float, by: float, r: Dictionary) -> bool:
	var t0: float = 0.0
	var t1: float = 1.0
	var dx: float = bx - ax
	var dy: float = by - ay
	for pq in [[-dx, ax - float(r.x0)], [dx, float(r.x1) - ax], [-dy, ay - float(r.y0)], [dy, float(r.y1) - ay]]:
		var p: float = pq[0]
		var q: float = pq[1]
		if p == 0.0:
			if q < 0.0:
				return false
		else:
			var t: float = q / p
			if p < 0.0:
				if t > t1:
					return false
				t0 = maxf(t0, t)
			else:
				if t < t0:
					return false
				t1 = minf(t1, t)
	return t0 < t1


## Where to step next to reach (tx, ty) on level w (a shelf, or -1 for the ground): down the steps, up the steps.
func _goal_point(f: Unit, tx: float, ty: float, w: int) -> Vector2:
	if f.climbing >= 0:
		var C: Dictionary = levels[f.climbing]
		if Vector2(C.top.x - f.x, C.top.y - f.y).length() < 0.9:
			f.on_wall = f.climbing
			f.climbing = -1
		else:
			return C.top
	if f.descending >= 0:
		var D: Dictionary = levels[f.descending]
		if Vector2(D.foot.x - f.x, D.foot.y - f.y).length() < 1.0:
			f.descending = -1
		else:
			return D.foot
	if f.on_wall >= 0:
		if f.on_wall == w:
			return Vector2(tx, ty)
		var C2: Dictionary = levels[f.on_wall]
		if Vector2(C2.top.x - f.x, C2.top.y - f.y).length() < 0.9:
			f.descending = f.on_wall
			f.on_wall = -1
			return C2.foot
		return C2.top
	if w >= 0:
		var W: Dictionary = levels[w]
		if Vector2(W.foot.x - f.x, W.foot.y - f.y).length() < 1.3:
			f.climbing = w
			return W.top
		return _route(f, W.foot.x, W.foot.y)
	return _route(f, tx, ty)


## Spots up high that nobody holds: [[shelf, slot], ...]
func _free_slots() -> Array:
	var out: Array = []
	for wi in levels.size():
		var sl: Array = levels[wi].slots
		for si in sl.size():
			var u = sl[si].u
			if u != null and (u.dead or u.gone or u.fleeing):
				sl[si]["u"] = null
			if sl[si].u == null:
				out.append([wi, si])
	return out


func _take_slot(f: Unit, wi: int, si: int) -> void:
	levels[wi]["slots"][si]["u"] = f
	f.slot_w = wi
	f.slot_i = si
	f.wall_goal = wi


# =====================================================================
# Fortress map
# Two thick walls on the holder's side, one down from the top edge and one up from the bottom, with the fortress between
# them. The holder's shooters start up on the walls (+1 damage, +50% range, 10% of hits on them miss); the way up is the
# stairs behind each wall. The fortress's passage runs straight through it: the holder's army marches in at the back and out
# of the gate, which faces the enemy; the enemy's melee must batter the gate down (150 health) to get in. Nothing on the
# ground shoots through the fortress (shooters up on the walls fire over it). The holder fights with +5% health and
# +1 damage. Two trebuchets stand behind the walls (scenery). Pictures: Ethan's bone-and-tusk and steel designs (OpenArt).
# =====================================================================

const WALL_X0 := 27.36
const WALL_X1 := 32.45
const FORT_HP := 1.05
const FORT_DMG := 1.0
## the wall pictures: left, width, how far the picture's top sits above the wall's lower end, the walkway's length,
## the stairs (foot and top x, and how far up from the lower end), the walkway's x, the tower at the lower end
const WALL_ART := {
	"dino": {"left": 24.789, "w": 10.599, "topAbove": 27.722, "walkLen": 17.34, "stairMid": 12.6, "footX": 24.01, "topX": 29.32, "walkX": 30.0, "towerTop": 3.92, "x0": WALL_X0, "x1": WALL_X1},
	"robot": {"left": 24.729, "w": 10.6, "topAbove": 28.026, "walkLen": 18.336, "stairMid": 14.539, "footX": 24.029, "topX": 29.419, "walkX": 30.0, "towerTop": 3.299, "x0": 27.771, "x1": 32.577},
	"mammal": {"left": 24.47, "w": 10.39, "topAbove": 27.72, "walkLen": 15.23, "stairMid": 13.54, "footX": 23.503, "topX": 28.053, "walkX": 30.0, "towerTop": 8.47, "x0": 26.903, "x1": 33.493}}
## the fortress pictures (left, top, width) and the gate on top of them (the Robots' gate is 8 frames, closed to open)
const FORT_ART := {
	"dino": {"left": 17.962, "top": 13.144, "w": 23.894, "gate": {"left": 35.405, "top": 24.494, "w": 5.336, "n": 1}},
	"robot": {"left": 17.995, "top": 14.015, "w": 24.037, "gate": {"left": 36.143, "top": 27.035, "w": 3.646, "n": 8}},
	"mammal": {"left": 20.904, "top": 10.843, "w": 25.0, "gate": {"left": 37.071, "top": 27.134, "w": 2.542, "n": 8}}}
## the passage: in at the back (inX), out of the gate (gateX); the rest of the footprint is solid
const FORT_DEF := {
	"dino": {"inX": 19.76, "gateX": 39.31, "gy": 32.41, "half": 2.6, "hpAt": Vector2(38.14, 24.22), "spans": [[0.0, 20.0], [37.4, 61.4]],
		"rects": [{"x0": 18.0, "x1": 40.0, "y0": 20.0, "y1": 29.81}, {"x0": 22.7, "x1": 36.5, "y0": 35.01, "y1": 40.0}]},
	"robot": {"inX": 18.98, "gateX": 39.21, "gy": 32.4, "half": 2.6, "hpAt": Vector2(37.75, 26.47), "spans": [[0.0, 20.0], [37.0, 61.0]],
		"rects": [{"x0": 19.09, "x1": 41.68, "y0": 20.0, "y1": 29.8}, {"x0": 23.59, "x1": 34.6, "y0": 35.01, "y1": 38.4}]},
	"mammal": {"inX": 23.0, "gateX": 39.0, "gy": 32.4, "half": 2.6, "hpAt": Vector2(38.35, 26.9), "spans": [[0.0, 27.0], [35.0, 61.4]],
		"rects": [{"x0": 23.0, "x1": 44.5, "y0": 24.5, "y1": 29.81}, {"x0": 24.5, "x1": 37.5, "y0": 35.01, "y1": 36.6}, {"x0": 28.5, "x1": 40.0, "y0": 12.5, "y1": 24.5}]}}
const TREB_ART := {"dino": {"w": 13.0, "ar": 0.96, "base": [0.07, 0.93, 2.6]}, "robot": {"w": 13.0, "ar": 0.883, "base": [0.07, 0.93, 2.6]}}
const TREB_SPOTS := [Vector2(15.5, 17.0), Vector2(15.5, 47.5)]   # the middle of each trebuchet's base, at its foot
const WALL_SLOTS := 5

var treb_spots: Array = []   # the fortress's trebuchets: [{x, y}] (scenery)


## The holder fights with +5% health and +1 damage on the fortress map.
func fort_buff(team: int) -> bool:
	return map == "fortress" and team == HOLD


func unit_hp(team: int, key: String) -> float:
	return snappedf(float(TYPES[key].hp) * (FORT_HP if fort_buff(team) else 1.0) * float(mod_hp[team]), 0.01)


func _make_fortress() -> void:
	var fac: String = "robot" if robo_holder() else ("mammal" if mammal_holder() else "dino")
	var D: Dictionary = FORT_DEF[fac]
	var A: Dictionary = WALL_ART[fac]
	# the two walls (raised levels, like the castle's walkway): five spots for shooters each, stairs at the back
	for i in 2:
		var y0: float = float(D.spans[i][0])
		var y1: float = float(D.spans[i][1])
		var walk_end: float = y1 - 24.0 + float(A.walkLen)
		var sy: float = y1 - float(A.stairMid)
		var lo: float = y0 + (5.0 if i == 0 else 3.5)
		var hi: float = walk_end - 0.4
		var sl: Array = []
		for k in WALL_SLOTS:
			sl.append({"x": float(A.walkX), "y": lo + (hi - lo) * k / (WALL_SLOTS - 1), "u": null})
		levels.append({"kind": "wall", "i": i, "x0": float(A.x0), "x1": float(A.x1), "y0": y0 + 0.8, "y1": y1 - float(A.towerTop),
			"foot": Vector2(float(A.footX), sy), "top": Vector2(float(A.topX), sy), "pri": 0,
			"blocks": [{"x0": float(A.x0), "x1": float(A.x1), "y0": -50.0 if y0 <= 0.0 else y0, "y1": AH + 50.0 if y1 >= AH else y1}], "slots": sl})
	fort = {"inX": D.inX, "gateX": D.gateX, "gy": D.gy, "half": D.half, "hp": GATE_HP, "max": GATE_HP, "broken": false, "flash": 0.0,
		"open": 0.0, "rects": D.rects, "castle": false, "hpAt": D.hpAt}
	var U: Dictionary = D.rects[0]
	var L: Dictionary = D.rects[1]
	# into the back of the fortress, out of its gate, and round its outer corners
	var wp: Array = [Vector2(float(U.x0) - 3.6, float(D.gy)), Vector2(float(D.gateX) + 3.5, float(D.gy)),
		Vector2(float(U.x0) - 3.6, float(U.y0) - 1.4), Vector2(float(U.x1) + 3.6, float(U.y0) - 1.4),
		Vector2(float(L.x0) - 3.6, float(L.y1) + 1.4), Vector2(float(L.x1) + 3.6, float(L.y1) + 1.4)]
	# the trebuchets: their bases are solid, with ways round them
	var TA: Dictionary = TREB_ART["robot" if fac == "robot" else "dino"]
	var tw: float = float(TA.w)
	var trebs: Array = []
	treb_spots = []
	for p in TREB_SPOTS:
		var left: float = p.x - tw / 2.0
		var r: Dictionary = {"x0": left + tw * float(TA.base[0]), "x1": left + tw * float(TA.base[1]), "y0": p.y - float(TA.base[2]), "y1": p.y - 0.2}
		trebs.append(r)
		treb_spots.append({"x": p.x, "y": p.y})
		wp.append_array([Vector2(r.x0 - 3.6, r.y0 - 1.4), Vector2(r.x1 + 3.6, r.y0 - 1.4), Vector2(r.x0 - 3.6, r.y1 + 1.4), Vector2(r.x1 + 3.6, r.y1 + 1.4)])
	fort["trebs"] = trebs
	fort["wp"] = wp
	_make_path(float(D.gateX) - 1.2, AW, float(D.gy))


# =====================================================================
# Castle map
# Ethan's sketch: two hexagonal archers' nests joined by a thick wall, with an angled wall running from each nest back to the
# top and bottom edges. The holder's army marches out of a hidden gate in the middle of the centre wall; the enemy's melee must
# batter that spot down (150 health). The holder's shooters start up on the centre wall's walkway and along the two angled
# walls (high-ground bonus); the way up is the stairs behind the walls. A ballista on each nest shoots anything in front of it;
# only shooters and flyers can reach the ballistas. Units passing through the gate are inside the castle: hidden from shooters.
# =====================================================================

const GATE_HP := 150.0
const CASTLE_DEF := {"inX": 26.6, "gateX": 33.2, "gy": 30.0, "half": 2.6, "hpAt": Vector2(34.2, 25.0),
	"rects": [{"x0": 24.6, "x1": 35.4, "y0": 13.5, "y1": 21.3}, {"x0": 26.6, "x1": 33.2, "y0": 21.3, "y1": 27.4},
		{"x0": 26.6, "x1": 33.2, "y0": 32.6, "y1": 41.0}, {"x0": 24.6, "x1": 35.4, "y0": 41.0, "y1": 49.8}]}
const OUT_Y := [50.0, 17.5, 57.0, 12.0]   # where the holder's Laser Tank and Alamosaurus start, out in front
const BALLISTA := {"hp": 50.0, "rate": 3.5, "dmg": 15, "range": 48.0, "turn": 35.0, "turnSpeed": 90.0, "w": 8.8,
	"spots": [Vector2(30, 16), Vector2(30, 44)]}
## ar = height/width; pivot: where the bow turns (fraction of the picture); muzzle: where its shot leaves
const BALLISTA_ART := {"dino": {"ar": 0.9667, "pivot": [0.50, 0.53], "muzzle": [0.97, 0.42]},
	"robot": {"ar": 0.9567, "pivot": [0.47, 0.36], "muzzle": [0.97, 0.29]}}
## the castle pictures (field units: left, top, width)
const CASTLE_ART := {"dino": {"mid": [24.0, 10.0, 11.897], "up": [-11.0, -15.05, 40.182], "lo": [-11.3, 35.2, 41.235]},
	"robot": {"mid": [23.901, 10.178, 12.194], "up": [-11.974, -13.479, 42.263], "lo": [-11.966, 35.56, 42.623]}}
const PATH_AR := 10.0   # the stone path picture is ten times as long as it is wide

var fort: Dictionary = {}   # the castle's gate: {inX, gateX, gy, half, hp, max, broken, flash, rects, wp}
var bal: Array = []         # the castle ballistas (Units that never move)
var bal_att: Unit = null    # who the ballistas' shots count as coming from
var path_rect: Rect2 = Rect2()
var _rects_cache: Dictionary = {}


func robo_holder() -> bool:
	return factions[HOLD] == "Robots"


func mammal_holder() -> bool:
	return factions[HOLD] == "Mammals"


func _castle_band(a: float, b: float, c: float, d: float, top: bool) -> Array:
	# an angled wall's footprint as steps along it (open past the field's edge so nobody slips round the end)
	# a + b*x: the picture's upper edge along the wall; c + d*x: its lower edge
	var xs: Array = [-1.0, 3.0, 7.0, 11.0, 15.0, 19.0, 23.0, 25.5]
	var R: Array = []
	for i in xs.size() - 1:
		var x0: float = xs[i]
		var x1: float = xs[i + 1]
		R.append({"x0": x0, "x1": x1, "y0": minf(a + b * x0, a + b * x1) + 3.0, "y1": maxf(c + d * x0, c + d * x1) + 0.3})
	if top:
		R[0]["y0"] = -50.0
	else:
		R[0]["y1"] = AH + 50.0
	return R


func _make_castle() -> void:
	var D: Dictionary = CASTLE_DEF
	fort = {"inX": D.inX, "gateX": D.gateX, "gy": D.gy, "half": D.half, "hp": GATE_HP, "max": GATE_HP, "broken": false, "flash": 0.0,
		"open": 0.0, "rects": D.rects, "castle": true, "hpAt": D.hpAt}
	# the centre wall's walkway (filled first; reached from inside the castle, behind the gate), then the two angled walls
	var mid_slots: Array = []
	for p in [[30.1, 22.6], [30.1, 37.6], [30.1, 25.1], [30.1, 35.1], [30.1, 27.6], [30.1, 32.6], [30.1, 30.1]]:
		mid_slots.append({"x": p[0], "y": p[1], "u": null})
	levels.append({"kind": "mid", "x0": 28.9, "x1": 31.3, "y0": 22.3, "y1": 38.0, "foot": Vector2(25, 30), "top": Vector2(30.1, 30),
		"blocks": [], "pri": 0, "slots": mid_slots})
	for side in 2:
		var xa: float = 13.5 if side == 0 else 2.0
		var xb: float = 22.4
		var wa: float = -6.3 if side == 0 else 58.9
		var wb: float = 0.72 if side == 0 else -0.73
		var sl: Array = []
		for x in ([15.5, 17.7, 19.9, 22.1] if side == 0 else [4.0, 7.6, 11.2, 14.8, 18.4, 22.0]):
			sl.append({"x": x, "y": wa + wb * x, "u": null})
		var band: Array = _castle_band(-10.1, 0.72, 1.2, 0.69, true) if side == 0 else _castle_band(55.1, -0.73, 66.0, -0.733, false)
		levels.append({"kind": "walk", "x0": xa, "x1": xb, "y0": minf(wa + wb * xa, wa + wb * xb), "y1": maxf(wa + wb * xa, wa + wb * xb),
			"wa": wa, "wb": wb, "foot": Vector2(9, 10.5) if side == 0 else Vector2(21, 39.5),
			"top": Vector2(15.5, 4.9) if side == 0 else Vector2(19.5, 44.7), "blocks": band, "pri": 1, "slots": sl})
	# the gate, round the nests' fronts, and inside
	fort["wp"] = [Vector2(D.inX - 3.6, D.gy), Vector2(D.gateX + 3.5, D.gy), Vector2(38.8, 22), Vector2(38.8, 38), Vector2(38.8, 10),
		Vector2(38.8, 52), Vector2(21, 24), Vector2(21, 36)]
	_make_ballistas()
	_make_path(float(D.gateX) - 1.2, AW, float(D.gy))


func _make_ballistas() -> void:
	var A: Dictionary = BALLISTA_ART.robot if robo_holder() else BALLISTA_ART.dino
	var w: float = BALLISTA.w
	var h: float = w * float(A.ar)
	bal_att = Unit.new()
	bal_att.team = HOLD
	bal_att.key = "ballista"
	bal_att.T = {"dmg": BALLISTA.dmg, "hitKey": "ballista", "w": 1.0}
	for p in BALLISTA.spots:
		var B := Unit.new()
		B.id = uid
		uid += 1
		B.team = HOLD
		B.key = "ballista"
		B.is_ballista = true
		B.T = {"ranged": true, "flying": false, "footX": 2.4, "footY": 1.2, "aimFrac": 0.5, "w": w * 0.6, "hp": BALLISTA.hp, "hitKey": "ballista", "dmg": 0}
		B.x = p.x
		B.y = p.y - h * 0.45
		B.h = h * 0.5
		B.hp = BALLISTA.hp
		B.cd = _rnd(1.0, 2.0)
		var L: float = p.x - w / 2.0
		var Tp: float = p.y - h
		B.spot = Vector2(L + float(A.pivot[0]) * w, Tp + float(A.pivot[1]) * h)                         # the pivot
		B.plan = Vector2((float(A.muzzle[0]) - float(A.pivot[0])) * w, (float(A.muzzle[1]) - float(A.pivot[1])) * h)   # pivot -> muzzle
		B.stand_y = p.y   # where it stands (for drawing order)
		B.aim = 0.0
		bal.append(B)


func bal_muzzle(B: Unit) -> Vector2:
	return B.spot + B.plan.rotated(deg_to_rad(B.aim))


func _update_ballistas(dt: float) -> void:
	for B in bal:
		B.kick = maxf(0.0, B.kick - dt * 4.0)   # its kick back after a shot
		B.flash = maxf(0.0, B.flash - dt)
		if B.dead:
			continue
		B.cd = maxf(0.0, B.cd - dt)
		# the nearest enemy in front of it, inside its turning arc and its reach, that it can see
		var best: Unit = null
		var bd: float = 1e9
		for o in F:
			if o.team == B.team or o.dead or not o.pass_pts.is_empty() or hidden_in(o) or shielded(o) or soaring_over(o):
				continue
			var dx: float = o.x - B.spot.x
			var dy: float = (o.y - o.alt - o.h * 0.5) - B.spot.y
			var d: float = Vector2(dx, dy).length()
			if dx <= 0 or d > BALLISTA.range or absf(rad_to_deg(atan2(dy, dx))) > BALLISTA.turn + 5.0:
				continue
			if d < bd:
				bd = d
				best = o
		var want: float = 0.0
		if best != null:
			want = clampf(rad_to_deg(atan2(best.y - best.alt - best.h * 0.5 - B.spot.y, best.x - B.spot.x)), -BALLISTA.turn, BALLISTA.turn)
		var st: float = BALLISTA.turnSpeed * dt
		B.aim += clampf(want - B.aim, -st, st)
		if best != null and B.cd == 0 and absf(want - B.aim) < 3.0:
			B.cd = BALLISTA.rate
			B.kick = 1.0
			var m: Vector2 = bal_muzzle(B)
			var robo: bool = robo_holder()   # the Robots' ballista fires lasers, the others bolts
			var s := Shot.new()
			s.att = bal_att
			s.t = best
			s.kind = "laser" if robo else "bolt"
			s.air = true
			s.spd = ARROW_SPEED * (2.2 if robo else 1.5)
			s.x = m.x
			s.y = m.y
			s.sx = m.x
			s.sy = m.y
			s.gx = m.x
			s.gy = m.y
			s.team = B.team
			s.big = true
			s.ang = deg_to_rad(B.aim)
			s.aim = Vector2(best.x, best.y - best.alt - best.h * 0.5)
			shots.append(s)
			if robo:
				fx.append({"type": "mflash", "x": m.x, "y": m.y, "team": B.team})


## The stone path from under the gate out to the enemy's edge, with a few patches of ferns along both sides.
func _make_path(x0: float, x1: float, cy: float) -> void:
	var w: float = x1 - x0
	var h: float = w / PATH_AR
	path_rect = Rect2(x0, cy - h / 2.0, w, h)
	var top: float = cy - h / 2.0 + 0.4
	var bot: float = cy + h / 2.0 + 0.9
	var xs: Array = [48.0, 59.0, 71.0, 83.0, 94.0]
	for i in xs.size():
		var px: float = xs[i]
		if px < x0 + 3.0 or px > x1 - 1.5:
			continue
		var n: int = 2 + (i % 2)
		var side: float = bot if i % 2 == 1 else top
		for k in n:
			var kind: int = (i * 3 + k * 2) % FERN_ART.size()
			var fw: float = float(FERN_ART[kind].w) * _rnd(0.85, 1.05)
			var x: float = px + (k - (n - 1) / 2.0) * 2.4 + _rnd(-0.4, 0.4)
			var y: float = side + _rnd(-0.3, 0.3)
			ferns.append({"x": x, "y": y, "kind": kind, "w": fw, "flip": (i + k) % 2 == 1, "rx": fw * 0.42, "ry": fw * 0.2})


func _gpad(f: Unit) -> float:
	return clampf(float(f.T.w) * 0.35, 1.0, 3.2)


## Units in the gateway are inside the castle: they fade out going in and back in coming out (and can't be shot meanwhile).
func fort_fade(f: Unit) -> float:
	if fort.is_empty() or _flying(f) or f.is_ballista or absf(f.y - float(fort.gy)) >= float(fort.half) + 0.6:
		return 1.0
	if not fort.broken and f.team != HOLD:
		return 1.0   # the gate is shut to the attackers: they're outside battering it, never in the passage (and stay in plain sight)
	if not fort.castle:   # the fortress: gone a little way in from either end of the passage
		var a0: float = (float(fort.inX) + 1.2 - f.x) / 1.2
		var b0: float = (f.x - (float(fort.gateX) - 1.6)) / 1.2
		return clampf(maxf(a0, b0), 0.0, 1.0)
	if f.on_wall >= 0 or f.climbing >= 0 or f.descending >= 0:
		return 1.0
	# a unit fades only while its middle is inside the wall (the same short stretch for big and small units):
	# gone 0.6 in from the gate, and back 0.6 out past the back of the wall
	var a: float = (float(fort.inX) + 0.6 - f.x) / 1.2
	var b: float = (f.x - (float(fort.gateX) - 0.6)) / 1.2
	return clampf(maxf(a, b), 0.0, 1.0)


## Is f (an attacker on foot) pressed up against the closed gate, with its target on the other side?
func _gate_blocks(f: Unit, t: Unit) -> bool:
	if fort.is_empty() or fort.broken or f.team == HOLD or _flying(f):
		return false
	if absf(f.y - float(fort.gy)) >= float(fort.half) + 1.2 or f.x < float(fort.gateX) - 0.5 or f.x > float(fort.gateX) + _gpad(f) + 1.2:
		return false
	return t == null or t.x < float(fort.gateX) - 1.0 or t.on_wall >= 0 or t.is_ballista


func _hit_gate(f: Unit) -> void:
	if sneak >= 0 and f.team == sneak:
		sneak_hit = true
	fort["hp"] = maxf(0.0, float(fort.hp) - (float(f.T.dmg) + float(mod_plus[f.team])) * float(mod_mult[f.team]))
	fort["flash"] = 0.12
	last_hit = clock
	if float(fort.hp) == 0.0 and not fort.broken:
		fort["broken"] = true
		for k in 3:
			fx.append({"type": "dust", "x": float(fort.gateX) + _rnd(0, 1.5), "y": float(fort.gy) + _rnd(-1.5, 1.5), "face": 1, "w": 3.0})


func _update_fort(dt: float) -> void:
	if fort.is_empty():
		return
	fort["flash"] = maxf(0.0, float(fort.flash) - dt)
	var want: bool = fort.broken
	if not want:
		for u in F:
			if u.team == HOLD and not u.dead and not _flying(u) and absf(u.y - float(fort.gy)) < float(fort.half) + 2.0 and u.x > float(fort.inX) - 3.0 and u.x < float(fort.gateX) + 4.5:
				want = true
				break
	fort["open"] = clampf(float(fort.get("open", 0.0)) + (1.0 if want else -1.0) * dt / 0.35, 0.0, 1.0)


## Do the castle's walls stand between a and b? (passage included: the gate is shut to shots)
func _fort_blocks(ax: float, ay: float, bx: float, by: float) -> bool:
	for r in fort.rects:
		if _seg_hits(ax, ay, bx, by, r):
			return true
	return _seg_hits(ax, ay, bx, by, {"x0": float(fort.inX) + 0.6, "x1": float(fort.gateX) - 0.6, "y0": float(fort.gy) - float(fort.half), "y1": float(fort.gy) + float(fort.half)})


func _high(u: Unit) -> bool:
	return u.on_wall >= 0 or u.is_ballista


## How far a unit's body keeps off the stone (big units further): the walls' footprints and the castle's, grown by its size.
func _wall_rects(f: Unit) -> Array:
	if mside or fort.is_empty():
		return []
	var rx: float = clampf(float(f.T.w) * 0.35, 1.0, 3.2)
	var key: String = "%.2f" % rx
	if _rects_cache.has(key):
		return _rects_cache[key]
	var R: Array = []
	for W in levels:
		for b in W.get("blocks", []):
			R.append({"x0": float(b.x0) - rx, "x1": float(b.x1) + rx, "y0": float(b.y0) - 1.0, "y1": float(b.y1) + 1.0})
	for r in fort.rects + fort.get("trebs", []):
		R.append({"x0": float(r.x0) - rx, "x1": float(r.x1) + rx, "y0": float(r.y0) - 1.0, "y1": float(r.y1) + 1.0})
	_rects_cache[key] = R
	return R


func _clear_walk(f: Unit, a: Vector2, b: Vector2) -> bool:
	for r in _wall_rects(f):
		if _seg_hits(a.x, a.y, b.x, b.y, r):
			return false
	return true


## The next point to walk toward on the ground: straight there, or the shortest way round the walls over a handful of waypoints.
func _route(f: Unit, tx: float, ty: float) -> Vector2:
	if fort.is_empty():
		return Vector2(tx, ty)
	var S := Vector2(f.x, f.y)
	var D := Vector2(tx, ty)
	if f.rt_set and clock < f.rt_t and D.distance_to(f.rt_d) < 1.5 and S.distance_to(f.rt_p) >= 0.8:
		return f.rt_p
	var p: Vector2 = D
	if not _clear_walk(f, S, D):
		var N: Array = [S]
		N.append_array(fort.wp)
		N.append(D)
		var n: int = N.size()
		var dist_v: Array = []
		var prev: Array = []
		var done: Array = []
		for i in n:
			dist_v.append(1e9)
			prev.append(-1)
			done.append(false)
		dist_v[0] = 0.0
		while true:
			var u: int = -1
			for i in n:
				if not done[i] and dist_v[i] < 1e9 and (u < 0 or dist_v[i] < dist_v[u]):
					u = i
			if u < 0 or u == n - 1:
				break
			done[u] = true
			for v in range(1, n):
				if done[v]:
					continue
				var dd: float = dist_v[u] + N[u].distance_to(N[v])
				if dd < dist_v[v] and _clear_walk(f, N[u], N[v]):
					dist_v[v] = dd
					prev[v] = u
		if prev[n - 1] < 0:   # boxed in: make for the nearest waypoint
			var bestw: Vector2 = fort.wp[0]
			for q in fort.wp:
				if S.distance_to(q) < S.distance_to(bestw):
					bestw = q
			p = bestw
		else:
			var path: Array = []
			var v2: int = n - 1
			while v2 > 0:
				path.push_front(N[v2])
				v2 = prev[v2]
			p = path[1] if (path.size() > 1 and S.distance_to(path[0]) < 0.8) else path[0]   # at a waypoint already: on to the next
	f.rt_set = true
	f.rt_t = clock + 0.25
	f.rt_d = D
	f.rt_p = p
	return p


## Ground units are pushed back out of the stone to its nearest side; attackers can't pass the closed gate.
func _push_out_of_walls(L: Array) -> void:
	for f in L:
		if _flying(f) or f.climbing >= 0 or f.descending >= 0 or f.on_wall >= 0:
			continue
		for r in _wall_rects(f):
			if f.x > r.x0 and f.x < r.x1 and f.y > r.y0 and f.y < r.y1:
				var opts: Array = [[f.x - r.x0, "l"], [r.x1 - f.x, "r"]]
				if r.y0 >= 0:
					opts.append([f.y - r.y0, "t"])
				if r.y1 <= AH:
					opts.append([r.y1 - f.y, "b"])
				opts.sort_custom(func(a, b): return a[0] < b[0])
				match String(opts[0][1]):
					"l":
						f.x = r.x0
					"r":
						f.x = r.x1
					"t":
						f.y = r.y0
					_:
						f.y = r.y1
		if not fort.broken and f.team != HOLD and absf(f.y - float(fort.gy)) < float(fort.half) + 0.5 and f.x > float(fort.inX) - 1.0 and f.x < float(fort.gateX) + _gpad(f):
			f.x = float(fort.gateX) + _gpad(f)


func _out_pos(T: Dictionary, k: int) -> Vector2:
	var x0: float = 38.5 if fort.get("castle", false) else float(levels[0].x1)   # in front of the castle, or of the fortress's walls
	return Vector2(x0 + float(T.w) / 2.0 + 0.8 + (k / OUT_Y.size()) * (float(T.w) + 1.0), maxf(float(T.w) * float(T.ratio) + 1.0, float(OUT_Y[k % OUT_Y.size()])))


# =====================================================================
# For the screen and for Crown & Coin
# =====================================================================

## Health left on each side: on the field, plus the full health of the reserve, plus what escaped.
func health() -> Array:
	var out: Array = []
	for t in 2:
		var s: float = 0.0
		for f in _alive(t):
			s += maxf(0.0, f.hp)
		for k in RES[t]:
			s += unit_hp(t, k)
		s += float(esc[t].hp)
		out.append(s)
	return out


func unit_count(t: int) -> int:
	return _alive(t).size() + RES[t].size()


## What each side has left (on the field and in reserve) and what got away, in Crown & Coin's unit names.
func tally() -> Dictionary:
	var key_out: Dictionary = {}
	for k in KEY_IN:
		key_out[KEY_IN[k]] = k
	var left: Array = [{}, {}]
	var esc_out: Array = [{}, {}]
	for f in F:
		if f.dead or f.gone:
			continue
		var k: String = key_out.get(f.key, f.key)
		left[f.team][k] = int(left[f.team].get(k, 0)) + 1
	for t in 2:
		for ak in RES[t]:
			var k2: String = key_out.get(ak, ak)
			left[t][k2] = int(left[t].get(k2, 0)) + 1
		for ak in esc[t].k:
			var k3: String = key_out.get(ak, ak)
			esc_out[t][k3] = int(esc_out[t].get(k3, 0)) + int(esc[t].k[ak])
	return {"left": left, "esc": esc_out, "fled": retreat, "stalemate": stalemate, "clock": snappedf(clock, 0.1)}


## Turns a Crown & Coin army ({brawler: 4, ...}) into Arena unit counts.
static func arena_counts(army: Dictionary) -> Dictionary:
	var c: Dictionary = {}
	for k in army:
		var ak: String = KEY_IN.get(k, k)
		if TYPES.has(ak) and ORDER.has(ak):   # (the Procoptodon is retired from the arena: any sent are dropped)
			c[ak] = mini(int(TYPES[ak].get("maxN", 99)), int(c.get(ak, 0)) + int(army[k]))
	return c

extends Node
## Loads the game's data files once at startup. Registered as the autoload "GameData",
## so any script can read GameData.units, GameData.factions, GameData.upgrades, GameData.rules.

var units: Dictionary = {}
var factions: Dictionary = {}
var upgrades: Dictionary = {}
var rules: Dictionary = {}
var maps: Array = []   # hand-made maps (data/maps.json)


func _ready() -> void:
	units = _load_json("res://data/units.json")
	factions = _load_json("res://data/factions.json")
	upgrades = _load_json("res://data/upgrades.json")
	rules = _load_json("res://data/rules.json")
	if FileAccess.file_exists("res://data/maps.json"):
		maps = _load_json("res://data/maps.json").get("maps", [])


## A hand-made map by its id, or an empty Dictionary.
func map_by_id(id: String) -> Dictionary:
	for m in maps:
		if String(m.id) == id:
			return m
	return {}


## The hand-made maps for this many players.
func maps_for(np: int) -> Array:
	return maps.filter(func(m): return int(m.players) == np)


func _load_json(path: String) -> Dictionary:
	var file := FileAccess.open(path, FileAccess.READ)
	assert(file != null, "Missing data file: " + path)
	var parsed = JSON.parse_string(file.get_as_text())
	assert(typeof(parsed) == TYPE_DICTIONARY, "Data file is not a JSON object: " + path)
	return parsed

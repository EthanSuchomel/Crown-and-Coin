extends Node
## Online play for the Godot version (Ethan, 2026-11-23): two players, each on their own computer, share one game through
## a small online database (Supabase: the `games` table, read and written over its REST API). Like the browser version:
## one player makes a game and gets a 4-letter code, the friend enters it, and each turn's board is stored for the other
## to pick up. The address and key are in res://data/online.json ({"url": ..., "key": ...}).

const CONFIG := "res://data/online.json"
const SETTINGS := "user://settings.cfg"
const CODE_CHARS := "ABCDEFGHJKLMNPQRSTUVWXYZ"   # no I or O (they look like 1 and 0)

var url: String = ""
var key: String = ""
var my_id: String = ""
var last_err: String = ""   # the last failed call, for the screen: "401: Invalid API key"


func _ready() -> void:
	if FileAccess.file_exists(CONFIG):
		var d = JSON.parse_string(FileAccess.get_file_as_string(CONFIG))
		if d is Dictionary:
			url = String(d.get("url", "")).strip_edges().trim_suffix("/")
			key = String(d.get("key", "")).strip_edges()
	# Each copy of the game running on this computer is its own player (Ethan, 2026-11-23: two windows on one computer
	# shared one id, so both sat in the maker's seat and the map flipped between their boards). The first copy open
	# uses slot 1, a second copy open at the same time slot 2, and so on; each slot keeps its id, so Your games stay.
	var cfg := ConfigFile.new()
	cfg.load(SETTINGS)
	var now: float = Time.get_unix_time_from_system()
	for slot in range(1, 9):
		var alive: String = "user://online_alive_%d" % slot
		if slot < 8 and FileAccess.file_exists(alive) and now - float(FileAccess.get_file_as_string(alive)) < 6.0:
			continue   # another copy of the game is using this slot right now
		_alive_file = alive
		var k: String = "id" if slot == 1 else "id%d" % slot
		my_id = String(cfg.get_value("online", k, ""))
		if my_id == "":
			my_id = Crypto.new().generate_random_bytes(12).hex_encode()
			cfg.set_value("online", k, my_id)
			cfg.save(SETTINGS)
		break
	_beat()
	var t := Timer.new()
	t.wait_time = 2.0
	t.autostart = true
	t.timeout.connect(_beat)
	add_child(t)


var _alive_file: String = ""

func _beat() -> void:
	var f := FileAccess.open(_alive_file, FileAccess.WRITE)
	if f != null:
		f.store_string(str(Time.get_unix_time_from_system()))
		f.close()


func _exit_tree() -> void:
	if _alive_file != "":
		DirAccess.remove_absolute(ProjectSettings.globalize_path(_alive_file))


func configured() -> bool:
	return url.begins_with("http") and key != ""


func new_code() -> String:
	var s: String = ""
	for i in 4:
		s += CODE_CHARS[randi() % CODE_CHARS.length()]
	return s


## One call to the database. Returns {ok, status, data} (data: the parsed reply, usually an Array of rows).
func call_db(method: int, path: String, body = null, prefer: String = "") -> Dictionary:
	if not configured():
		return {"ok": false, "status": 0, "data": null, "err": "not set up"}
	var http := HTTPRequest.new()
	http.timeout = 15.0
	add_child(http)
	var headers := PackedStringArray(["apikey: " + key, "Content-Type: application/json", "Accept: application/json"])
	if key.begins_with("eyJ"):   # the older (JWT) keys go in Authorization too
		headers.append("Authorization: Bearer " + key)
	if prefer != "":
		headers.append("Prefer: " + prefer)
	var err: int = http.request(url + "/rest/v1/" + path, headers, method, JSON.stringify(body) if body != null else "")
	if err != OK:
		http.queue_free()
		return {"ok": false, "status": 0, "data": null, "err": "request %d" % err}
	var r: Array = await http.request_completed
	http.queue_free()
	var status: int = int(r[1])
	var text: String = (r[3] as PackedByteArray).get_string_from_utf8()
	var data = JSON.parse_string(text) if text != "" else null
	var ok: bool = int(r[0]) == HTTPRequest.RESULT_SUCCESS and status >= 200 and status < 300
	if not ok:
		var msg: String = text.left(300)
		if data is Dictionary:
			msg = String(data.get("message", data.get("msg", data.get("error", msg))))
			if data.get("hint") != null and String(data.hint) != "":
				msg += " (" + String(data.hint) + ")"
		last_err = ("%d: %s" % [status, msg]) if status > 0 else "no connection (%d)" % int(r[0])
	return {"ok": ok, "status": status, "data": data, "err": last_err if not ok else ""}


func get_game(code: String) -> Dictionary:
	var r: Dictionary = await call_db(HTTPClient.METHOD_GET, "games?code=eq.%s&select=*" % code.uri_encode())
	if r.ok and r.data is Array and not r.data.is_empty():
		return r.data[0]
	return {}


## Only what changed since rev: a quick look while waiting for the other player.
func peek(code: String) -> Dictionary:
	var r: Dictionary = await call_db(HTTPClient.METHOD_GET, "games?code=eq.%s&select=rev,status,guest,cur,winner" % code.uri_encode())
	if r.ok and r.data is Array and not r.data.is_empty():
		return r.data[0]
	return {}


func create(doc: Dictionary) -> Dictionary:
	return await call_db(HTTPClient.METHOD_POST, "games", doc, "return=representation")


## Take the empty seat: only works while nobody else has (the guest=is.null filter makes it first come, first served).
func join(code: String, fields: Dictionary) -> Dictionary:
	var r: Dictionary = await call_db(HTTPClient.METHOD_PATCH, "games?code=eq.%s&guest=is.null" % code.uri_encode(), fields, "return=representation")
	if r.ok and r.data is Array and not r.data.is_empty():
		return r.data[0]
	return {}


## Store the board: only if nobody stored a newer one since rev (otherwise returns {} and the caller reloads).
func push(code: String, rev: int, fields: Dictionary) -> Dictionary:
	var r: Dictionary = await call_db(HTTPClient.METHOD_PATCH, "games?code=eq.%s&rev=eq.%d" % [code.uri_encode(), rev], fields, "return=representation")
	if r.ok and r.data is Array and not r.data.is_empty():
		return r.data[0]
	return {}


func my_games() -> Array:
	last_err = ""
	var r: Dictionary = await call_db(HTTPClient.METHOD_GET, "games?or=(host.eq.%s,guest.eq.%s)&select=code,host,guest,host_faction,guest_faction,status,cur,turn,winner,updated&order=updated.desc&limit=20" % [my_id, my_id])
	return r.data if (r.ok and r.data is Array) else []


func remove(code: String) -> bool:
	var r: Dictionary = await call_db(HTTPClient.METHOD_DELETE, "games?code=eq.%s" % code.uri_encode())
	return r.ok


## The stored game is always from the maker's side (seat 0). The friend (seat 1) sees it turned round, so on every
## computer you are player 0 and the other side player 1, as the rest of the game expects.
static func swap_seats(d: Dictionary) -> Dictionary:
	var s: Dictionary = d.duplicate(true)
	var m := func(p) -> int: return int(p) if int(p) < 0 else 1 - int(p)
	if s.has("players") and s.players.size() == 2:
		s.players.reverse()
		for i in s.players.size():
			s.players[i]["id"] = i
			if s.players[i].has("out_by"):
				s.players[i]["out_by"] = m.call(s.players[i].out_by)
	if s.has("tiles"):
		for t in s.tiles:
			t["owner"] = m.call(t.get("owner", -1))
			if t.has("cap_by"):
				t["cap_by"] = m.call(t.cap_by)
			if t.has("braced"):
				t["braced"] = m.call(t.braced)
	if s.has("homes") and s.homes.size() == 2:
		s.homes = [s.homes[1], s.homes[0]]
	for k in ["current", "first", "over"]:
		if s.has(k):
			s[k] = m.call(s[k])
	if s.has("siege") and s.siege is Dictionary and s.siege.has("pid"):
		s.siege["pid"] = m.call(s.siege.pid)
	return s

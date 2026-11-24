"""Ethan, 2026-11-23: "We are also changing all the cards. We need the game to be simpler and have the playing style
based on units and buildings." Every faction plays the same five cards (keeping its own card names and pictures):
  1st Move, Build, Advance      2nd Build, Advance, Recruit      3rd Recruit, Fortify, Move
  4th Harvest, Build, Advance   5th Fortify, Harvest, Advance
Card upgrades are off for now (rules.json cards.upgrades false: no favors toward upgrades, no faction card upgrades);
"we can go over the upgrades later". The Mythical lose Channeling (their 5th card is the 5th above).
And each player may once a game swap a card in hand for one in reserve (before playing a card that turn).
Usage: python3 p12_cards.py PROJ"""
import sys, json
sys.path.insert(0, __file__.rsplit('/', 2)[0] + '/godot-port-nov22')
from common import F
P = sys.argv[1]
NEW = [["move", "build", "advance"], ["build", "advance", "recruit"], ["recruit", "fortify", "move"],
       ["harvest", "build", "advance"], ["fortify", "harvest", "advance"]]

# data: the decks and the switch
fj = P + '/data/factions.json'
d = json.load(open(fj))
for fid in d['order']:
    for k, c in enumerate(d[fid]['cards']):
        c['actions'] = list(NEW[k])
json.dump(d, open(fj, 'w'), indent='\t', ensure_ascii=False)
rj = P + '/data/rules.json'
r = json.load(open(rj))
r['cards']['upgrades'] = False
r['cards']['_note_upgrades'] = "Ethan 2026-11-23: card upgrades off while the new cards settle (no favors toward upgrades, no faction card upgrades)"
json.dump(r, open(rj, 'w'), indent='\t', ensure_ascii=False)

f = F(P + '/scripts/rules/game_state.gd')
f.rep('''func upgrade_due(pid: int, cid: String) -> bool:
    if is_myth(pid):   # Mythical cards don't upgrade yet
        return false''', '''## Card upgrades on at all (rules.json cards.upgrades; off since the new cards, 2026-11-23).
static func ups_on() -> bool:
    return bool(GameData.rules.cards.get("upgrades", true))


func upgrade_due(pid: int, cid: String) -> bool:
    if is_myth(pid) or not ups_on():   # Mythical cards don't upgrade yet
        return false''')
f.rep('''func card_ups(pid: int) -> bool:
    return is_dinos(pid) or is_robots(pid) or is_mammals(pid)''', '''func card_ups(pid: int) -> bool:
    return ups_on() and (is_dinos(pid) or is_robots(pid) or is_mammals(pid))


## The one-time swap (Ethan, 2026-11-23): once a game, before playing a card, put a card from your hand into your
## reserve and take a reserve card in its place.
func can_swap(pid: int) -> bool:
    return over < 0 and current == pid and play.is_empty() and not bool(players[pid].get("swapped", false)) and not players[pid].reserve.is_empty()


func swap_card(pid: int, hand_cid: String, reserve_cid: String) -> bool:
    var p: Dictionary = players[pid]
    if not can_swap(pid) or not p.hand.has(hand_cid) or not p.reserve.has(reserve_cid):
        return false
    p.hand[p.hand.find(hand_cid)] = reserve_cid
    p.reserve[p.reserve.find(reserve_cid)] = hand_cid
    p["swapped"] = true
    add_log("%s swap %s for %s (once a game)." % [p.name, card_of(pid, hand_cid).name, card_of(pid, reserve_cid).name])
    return true''')
f.save()

m = F(P + '/scripts/ui/main.gd')
m.rep('''func _favor_strip(pid: int, cid: String) -> Control:
    if g.is_myth(pid):   # Mythical cards don't upgrade yet: just the colour edge''', '''func _favor_strip(pid: int, cid: String) -> Control:
    if g.is_myth(pid) or not GameState.ups_on():   # no upgrades (Mythical, or card upgrades off): just the colour edge''')
m.rep('''        var up_txt: String = "You'll carry out these 3 actions in order and can skip any of them. Playing it earns a favor. Every 2nd favor upgrades one of its actions. Tap an action's icon to read what it does."''',
      '''        var up_txt: String = ("You'll carry out these 3 actions in order and can skip any of them. Playing it earns a favor. Every 2nd favor upgrades one of its actions. Tap an action's icon to read what it does.") if GameState.ups_on() else "You'll carry out these 3 actions in order and can skip any of them. Tap an action's icon to read what it does."''')
m.rep('''    body.add_child(_label("In reserve: " + ", ".join(reserve), 12, LICHEN))''', '''    body.add_child(_label("In reserve: " + ", ".join(reserve), 12, LICHEN))
    if g.can_swap(0) and not busy:   # the one-time swap (2026-11-23)
        var sw := _plate_button("⇄  Swap a card (once a game)", func(): _open_swap(), "iron", false, 14, 12, 6)
        sw.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
        body.add_child(sw)


## The one-time swap: first the hand card to put back, then the reserve card to take.
func _open_swap(from: String = "") -> void:
    var box := _open_overlay("Swap a card", 600.0)
    var intro := _label("Once a game, before you play a card, you can put a card from your hand into your reserve and take a reserve card in its place.", 15, BONE)
    intro.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    box.add_child(intro)
    var ask := _label(("Put back %s. Take which card?" % String(g.card_of(0, from).name)) if from != "" else "Which card goes back to your reserve?", 17, GOLD, true)
    ask.add_theme_font_override("font", _font_head)
    box.add_child(ask)
    var list: Array = g.players[0].reserve if from != "" else g.players[0].hand
    for cid in list:
        var c: String = String(cid)
        var card: Dictionary = g.card_of(0, c)
        var acts: Array = []
        for a in card.actions:
            acts.append(String(ACTION_NAMES.get(a, a)))
        var b := _plate_button("%s   ·   %s" % [String(card.name), "  ›  ".join(PackedStringArray(acts))], func():
            if from == "":
                _open_swap(c)
            else:
                _close_overlay()
                if g.swap_card(0, from, c):
                    preview = ""
                    sel = -1
                    refresh(), "gold" if from != "" else "iron", false, 15, 14, 8)
        b.alignment = HORIZONTAL_ALIGNMENT_LEFT
        box.add_child(b)
    var foot := HBoxContainer.new()
    foot.alignment = BoxContainer.ALIGNMENT_END
    foot.add_theme_constant_override("separation", 8)
    box.add_child(foot)
    if from != "":
        foot.add_child(_plate_button("Back", func(): _open_swap(), "iron", false, 14, 14, 6))
    foot.add_child(_plate_button("Cancel", func(): _close_overlay(), "iron", false, 14, 14, 6))''')
m.save()
print('ok')

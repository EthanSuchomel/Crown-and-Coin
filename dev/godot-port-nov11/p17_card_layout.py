# Ethan, 2026-11-12: cards with a picture (the Dinosaurs here) show no name, and the picture sits on the left.
import sys
F = sys.argv[1] + '/scripts/ui/main.gd'
s = open(F, encoding='utf-8').read()
def rep(a, b):
    global s
    if s.count(a) != 1: print('COUNT', s.count(a), a[:100]); sys.exit(1)
    s = s.replace(a, b)
rep('''	hb.add_child(_favor_strip(0, cid))
	var vb := VBoxContainer.new()''', '''	hb.add_child(_favor_strip(0, cid))
	var art: TextureRect = _card_art(0, cid, 92.0)   # the card's picture on the left, in place of its name
	if art != null:
		var am := MarginContainer.new()
		am.add_theme_constant_override("margin_left", 8)
		am.add_child(art)
		hb.add_child(am)
	var vb := VBoxContainer.new()''')
rep('''	vb.add_child(_label(String(card.name), 17, BONE, true))
	for s in card.actions.size():''', '''	if art == null:
		vb.add_child(_label(String(card.name), 17, BONE, true))
	for s in card.actions.size():''')
rep('''		vb.add_child(_label("▲ Playing it now upgrades an action", 12, GOLD))
	var art: TextureRect = _card_art(0, cid, 92.0)
	if art != null:
		hb.add_child(art)
	_ignore_mouse(hb)''', '''		vb.add_child(_label("▲ Playing it now upgrades an action", 12, GOLD))
	_ignore_mouse(hb)''')
rep('''	if hart != null:
		head.add_child(hart)
	head.add_child(_label(String(card.name), 21, BONE, true))''', '''	if hart != null:
		head.add_child(hart)
	else:
		head.add_child(_label(String(card.name), 21, BONE, true))''')
open(F, 'w', encoding='utf-8').write(s); print('card layout ok')

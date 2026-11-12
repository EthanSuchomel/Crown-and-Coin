# Ethan, 2026-11-12: no card names on the Robot and Dinosaur cards (the pictures say which is which), and the picture
# on the left side of the card.
import sys
for fn in sys.argv[1:]:
    s = open(fn, encoding='utf-8').read()
    def rep(a, b):
        global s
        if s.count(a) != 1: print(fn, 'COUNT', s.count(a), a[:100]); sys.exit(1)
        s = s.replace(a, b)
    rep('''  return `<button class="gcard" data-act="pick" data-cid="${cid}" style="--fc:${S.players[0].color}">${favStrip(0,cid)}<span class="gc-body">
    <span class="cname">${c.name}</span>''', '''  const art=CARD_ART[cid]&&cardUps(0);   // Robot and Dinosaur cards: the picture on the left, no name (Ethan, 2026-11-12)
  return `<button class="gcard" data-act="pick" data-cid="${cid}" style="--fc:${S.players[0].color}"${art?` aria-label="${c.name}"`:''}>${favStrip(0,cid)}${art?`<img class="cart" src="${CARD_ART[cid]}" alt="">`:''}<span class="gc-body">
    ${art?'':`<span class="cname">${c.name}</span>`}''')
    rep('''.join('')}</span></span>${CARD_ART[cid]&&cardUps(0)?`<img class="cart" src="${CARD_ART[cid]}" alt="">`:''}</button>`;''',
        '''.join('')}</span></span></button>`;''')
    rep('''<div class="bc-head">${CARD_ART[cid]&&cardUps(pid)?`<img class="bc-art" src="${CARD_ART[cid]}" alt="">`:''}<span class="bc-name">${c.name}</span>''',
        '''<div class="bc-head">${CARD_ART[cid]&&cardUps(pid)?`<img class="bc-art" src="${CARD_ART[cid]}" alt="${c.name}">`:`<span class="bc-name">${c.name}</span>`}''')
    rep('''.gcard .cart{flex:none;align-self:center;height:min(5.2em,90%);width:auto;max-width:28%;object-fit:contain;margin:0 .45em 0 .1em;''',
        '''.gcard .cart{flex:none;align-self:center;height:min(5.2em,90%);width:auto;max-width:28%;object-fit:contain;margin:0 .3em 0 .35em;''')
    open(fn, 'w', encoding='utf-8').write(s); print(fn, 'ok')
